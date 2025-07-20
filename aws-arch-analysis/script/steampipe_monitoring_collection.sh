#!/bin/bash

# AWS 모니터링 및 리소스 관리 서비스 데이터 수집 스크립트
# CloudWatch, X-Ray, Config, Organizations, Service Catalog 등 포괄적 수집
#
# 작성자: Amazon Q CLI Lab
# 버전: 1.0
# 생성일: 2025-06-27

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 전역 변수
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
# 스크립트의 실제 위치를 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUTPUT_DIR="${PROJECT_ROOT}/aws-arch-analysis/report"
SUCCESSFUL_COLLECTIONS=0
TOTAL_ITEMS=0
TOTAL_QUERIES=0

# 로깅 함수
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_progress() {
    echo -e "${CYAN}🔍 $1${NC}"
}

# 출력 디렉토리 생성
create_output_directory() {
    if mkdir -p "$OUTPUT_DIR"; then
        log_success "출력 디렉토리 생성: $OUTPUT_DIR"
    else
        log_error "디렉토리 생성 실패: $OUTPUT_DIR"
        exit 1
    fi
}

# Steampipe 쿼리 실행 함수
run_steampipe_query() {
    local service_name="$1"
    local query="$2"
    local filename="${OUTPUT_DIR}/monitoring_${service_name,,}.json"
    filename=$(echo "$filename" | tr ' ' '_')
    
    log_progress "${service_name} 데이터 수집 중..."
    
    # Steampipe 쿼리 실행 (60초 타임아웃)
    if timeout 60 steampipe query "$query" --output json > "$filename" 2>/dev/null; then
        # JSON 파일이 비어있지 않고 유효한지 확인
        if [ -s "$filename" ] && jq empty "$filename" 2>/dev/null; then
            local item_count=$(jq length "$filename" 2>/dev/null || echo "0")
            if [ "$item_count" -gt 0 ]; then
                log_success "${service_name}: ${item_count}개 항목 수집 완료"
                ((SUCCESSFUL_COLLECTIONS++))
                ((TOTAL_ITEMS += item_count))
                return 0
            else
                log_warning "${service_name}: 데이터 없음"
                rm -f "$filename"
                return 1
            fi
        else
            log_error "${service_name}: 유효하지 않은 JSON 데이터"
            rm -f "$filename"
            return 1
        fi
    else
        log_error "${service_name}: 쿼리 실행 실패 또는 타임아웃"
        rm -f "$filename"
        return 1
    fi
}

