#!/usr/bin/env python3
"""
AWS 컨테이너 서비스 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeContainerCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        self.report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "container_collection_errors.log"
        
        # 색상 코드
        self.GREEN = '\033[0;32m'
        self.BLUE = '\033[0;34m'
        self.YELLOW = '\033[1;33m'
        self.RED = '\033[0;31m'
        self.PURPLE = '\033[0;35m'
        self.NC = '\033[0m'  # No Color
        
    def log_info(self, message: str):
        print(f"{self.BLUE}ℹ️ {message}{self.NC}")
        
    def log_success(self, message: str):
        print(f"{self.GREEN}✅ {message}{self.NC}")
        
    def log_warning(self, message: str):
        print(f"{self.YELLOW}⚠️ {message}{self.NC}")
        
    def log_error(self, message: str):
        print(f"{self.RED}❌ {message}{self.NC}")
        
    def log_container(self, message: str):
        print(f"{self.PURPLE}🐳 {message}{self.NC}")
        
    def log_k8s(self, message: str):
        print(f"{self.BLUE}☸️ {message}{self.NC}")

    def check_steampipe_plugin(self):
        """Steampipe AWS 및 Kubernetes 플러그인 확인"""
        self.log_info("Steampipe AWS 플러그인 확인 중...")
        try:
            result = subprocess.run(
                ["steampipe", "plugin", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            if "aws" not in result.stdout:
                self.log_warning("AWS 플러그인이 설치되지 않았습니다. 설치 중...")
                subprocess.run(["steampipe", "plugin", "install", "aws"], check=True)
                
            if "kubernetes" not in result.stdout:
                self.log_warning("Kubernetes 플러그인이 설치되지 않았습니다. 설치 중...")
                subprocess.run(["steampipe", "plugin", "install", "kubernetes"], check=True)
        except subprocess.CalledProcessError:
            self.log_warning("Steampipe 플러그인 확인 중 오류 발생")

    def execute_steampipe_query(self, description: str, query: str, output_file: str) -> bool:
        self.log_info(f"수집 중: {description}")
        self.total_count += 1
        
        try:
            # 작업 디렉토리를 report_dir로 변경
            os.chdir(self.report_dir)
            
            result = subprocess.run(
                ["steampipe", "query", query, "--output", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            output_path = self.report_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            file_size = output_path.stat().st_size
            if file_size > 100:
                self.log_success(f"{description} 완료 ({output_file}, {file_size} bytes)")
                self.success_count += 1
                return True
            else:
                self.log_warning(f"{description} - 데이터 없음 ({output_file}, {file_size} bytes)")
                return False
                
        except subprocess.CalledProcessError as e:
            # 오류 메시지를 error_log에 기록
            error_msg = f"{description} 실패 - {output_file}"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            self.log_error(error_msg)
            
            # 오류 로그에 추가 정보 기록
            with open(self.error_log, 'a') as f:
                f.write(f"\nQuery failed: {query}\n")
                f.write(f"Error: {e.stderr}\n")
            
            return False

    def get_container_queries(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 쿼리 구조 사용"""
        return [
            # ECS 클러스터 상세 정보
            (
                "ECS 클러스터 상세 정보",
                f"select cluster_name, cluster_arn, status, running_tasks_count, pending_tasks_count, active_services_count, statistics, registered_container_instances_count, capacity_providers, default_capacity_provider_strategy, attachments, attachments_status, configuration, service_connect_defaults, tags from aws_ecs_cluster where region = '{self.region}'",
                "compute_ecs_clusters.json"
            ),
            
            # ECS 서비스
            (
                "ECS 서비스",
                f"select service_name, service_arn, cluster_arn, task_definition, desired_count, running_count, pending_count, status, task_sets, deployment_controller, deployments, role_arn, events, created_at, placement_constraints, placement_strategy, platform_version, platform_family, capacity_provider_strategy, service_registries, network_configuration, health_check_grace_period_seconds, scheduling_strategy, deployment_configuration, service_connect_configuration, volume_configurations, tags from aws_ecs_service where region = '{self.region}'",
                "compute_ecs_services.json"
            ),
            
            # ECS 태스크 정의
            (
                "ECS 태스크 정의",
                f"select task_definition_arn, family, task_role_arn, execution_role_arn, network_mode, revision, volumes, status, requires_attributes, placement_constraints, compatibilities, runtime_platform, requires_compatibilities, cpu, memory, inference_accelerators, pid_mode, ipc_mode, proxy_configuration, registered_at, deregistered_at, registered_by, ephemeral_storage, tags from aws_ecs_task_definition where region = '{self.region}'",
                "compute_ecs_task_definitions.json"
            ),
            
            # ECS 컨테이너 인스턴스
            (
                "ECS 컨테이너 인스턴스",
                f"select container_instance_arn, ec2_instance_id, capacity_provider_name, version, version_info, remaining_resources, registered_resources, status, status_reason, agent_connected, running_tasks_count, pending_tasks_count, agent_update_status, attributes, registered_at, attachments, health_status, tags from aws_ecs_container_instance where region = '{self.region}'",
                "compute_ecs_container_instances.json"
            ),
            
            # ECS 태스크
            (
                "ECS 태스크",
                f"select task_arn, cluster_arn, task_definition_arn, container_instance_arn, overrides, last_status, desired_status, health_status, connectivity, connectivity_at, pull_started_at, pull_stopped_at, execution_stopped_at, created_at, started_at, starting_at, stopped_at, stopped_reason, stopping_at, platform_version, platform_family, cpu, memory, inference_accelerators, ephemeral_storage, launch_type, capacity_provider_name, availability_zone, \"group\", attachments, attributes, tags from aws_ecs_task where region = '{self.region}'",
                "compute_ecs_tasks.json"
            ),
            
            # Fargate 태스크 (ECS)
            (
                "Fargate 태스크 (ECS)",
                f"select task_arn, cluster_arn, task_definition_arn, last_status, desired_status, launch_type, platform_version, cpu, memory, connectivity, created_at, started_at, \"group\", tags from aws_ecs_task where region = '{self.region}' and launch_type = 'FARGATE'",
                "compute_fargate_tasks.json"
            ),
            
            # EKS 클러스터 상세 정보
            (
                "EKS 클러스터 상세 정보",
                f"select name, arn, version, status, endpoint, platform_version, role_arn, resources_vpc_config, kubernetes_network_config, logging, identity, certificate_authority, created_at, encryption_config, tags from aws_eks_cluster where region = '{self.region}'",
                "compute_eks_clusters.json"
            ),
            
            # EKS 노드 그룹
            (
                "EKS 노드 그룹",
                f"select nodegroup_name, cluster_name, arn, status, capacity_type, scaling_config, instance_types, subnets, remote_access, ami_type, node_role, labels, taints, resources, disk_size, health, update_config, launch_template, version, release_version, created_at, modified_at, tags from aws_eks_node_group where region = '{self.region}'",
                "compute_eks_node_groups.json"
            ),
            
            # EKS Fargate 프로필
            (
                "EKS Fargate 프로필",
                f"select fargate_profile_name, cluster_name, fargate_profile_arn, status, pod_execution_role_arn, subnets, selectors, created_at, tags from aws_eks_fargate_profile where region = '{self.region}'",
                "compute_eks_fargate_profiles.json"
            ),
            
            # EKS 애드온
            (
                "EKS 애드온",
                f"select addon_name, cluster_name, arn, addon_version, status, service_account_role_arn, configuration_values, created_at, modified_at, health_issues, marketplace_information, publisher, owner, tags from aws_eks_addon where region = '{self.region}'",
                "compute_eks_addons.json"
            ),
            
            # EKS Identity Provider 구성
            (
                "EKS Identity Provider 구성",
                f"select name, type, cluster_name, arn, status, client_id, groups_claim, groups_prefix, issuer_url, username_claim, username_prefix, required_claims, tags from aws_eks_identity_provider_config where region = '{self.region}'",
                "compute_eks_identity_providers.json"
            ),
            
            # ECR 리포지토리
            (
                "ECR 리포지토리",
                f"select repository_name, repository_arn, registry_id, repository_uri, created_at, image_tag_mutability, image_scanning_configuration, lifecycle_policy, encryption_configuration, tags from aws_ecr_repository where region = '{self.region}'",
                "compute_ecr_repositories.json"
            ),
            
            # ECR 이미지
            (
                "ECR 이미지",
                f"select repository_name, registry_id, image_digest, image_tags, image_size_in_bytes, image_pushed_at, image_scan_completed_at, image_scan_findings_summary, artifact_media_type, image_manifest_media_type from aws_ecr_image where region = '{self.region}'",
                "compute_ecr_images.json"
            ),
            
            # ECS 용량 공급자
            (
                "ECS 용량 공급자",
                f"select name, arn, status, auto_scaling_group_provider, update_status, update_status_reason, tags from aws_ecs_capacity_provider where region = '{self.region}'",
                "compute_ecs_capacity_providers.json"
            ),
            
            # ECR 스캔 결과
            (
                "ECR 스캔 결과",
                f"select repository_name, registry_id, image_digest, image_tags, vulnerability_source_updated_at, finding_counts, enhanced_findings from aws_ecr_image_scan_finding where region = '{self.region}'",
                "compute_ecr_scan_findings.json"
            ),
            
            # K8s 네임스페이스
            (
                "K8s 네임스페이스",
                "select name, uid, phase, conditions, spec_finalizers, labels, annotations, creation_timestamp from kubernetes_namespace",
                "k8s_namespaces.json"
            ),
            
            # K8s 파드
            (
                "K8s 파드",
                "select name, namespace, uid, phase, node_name, pod_ip, host_ip, qos_class, restart_policy, service_account_name, containers, init_containers, volumes, conditions, creation_timestamp, labels, annotations from kubernetes_pod",
                "k8s_pods.json"
            ),
            
            # K8s 서비스
            (
                "K8s 서비스",
                "select name, namespace, uid, type, cluster_ip, external_ips, load_balancer_ip, ports, selector, session_affinity, external_traffic_policy, health_check_node_port, publish_not_ready_addresses, ip_families, ip_family_policy, allocate_load_balancer_node_ports, load_balancer_class, internal_traffic_policy, creation_timestamp, labels, annotations from kubernetes_service",
                "k8s_services.json"
            ),
            
            # K8s 디플로이먼트
            (
                "K8s 디플로이먼트",
                "select name, namespace, uid, replicas, updated_replicas, ready_replicas, available_replicas, unavailable_replicas, observed_generation, conditions, strategy, min_ready_seconds, progress_deadline_seconds, revision_history_limit, paused, creation_timestamp, labels, annotations from kubernetes_deployment",
                "k8s_deployments.json"
            ),
            
            # K8s 노드
            (
                "K8s 노드",
                "select name, uid, pod_cidr, pod_cidrs, provider_id, unschedulable, taints, allocatable, capacity, conditions, addresses, node_info, images, volumes_in_use, volumes_attached, config, creation_timestamp, labels, annotations from kubernetes_node",
                "k8s_nodes.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_container("🚀 컨테이너 서비스 리소스 데이터 수집 시작 (Kubernetes 포함)")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 쿼리 실행
        queries = self.get_container_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("컨테이너 서비스 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("compute_*.json")):
            file_size = file_path.stat().st_size
            if file_size > 100:
                print(f"{self.GREEN}✓ {file_path.name} ({file_size} bytes){self.NC}")
            else:
                print(f"{self.YELLOW}⚠ {file_path.name} ({file_size} bytes) - 데이터 없음{self.NC}")
                
        for file_path in sorted(self.report_dir.glob("k8s_*.json")):
            file_size = file_path.stat().st_size
            if file_size > 100:
                print(f"{self.GREEN}✓ {file_path.name} ({file_size} bytes){self.NC}")
            else:
                print(f"{self.YELLOW}⚠ {file_path.name} ({file_size} bytes) - 데이터 없음{self.NC}")
        
        # 수집 통계
        print(f"\n{self.BLUE}📊 수집 통계:{self.NC}")
        print(f"총 쿼리 수: {self.total_count}")
        print(f"성공한 쿼리: {self.success_count}")
        print(f"실패한 쿼리: {self.total_count - self.success_count}")
        print(f"성공률: {(self.success_count/self.total_count*100):.1f}%")
        
        if self.error_log.exists():
            print(f"\n{self.YELLOW}⚠️ 오류 로그: {self.error_log}{self.NC}")

def main():
    """메인 함수"""
    region = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-2')
    collector = SteampipeContainerCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
