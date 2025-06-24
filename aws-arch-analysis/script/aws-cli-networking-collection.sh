#!/bin/bash
# AWS CLI 기반 네트워킹 리소스 데이터 수집 스크립트

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="$REPORT_DIR/aws_cli_collection.log"
ERROR_LOG="$REPORT_DIR/aws_cli_errors.log"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$ERROR_LOG"
}

# AWS CLI 데이터 수집 함수
collect_aws_data() {
    local description="$1"
    local aws_command="$2"
    local output_file="$3"
    local jq_filter="$4"
    
    log_info "수집 중: $description"
    
    # AWS CLI 명령 실행
    if eval "$aws_command" > /tmp/aws_raw_output.json 2>/tmp/aws_error.tmp; then
        # jq 필터 적용 (제공된 경우)
        if [ -n "$jq_filter" ]; then
            jq "$jq_filter" /tmp/aws_raw_output.json > "$output_file" 2>/tmp/jq_error.tmp
        else
            cp /tmp/aws_raw_output.json "$output_file"
        fi
        
        local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
        if [ "$file_size" -gt 50 ]; then
            log_success "$description 완료 ($output_file, ${file_size} bytes)"
            return 0
        else
            log_warning "$description - 데이터 없음 ($output_file, ${file_size} bytes)"
            return 1
        fi
    else
        cat /tmp/aws_error.tmp >> "$ERROR_LOG"
        log_error "$description 실패 - $output_file"
        echo "[]" > "$output_file"
        return 1
    fi
}