# 모니터링 서비스 데이터 수집
collect_monitoring_data() {
    log_info "🚀 모니터링 및 리소스 관리 데이터 수집 시작"
    echo "================================================================================"
    
    local start_time=$(date +%s)
    
    # CloudWatch 알람 (실제 테이블명: aws_cloudwatch_alarm)
    run_steampipe_query "CloudWatch Alarms" \
        "select name, arn, alarm_description, state_value, metric_name, namespace, statistic, threshold, comparison_operator, evaluation_periods, datapoints_to_alarm, treat_missing_data, alarm_actions, ok_actions, insufficient_data_actions, region, account_id from aws_cloudwatch_alarm;"
    
    # CloudWatch 이벤트 규칙 (EventBridge)
    run_steampipe_query "CloudWatch Event Rules" \
        "select name, arn, description, event_pattern, schedule_expression, state, role_arn, managed_by, event_bus_name, targets, tags, region, account_id from aws_cloudwatch_event_rule;"
    
    # CloudWatch Logs
    run_steampipe_query "CloudWatch Log Groups" \
        "select name, arn, creation_time, retention_in_days, stored_bytes, metric_filter_count, kms_key_id, tags, region, account_id from aws_cloudwatch_log_group;"
    
    run_steampipe_query "CloudWatch Log Streams" \
        "select log_group_name, name, arn, creation_time, first_event_time, last_event_time, last_ingestion_time, upload_sequence_token, stored_bytes, region, account_id from aws_cloudwatch_log_stream;"
    
    run_steampipe_query "CloudWatch Log Metric Filters" \
        "select name, log_group_name, filter_pattern, metric_transformations, creation_time, region, account_id from aws_cloudwatch_log_metric_filter;"
    
    run_steampipe_query "CloudWatch Log Subscription Filters" \
        "select name, log_group_name, filter_pattern, destination_arn, role_arn, distribution, creation_time, region, account_id from aws_cloudwatch_log_subscription_filter;"
    
    run_steampipe_query "CloudWatch Log Destinations" \
        "select destination_name, arn, role_arn, target_arn, access_policy, creation_time, region, account_id from aws_cloudwatch_log_destination;"
    
    run_steampipe_query "CloudWatch Log Resource Policies" \
        "select policy_name, policy_document, last_updated_time, region, account_id from aws_cloudwatch_log_resource_policy;"
    
    # CloudWatch 메트릭
    run_steampipe_query "CloudWatch Metrics" \
        "select metric_name, namespace, dimensions, region, account_id from aws_cloudwatch_metric;"
    
    # CloudTrail
    run_steampipe_query "CloudTrail Trails" \
        "select name, arn, s3_bucket_name, s3_key_prefix, include_global_service_events, is_multi_region_trail, home_region, trail_arn, log_file_validation_enabled, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn, kms_key_id, has_custom_event_selectors, has_insight_selectors, is_organization_trail, is_logging, latest_delivery_time, latest_notification_time, start_logging_time, stop_logging_time, tags, region, account_id from aws_cloudtrail_trail;"
    
    run_steampipe_query "CloudTrail Event Data Stores" \
        "select arn, name, status, advanced_event_selectors, multi_region_enabled, organization_enabled, retention_period, termination_protection_enabled, kms_key_id, created_timestamp, updated_timestamp, region, account_id from aws_cloudtrail_event_data_store;"
    
    run_steampipe_query "CloudTrail Channels" \
        "select arn, name, source, destinations, region, account_id from aws_cloudtrail_channel;"
    
    # Config
    run_steampipe_query "Config Configuration Recorders" \
        "select name, role_arn, recording_group, status, region, account_id from aws_config_configuration_recorder;"
    
    run_steampipe_query "Config Delivery Channels" \
        "select name, s3_bucket_name, s3_key_prefix, sns_topic_arn, region, account_id from aws_config_delivery_channel;"
    
    run_steampipe_query "Config Rules" \
        "select name, arn, rule_id, description, source, input_parameters, maximum_execution_frequency, state, created_by, region, account_id from aws_config_rule;"
    
    run_steampipe_query "Config Conformance Packs" \
        "select name, arn, conformance_pack_id, delivery_s3_bucket, delivery_s3_key_prefix, conformance_pack_input_parameters, last_update_requested_time, created_by, region, account_id from aws_config_conformance_pack;"
    
    run_steampipe_query "Config Aggregate Authorizations" \
        "select authorized_account_id, authorized_aws_region, creation_time, region, account_id from aws_config_aggregate_authorization;"
    
    run_steampipe_query "Config Retention Configurations" \
        "select name, retention_period_in_days, region, account_id from aws_config_retention_configuration;"
    
    # Service Catalog
    run_steampipe_query "Service Catalog Portfolios" \
        "select id, arn, display_name, description, provider_name, created_time, tags, region, account_id from aws_servicecatalog_portfolio;"
    
    run_steampipe_query "Service Catalog Products" \
        "select product_id, name, owner, short_description, type, distributor, has_default_path, support_description, support_email, support_url, created_time, tags, region, account_id from aws_servicecatalog_product;"
    
    run_steampipe_query "Service Catalog Provisioned Products" \
        "select name, arn, id, type, provisioning_artifact_id, product_id, user_arn, user_arn_session, status, status_message, created_time, last_updated_time, last_record_id, last_provisioning_record_id, last_successful_provisioning_record_id, tags, region, account_id from aws_servicecatalog_provisioned_product;"
    
    # Organizations (권한 필요)
    run_steampipe_query "Organizations Accounts" \
        "select id, arn, email, name, status, joined_method, joined_timestamp, region, account_id from aws_organizations_account;"
    
    run_steampipe_query "Organizations Organizational Units" \
        "select id, arn, name, parent_id, region, account_id from aws_organizations_organizational_unit;"
    
    run_steampipe_query "Organizations Policies" \
        "select id, arn, name, description, type, aws_managed, content, region, account_id from aws_organizations_policy;"
    
    run_steampipe_query "Organizations Policy Targets" \
        "select policy_id, target_id, target_type, region, account_id from aws_organizations_policy_target;"
    
    run_steampipe_query "Organizations Delegated Administrators" \
        "select account_id, service_principal, delegation_enabled_date, region from aws_organizations_delegated_administrator;"
    
    run_steampipe_query "Organizations Root" \
        "select id, arn, name, policy_types, region, account_id from aws_organizations_root;"
    
    # 총 쿼리 수 계산
    TOTAL_QUERIES=26
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    
    # 수집 결과 요약
    echo ""
    echo "================================================================================"
    log_success "📊 모니터링 데이터 수집 완료!"
    echo "✅ 성공한 수집: ${SUCCESSFUL_COLLECTIONS}/${TOTAL_QUERIES} ($(( SUCCESSFUL_COLLECTIONS * 100 / TOTAL_QUERIES ))%)"
    echo "📦 총 수집 항목: ${TOTAL_ITEMS}개"
    echo "⏱️  실행 시간: ${execution_time}초"
    echo "📁 출력 디렉토리: ${OUTPUT_DIR}"
    
    # 수집된 파일 목록
    if [ "$SUCCESSFUL_COLLECTIONS" -gt 0 ]; then
        echo ""
        echo "📋 수집된 데이터 파일:"
        for file in "${OUTPUT_DIR}"/monitoring_*.json; do
            if [ -f "$file" ]; then
                local file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
                echo "   • $(basename "$file") (${file_size} bytes)"
            fi
        done
    fi
}

