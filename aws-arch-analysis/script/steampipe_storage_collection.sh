#!/bin/bash
# Steampipe 기반 스토리지 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_storage_collection.log"
ERROR_LOG="steampipe_storage_errors.log"

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
    log_info "💾 Steampipe 기반 스토리지 리소스 데이터 수집 시작"
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
    
    log_info "💾 스토리지 리소스 수집 시작..."
    
    # 스토리지 리소스 수집 배열
    declare -a storage_queries=(
        "EBS 볼륨 상세 정보|select volume_id, volume_type, size, state, encrypted, kms_key_id, availability_zone, create_time, attachments, snapshot_id, iops, throughput, multi_attach_enabled, outpost_arn, fast_restored, tags from aws_ebs_volume where region = '$REGION'|storage_ebs_volumes.json"
        "EBS 스냅샷 상세 정보|select snapshot_id, volume_id, volume_size, state, start_time, progress, owner_id, description, encrypted, kms_key_id, data_encryption_key_id, outpost_arn, storage_tier, restore_expiry_time, tags from aws_ebs_snapshot where region = '$REGION' and owner_id = (select account_id from aws_caller_identity)|storage_ebs_snapshots.json"
        "EBS 암호화 기본 설정|select ebs_encryption_by_default, ebs_default_kms_key_id from aws_ec2_regional_settings where region = '$REGION'|storage_ebs_encryption_default.json"
        "S3 버킷 상세 정보|select name, arn, region, creation_date, lifecycle_rules, logging, event_notification_configuration, object_lock_configuration, policy, policy_std, replication, server_side_encryption_configuration, versioning_enabled, versioning_mfa_delete, website_configuration, block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets, tags from aws_s3_bucket|storage_s3_buckets.json"
        "S3 버킷 정책|select name, policy, policy_std from aws_s3_bucket where policy is not null|storage_s3_bucket_policies.json"
        "S3 버킷 퍼블릭 액세스 차단|select name, block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets from aws_s3_bucket|storage_s3_public_access_block.json"
        "S3 버킷 CORS 구성|select name, cors_rules from aws_s3_bucket where cors_rules is not null|storage_s3_cors.json"
        "S3 버킷 수명 주기 구성|select name, lifecycle_rules from aws_s3_bucket where lifecycle_rules is not null|storage_s3_lifecycle.json"
        "S3 버킷 복제 구성|select name, replication from aws_s3_bucket where replication is not null|storage_s3_replication.json"
        "S3 버킷 버전 관리|select name, versioning_enabled, versioning_mfa_delete from aws_s3_bucket|storage_s3_versioning.json"
        "S3 버킷 로깅|select name, logging from aws_s3_bucket where logging is not null|storage_s3_logging.json"
        "S3 버킷 알림|select name, event_notification_configuration from aws_s3_bucket where event_notification_configuration is not null|storage_s3_notifications.json"
        "S3 버킷 웹사이트 구성|select name, website_configuration from aws_s3_bucket where website_configuration is not null|storage_s3_website.json"
        "S3 Glacier 볼트|select vault_name, vault_arn, creation_date, last_inventory_date, number_of_archives, size_in_bytes, tags from aws_glacier_vault where region = '$REGION'|storage_glacier_vaults.json"
        "EFS 파일 시스템 상세 정보|select file_system_id, arn, creation_token, creation_time, life_cycle_state, name, number_of_mount_targets, owner_id, performance_mode, provisioned_throughput_in_mibps, throughput_mode, encrypted, kms_key_id, automatic_backups, replication_overwrite_protection, availability_zone_name, availability_zone_id, tags from aws_efs_file_system where region = '$REGION'|storage_efs_file_systems.json"
        "EFS 액세스 포인트|select access_point_id, access_point_arn, file_system_id, posix_user, root_directory, client_token, life_cycle_state, name, owner_id, tags from aws_efs_access_point where region = '$REGION'|storage_efs_access_points.json"
        "EFS 마운트 타겟|select mount_target_id, file_system_id, subnet_id, life_cycle_state, ip_address, network_interface_id, availability_zone_id, availability_zone_name, vpc_id, owner_id from aws_efs_mount_target where region = '$REGION'|storage_efs_mount_targets.json"
        "EFS 백업 정책|select file_system_id, backup_policy from aws_efs_backup_policy where region = '$REGION'|storage_efs_backup_policies.json"
        "FSx 파일 시스템|select file_system_id, file_system_type, file_system_type_version, lifecycle, failure_details, storage_capacity, storage_type, vpc_id, subnet_ids, network_interface_ids, dns_name, kms_key_id, arn, tags, creation_time, lustre_configuration, ontap_configuration, open_zfs_configuration, windows_configuration from aws_fsx_file_system where region = '$REGION'|storage_fsx_file_systems.json"
        "FSx 백업|select backup_id, file_system_id, type, lifecycle, failure_details, progress_percent, creation_time, kms_key_id, resource_arn, tags, volume_id, source_backup_id, source_backup_region, resource_type, backup_type from aws_fsx_backup where region = '$REGION'|storage_fsx_backups.json"
        "Storage Gateway|select gateway_id, gateway_name, gateway_timezone, gateway_type, gateway_state, ec2_instance_id, ec2_instance_region, host_environment, host_environment_id, endpoint_type, gateway_capacity, supported_gateway_capacities, deprecation_date, software_updates_end_date, tags from aws_storagegateway_gateway where region = '$REGION'|storage_gateway_gateways.json"
        "AWS Backup 볼트|select name, arn, creation_date, creator_request_id, number_of_recovery_points, locked, min_retention_days, max_retention_days, lock_date, encryption_key_arn from aws_backup_vault where region = '$REGION'|storage_backup_vaults.json"
        "AWS Backup 계획|select backup_plan_id, arn, name, creation_date, deletion_date, last_execution_date, advanced_backup_settings, backup_plan from aws_backup_plan where region = '$REGION'|storage_backup_plans.json"
        "AWS Backup 작업|select job_id, backup_vault_name, resource_arn, creation_date, completion_date, status, status_message, percent_done, backup_size, iam_role_arn, expected_completion_date, start_by, resource_type, bytes_transferred, backup_options, backup_type, parent_job_id, is_parent from aws_backup_job where region = '$REGION'|storage_backup_jobs.json"
        "Data Lifecycle Manager 정책|select policy_id, description, state, status_message, execution_role_arn, date_created, date_modified, policy_details, tags from aws_dlm_lifecycle_policy where region = '$REGION'|storage_dlm_policies.json"
    )
    
    # 스토리지 리소스 쿼리 실행
    for query_info in "${storage_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "스토리지 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in storage_*.json; do
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
    echo "1. 수집된 스토리지 데이터를 바탕으로 Phase 1 인프라 분석 진행"
    echo "2. EBS 볼륨 성능 및 비용 최적화 분석"
    echo "3. S3 버킷 보안 설정 및 수명 주기 정책 검토"
    echo "4. EFS 및 FSx 파일 시스템 성능 분석"
    echo "5. 백업 전략 및 데이터 보호 정책 검토"
    
    log_info "🎉 스토리지 리소스 데이터 수집이 완료되었습니다!"
}

# 도움말 함수
show_help() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -r, --region REGION    AWS 리전 설정 (기본값: ap-northeast-2)"
    echo "  -d, --dir DIRECTORY    보고서 디렉토리 설정 (기본값: ~/report)"
    echo "  -h, --help            이 도움말 표시"
    echo ""
    echo "환경 변수:"
    echo "  AWS_REGION            AWS 리전 설정"
    echo "  REPORT_DIR            보고서 디렉토리 설정"
    echo ""
    echo "예시:"
    echo "  $0                                    # 기본 설정으로 실행"
    echo "  $0 -r us-east-1                      # 특정 리전으로 실행"
    echo "  $0 -d /custom/path                   # 사용자 정의 디렉토리로 실행"
    echo "  AWS_REGION=eu-west-1 $0              # 환경 변수로 리전 설정"
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
            show_help
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 스크립트 실행
main "$@"