# 메인 실행 부분
main() {
    log_info "🚀 AWS CLI 기반 네트워킹 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 디렉토리 생성
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR"
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
    # AWS CLI 연결 확인
    log_info "AWS CLI 연결 확인 중..."
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS CLI 연결 실패"
        exit 1
    fi
    
    log_info "📡 네트워킹 리소스 수집 시작..."
    
    local success_count=0
    local total_count=0
    
    # 1. VPC 정보
    ((total_count++))
    if collect_aws_data "VPC 정보" \
        "aws ec2 describe-vpcs --region $REGION --output json" \
        "networking_vpc.json" \
        '.Vpcs | map({vpc_id: .VpcId, cidr_block: .CidrBlock, state: .State, is_default: .IsDefault, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 2. 서브넷 정보
    ((total_count++))
    if collect_aws_data "서브넷 정보" \
        "aws ec2 describe-subnets --region $REGION --output json" \
        "networking_subnets.json" \
        '.Subnets | map({subnet_id: .SubnetId, vpc_id: .VpcId, cidr_block: .CidrBlock, availability_zone: .AvailabilityZone, state: .State, map_public_ip_on_launch: .MapPublicIpOnLaunch, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 3. 보안 그룹 정보
    ((total_count++))
    if collect_aws_data "보안 그룹 정보" \
        "aws ec2 describe-security-groups --region $REGION --output json" \
        "security_groups.json" \
        '.SecurityGroups | map({group_id: .GroupId, group_name: .GroupName, description: .Description, vpc_id: .VpcId, ip_permissions: .IpPermissions, ip_permissions_egress: .IpPermissionsEgress, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 4. 라우팅 테이블 정보
    ((total_count++))
    if collect_aws_data "라우팅 테이블 정보" \
        "aws ec2 describe-route-tables --region $REGION --output json" \
        "networking_route_tables.json" \
        '.RouteTables | map({route_table_id: .RouteTableId, vpc_id: .VpcId, routes: .Routes, associations: .Associations, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 5. 인터넷 게이트웨이 정보
    ((total_count++))
    if collect_aws_data "인터넷 게이트웨이 정보" \
        "aws ec2 describe-internet-gateways --region $REGION --output json" \
        "networking_igw.json" \
        '.InternetGateways | map({internet_gateway_id: .InternetGatewayId, state: .State, attachments: .Attachments, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 6. NAT 게이트웨이 정보
    ((total_count++))
    if collect_aws_data "NAT 게이트웨이 정보" \
        "aws ec2 describe-nat-gateways --region $REGION --output json" \
        "networking_nat.json" \
        '.NatGateways | map({nat_gateway_id: .NatGatewayId, vpc_id: .VpcId, subnet_id: .SubnetId, state: .State, nat_gateway_addresses: .NatGatewayAddresses, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 7. VPC 엔드포인트 정보
    ((total_count++))
    if collect_aws_data "VPC 엔드포인트 정보" \
        "aws ec2 describe-vpc-endpoints --region $REGION --output json" \
        "networking_vpc_endpoints.json" \
        '.VpcEndpoints | map({vpc_endpoint_id: .VpcEndpointId, vpc_id: .VpcId, service_name: .ServiceName, vpc_endpoint_type: .VpcEndpointType, state: .State, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 8. VPC 피어링 연결 정보
    ((total_count++))
    if collect_aws_data "VPC 피어링 연결 정보" \
        "aws ec2 describe-vpc-peering-connections --region $REGION --output json" \
        "networking_vpc_peering.json" \
        '.VpcPeeringConnections | map({vpc_peering_connection_id: .VpcPeeringConnectionId, accepter_vpc_info: .AccepterVpcInfo, requester_vpc_info: .RequesterVpcInfo, status: .Status, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 9. Elastic IP 정보
    ((total_count++))
    if collect_aws_data "Elastic IP 정보" \
        "aws ec2 describe-addresses --region $REGION --output json" \
        "networking_eip.json" \
        '.Addresses | map({public_ip: .PublicIp, allocation_id: .AllocationId, association_id: .AssociationId, domain: .Domain, instance_id: .InstanceId, network_interface_id: .NetworkInterfaceId, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 10. 네트워크 인터페이스 정보
    ((total_count++))
    if collect_aws_data "네트워크 인터페이스 정보" \
        "aws ec2 describe-network-interfaces --region $REGION --output json" \
        "networking_interfaces.json" \
        '.NetworkInterfaces | map({network_interface_id: .NetworkInterfaceId, subnet_id: .SubnetId, vpc_id: .VpcId, status: .Status, mac_address: .MacAddress, private_ip_address: .PrivateIpAddress, source_dest_check: .SourceDestCheck, groups: .Groups, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 11. 네트워크 ACL 정보
    ((total_count++))
    if collect_aws_data "네트워크 ACL 정보" \
        "aws ec2 describe-network-acls --region $REGION --output json" \
        "networking_acl.json" \
        '.NetworkAcls | map({network_acl_id: .NetworkAclId, vpc_id: .VpcId, is_default: .IsDefault, entries: .Entries, associations: .Associations, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 12. VPC Flow Logs 정보
    ((total_count++))
    if collect_aws_data "VPC Flow Logs 정보" \
        "aws ec2 describe-flow-logs --region $REGION --output json" \
        "networking_flow_logs.json" \
        '.FlowLogs | map({flow_log_id: .FlowLogId, resource_id: .ResourceId, resource_type: .ResourceType, traffic_type: .TrafficType, log_destination_type: .LogDestinationType, log_destination: .LogDestination, flow_log_status: .FlowLogStatus, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 13. Transit Gateway 정보
    ((total_count++))
    if collect_aws_data "Transit Gateway 정보" \
        "aws ec2 describe-transit-gateways --region $REGION --output json" \
        "networking_transit_gateway.json" \
        '.TransitGateways | map({transit_gateway_id: .TransitGatewayId, state: .State, owner_id: .OwnerId, description: .Description, default_route_table_association: .DefaultRouteTableAssociation, default_route_table_propagation: .DefaultRouteTablePropagation, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 14. Transit Gateway 연결 정보
    ((total_count++))
    if collect_aws_data "Transit Gateway 연결 정보" \
        "aws ec2 describe-transit-gateway-attachments --region $REGION --output json" \
        "networking_transit_gateway_attachments.json" \
        '.TransitGatewayAttachments | map({transit_gateway_attachment_id: .TransitGatewayAttachmentId, transit_gateway_id: .TransitGatewayId, resource_type: .ResourceType, resource_id: .ResourceId, state: .State, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 15. Customer Gateway 정보
    ((total_count++))
    if collect_aws_data "Customer Gateway 정보" \
        "aws ec2 describe-customer-gateways --region $REGION --output json" \
        "networking_customer_gateways.json" \
        '.CustomerGateways | map({customer_gateway_id: .CustomerGatewayId, state: .State, type: .Type, ip_address: .IpAddress, bgp_asn: .BgpAsn, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 16. VPN Gateway 정보
    ((total_count++))
    if collect_aws_data "VPN Gateway 정보" \
        "aws ec2 describe-vpn-gateways --region $REGION --output json" \
        "networking_vpn_gateways.json" \
        '.VpnGateways | map({vpn_gateway_id: .VpnGatewayId, state: .State, type: .Type, availability_zone: .AvailabilityZone, vpc_attachments: .VpcAttachments, tags: .Tags})'; then
        ((success_count++))
    fi
    
    # 결과 요약
    log_success "네트워킹 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    if [ $success_count -lt $total_count ]; then
        log_warning "일부 오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo ""
        echo "최근 오류 (마지막 5줄):"
        tail -5 "$ERROR_LOG" 2>/dev/null || echo "오류 로그가 없습니다."
    fi
    
    # 정리
    rm -f /tmp/aws_raw_output.json /tmp/aws_error.tmp /tmp/jq_error.tmp
    
    return 0
}

# 스크립트 실행
main "$@"
