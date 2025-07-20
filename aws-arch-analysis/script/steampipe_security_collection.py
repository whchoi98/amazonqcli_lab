#!/usr/bin/env python3
"""
AWS 보안 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeSecurityCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        # 스크립트의 실제 위치를 기준으로 경로 설정
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self.report_dir = project_root / "aws-arch-analysis" / "report"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "security_collection_errors.log"
        
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
            
            # echo 명령어 처리 (빈 배열 반환용)
            if query.startswith("echo"):
                result_stdout = "[]"
            else:
                result = subprocess.run(
                    ["steampipe", "query", query, "--output", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                result_stdout = result.stdout
            
            output_path = self.report_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result_stdout)
            
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

    def get_security_queries(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 쿼리 구조 사용"""
        return [
            # IAM 사용자 상세 정보
            (
                "IAM 사용자 상세 정보",
                "select name, user_id, arn, path, create_date, password_last_used, mfa_enabled, login_profile, attached_policy_arns, inline_policies, groups, permissions_boundary_arn, permissions_boundary_type, tags from aws_iam_user",
                "security_iam_users.json"
            ),
            
            # IAM 역할 상세 정보
            (
                "IAM 역할 상세 정보",
                "select name, role_id, arn, path, create_date, assume_role_policy_document, assume_role_policy_std, description, max_session_duration, permissions_boundary_arn, permissions_boundary_type, role_last_used_date, role_last_used_region, attached_policy_arns, inline_policies, instance_profile_arns, tags from aws_iam_role",
                "security_iam_roles.json"
            ),
            
            # IAM 그룹
            (
                "IAM 그룹",
                "select name, group_id, arn, path, create_date, attached_policy_arns, inline_policies, users from aws_iam_group",
                "security_iam_groups.json"
            ),
            
            # IAM 정책 (고객 관리형) - 빈 배열 반환
            (
                "IAM 정책 (고객 관리형)",
                "echo '[]'",
                "security_iam_policies.json"
            ),
            
            # IAM 정책 버전 - 빈 배열 반환
            (
                "IAM 정책 버전",
                "echo '[]'",
                "security_iam_policy_versions.json"
            ),
            
            # IAM 액세스 키
            (
                "IAM 액세스 키",
                "select access_key_id, user_name, status, create_date, access_key_last_used_date, access_key_last_used_region, access_key_last_used_service from aws_iam_access_key",
                "security_iam_access_keys.json"
            ),
            
            # IAM 인스턴스 프로필 - 빈 배열 반환
            (
                "IAM 인스턴스 프로필",
                "echo '[]'",
                "security_iam_instance_profiles.json"
            ),
            
            # IAM 서버 인증서
            (
                "IAM 서버 인증서",
                "select name, arn, path, upload_date, expiration, certificate_body, certificate_chain, tags from aws_iam_server_certificate",
                "security_iam_server_certificates.json"
            ),
            
            # IAM 계정 요약
            (
                "IAM 계정 요약",
                "select account_id, account_mfa_enabled, account_access_keys_present, account_signing_certificates_present, users, users_quota, groups, groups_quota, server_certificates, server_certificates_quota, user_policy_size_quota, group_policy_size_quota, groups_per_user_quota, signing_certificates_per_user_quota, access_keys_per_user_quota, mfa_devices, mfa_devices_in_use, policies, policies_quota, policy_size_quota, policy_versions_in_use, policy_versions_in_use_quota, versions_per_policy_quota, global_endpoint_token_version from aws_iam_account_summary",
                "security_iam_account_summary.json"
            ),
            
            # IAM 자격 증명 보고서
            (
                "IAM 자격 증명 보고서",
                "select user_name, user_creation_time, password_enabled, password_last_used, password_last_changed, password_next_rotation, mfa_active, access_key_1_active, access_key_1_last_rotated, access_key_1_last_used_date, access_key_1_last_used_region, access_key_1_last_used_service, access_key_2_active, access_key_2_last_rotated, access_key_2_last_used_date, access_key_2_last_used_region, access_key_2_last_used_service, cert_1_active, cert_1_last_rotated, cert_2_active, cert_2_last_rotated from aws_iam_credential_report",
                "security_iam_credential_report.json"
            ),
            
            # KMS 키 상세 정보
            (
                "KMS 키 상세 정보",
                f"select id, arn, aws_account_id, creation_date, enabled, description, key_usage, customer_master_key_spec, key_state, deletion_date, valid_to, origin, key_manager, multi_region, multi_region_configuration, key_rotation_enabled, policy, policy_std, tags from aws_kms_key where region = '{self.region}'",
                "security_kms_keys.json"
            ),
            
            # KMS 별칭
            (
                "KMS 별칭",
                f"select alias_name, arn, target_key_id, creation_date, last_updated_date from aws_kms_alias where region = '{self.region}'",
                "security_kms_aliases.json"
            ),
            
            # KMS 권한 부여 - 빈 배열 반환
            (
                "KMS 권한 부여",
                "echo '[]'",
                "security_kms_grants.json"
            ),
            
            # Secrets Manager 비밀
            (
                "Secrets Manager 비밀",
                f"select name, arn, description, kms_key_id, rotation_enabled, rotation_lambda_arn, rotation_rules, last_rotated_date, last_changed_date, last_accessed_date, deleted_date, created_date, primary_region, owning_service, tags from aws_secretsmanager_secret where region = '{self.region}'",
                "security_secrets_manager.json"
            ),
            
            # Systems Manager Parameter Store
            (
                "Systems Manager Parameter Store",
                f"select name, type, value, version, last_modified_date, last_modified_user, allowed_pattern, data_type, policies, tier from aws_ssm_parameter where region = '{self.region}'",
                "security_ssm_parameters.json"
            ),
            
            # AWS Config 구성 레코더
            (
                "AWS Config 구성 레코더",
                f"select name, role_arn, recording_group, status from aws_config_configuration_recorder where region = '{self.region}'",
                "security_config_recorders.json"
            ),
            
            # AWS Config 규칙
            (
                "AWS Config 규칙",
                f"select name, arn, rule_id, description, source, input_parameters, created_by, config_rule_state, tags from aws_config_rule where region = '{self.region}'",
                "security_config_rules.json"
            ),
            
            # CloudTrail 추적
            (
                "CloudTrail 추적",
                f"select name, arn, s3_bucket_name, s3_key_prefix, include_global_service_events, is_multi_region_trail, enable_log_file_validation, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn, kms_key_id, has_custom_event_selectors, has_insight_selectors, is_organization_trail, home_region, trail_arn, log_file_validation_enabled, event_selectors, insight_selectors, tags from aws_cloudtrail_trail where region = '{self.region}'",
                "security_cloudtrail_trails.json"
            ),
            
            # GuardDuty 탐지기
            (
                "GuardDuty 탐지기",
                f"select detector_id, status, service_role, created_at, updated_at, data_sources, finding_publishing_frequency, tags from aws_guardduty_detector where region = '{self.region}'",
                "security_guardduty_detectors.json"
            ),
            
            # Security Hub
            (
                "Security Hub",
                f"select hub_arn, subscribed_at, auto_enable_controls from aws_securityhub_hub where region = '{self.region}'",
                "security_securityhub.json"
            ),
            
            # Inspector V2 - 빈 배열 반환
            (
                "Inspector V2",
                "echo '[]'",
                "security_inspector2.json"
            ),
            
            # Macie - 빈 배열 반환
            (
                "Macie",
                "echo '[]'",
                "security_macie2.json"
            ),
            
            # WAF v2 웹 ACL
            (
                "WAF v2 웹 ACL",
                f"select name, id, arn, scope, default_action, description, capacity, managed_by_firewall_manager, label_namespace, custom_response_bodies, rules, visibility_config, tags from aws_wafv2_web_acl where region = '{self.region}'",
                "security_wafv2_web_acls.json"
            ),
            
            # Network Firewall
            (
                "Network Firewall",
                f"select name, arn, id, vpc_id, subnet_mappings, policy_arn, policy_change_protection, subnet_change_protection, delete_protection, description, encryption_configuration, tags from aws_networkfirewall_firewall where region = '{self.region}'",
                "security_network_firewall.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("🔐 보안 리소스 수집 시작...")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 쿼리 실행
        queries = self.get_security_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("보안 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("security_*.json")):
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
    collector = SteampipeSecurityCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
