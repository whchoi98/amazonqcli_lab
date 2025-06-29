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
        """확장된 애플리케이션 서비스 쿼리 구조"""
        return [
            # ===== API Gateway REST API =====
            (
                "API Gateway REST API",
                f"select id, name, description, created_date, version, warnings, binary_media_types, minimum_compression_size, api_key_source, endpoint_configuration, policy, tags from aws_api_gateway_rest_api where region = '{self.region}'",
                "application_api_gateway_rest_apis.json"
            ),
            (
                "API Gateway 리소스",
                f"select rest_api_id, id, parent_id, path_part, path, resource_methods from aws_api_gateway_resource where region = '{self.region}'",
                "application_api_gateway_resources.json"
            ),
            (
                "API Gateway 메서드",
                f"select rest_api_id, resource_id, http_method, authorization_type, authorizer_id, api_key_required, request_validator_id, request_models, request_parameters, method_integration from aws_api_gateway_method where region = '{self.region}'",
                "application_api_gateway_methods.json"
            ),
            (
                "API Gateway 배포",
                f"select rest_api_id, id, description, created_date, api_summary from aws_api_gateway_deployment where region = '{self.region}'",
                "application_api_gateway_deployments.json"
            ),
            (
                "API Gateway 스테이지",
                f"select rest_api_id, stage_name, deployment_id, description, created_date, last_updated_date, cache_cluster_enabled, cache_cluster_size, cache_cluster_status, method_settings, variables, documentation_version, access_log_settings, canary_settings, tracing_config, web_acl_arn, tags from aws_api_gateway_stage where region = '{self.region}'",
                "application_api_gateway_stages.json"
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
            (
                "API Gateway 도메인 이름",
                f"select domain_name, certificate_name, certificate_arn, certificate_upload_date, regional_domain_name, regional_hosted_zone_id, regional_certificate_name, regional_certificate_arn, distribution_domain_name, distribution_hosted_zone_id, endpoint_configuration, domain_name_status, domain_name_status_message, security_policy, tags from aws_api_gateway_domain_name where region = '{self.region}'",
                "application_api_gateway_domain_names.json"
            ),
            (
                "API Gateway 권한 부여자",
                f"select rest_api_id, id, name, type, provider_arns, auth_type, authorizer_uri, authorizer_credentials, identity_source, identity_validation_expression, authorizer_result_ttl_in_seconds from aws_api_gateway_authorizer where region = '{self.region}'",
                "application_api_gateway_authorizers.json"
            ),
            (
                "API Gateway 모델",
                f"select rest_api_id, id, name, description, schema, content_type from aws_api_gateway_model where region = '{self.region}'",
                "application_api_gateway_models.json"
            ),
            (
                "API Gateway 요청 검증기",
                f"select rest_api_id, id, name, validate_request_body, validate_request_parameters from aws_api_gateway_request_validator where region = '{self.region}'",
                "application_api_gateway_request_validators.json"
            ),
            (
                "API Gateway VPC 링크",
                f"select id, name, description, target_arns, status, status_message, tags from aws_api_gateway_vpc_link where region = '{self.region}'",
                "application_api_gateway_vpc_links.json"
            ),

            # ===== API Gateway v2 (HTTP API) =====
            (
                "API Gateway v2 API",
                f"select api_id, name, description, api_endpoint, api_gateway_managed, api_key_selection_expression, cors_configuration, created_date, disable_schema_validation, disable_execute_api_endpoint, import_info, protocol_type, route_selection_expression, version, warnings, tags from aws_apigatewayv2_api where region = '{self.region}'",
                "application_apigatewayv2_apis.json"
            ),
            (
                "API Gateway v2 권한 부여자",
                f"select api_id, authorizer_id, name, authorizer_type, authorizer_credentials_arn, authorizer_payload_format_version, authorizer_result_ttl_in_seconds, authorizer_uri, enable_simple_responses, identity_sources, jwt_configuration from aws_apigatewayv2_authorizer where region = '{self.region}'",
                "application_apigatewayv2_authorizers.json"
            ),
            (
                "API Gateway v2 배포",
                f"select api_id, deployment_id, auto_deployed, created_date, deployment_status, deployment_status_message, description from aws_apigatewayv2_deployment where region = '{self.region}'",
                "application_apigatewayv2_deployments.json"
            ),
            (
                "API Gateway v2 도메인 이름",
                f"select domain_name, api_mapping_selection_expression, domain_name_configurations, mutual_tls_authentication, tags from aws_apigatewayv2_domain_name where region = '{self.region}'",
                "application_apigatewayv2_domain_names.json"
            ),
            (
                "API Gateway v2 통합",
                f"select api_id, integration_id, connection_id, connection_type, content_handling_strategy, credentials_arn, description, integration_method, integration_response_selection_expression, integration_subtype, integration_type, integration_uri, passthrough_behavior, payload_format_version, request_parameters, request_templates, response_parameters, template_selection_expression, timeout_in_millis, tls_config from aws_apigatewayv2_integration where region = '{self.region}'",
                "application_apigatewayv2_integrations.json"
            ),
            (
                "API Gateway v2 모델",
                f"select api_id, model_id, content_type, description, name, schema from aws_apigatewayv2_model where region = '{self.region}'",
                "application_apigatewayv2_models.json"
            ),
            (
                "API Gateway v2 라우트",
                f"select api_id, route_id, api_gateway_managed, api_key_required, authorization_scopes, authorization_type, authorizer_id, model_selection_expression, operation_name, request_models, request_parameters, route_key, route_response_selection_expression, target from aws_apigatewayv2_route where region = '{self.region}'",
                "application_apigatewayv2_routes.json"
            ),
            (
                "API Gateway v2 스테이지",
                f"select api_id, stage_name, access_log_settings, api_gateway_managed, auto_deploy, client_certificate_id, created_date, default_route_settings, deployment_id, description, last_deployment_status_message, last_updated_date, route_settings, tags, throttle_settings from aws_apigatewayv2_stage where region = '{self.region}'",
                "application_apigatewayv2_stages.json"
            ),
            (
                "API Gateway v2 VPC 링크",
                f"select vpc_link_id, name, security_group_ids, subnet_ids, tags, vpc_link_status, vpc_link_status_message, vpc_link_version, created_date from aws_apigatewayv2_vpc_link where region = '{self.region}'",
                "application_apigatewayv2_vpc_links.json"
            ),

            # ===== Application Load Balancer 고급 기능 =====
            (
                "ALB 리스너 인증서",
                f"select listener_arn, certificate_arn, is_default from aws_ec2_load_balancer_listener_certificate where region = '{self.region}'",
                "application_alb_listener_certificates.json"
            ),

            # ===== SNS =====
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

            # ===== SQS =====
            (
                "SQS 큐",
                f"select queue_url, name, attributes, tags from aws_sqs_queue where region = '{self.region}'",
                "application_sqs_queues.json"
            ),

            # ===== Amazon MQ =====
            (
                "MQ 브로커",
                f"select broker_id, broker_name, broker_arn, broker_state, created, deployment_mode, engine_type, engine_version, host_instance_type, publicly_accessible, storage_type, subnet_ids, security_groups, auto_minor_version_upgrade, maintenance_window_start_time, logs, users, configurations, tags from aws_mq_broker where region = '{self.region}'",
                "application_mq_brokers.json"
            ),
            (
                "MQ 구성",
                f"select id, arn, name, description, engine_type, engine_version, latest_revision, created, authentication_strategy, tags from aws_mq_configuration where region = '{self.region}'",
                "application_mq_configurations.json"
            ),

            # ===== EventBridge =====
            (
                "EventBridge 이벤트 버스",
                f"select name, arn, policy, tags from aws_eventbridge_bus where region = '{self.region}'",
                "application_eventbridge_buses.json"
            ),
            (
                "EventBridge 규칙",
                f"select name, arn, description, event_pattern, schedule_expression, state, targets, managed_by, event_bus_name, role_arn, tags from aws_eventbridge_rule where region = '{self.region}'",
                "application_eventbridge_rules.json"
            ),

            # ===== Step Functions =====
            (
                "Step Functions 상태 머신",
                f"select state_machine_arn, name, status, type, definition, role_arn, creation_date, logging_configuration, tags from aws_sfn_state_machine where region = '{self.region}'",
                "application_stepfunctions_state_machines.json"
            ),
            (
                "Step Functions 활동",
                f"select activity_arn, name, creation_date from aws_sfn_activity where region = '{self.region}'",
                "application_stepfunctions_activities.json"
            ),

            # ===== CloudFormation =====
            (
                "CloudFormation 스택",
                f"select stack_id, stack_name, description, parameters, creation_time, last_updated_time, rollback_configuration, stack_status, stack_status_reason, drift_information, enable_termination_protection, parent_id, root_id, notification_arns, timeout_in_minutes, capabilities, outputs, role_arn, tags from aws_cloudformation_stack where region = '{self.region}'",
                "application_cloudformation_stacks.json"
            ),
            (
                "CloudFormation 스택 세트",
                f"select stack_set_id, stack_set_name, description, status, template_body, parameters, capabilities, tags, administration_role_arn, execution_role_name, permission_model, auto_deployment, managed_execution, call_as from aws_cloudformation_stack_set where region = '{self.region}'",
                "application_cloudformation_stack_sets.json"
            ),

            # ===== CodePipeline =====
            (
                "CodePipeline 파이프라인",
                f"select name, role_arn, artifact_store, stages, version, created, updated from aws_codepipeline_pipeline where region = '{self.region}'",
                "application_codepipeline_pipelines.json"
            ),

            # ===== CodeBuild =====
            (
                "CodeBuild 프로젝트",
                f"select name, arn, description, source, secondary_sources, source_version, secondary_source_versions, artifacts, secondary_artifacts, cache, environment, service_role, timeout_in_minutes, queued_timeout_in_minutes, encryption_key, tags, created, last_modified, webhook, vpc_config, badge, logs_config, file_system_locations, build_batch_config from aws_codebuild_project where region = '{self.region}'",
                "application_codebuild_projects.json"
            ),

            # ===== CodeCommit =====
            (
                "CodeCommit 저장소",
                f"select repository_name, repository_id, repository_description, default_branch, last_modified_date, creation_date, clone_url_http, clone_url_ssh, arn from aws_codecommit_repository where region = '{self.region}'",
                "application_codecommit_repositories.json"
            ),

            # ===== CodeDeploy =====
            (
                "CodeDeploy 애플리케이션",
                f"select application_id, application_name, description, create_time, linked_to_github, github_account_name, compute_platform from aws_codedeploy_application where region = '{self.region}'",
                "application_codedeploy_applications.json"
            ),
            (
                "CodeDeploy 배포 구성",
                f"select deployment_config_id, deployment_config_name, minimum_healthy_hosts, traffic_routing_config, compute_platform, create_time from aws_codedeploy_deployment_config where region = '{self.region}'",
                "application_codedeploy_deployment_configs.json"
            ),

            # ===== OpsWorks =====
            (
                "OpsWorks 스택",
                f"select stack_id, name, arn, region, vpc_id, attributes, service_role_arn, default_instance_profile_arn, default_os, hostname_theme, default_availability_zone, default_subnet_id, custom_json, configuration_manager, chef_configuration, use_custom_cookbooks, use_opsworks_security_groups, custom_cookbooks_source, default_ssh_key_name, created_at, default_root_device_type, agent_version from aws_opsworks_stack",
                "application_opsworks_stacks.json"
            ),

            # ===== 기존 서비스들 =====
            (
                "AppSync API",
                f"select api_id, name, authentication_type, log_config, open_id_connect_config, user_pool_config, lambda_authorizer_config, additional_authentication_providers, xray_enabled, waf_web_acl_arn, tags from aws_appsync_graphql_api where region = '{self.region}'",
                "application_appsync_apis.json"
            ),
            (
                "Kinesis 스트림",
                f"select stream_name, stream_arn, stream_status, stream_mode_details, shard_count, retention_period, encryption_type, key_id, stream_creation_timestamp, tags from aws_kinesis_stream where region = '{self.region}'",
                "application_kinesis_streams.json"
            ),
            (
                "Kinesis Firehose 스트림",
                f"select delivery_stream_name, delivery_stream_arn, delivery_stream_status, delivery_stream_type, version_id, create_timestamp, last_update_timestamp, source, destinations, has_more_destinations, tags from aws_kinesis_firehose_delivery_stream where region = '{self.region}'",
                "application_kinesis_firehose_streams.json"
            ),
            (
                "CloudFront 배포",
                "select id, arn, status, last_modified_time, domain_name, comment, default_cache_behavior, cache_behaviors, custom_error_responses, logging, enabled, price_class, http_version, is_ipv6_enabled, web_acl_id, tags from aws_cloudfront_distribution",
                "application_cloudfront_distributions.json"
            ),
            (
                "CloudFront Origin Access Identity",
                "select id, s3_canonical_user_id, comment from aws_cloudfront_origin_access_identity",
                "application_cloudfront_oai.json"
            ),
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
        
        # 다음 단계 안내
        print(f"\n{self.YELLOW}💡 다음 단계:{self.NC}")
        print("1. 수집된 애플리케이션 데이터를 바탕으로 Phase 1 인프라 분석 진행")
        print("2. API Gateway (REST/HTTP) 및 서버리스 아키텍처 최적화 검토")
        print("3. 메시징 서비스 (SNS/SQS/MQ) 구성 및 패턴 분석")
        print("4. 이벤트 기반 아키텍처 (EventBridge/Step Functions) 패턴 분석")
        print("5. CI/CD 파이프라인 (CodePipeline/CodeBuild/CodeDeploy) 최적화")
        print("6. CloudFormation 스택 및 IaC 거버넌스 분석")
        print("7. CDN 및 콘텐츠 전송 최적화 분석")
        print("9. OpsWorks 및 애플리케이션 배포 전략 검토")
        print("10. 마이크로서비스 아키텍처 패턴 및 통합 분석")
        
        print(f"\n{self.BLUE}🎉 확장된 애플리케이션 서비스 데이터 수집이 완료되었습니다!{self.NC}")

def main():
    """메인 함수"""
    region = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-2')
    collector = SteampipeApplicationCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
