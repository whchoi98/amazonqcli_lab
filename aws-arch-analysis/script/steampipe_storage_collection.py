#!/usr/bin/env python3
"""
AWS 스토리지 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeStorageCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        self.report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "storage_collection_errors.log"
        
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

    def get_storage_queries(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 쿼리 구조 사용"""
        return [
            # EBS 볼륨 상세 정보
            (
                "EBS 볼륨 상세 정보",
                f"select volume_id, volume_type, size, state, encrypted, kms_key_id, availability_zone, create_time, attachments, snapshot_id, iops, throughput, multi_attach_enabled, outpost_arn, fast_restored, tags from aws_ebs_volume where region = '{self.region}'",
                "storage_ebs_volumes.json"
            ),
            
            # EBS 스냅샷 상세 정보
            (
                "EBS 스냅샷 상세 정보",
                f"select snapshot_id, volume_id, volume_size, state, start_time, progress, owner_id, description, encrypted, kms_key_id, data_encryption_key_id, outpost_arn, storage_tier, restore_expiry_time, tags from aws_ebs_snapshot where region = '{self.region}' and owner_id = (select account_id from aws_caller_identity)",
                "storage_ebs_snapshots.json"
            ),
            
            # EBS 암호화 기본 설정
            (
                "EBS 암호화 기본 설정",
                f"select ebs_encryption_by_default, ebs_default_kms_key_id from aws_ec2_regional_settings where region = '{self.region}'",
                "storage_ebs_encryption_default.json"
            ),
            
            # S3 버킷 상세 정보
            (
                "S3 버킷 상세 정보",
                "select name, arn, region, creation_date, lifecycle_rules, logging, event_notification_configuration, object_lock_configuration, policy, policy_std, replication, server_side_encryption_configuration, versioning_enabled, versioning_mfa_delete, website_configuration, block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets, tags from aws_s3_bucket",
                "storage_s3_buckets.json"
            ),
            
            # S3 버킷 정책
            (
                "S3 버킷 정책",
                "select name, policy, policy_std from aws_s3_bucket where policy is not null",
                "storage_s3_bucket_policies.json"
            ),
            
            # S3 버킷 퍼블릭 액세스 차단
            (
                "S3 버킷 퍼블릭 액세스 차단",
                "select name, block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets from aws_s3_bucket",
                "storage_s3_public_access_block.json"
            ),
            
            # S3 버킷 CORS 구성
            (
                "S3 버킷 CORS 구성",
                "select name, cors_rules from aws_s3_bucket where cors_rules is not null",
                "storage_s3_cors.json"
            ),
            
            # S3 버킷 수명 주기 구성
            (
                "S3 버킷 수명 주기 구성",
                "select name, lifecycle_rules from aws_s3_bucket where lifecycle_rules is not null",
                "storage_s3_lifecycle.json"
            ),
            
            # S3 버킷 복제 구성
            (
                "S3 버킷 복제 구성",
                "select name, replication from aws_s3_bucket where replication is not null",
                "storage_s3_replication.json"
            ),
            
            # S3 버킷 버전 관리
            (
                "S3 버킷 버전 관리",
                "select name, versioning_enabled, versioning_mfa_delete from aws_s3_bucket",
                "storage_s3_versioning.json"
            ),
            
            # S3 버킷 로깅
            (
                "S3 버킷 로깅",
                "select name, logging from aws_s3_bucket where logging is not null",
                "storage_s3_logging.json"
            ),
            
            # S3 버킷 알림
            (
                "S3 버킷 알림",
                "select name, event_notification_configuration from aws_s3_bucket where event_notification_configuration is not null",
                "storage_s3_notifications.json"
            ),
            
            # S3 버킷 웹사이트 구성
            (
                "S3 버킷 웹사이트 구성",
                "select name, website_configuration from aws_s3_bucket where website_configuration is not null",
                "storage_s3_website.json"
            ),
            
            # S3 Glacier 볼트
            (
                "S3 Glacier 볼트",
                f"select vault_name, vault_arn, creation_date, last_inventory_date, number_of_archives, size_in_bytes, tags from aws_glacier_vault where region = '{self.region}'",
                "storage_glacier_vaults.json"
            ),
            
            # EFS 파일 시스템 상세 정보
            (
                "EFS 파일 시스템 상세 정보",
                f"select file_system_id, arn, creation_token, creation_time, life_cycle_state, name, number_of_mount_targets, owner_id, performance_mode, provisioned_throughput_in_mibps, throughput_mode, encrypted, kms_key_id, automatic_backups, replication_overwrite_protection, availability_zone_name, availability_zone_id, tags from aws_efs_file_system where region = '{self.region}'",
                "storage_efs_file_systems.json"
            ),
            
            # EFS 액세스 포인트
            (
                "EFS 액세스 포인트",
                f"select access_point_id, access_point_arn, file_system_id, posix_user, root_directory, client_token, life_cycle_state, name, owner_id, tags from aws_efs_access_point where region = '{self.region}'",
                "storage_efs_access_points.json"
            ),
            
            # EFS 마운트 타겟
            (
                "EFS 마운트 타겟",
                f"select mount_target_id, file_system_id, subnet_id, life_cycle_state, ip_address, network_interface_id, availability_zone_id, availability_zone_name, vpc_id, owner_id from aws_efs_mount_target where region = '{self.region}'",
                "storage_efs_mount_targets.json"
            ),
            
            # EFS 백업 정책
            (
                "EFS 백업 정책",
                f"select file_system_id, backup_policy from aws_efs_backup_policy where region = '{self.region}'",
                "storage_efs_backup_policies.json"
            ),
            
            # FSx 파일 시스템
            (
                "FSx 파일 시스템",
                f"select file_system_id, file_system_type, file_system_type_version, lifecycle, failure_details, storage_capacity, storage_type, vpc_id, subnet_ids, network_interface_ids, dns_name, kms_key_id, arn, tags, creation_time, lustre_configuration, ontap_configuration, open_zfs_configuration, windows_configuration from aws_fsx_file_system where region = '{self.region}'",
                "storage_fsx_file_systems.json"
            ),
            
            # FSx 백업
            (
                "FSx 백업",
                f"select backup_id, file_system_id, type, lifecycle, failure_details, progress_percent, creation_time, kms_key_id, resource_arn, tags, volume_id, source_backup_id, source_backup_region, resource_type, backup_type from aws_fsx_backup where region = '{self.region}'",
                "storage_fsx_backups.json"
            ),
            
            # Storage Gateway
            (
                "Storage Gateway",
                f"select gateway_id, gateway_name, gateway_timezone, gateway_type, gateway_state, ec2_instance_id, ec2_instance_region, host_environment, host_environment_id, endpoint_type, gateway_capacity, supported_gateway_capacities, deprecation_date, software_updates_end_date, tags from aws_storagegateway_gateway where region = '{self.region}'",
                "storage_gateway_gateways.json"
            ),
            
            # AWS Backup 볼트
            (
                "AWS Backup 볼트",
                f"select name, arn, creation_date, creator_request_id, number_of_recovery_points, locked, min_retention_days, max_retention_days, lock_date, encryption_key_arn from aws_backup_vault where region = '{self.region}'",
                "storage_backup_vaults.json"
            ),
            
            # AWS Backup 계획
            (
                "AWS Backup 계획",
                f"select backup_plan_id, arn, name, creation_date, deletion_date, last_execution_date, advanced_backup_settings, backup_plan from aws_backup_plan where region = '{self.region}'",
                "storage_backup_plans.json"
            ),
            
            # AWS Backup 작업
            (
                "AWS Backup 작업",
                f"select job_id, backup_vault_name, resource_arn, creation_date, completion_date, status, status_message, percent_done, backup_size, iam_role_arn, expected_completion_date, start_by, resource_type, bytes_transferred, backup_options, backup_type, parent_job_id, is_parent from aws_backup_job where region = '{self.region}'",
                "storage_backup_jobs.json"
            ),
            
            # Data Lifecycle Manager 정책
            (
                "Data Lifecycle Manager 정책",
                f"select policy_id, description, state, status_message, execution_role_arn, date_created, date_modified, policy_details, tags from aws_dlm_lifecycle_policy where region = '{self.region}'",
                "storage_dlm_policies.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("💾 스토리지 리소스 수집 시작...")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 쿼리 실행
        queries = self.get_storage_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("스토리지 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("storage_*.json")):
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
    collector = SteampipeStorageCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
