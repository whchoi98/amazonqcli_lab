#!/usr/bin/env python3
"""
Steampipe 기반 컴퓨팅 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

class SteampipeComputeCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 로그 파일 설정
        self.log_file = self.report_dir / "steampipe_compute_collection.log"
        self.error_log = self.report_dir / "steampipe_compute_errors.log"
        
        # 로그 파일 초기화
        self.log_file.write_text("")
        self.error_log.write_text("")
        
        # 카운터
        self.success_count = 0
        self.total_count = 0

    def log_info(self, message: str):
        """정보 로그"""
        print(f"\033[0;34m[INFO]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[INFO] {message}\n")

    def log_success(self, message: str):
        """성공 로그"""
        print(f"\033[0;32m[SUCCESS]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[SUCCESS] {message}\n")

    def log_warning(self, message: str):
        """경고 로그"""
        print(f"\033[1;33m[WARNING]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[WARNING] {message}\n")

    def log_error(self, message: str):
        """에러 로그"""
        print(f"\033[0;31m[ERROR]\033[0m {message}")
        with open(self.error_log, 'a') as f:
            f.write(f"[ERROR] {message}\n")

    def execute_steampipe_query(self, description: str, query: str, output_file: str) -> bool:
        """Steampipe 쿼리 실행"""
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
            self.log_error(f"{description} 실패 - {output_file}: {e.stderr}")
            return False

    def get_compute_queries(self) -> List[Tuple[str, str, str]]:
        """컴퓨팅 서비스 쿼리 목록 반환"""
        return [
            # EC2 인스턴스
            (
                "EC2 인스턴스",
                f"select instance_id, instance_type, instance_state, private_ip_address, public_ip_address, subnet_id, vpc_id, availability_zone, launch_time, image_id, key_name, monitoring, security_groups, tags from aws_ec2_instance where region = '{self.region}'",
                "compute_ec2_instances.json"
            ),
            
            # Auto Scaling 그룹
            (
                "Auto Scaling 그룹",
                f"select auto_scaling_group_name, auto_scaling_group_arn, launch_configuration_name, launch_template, min_size, max_size, desired_capacity, default_cooldown, availability_zones, load_balancer_names, target_group_arns, health_check_type, health_check_grace_period, placement_group, vpc_zone_identifier, termination_policies, new_instances_protected_from_scale_in, service_linked_role_arn, max_instance_lifetime, capacity_rebalance, warm_pool_configuration, predicted_capacity, warm_pool_size, instances, tags from aws_ec2_autoscaling_group where region = '{self.region}'",
                "compute_asg_detailed.json"
            ),
            
            # Application Load Balancer
            (
                "Application Load Balancer",
                f"select load_balancer_arn, dns_name, canonical_hosted_zone_id, created_time, load_balancer_name, scheme, vpc_id, state, type, availability_zones, security_groups, ip_address_type, customer_owned_ipv4_pool, tags from aws_ec2_application_load_balancer where region = '{self.region}'",
                "compute_alb_detailed.json"
            ),
            
            # Network Load Balancer
            (
                "Network Load Balancer",
                f"select load_balancer_arn, dns_name, canonical_hosted_zone_id, created_time, load_balancer_name, scheme, vpc_id, state, type, availability_zones, ip_address_type, customer_owned_ipv4_pool, tags from aws_ec2_network_load_balancer where region = '{self.region}'",
                "compute_nlb_detailed.json"
            ),
            
            # Target Groups
            (
                "Target Groups",
                f"select target_group_arn, target_group_name, protocol, port, vpc_id, health_check_protocol, health_check_port, health_check_enabled, health_check_interval_seconds, health_check_timeout_seconds, healthy_threshold_count, unhealthy_threshold_count, health_check_path, matcher, load_balancer_arns, target_type, protocol_version, ip_address_type, tags from aws_ec2_target_group where region = '{self.region}'",
                "compute_target_groups.json"
            ),
            
            # Launch Templates
            (
                "Launch Templates",
                f"select launch_template_id, launch_template_name, create_time, created_by, default_version_number, latest_version_number, tags from aws_ec2_launch_template where region = '{self.region}'",
                "compute_launch_templates.json"
            ),
            
            # AMI
            (
                "AMI 이미지",
                f"select image_id, name, description, architecture, creation_date, image_location, image_type, public, kernel_id, owner_id, platform, platform_details, ramdisk_id, root_device_name, root_device_type, sriov_net_support, state, state_reason, usage_operation, virtualization_type, hypervisor, image_owner_alias, ena_support, boot_mode, tpm_support, imds_support, source_instance_id, deprecation_time, tags from aws_ec2_ami where region = '{self.region}' and owner_id = account_id",
                "compute_ami_owned.json"
            ),
            
            # Key Pairs
            (
                "EC2 Key Pairs",
                f"select key_name, key_fingerprint, key_type, public_key_material, create_time, tags from aws_ec2_key_pair where region = '{self.region}'",
                "compute_key_pairs.json"
            ),
            
            # Placement Groups
            (
                "Placement Groups",
                f"select group_name, group_id, strategy, partition_count, state, tags from aws_ec2_placement_group where region = '{self.region}'",
                "compute_placement_groups.json"
            ),
            
            # Elastic IPs
            (
                "Elastic IP 주소",
                f"select public_ip, allocation_id, association_id, domain, instance_id, network_interface_id, network_interface_owner_id, private_ip_address, public_ipv4_pool, network_border_group, customer_owned_ip, customer_owned_ipv4_pool, carrier_ip, tags from aws_ec2_eip where region = '{self.region}'",
                "compute_elastic_ips.json"
            )
        ]

    def run_collection(self):
        """전체 수집 프로세스 실행"""
        self.log_info("🚀 Steampipe 기반 컴퓨팅 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        self.log_info("💻 컴퓨팅 리소스 수집 시작...")
        
        # 각 쿼리 실행
        queries = self.get_compute_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("컴퓨팅 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 컴퓨팅 리소스 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeComputeCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