# Steampipe 설치 확인
check_steampipe() {
    if ! command -v steampipe &> /dev/null; then
        log_error "Steampipe가 설치되지 않았거나 PATH에 없습니다."
        echo "   설치 방법: https://steampipe.io/downloads"
        exit 1
    fi
    
    local version=$(steampipe --version 2>/dev/null | head -n1)
    log_success "Steampipe 버전: $version"
}

# jq 설치 확인
check_jq() {
    if ! command -v jq &> /dev/null; then
        log_error "jq가 설치되지 않았습니다. JSON 처리를 위해 필요합니다."
        echo "   설치 방법: sudo yum install jq (Amazon Linux) 또는 sudo apt install jq (Ubuntu)"
        exit 1
    fi
    
    log_success "jq 설치 확인됨"
}

# 메인 실행 함수
main() {
    echo "🔍 AWS 모니터링 및 리소스 관리 서비스 데이터 수집기"
    echo "================================================================================"
    
    # 필수 도구 확인
    check_steampipe
    check_jq
    
    # 출력 디렉토리 생성
    create_output_directory
    
    # 데이터 수집 실행
    collect_monitoring_data
    
    if [ "$SUCCESSFUL_COLLECTIONS" -eq 0 ]; then
        log_warning "수집된 데이터가 없습니다. AWS 자격 증명과 권한을 확인하세요."
        exit 1
    fi
    
    echo ""
    log_success "🎉 모니터링 데이터 수집이 완료되었습니다!"
    echo "   다음 명령어로 리포트를 생성할 수 있습니다:"
    echo "   python3 generate-monitoring-report.py"
}

# 스크립트 실행
main "$@"
