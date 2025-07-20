#!/bin/bash
# Steampipe 기반 컨테이너 서비스 리소스 데이터 수집 스크립트 (Kubernetes 포함)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
# 스크립트의 실제 위치를 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORT_DIR="${REPORT_DIR:-${PROJECT_ROOT}/aws-arch-analysis/report}"
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

log_k8s() {
    echo -e "${CYAN}[K8S]${NC} $1" | tee -a "$LOG_FILE"
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

# 컨테이너 서비스 존재 확인 함수
check_container_services() {
    log_container "컨테이너 서비스 존재 확인 중..."
    
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
    
    # Kubernetes 연결 확인
    if [ "$eks_clusters" -gt 0 ]; then
        log_k8s "EKS 클러스터가 발견되었습니다. Kubernetes 리소스 수집을 시도합니다."
    fi
}

# 메인 함수
main() {
    log_container "🚀 Steampipe 기반 컨테이너 서비스 리소스 데이터 수집 시작 (Kubernetes 포함)"
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
        echo "steampipe plugin install aws kubernetes"
        exit 1
    fi
    
    # AWS 플러그인 확인
    log_info "Steampipe AWS 플러그인 확인 중..."
    if ! steampipe plugin list | grep -q "aws"; then
        log_warning "AWS 플러그인이 설치되지 않았습니다. 설치 중..."
        steampipe plugin install aws
    fi
    
    # Kubernetes 플러그인 확인
    log_info "Steampipe Kubernetes 플러그인 확인 중..."
    if ! steampipe plugin list | grep -q "kubernetes"; then
        log_warning "Kubernetes 플러그인이 설치되지 않았습니다. 설치 중..."
        steampipe plugin install kubernetes
    fi
    
    # 컨테이너 서비스 존재 확인
    check_container_services
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_container "🐳 컨테이너 서비스 리소스 수집 시작..."
    
    # 컨테이너 서비스 수집 배열
    declare -a queries=(
        # ECS 관련 쿼리
        "ECS 클러스터 상세 정보|select cluster_name, cluster_arn, status, running_tasks_count, pending_tasks_count, active_services_count, statistics, registered_container_instances_count, capacity_providers, default_capacity_provider_strategy, attachments, attachments_status, configuration, service_connect_defaults, tags from aws_ecs_cluster where region = '$REGION'|compute_ecs_clusters.json"
        "ECS 서비스|select service_name, service_arn, cluster_arn, task_definition, desired_count, running_count, pending_count, status, task_sets, deployment_controller, deployments, role_arn, events, created_at, placement_constraints, placement_strategy, platform_version, platform_family, capacity_provider_strategy, service_registries, network_configuration, health_check_grace_period_seconds, scheduling_strategy, deployment_configuration, service_connect_configuration, volume_configurations, tags from aws_ecs_service where region = '$REGION'|compute_ecs_services.json"
        "ECS 태스크 정의|select task_definition_arn, family, task_role_arn, execution_role_arn, network_mode, revision, volumes, status, requires_attributes, placement_constraints, compatibilities, runtime_platform, requires_compatibilities, cpu, memory, inference_accelerators, pid_mode, ipc_mode, proxy_configuration, registered_at, deregistered_at, registered_by, ephemeral_storage, tags from aws_ecs_task_definition where region = '$REGION'|compute_ecs_task_definitions.json"
        "ECS 컨테이너 인스턴스|select container_instance_arn, ec2_instance_id, capacity_provider_name, version, version_info, remaining_resources, registered_resources, status, status_reason, agent_connected, running_tasks_count, pending_tasks_count, agent_update_status, attributes, registered_at, attachments, health_status, tags from aws_ecs_container_instance where region = '$REGION'|compute_ecs_container_instances.json"
        "ECS 태스크|select task_arn, cluster_arn, task_definition_arn, container_instance_arn, overrides, last_status, desired_status, health_status, connectivity, connectivity_at, pull_started_at, pull_stopped_at, execution_stopped_at, created_at, started_at, starting_at, stopped_at, stopped_reason, stopping_at, platform_version, platform_family, cpu, memory, inference_accelerators, ephemeral_storage, launch_type, capacity_provider_name, availability_zone, \\\"group\\\", attachments, attributes, tags from aws_ecs_task where region = '$REGION'|compute_ecs_tasks.json"
        "Fargate 태스크 (ECS)|select task_arn, cluster_arn, task_definition_arn, last_status, desired_status, launch_type, platform_version, cpu, memory, connectivity, created_at, started_at, \\\"group\\\", tags from aws_ecs_task where region = '$REGION' and launch_type = 'FARGATE'|compute_fargate_tasks.json"
        
        # EKS 관련 쿼리 (기존 + 추가)
        "EKS 클러스터 상세 정보|select name, arn, version, status, endpoint, platform_version, role_arn, resources_vpc_config, kubernetes_network_config, logging, identity, certificate_authority, created_at, encryption_config, tags from aws_eks_cluster where region = '$REGION'|compute_eks_clusters.json"
        "EKS 노드 그룹|select nodegroup_name, cluster_name, arn, status, capacity_type, scaling_config, instance_types, subnets, remote_access, ami_type, node_role, labels, taints, resources, disk_size, health, update_config, launch_template, version, release_version, created_at, modified_at, tags from aws_eks_node_group where region = '$REGION'|compute_eks_node_groups.json"
        "EKS Fargate 프로필|select fargate_profile_name, cluster_name, fargate_profile_arn, status, pod_execution_role_arn, subnets, selectors, created_at, tags from aws_eks_fargate_profile where region = '$REGION'|compute_eks_fargate_profiles.json"
        "EKS 애드온|select addon_name, cluster_name, arn, addon_version, status, service_account_role_arn, configuration_values, created_at, modified_at, health_issues, marketplace_information, publisher, owner, tags from aws_eks_addon where region = '$REGION'|compute_eks_addons.json"
        "EKS Identity Provider 구성|select name, type, cluster_name, arn, status, client_id, groups_claim, groups_prefix, issuer_url, username_claim, username_prefix, required_claims, tags from aws_eks_identity_provider_config where region = '$REGION'|compute_eks_identity_providers.json"
        
        # ECR 관련 쿼리
        "ECR 리포지토리|select repository_name, repository_arn, registry_id, repository_uri, created_at, image_tag_mutability, image_scanning_configuration, lifecycle_policy, encryption_configuration, tags from aws_ecr_repository where region = '$REGION'|compute_ecr_repositories.json"
        "ECR 이미지|select repository_name, registry_id, image_digest, image_tags, image_size_in_bytes, image_pushed_at, image_scan_completed_at, image_scan_findings_summary, artifact_media_type, image_manifest_media_type from aws_ecr_image where region = '$REGION'|compute_ecr_images.json"
        
        # 추가 컨테이너 관련 쿼리
        "ECS 용량 공급자|select name, arn, status, auto_scaling_group_provider, update_status, update_status_reason, tags from aws_ecs_capacity_provider where region = '$REGION'|compute_ecs_capacity_providers.json"
        "ECR 스캔 결과|select repository_name, registry_id, image_digest, image_tags, vulnerability_source_updated_at, finding_counts, enhanced_findings from aws_ecr_image_scan_finding where region = '$REGION'|compute_ecr_scan_findings.json"
    )
    
    # Kubernetes 리소스 쿼리 추가
    declare -a k8s_queries=(
        # Kubernetes 네임스페이스
        "K8s 네임스페이스|select name, uid, phase, conditions, spec_finalizers, labels, annotations, creation_timestamp from kubernetes_namespace|k8s_namespaces.json"
        
        # Kubernetes 파드
        "K8s 파드|select name, namespace, uid, phase, node_name, pod_ip, host_ip, qos_class, restart_policy, service_account_name, containers, init_containers, volumes, conditions, creation_timestamp, labels, annotations from kubernetes_pod|k8s_pods.json"
        
        # Kubernetes 서비스
        "K8s 서비스|select name, namespace, uid, type, cluster_ip, external_ips, load_balancer_ip, ports, selector, session_affinity, external_traffic_policy, health_check_node_port, publish_not_ready_addresses, ip_families, ip_family_policy, allocate_load_balancer_node_ports, load_balancer_class, internal_traffic_policy, creation_timestamp, labels, annotations from kubernetes_service|k8s_services.json"
        
        # Kubernetes 디플로이먼트
        "K8s 디플로이먼트|select name, namespace, uid, replicas, updated_replicas, ready_replicas, available_replicas, unavailable_replicas, observed_generation, conditions, strategy, min_ready_seconds, progress_deadline_seconds, revision_history_limit, paused, creation_timestamp, labels, annotations from kubernetes_deployment|k8s_deployments.json"
        
        # Kubernetes 노드
        "K8s 노드|select name, uid, pod_cidr, pod_cidrs, provider_id, unschedulable, taints, allocatable, capacity, conditions, addresses, node_info, images, volumes_in_use, volumes_attached, config, creation_timestamp, labels, annotations from kubernetes_node|k8s_nodes.json"
        
        # Kubernetes 이벤트
        "K8s 이벤트|select name, namespace, uid, type, reason, message, source, involved_object, first_timestamp, last_timestamp, count, event_time, series, action, related, reporting_component, reporting_instance, creation_timestamp from kubernetes_event|k8s_events.json"
        
        # Kubernetes ConfigMap
        "K8s ConfigMap|select name, namespace, uid, data, binary_data, immutable, creation_timestamp, labels, annotations from kubernetes_config_map|k8s_configmaps.json"
        
        # Kubernetes Secret
        "K8s Secret|select name, namespace, uid, type, data, string_data, immutable, creation_timestamp, labels, annotations from kubernetes_secret|k8s_secrets.json"
        
        # Kubernetes Ingress
        "K8s Ingress|select name, namespace, uid, ingress_class_name, rules, tls, load_balancer, creation_timestamp, labels, annotations from kubernetes_ingress|k8s_ingress.json"
        
        # Kubernetes PersistentVolume
        "K8s PersistentVolume|select name, uid, capacity, access_modes, reclaim_policy, storage_class, volume_mode, persistent_volume_source, claim_ref, phase, reason, message, mount_options, volume_attributes_class, node_affinity, creation_timestamp, labels, annotations from kubernetes_persistent_volume|k8s_persistent_volumes.json"
        
        # Kubernetes PersistentVolumeClaim
        "K8s PersistentVolumeClaim|select name, namespace, uid, access_modes, resources, selector, storage_class, volume_mode, volume_name, phase, conditions, allocated_resources, capacity, resize_status, allocated_resource_statuses, creation_timestamp, labels, annotations from kubernetes_persistent_volume_claim|k8s_persistent_volume_claims.json"
    )
    
    # AWS 쿼리 실행
    for query_info in "${queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # Kubernetes 쿼리 실행
    log_k8s "☸️  Kubernetes 리소스 수집 시작..."
    for query_info in "${k8s_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "컨테이너 서비스 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in compute_*.json k8s_*.json; do
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
    
    # 서비스별 통계
    local ecs_files=$(ls compute_ecs_*.json compute_fargate_*.json 2>/dev/null | wc -l)
    local eks_files=$(ls compute_eks_*.json 2>/dev/null | wc -l)
    local ecr_files=$(ls compute_ecr_*.json 2>/dev/null | wc -l)
    local k8s_files=$(ls k8s_*.json 2>/dev/null | wc -l)
    
    echo -e "\n${PURPLE}서비스별 파일 수:${NC}"
    echo "ECS 관련: $ecs_files 개"
    echo "EKS 관련: $eks_files 개"
    echo "ECR 관련: $ecr_files 개"
    echo "Kubernetes 관련: $k8s_files 개"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 컨테이너 데이터를 바탕으로 Phase 1 인프라 분석 진행"
    echo "2. ECS/EKS 클러스터 리소스 사용률 및 비용 분석"
    echo "3. 컨테이너 보안 설정 및 네트워크 구성 검토"
    echo "4. ECR 이미지 취약점 스캔 결과 분석"
    echo "5. EKS 애드온 버전 및 Identity Provider 구성 검토"
    echo "6. Kubernetes 리소스 최적화 및 보안 정책 검토"
    
    # 컨테이너 서비스 요약 JSON 생성
    cat > container_services_summary.json << EOF
{
  "collection_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "region": "$REGION",
  "summary": {
    "total_queries": $total_count,
    "successful_queries": $success_count,
    "failed_queries": $((total_count - success_count))
  },
  "services": {
    "ecs": {
      "clusters": "$([ -f compute_ecs_clusters.json ] && jq '.rows | length' compute_ecs_clusters.json 2>/dev/null || echo 0)",
      "services": "$([ -f compute_ecs_services.json ] && jq '.rows | length' compute_ecs_services.json 2>/dev/null || echo 0)",
      "task_definitions": "$([ -f compute_ecs_task_definitions.json ] && jq '.rows | length' compute_ecs_task_definitions.json 2>/dev/null || echo 0)",
      "tasks": "$([ -f compute_ecs_tasks.json ] && jq '.rows | length' compute_ecs_tasks.json 2>/dev/null || echo 0)",
      "container_instances": "$([ -f compute_ecs_container_instances.json ] && jq '.rows | length' compute_ecs_container_instances.json 2>/dev/null || echo 0)",
      "fargate_tasks": "$([ -f compute_fargate_tasks.json ] && jq '.rows | length' compute_fargate_tasks.json 2>/dev/null || echo 0)",
      "capacity_providers": "$([ -f compute_ecs_capacity_providers.json ] && jq '.rows | length' compute_ecs_capacity_providers.json 2>/dev/null || echo 0)"
    },
    "eks": {
      "clusters": "$([ -f compute_eks_clusters.json ] && jq '.rows | length' compute_eks_clusters.json 2>/dev/null || echo 0)",
      "node_groups": "$([ -f compute_eks_node_groups.json ] && jq '.rows | length' compute_eks_node_groups.json 2>/dev/null || echo 0)",
      "fargate_profiles": "$([ -f compute_eks_fargate_profiles.json ] && jq '.rows | length' compute_eks_fargate_profiles.json 2>/dev/null || echo 0)",
      "addons": "$([ -f compute_eks_addons.json ] && jq '.rows | length' compute_eks_addons.json 2>/dev/null || echo 0)",
      "addon_versions": "$([ -f compute_eks_addon_versions.json ] && jq '.rows | length' compute_eks_addon_versions.json 2>/dev/null || echo 0)",
      "identity_providers": "$([ -f compute_eks_identity_providers.json ] && jq '.rows | length' compute_eks_identity_providers.json 2>/dev/null || echo 0)"
    },
    "ecr": {
      "repositories": "$([ -f compute_ecr_repositories.json ] && jq '.rows | length' compute_ecr_repositories.json 2>/dev/null || echo 0)",
      "images": "$([ -f compute_ecr_images.json ] && jq '.rows | length' compute_ecr_images.json 2>/dev/null || echo 0)",
      "scan_findings": "$([ -f compute_ecr_scan_findings.json ] && jq '.rows | length' compute_ecr_scan_findings.json 2>/dev/null || echo 0)"
    },
    "kubernetes": {
      "namespaces": "$([ -f k8s_namespaces.json ] && jq '.rows | length' k8s_namespaces.json 2>/dev/null || echo 0)",
      "pods": "$([ -f k8s_pods.json ] && jq '.rows | length' k8s_pods.json 2>/dev/null || echo 0)",
      "services": "$([ -f k8s_services.json ] && jq '.rows | length' k8s_services.json 2>/dev/null || echo 0)",
      "deployments": "$([ -f k8s_deployments.json ] && jq '.rows | length' k8s_deployments.json 2>/dev/null || echo 0)",
      "nodes": "$([ -f k8s_nodes.json ] && jq '.rows | length' k8s_nodes.json 2>/dev/null || echo 0)",
      "events": "$([ -f k8s_events.json ] && jq '.rows | length' k8s_events.json 2>/dev/null || echo 0)",
      "configmaps": "$([ -f k8s_configmaps.json ] && jq '.rows | length' k8s_configmaps.json 2>/dev/null || echo 0)",
      "secrets": "$([ -f k8s_secrets.json ] && jq '.rows | length' k8s_secrets.json 2>/dev/null || echo 0)",
      "ingress": "$([ -f k8s_ingress.json ] && jq '.rows | length' k8s_ingress.json 2>/dev/null || echo 0)",
      "persistent_volumes": "$([ -f k8s_persistent_volumes.json ] && jq '.rows | length' k8s_persistent_volumes.json 2>/dev/null || echo 0)",
      "persistent_volume_claims": "$([ -f k8s_persistent_volume_claims.json ] && jq '.rows | length' k8s_persistent_volume_claims.json 2>/dev/null || echo 0)"
    }
  }
}
EOF
    
    log_success "컨테이너 서비스 요약 JSON 생성 완료 (container_services_summary.json)"
    
    # 사용 가이드 출력
    echo -e "\n${CYAN}📖 사용 가이드:${NC}"
    echo "수집되는 컨테이너 서비스:"
    echo "  🐳 ECS: 클러스터, 서비스, 태스크, 컨테이너 인스턴스, 용량 공급자"
    echo "  ☸️  EKS: 클러스터, 노드 그룹, Fargate 프로필, 애드온, 애드온 버전, Identity Provider"
    echo "  📦 ECR: 리포지토리, 이미지, 스캔 결과"
    echo "  🎯 K8s: 네임스페이스, 파드, 서비스, 디플로이먼트, 노드, 이벤트, ConfigMap, Secret, Ingress, PV/PVC"
    echo ""
    echo "주요 개선사항:"
    echo "  ✨ EKS 애드온 버전 정보 수집"
    echo "  🔐 EKS Identity Provider 구성 수집"
    echo "  🛡️  ECR 이미지 스캔 결과 수집"
    echo "  📊 ECS 용량 공급자 정보 수집"
    echo "  ☸️  Kubernetes 리소스 완전 수집 (11개 리소스 타입)"
    
    log_container "🎉 컨테이너 서비스 리소스 데이터 수집이 완료되었습니다!"
}

# 스크립트 실행
main "$@"
