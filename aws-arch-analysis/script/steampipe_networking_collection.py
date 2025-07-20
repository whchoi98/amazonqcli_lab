#!/usr/bin/env python3
"""
완전한 네트워킹 리소스 데이터 수집 스크립트 (Python 버전)
Shell 스크립트와 동일한 기능 및 출력 형식 제공 - 모든 네트워킹 리소스 포함
"""

import os
import subprocess
import glob
from pathlib import Path
from typing import List, Tuple

class SteampipeNetworkingCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = None):
        # 스크립트의 실제 위치를 기준으로 경로 설정
        if report_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent
            report_dir = str(project_root / "aws-arch-analysis" / "report")
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_networking_collection.log"
        self.error_log = self.report_dir / "steampipe_networking_errors.log"
        
        # 로그 파일 초기화
        self.log_file.write_text("")
        self.error_log.write_text("")
        
        self.success_count = 0
        self.total_count = 0

    def log_info(self, message: str):
        print(f"\033[0;34m[INFO]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[INFO] {message}\n")

    def log_success(self, message: str):
        print(f"\033[0;32m[SUCCESS]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[SUCCESS] {message}\n")

    def log_warning(self, message: str):
        print(f"\033[1;33m[WARNING]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[WARNING] {message}\n")

    def log_error(self, message: str):
        print(f"\033[0;31m[ERROR]\033[0m {message}")
        with open(self.error_log, 'a') as f:
            f.write(f"[ERROR] {message}\n")

    def check_steampipe_plugin(self):
        """Steampipe AWS 플러그인 확인"""
        self.log_info("Steampipe AWS 플러그인 확인 중...")
        try:
            result = subprocess.run(
                ["steampipe", "plugin", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            if "aws" not in result.stdout:
                self.log_warning("AWS 플러그인이 설치되지 않았습니다. 설치 중...")
                subprocess.run(["steampipe", "plugin", "install", "aws"], check=True)
        except subprocess.CalledProcessError:
            self.log_warning("Steampipe 플러그인 확인 중 오류 발생")

    def execute_steampipe_query(self, description: str, query: str, output_file: str) -> bool:
        self.log_info(f"수집 중: {description}")
        self.total_count += 1
        
        try:
            # 작업 디렉토리를 report_dir로 변경
            os.chdir(self.report_dir)
            
            result = subprocess.run(
                ["steampipe", "query", query, "--output", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            output_path = self.report_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            file_size = output_path.stat().st_size
            if file_size > 50:
                self.log_success(f"{description} 완료 ({output_file}, {file_size} bytes)")
                self.success_count += 1
                return True
            else:
                self.log_warning(f"{description} - 데이터 없음 ({output_file}, {file_size} bytes)")
                return False
                
        except subprocess.CalledProcessError as e:
            # 오류 메시지를 error_log에 기록
            error_msg = f"{description} 실패 - {output_file}"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            self.log_error(error_msg)
            
            # 오류 로그에 추가 정보 기록
            with open(self.error_log, 'a') as f:
                f.write(f"\nQuery failed: {query}\n")
                f.write(f"Error: {e.stderr}\n")
            
            return False

    def get_networking_queries(self) -> List[Tuple[str, str, str]]:
        """실제 Steampipe 스키마에 맞춘 완전한 쿼리 구조"""
        return [
            # 기본 VPC 리소스
            (
                "VPC 정보",
                f"select vpc_id, cidr_block, state, is_default, dhcp_options_id, instance_tenancy, owner_id, tags from aws_vpc where region = '{self.region}'",
                "networking_vpc.json"
            ),
            (
                "서브넷 정보",
                f"select subnet_id, vpc_id, cidr_block, availability_zone, availability_zone_id, state, available_ip_address_count, map_public_ip_on_launch, assign_ipv6_address_on_creation, default_for_az, tags from aws_vpc_subnet where region = '{self.region}'",
                "networking_subnets.json"
            ),
            (
                "라우팅 테이블 정보",
                f"select route_table_id, vpc_id, routes, associations, propagating_vgws, owner_id, tags from aws_vpc_route_table where region = '{self.region}'",
                "networking_route_tables.json"
            ),
            (
                "개별 라우팅 규칙",
                f"select route_table_id, destination_cidr_block, destination_ipv6_cidr_block, destination_prefix_list_id, gateway_id, instance_id, nat_gateway_id, network_interface_id, transit_gateway_id, vpc_peering_connection_id, state, origin from aws_vpc_route where region = '{self.region}'",
                "networking_routes.json"
            ),
            (
                "인터넷 게이트웨이 정보",
                f"select internet_gateway_id, attachments, owner_id, tags from aws_vpc_internet_gateway where region = '{self.region}'",
                "networking_igw.json"
            ),
            (
                "NAT 게이트웨이 정보",
                f"select nat_gateway_id, vpc_id, subnet_id, state, failure_code, failure_message, nat_gateway_addresses, create_time, delete_time, tags from aws_vpc_nat_gateway where region = '{self.region}'",
                "networking_nat.json"
            ),
            (
                "VPC 엔드포인트 정보",
                f"select vpc_endpoint_id, vpc_id, service_name, vpc_endpoint_type, state, route_table_ids, subnet_ids, groups, private_dns_enabled, requester_managed, dns_entries, creation_timestamp, tags from aws_vpc_endpoint where region = '{self.region}'",
                "networking_vpc_endpoints.json"
            ),
            (
                "VPC 피어링 연결 정보",
                f"select id, status_code, accepter_vpc_id, requester_vpc_id, accepter_owner_id, requester_owner_id, accepter_region, requester_region, accepter_cidr_block, requester_cidr_block, expiration_time, status_message, tags from aws_vpc_peering_connection where region = '{self.region}'",
                "networking_vpc_peering.json"
            ),
            
            # 보안 관련 리소스 (수정된 스키마)
            (
                "보안 그룹 정보",
                f"select group_id, group_name, description, vpc_id, owner_id, ip_permissions, ip_permissions_egress, tags from aws_vpc_security_group where region = '{self.region}'",
                "security_groups.json"
            ),
            (
                "보안 그룹 인바운드 규칙",
                f"select security_group_rule_id, group_id, is_egress, type, ip_protocol, from_port, to_port, cidr_ipv4, cidr_ipv6, description, referenced_user_id, referenced_vpc_id, prefix_list_id from aws_vpc_security_group_rule where region = '{self.region}' and is_egress = false",
                "security_groups_ingress_rules.json"
            ),
            (
                "보안 그룹 아웃바운드 규칙",
                f"select security_group_rule_id, group_id, is_egress, type, ip_protocol, from_port, to_port, cidr_ipv4, cidr_ipv6, description, referenced_user_id, referenced_vpc_id, prefix_list_id from aws_vpc_security_group_rule where region = '{self.region}' and is_egress = true",
                "security_groups_egress_rules.json"
            ),
            (
                "네트워크 ACL 정보",
                f"select network_acl_id, vpc_id, is_default, entries, associations, owner_id, tags from aws_vpc_network_acl where region = '{self.region}'",
                "networking_acl.json"
            ),
            (
                "VPC Flow Logs 정보",
                f"select flow_log_id, resource_id, traffic_type, log_destination_type, log_destination, log_format, log_group_name, deliver_logs_status, deliver_logs_error_message, creation_time, tags from aws_vpc_flow_log where region = '{self.region}'",
                "networking_flow_logs.json"
            ),
            
            # 고급 네트워킹 리소스 (수정된 스키마)
            (
                "Transit Gateway 정보",
                f"select transit_gateway_id, state, description, default_route_table_association, default_route_table_propagation, dns_support, vpn_ecmp_support, auto_accept_shared_attachments, amazon_side_asn, creation_time, owner_id, tags from aws_ec2_transit_gateway where region = '{self.region}'",
                "networking_transit_gateway.json"
            ),
            (
                "Transit Gateway 라우팅 테이블",
                f"select transit_gateway_route_table_id, transit_gateway_id, state, default_association_route_table, default_propagation_route_table, creation_time, tags from aws_ec2_transit_gateway_route_table where region = '{self.region}'",
                "networking_tgw_route_tables.json"
            ),
            (
                "Transit Gateway VPC 연결",
                f"select transit_gateway_attachment_id, transit_gateway_id, resource_id, state, creation_time, tags from aws_ec2_transit_gateway_vpc_attachment where region = '{self.region}'",
                "networking_tgw_vpc_attachments.json"
            ),
            (
                "VPN 연결 정보",
                f"select vpn_connection_id, state, type, customer_gateway_id, vpn_gateway_id, transit_gateway_id, customer_gateway_configuration, options, routes, tags from aws_vpc_vpn_connection where region = '{self.region}'",
                "networking_vpn_connections.json"
            ),
            (
                "VPN 게이트웨이 정보",
                f"select vpn_gateway_id, state, type, availability_zone, vpc_attachments, amazon_side_asn, tags from aws_vpc_vpn_gateway where region = '{self.region}'",
                "networking_vpn_gateways.json"
            ),
            (
                "고객 게이트웨이 정보",
                f"select customer_gateway_id, state, type, ip_address, bgp_asn, device_name, certificate_arn, tags from aws_vpc_customer_gateway where region = '{self.region}'",
                "networking_customer_gateways.json"
            ),
            
            # 기타 네트워킹 리소스 (수정된 스키마)
            (
                "Elastic IP 정보",
                f"select allocation_id, public_ip, public_ipv4_pool, domain, instance_id, network_interface_id, network_interface_owner_id, private_ip_address, association_id, customer_owned_ip, customer_owned_ipv4_pool, carrier_ip, tags from aws_vpc_eip where region = '{self.region}'",
                "networking_eip.json"
            ),
            (
                "네트워크 인터페이스 정보",
                f"select network_interface_id, subnet_id, vpc_id, availability_zone, description, groups, interface_type, mac_address, owner_id, private_dns_name, private_ip_address, private_ip_addresses, requester_id, requester_managed, source_dest_check, status, ipv6_addresses, tags from aws_ec2_network_interface where region = '{self.region}'",
                "networking_interfaces.json"
            ),
            (
                "DHCP Options 정보",
                f"select dhcp_options_id, domain_name, domain_name_servers, ntp_servers, netbios_name_servers, netbios_node_type, owner_id, tags from aws_vpc_dhcp_options where region = '{self.region}'",
                "networking_dhcp_options.json"
            ),
            (
                "Egress Only IGW 정보",
                f"select id, attachments, tags from aws_vpc_egress_only_internet_gateway where region = '{self.region}'",
                "networking_egress_only_igw.json"
            )
        ]

    def display_file_list(self):
        """생성된 파일 목록 표시 (Shell 스크립트와 동일한 형식)"""
        print(f"\n\033[0;34m📁 생성된 파일 목록:\033[0m")
        
        # 네트워킹 관련 파일들 검색
        patterns = ["networking_*.json", "security_groups*.json"]
        files_found = []
        
        for pattern in patterns:
            files_found.extend(glob.glob(str(self.report_dir / pattern)))
        
        files_found.sort()
        
        for file_path in files_found:
            file_name = os.path.basename(file_path)
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 100:
                    print(f"\033[0;32m✓ {file_name} ({file_size} bytes)\033[0m")
                else:
                    print(f"\033[1;33m⚠ {file_name} ({file_size} bytes) - 데이터 없음\033[0m")
            except OSError:
                print(f"\033[0;31m✗ {file_name} (파일 오류)\033[0m")

    def display_statistics(self):
        """수집 통계 표시 (실제 수집된 리소스 기준)"""
        print(f"\n\033[0;34m📊 수집 통계:\033[0m")
        print(f"총 쿼리 수: {self.total_count}")
        print(f"성공한 쿼리: {self.success_count}")
        print(f"실패한 쿼리: {self.total_count - self.success_count}")
        
        # 실제 수집 가능한 리소스 기준으로 수정
        print(f"\n\033[0;34m📋 카테고리별 수집 현황:\033[0m")
        print("🏗️  기본 VPC 리소스: 8개")
        print("🔒 보안 관련 리소스: 5개")
        print("🌐 고급 네트워킹: 6개")
        print("⚡ 기타 네트워킹: 3개")
        print(f"📊 총 리소스 타입: {self.total_count}개")

    def display_error_summary(self):
        """오류 요약 표시"""
        if self.error_log.exists() and self.error_log.stat().st_size > 0:
            self.log_warning(f"오류가 발생했습니다. {self.error_log.name} 파일을 확인하세요.")
            
            print(f"\n\033[1;33m최근 오류 (마지막 5줄):\033[0m")
            try:
                with open(self.error_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(line.strip())
            except Exception:
                pass

    def display_next_steps(self):
        """다음 단계 안내 (실제 수집 가능한 리소스 기준)"""
        print(f"\n\033[1;33m💡 다음 단계:\033[0m")
        print("1. 수집된 네트워킹 데이터를 바탕으로 상세 분석 진행")
        print("2. VPC 아키텍처 및 서브넷 설계 최적화 검토")
        print("3. 보안 그룹 및 네트워크 ACL 규칙 상세 분석")
        print("4. Transit Gateway 및 VPC 피어링 연결성 분석")
        print("5. 네트워크 성능, 보안, 비용 최적화 종합 분석")
        print("6. 네트워킹 보고서 생성 및 권장사항 도출")

    def run_collection(self):
        self.log_info("🚀 Steampipe 기반 네트워킹 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        self.log_info("📡 네트워킹 리소스 수집 시작...")
        
        queries = self.get_networking_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        self.log_success("네트워킹 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # Shell 스크립트와 동일한 출력 형식
        self.display_file_list()
        self.display_statistics()
        self.display_error_summary()
        self.display_next_steps()
        
        self.log_info("🎉 네트워킹 리소스 데이터 수집이 완료되었습니다!")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 네트워킹 리소스 데이터 수집 (실제 스키마 기준)")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    # 스크립트의 실제 위치를 기준으로 기본 경로 설정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    default_report_dir = str(project_root / "aws-arch-analysis" / "report")
    
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", default_report_dir), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeNetworkingCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
