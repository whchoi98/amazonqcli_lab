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

# 메인 함수
main() {
    log_info "🚀 Steampipe 기반 API 및 애플리케이션 서비스 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 디렉토리 생성
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR"
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
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
    
    # API 및 애플리케이션 서비스 수집 배열
    declare -a queries=(
        # API Gateway
        "API Gateway REST API|select id, name, description, created_date, version, warnings, binary_media_types, minimum_compression_size, api_key_source, endpoint_configuration, policy, tags from aws_api_gateway_rest_api where region = '$REGION'|application_api_gateway_rest_apis.json"
        "API Gateway 스테이지|select rest_api_id, stage_name, deployment_id, description, created_date, last_updated_date, cache_cluster_enabled, cache_cluster_size, cache_cluster_status, method_settings, variables, documentation_version, access_log_settings, canary_settings, tracing_config, web_acl_arn, tags from aws_api_gateway_stage where region = '$REGION'|application_api_gateway_stages.json"
        "API Gateway 도메인 이름|select domain_name, certificate_name, certificate_arn, certificate_upload_date, regional_domain_name, regional_hosted_zone_id, regional_certificate_name, regional_certificate_arn, distribution_domain_name, distribution_hosted_zone_id, endpoint_configuration, domain_name_status, domain_name_status_message, security_policy, tags from aws_api_gateway_domain_name where region = '$REGION'|application_api_gateway_domain_names.json"
        "API Gateway 사용 계획|select id, name, description, api_stages, throttle, quota, product_code, tags from aws_api_gateway_usage_plan where region = '$REGION'|application_api_gateway_usage_plans.json"
        "API Gateway API 키|select id, name, description, enabled, created_date, last_updated_date, stage_keys, tags from aws_api_gateway_api_key where region = '$REGION'|application_api_gateway_api_keys.json"
        
        # SNS
        "SNS 토픽|select topic_arn, name, display_name, owner, subscriptions_confirmed, subscriptions_deleted, subscriptions_pending, policy, delivery_policy, effective_delivery_policy, kms_master_key_id, fifo_topic, content_based_deduplication, tags from aws_sns_topic where region = '$REGION'|application_sns_topics.json"
        "SNS 구독|select subscription_arn, topic_arn, owner, protocol, endpoint, confirmation_was_authenticated, delivery_policy, effective_delivery_policy, filter_policy, pending_confirmation, raw_message_delivery, redrive_policy, subscription_role_arn from aws_sns_topic_subscription where region = '$REGION'|application_sns_subscriptions.json"
        
        # SQS
        "SQS 큐|select queue_url, name, attributes, tags from aws_sqs_queue where region = '$REGION'|application_sqs_queues.json"
        
        # EventBridge
        "EventBridge 규칙|select name, arn, description, event_pattern, schedule_expression, state, targets, managed_by, event_bus_name, role_arn, tags from aws_eventbridge_rule where region = '$REGION'|application_eventbridge_rules.json"
        "EventBridge 이벤트 버스|select name, arn, policy, tags from aws_eventbridge_bus where region = '$REGION'|application_eventbridge_buses.json"
        
        # Step Functions
        "Step Functions 상태 머신|select state_machine_arn, name, status, type, definition, role_arn, creation_date, logging_configuration, tags from aws_sfn_state_machine where region = '$REGION'|application_stepfunctions_state_machines.json"
        
        # AppSync
        "AppSync API|select api_id, name, authentication_type, log_config, open_id_connect_config, user_pool_config, lambda_authorizer_config, additional_authentication_providers, xray_enabled, waf_web_acl_arn, tags from aws_appsync_graphql_api where region = '$REGION'|application_appsync_apis.json"
        
        # Kinesis
        "Kinesis 스트림|select stream_name, stream_arn, stream_status, stream_mode_details, shard_count, retention_period, encryption_type, key_id, stream_creation_timestamp, tags from aws_kinesis_stream where region = '$REGION'|application_kinesis_streams.json"
        "Kinesis Firehose 스트림|select delivery_stream_name, delivery_stream_arn, delivery_stream_status, delivery_stream_type, version_id, create_timestamp, last_update_timestamp, source, destinations, has_more_destinations, tags from aws_kinesis_firehose_delivery_stream where region = '$REGION'|application_kinesis_firehose_streams.json"
        
        # CloudFront
        "CloudFront 배포|select id, arn, status, last_modified_time, domain_name, comment, default_cache_behavior, cache_behaviors, custom_error_responses, logging, enabled, price_class, http_version, is_ipv6_enabled, web_acl_id, tags from aws_cloudfront_distribution|application_cloudfront_distributions.json"
        "CloudFront Origin Access Identity|select id, s3_canonical_user_id, comment from aws_cloudfront_origin_access_identity|application_cloudfront_oai.json"
        
        # Amplify
        "Amplify 앱|select app_id, app_arn, name, description, repository, platform, create_time, update_time, iam_service_role_arn, environment_variables, default_domain, enable_branch_auto_build, enable_branch_auto_deletion, enable_basic_auth, basic_auth_credentials, custom_rules, production_branch, build_spec, custom_headers, enable_auto_branch_creation, auto_branch_creation_patterns, auto_branch_creation_config, tags from aws_amplify_app where region = '$REGION'|application_amplify_apps.json"
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
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in application_*.json; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            if [ "$size" -gt 100 ]; then
                echo -e "${GREEN}✓ $file (${size} bytes)${NC}"
            else
                echo -e "${YELLOW}⚠ $file (${size} bytes) - 데이터 없음${NC}"
            fi
        fi
    done
    
    # 수집 통계
    echo -e "\n${BLUE}📊 수집 통계:${NC}"
    echo "총 쿼리 수: $total_count"
    echo "성공한 쿼리: $success_count"
    echo "실패한 쿼리: $((total_count - success_count))"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 애플리케이션 데이터를 바탕으로 Phase 1 인프라 분석 진행"
    echo "2. API Gateway 및 서버리스 아키텍처 최적화 검토"
    echo "3. 메시징 서비스 (SNS/SQS) 구성 분석"
    echo "4. 이벤트 기반 아키텍처 패턴 분석"
    echo "5. CDN 및 콘텐츠 전송 최적화 분석"
    
    log_info "🎉 API 및 애플리케이션 서비스 리소스 데이터 수집이 완료되었습니다!"
}

# 스크립트 실행
main "$@"
