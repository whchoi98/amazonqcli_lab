#!/bin/bash
# Steampipe 기반 컨테이너 서비스 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_container_collection.log"
ERROR_LOG="steampipe_container_errors.log"

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

log_container() {
    echo -e "${PURPLE}[CONTAINER]${NC} $1" | tee -a "$LOG_FILE"
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

# 컨테이너 서비스 상태 확인 함수
check_container_services() {
    log_info "컨테이너 서비스 상태 확인 중..."
    
    # ECS 클러스터 존재 확인
    local ecs_clusters=$(aws ecs list-clusters --region "$REGION" --query 'clusterArns | length(@)' --output text 2>/dev/null || echo "0")
    log_info "ECS 클러스터 개수: $ecs_clusters"
    
    # EKS 클러스터 존재 확인
    local eks_clusters=$(aws eks list-clusters --region "$REGION" --query 'clusters | length(@)' --output text 2>/dev/null || echo "0")
    log_info "EKS 클러스터 개수: $eks_clusters"
    
    # ECR 리포지토리 존재 확인
    local ecr_repos=$(aws ecr describe-repositories --region "$REGION" --query 'repositories | length(@)' --output text 2>/dev/null || echo "0")
    log_info "ECR 리포지토리 개수: $ecr_repos"
    
    if [ "$ecs_clusters" -eq 0 ] && [ "$eks_clusters" -eq 0 ] && [ "$ecr_repos" -eq 0 ]; then
        log_warning "컨테이너 서비스가 발견되지 않았습니다. 데이터 수집을 계속 진행합니다."
    fi
}

# 메인 실행부
main() {
    log_container "🐳 Steampipe 기반 컨테이너 서비스 리소스 데이터 수집 시작"
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
    
    # 컨테이너 서비스 상태 확인
    check_container_services
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_container "🐳 컨테이너 서비스 수집 시작..."
    
    # 컨테이너 서비스 수집 배열
    declare -a container_queries=(
        # ECS 관련 쿼리
        "ECS 클러스터 상세 정보|select cluster_name, cluster_arn, status, running_tasks_count, pending_tasks_count, active_services_count, registered_container_instances_count, capacity_providers, default_capacity_provider_strategy, settings, tags from aws_ecs_cluster where region = '$REGION'|compute_ecs_clusters.json"
        "ECS 서비스|select service_name, arn, cluster_arn, task_definition, desired_count, running_count, pending_count, status, launch_type, platform_version, load_balancers, service_registries, network_configuration, capacity_provider_strategy, deployment_configuration, scheduling_strategy, tags from aws_ecs_service where region = '$REGION'|compute_ecs_services.json"
        "ECS 태스크 정의|select task_definition_arn, family, revision, status, task_role_arn, execution_role_arn, network_mode, requires_compatibilities, cpu, memory, container_definitions, volumes, placement_constraints, tags from aws_ecs_task_definition where region = '$REGION' and status = 'ACTIVE'|compute_ecs_task_definitions.json"
        "ECS 컨테이너 인스턴스|select arn, ec2_instance_id, cluster_arn, status, agent_connected, running_tasks_count, pending_tasks_count, version, attributes, registered_resources, remaining_resources, capacity_provider_name, tags from aws_ecs_container_instance where region = '$REGION'|compute_ecs_container_instances.json"
        "ECS 실행 중인 태스크|select task_arn, cluster_arn, task_definition_arn, container_instance_arn, last_status, desired_status, health_status, launch_type, platform_version, cpu, memory, connectivity, created_at, started_at, \"group\", capacity_provider_name, tags from aws_ecs_task where region = '$REGION'|compute_ecs_tasks.json"
        "Fargate 태스크 (ECS)|select task_arn, cluster_arn, task_definition_arn, last_status, desired_status, launch_type, platform_version, cpu, memory, connectivity, created_at, started_at, \"group\", tags from aws_ecs_task where region = '$REGION' and launch_type = 'FARGATE'|compute_fargate_tasks.json"
        
        # EKS 관련 쿼리
        "EKS 클러스터 상세 정보|select name, arn, version, status, endpoint, platform_version, role_arn, resources_vpc_config, kubernetes_network_config, logging, identity, certificate_authority, created_at, encryption_config, tags from aws_eks_cluster where region = '$REGION'|compute_eks_clusters.json"
        "EKS 노드 그룹|select nodegroup_name, cluster_name, arn, status, capacity_type, scaling_config, instance_types, subnets, remote_access, ami_type, node_role, labels, taints, resources, disk_size, health, update_config, launch_template, version, release_version, created_at, modified_at, tags from aws_eks_node_group where region = '$REGION'|compute_eks_node_groups.json"
        "EKS Fargate 프로필|select fargate_profile_name, cluster_name, fargate_profile_arn, status, pod_execution_role_arn, subnets, selectors, created_at, tags from aws_eks_fargate_profile where region = '$REGION'|compute_eks_fargate_profiles.json"
        "EKS 애드온|select addon_name, cluster_name, arn, addon_version, status, service_account_role_arn, configuration_values, created_at, modified_at, health_issues, marketplace_information, publisher, owner, tags from aws_eks_addon where region = '$REGION'|compute_eks_addons.json"
        
        # ECR 관련 쿼리
        "ECR 리포지토리|select repository_name, arn, registry_id, repository_uri, created_at, image_tag_mutability, image_scanning_configuration, encryption_configuration, lifecycle_policy, policy, tags from aws_ecr_repository where region = '$REGION'|compute_ecr_repositories.json"
        "ECR 이미지 (최근 100개)|select registry_id, repository_name, image_digest, image_tags, image_size_in_bytes, image_pushed_at, image_scan_status, image_scan_findings_summary, artifact_media_type from aws_ecr_image where region = '$REGION' order by image_pushed_at desc limit 100|compute_ecr_images.json"
    )
    
    # 컨테이너 서비스 쿼리 실행
    for query_info in "${container_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
        
        # 진행률 표시
        local progress=$((success_count * 100 / total_count))
        echo -ne "\r${CYAN}진행률: ${progress}% (${success_count}/${total_count})${NC}"
    done
    
    echo "" # 새 줄
    
    # 결과 요약
    log_success "컨테이너 서비스 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    
    # ECS 파일들
    echo -e "${PURPLE}🐳 ECS 관련 파일:${NC}"
    for file in compute_ecs_*.json compute_fargate_*.json; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            if [ "$size" -gt 100 ]; then
                echo -e "${GREEN}  ✓ $file (${size} bytes)${NC}"
            else
                echo -e "${YELLOW}  ⚠ $file (${size} bytes) - 데이터 없음${NC}"
            fi
        fi
    done
    
    # EKS 파일들
    echo -e "${PURPLE}☸️  EKS 관련 파일:${NC}"
    for file in compute_eks_*.json; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            if [ "$size" -gt 100 ]; then
                echo -e "${GREEN}  ✓ $file (${size} bytes)${NC}"
            else
                echo -e "${YELLOW}  ⚠ $file (${size} bytes) - 데이터 없음${NC}"
            fi
        fi
    done
    
    # ECR 파일들
    echo -e "${PURPLE}📦 ECR 관련 파일:${NC}"
    for file in compute_ecr_*.json; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            if [ "$size" -gt 100 ]; then
                echo -e "${GREEN}  ✓ $file (${size} bytes)${NC}"
            else
                echo -e "${YELLOW}  ⚠ $file (${size} bytes) - 데이터 없음${NC}"
            fi
        fi
    done
    
    # 수집 통계
    echo -e "\n${BLUE}📊 수집 통계:${NC}"
    echo "총 쿼리 수: $total_count"
    echo "성공한 쿼리: $success_count"
    echo "실패한 쿼리: $((total_count - success_count))"
    
    # 서비스별 통계
    local ecs_files=$(ls compute_ecs_*.json compute_fargate_*.json 2>/dev/null | wc -l)
    local eks_files=$(ls compute_eks_*.json 2>/dev/null | wc -l)
    local ecr_files=$(ls compute_ecr_*.json 2>/dev/null | wc -l)
    
    echo -e "\n${PURPLE}서비스별 파일 수:${NC}"
    echo "ECS 관련: $ecs_files 개"
    echo "EKS 관련: $eks_files 개"
    echo "ECR 관련: $ecr_files 개"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 컨테이너 서비스 요약 정보 생성
    generate_container_summary
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 컨테이너 데이터를 바탕으로 Phase 1 인프라 분석 진행"
    echo "2. ECS/EKS 클러스터 리소스 사용률 및 비용 분석"
    echo "3. 컨테이너 보안 설정 및 네트워크 구성 검토"
    echo "4. ECR 이미지 취약점 스캔 결과 분석"
    echo "5. Fargate vs EC2 비용 효율성 분석"
    
    log_container "🎉 컨테이너 서비스 리소스 데이터 수집이 완료되었습니다!"
}

# 컨테이너 서비스 요약 정보 생성 함수
generate_container_summary() {
    local summary_file="container_services_summary.json"
    log_info "컨테이너 서비스 요약 정보 생성 중..."
    
    cat > "$summary_file" << EOF
{
  "collection_info": {
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "region": "$REGION",
    "total_queries": $total_count,
    "successful_queries": $success_count,
    "failed_queries": $((total_count - success_count))
  },
  "services": {
    "ecs": {
      "clusters": "$([ -f compute_ecs_clusters.json ] && jq '. | length' compute_ecs_clusters.json 2>/dev/null || echo 0)",
      "services": "$([ -f compute_ecs_services.json ] && jq '. | length' compute_ecs_services.json 2>/dev/null || echo 0)",
      "tasks": "$([ -f compute_ecs_tasks.json ] && jq '. | length' compute_ecs_tasks.json 2>/dev/null || echo 0)",
      "fargate_tasks": "$([ -f compute_fargate_tasks.json ] && jq '. | length' compute_fargate_tasks.json 2>/dev/null || echo 0)"
    },
    "eks": {
      "clusters": "$([ -f compute_eks_clusters.json ] && jq '. | length' compute_eks_clusters.json 2>/dev/null || echo 0)",
      "node_groups": "$([ -f compute_eks_node_groups.json ] && jq '. | length' compute_eks_node_groups.json 2>/dev/null || echo 0)",
      "fargate_profiles": "$([ -f compute_eks_fargate_profiles.json ] && jq '. | length' compute_eks_fargate_profiles.json 2>/dev/null || echo 0)",
      "addons": "$([ -f compute_eks_addons.json ] && jq '. | length' compute_eks_addons.json 2>/dev/null || echo 0)"
    },
    "ecr": {
      "repositories": "$([ -f compute_ecr_repositories.json ] && jq '. | length' compute_ecr_repositories.json 2>/dev/null || echo 0)",
      "images": "$([ -f compute_ecr_images.json ] && jq '. | length' compute_ecr_images.json 2>/dev/null || echo 0)"
    }
  }
}
EOF
    
    if [ -f "$summary_file" ]; then
        log_success "컨테이너 서비스 요약 정보 생성 완료: $summary_file"
    fi
}

# 도움말 함수
show_help() {
    echo -e "${CYAN}🐳 Steampipe 컨테이너 서비스 데이터 수집 스크립트${NC}"
    echo ""
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
    echo "수집되는 컨테이너 서비스:"
    echo "  🐳 ECS: 클러스터, 서비스, 태스크, 컨테이너 인스턴스"
    echo "  ☸️  EKS: 클러스터, 노드 그룹, Fargate 프로필, 애드온"
    echo "  📦 ECR: 리포지토리, 이미지"
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
            echo -e "${RED}알 수 없는 옵션: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 스크립트 실행
main "$@"
