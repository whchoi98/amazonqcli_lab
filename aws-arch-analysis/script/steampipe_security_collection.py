#!/usr/bin/env python3
"""
Steampipe 기반 보안 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

class SteampipeSecurityCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_security_collection.log"
        self.error_log = self.report_dir / "steampipe_security_errors.log"
        
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

    def get_security_queries(self) -> List[Tuple[str, str, str]]:
        return [
            # IAM 사용자
            (
                "IAM 사용자",
                "select name, user_id, arn, path, create_date, password_last_used, mfa_enabled, access_keys, attached_policy_arns, inline_policies, groups, login_profile, tags from aws_iam_user",
                "security_iam_users.json"
            ),
            
            # IAM 역할
            (
                "IAM 역할",
                "select name, role_id, arn, path, create_date, assume_role_policy_document, description, max_session_duration, permissions_boundary, attached_policy_arns, inline_policies, instance_profile_arns, tags from aws_iam_role",
                "security_iam_roles.json"
            ),
            
            # IAM 정책
            (
                "IAM 정책",
                "select name, policy_id, arn, path, default_version_id, attachment_count, permissions_boundary_usage_count, is_attachable, description, create_date, update_date, policy_version_list, tags from aws_iam_policy where is_aws_managed = false",
                "security_iam_policies.json"
            ),
            
            # KMS 키
            (
                "KMS 키",
                f"select key_id, arn, creation_date, description, enabled, key_state, key_usage, key_spec, key_manager, origin, valid_to, deletion_date, custom_key_store_id, cloud_hsm_cluster_id, expiration_model, multi_region, multi_region_configuration, pending_deletion_window_in_days, replica_keys, tags from aws_kms_key where region = '{self.region}'",
                "security_kms_keys.json"
            ),
            
            # CloudTrail
            (
                "CloudTrail",
                f"select name, trail_arn, s3_bucket_name, s3_key_prefix, sns_topic_name, sns_topic_arn, include_global_service_events, is_multi_region_trail, home_region, is_organization_trail, has_custom_event_selectors, has_insight_selectors, is_logging, latest_delivery_error, latest_delivery_time, latest_digest_delivery_error, latest_digest_delivery_time, latest_notification_error, latest_notification_time, start_logging_time, stop_logging_time, latest_cloud_watch_logs_delivery_error, latest_cloud_watch_logs_delivery_time, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn, kms_key_id, event_selectors, insight_selectors, tags from aws_cloudtrail_trail where region = '{self.region}'",
                "security_cloudtrail.json"
            ),
            
            # Config
            (
                "AWS Config",
                f"select name, configuration_recorder_arn, role_arn, recording_group, status from aws_config_configuration_recorder where region = '{self.region}'",
                "security_config_recorders.json"
            ),
            
            # GuardDuty
            (
                "GuardDuty 탐지기",
                f"select detector_id, created_at, finding_publishing_frequency, service_role, status, updated_at, data_sources, tags from aws_guardduty_detector where region = '{self.region}'",
                "security_guardduty_detectors.json"
            ),
            
            # Security Hub
            (
                "Security Hub",
                f"select hub_arn, subscribed_at, auto_enable_controls, control_finding_generator from aws_securityhub_hub where region = '{self.region}'",
                "security_hub.json"
            ),
            
            # WAF Web ACL
            (
                "WAF Web ACL",
                f"select name, id, arn, default_action, description, rules, capacity, managed_by_firewall_manager, label_namespace, custom_response_bodies, tags from aws_wafv2_web_acl where region = '{self.region}'",
                "security_waf_web_acls.json"
            )
        ]

    def run_collection(self):
        self.log_info("🚀 Steampipe 기반 보안 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        self.log_info("🔒 보안 리소스 수집 시작...")
        
        queries = self.get_security_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        self.log_success("보안 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 보안 리소스 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeSecurityCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
