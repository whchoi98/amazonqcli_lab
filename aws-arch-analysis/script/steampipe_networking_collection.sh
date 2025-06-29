#!/bin/bash
# 완전한 네트워킹 리소스 데이터 수집 스크립트 (모든 네트워킹 리소스 포함)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report}"
LOG_FILE="steampipe_networking_collection.log"
ERROR_LOG="steampipe_networking_errors.log"

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

# 메인 함수
main() {
    log_info "🚀 완전한 네트워킹 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 디렉토리 생성
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR"
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
    # AWS 플러그인 확인
    log_info "Steampipe AWS 플러그인 확인 중..."
    if ! steampipe plugin list | grep -q "aws"; then
        log_warning "AWS 플러그인이 설치되지 않았습니다. 설치 중..."
        steampipe plugin install aws
    fi
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_info "📡 완전한 네트워킹 리소스 수집 시작..."
    
    # 완전한 네트워킹 리소스 수집 배열
    declare -a queries=(
        # 기본 VPC 리소스
        "VPC 정보|select vpc_id, cidr_block, state, is_default, dhcp_options_id, instance_tenancy, owner_id, tags from aws_vpc where region = '$REGION'|networking_vpc.json"
        "서브넷 정보|select subnet_id, vpc_id, cidr_block, availability_zone, availability_zone_id, state, available_ip_address_count, map_public_ip_on_launch, assign_ipv6_address_on_creation, default_for_az, tags from aws_vpc_subnet where region = '$REGION'|networking_subnets.json"
        "라우팅 테이블 정보|select route_table_id, vpc_id, routes, associations, propagating_vgws, owner_id, tags from aws_vpc_route_table where region = '$REGION'|networking_route_tables.json"
        "개별 라우팅 규칙|select route_table_id, destination_cidr_block, destination_ipv6_cidr_block, destination_prefix_list_id, gateway_id, instance_id, nat_gateway_id, network_interface_id, transit_gateway_id, vpc_peering_connection_id, state, origin from aws_vpc_route where region = '$REGION'|networking_routes.json"
        "인터넷 게이트웨이 정보|select internet_gateway_id, attachments, owner_id, tags from aws_vpc_internet_gateway where region = '$REGION'|networking_igw.json"
        "NAT 게이트웨이 정보|select nat_gateway_id, vpc_id, subnet_id, state, failure_code, failure_message, nat_gateway_addresses, create_time, delete_time, tags from aws_vpc_nat_gateway where region = '$REGION'|networking_nat.json"
        "VPC 엔드포인트 정보|select vpc_endpoint_id, vpc_id, service_name, vpc_endpoint_type, state, route_table_ids, subnet_ids, groups, private_dns_enabled, requester_managed, dns_entries, creation_timestamp, tags from aws_vpc_endpoint where region = '$REGION'|networking_vpc_endpoints.json"
        "VPC 피어링 연결 정보|select id, status_code, accepter_vpc_id, requester_vpc_id, accepter_owner_id, requester_owner_id, accepter_region, requester_region, accepter_cidr_block, requester_cidr_block, expiration_time, status_message, tags from aws_vpc_peering_connection where region = '$REGION'|networking_vpc_peering.json"
        
        # 보안 관련 리소스
        "보안 그룹 정보|select group_id, group_name, description, vpc_id, owner_id, ip_permissions, ip_permissions_egress, tags from aws_vpc_security_group where region = '$REGION'|security_groups.json"
        "보안 그룹 인바운드 규칙|select security_group_rule_id, group_id, is_egress, type, ip_protocol, from_port, to_port, cidr_ipv4, cidr_ipv6, description, referenced_group_info, prefix_list_id from aws_vpc_security_group_rule where region = '$REGION' and is_egress = false|security_groups_ingress_rules.json"
        "보안 그룹 아웃바운드 규칙|select security_group_rule_id, group_id, is_egress, type, ip_protocol, from_port, to_port, cidr_ipv4, cidr_ipv6, description, referenced_group_info, prefix_list_id from aws_vpc_security_group_rule where region = '$REGION' and is_egress = true|security_groups_egress_rules.json"
        "네트워크 ACL 정보|select network_acl_id, vpc_id, is_default, entries, associations, owner_id, tags from aws_vpc_network_acl where region = '$REGION'|networking_acl.json"
        "VPC Flow Logs 정보|select flow_log_id, resource_id, traffic_type, log_destination_type, log_destination, log_format, log_group_name, deliver_logs_status, deliver_logs_error_message, creation_time, tags from aws_vpc_flow_log where region = '$REGION'|networking_flow_logs.json"
        
        # 고급 네트워킹 리소스
        "Transit Gateway 정보|select transit_gateway_id, state, description, default_route_table_association, default_route_table_propagation, dns_support, vpn_ecmp_support, auto_accept_shared_attachments, amazon_side_asn, creation_time, owner_id, tags from aws_ec2_transit_gateway where region = '$REGION'|networking_transit_gateway.json"
        "Transit Gateway 라우팅 테이블|select transit_gateway_route_table_id, transit_gateway_id, state, default_association_route_table, default_propagation_route_table, creation_time, tags from aws_ec2_transit_gateway_route_table where region = '$REGION'|networking_tgw_route_tables.json"
        "Transit Gateway VPC 연결|select transit_gateway_attachment_id, transit_gateway_id, vpc_id, state, subnet_ids, creation_time, tags from aws_ec2_transit_gateway_vpc_attachment where region = '$REGION'|networking_tgw_vpc_attachments.json"
        "VPN 연결 정보|select vpn_connection_id, state, type, customer_gateway_id, vpn_gateway_id, transit_gateway_id, customer_gateway_configuration, options, routes, tags from aws_vpc_vpn_connection where region = '$REGION'|networking_vpn_connections.json"
        "VPN 게이트웨이 정보|select vpn_gateway_id, state, type, availability_zone, vpc_attachments, amazon_side_asn, tags from aws_vpc_vpn_gateway where region = '$REGION'|networking_vpn_gateways.json"
        "고객 게이트웨이 정보|select customer_gateway_id, state, type, ip_address, bgp_asn, device_name, certificate_arn, tags from aws_vpc_customer_gateway where region = '$REGION'|networking_customer_gateways.json"
        
        # Direct Connect 리소스
        "Direct Connect 연결|select connection_id, connection_name, connection_state, region, location, bandwidth, vlan, partner_name, loa_issue_time, lag_id, aws_device, aws_device_v2, has_logical_redundancy, jumbo_frame_capable, aws_logical_device_id, encryption_mode, mac_sec_capable, port_encryption_status, mac_sec_keys, provider_name, tags from aws_directconnect_connection where region = '$REGION'|networking_dx_connections.json"
        "Direct Connect 가상 인터페이스|select virtual_interface_id, virtual_interface_name, virtual_interface_type, virtual_interface_state, connection_id, vlan, bgp_asn, amazon_address, customer_address, address_family, amazon_side_asn, auth_key, direct_connect_gateway_id, location, mtu, owner_account, region, route_filter_prefixes, tags from aws_directconnect_virtual_interface where region = '$REGION'|networking_dx_virtual_interfaces.json"
        "Direct Connect 게이트웨이|select direct_connect_gateway_id, direct_connect_gateway_name, direct_connect_gateway_state, amazon_side_asn, owner_account, state_change_error from aws_directconnect_gateway|networking_dx_gateways.json"
        
        # 기타 네트워킹 리소스
        "Elastic IP 정보|select allocation_id, public_ip, public_ipv4_pool, domain, instance_id, network_interface_id, network_interface_owner_id, private_ip_address, association_id, customer_owned_ip, customer_owned_ipv4_pool, carrier_ip, tags from aws_vpc_eip where region = '$REGION'|networking_eip.json"
        "네트워크 인터페이스 정보|select network_interface_id, subnet_id, vpc_id, availability_zone, description, groups, interface_type, mac_address, owner_id, private_dns_name, private_ip_address, private_ip_addresses, requester_id, requester_managed, source_dest_check, status, attachment, association, ipv6_addresses, tags from aws_ec2_network_interface where region = '$REGION'|networking_interfaces.json"
        "DHCP Options 정보|select dhcp_options_id, dhcp_configurations, owner_id, tags from aws_vpc_dhcp_options where region = '$REGION'|networking_dhcp_options.json"
        "Prefix List 정보|select prefix_list_id, prefix_list_name, state, address_family, max_entries, version, entries, owner_id, tags from aws_vpc_managed_prefix_list where region = '$REGION'|networking_prefix_lists.json"
        "Carrier Gateway 정보|select carrier_gateway_id, vpc_id, state, owner_id, tags from aws_vpc_carrier_gateway where region = '$REGION'|networking_carrier_gateways.json"
        "Egress Only IGW 정보|select egress_only_internet_gateway_id, attachments, tags from aws_vpc_egress_only_internet_gateway where region = '$REGION'|networking_egress_only_igw.json"
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
    log_success "완전한 네트워킹 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in networking_*.json security_groups*.json; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            if [ "$size" -gt 100 ]; then
                echo -e "${GREEN}✓ $file (${size} bytes)${NC}"
            else
                echo -e "${YELLOW}⚠ $file (${size} bytes) - 데이터 없음${NC}"
            fi
        fi
    done
    
    # 수집 통계
    echo -e "\n${BLUE}📊 수집 통계:${NC}"
    echo "총 쿼리 수: $total_count"
    echo "성공한 쿼리: $success_count"
    echo "실패한 쿼리: $((total_count - success_count))"
    
    # 카테고리별 수집 현황
    echo -e "\n${BLUE}📋 카테고리별 수집 현황:${NC}"
    echo "🏗️  기본 VPC 리소스: 8개"
    echo "🔒 보안 관련 리소스: 5개"
    echo "🌐 고급 네트워킹: 6개"
    echo "🔌 Direct Connect: 3개"
    echo "⚡ 기타 네트워킹: 6개"
    echo "📊 총 리소스 타입: 28개"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 완전한 네트워킹 데이터를 바탕으로 상세 분석 진행"
    echo "2. VPC 아키텍처 및 서브넷 설계 최적화 검토"
    echo "3. 보안 그룹 및 네트워크 ACL 규칙 상세 분석"
    echo "4. Transit Gateway 및 VPC 피어링 연결성 분석"
    echo "5. Direct Connect 및 VPN 연결 현황 분석"
    echo "6. 네트워크 성능, 보안, 비용 최적화 종합 분석"
    
    log_info "🎉 완전한 네트워킹 리소스 데이터 수집이 완료되었습니다!"
}

# 스크립트 실행
main "$@"
