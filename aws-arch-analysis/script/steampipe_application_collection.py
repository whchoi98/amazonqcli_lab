#!/usr/bin/env python3
"""
AWS 애플리케이션 서비스 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeApplicationCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        self.report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "application_collection_errors.log"
        
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

    def get_application_queries(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 쿼리 구조 사용"""
        return [
            # API Gateway REST API
            (
                "API Gateway REST API",
                f"select id, name, description, created_date, version, warnings, binary_media_types, minimum_compression_size, api_key_source, endpoint_configuration, policy, tags from aws_api_gateway_rest_api where region = '{self.region}'",
                "application_api_gateway_rest_apis.json"
            ),
            
            # API Gateway 스테이지
            (
                "API Gateway 스테이지",
                f"select rest_api_id, stage_name, deployment_id, description, created_date, last_updated_date, cache_cluster_enabled, cache_cluster_size, cache_cluster_status, method_settings, variables, documentation_version, access_log_settings, canary_settings, tracing_config, web_acl_arn, tags from aws_api_gateway_stage where region = '{self.region}'",
                "application_api_gateway_stages.json"
            ),
            
            # API Gateway 도메인 이름
            (
                "API Gateway 도메인 이름",
                f"select domain_name, certificate_name, certificate_arn, certificate_upload_date, regional_domain_name, regional_hosted_zone_id, regional_certificate_name, regional_certificate_arn, distribution_domain_name, distribution_hosted_zone_id, endpoint_configuration, domain_name_status, domain_name_status_message, security_policy, tags from aws_api_gateway_domain_name where region = '{self.region}'",
                "application_api_gateway_domain_names.json"
            ),
            
            # API Gateway 사용 계획
            (
                "API Gateway 사용 계획",
                f"select id, name, description, api_stages, throttle, quota, product_code, tags from aws_api_gateway_usage_plan where region = '{self.region}'",
                "application_api_gateway_usage_plans.json"
            ),
            
            # API Gateway API 키
            (
                "API Gateway API 키",
                f"select id, name, description, enabled, created_date, last_updated_date, stage_keys, tags from aws_api_gateway_api_key where region = '{self.region}'",
                "application_api_gateway_api_keys.json"
            ),
            
            # SNS 토픽
            (
                "SNS 토픽",
                f"select topic_arn, name, display_name, owner, subscriptions_confirmed, subscriptions_deleted, subscriptions_pending, policy, delivery_policy, effective_delivery_policy, kms_master_key_id, fifo_topic, content_based_deduplication, tags from aws_sns_topic where region = '{self.region}'",
                "application_sns_topics.json"
            ),
            
            # SNS 구독
            (
                "SNS 구독",
                f"select subscription_arn, topic_arn, owner, protocol, endpoint, confirmation_was_authenticated, delivery_policy, effective_delivery_policy, filter_policy, pending_confirmation, raw_message_delivery, redrive_policy, subscription_role_arn from aws_sns_topic_subscription where region = '{self.region}'",
                "application_sns_subscriptions.json"
            ),
            
            # SQS 큐
            (
                "SQS 큐",
                f"select queue_url, name, attributes, tags from aws_sqs_queue where region = '{self.region}'",
                "application_sqs_queues.json"
            ),
            
            # EventBridge 규칙
            (
                "EventBridge 규칙",
                f"select name, arn, description, event_pattern, schedule_expression, state, targets, managed_by, event_bus_name, role_arn, tags from aws_eventbridge_rule where region = '{self.region}'",
                "application_eventbridge_rules.json"
            ),
            
            # EventBridge 이벤트 버스
            (
                "EventBridge 이벤트 버스",
                f"select name, arn, policy, tags from aws_eventbridge_bus where region = '{self.region}'",
                "application_eventbridge_buses.json"
            ),
            
            # Step Functions 상태 머신
            (
                "Step Functions 상태 머신",
                f"select state_machine_arn, name, status, type, definition, role_arn, creation_date, logging_configuration, tags from aws_sfn_state_machine where region = '{self.region}'",
                "application_stepfunctions_state_machines.json"
            ),
            
            # AppSync API
            (
                "AppSync API",
                f"select api_id, name, authentication_type, log_config, open_id_connect_config, user_pool_config, lambda_authorizer_config, additional_authentication_providers, xray_enabled, waf_web_acl_arn, tags from aws_appsync_graphql_api where region = '{self.region}'",
                "application_appsync_apis.json"
            ),
            
            # Kinesis 스트림
            (
                "Kinesis 스트림",
                f"select stream_name, stream_arn, stream_status, stream_mode_details, shard_count, retention_period, encryption_type, key_id, stream_creation_timestamp, tags from aws_kinesis_stream where region = '{self.region}'",
                "application_kinesis_streams.json"
            ),
            
            # Kinesis Firehose 스트림
            (
                "Kinesis Firehose 스트림",
                f"select delivery_stream_name, delivery_stream_arn, delivery_stream_status, delivery_stream_type, version_id, create_timestamp, last_update_timestamp, source, destinations, has_more_destinations, tags from aws_kinesis_firehose_delivery_stream where region = '{self.region}'",
                "application_kinesis_firehose_streams.json"
            ),
            
            # CloudFront 배포
            (
                "CloudFront 배포",
                "select id, arn, status, last_modified_time, domain_name, comment, default_cache_behavior, cache_behaviors, custom_error_responses, logging, enabled, price_class, http_version, is_ipv6_enabled, web_acl_id, tags from aws_cloudfront_distribution",
                "application_cloudfront_distributions.json"
            ),
            
            # CloudFront Origin Access Identity
            (
                "CloudFront Origin Access Identity",
                "select id, s3_canonical_user_id, comment from aws_cloudfront_origin_access_identity",
                "application_cloudfront_oai.json"
            ),
            
            # Amplify 앱
            (
                "Amplify 앱",
                f"select app_id, app_arn, name, description, repository, platform, create_time, update_time, iam_service_role_arn, environment_variables, default_domain, enable_branch_auto_build, enable_branch_auto_deletion, enable_basic_auth, basic_auth_credentials, custom_rules, production_branch, build_spec, custom_headers, enable_auto_branch_creation, auto_branch_creation_patterns, auto_branch_creation_config, tags from aws_amplify_app where region = '{self.region}'",
                "application_amplify_apps.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("🌐 API 및 애플리케이션 서비스 수집 시작...")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 쿼리 실행
        queries = self.get_application_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("API 및 애플리케이션 서비스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("application_*.json")):
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
    collector = SteampipeApplicationCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
