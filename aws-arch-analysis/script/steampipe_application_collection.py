#!/usr/bin/env python3
"""
Steampipe 기반 API 및 애플리케이션 서비스 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Tuple, Optional

class SteampipeApplicationCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 로그 파일 설정
        self.log_file = self.report_dir / "steampipe_application_collection.log"
        self.error_log = self.report_dir / "steampipe_application_errors.log"
        
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
            # Steampipe 쿼리 실행
            result = subprocess.run(
                ["steampipe", "query", query, "--output", "json"],
                cwd=self.report_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 결과를 파일에 저장
            output_path = self.report_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            # 파일 크기 확인
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
            with open(self.error_log, 'a') as f:
                f.write(f"Query failed: {query}\nError: {e.stderr}\n")
            return False
        except Exception as e:
            self.log_error(f"{description} 예상치 못한 오류 - {output_file}: {str(e)}")
            return False

    def check_steampipe_plugin(self) -> bool:
        """Steampipe AWS 플러그인 확인"""
        try:
            result = subprocess.run(
                ["steampipe", "plugin", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            return "aws" in result.stdout
        except subprocess.CalledProcessError:
            return False

    def install_steampipe_plugin(self):
        """Steampipe AWS 플러그인 설치"""
        try:
            subprocess.run(
                ["steampipe", "plugin", "install", "aws"],
                check=True
            )
            self.log_success("AWS 플러그인 설치 완료")
        except subprocess.CalledProcessError as e:
            self.log_error(f"AWS 플러그인 설치 실패: {e}")

    def get_application_queries(self) -> List[Tuple[str, str, str]]:
        """애플리케이션 서비스 쿼리 목록 반환"""
        return [
            # API Gateway
            (
                "API Gateway REST API",
                f"select id, name, description, created_date, version, warnings, binary_media_types, minimum_compression_size, api_key_source, endpoint_configuration, policy, tags from aws_api_gateway_rest_api where region = '{self.region}'",
                "application_api_gateway_rest_apis.json"
            ),
            (
                "API Gateway 스테이지",
                f"select rest_api_id, stage_name, deployment_id, description, created_date, last_updated_date, cache_cluster_enabled, cache_cluster_size, cache_cluster_status, method_settings, variables, documentation_version, access_log_settings, canary_settings, tracing_config, web_acl_arn, tags from aws_api_gateway_stage where region = '{self.region}'",
                "application_api_gateway_stages.json"
            ),
            (
                "API Gateway 도메인 이름",
                f"select domain_name, certificate_name, certificate_arn, certificate_upload_date, regional_domain_name, regional_hosted_zone_id, regional_certificate_name, regional_certificate_arn, distribution_domain_name, distribution_hosted_zone_id, endpoint_configuration, domain_name_status, domain_name_status_message, security_policy, tags from aws_api_gateway_domain_name where region = '{self.region}'",
                "application_api_gateway_domain_names.json"
            ),
            (
                "API Gateway 사용 계획",
                f"select id, name, description, api_stages, throttle, quota, product_code, tags from aws_api_gateway_usage_plan where region = '{self.region}'",
                "application_api_gateway_usage_plans.json"
            ),
            (
                "API Gateway API 키",
                f"select id, name, description, enabled, created_date, last_updated_date, stage_keys, tags from aws_api_gateway_api_key where region = '{self.region}'",
                "application_api_gateway_api_keys.json"
            ),
            
            # SNS
            (
                "SNS 토픽",
                f"select topic_arn, name, display_name, owner, subscriptions_confirmed, subscriptions_deleted, subscriptions_pending, policy, delivery_policy, effective_delivery_policy, kms_master_key_id, fifo_topic, content_based_deduplication, tags from aws_sns_topic where region = '{self.region}'",
                "application_sns_topics.json"
            ),
            (
                "SNS 구독",
                f"select subscription_arn, topic_arn, owner, protocol, endpoint, confirmation_was_authenticated, delivery_policy, effective_delivery_policy, filter_policy, pending_confirmation, raw_message_delivery, redrive_policy, subscription_role_arn from aws_sns_topic_subscription where region = '{self.region}'",
                "application_sns_subscriptions.json"
            ),
            
            # SQS
            (
                "SQS 큐",
                f"select queue_url, name, attributes, tags from aws_sqs_queue where region = '{self.region}'",
                "application_sqs_queues.json"
            ),
            
            # EventBridge
            (
                "EventBridge 규칙",
                f"select name, arn, event_pattern, schedule_expression, state, description, role_arn, managed_by, event_bus_name, tags from aws_eventbridge_rule where region = '{self.region}'",
                "application_eventbridge_rules.json"
            ),
            
            # Lambda
            (
                "Lambda 함수",
                f"select function_name, function_arn, runtime, role, handler, code_size, description, timeout, memory_size, last_modified, code_sha256, version, vpc_config, environment, dead_letter_config, kms_key_arn, tracing_config, master_arn, revision_id, layers, state, state_reason, state_reason_code, last_update_status, last_update_status_reason, last_update_status_reason_code, file_system_configs, image_config_response, signing_profile_version_arn, signing_job_arn, architectures, ephemeral_storage, snap_start, runtime_version_config, logging_config, tags from aws_lambda_function where region = '{self.region}'",
                "iac_lambda_functions.json"
            ),
            
            # Step Functions
            (
                "Step Functions 상태 머신",
                f"select state_machine_arn, name, status, definition, role_arn, type, creation_date, logging_configuration, tracing_configuration, tags from aws_sfn_state_machine where region = '{self.region}'",
                "application_step_functions.json"
            ),
            
            # Kinesis
            (
                "Kinesis 스트림",
                f"select stream_name, stream_arn, stream_status, stream_mode_details, shard_count, has_more_shards, retention_period, stream_creation_timestamp, encryption_type, key_id, tags from aws_kinesis_stream where region = '{self.region}'",
                "application_kinesis_streams.json"
            ),
            
            # Cognito
            (
                "Cognito 사용자 풀",
                f"select id, name, status, lambda_config, auto_verified_attributes, username_attributes, sms_verification_message, email_verification_message, email_verification_subject, verification_message_template, sms_authentication_message, mfa_configuration, device_configuration, estimated_number_of_users, email_configuration, sms_configuration, user_pool_tags, admin_create_user_config, user_pool_add_ons, username_configuration, arn, custom_domain, domain, tags from aws_cognito_user_pool where region = '{self.region}'",
                "application_cognito_user_pools.json"
            ),
            
            # AppSync
            (
                "AppSync GraphQL API",
                f"select api_id, name, authentication_type, log_config, user_pool_config, open_id_connect_config, arn, uris, tags, additional_authentication_providers, xray_enabled, lambda_authorizer_config, dns, waf_web_acl_arn, api_type, merged_api_execution_role_arn, owner, owner_contact, introspection_config, query_depth_limit, resolver_count_limit, enhanced_metrics_config from aws_appsync_graphql_api where region = '{self.region}'",
                "application_appsync_apis.json"
            ),
            
            # SES
            (
                "SES 구성 세트",
                f"select name, tracking_options, delivery_options, reputation_tracking_enabled, tags from aws_sesv2_configuration_set where region = '{self.region}'",
                "application_ses_configuration_sets.json"
            )
        ]

    def run_collection(self):
        """전체 수집 프로세스 실행"""
        self.log_info("🚀 Steampipe 기반 API 및 애플리케이션 서비스 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        # Steampipe AWS 플러그인 확인
        self.log_info("Steampipe AWS 플러그인 확인 중...")
        if not self.check_steampipe_plugin():
            self.log_warning("AWS 플러그인이 설치되지 않았습니다. 설치 중...")
            self.install_steampipe_plugin()
        
        self.log_info("🌐 API 및 애플리케이션 서비스 수집 시작...")
        
        # 각 쿼리 실행
        queries = self.get_application_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("API 및 애플리케이션 서비스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")
            
            # 최근 오류 5줄 표시
            try:
                with open(self.error_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        print("\n최근 오류 (마지막 5줄):")
                        for line in lines[-5:]:
                            print(line.strip())
            except FileNotFoundError:
                print("오류 로그가 없습니다.")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 애플리케이션 서비스 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeApplicationCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
