#!/usr/bin/env python3
"""
Steampipe 기반 데이터베이스 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

class SteampipeDatabaseCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_database_collection.log"
        self.error_log = self.report_dir / "steampipe_database_errors.log"
        
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

    def get_database_queries(self) -> List[Tuple[str, str, str]]:
        return [
            # RDS 인스턴스
            (
                "RDS DB 인스턴스",
                f"select db_instance_identifier, db_instance_class, engine, engine_version, db_instance_status, master_username, db_name, endpoint_address, endpoint_port, allocated_storage, storage_type, storage_encrypted, kms_key_id, availability_zone, multi_az, publicly_accessible, auto_minor_version_upgrade, backup_retention_period, preferred_backup_window, preferred_maintenance_window, latest_restorable_time, deletion_protection, performance_insights_enabled, monitoring_interval, enhanced_monitoring_resource_arn, db_subnet_group_name, vpc_security_groups, db_parameter_groups, option_group_memberships, tags from aws_rds_db_instance where region = '{self.region}'",
                "database_rds_instances.json"
            ),
            
            # RDS 클러스터
            (
                "RDS DB 클러스터",
                f"select db_cluster_identifier, cluster_create_time, engine, engine_version, database_name, db_cluster_parameter_group, db_subnet_group, status, percent_progress, earliest_restorable_time, endpoint, reader_endpoint, multi_az, engine_mode, master_username, port, preferred_backup_window, preferred_maintenance_window, backup_retention_period, vpc_security_groups, hosted_zone_id, storage_encrypted, kms_key_id, db_cluster_resource_id, associated_roles, iam_database_authentication_enabled, clone_group_id, cluster_create_time, copy_tags_to_snapshot, cross_account_clone, deletion_protection, earliest_restorable_time, enabled_cloudwatch_logs_exports, global_write_forwarding_requested, global_write_forwarding_status, tags from aws_rds_db_cluster where region = '{self.region}'",
                "database_rds_clusters.json"
            ),
            
            # DynamoDB 테이블
            (
                "DynamoDB 테이블",
                f"select table_name, table_arn, table_status, creation_date_time, provisioned_throughput, billing_mode_summary, local_secondary_indexes, global_secondary_indexes, stream_specification, latest_stream_label, latest_stream_arn, global_table_version, replicas, restore_summary, sse_description, archival_summary, table_class_summary, deletion_protection_enabled, tags from aws_dynamodb_table where region = '{self.region}'",
                "database_dynamodb_tables.json"
            ),
            
            # ElastiCache 클러스터
            (
                "ElastiCache 클러스터",
                f"select cache_cluster_id, configuration_endpoint, client_download_landing_page, cache_node_type, engine, engine_version, cache_cluster_status, num_cache_nodes, preferred_availability_zone, preferred_outpost_arn, cache_cluster_create_time, preferred_maintenance_window, pending_modified_values, notification_configuration, cache_security_groups, cache_parameter_group, cache_subnet_group_name, cache_nodes, auto_minor_version_upgrade, security_groups, replication_group_id, snapshot_retention_limit, snapshot_window, auth_token_enabled, auth_token_last_modified_date, transit_encryption_enabled, at_rest_encryption_enabled, arn, replication_group_log_delivery_enabled, log_delivery_configurations, network_type, ip_discovery, transit_encryption_mode, tags from aws_elasticache_cluster where region = '{self.region}'",
                "database_elasticache_clusters.json"
            ),
            
            # DocumentDB 클러스터
            (
                "DocumentDB 클러스터",
                f"select db_cluster_identifier, cluster_create_time, engine, master_username, port, endpoint, reader_endpoint, status, percent_progress, earliest_restorable_time, backup_retention_period, preferred_backup_window, preferred_maintenance_window, db_cluster_parameter_group, db_subnet_group, vpc_security_groups, hosted_zone_id, storage_encrypted, kms_key_id, db_cluster_resource_id, associated_roles, enabled_cloudwatch_logs_exports, deletion_protection, tags from aws_docdb_cluster where region = '{self.region}'",
                "database_docdb_clusters.json"
            ),
            
            # Neptune 클러스터
            (
                "Neptune 클러스터",
                f"select db_cluster_identifier, cluster_create_time, engine, engine_version, database_name, db_cluster_parameter_group, db_subnet_group, status, percent_progress, earliest_restorable_time, endpoint, reader_endpoint, multi_az, port, master_username, preferred_backup_window, preferred_maintenance_window, backup_retention_period, vpc_security_groups, hosted_zone_id, storage_encrypted, kms_key_id, db_cluster_resource_id, associated_roles, iam_database_authentication_enabled, clone_group_id, cluster_create_time, copy_tags_to_snapshot, cross_account_clone, deletion_protection, enabled_cloudwatch_logs_exports, tags from aws_neptune_db_cluster where region = '{self.region}'",
                "database_neptune_clusters.json"
            )
        ]

    def run_collection(self):
        self.log_info("🚀 Steampipe 기반 데이터베이스 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        self.log_info("🗄️ 데이터베이스 리소스 수집 시작...")
        
        queries = self.get_database_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        self.log_success("데이터베이스 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 데이터베이스 리소스 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeDatabaseCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
