#!/bin/bash
# 완전한 데이터베이스 리소스 데이터 수집 스크립트 (RDS, NoSQL, 분석 서비스 포함)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report}"
LOG_FILE="steampipe_database_collection.log"
ERROR_LOG="steampipe_database_errors.log"

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

log_rds() {
    echo -e "${PURPLE}[RDS]${NC} $1" | tee -a "$LOG_FILE"
}

log_nosql() {
    echo -e "${CYAN}[NoSQL]${NC} $1" | tee -a "$LOG_FILE"
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
    log_info "🗄️ 완전한 데이터베이스 리소스 데이터 수집 시작 (RDS, NoSQL, 분석 서비스 포함)"
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
    
    log_rds "🏛️ RDS 인스턴스 및 클러스터 수집 시작..."
    
    # RDS 기본 리소스 수집 배열
    declare -a rds_queries=(
        "RDS DB 인스턴스|select db_instance_identifier, db_instance_class, engine, engine_version, db_instance_status, allocated_storage, storage_type, storage_encrypted, multi_az, publicly_accessible, vpc_security_groups, db_subnet_group_name, backup_retention_period, preferred_backup_window, preferred_maintenance_window, auto_minor_version_upgrade, deletion_protection, tags from aws_rds_db_instance where region = '$REGION'|database_rds_instances.json"
        "RDS DB 클러스터|select db_cluster_identifier, engine, engine_version, database_name, db_cluster_members, vpc_security_groups, db_subnet_group_name, backup_retention_period, preferred_backup_window, preferred_maintenance_window, multi_az, storage_encrypted, kms_key_id, endpoint, reader_endpoint, status, deletion_protection, tags from aws_rds_db_cluster where region = '$REGION'|database_rds_clusters.json"
        "RDS 서브넷 그룹|select db_subnet_group_name, db_subnet_group_description, vpc_id, subnet_group_status, subnets, tags from aws_rds_db_subnet_group where region = '$REGION'|database_rds_subnet_groups.json"
        "RDS 파라미터 그룹|select db_parameter_group_name, db_parameter_group_family, description, tags from aws_rds_db_parameter_group where region = '$REGION'|database_rds_parameter_groups.json"
        "RDS 스냅샷|select db_snapshot_identifier, db_instance_identifier, snapshot_create_time, engine, allocated_storage, status, encrypted, kms_key_id, tags from aws_rds_db_snapshot where region = '$REGION'|database_rds_snapshots.json"
    )
    
    # RDS 쿼리 실행
    for query_info in "${rds_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_nosql "🔥 DynamoDB 리소스 수집 시작..."
    
    # DynamoDB 관련 리소스 수집 배열
    declare -a dynamodb_queries=(
        "DynamoDB 테이블|select name, table_status, creation_date_time, billing_mode_summary, provisioned_throughput, global_secondary_indexes, stream_specification, deletion_protection_enabled, tags from aws_dynamodb_table where region = '$REGION'|database_dynamodb_tables.json"
        "DynamoDB 백업|select backup_name, backup_status, backup_type, backup_creation_date_time, table_name, backup_size_bytes from aws_dynamodb_backup where region = '$REGION'|database_dynamodb_backups.json"
    )
    
    # DynamoDB 쿼리 실행
    for query_info in "${dynamodb_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_nosql "⚡ ElastiCache 리소스 수집 시작..."
    
    # ElastiCache 관련 리소스 수집 배열
    declare -a elasticache_queries=(
        "ElastiCache 클러스터|select cache_cluster_id, cache_node_type, engine, engine_version, cache_cluster_status, num_cache_nodes, preferred_availability_zone, cache_cluster_create_time, preferred_maintenance_window, auto_minor_version_upgrade, security_groups, replication_group_id from aws_elasticache_cluster where region = '$REGION'|database_elasticache_clusters.json"
        "ElastiCache 복제 그룹|select replication_group_id, description, status, member_clusters, automatic_failover, multi_az, cache_node_type, auth_token_enabled, transit_encryption_enabled, at_rest_encryption_enabled from aws_elasticache_replication_group where region = '$REGION'|database_elasticache_replication_groups.json"
    )
    
    # ElastiCache 쿼리 실행
    for query_info in "${elasticache_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "🏢 데이터 웨어하우스 서비스 수집 시작..."
    
    # 데이터 웨어하우스 관련 리소스 수집 배열
    declare -a warehouse_queries=(
        "Redshift 클러스터|select cluster_identifier, node_type, cluster_status, master_username, db_name, endpoint, cluster_create_time, number_of_nodes, publicly_accessible, encrypted, vpc_id, tags from aws_redshift_cluster where region = '$REGION'|database_redshift_clusters.json"
        "OpenSearch 도메인|select domain_name, elasticsearch_version, endpoint, processing, created, deleted, elasticsearch_cluster_config, ebs_options, vpc_options, encryption_at_rest_options, tags from aws_opensearch_domain where region = '$REGION'|database_opensearch_domains.json"
    )
    
    # 데이터 웨어하우스 쿼리 실행
    for query_info in "${warehouse_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "🚀 빅데이터 처리 서비스 수집 시작..."
    
    # 빅데이터 처리 관련 리소스 수집 배열
    declare -a bigdata_queries=(
        "EMR 클러스터|select id, name, status, ec2_instance_attributes, log_uri, release_label, auto_terminate, termination_protected, applications, service_role, tags from aws_emr_cluster where region = '$REGION'|database_emr_clusters.json"
        "Kinesis 스트림|select name, status, retention_period, shard_count, stream_creation_timestamp, tags from aws_kinesis_stream where region = '$REGION'|database_kinesis_streams.json"
        "Glue 데이터베이스|select name, description, location_uri, create_time from aws_glue_catalog_database where region = '$REGION'|database_glue_databases.json"
        "Athena 워크그룹|select name, description, state, configuration, creation_time, tags from aws_athena_workgroup where region = '$REGION'|database_athena_workgroups.json"
    )
    
    # 빅데이터 처리 쿼리 실행
    for query_info in "${bigdata_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "완전한 데이터베이스 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in database_*.json; do
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
    echo "🏛️  RDS 리소스: 5개"
    echo "🔥 DynamoDB: 2개"
    echo "⚡ ElastiCache: 2개"
    echo "🏢 데이터 웨어하우스: 2개"
    echo "🚀 빅데이터 처리: 4개"
    echo "📊 총 리소스 타입: 15개"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 완전한 데이터베이스 데이터를 바탕으로 상세 분석 진행"
    echo "2. RDS 인스턴스 성능 및 비용 최적화 분석"
    echo "3. DynamoDB 테이블 구성 및 성능 검토"
    echo "4. ElastiCache 클러스터 최적화 분석"
    echo "5. 데이터 웨어하우스 및 분석 서비스 활용도 분석"
    echo "6. 빅데이터 처리 파이프라인 최적화"
    echo "7. 데이터베이스 백업 및 보안 설정 종합 검토"
    
    log_info "🎉 완전한 데이터베이스 리소스 데이터 수집이 완료되었습니다!"
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
