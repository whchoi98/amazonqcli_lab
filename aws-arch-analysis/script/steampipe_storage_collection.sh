#!/bin/bash
# 완전한 스토리지 리소스 데이터 수집 스크립트 (모든 스토리지 서비스 포함)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report}"
LOG_FILE="steampipe_storage_collection.log"
ERROR_LOG="steampipe_storage_errors.log"

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

log_storage() {
    echo -e "${PURPLE}[STORAGE]${NC} $1" | tee -a "$LOG_FILE"
}

log_s3() {
    echo -e "${CYAN}[S3]${NC} $1" | tee -a "$LOG_FILE"
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

# 스토리지 서비스 존재 확인 함수
check_storage_services() {
    log_storage "스토리지 서비스 존재 확인 중..."
    
    # S3 버킷 존재 확인
    local s3_buckets=$(aws s3api list-buckets --query 'Buckets | length(@)' --output text 2>/dev/null || echo "0")
    log_info "S3 버킷 개수: $s3_buckets"
    
    # EBS 볼륨 존재 확인
    local ebs_volumes=$(aws ec2 describe-volumes --region "$REGION" --query 'Volumes | length(@)' --output text 2>/dev/null || echo "0")
    log_info "EBS 볼륨 개수: $ebs_volumes"
    
    # EFS 파일 시스템 존재 확인
    local efs_filesystems=$(aws efs describe-file-systems --region "$REGION" --query 'FileSystems | length(@)' --output text 2>/dev/null || echo "0")
    log_info "EFS 파일 시스템 개수: $efs_filesystems"
    
    if [ "$s3_buckets" -eq 0 ] && [ "$ebs_volumes" -eq 0 ] && [ "$efs_filesystems" -eq 0 ]; then
        log_warning "주요 스토리지 서비스가 발견되지 않았습니다. 데이터 수집을 계속 진행합니다."
    fi
}

# 메인 함수
main() {
    log_storage "🚀 완전한 스토리지 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 디렉토리 생성
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
    
    # 스토리지 서비스 확인
    check_storage_services
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_storage "💾 블록 스토리지 리소스 수집 시작..."
    
    # 블록 스토리지 관련 리소스 수집 배열
    declare -a block_storage_queries=(
        "EBS 볼륨|select volume_id, volume_type, size, state, availability_zone, create_time, encrypted, kms_key_id, iops, throughput, multi_attach_enabled, snapshot_id, attachments, tags from aws_ebs_volume where region = '$REGION'|storage_ebs_volumes.json"
        "EBS 스냅샷|select snapshot_id, description, volume_id, volume_size, state, start_time, progress, owner_id, encrypted, kms_key_id, data_encryption_key_id, tags from aws_ebs_snapshot where region = '$REGION' and owner_id = (select account_id from aws_caller_identity)|storage_ebs_snapshots.json"
        "EBS 볼륨 메트릭 읽기 IOPS|select volume_id, timestamp, maximum, minimum, average, sum, sample_count from aws_ebs_volume_metric_read_ops where region = '$REGION' and timestamp >= now() - interval '1 hour'|storage_ebs_volume_metric_read_ops.json"
        "EBS 볼륨 메트릭 쓰기 IOPS|select volume_id, timestamp, maximum, minimum, average, sum, sample_count from aws_ebs_volume_metric_write_ops where region = '$REGION' and timestamp >= now() - interval '1 hour'|storage_ebs_volume_metric_write_ops.json"
        "EBS 볼륨 메트릭 읽기 바이트|select volume_id, timestamp, maximum, minimum, average, sum, sample_count from aws_ebs_volume_metric_read_bytes where region = '$REGION' and timestamp >= now() - interval '1 hour'|storage_ebs_volume_metric_read_bytes.json"
        "EBS 볼륨 메트릭 쓰기 바이트|select volume_id, timestamp, maximum, minimum, average, sum, sample_count from aws_ebs_volume_metric_write_bytes where region = '$REGION' and timestamp >= now() - interval '1 hour'|storage_ebs_volume_metric_write_bytes.json"
    )
    
    # 블록 스토리지 리소스 쿼리 실행
    for query_info in "${block_storage_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_s3 "🪣 객체 스토리지 (S3) 리소스 수집 시작..."
    
    # 객체 스토리지 관련 리소스 수집 배열
    declare -a object_storage_queries=(
        "S3 버킷|select name, region, creation_date, versioning_enabled, versioning_mfa_delete, logging, policy, policy_std, acl, grant, lifecycle_rules, notification_configuration, accelerate_configuration, request_payment_configuration, replication, server_side_encryption_configuration, website_configuration, cors_rules, public_access_block_configuration, bucket_policy_is_public, tags from aws_s3_bucket|storage_s3_buckets.json"
        "S3 객체|select bucket_name, key, last_modified, etag, size, storage_class, owner_display_name, owner_id from aws_s3_object where bucket_name in (select name from aws_s3_bucket limit 10)|storage_s3_objects.json"
        "S3 액세스 포인트|select name, bucket, network_origin, vpc_id, policy, policy_status, creation_date, public_access_block_configuration from aws_s3_access_point where region = '$REGION'|storage_s3_access_points.json"
        "S3 멀티 리전 액세스 포인트|select name, alias, status, public_access_block_configuration, created_at, regions from aws_s3_multi_region_access_point|storage_s3_multi_region_access_points.json"
        "S3 멀티파트 업로드|select bucket_name, key, upload_id, initiated, initiator_display_name, initiator_id, owner_display_name, owner_id, storage_class from aws_s3_multipart_upload|storage_s3_multipart_uploads.json"
        "S3 인텔리전트 티어링|select bucket_name, id, status, filter, tierings from aws_s3_bucket_intelligent_tiering_configuration|storage_s3_intelligent_tiering.json"
        "S3 버킷 메트릭|select name, bucket_size_bytes, number_of_objects from aws_s3_bucket_metric_bucket_size_bytes where timestamp >= now() - interval '1 day'|storage_s3_bucket_metrics.json"
        "S3 버킷 정책|select name, policy, policy_std from aws_s3_bucket where policy is not null|storage_s3_bucket_policies.json"
        "S3 버킷 CORS|select name, cors_rules from aws_s3_bucket where cors_rules is not null|storage_s3_bucket_cors.json"
        "S3 버킷 라이프사이클|select name, lifecycle_rules from aws_s3_bucket where lifecycle_rules is not null|storage_s3_bucket_lifecycle.json"
    )
    
    # 객체 스토리지 리소스 쿼리 실행
    for query_info in "${object_storage_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "📁 파일 시스템 리소스 수집 시작..."
    
    # 파일 시스템 관련 리소스 수집 배열
    declare -a file_system_queries=(
        "EFS 파일 시스템|select file_system_id, name, creation_token, creation_time, life_cycle_state, number_of_mount_targets, size_in_bytes, performance_mode, throughput_mode, provisioned_throughput_in_mibps, encrypted, kms_key_id, policy, backup_policy, tags from aws_efs_file_system where region = '$REGION'|storage_efs_file_systems.json"
        "EFS 액세스 포인트|select access_point_id, access_point_arn, file_system_id, path, creation_info, posix_user, root_directory, client_token, life_cycle_state, name, tags from aws_efs_access_point where region = '$REGION'|storage_efs_access_points.json"
        "EFS 마운트 타겟|select mount_target_id, file_system_id, subnet_id, ip_address, network_interface_id, availability_zone_id, availability_zone_name, owner_id, life_cycle_state, security_groups from aws_efs_mount_target where region = '$REGION'|storage_efs_mount_targets.json"
        "EFS 백업 정책|select file_system_id, backup_policy from aws_efs_backup_policy where region = '$REGION'|storage_efs_backup_policies.json"
        "FSx 파일 시스템|select file_system_id, file_system_type, lifecycle_state, failure_details, storage_capacity, storage_type, vpc_id, subnet_ids, network_interface_ids, dns_name, kms_key_id, resource_arn, tags, creation_time, lustre_configuration, windows_configuration, ontap_configuration, open_zfs_configuration from aws_fsx_file_system where region = '$REGION'|storage_fsx_file_systems.json"
        "FSx 백업|select backup_id, lifecycle, failure_details, type, progress_percent, creation_time, kms_key_id, resource_arn, tags, file_system, directory_information, volume from aws_fsx_backup where region = '$REGION'|storage_fsx_backups.json"
    )
    
    # 파일 시스템 리소스 쿼리 실행
    for query_info in "${file_system_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "🗄️ 아카이브 스토리지 리소스 수집 시작..."
    
    # 아카이브 스토리지 관련 리소스 수집 배열
    declare -a archive_storage_queries=(
        "Glacier 볼트|select vault_name, vault_arn, creation_date, last_inventory_date, number_of_archives, size_in_bytes from aws_glacier_vault where region = '$REGION'|storage_glacier_vaults.json"
        "Glacier 볼트 액세스 정책|select vault_name, policy from aws_glacier_vault_access_policy where region = '$REGION'|storage_glacier_vault_policies.json"
        "Glacier 볼트 알림|select vault_name, sns_topic, events from aws_glacier_vault_notification where region = '$REGION'|storage_glacier_vault_notifications.json"
    )
    
    # 아카이브 스토리지 리소스 쿼리 실행
    for query_info in "${archive_storage_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "🌉 스토리지 게이트웨이 리소스 수집 시작..."
    
    # 스토리지 게이트웨이 관련 리소스 수집 배열
    declare -a storage_gateway_queries=(
        "Storage Gateway|select gateway_id, gateway_name, gateway_type, gateway_operational_state, gateway_network_interfaces, ec2_instance_id, ec2_instance_region, host_environment, host_environment_id, endpoint_type, gateway_capacity, supported_gateway_capacities, deprecation_date, software_updates_end_date, tags from aws_storagegateway_gateway where region = '$REGION'|storage_gateway_gateways.json"
        "Storage Gateway 로컬 디스크|select gateway_arn, disk_id, disk_path, disk_node, disk_status, disk_size_in_bytes, disk_allocation_type from aws_storagegateway_local_disk where region = '$REGION'|storage_gateway_local_disks.json"
        "Storage Gateway 볼륨|select volume_arn, volume_id, gateway_arn, volume_type, volume_status, volume_size_in_bytes, volume_progress, source_snapshot_id, preserved_existing_data, iscsi_attributes, created_date, kms_key, target_name from aws_storagegateway_volume where region = '$REGION'|storage_gateway_volumes.json"
        "Storage Gateway 파일 공유|select file_share_arn, file_share_id, file_share_status, file_share_type, gateway_arn, path, role, location_arn, default_storage_class, object_acl, read_only, guess_mime_type_enabled, valid_user_list, invalid_user_list, audit_destination_arn, authentication, case_sensitivity, tags, cache_attributes, notification_policy from aws_storagegateway_file_share where region = '$REGION'|storage_gateway_file_shares.json"
    )
    
    # 스토리지 게이트웨이 리소스 쿼리 실행
    for query_info in "${storage_gateway_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "💾 백업 및 복구 리소스 수집 시작..."
    
    # 백업 및 복구 관련 리소스 수집 배열
    declare -a backup_queries=(
        "AWS Backup 볼트|select name, backup_vault_arn, recovery_points, creation_date, creator_request_id, encryption_key_arn, number_of_recovery_points from aws_backup_vault where region = '$REGION'|storage_backup_vaults.json"
        "AWS Backup 계획|select name, backup_plan_arn, backup_plan_id, creation_date, creator_request_id, last_execution_date, advanced_backup_settings, backup_plan from aws_backup_plan where region = '$REGION'|storage_backup_plans.json"
        "AWS Backup 작업|select backup_job_id, backup_vault_name, backup_vault_arn, recovery_point_arn, resource_arn, creation_date, completion_date, state, status_message, percent_done, backup_size_in_bytes, iam_role_arn, created_by, expected_completion_date, start_by, resource_type, bytes_transferred, backup_options, backup_type, parent_job_id, is_parent, account_id from aws_backup_job where region = '$REGION'|storage_backup_jobs.json"
        "AWS Backup 복구 포인트|select recovery_point_arn, backup_vault_name, backup_vault_arn, source_backup_vault_arn, resource_arn, resource_type, created_by, iam_role_arn, status, status_message, creation_date, completion_date, backup_size_in_bytes, calculated_lifecycle, lifecycle, encryption_key_arn, is_encrypted, storage_class, last_restore_time, parent_recovery_point_arn, composite_member_identifier, is_parent, vault_type from aws_backup_recovery_point where region = '$REGION'|storage_backup_recovery_points.json"
    )
    
    # 백업 및 복구 리소스 쿼리 실행
    for query_info in "${backup_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "📊 데이터 라이프사이클 관리 리소스 수집 시작..."
    
    # 데이터 라이프사이클 관리 관련 리소스 수집 배열
    declare -a dlm_queries=(
        "DLM 정책|select policy_id, description, state, status_message, execution_role_arn, date_created, date_modified, policy_details, tags, policy_arn from aws_dlm_lifecycle_policy where region = '$REGION'|storage_dlm_policies.json"
    )
    
    # DLM 리소스 쿼리 실행
    for query_info in "${dlm_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "완전한 스토리지 리소스 데이터 수집 완료!"
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
    
    # 카테고리별 수집 현황
    echo -e "\n${BLUE}📋 카테고리별 수집 현황:${NC}"
    echo "💾 블록 스토리지: 6개"
    echo "🪣 객체 스토리지 (S3): 10개"
    echo "📁 파일 시스템: 6개"
    echo "🗄️  아카이브 스토리지: 3개"
    echo "🌉 스토리지 게이트웨이: 4개"
    echo "💾 백업 및 복구: 4개"
    echo "📊 데이터 라이프사이클: 1개"
    echo "📊 총 리소스 타입: 34개"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 완전한 스토리지 데이터를 바탕으로 상세 분석 진행"
    echo "2. EBS 볼륨 타입 및 성능 최적화 검토"
    echo "3. S3 버킷 보안 설정 및 비용 최적화 분석"
    echo "4. 파일 시스템 성능 모드 및 처리량 분석"
    echo "5. 백업 정책 및 데이터 보존 전략 검토"
    echo "6. 스토리지 클래스 최적화 및 라이프사이클 정책 분석"
    echo "7. 아카이브 스토리지 활용도 및 비용 효율성 평가"
    
    log_storage "🎉 완전한 스토리지 리소스 데이터 수집이 완료되었습니다!"
}

# 도움말 함수
show_help() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -r, --region REGION    AWS 리전 설정 (기본값: ap-northeast-2)"
    echo "  -d, --dir DIRECTORY    보고서 디렉토리 설정"
    echo "  -h, --help            이 도움말 표시"
    echo ""
    echo "환경 변수:"
    echo "  AWS_REGION            AWS 리전 설정"
    echo "  REPORT_DIR            보고서 디렉토리 설정"
    echo ""
    echo "필수 요구사항:"
    echo "  - Steampipe 설치"
    echo "  - AWS 플러그인 설치: steampipe plugin install aws"
    echo ""
    echo "수집되는 스토리지 리소스:"
    echo "  💾 블록 스토리지: EBS 볼륨, 스냅샷, 성능 메트릭"
    echo "  🪣 객체 스토리지: S3 버킷, 객체, 액세스 포인트, 정책"
    echo "  📁 파일 시스템: EFS, FSx 파일 시스템"
    echo "  🗄️  아카이브: Glacier 볼트"
    echo "  🌉 하이브리드: Storage Gateway"
    echo "  💾 백업: AWS Backup 서비스"
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
