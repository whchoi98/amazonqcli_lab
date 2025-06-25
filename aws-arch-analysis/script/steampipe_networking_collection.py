#!/usr/bin/env python3
"""
Steampipe 기반 네트워킹 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

class SteampipeNetworkingCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_networking_collection.log"
        self.error_log = self.report_dir / "steampipe_networking_errors.log"
        
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

    def execute_steampipe_query(self, description: str, query: str, output_file: str) -> bool:
        self.log_info(f"수집 중: {description}")
        self.total_count += 1
        
        try:
            result = subprocess.run(
                ["steampipe", "query", query, "--output", "json"],
                cwd=self.report_dir,
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
            self.log_error(f"{description} 실패 - {output_file}")
            return False

    def get_networking_queries(self) -> List[Tuple[str, str, str]]:
        return [
            # VPC
            (
                "VPC 정보",
                f"select vpc_id, cidr_block, dhcp_options_id, state, is_default, instance_tenancy, ipv6_cidr_block_association_set, cidr_block_association_set, owner_id, tags from aws_vpc where region = '{self.region}'",
                "networking_vpc.json"
            ),
            
            # 서브넷
            (
                "서브넷 정보",
                f"select subnet_id, vpc_id, cidr_block, available_ip_address_count, availability_zone, availability_zone_id, default_for_az, map_public_ip_on_launch, map_customer_owned_ip_on_launch, state, subnet_arn, outpost_arn, customer_owned_ipv4_pool, ipv6_cidr_block_association_set, assign_ipv6_address_on_creation, ipv6_native, private_dns_name_options_on_launch, tags from aws_vpc_subnet where region = '{self.region}'",
                "networking_subnets.json"
            ),
            
            # 보안 그룹
            (
                "보안 그룹 정보",
                f"select group_id, group_name, description, vpc_id, owner_id, ip_permissions, ip_permissions_egress, tags from aws_vpc_security_group where region = '{self.region}'",
                "security_groups.json"
            ),
            
            # 라우팅 테이블
            (
                "라우팅 테이블 정보",
                f"select route_table_id, vpc_id, routes, associations, propagating_vgws, owner_id, tags from aws_vpc_route_table where region = '{self.region}'",
                "networking_route_tables.json"
            ),
            
            # 인터넷 게이트웨이
            (
                "인터넷 게이트웨이 정보",
                f"select internet_gateway_id, attachments, owner_id, tags from aws_vpc_internet_gateway where region = '{self.region}'",
                "networking_igw.json"
            ),
            
            # NAT 게이트웨이
            (
                "NAT 게이트웨이 정보",
                f"select nat_gateway_id, vpc_id, subnet_id, state, failure_code, failure_message, create_time, delete_time, nat_gateway_addresses, connectivity_type, tags from aws_vpc_nat_gateway where region = '{self.region}'",
                "networking_nat.json"
            ),
            
            # VPC 엔드포인트
            (
                "VPC 엔드포인트 정보",
                f"select vpc_endpoint_id, vpc_id, service_name, vpc_endpoint_type, state, creation_timestamp, route_table_ids, subnet_ids, groups, private_dns_enabled, requester_managed, network_interface_ids, dns_entries, policy_document, tags from aws_vpc_endpoint where region = '{self.region}'",
                "networking_vpc_endpoints.json"
            ),
            
            # 네트워크 ACL
            (
                "네트워크 ACL 정보",
                f"select network_acl_id, vpc_id, is_default, entries, associations, owner_id, tags from aws_vpc_network_acl where region = '{self.region}'",
                "networking_acl.json"
            )
        ]

    def run_collection(self):
        self.log_info("🚀 Steampipe 기반 네트워킹 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        self.log_info("🌐 네트워킹 리소스 수집 시작...")
        
        queries = self.get_networking_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        self.log_success("네트워킹 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 네트워킹 리소스 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeNetworkingCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
