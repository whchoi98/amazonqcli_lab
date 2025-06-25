#!/usr/bin/env python3
"""
Steampipe 기반 스토리지 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

class SteampipeStorageCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 로그 파일 설정
        self.log_file = self.report_dir / "steampipe_storage_collection.log"
        self.error_log = self.report_dir / "steampipe_storage_errors.log"
        
        # 로그 파일 초기화
        self.log_file.write_text("")
        self.error_log.write_text("")
        
        # 카운터
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

    def get_storage_queries(self) -> List[Tuple[str, str, str]]:
        return [
            # S3 버킷
            (
                "S3 버킷",
                f"select name, arn, creation_date, bucket_policy_is_public, block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets, bucket_policy, acl, logging, versioning, server_side_encryption_configuration, website_configuration, notification_configuration, lifecycle_rules, replication, object_lock_configuration, tags from aws_s3_bucket",
                "storage_s3_buckets.json"
            ),
            
            # EBS 볼륨
            (
                "EBS 볼륨",
                f"select volume_id, volume_type, size, state, create_time, availability_zone, snapshot_id, encrypted, kms_key_id, iops, throughput, multi_attach_enabled, attachments, tags from aws_ebs_volume where region = '{self.region}'",
                "storage_ebs_volumes.json"
            ),
            
            # EBS 스냅샷
            (
                "EBS 스냅샷",
                f"select snapshot_id, description, encrypted, kms_key_id, owner_id, progress, start_time, state, state_message, volume_id, volume_size, owner_alias, outpost_arn, storage_tier, restore_expiry_time, tags from aws_ebs_snapshot where region = '{self.region}' and owner_id = account_id",
                "storage_ebs_snapshots.json"
            ),
            
            # EFS 파일 시스템
            (
                "EFS 파일 시스템",
                f"select file_system_id, file_system_arn, creation_token, creation_time, life_cycle_state, name, number_of_mount_targets, owner_id, performance_mode, provisioned_throughput_in_mibps, throughput_mode, encrypted, kms_key_id, policy, backup_policy, replication_overwrite_protection, tags from aws_efs_file_system where region = '{self.region}'",
                "storage_efs_filesystems.json"
            ),
            
            # FSx 파일 시스템
            (
                "FSx 파일 시스템",
                f"select file_system_id, file_system_type, file_system_type_version, lifecycle_state, failure_details, storage_capacity, storage_type, vpc_id, subnet_ids, network_interface_ids, dns_name, kms_key_id, resource_arn, creation_time, lustre_configuration, windows_configuration, ontap_configuration, open_zfs_configuration, tags from aws_fsx_file_system where region = '{self.region}'",
                "storage_fsx_filesystems.json"
            ),
            
            # Backup 볼트
            (
                "AWS Backup 볼트",
                f"select backup_vault_name, backup_vault_arn, creation_date, creator_request_id, number_of_recovery_points, locked, min_retention_days, max_retention_days, lock_date from aws_backup_vault where region = '{self.region}'",
                "storage_backup_vaults.json"
            ),
            
            # Storage Gateway
            (
                "Storage Gateway",
                f"select gateway_id, gateway_arn, gateway_name, gateway_timezone, gateway_type, gateway_state, software_version, ec2_instance_id, ec2_instance_region, endpoint_type, medium_changer_type, vtl_device_type, smb_guest_password_set, smb_security_strategy, file_shares_visible, tags from aws_storagegateway_gateway where region = '{self.region}'",
                "storage_gateway.json"
            )
        ]

    def run_collection(self):
        self.log_info("🚀 Steampipe 기반 스토리지 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        self.log_info("💾 스토리지 리소스 수집 시작...")
        
        queries = self.get_storage_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        self.log_success("스토리지 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 스토리지 리소스 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeStorageCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
