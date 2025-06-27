#!/usr/bin/env python3
"""
완전한 컴퓨팅 리소스 데이터 수집 스크립트 (Kubernetes 포함)
Shell 스크립트와 동일한 기능 및 출력 형식 제공
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeComputeCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_compute_collection.log"
        self.error_log = self.report_dir / "steampipe_compute_errors.log"
        
        # 로그 파일 초기화
        self.log_file.write_text("")
        self.error_log.write_text("")
        
        self.total_count = 0
        self.success_count = 0
        
        # 색상 코드
        self.RED = '\033[0;31m'
        self.GREEN = '\033[0;32m'
        self.YELLOW = '\033[1;33m'
        self.BLUE = '\033[0;34m'
        self.PURPLE = '\033[0;35m'
        self.CYAN = '\033[0;36m'
        self.NC = '\033[0m'  # No Color
        
    def log_info(self, message: str):
        print(f"{self.BLUE}[INFO]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[INFO] {message}\n")
        
    def log_success(self, message: str):
        print(f"{self.GREEN}[SUCCESS]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[SUCCESS] {message}\n")
        
    def log_warning(self, message: str):
        print(f"{self.YELLOW}[WARNING]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[WARNING] {message}\n")
        
    def log_error(self, message: str):
        print(f"{self.RED}[ERROR]{self.NC} {message}")
        with open(self.error_log, 'a') as f:
            f.write(f"[ERROR] {message}\n")
            
    def log_container(self, message: str):
        print(f"{self.PURPLE}[CONTAINER]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[CONTAINER] {message}\n")
            
    def log_k8s(self, message: str):
        print(f"{self.CYAN}[K8S]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[K8S] {message}\n")

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
        except subprocess.CalledProcessError:
            self.log_warning("Steampipe 플러그인 확인 중 오류 발생")
            
        # Kubernetes 플러그인 확인
        self.log_k8s("Steampipe Kubernetes 플러그인 확인 중...")
        try:
            result = subprocess.run(
                ["steampipe", "plugin", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            if "kubernetes" not in result.stdout:
                self.log_warning("Kubernetes 플러그인이 설치되지 않았습니다. 설치 중...")
                subprocess.run(["steampipe", "plugin", "install", "kubernetes"], check=True)
        except subprocess.CalledProcessError:
            self.log_warning("Kubernetes 플러그인 확인 중 오류 발생")

    def check_container_services(self):
        """컨테이너 서비스 존재 확인"""
        self.log_container("컨테이너 서비스 존재 확인 중...")
        
        try:
            # ECS 클러스터 존재 확인
            ecs_result = subprocess.run(
                ["aws", "ecs", "list-clusters", "--region", self.region, "--query", "clusterArns | length(@)", "--output", "text"],
                capture_output=True,
                text=True
            )
            ecs_clusters = int(ecs_result.stdout.strip()) if ecs_result.returncode == 0 else 0
            self.log_info(f"ECS 클러스터 개수: {ecs_clusters}")
            
            # EKS 클러스터 존재 확인
            eks_result = subprocess.run(
                ["aws", "eks", "list-clusters", "--region", self.region, "--query", "clusters | length(@)", "--output", "text"],
                capture_output=True,
                text=True
            )
            eks_clusters = int(eks_result.stdout.strip()) if eks_result.returncode == 0 else 0
            self.log_info(f"EKS 클러스터 개수: {eks_clusters}")
            
            # ECR 리포지토리 존재 확인
            ecr_result = subprocess.run(
                ["aws", "ecr", "describe-repositories", "--region", self.region, "--query", "repositories | length(@)", "--output", "text"],
                capture_output=True,
                text=True
            )
            ecr_repos = int(ecr_result.stdout.strip()) if ecr_result.returncode == 0 else 0
            self.log_info(f"ECR 리포지토리 개수: {ecr_repos}")
            
            if ecs_clusters == 0 and eks_clusters == 0 and ecr_repos == 0:
                self.log_warning("컨테이너 서비스가 발견되지 않았습니다. 데이터 수집을 계속 진행합니다.")
            
            # Kubernetes 연결 확인
            if eks_clusters > 0:
                self.log_k8s("EKS 클러스터가 발견되었습니다. Kubernetes 리소스 수집을 시도합니다.")
                
        except Exception as e:
            self.log_warning(f"컨테이너 서비스 확인 중 오류: {str(e)}")

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
            if file_size > 50:
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

    def get_ec2_queries(self) -> List[Tuple[str, str, str]]:
        """EC2 관련 리소스 쿼리"""
        return [
            (
                "EC2 인스턴스 상세 정보",
                f"select instance_id, instance_type, instance_state, vpc_id, subnet_id, private_ip_address, public_ip_address, private_dns_name, public_dns_name, key_name, security_groups, iam_instance_profile_arn, monitoring_state, placement_availability_zone, platform, architecture, virtualization_type, hypervisor, root_device_type, root_device_name, block_device_mappings, ebs_optimized, ena_support, sriov_net_support, source_dest_check, launch_time, state_transition_reason, usage_operation, usage_operation_update_time, tags from aws_ec2_instance where region = '{self.region}'",
                "compute_ec2_instances.json"
            ),
            (
                "EC2 AMI 이미지",
                f"select image_id, name, description, state, public, owner_id, architecture, platform, virtualization_type, hypervisor, root_device_type, root_device_name, block_device_mappings, creation_date, deprecation_time, usage_operation, platform_details, image_type, image_location, kernel_id, ramdisk_id, sriov_net_support, ena_support, boot_mode, tags from aws_ec2_ami where region = '{self.region}' and owner_id = (select account_id from aws_caller_identity)",
                "compute_ec2_amis.json"
            ),
            (
                "EC2 키 페어",
                f"select key_name, key_fingerprint, key_type, key_pair_id, create_time, tags from aws_ec2_key_pair where region = '{self.region}'",
                "compute_ec2_key_pairs.json"
            ),
            (
                "EC2 인스턴스 타입",
                f"select instance_type, current_generation, free_tier_eligible, supported_usage_classes, supported_root_device_types, supported_virtualization_types, bare_metal, hypervisor, processor_info, vcpu_info, memory_info, instance_storage_info, ebs_info, network_info, gpu_info, fpga_info, placement_group_info, hibernation_supported, burstable_performance_supported, dedicated_hosts_supported, auto_recovery_supported, supported_boot_modes from aws_ec2_instance_type where region = '{self.region}'",
                "compute_ec2_instance_types.json"
            ),
            (
                "EC2 스팟 가격",
                f"select instance_type, product_description, spot_price, timestamp, availability_zone from aws_ec2_spot_price where region = '{self.region}' and timestamp >= now() - interval '1 day'",
                "compute_ec2_spot_prices.json"
            ),
            (
                "EC2 예약 인스턴스",
                f"select reserved_instance_id, instance_type, availability_zone, instance_count, product_description, instance_state, start_time, end_time, duration, usage_price, fixed_price, currency_code, instance_tenancy, offering_class, offering_type, scope, tags from aws_ec2_reserved_instance where region = '{self.region}'",
                "compute_ec2_reserved_instances.json"
            ),
            (
                "EC2 배치 그룹",
                f"select group_name, group_id, strategy, partition_count, state, tags from aws_ec2_placement_group where region = '{self.region}'",
                "compute_ec2_placement_groups.json"
            )
        ]

    def get_autoscaling_queries(self) -> List[Tuple[str, str, str]]:
        """Auto Scaling 관련 리소스 쿼리"""
        return [
            (
                "Auto Scaling 그룹 상세 정보",
                f"select name, autoscaling_group_arn, min_size, max_size, desired_capacity, default_cooldown, availability_zones, load_balancer_names, target_group_arns, health_check_type, health_check_grace_period, placement_group, vpc_zone_identifier, termination_policies, new_instances_protected_from_scale_in, service_linked_role_arn, max_instance_lifetime, capacity_rebalance, warm_pool_configuration, warm_pool_size, status, suspended_processes, enabled_metrics, tags from aws_ec2_autoscaling_group where region = '{self.region}'",
                "compute_asg_detailed.json"
            ),
            (
                "Auto Scaling 시작 구성",
                f"select launch_configuration_name, launch_configuration_arn, image_id, instance_type, key_name, security_groups, classic_link_vpc_id, classic_link_vpc_security_groups, user_data, instance_monitoring, spot_price, iam_instance_profile, created_time, ebs_optimized, associate_public_ip_address, placement_tenancy, block_device_mappings, metadata_options from aws_ec2_autoscaling_launch_configuration where region = '{self.region}'",
                "compute_asg_launch_configs.json"
            ),
            (
                "EC2 시작 템플릿",
                f"select launch_template_id, launch_template_name, create_time, created_by, default_version_number, latest_version_number, tags from aws_ec2_launch_template where region = '{self.region}'",
                "compute_ec2_launch_templates.json"
            ),
            (
                "EC2 시작 템플릿 버전",
                f"select launch_template_id, launch_template_name, version_number, version_description, create_time, created_by, default_version, launch_template_data from aws_ec2_launch_template_version where region = '{self.region}'",
                "compute_ec2_launch_template_versions.json"
            )
        ]

    def get_loadbalancer_queries(self) -> List[Tuple[str, str, str]]:
        """로드 밸런싱 관련 리소스 쿼리"""
        return [
            (
                "Application Load Balancer 상세 정보",
                f"select arn, name, type, scheme, vpc_id, availability_zones, security_groups, ip_address_type, state_code, state_reason, dns_name, canonical_hosted_zone_id, created_time, load_balancer_attributes, tags from aws_ec2_application_load_balancer where region = '{self.region}'",
                "compute_alb_detailed.json"
            ),
            (
                "Network Load Balancer 상세 정보",
                f"select arn, name, type, scheme, vpc_id, availability_zones, ip_address_type, state_code, state_reason, dns_name, canonical_hosted_zone_id, created_time, load_balancer_attributes, tags from aws_ec2_network_load_balancer where region = '{self.region}'",
                "compute_nlb_detailed.json"
            ),
            (
                "Classic Load Balancer",
                f"select name, dns_name, canonical_hosted_zone_name, canonical_hosted_zone_name_id, vpc_id, subnets, security_groups, instances, availability_zones, backend_server_descriptions, connection_draining, cross_zone_load_balancing, access_log, connection_settings, created_time, scheme, source_security_group, tags from aws_ec2_classic_load_balancer where region = '{self.region}'",
                "compute_clb.json"
            ),
            (
                "타겟 그룹",
                f"select target_group_arn, target_group_name, protocol, port, vpc_id, health_check_enabled, health_check_interval_seconds, health_check_path, health_check_port, health_check_protocol, health_check_timeout_seconds, healthy_threshold_count, unhealthy_threshold_count, load_balancer_arns, target_type, protocol_version, ip_address_type, tags from aws_ec2_target_group where region = '{self.region}'",
                "compute_target_groups.json"
            ),
            (
                "로드 밸런서 리스너",
                f"select arn, load_balancer_arn, port, protocol, certificates, ssl_policy, default_actions from aws_ec2_load_balancer_listener where region = '{self.region}'",
                "compute_lb_listeners.json"
            ),
            (
                "로드 밸런서 리스너 규칙",
                f"select arn, listener_arn, priority, conditions, actions, is_default from aws_ec2_load_balancer_listener_rule where region = '{self.region}'",
                "compute_lb_listener_rules.json"
            )
        ]

    def get_serverless_queries(self) -> List[Tuple[str, str, str]]:
        """서버리스 컴퓨팅 관련 리소스 쿼리"""
        return [
            (
                "Lambda 함수 상세 정보",
                f"select name, arn, runtime, role, handler, code_size, description, timeout, memory_size, last_modified, code_sha_256, version, vpc_id, environment_variables, dead_letter_config_target_arn, kms_key_arn, tracing_config, master_arn, revision_id, layers, state, state_reason, state_reason_code, last_update_status, last_update_status_reason, last_update_status_reason_code, file_system_configs, package_type, architectures, ephemeral_storage, snap_start, logging_config, tags from aws_lambda_function where region = '{self.region}'",
                "compute_lambda_functions.json"
            ),
            (
                "Lambda 레이어",
                f"select layer_name, layer_arn, version, description, created_date, compatible_runtimes, license_info, compatible_architectures from aws_lambda_layer_version where region = '{self.region}'",
                "compute_lambda_layers.json"
            ),
            (
                "Lambda 별칭",
                f"select name, alias_arn, function_name, function_version, description, revision_id from aws_lambda_alias where region = '{self.region}'",
                "compute_lambda_aliases.json"
            ),
            (
                "Lambda 버전",
                f"select version, function_name, function_arn, description, code_size, code_sha_256, last_modified, master_arn, revision_id, layers, state, state_reason, state_reason_code, last_update_status, last_update_status_reason, last_update_status_reason_code from aws_lambda_version where region = '{self.region}'",
                "compute_lambda_versions.json"
            ),
            (
                "Lambda 이벤트 소스 매핑",
                f"select uuid, arn, function_arn, function_name, last_modified, last_processing_result, state, state_transition_reason, batch_size, maximum_batching_window_in_seconds, parallelization_factor, starting_position, starting_position_timestamp, maximum_record_age_in_seconds, bisect_batch_on_function_error, maximum_retry_attempts, tumbling_window_in_seconds, topics, queues, source_access_configurations, self_managed_event_source, function_response_types, amazon_managed_kafka_event_source_config, self_managed_kafka_event_source_config, scaling_config from aws_lambda_event_source_mapping where region = '{self.region}'",
                "compute_lambda_event_mappings.json"
            )
        ]

    def get_container_queries(self) -> List[Tuple[str, str, str]]:
        """컨테이너 서비스 관련 리소스 쿼리"""
        return [
            (
                "ECS 클러스터",
                f"select cluster_name, cluster_arn, status, running_tasks_count, pending_tasks_count, active_services_count, statistics, tags, settings, configuration, service_connect_defaults, capacity_providers, default_capacity_provider_strategy from aws_ecs_cluster where region = '{self.region}'",
                "compute_ecs_clusters.json"
            ),
            (
                "ECS 서비스",
                f"select service_name, service_arn, cluster_arn, task_definition, desired_count, running_count, pending_count, status, task_sets, deployment_controller, deployments, role_arn, events, created_at, platform_version, platform_family, tags, propagate_tags, enable_ecs_managed_tags, created_by, enable_execute_command, health_check_grace_period_seconds, scheduling_strategy, deployment_configuration, network_configuration, service_registries, scale_in_protection, capacity_provider_strategy from aws_ecs_service where region = '{self.region}'",
                "compute_ecs_services.json"
            ),
            (
                "ECS 태스크",
                f"select task_arn, cluster_arn, task_definition_arn, container_instance_arn, overrides, last_status, desired_status, cpu, memory, containers, started_by, version, stopped_reason, stopped_at, connectivity, connectivity_at, pull_started_at, pull_stopped_at, execution_stopped_at, created_at, started_at, stopping_at, platform_version, platform_family, attributes, health_status, tags, group_name, launch_type, capacity_provider_name, availability_zone, ephemeral_storage from aws_ecs_task where region = '{self.region}'",
                "compute_ecs_tasks.json"
            ),
            (
                "ECS 태스크 정의",
                f"select task_definition_arn, family, task_role_arn, execution_role_arn, network_mode, revision, volumes, status, requires_attributes, placement_constraints, compatibilities, runtime_platform, requires_compatibilities, cpu, memory, inference_accelerators, pid_mode, ipc_mode, proxy_configuration, registered_at, deregistered_at, registered_by, ephemeral_storage from aws_ecs_task_definition where region = '{self.region}'",
                "compute_ecs_task_definitions.json"
            ),
            (
                "ECS 컨테이너 인스턴스",
                f"select container_instance_arn, ec2_instance_id, capacity_provider_name, version, version_info, remaining_resources, registered_resources, status, status_reason, agent_connected, running_tasks_count, pending_tasks_count, agent_update_status, attributes, registered_at, attachments, tags from aws_ecs_container_instance where region = '{self.region}'",
                "compute_ecs_container_instances.json"
            ),
            (
                "EKS 클러스터",
                f"select name, arn, created_at, version, endpoint, role_arn, resources_vpc_config, kubernetes_network_config, logging, identity, status, certificate_authority, client_request_token, platform_version, tags, encryption_config, connector_config, id, health, outpost_config, access_config from aws_eks_cluster where region = '{self.region}'",
                "compute_eks_clusters.json"
            ),
            (
                "EKS 노드 그룹",
                f"select cluster_name, nodegroup_name, nodegroup_arn, status, capacity_type, scaling_config, instance_types, subnets, remote_access, ami_type, node_role, labels, taints, resources, health, update_config, launch_template, version, release_version, created_at, modified_at, tags from aws_eks_node_group where region = '{self.region}'",
                "compute_eks_node_groups.json"
            ),
            (
                "EKS Fargate 프로필",
                f"select fargate_profile_name, fargate_profile_arn, cluster_name, created_at, pod_execution_role_arn, subnets, selectors, status, tags from aws_eks_fargate_profile where region = '{self.region}'",
                "compute_eks_fargate_profiles.json"
            ),
            (
                "EKS 애드온",
                f"select addon_name, cluster_name, addon_arn, addon_version, status, health, configuration_values, resolve_conflicts, service_account_role_arn, created_at, modified_at, tags from aws_eks_addon where region = '{self.region}'",
                "compute_eks_addons.json"
            ),
            (
                "EKS 아이덴티티 제공자",
                f"select cluster_name, identity_provider_config_name, identity_provider_config_arn, type, status, tags from aws_eks_identity_provider_config where region = '{self.region}'",
                "compute_eks_identity_providers.json"
            ),
            (
                "Fargate 태스크",
                f"select task_arn, cluster_arn, task_definition_arn, overrides, last_status, desired_status, cpu, memory, containers, started_by, version, stopped_reason, stopped_at, connectivity, connectivity_at, pull_started_at, pull_stopped_at, execution_stopped_at, created_at, started_at, stopping_at, platform_version, platform_family, attributes, health_status, tags, group_name, launch_type, capacity_provider_name, availability_zone, ephemeral_storage from aws_ecs_task where region = '{self.region}' and launch_type = 'FARGATE'",
                "compute_fargate_tasks.json"
            )
        ]

    def get_k8s_queries(self) -> List[Tuple[str, str, str]]:
        """Kubernetes 관련 리소스 쿼리"""
        return [
            (
                "K8s 네임스페이스",
                "select name, uid, creation_timestamp, deletion_timestamp, labels, annotations from kubernetes_namespace",
                "k8s_namespaces.json"
            ),
            (
                "K8s 파드",
                "select name, namespace, uid, node_name, phase, pod_ip, host_ip, qos_class, restart_policy, service_account_name, node_selector, tolerations, affinity, priority, priority_class_name, runtime_class_name, overhead, topology_spread_constraints, preemption_policy, os, host_network, host_pid, host_ipc, share_process_namespace, security_context, dns_policy, dns_config, hostname, subdomain, scheduler_name, creation_timestamp, deletion_timestamp, labels, annotations from kubernetes_pod",
                "k8s_pods.json"
            ),
            (
                "K8s 디플로이먼트",
                "select name, namespace, uid, replicas, updated_replicas, ready_replicas, available_replicas, unavailable_replicas, observed_generation, creation_timestamp, labels, annotations from kubernetes_deployment",
                "k8s_deployments.json"
            ),
            (
                "K8s 서비스",
                "select name, namespace, uid, type, cluster_ip, cluster_ips, external_ips, session_affinity, external_name, external_traffic_policy, health_check_node_port, publish_not_ready_addresses, ip_families, ip_family_policy, allocate_load_balancer_node_ports, load_balancer_class, internal_traffic_policy, creation_timestamp, labels, annotations from kubernetes_service",
                "k8s_services.json"
            ),
            (
                "K8s 노드",
                "select name, uid, pod_cidr, pod_cidrs, provider_id, unschedulable, creation_timestamp, labels, annotations from kubernetes_node",
                "k8s_nodes.json"
            ),
            (
                "K8s 인그레스",
                "select name, namespace, uid, ingress_class_name, creation_timestamp, labels, annotations from kubernetes_ingress",
                "k8s_ingress.json"
            ),
            (
                "K8s 컨피그맵",
                "select name, namespace, uid, data, binary_data, immutable, creation_timestamp, labels, annotations from kubernetes_config_map",
                "k8s_configmaps.json"
            ),
            (
                "K8s 시크릿",
                "select name, namespace, uid, type, data, string_data, immutable, creation_timestamp, labels, annotations from kubernetes_secret",
                "k8s_secrets.json"
            ),
            (
                "K8s 퍼시스턴트 볼륨",
                "select name, uid, capacity, access_modes, reclaim_policy, storage_class, mount_options, volume_mode, node_affinity, creation_timestamp, labels, annotations from kubernetes_persistent_volume",
                "k8s_persistent_volumes.json"
            ),
            (
                "K8s 퍼시스턴트 볼륨 클레임",
                "select name, namespace, uid, access_modes, storage_class, volume_name, volume_mode, creation_timestamp, labels, annotations from kubernetes_persistent_volume_claim",
                "k8s_persistent_volume_claims.json"
            ),
            (
                "K8s 데몬셋",
                "select name, namespace, uid, current_number_scheduled, desired_number_scheduled, number_available, number_misscheduled, number_ready, number_unavailable, updated_number_scheduled, observed_generation, creation_timestamp, labels, annotations from kubernetes_daemonset",
                "k8s_daemonsets.json"
            ),
            (
                "K8s 스테이트풀셋",
                "select name, namespace, uid, replicas, ready_replicas, current_replicas, updated_replicas, current_revision, update_revision, observed_generation, collision_count, creation_timestamp, labels, annotations from kubernetes_stateful_set",
                "k8s_statefulsets.json"
            ),
            (
                "K8s 잡",
                "select name, namespace, uid, parallelism, completions, active_deadline_seconds, backoff_limit, selector, manual_selector, completion_mode, suspend, creation_timestamp, labels, annotations from kubernetes_job",
                "k8s_jobs.json"
            ),
            (
                "K8s 크론잡",
                "select name, namespace, uid, schedule, timezone, starting_deadline_seconds, concurrency_policy, suspend, successful_jobs_history_limit, failed_jobs_history_limit, creation_timestamp, labels, annotations from kubernetes_cronjob",
                "k8s_cronjobs.json"
            )
        ]

    def get_other_queries(self) -> List[Tuple[str, str, str]]:
        """기타 컴퓨팅 서비스 관련 리소스 쿼리"""
        return [
            (
                "Elastic Beanstalk 애플리케이션",
                f"select name, description, date_created, date_updated, versions, configuration_templates, resource_lifecycle_config from aws_elastic_beanstalk_application where region = '{self.region}'",
                "compute_beanstalk_applications.json"
            ),
            (
                "Elastic Beanstalk 환경",
                f"select environment_name, environment_id, application_name, version_label, solution_stack_name, platform_arn, template_name, description, endpoint_url, cname, date_created, date_updated, status, abortable_operation_in_progress, health, health_status, resources, tier, environment_links, environment_arn, operations_role from aws_elastic_beanstalk_environment where region = '{self.region}'",
                "compute_beanstalk_environments.json"
            ),
            (
                "Batch 작업 큐",
                f"select job_queue_name, job_queue_arn, state, status, status_reason, priority, compute_environment_order, tags from aws_batch_job_queue where region = '{self.region}'",
                "compute_batch_queues.json"
            ),
            (
                "Batch 컴퓨팅 환경",
                f"select compute_environment_name, compute_environment_arn, arn, type, state, status, status_reason, compute_resources, service_role, tags from aws_batch_compute_environment where region = '{self.region}'",
                "compute_batch_environments.json"
            ),
            (
                "Lightsail 인스턴스",
                f"select name, arn, support_code, created_at, location, resource_type, tags, blueprint_id, blueprint_name, bundle_id, add_ons, is_static_ip, private_ip_address, public_ip_address, ipv6_addresses, hardware, networking, state, username, ssh_key_name from aws_lightsail_instance where region = '{self.region}'",
                "compute_lightsail_instances.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_container("🚀 완전한 컴퓨팅 리소스 데이터 수집 시작 (Kubernetes 포함)")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 컨테이너 서비스 확인
        self.check_container_services()
        
        # EC2 관련 리소스 수집
        self.log_info("💻 EC2 관련 리소스 수집 시작...")
        ec2_queries = self.get_ec2_queries()
        for description, query, output_file in ec2_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # Auto Scaling 관련 리소스 수집
        self.log_info("⚖️ Auto Scaling 관련 리소스 수집 시작...")
        autoscaling_queries = self.get_autoscaling_queries()
        for description, query, output_file in autoscaling_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 로드 밸런싱 관련 리소스 수집
        self.log_info("🔄 로드 밸런싱 관련 리소스 수집 시작...")
        loadbalancer_queries = self.get_loadbalancer_queries()
        for description, query, output_file in loadbalancer_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 서버리스 컴퓨팅 리소스 수집
        self.log_info("🚀 서버리스 컴퓨팅 리소스 수집 시작...")
        serverless_queries = self.get_serverless_queries()
        for description, query, output_file in serverless_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 컨테이너 서비스 리소스 수집
        self.log_container("📦 컨테이너 서비스 리소스 수집 시작...")
        container_queries = self.get_container_queries()
        for description, query, output_file in container_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # Kubernetes 리소스 수집
        self.log_k8s("☸️ Kubernetes 리소스 수집 시작...")
        k8s_queries = self.get_k8s_queries()
        for description, query, output_file in k8s_queries:
            if self.execute_steampipe_query(description, query, output_file):
                pass
            else:
                self.log_warning(f"Kubernetes 리소스 수집 실패: {description} (클러스터 연결 확인 필요)")
        
        # 기타 컴퓨팅 서비스 수집
        self.log_info("🏗️ 기타 컴퓨팅 서비스 수집 시작...")
        other_queries = self.get_other_queries()
        for description, query, output_file in other_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("완전한 컴퓨팅 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        self.display_file_list()
        self.display_statistics()
        self.display_error_summary()
        self.display_next_steps()
        
        self.log_container("🎉 완전한 컴퓨팅 리소스 데이터 수집이 완료되었습니다!")

    def display_file_list(self):
        """생성된 파일 목록 표시"""
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        
        # 컴퓨팅 및 K8s 관련 파일들 검색
        patterns = ["compute_*.json", "k8s_*.json"]
        files_found = []
        
        for pattern in patterns:
            files_found.extend(self.report_dir.glob(pattern))
        
        files_found.sort()
        
        for file_path in files_found:
            file_size = file_path.stat().st_size
            if file_size > 100:
                print(f"{self.GREEN}✓ {file_path.name} ({file_size} bytes){self.NC}")
            else:
                print(f"{self.YELLOW}⚠ {file_path.name} ({file_size} bytes) - 데이터 없음{self.NC}")

    def display_statistics(self):
        """수집 통계 표시"""
        print(f"\n{self.BLUE}📊 수집 통계:{self.NC}")
        print(f"총 쿼리 수: {self.total_count}")
        print(f"성공한 쿼리: {self.success_count}")
        print(f"실패한 쿼리: {self.total_count - self.success_count}")
        
        # 카테고리별 수집 현황
        print(f"\n{self.BLUE}📋 카테고리별 수집 현황:{self.NC}")
        print("💻 EC2 관련: 7개")
        print("⚖️ Auto Scaling: 4개")
        print("🔄 로드 밸런싱: 6개")
        print("🚀 서버리스 컴퓨팅: 5개")
        print("📦 컨테이너 서비스: 11개")
        print("☸️ Kubernetes: 13개")
        print("🏗️ 기타 컴퓨팅: 5개")
        print("📊 총 리소스 타입: 51개")

    def display_error_summary(self):
        """오류 요약 표시"""
        if self.error_log.exists() and self.error_log.stat().st_size > 0:
            self.log_warning(f"오류가 발생했습니다. {self.error_log.name} 파일을 확인하세요.")
            
            print(f"\n{self.YELLOW}최근 오류 (마지막 5줄):{self.NC}")
            try:
                with open(self.error_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(line.strip())
            except Exception:
                pass

    def display_next_steps(self):
        """다음 단계 안내"""
        print(f"\n{self.YELLOW}💡 다음 단계:{self.NC}")
        print("1. 수집된 완전한 컴퓨팅 데이터를 바탕으로 상세 분석 진행")
        print("2. EC2 인스턴스 타입 최적화 및 비용 분석")
        print("3. Auto Scaling 및 Load Balancer 구성 최적화 검토")
        print("4. Lambda 함수 성능 및 비용 최적화 분석")
        print("5. 컨테이너 서비스 (ECS/EKS) 리소스 활용도 분석")
        print("6. Kubernetes 클러스터 구성 및 워크로드 분석")
        print("7. 서버리스 vs 컨테이너 vs EC2 비용 효율성 비교")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="완전한 컴퓨팅 리소스 데이터 수집 (Kubernetes 포함)")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeComputeCollector(args.region, args.report_dir)
    collector.collect_data()

if __name__ == "__main__":
    main()
