#!/bin/bash
# Steampipe 기반 API 및 애플리케이션 서비스 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_application_collection.log"
ERROR_LOG="steampipe_application_errors.log"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$ERROR_LOG"
}

# Steampipe 쿼리 실행 함수
execute_steampipe_query() {
    local description="$1"
    local query="$2"
    local output_file="$3"
    
    log_info "수집 중: $description"
    
    if steampipe query "$query" --output json > "$output_file" 2>>"$ERROR_LOG"; then
        local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
        if [ "$file_size" -gt 50 ]; then
            log_success "$description 완료 ($output_file, ${file_size} bytes)"
            return 0
        else
            log_warning "$description - 데이터 없음 ($output_file, ${file_size} bytes)"
            return 1
        fi
    else
        log_error "$description 실패 - $output_file"
        return 1
    fi
}

# 메인 실행부
main() {
    log_info "🌐 Steampipe 기반 API 및 애플리케이션 서비스 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 보고서 디렉토리 생성 및 이동
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR" || exit 1
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
    # Steampipe 설치 확인
    if ! command -v steampipe &> /dev/null; then
        log_error "Steampipe가 설치되지 않았습니다."
        echo -e "${YELLOW}💡 Steampipe 설치 방법:${NC}"
        echo "sudo /bin/sh -c \"\$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)\""
        echo "steampipe plugin install aws"
        exit 1
    fi
    
    # AWS 플러그인 확인
    log_info "Steampipe AWS 플러그인 확인 중..."
    if ! steampipe plugin list | grep -q "aws"; then
        log_warning "AWS 플러그인이 설치되지 않았습니다. 설치 중..."
        steampipe plugin install aws
    fi
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_info "🌐 API 및 애플리케이션 서비스 수집 시작..."
    
    # API 및 애플리케이션 서비스 리소스 수집 배열
    declare -a queries=(
        "API Gateway REST API 상세 정보|select api_id, name, description, created_date, version, warnings, binary_media_types, minimum_compression_size, api_key_source, endpoint_configuration_types, policy, tags from aws_api_gateway_rest_api where region = '$REGION'|application_api_gateway_rest_apis.json"
        "API Gateway HTTP API (v2)|select api_id, name, description, created_date, version, warnings, api_endpoint, api_gateway_managed, api_key_selection_expression, cors_configuration, disable_execute_api_endpoint, disable_schema_validation, import_info, protocol_type, route_selection_expression, tags from aws_apigatewayv2_api where region = '$REGION'|application_api_gateway_v2_apis.json"
        "API Gateway 스테이지 (REST API)|select rest_api_id, name, deployment_id, description, created_date, last_updated_date, cache_cluster_enabled, cache_cluster_size, cache_cluster_status, method_settings, variables, documentation_version, access_log_settings, canary_settings, web_acl_arn, tags from aws_api_gateway_stage where region = '$REGION'|application_api_gateway_stages.json"
        "API Gateway 도메인 이름|select domain_name, certificate_name, certificate_arn, certificate_upload_date, regional_domain_name, regional_hosted_zone_id, regional_certificate_name, regional_certificate_arn, distribution_domain_name, distribution_hosted_zone_id, endpoint_configuration, domain_name_status, domain_name_status_message, security_policy, tags from aws_api_gateway_domain_name where region = '$REGION'|application_api_gateway_domain_names.json"
        "API Gateway 사용 계획|select id, name, description, api_stages, throttle, quota, product_code, tags from aws_api_gateway_usage_plan where region = '$REGION'|application_api_gateway_usage_plans.json"
        "API Gateway API 키|select id, name, description, enabled, created_date, last_updated_date, stage_keys, tags from aws_api_gateway_api_key where region = '$REGION'|application_api_gateway_api_keys.json"
        "SNS 토픽 상세 정보|select topic_arn, display_name, owner, policy, policy_std, delivery_policy, effective_delivery_policy, subscriptions_confirmed, subscriptions_deleted, subscriptions_pending, kms_master_key_id, tags from aws_sns_topic where region = '$REGION'|application_sns_topics.json"
        "SNS 구독|select subscription_arn, topic_arn, owner, protocol, endpoint, confirmation_was_authenticated, pending_confirmation, raw_message_delivery, filter_policy, delivery_policy, effective_delivery_policy, redrive_policy from aws_sns_topic_subscription where region = '$REGION'|application_sns_subscriptions.json"
        "SQS 큐 상세 정보|select queue_url, queue_arn, fifo_queue, delay_seconds, max_message_size, message_retention_seconds, receive_wait_time_seconds, visibility_timeout_seconds, policy, policy_std, redrive_policy, content_based_deduplication, deduplication_scope, fifo_throughput_limit, kms_master_key_id, tags from aws_sqs_queue where region = '$REGION'|application_sqs_queues.json"
        "EventBridge 규칙|select name, arn, description, event_pattern, schedule_expression, state, managed_by, event_bus_name, role_arn, targets, tags from aws_eventbridge_rule where region = '$REGION'|application_eventbridge_rules.json"
        "EventBridge 사용자 정의 버스|select name, arn, policy, tags from aws_eventbridge_bus where region = '$REGION'|application_eventbridge_buses.json"
        "Step Functions 상태 머신|select name, arn, status, type, role_arn, definition, creation_date, logging_configuration, tracing_configuration, tags from aws_sfn_state_machine where region = '$REGION'|application_stepfunctions_state_machines.json"
        "Step Functions 활동|select activity_arn, name, creation_date from aws_sfn_activity where region = '$REGION'|application_stepfunctions_activities.json"
        "AppSync GraphQL API|select api_id, name, authentication_type, log_config, open_id_connect_config, user_pool_config, lambda_authorizer_config, additional_authentication_providers, xray_enabled, waf_web_acl_arn, dns, api_type, merged_api_execution_role_arn, owner, owner_contact, introspection_config, query_depth_limit, resolver_count_limit, tags from aws_appsync_graphql_api where region = '$REGION'|application_appsync_apis.json"
        "Kinesis 스트림 상세 정보|select stream_name, stream_arn, stream_status, stream_mode_details, open_shard_count, has_more_shards, retention_period_hours, stream_creation_timestamp, encryption_type, key_id, tags from aws_kinesis_stream where region = '$REGION'|application_kinesis_streams.json"
        "Kinesis Data Firehose 전송 스트림|select delivery_stream_name, arn, delivery_stream_type, delivery_stream_status, version_id, create_timestamp, last_update_timestamp, source, destinations, has_more_destinations, failure_description, tags from aws_kinesis_firehose_delivery_stream where region = '$REGION'|application_kinesis_firehose_streams.json"
        "Kinesis Analytics 애플리케이션|select application_name, application_arn, application_description, application_status, create_timestamp, last_update_timestamp, application_code, application_version_id from aws_kinesisanalyticsv2_application where region = '$REGION'|application_kinesis_analytics.json"
        "CloudFront 배포|select id, arn, caller_reference, comment, default_root_object, domain_name, enabled, http_version, is_ipv6_enabled, last_modified_time, price_class, status, web_acl_id, tags from aws_cloudfront_distribution|application_cloudfront_distributions.json"
        "CloudFront Origin Access Identity|select id, s3_canonical_user_id, caller_reference, comment from aws_cloudfront_origin_access_identity|application_cloudfront_oai.json"
        "OpenSearch 도메인 상세 정보|select domain_name, domain_id, arn, created, deleted, endpoint, endpoints, processing, upgrade_processing, engine_version, cluster_config, ebs_options, access_policies, snapshot_options, vpc_options, cognito_options, encryption_at_rest_options, node_to_node_encryption_options, advanced_options, log_publishing_options, service_software_options, domain_endpoint_options, advanced_security_options, auto_tune_options, change_progress_details, tags from aws_opensearch_domain where region = '$REGION'|application_opensearch_domains.json"
        "SES 구성 세트|select name, creation_date, delivery_options, reputation_tracking_enabled, sending_enabled from aws_ses_configuration_set where region = '$REGION'|application_ses_configuration_sets.json"
        "SES 자격 증명|select identity, verification_status, verification_token, dkim_enabled, dkim_verification_status, bounce_topic, complaint_topic, delivery_topic, forwarding_enabled, headers_in_bounce_notifications_enabled, headers_in_complaint_notifications_enabled, headers_in_delivery_notifications_enabled from aws_ses_email_identity where region = '$REGION'|application_ses_identities.json"
        "Pinpoint 애플리케이션|select id, arn, name, settings, tags from aws_pinpoint_app where region = '$REGION'|application_pinpoint_apps.json"
        "WorkSpaces|select workspace_id, directory_id, user_name, ip_address, state, bundle_id, subnet_id, error_message, error_code, volume_encryption_key, user_volume_encryption_enabled, root_volume_encryption_enabled, workspace_properties, modification_states, related_workspaces, data_replication_settings, standby_workspaces_properties from aws_workspaces_workspace where region = '$REGION'|application_workspaces.json"
        "App Runner 서비스|select service_name, service_id, service_arn, service_url, created_at, updated_at, deleted_at, status, source_configuration, instance_configuration, encryption_configuration, health_check_configuration, auto_scaling_configuration_arn, network_configuration, observability_configuration, tags from aws_apprunner_service where region = '$REGION'|application_apprunner_services.json"
        "Amplify 앱|select app_id, arn, name, description, repository, platform, create_time, update_time, iam_service_role_arn, environment_variables, default_domain, enable_branch_auto_build, enable_branch_auto_deletion, enable_basic_auth, basic_auth_credentials, custom_rules, production_branch, build_spec, custom_headers, enable_auto_branch_creation, auto_branch_creation_patterns, auto_branch_creation_config, tags from aws_amplify_app where region = '$REGION'|application_amplify_apps.json"
    )
    
    # 쿼리 실행
    for query_info in "${queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "API 및 애플리케이션 서비스 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    log_info "🎉 API 및 애플리케이션 서비스 리소스 데이터 수집이 완료되었습니다!"
}

# 명령행 인수 처리
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -d|--dir)
            REPORT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "사용법: $0 [옵션]"
            echo "  -r, --region REGION    AWS 리전 설정"
            echo "  -d, --dir DIRECTORY    보고서 디렉토리 설정"
            echo "  -h, --help            도움말 표시"
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            exit 1
            ;;
    esac
done

# 스크립트 실행
main "$@"
