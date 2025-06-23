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
    declare -a queries=(
        "EBS 볼륨 상세 정보|select volume_id, volume_type, size, state, encrypted, kms_key_id, availability_zone, create_time, attachments, snapshot_id, iops, throughput, multi_attach_enabled, outpost_arn, fast_restored, tags from aws_ebs_volume where region = '$REGION'|storage_ebs_volumes.json"
        "EBS 스냅샷 상세 정보|echo '[]'|storage_ebs_snapshots.json"
        "EBS 암호화 기본 설정|echo '[]'|storage_ebs_encryption_default.json"
        "S3 버킷 상세 정보|select name, arn, region, creation_date, lifecycle_rules, logging, event_notification_configuration, object_lock_configuration, policy, policy_std, replication, server_side_encryption_configuration, versioning_enabled, versioning_mfa_delete, website_configuration, block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets, tags from aws_s3_bucket|storage_s3_buckets.json"
        "S3 버킷 정책|echo '[]'|storage_s3_bucket_policies.json"
        "S3 버킷 퍼블릭 액세스 차단|echo '[]'|storage_s3_public_access_block.json"
        "S3 버킷 CORS 구성|echo '[]'|storage_s3_cors.json"
        "S3 버킷 수명 주기 구성|echo '[]'|storage_s3_lifecycle.json"
        "S3 버킷 복제 구성|echo '[]'|storage_s3_replication.json"
        "S3 버킷 버전 관리|echo '[]'|storage_s3_versioning.json"
        "S3 버킷 로깅|echo '[]'|storage_s3_logging.json"
        "S3 버킷 알림|echo '[]'|storage_s3_notifications.json"
        "S3 버킷 웹사이트 구성|echo '[]'|storage_s3_website.json"
        "S3 Glacier 볼트|select vault_name, vault_arn, creation_date, last_inventory_date, number_of_archives, size_in_bytes, tags from aws_glacier_vault where region = '$REGION'|storage_glacier_vaults.json"
        "EFS 파일 시스템 상세 정보|select file_system_id, arn, creation_token, creation_time, life_cycle_state, name, number_of_mount_targets, owner_id, performance_mode, provisioned_throughput_in_mibps, throughput_mode, encrypted, kms_key_id, automatic_backups, replication_overwrite_protection, availability_zone_name, availability_zone_id, tags from aws_efs_file_system where region = '$REGION'|storage_efs_file_systems.json"
        "EFS 액세스 포인트|select access_point_id, access_point_arn, file_system_id, posix_user, root_directory, client_token, life_cycle_state, name, owner_id, tags from aws_efs_access_point where region = '$REGION'|storage_efs_access_points.json"
        "EFS 마운트 타겟|select mount_target_id, file_system_id, subnet_id, life_cycle_state, ip_address, network_interface_id, availability_zone_id, availability_zone_name, vpc_id, owner_id from aws_efs_mount_target where region = '$REGION'|storage_efs_mount_targets.json"
        "EFS 백업 정책|echo '[]'|storage_efs_backup_policies.json"
        "FSx 파일 시스템|select file_system_id, file_system_type, file_system_type_version, lifecycle, failure_details, storage_capacity, storage_type, vpc_id, subnet_ids, network_interface_ids, dns_name, kms_key_id, arn, tags, creation_time, lustre_configuration, ontap_configuration, open_zfs_configuration, windows_configuration from aws_fsx_file_system where region = '$REGION'|storage_fsx_file_systems.json"
        "FSx 백업|echo '[]'|storage_fsx_backups.json"
        "Storage Gateway|echo '[]'|storage_gateway_gateways.json"
        "AWS Backup 볼트|select name, arn, creation_date, creator_request_id, number_of_recovery_points, locked, min_retention_days, max_retention_days, lock_date, encryption_key_arn from aws_backup_vault where region = '$REGION'|storage_backup_vaults.json"
        "AWS Backup 계획|select backup_plan_id, arn, name, creation_date, deletion_date, last_execution_date, advanced_backup_settings, backup_plan from aws_backup_plan where region = '$REGION'|storage_backup_plans.json"
        "AWS Backup 작업|select job_id, backup_vault_name, resource_arn, creation_date, completion_date, status, status_message, percent_done, backup_size, iam_role_arn, expected_completion_date, start_by, resource_type, bytes_transferred, backup_options, backup_type, parent_job_id, is_parent from aws_backup_job where region = '$REGION'|storage_backup_jobs.json"
        "Data Lifecycle Manager 정책|select policy_id, description, state, status_message, execution_role_arn, date_created, date_modified, policy_details, tags from aws_dlm_lifecycle_policy where region = '$REGION'|storage_dlm_policies.json"
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
    log_success "스토리지 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    log_info "🎉 스토리지 리소스 데이터 수집이 완료되었습니다!"
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
