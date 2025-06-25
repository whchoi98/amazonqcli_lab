#!/usr/bin/env python3
"""
Steampipe 기반 컨테이너 서비스 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

class SteampipeContainerCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_container_collection.log"
        self.error_log = self.report_dir / "steampipe_container_errors.log"
        
        self.log_file.write_text("")
        self.error_log.write_text("")
        
        self.success_count = 0
        self.total_count = 0

    def log_info(self, message: str):
        print(f"\033[0;34m[INFO]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[INFO] {message}\n")

    def log_success(self, message: str):
        print(f"\033[0;32m[SUCCESS]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[SUCCESS] {message}\n")

    def log_warning(self, message: str):
        print(f"\033[1;33m[WARNING]\033[0m {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[WARNING] {message}\n")

    def log_error(self, message: str):
        print(f"\033[0;31m[ERROR]\033[0m {message}")
        with open(self.error_log, 'a') as f:
            f.write(f"[ERROR] {message}\n")

    def execute_steampipe_query(self, description: str, query: str, output_file: str) -> bool:
        self.log_info(f"수집 중: {description}")
        self.total_count += 1
        
        try:
            result = subprocess.run(
                ["steampipe", "query", query, "--output", "json"],
                cwd=self.report_dir,
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
            self.log_error(f"{description} 실패 - {output_file}")
            return False

    def get_container_queries(self) -> List[Tuple[str, str, str]]:
        return [
            # ECS 클러스터
            (
                "ECS 클러스터",
                f"select cluster_name, cluster_arn, status, registered_container_instances_count, running_tasks_count, pending_tasks_count, active_services_count, statistics, capacity_providers, default_capacity_provider_strategy, attachments, attachments_status, tags from aws_ecs_cluster where region = '{self.region}'",
                "container_ecs_clusters.json"
            ),
            
            # ECS 서비스
            (
                "ECS 서비스",
                f"select service_name, service_arn, cluster_arn, task_definition, desired_count, running_count, pending_count, status, deployment_status, launch_type, platform_version, load_balancers, service_registries, network_configuration, capacity_provider_strategy, enable_execute_command, tags from aws_ecs_service where region = '{self.region}'",
                "container_ecs_services.json"
            ),
            
            # EKS 클러스터
            (
                "EKS 클러스터",
                f"select name, arn, created_at, version, endpoint, role_arn, resources_vpc_config, kubernetes_network_config, logging, identity, status, certificate_authority, client_request_token, platform_version, tags, encryption_config, connector_config, id, health, outpost_config from aws_eks_cluster where region = '{self.region}'",
                "container_eks_clusters.json"
            ),
            
            # ECR 리포지토리
            (
                "ECR 리포지토리",
                f"select repository_name, repository_arn, registry_id, repository_uri, created_at, image_tag_mutability, image_scanning_configuration, encryption_configuration, tags from aws_ecr_repository where region = '{self.region}'",
                "container_ecr_repositories.json"
            )
        ]

    def run_collection(self):
        self.log_info("🚀 Steampipe 기반 컨테이너 서비스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        self.log_info("🐳 컨테이너 서비스 수집 시작...")
        
        queries = self.get_container_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        self.log_success("컨테이너 서비스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 컨테이너 서비스 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeContainerCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
