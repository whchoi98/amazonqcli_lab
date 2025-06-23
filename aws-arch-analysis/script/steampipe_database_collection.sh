#!/bin/bash
# Steampipe 기반 데이터베이스 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_database_collection.log"
ERROR_LOG="steampipe_database_errors.log"

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
    log_info "🗄️ Steampipe 기반 데이터베이스 리소스 데이터 수집 시작"
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
    
    log_info "🗄️ 데이터베이스 리소스 수집 시작..."
    
    # RDS 관련 쿼리
    execute_steampipe_query "RDS 인스턴스 상세 정보" "select db_instance_identifier, arn, class, engine, engine_version, master_user_name, db_name, allocated_storage, max_allocated_storage, storage_type, storage_encrypted, kms_key_id, iops, storage_throughput, status, endpoint_address, endpoint_port, endpoint_hosted_zone_id, multi_az, availability_zone, secondary_availability_zone, publicly_accessible, vpc_security_groups, db_security_groups, db_parameter_groups, db_subnet_group_name, option_group_memberships, preferred_backup_window, backup_retention_period, preferred_maintenance_window, pending_modified_values, latest_restorable_time, auto_minor_version_upgrade, read_replica_source_db_instance_identifier, read_replica_db_instance_identifiers, read_replica_db_cluster_identifiers, replica_mode, license_model, character_set_name, nchar_character_set_name, enhanced_monitoring_resource_arn, monitoring_interval, monitoring_role_arn, promotion_tier, timezone, iam_database_authentication_enabled, performance_insights_enabled, performance_insights_kms_key_id, performance_insights_retention_period, enabled_cloudwatch_logs_exports, processor_features, deletion_protection, associated_roles, tags from aws_rds_db_instance where region = '$REGION'" "database_rds_instances.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "RDS 클러스터 상세 정보" "select db_cluster_identifier, arn, engine, engine_version, engine_mode, master_user_name, database_name, status, endpoint, reader_endpoint, custom_endpoints, multi_az, port, preferred_backup_window, backup_retention_period, preferred_maintenance_window, read_replica_identifiers, members, vpc_security_groups, db_subnet_group, db_cluster_parameter_group, option_group_memberships, availability_zones, character_set_name, kms_key_id, storage_encrypted, associated_roles, iam_database_authentication_enabled, clone_group_id, create_time, earliest_restorable_time, earliest_backtrack_time, backtrack_window, backtrack_consumed_change_records, enabled_cloudwatch_logs_exports, capacity, scaling_configuration_info, deletion_protection, http_endpoint_enabled, activity_stream_mode, activity_stream_status, activity_stream_kms_key_id, activity_stream_kinesis_stream_name, copy_tags_to_snapshot, cross_account_clone, domain_memberships, tags from aws_rds_db_cluster where region = '$REGION'" "database_rds_clusters.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "RDS 스냅샷" "select db_snapshot_identifier, db_instance_identifier, create_time, engine, allocated_storage, status, port, availability_zone, vpc_id, instance_create_time, master_user_name, engine_version, license_model, type, iops, option_group_name, percent_progress, source_region, source_db_snapshot_identifier, storage_type, tde_credential_arn, encrypted, kms_key_id, timezone, iam_database_authentication_enabled, processor_features, dbi_resource_id, tags from aws_rds_db_snapshot where region = '$REGION'" "database_rds_snapshots.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "RDS 클러스터 스냅샷" "select db_cluster_snapshot_identifier, db_cluster_identifier, create_time, engine, engine_version, allocated_storage, status, port, vpc_id, cluster_create_time, master_user_name, license_model, type, percent_progress, storage_encrypted, kms_key_id, arn, source_db_cluster_snapshot_arn, iam_database_authentication_enabled, tags from aws_rds_db_cluster_snapshot where region = '$REGION'" "database_rds_cluster_snapshots.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "RDS 서브넷 그룹" "select name, arn, description, status, vpc_id, subnets, tags from aws_rds_db_subnet_group where region = '$REGION'" "database_rds_subnet_groups.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "RDS 파라미터 그룹" "select name, arn, description, db_parameter_group_family, parameters, tags from aws_rds_db_parameter_group where region = '$REGION'" "database_rds_parameter_groups.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "RDS 옵션 그룹" "select name, arn, description, engine_name, major_engine_version, vpc_id, allows_vpc_and_non_vpc_instance_memberships, options, tags from aws_rds_db_option_group where region = '$REGION'" "database_rds_option_groups.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "RDS 이벤트 구독" "select cust_subscription_id, customer_aws_id, sns_topic_arn, status, subscription_creation_time, source_type, source_ids_list, event_categories_list, enabled from aws_rds_db_event_subscription where region = '$REGION'" "database_rds_event_subscriptions.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    # DynamoDB 관련 쿼리
    execute_steampipe_query "DynamoDB 테이블 상세 정보" "select name, arn, table_id, table_status, creation_date_time, billing_mode, attribute_definitions, key_schema, table_size_bytes, item_count, stream_specification, latest_stream_label, latest_stream_arn, restore_summary, sse_description, replicas, archival_summary, table_class, deletion_protection_enabled, tags from aws_dynamodb_table where region = '$REGION'" "database_dynamodb_tables.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "DynamoDB 백업" "select name, arn, table_name, table_arn, table_id, backup_status, backup_type, backup_creation_datetime, backup_expiry_datetime, backup_size_bytes from aws_dynamodb_backup where region = '$REGION'" "database_dynamodb_backups.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "DynamoDB Global Tables" "select global_table_name, global_table_status, creation_date_time, global_table_arn, replication_group from aws_dynamodb_global_table where region = '$REGION'" "database_dynamodb_global_tables.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    # ElastiCache 관련 쿼리
    execute_steampipe_query "ElastiCache 클러스터 상세 정보" "select cache_cluster_id, configuration_endpoint, client_download_landing_page, cache_node_type, engine, engine_version, cache_cluster_status, num_cache_nodes, preferred_availability_zone, preferred_outpost_arn, cache_cluster_create_time, preferred_maintenance_window, pending_modified_values, notification_configuration, cache_security_groups, cache_parameter_group, cache_subnet_group_name, cache_nodes, auto_minor_version_upgrade, security_groups, replication_group_id, snapshot_retention_limit, snapshot_window, auth_token_enabled, auth_token_last_modified_date, transit_encryption_enabled, at_rest_encryption_enabled, arn, replication_group_log_delivery_enabled, log_delivery_configurations, network_type, ip_discovery, transit_encryption_mode, tags from aws_elasticache_cluster where region = '$REGION'" "database_elasticache_clusters.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "ElastiCache 복제 그룹" "select replication_group_id, description, global_replication_group_info, status, pending_modified_values, member_clusters, node_groups, snapshotting_cluster_id, automatic_failover, multi_az, configuration_endpoint, snapshot_retention_limit, snapshot_window, cluster_enabled, cache_node_type, auth_token_enabled, auth_token_last_modified_date, transit_encryption_enabled, at_rest_encryption_enabled, member_clusters_outpost_arns, kms_key_id, arn, user_group_ids, log_delivery_configurations, replication_group_create_time, data_tiering, network_type, ip_discovery, transit_encryption_mode, cluster_mode from aws_elasticache_replication_group where region = '$REGION'" "database_elasticache_replication_groups.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "ElastiCache 서브넷 그룹" "select cache_subnet_group_name, cache_subnet_group_description, vpc_id, subnets, arn, supported_network_types from aws_elasticache_subnet_group where region = '$REGION'" "database_elasticache_subnet_groups.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "ElastiCache 파라미터 그룹" "select cache_parameter_group_name, cache_parameter_group_family, description, is_global, arn from aws_elasticache_parameter_group where region = '$REGION'" "database_elasticache_parameter_groups.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    # 기타 데이터베이스 서비스
    execute_steampipe_query "Redshift 클러스터" "select cluster_identifier, node_type, cluster_status, cluster_availability_status, modify_status, master_username, db_name, endpoint, cluster_create_time, automated_snapshot_retention_period, manual_snapshot_retention_period, cluster_security_groups, vpc_security_groups, cluster_parameter_groups, cluster_subnet_group_name, vpc_id, availability_zone, preferred_maintenance_window, pending_modified_values, cluster_version, allow_version_upgrade, number_of_nodes, publicly_accessible, encrypted, restore_status, data_transfer_progress, hsm_status, cluster_snapshot_copy_status, cluster_public_key, cluster_nodes, elastic_ip_status, cluster_revision_number, tags, kms_key_id, enhanced_vpc_routing, iam_roles, pending_actions, maintenance_track_name, elastic_resize_number_of_node_options, deferred_maintenance_windows, snapshot_schedule_identifier, snapshot_schedule_state, expected_next_snapshot_schedule_time, expected_next_snapshot_schedule_time_status, next_maintenance_window_start_time, resize_info, availability_zone_relocation_status, cluster_namespace_arn, total_storage_capacity_in_mega_bytes, aqua_configuration, default_iam_role_arn, reserved_node_exchange_status from aws_redshift_cluster where region = '$REGION'" "database_redshift_clusters.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "DocumentDB 클러스터" "select db_cluster_identifier, members, backup_retention_period, preferred_backup_window, preferred_maintenance_window, port, master_user_name, engine, engine_version, latest_restorable_time, multi_az, storage_encrypted, kms_key_id, db_cluster_resource_id, arn, associated_roles, vpc_security_groups, db_subnet_group, cluster_create_time, enabled_cloudwatch_logs_exports, deletion_protection, tags from aws_docdb_cluster where region = '$REGION'" "database_docdb_clusters.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "Neptune 클러스터" "select db_cluster_identifier, cluster_members, backup_retention_period, preferred_backup_window, preferred_maintenance_window, port, master_username, engine, engine_version, latest_restorable_time, multi_az, storage_encrypted, kms_key_id, db_cluster_resource_id, db_cluster_arn, associated_roles, vpc_security_groups, db_subnet_group_name, activity_stream_mode, activity_stream_status, activity_stream_kms_key_id, activity_stream_kinesis_stream_name, cluster_create_time, copy_tags_to_snapshot, cross_account_clone, enabled_cloudwatch_logs_exports, deletion_protection, tags from aws_neptune_cluster where region = '$REGION'" "database_neptune_clusters.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "MemoryDB 클러스터" "select name, description, status, pending_updates, number_of_shards, cluster_endpoint, node_type, engine_version, engine_patch_version, parameter_group_name, parameter_group_status, security_groups, subnet_group_name, tls_enabled, kms_key_id, arn, sns_topic_arn, sns_topic_status, snapshot_retention_limit, maintenance_window, snapshot_window, acl_name, auto_minor_version_upgrade, data_tiering from aws_memorydb_cluster where region = '$REGION'" "database_memorydb_clusters.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    execute_steampipe_query "DAX 클러스터" "select cluster_name, description, arn, total_nodes, active_nodes, node_type, status, cluster_discovery_endpoint, node_ids_to_remove, nodes, preferred_maintenance_window, notification_configuration, subnet_group, security_groups, iam_role_arn, parameter_group, sse_description, cluster_endpoint_encryption_type, tags from aws_dax_cluster where region = '$REGION'" "database_dax_clusters.json"
    ((total_count++))
    [ $? -eq 0 ] && ((success_count++))
    
    # 결과 요약
    log_success "데이터베이스 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    log_info "🎉 데이터베이스 리소스 데이터 수집이 완료되었습니다!"
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
