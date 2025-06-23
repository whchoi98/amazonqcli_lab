#!/bin/bash
# Steampipe 기반 네트워킹 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_collection.log"
ERROR_LOG="steampipe_errors.log"

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

# Steampipe 쿼리 실행 함수
execute_steampipe_query() {
    local description="$1"
    local query="$2"
    local output_file="$3"
    
    log_info "수집 중: $description"
    
    if steampipe query "$query" --output json > "$output_file" 2>>"$ERROR_LOG"; then
        local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
        if [ "$file_size" -gt 50 ]; then
            log_success "$description 완료 ($output_file, ${file_size} bytes)"
            return 0
        else
            log_warning "$description - 데이터 없음 ($output_file, ${file_size} bytes)"
            return 1
        fi
    else
        log_error "$description 실패 - $output_file"
        return 1
    fi
}

# 메인 실행부
main() {
    log_info "🚀 Steampipe 기반 네트워킹 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 보고서 디렉토리 생성 및 이동
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR" || exit 1
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
    # Steampipe 설치 확인
    if ! command -v steampipe &> /dev/null; then
        log_error "Steampipe가 설치되지 않았습니다."
        echo -e "${YELLOW}💡 Steampipe 설치 방법:${NC}"
        echo "sudo /bin/sh -c \"\$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)\""
        echo "steampipe plugin install aws"
        exit 1
    fi
    
    # AWS 플러그인 확인
    log_info "Steampipe AWS 플러그인 확인 중..."
    if ! steampipe plugin list | grep -q "aws"; then
        log_warning "AWS 플러그인이 설치되지 않았습니다. 설치 중..."
        steampipe plugin install aws
    fi
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_info "📡 네트워킹 리소스 수집 시작..."
    
    # 네트워킹 리소스 수집 배열
    declare -a queries=(
        "VPC 정보|select vpc_id, cidr_block, state, is_default, dhcp_options_id, instance_tenancy, ipv6_cidr_block_association_set, owner_id, tags from aws_vpc where region = '$REGION'|networking_vpc.json"
        "서브넷 정보|select subnet_id, vpc_id, cidr_block, ipv6_cidr_block, availability_zone, availability_zone_id, state, available_ip_address_count, map_public_ip_on_launch, assign_ipv6_address_on_creation, default_for_az, outpost_arn, customer_owned_ipv4_pool, tags from aws_vpc_subnet where region = '$REGION'|networking_subnets.json"
        "보안 그룹 정보|select group_id, group_name, description, vpc_id, owner_id, ip_permissions, ip_permissions_egress, tags from aws_vpc_security_group where region = '$REGION'|security_groups.json"
        "보안 그룹 인바운드 규칙|select group_id, group_name, type, ip_protocol, from_port, to_port, cidr_ipv4, cidr_ipv6, prefix_list_id, referenced_group_info, description, tags from aws_vpc_security_group_rule where region = '$REGION' and type = 'ingress'|security_groups_ingress_rules.json"
        "보안 그룹 아웃바운드 규칙|select group_id, group_name, type, ip_protocol, from_port, to_port, cidr_ipv4, cidr_ipv6, prefix_list_id, referenced_group_info, description, tags from aws_vpc_security_group_rule where region = '$REGION' and type = 'egress'|security_groups_egress_rules.json"
        "라우팅 테이블 정보|select route_table_id, vpc_id, routes, associations, propagating_vgws, owner_id, tags from aws_vpc_route_table where region = '$REGION'|networking_route_tables.json"
        "인터넷 게이트웨이 정보|select internet_gateway_id, attachments, owner_id, tags from aws_vpc_internet_gateway where region = '$REGION'|networking_igw.json"
        "NAT 게이트웨이 정보|select nat_gateway_id, vpc_id, subnet_id, state, failure_code, failure_message, nat_gateway_addresses, connectivity_type, create_time, delete_time, tags from aws_vpc_nat_gateway where region = '$REGION'|networking_nat.json"
        "VPC 엔드포인트 정보|select vpc_endpoint_id, vpc_id, service_name, vpc_endpoint_type, state, policy_document, route_table_ids, subnet_ids, groups, private_dns_enabled, requester_managed, dns_entries, creation_timestamp, tags from aws_vpc_endpoint where region = '$REGION'|networking_vpc_endpoints.json"
        "VPC 피어링 연결 정보|select vpc_peering_connection_id, accepter_vpc_info, requester_vpc_info, status, expiration_time, tags from aws_vpc_peering_connection where region = '$REGION'|networking_vpc_peering.json"
        "Elastic IP 정보|select allocation_id, public_ip, public_ipv4_pool, domain, instance_id, network_interface_id, network_interface_owner_id, private_ip_address, association_id, customer_owned_ip, customer_owned_ipv4_pool, carrier_ip, tags from aws_vpc_eip where region = '$REGION'|networking_eip.json"
        "네트워크 인터페이스 정보|select network_interface_id, subnet_id, vpc_id, availability_zone, description, groups, interface_type, mac_address, owner_id, private_dns_name, private_ip_address, private_ip_addresses, public_dns_name, public_ip, requester_id, requester_managed, source_dest_check, status, attachment, association, ipv6_addresses, outpost_arn, tags from aws_ec2_network_interface where region = '$REGION'|networking_interfaces.json"
        "네트워크 ACL 정보|select network_acl_id, vpc_id, is_default, entries, associations, owner_id, tags from aws_vpc_network_acl where region = '$REGION'|networking_acl.json"
        "VPC Flow Logs 정보|select flow_log_id, resource_type, resource_ids, traffic_type, log_destination_type, log_destination, log_format, log_group_name, deliver_logs_status, deliver_logs_error_message, creation_time, tags from aws_vpc_flow_log where region = '$REGION'|networking_flow_logs.json"
        "Transit Gateway 정보|select transit_gateway_id, state, description, default_route_table_association, default_route_table_propagation, dns_support, vpn_ecmp_support, auto_accept_shared_attachments, default_route_table_id, association_default_route_table_id, propagation_default_route_table_id, amazon_side_asn, creation_time, owner_id, tags from aws_ec2_transit_gateway where region = '$REGION'|networking_transit_gateway.json"
        "Transit Gateway 연결 정보|select transit_gateway_attachment_id, transit_gateway_id, resource_type, resource_id, state, creation_time, tags from aws_ec2_transit_gateway_attachment where region = '$REGION'|networking_transit_gateway_attachments.json"
        "VPN 연결 정보|select vpn_connection_id, state, type, customer_gateway_id, vpn_gateway_id, transit_gateway_id, core_network_arn, core_network_attachment_arn, gateway_association_state, options, routes, customer_gateway_configuration, category, tags from aws_vpc_vpn_connection where region = '$REGION'|networking_vpn_connections.json"
        "Customer Gateway 정보|select customer_gateway_id, state, type, ip_address, bgp_asn, device_name, certificate_arn, tags from aws_vpc_customer_gateway where region = '$REGION'|networking_customer_gateways.json"
        "VPN Gateway 정보|select vpn_gateway_id, state, type, availability_zone, vpc_attachments, amazon_side_asn, tags from aws_vpc_vpn_gateway where region = '$REGION'|networking_vpn_gateways.json"
        "DHCP Options 정보|select dhcp_options_id, dhcp_configurations, owner_id, tags from aws_vpc_dhcp_options where region = '$REGION'|networking_dhcp_options.json"
        "Prefix Lists 정보|select prefix_list_id, prefix_list_name, state, address_family, max_entries, version, entries, owner_id, tags from aws_vpc_managed_prefix_list where region = '$REGION'|networking_prefix_lists.json"
    )
    
    # 쿼리 실행
    for query_info in "${queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "네트워킹 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    log_info "🎉 네트워킹 리소스 데이터 수집이 완료되었습니다!"
}

# 명령행 인수 처리
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -d|--dir)
            REPORT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "사용법: $0 [옵션]"
            echo "  -r, --region REGION    AWS 리전 설정"
            echo "  -d, --dir DIRECTORY    보고서 디렉토리 설정"
            echo "  -h, --help            도움말 표시"
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            exit 1
            ;;
    esac
done

# 스크립트 실행
main "$@"
