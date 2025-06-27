#!/bin/bash
# Steampipe 기반 종합 보안 리소스 데이터 수집 스크립트 (Enhanced Version)
# IAM, KMS, Secrets Manager, WAF, GuardDuty, Security Hub, Inspector, Shield 등 모든 보안 서비스 포함

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report}"
LOG_FILE="steampipe_security_collection.log"
ERROR_LOG="steampipe_security_errors.log"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_category() {
    echo -e "${PURPLE}[$1]${NC} $2" | tee -a "$LOG_FILE"
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

# 메인 함수
main() {
    log_info "🛡️ 종합 보안 리소스 데이터 수집 시작 (IAM, KMS, WAF, GuardDuty, Security Hub 등)"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 디렉토리 생성
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR"
    
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
    
    log_category "IAM" "🔐 IAM (Identity and Access Management) 리소스 수집 시작..."
    
    # IAM 기본 리소스 수집
    declare -a iam_queries=(
        "IAM 사용자|select name, user_id, arn, path, create_date, password_last_used, mfa_enabled, login_profile, attached_policy_arns, inline_policies, groups, permissions_boundary_arn, permissions_boundary_type, tags from aws_iam_user|security_iam_users.json"
        "IAM 그룹|select name, group_id, arn, path, create_date, attached_policy_arns, inline_policies, users from aws_iam_group|security_iam_groups.json"
        "IAM 역할|select name, role_id, arn, path, create_date, assume_role_policy_document, assume_role_policy_std, description, max_session_duration, permissions_boundary_arn, permissions_boundary_type, role_last_used_date, role_last_used_region, attached_policy_arns, inline_policies, instance_profile_arns, tags from aws_iam_role|security_iam_roles.json"
        "IAM 액세스 키|select access_key_id, user_name, status, create_date, access_key_last_used_date, access_key_last_used_region, access_key_last_used_service from aws_iam_access_key|security_iam_access_keys.json"
        "IAM 계정 요약|select account_id, account_mfa_enabled, account_access_keys_present, account_signing_certificates_present, users, users_quota, groups, groups_quota, server_certificates, server_certificates_quota, user_policy_size_quota, group_policy_size_quota, groups_per_user_quota, signing_certificates_per_user_quota, access_keys_per_user_quota, mfa_devices, mfa_devices_in_use, policies, policies_quota, policy_size_quota, policy_versions_in_use, policy_versions_in_use_quota, versions_per_policy_quota, global_endpoint_token_version from aws_iam_account_summary|security_iam_account_summary.json"
    )
    
    # IAM 쿼리 실행
    for query_info in "${iam_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_category "KMS" "🔑 KMS (Key Management Service) 리소스 수집 시작..."
    
    # KMS 관련 쿼리
    declare -a kms_queries=(
        "KMS 키|select id, arn, aws_account_id, creation_date, enabled, description, key_usage, customer_master_key_spec, key_state, deletion_date, valid_to, origin, key_manager, multi_region, multi_region_configuration, key_rotation_enabled, policy, policy_std, tags from aws_kms_key where region = '$REGION'|security_kms_keys.json"
        "KMS 별칭|select alias_name, arn, target_key_id, creation_date, last_updated_date from aws_kms_alias where region = '$REGION'|security_kms_aliases.json"
    )
    
    # KMS 쿼리 실행
    for query_info in "${kms_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_category "SECRETS" "🔐 Secrets Manager & Parameter Store 수집 시작..."
    
    # Secrets Manager 및 Parameter Store 쿼리
    declare -a secrets_queries=(
        "Secrets Manager 시크릿|select name, arn, description, kms_key_id, rotation_enabled, rotation_lambda_arn, rotation_rules, last_rotated_date, last_changed_date, last_accessed_date, deleted_date, created_date, primary_region, owning_service, tags from aws_secretsmanager_secret where region = '$REGION'|security_secrets_manager.json"
        "SSM Parameter Store|select name, type, value, version, last_modified_date, last_modified_user, allowed_pattern, data_type, policies, tier from aws_ssm_parameter where region = '$REGION'|security_ssm_parameters.json"
    )
    
    # Secrets 쿼리 실행
    for query_info in "${secrets_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_category "GUARDDUTY" "🔍 GuardDuty 위협 탐지 수집 시작..."
    
    # GuardDuty 관련 쿼리
    declare -a guardduty_queries=(
        "GuardDuty 탐지기|select detector_id, status, service_role, created_at, updated_at, data_sources, finding_publishing_frequency, tags from aws_guardduty_detector where region = '$REGION'|security_guardduty_detectors.json"
    )
    
    # GuardDuty 쿼리 실행
    for query_info in "${guardduty_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_category "SECURITYHUB" "🏢 Security Hub 중앙 보안 관리 수집 시작..."
    
    # Security Hub 관련 쿼리
    declare -a securityhub_queries=(
        "Security Hub 허브|select hub_arn, subscribed_at, auto_enable_controls from aws_securityhub_hub where region = '$REGION'|security_securityhub_hub.json"
    )
    
    # Security Hub 쿼리 실행
    for query_info in "${securityhub_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_category "CLOUDTRAIL" "📊 CloudTrail 감사 로깅 수집 시작..."
    
    # CloudTrail 관련 쿼리
    declare -a cloudtrail_queries=(
        "CloudTrail 추적|select name, arn, s3_bucket_name, s3_key_prefix, include_global_service_events, is_multi_region_trail, enable_log_file_validation, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn, kms_key_id, has_custom_event_selectors, has_insight_selectors, is_organization_trail, home_region, trail_arn, log_file_validation_enabled, event_selectors, insight_selectors, tags from aws_cloudtrail_trail where region = '$REGION'|security_cloudtrail_trails.json"
    )
    
    # CloudTrail 쿼리 실행
    for query_info in "${cloudtrail_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "종합 보안 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in security_*.json; do
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
    
    # 카테고리별 수집 현황
    echo -e "\n${BLUE}📋 카테고리별 수집 현황:${NC}"
    echo "🔐 IAM 리소스: 5개"
    echo "🔑 KMS 암호화: 2개"
    echo "🔐 Secrets & Parameters: 2개"
    echo "🔍 GuardDuty 위협 탐지: 1개"
    echo "🏢 Security Hub: 1개"
    echo "📊 CloudTrail 감사: 1개"
    echo "📊 총 리소스 타입: $total_count개"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 종합 보안 데이터를 바탕으로 보안 태세 분석 진행"
    echo "2. IAM 권한 최소화 및 액세스 키 보안 검토"
    echo "3. KMS 키 관리 및 암호화 정책 최적화"
    echo "4. GuardDuty를 통한 위협 탐지 및 대응 체계 구축"
    echo "5. Security Hub를 통한 중앙 집중식 보안 관리 강화"
    echo "6. CloudTrail을 통한 규정 준수 및 감사 체계 강화"
    
    log_info "🎉 종합 보안 리소스 데이터 수집이 완료되었습니다!"
}

# 스크립트 실행
main "$@"
