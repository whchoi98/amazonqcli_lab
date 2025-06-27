#!/usr/bin/env python3
"""
AWS 컴퓨팅 및 서버리스 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeComputeCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        self.report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "compute_collection_errors.log"
        
        # 색상 코드
        self.GREEN = '\033[0;32m'
        self.BLUE = '\033[0;34m'
        self.YELLOW = '\033[1;33m'
        self.RED = '\033[0;31m'
        self.NC = '\033[0m'  # No Color
        
    def log_info(self, message: str):
        print(f"{self.BLUE}ℹ️ {message}{self.NC}")
        
    def log_success(self, message: str):
        print(f"{self.GREEN}✅ {message}{self.NC}")
        
    def log_warning(self, message: str):
        print(f"{self.YELLOW}⚠️ {message}{self.NC}")
        
    def log_error(self, message: str):
        print(f"{self.RED}❌ {message}{self.NC}")

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
            if file_size > 100:
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

    def get_compute_queries(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 쿼리 구조 사용"""
        return [
            # EC2 인스턴스 상세 정보
            (
                "EC2 인스턴스 상세 정보",
                f"select instance_id, instance_type, instance_state, vpc_id, subnet_id, private_ip_address, public_ip_address, private_dns_name, public_dns_name, key_name, security_groups, iam_instance_profile_arn, monitoring_state, placement_availability_zone, platform, architecture, virtualization_type, hypervisor, root_device_type, root_device_name, block_device_mappings, ebs_optimized, ena_support, sriov_net_support, source_dest_check, launch_time, state_transition_reason, usage_operation, usage_operation_update_time, tags from aws_ec2_instance where region = '{self.region}'",
                "compute_ec2_instances.json"
            ),
            
            # EC2 AMI 이미지
            (
                "EC2 AMI 이미지",
                f"select image_id, name, description, state, public, owner_id, architecture, platform, virtualization_type, hypervisor, root_device_type, root_device_name, block_device_mappings, creation_date, deprecation_time, usage_operation, platform_details, image_type, image_location, kernel_id, ramdisk_id, sriov_net_support, ena_support, boot_mode, tags from aws_ec2_ami where region = '{self.region}' and owner_id = (select account_id from aws_caller_identity)",
                "compute_ec2_amis.json"
            ),
            
            # EC2 키 페어
            (
                "EC2 키 페어",
                f"select key_name, key_fingerprint, key_type, key_pair_id, create_time, tags from aws_ec2_key_pair where region = '{self.region}'",
                "compute_ec2_key_pairs.json"
            ),
            
            # EC2 예약 인스턴스
            (
                "EC2 예약 인스턴스",
                f"select reserved_instance_id, instance_type, availability_zone, instance_count, product_description, instance_state, start_time, end_time, duration, usage_price, fixed_price, currency_code, instance_tenancy, offering_class, offering_type, scope, tags from aws_ec2_reserved_instance where region = '{self.region}'",
                "compute_ec2_reserved_instances.json"
            ),
            
            # EC2 스팟 인스턴스 요청
            (
                "EC2 스팟 인스턴스 요청",
                f"select spot_instance_request_id, spot_price, type, state, status, fault, valid_from, valid_until, launch_group, availability_zone_group, launch_specification, instance_id, create_time, product_description, block_duration_minutes, actual_block_hourly_price, tags from aws_ec2_spot_instance_request where region = '{self.region}'",
                "compute_ec2_spot_requests.json"
            ),
            
            # EC2 배치 그룹
            (
                "EC2 배치 그룹",
                f"select group_name, group_id, strategy, partition_count, state, tags from aws_ec2_placement_group where region = '{self.region}'",
                "compute_ec2_placement_groups.json"
            ),
            
            # EC2 시작 템플릿
            (
                "EC2 시작 템플릿",
                f"select launch_template_id, launch_template_name, create_time, created_by, default_version_number, latest_version_number, tags from aws_ec2_launch_template where region = '{self.region}'",
                "compute_ec2_launch_templates.json"
            ),
            
            # EC2 시작 템플릿 버전
            (
                "EC2 시작 템플릿 버전",
                f"select launch_template_id, launch_template_name, version_number, version_description, create_time, created_by, default_version, launch_template_data from aws_ec2_launch_template_version where region = '{self.region}'",
                "compute_ec2_launch_template_versions.json"
            ),
            
            # Application Load Balancer
            (
                "Application Load Balancer 상세 정보",
                f"select arn, name, type, scheme, vpc_id, availability_zones, security_groups, ip_address_type, state_code, state_reason, dns_name, canonical_hosted_zone_id, created_time, load_balancer_attributes, tags from aws_ec2_application_load_balancer where region = '{self.region}'",
                "compute_alb_detailed.json"
            ),
            
            # Network Load Balancer
            (
                "Network Load Balancer 상세 정보",
                f"select arn, name, type, scheme, vpc_id, availability_zones, ip_address_type, state_code, state_reason, dns_name, canonical_hosted_zone_id, created_time, load_balancer_attributes, tags from aws_ec2_network_load_balancer where region = '{self.region}'",
                "compute_nlb_detailed.json"
            ),
            
            # Classic Load Balancer
            (
                "Classic Load Balancer",
                f"select name, dns_name, canonical_hosted_zone_name, canonical_hosted_zone_name_id, vpc_id, subnets, security_groups, instances, availability_zones, backend_server_descriptions, connection_draining, cross_zone_load_balancing, access_log, connection_settings, created_time, scheme, source_security_group, tags from aws_ec2_classic_load_balancer where region = '{self.region}'",
                "compute_clb.json"
            ),
            
            # 타겟 그룹
            (
                "타겟 그룹",
                f"select target_group_arn, target_group_name, protocol, port, vpc_id, health_check_enabled, health_check_interval_seconds, health_check_path, health_check_port, health_check_protocol, health_check_timeout_seconds, healthy_threshold_count, unhealthy_threshold_count, load_balancer_arns, target_type, protocol_version, ip_address_type, tags from aws_ec2_target_group where region = '{self.region}'",
                "compute_target_groups.json"
            ),
            
            # Auto Scaling 그룹
            (
                "Auto Scaling 그룹 상세 정보",
                f"select name, autoscaling_group_arn, min_size, max_size, desired_capacity, default_cooldown, availability_zones, load_balancer_names, target_group_arns, health_check_type, health_check_grace_period, placement_group, vpc_zone_identifier, termination_policies, new_instances_protected_from_scale_in, service_linked_role_arn, max_instance_lifetime, capacity_rebalance, warm_pool_configuration, warm_pool_size, status, suspended_processes, enabled_metrics, tags from aws_ec2_autoscaling_group where region = '{self.region}'",
                "compute_asg_detailed.json"
            ),
            
            # Auto Scaling 시작 구성
            (
                "Auto Scaling 시작 구성",
                f"select launch_configuration_name, launch_configuration_arn, image_id, instance_type, key_name, security_groups, classic_link_vpc_id, classic_link_vpc_security_groups, user_data, instance_monitoring, spot_price, iam_instance_profile, created_time, ebs_optimized, associate_public_ip_address, placement_tenancy, block_device_mappings, metadata_options from aws_ec2_autoscaling_launch_configuration where region = '{self.region}'",
                "compute_asg_launch_configs.json"
            ),
            
            # Auto Scaling 정책
            (
                "Auto Scaling 정책",
                f"select policy_name, policy_arn, auto_scaling_group_name, policy_type, adjustment_type, min_adjustment_step, min_adjustment_magnitude, scaling_adjustment, cooldown, step_adjustments, metric_aggregation_type, estimated_instance_warmup, target_tracking_configuration, enabled, alarms from aws_ec2_autoscaling_policy where region = '{self.region}'",
                "compute_asg_policies.json"
            ),
            
            # Elastic Beanstalk 애플리케이션
            (
                "Elastic Beanstalk 애플리케이션",
                f"select name, description, date_created, date_updated, versions, configuration_templates, resource_lifecycle_config from aws_elastic_beanstalk_application where region = '{self.region}'",
                "compute_beanstalk_applications.json"
            ),
            
            # Elastic Beanstalk 환경
            (
                "Elastic Beanstalk 환경",
                f"select environment_name, environment_id, application_name, version_label, solution_stack_name, platform_arn, template_name, description, endpoint_url, cname, date_created, date_updated, status, abortable_operation_in_progress, health, health_status, resources, tier, environment_links, environment_arn, operations_role from aws_elastic_beanstalk_environment where region = '{self.region}'",
                "compute_beanstalk_environments.json"
            ),
            
            # Lambda 함수
            (
                "Lambda 함수 상세 정보",
                f"select name, arn, runtime, role, handler, code_size, description, timeout, memory_size, last_modified, code_sha_256, version, vpc_id, environment_variables, dead_letter_config_target_arn, kms_key_arn, tracing_config, master_arn, revision_id, layers, state, state_reason, state_reason_code, last_update_status, last_update_status_reason, last_update_status_reason_code, file_system_configs, package_type, architectures, ephemeral_storage, snap_start, logging_config, tags from aws_lambda_function where region = '{self.region}'",
                "compute_lambda_functions.json"
            ),
            
            # Lambda 레이어
            (
                "Lambda 레이어",
                f"select layer_name, layer_arn, version, description, created_date, compatible_runtimes, license_info, compatible_architectures from aws_lambda_layer_version where region = '{self.region}'",
                "compute_lambda_layers.json"
            ),
            
            # Lambda 별칭
            (
                "Lambda 별칭",
                f"select name, alias_arn, function_name, function_version, description, revision_id from aws_lambda_alias where region = '{self.region}'",
                "compute_lambda_aliases.json"
            ),
            
            # Lambda 이벤트 소스 매핑
            (
                "Lambda 이벤트 소스 매핑",
                f"select uuid, arn, function_arn, function_name, last_modified, last_processing_result, state, state_transition_reason, batch_size, maximum_batching_window_in_seconds, parallelization_factor, starting_position, starting_position_timestamp, maximum_record_age_in_seconds, bisect_batch_on_function_error, maximum_retry_attempts, tumbling_window_in_seconds, topics, queues, source_access_configurations, self_managed_event_source, function_response_types, amazon_managed_kafka_event_source_config, self_managed_kafka_event_source_config, scaling_config from aws_lambda_event_source_mapping where region = '{self.region}'",
                "compute_lambda_event_mappings.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("🚀 컴퓨팅 및 서버리스 리소스 수집 시작...")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 쿼리 실행
        queries = self.get_compute_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("컴퓨팅 및 서버리스 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("compute_*.json")):
            file_size = file_path.stat().st_size
            if file_size > 100:
                print(f"{self.GREEN}✓ {file_path.name} ({file_size} bytes){self.NC}")
            else:
                print(f"{self.YELLOW}⚠ {file_path.name} ({file_size} bytes) - 데이터 없음{self.NC}")
        
        # 수집 통계
        print(f"\n{self.BLUE}📊 수집 통계:{self.NC}")
        print(f"총 쿼리 수: {self.total_count}")
        print(f"성공한 쿼리: {self.success_count}")
        print(f"실패한 쿼리: {self.total_count - self.success_count}")
        print(f"성공률: {(self.success_count/self.total_count*100):.1f}%")
        
        if self.error_log.exists():
            print(f"\n{self.YELLOW}⚠️ 오류 로그: {self.error_log}{self.NC}")

def main():
    """메인 함수"""
    region = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-2')
    collector = SteampipeComputeCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
