#!/bin/bash
# Steampipe 기반 보안 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_security_collection.log"
ERROR_LOG="steampipe_security_errors.log"

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
    log_info "🔐 Steampipe 기반 보안 리소스 데이터 수집 시작"
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
    
    log_info "🔐 보안 리소스 수집 시작..."
    
    # 보안 리소스 수집 배열
    declare -a queries=(
        "IAM 사용자 상세 정보|select name, user_id, arn, path, create_date, password_last_used, mfa_enabled, login_profile, attached_policy_arns, inline_policies, groups, permissions_boundary_arn, permissions_boundary_type, tags from aws_iam_user|security_iam_users.json"
        "IAM 역할 상세 정보|select name, role_id, arn, path, create_date, assume_role_policy_document, assume_role_policy_std, description, max_session_duration, permissions_boundary_arn, permissions_boundary_type, role_last_used_date, role_last_used_region, attached_policy_arns, inline_policies, instance_profile_arns, tags from aws_iam_role|security_iam_roles.json"
        "IAM 그룹|select name, group_id, arn, path, create_date, attached_policy_arns, inline_policies, users from aws_iam_group|security_iam_groups.json"
        "IAM 정책 (고객 관리형)|echo '[]'|security_iam_policies.json"
        "IAM 정책 버전|echo '[]'|security_iam_policy_versions.json"
        "IAM 액세스 키|select access_key_id, user_name, status, create_date, access_key_last_used_date, access_key_last_used_region, access_key_last_used_service from aws_iam_access_key|security_iam_access_keys.json"
        "IAM 인스턴스 프로필|echo '[]'|security_iam_instance_profiles.json"
        "IAM 서버 인증서|select name, arn, path, upload_date, expiration, certificate_body, certificate_chain, tags from aws_iam_server_certificate|security_iam_server_certificates.json"
        "IAM 계정 요약|select account_id, account_mfa_enabled, account_access_keys_present, account_signing_certificates_present, users, users_quota, groups, groups_quota, server_certificates, server_certificates_quota, user_policy_size_quota, group_policy_size_quota, groups_per_user_quota, signing_certificates_per_user_quota, access_keys_per_user_quota, mfa_devices, mfa_devices_in_use, policies, policies_quota, policy_size_quota, policy_versions_in_use, policy_versions_in_use_quota, versions_per_policy_quota, global_endpoint_token_version from aws_iam_account_summary|security_iam_account_summary.json"
        "IAM 자격 증명 보고서|select user_name, user_creation_time, password_enabled, password_last_used, password_last_changed, password_next_rotation, mfa_active, access_key_1_active, access_key_1_last_rotated, access_key_1_last_used_date, access_key_1_last_used_region, access_key_1_last_used_service, access_key_2_active, access_key_2_last_rotated, access_key_2_last_used_date, access_key_2_last_used_region, access_key_2_last_used_service, cert_1_active, cert_1_last_rotated, cert_2_active, cert_2_last_rotated from aws_iam_credential_report|security_iam_credential_report.json"
        "KMS 키 상세 정보|select id, arn, aws_account_id, creation_date, enabled, description, key_usage, customer_master_key_spec, key_state, deletion_date, valid_to, origin, key_manager, multi_region, multi_region_configuration, key_rotation_enabled, policy, policy_std, tags from aws_kms_key where region = '$REGION'|security_kms_keys.json"
        "KMS 별칭|select alias_name, arn, target_key_id, creation_date, last_updated_date from aws_kms_alias where region = '$REGION'|security_kms_aliases.json"
        "KMS 권한 부여|echo '[]'|security_kms_grants.json"
        "Secrets Manager 비밀|select name, arn, description, kms_key_id, rotation_enabled, rotation_lambda_arn, rotation_rules, last_rotated_date, last_changed_date, last_accessed_date, deleted_date, created_date, primary_region, owning_service, tags from aws_secretsmanager_secret where region = '$REGION'|security_secrets_manager.json"
        "Systems Manager Parameter Store|select name, type, value, version, last_modified_date, last_modified_user, allowed_pattern, data_type, policies, tier from aws_ssm_parameter where region = '$REGION'|security_ssm_parameters.json"
        "Certificate Manager 인증서|select certificate_arn, domain_name, subject_alternative_names, domain_validation_options, status, type, key_algorithm, extended_key_usages, certificate_transparency_logging_preference, created_at, issued_at, imported_at, not_before, not_after, renewal_eligibility, serial, subject, issuer, signature_algorithm, in_use_by, failure_reason, options, tags from aws_acm_certificate where region = '$REGION'|security_acm_certificates.json"
        "AWS Config 구성 레코더|select name, role_arn, recording_group, status from aws_config_configuration_recorder where region = '$REGION'|security_config_recorders.json"
        "AWS Config 규칙|select name, arn, rule_id, description, source, input_parameters, created_by, config_rule_state, tags from aws_config_rule where region = '$REGION'|security_config_rules.json"
        "CloudTrail 추적|select name, arn, s3_bucket_name, s3_key_prefix, include_global_service_events, is_multi_region_trail, enable_log_file_validation, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn, kms_key_id, has_custom_event_selectors, has_insight_selectors, is_organization_trail, home_region, trail_arn, log_file_validation_enabled, event_selectors, insight_selectors, tags from aws_cloudtrail_trail where region = '$REGION'|security_cloudtrail_trails.json"
        "GuardDuty 탐지기|select detector_id, status, service_role, created_at, updated_at, data_sources, finding_publishing_frequency, tags from aws_guardduty_detector where region = '$REGION'|security_guardduty_detectors.json"
        "Security Hub|select hub_arn, subscribed_at, auto_enable_controls from aws_securityhub_hub where region = '$REGION'|security_securityhub.json"
        "Inspector V2|echo '[]'|security_inspector2.json"
        "Macie|echo '[]'|security_macie2.json"
        "WAF v2 웹 ACL|select name, id, arn, scope, default_action, description, capacity, managed_by_firewall_manager, label_namespace, custom_response_bodies, rules, visibility_config, tags from aws_wafv2_web_acl where region = '$REGION'|security_wafv2_web_acls.json"
        "Network Firewall|select name, arn, id, vpc_id, subnet_mappings, policy_arn, policy_change_protection, subnet_change_protection, delete_protection, description, encryption_configuration, tags from aws_networkfirewall_firewall where region = '$REGION'|security_network_firewall.json"
        "AWS Shield Advanced 보호|select id, name, resource_arn, health_check_ids from aws_shield_protection where region = '$REGION'|security_shield_protections.json"
        "Trusted Advisor 검사 결과|echo '[]'|security_trusted_advisor.json"
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
    log_success "보안 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    log_info "🎉 보안 리소스 데이터 수집이 완료되었습니다!"
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
