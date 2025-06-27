#!/bin/bash
# Steampipe 기반 모니터링 및 로깅 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_monitoring_collection.log"
ERROR_LOG="steampipe_monitoring_errors.log"

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
    
    # echo 명령인 경우 직접 실행
    if [[ "$query" == echo* ]]; then
        if eval "$query" > "$output_file" 2>>"$ERROR_LOG"; then
            local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
            log_warning "$description - 서비스 미지원 ($output_file, ${file_size} bytes)"
            return 1
        else
            log_error "$description 실패 - $output_file"
            return 1
        fi
    else
        # 일반 Steampipe 쿼리 실행
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
    fi
}

# 메인 실행부
main() {
    log_info "📊 Steampipe 기반 모니터링 및 로깅 리소스 데이터 수집 시작"
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
    
    log_info "📊 모니터링 및 로깅 리소스 수집 시작..."
    
    # 모니터링 및 로깅 리소스 수집 배열
    declare -a queries=(
        "CloudWatch 알람 상세 정보|select name, arn, alarm_description, alarm_configuration_updated_timestamp, actions_enabled, ok_actions, alarm_actions, insufficient_data_actions, state_value, state_reason, state_reason_data, state_updated_timestamp, metric_name, namespace, statistic, extended_statistic, dimensions, period, evaluation_periods, datapoints_to_alarm, threshold, comparison_operator, treat_missing_data, evaluate_low_sample_count_percentile, metrics, tags from aws_cloudwatch_alarm where region = '$REGION'|monitoring_cloudwatch_alarms.json"
        "CloudWatch 로그 그룹 상세 정보|select name, arn, creation_time, retention_in_days, metric_filter_count, stored_bytes, kms_key_id, tags from aws_cloudwatch_log_group where region = '$REGION'|monitoring_cloudwatch_log_groups.json"
        "CloudWatch 로그 스트림|select arn, log_group_name, name, creation_time, first_event_timestamp, last_event_timestamp, last_ingestion_time, upload_sequence_token from aws_cloudwatch_log_stream where region = '$REGION'|monitoring_cloudwatch_log_streams.json"
        "CloudWatch 메트릭 필터|select name, log_group_name, filter_pattern, metric_transformation_name, metric_transformation_namespace, metric_transformation_value, creation_time from aws_cloudwatch_log_metric_filter where region = '$REGION'|monitoring_cloudwatch_metric_filters.json"
        "CloudWatch 대시보드|echo '[]'|monitoring_cloudwatch_dashboards.json"
        "CloudWatch Insights 쿼리|echo '[]'|monitoring_cloudwatch_insights_queries.json"
        "CloudWatch 복합 알람|echo '[]'|monitoring_cloudwatch_composite_alarms.json"
        "X-Ray 추적 구성|echo '[]'|monitoring_xray_tracing_config.json"
        "X-Ray 서비스 맵|echo '[]'|monitoring_xray_services.json"
        "X-Ray 암호화 구성|echo '[]'|monitoring_xray_encryption_config.json"
        "CloudWatch Application Insights 애플리케이션|echo '[]'|monitoring_application_insights.json"
        "CloudWatch Container Insights|echo '[]'|monitoring_container_insights.json"
        "CloudWatch Synthetics Canary|echo '[]'|monitoring_synthetics_canaries.json"
        "CloudWatch RUM 앱 모니터|echo '[]'|monitoring_rum_app_monitors.json"
        "CloudWatch Evidently 프로젝트|echo '[]'|monitoring_evidently_projects.json"
        "AWS Systems Manager OpsCenter OpsItems|echo '[]'|monitoring_ssm_ops_items.json"
        "AWS Personal Health Dashboard 이벤트|select arn, service, event_type_code, event_type_category, region, availability_zone, start_time, end_time, last_updated_time, status_code, event_scope_code from aws_health_event where region = '$REGION'|monitoring_health_events.json"
        "AWS Cost and Usage Reports|echo '[]'|monitoring_cost_usage_reports.json"
        "AWS Budgets|echo '[]'|monitoring_budgets.json"
        "AWS Cost Explorer 비용 카테고리|echo '[]'|monitoring_cost_categories.json"
        "AWS Resource Groups|echo '[]'|monitoring_resource_groups.json"
        "AWS Systems Manager Compliance|echo '[]'|monitoring_ssm_compliance.json"
        "AWS Config 적합성 팩|select name, arn, conformance_pack_id, delivery_s3_bucket, delivery_s3_key_prefix, input_parameters, last_update_requested_time, created_by from aws_config_conformance_pack where region = '$REGION'|monitoring_config_conformance_packs.json"
        "AWS Well-Architected 워크로드|select workload_id, workload_arn, workload_name, description, environment, account_ids, aws_regions, non_aws_regions, architectural_design, review_owner, industry_type, industry, notes, improvement_status, risk_counts, pillar_priorities, lenses, owner, share_invitation_id, tags from aws_wellarchitected_workload where region = '$REGION'|monitoring_wellarchitected_workloads.json"
        "AWS Service Catalog 포트폴리오|select id, arn, display_name, description, provider_name, created_time, tags from aws_servicecatalog_portfolio where region = '$REGION'|monitoring_servicecatalog_portfolios.json"
        "AWS License Manager 라이선스 구성|echo '[]'|monitoring_license_manager_configs.json"
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
    log_success "모니터링 및 로깅 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    log_info "🎉 모니터링 및 로깅 리소스 데이터 수집이 완료되었습니다!"
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
