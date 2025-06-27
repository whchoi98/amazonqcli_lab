#!/usr/bin/env python3
"""
AWS 데이터베이스 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeDatabaseCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        self.report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "database_collection_errors.log"
        
        # 색상 코드
        self.GREEN = '\033[0;32m'
        self.BLUE = '\033[0;34m'
        self.YELLOW = '\033[1;33m'
        self.RED = '\033[0;31m'
        self.NC = '\033[0m'  # No Color
        
    def log_info(self, message: str):
        print(f"{self.BLUE}ℹ️ {message}{self.NC}")
        
    def log_success(self, message: str):
        print(f"{self.GREEN}✅ {message}{self.NC}")
        
    def log_warning(self, message: str):
        print(f"{self.YELLOW}⚠️ {message}{self.NC}")
        
    def log_error(self, message: str):
        print(f"{self.RED}❌ {message}{self.NC}")

    def check_steampipe_plugin(self):
        """Steampipe AWS 플러그인 확인"""
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

    def get_database_queries(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 쿼리 구조 사용"""
        return [
            # RDS 인스턴스 상세 정보
            (
                "RDS 인스턴스 상세 정보",
                f"select db_instance_identifier, arn, class, engine, engine_version, master_user_name, db_name, allocated_storage, max_allocated_storage, storage_type, storage_encrypted, kms_key_id, iops, storage_throughput, status, endpoint_address, endpoint_port, endpoint_hosted_zone_id, multi_az, availability_zone, secondary_availability_zone, publicly_accessible, vpc_security_groups, db_security_groups, db_parameter_groups, db_subnet_group_name, option_group_memberships, preferred_backup_window, backup_retention_period, preferred_maintenance_window, pending_modified_values, latest_restorable_time, auto_minor_version_upgrade, read_replica_source_db_instance_identifier, read_replica_db_instance_identifiers, read_replica_db_cluster_identifiers, replica_mode, license_model, character_set_name, nchar_character_set_name, enhanced_monitoring_resource_arn, monitoring_interval, monitoring_role_arn, promotion_tier, timezone, iam_database_authentication_enabled, performance_insights_enabled, performance_insights_kms_key_id, performance_insights_retention_period, enabled_cloudwatch_logs_exports, processor_features, deletion_protection, associated_roles, tags from aws_rds_db_instance where region = '{self.region}'",
                "database_rds_instances.json"
            ),
            
            # RDS 클러스터 상세 정보
            (
                "RDS 클러스터 상세 정보",
                f"select db_cluster_identifier, arn, engine, engine_version, engine_mode, master_user_name, database_name, status, endpoint, reader_endpoint, custom_endpoints, multi_az, port, preferred_backup_window, backup_retention_period, preferred_maintenance_window, read_replica_identifiers, members, vpc_security_groups, db_subnet_group, db_cluster_parameter_group, option_group_memberships, availability_zones, character_set_name, kms_key_id, storage_encrypted, associated_roles, iam_database_authentication_enabled, clone_group_id, create_time, earliest_restorable_time, earliest_backtrack_time, backtrack_window, backtrack_consumed_change_records, enabled_cloudwatch_logs_exports, capacity, scaling_configuration_info, deletion_protection, http_endpoint_enabled, activity_stream_mode, activity_stream_status, activity_stream_kms_key_id, activity_stream_kinesis_stream_name, copy_tags_to_snapshot, cross_account_clone, domain_memberships, tags from aws_rds_db_cluster where region = '{self.region}'",
                "database_rds_clusters.json"
            ),
            
            # RDS 스냅샷
            (
                "RDS 스냅샷",
                f"select db_snapshot_identifier, db_instance_identifier, create_time, engine, allocated_storage, status, port, availability_zone, vpc_id, instance_create_time, master_user_name, engine_version, license_model, type, iops, option_group_name, percent_progress, source_region, source_db_snapshot_identifier, storage_type, tde_credential_arn, encrypted, kms_key_id, timezone, iam_database_authentication_enabled, processor_features, dbi_resource_id, tags from aws_rds_db_snapshot where region = '{self.region}'",
                "database_rds_snapshots.json"
            ),
            
            # RDS 클러스터 스냅샷
            (
                "RDS 클러스터 스냅샷",
                f"select db_cluster_snapshot_identifier, db_cluster_identifier, create_time, engine, engine_version, allocated_storage, status, port, vpc_id, cluster_create_time, master_user_name, license_model, type, percent_progress, storage_encrypted, kms_key_id, arn, source_db_cluster_snapshot_arn, iam_database_authentication_enabled, tags from aws_rds_db_cluster_snapshot where region = '{self.region}'",
                "database_rds_cluster_snapshots.json"
            ),
            
            # RDS 서브넷 그룹
            (
                "RDS 서브넷 그룹",
                f"select name, arn, description, status, vpc_id, subnets, tags from aws_rds_db_subnet_group where region = '{self.region}'",
                "database_rds_subnet_groups.json"
            ),
            
            # RDS 파라미터 그룹
            (
                "RDS 파라미터 그룹",
                f"select name, arn, description, db_parameter_group_family, parameters, tags from aws_rds_db_parameter_group where region = '{self.region}'",
                "database_rds_parameter_groups.json"
            ),
            
            # RDS 옵션 그룹
            (
                "RDS 옵션 그룹",
                f"select name, arn, description, engine_name, major_engine_version, vpc_id, allows_vpc_and_non_vpc_instance_memberships, options, tags from aws_rds_db_option_group where region = '{self.region}'",
                "database_rds_option_groups.json"
            ),
            
            # RDS 이벤트 구독
            (
                "RDS 이벤트 구독",
                f"select cust_subscription_id, customer_aws_id, sns_topic_arn, status, subscription_creation_time, source_type, source_ids_list, event_categories_list, enabled from aws_rds_db_event_subscription where region = '{self.region}'",
                "database_rds_event_subscriptions.json"
            ),
            
            # DynamoDB 테이블 상세 정보
            (
                "DynamoDB 테이블 상세 정보",
                f"select name, arn, table_id, table_status, creation_date_time, billing_mode, attribute_definitions, key_schema, table_size_bytes, item_count, stream_specification, latest_stream_label, latest_stream_arn, restore_summary, sse_description, replicas, archival_summary, table_class, deletion_protection_enabled, tags from aws_dynamodb_table where region = '{self.region}'",
                "database_dynamodb_tables.json"
            ),
            
            # DynamoDB 백업
            (
                "DynamoDB 백업",
                f"select name, arn, table_name, table_arn, table_id, backup_status, backup_type, backup_creation_datetime, backup_expiry_datetime, backup_size_bytes from aws_dynamodb_backup where region = '{self.region}'",
                "database_dynamodb_backups.json"
            ),
            
            # DynamoDB Global Tables
            (
                "DynamoDB Global Tables",
                f"select global_table_name, global_table_status, creation_date_time, global_table_arn, replication_group from aws_dynamodb_global_table where region = '{self.region}'",
                "database_dynamodb_global_tables.json"
            ),
            
            # ElastiCache 클러스터 상세 정보
            (
                "ElastiCache 클러스터 상세 정보",
                f"select cache_cluster_id, configuration_endpoint, client_download_landing_page, cache_node_type, engine, engine_version, cache_cluster_status, num_cache_nodes, preferred_availability_zone, preferred_outpost_arn, cache_cluster_create_time, preferred_maintenance_window, pending_modified_values, notification_configuration, cache_security_groups, cache_parameter_group, cache_subnet_group_name, cache_nodes, auto_minor_version_upgrade, security_groups, replication_group_id, snapshot_retention_limit, snapshot_window, auth_token_enabled, auth_token_last_modified_date, transit_encryption_enabled, at_rest_encryption_enabled, arn, replication_group_log_delivery_enabled, log_delivery_configurations, network_type, ip_discovery, transit_encryption_mode, tags from aws_elasticache_cluster where region = '{self.region}'",
                "database_elasticache_clusters.json"
            ),
            
            # ElastiCache 복제 그룹
            (
                "ElastiCache 복제 그룹",
                f"select replication_group_id, description, global_replication_group_info, status, pending_modified_values, member_clusters, node_groups, snapshotting_cluster_id, automatic_failover, multi_az, configuration_endpoint, snapshot_retention_limit, snapshot_window, cluster_enabled, cache_node_type, auth_token_enabled, auth_token_last_modified_date, transit_encryption_enabled, at_rest_encryption_enabled, member_clusters_outpost_arns, kms_key_id, arn, user_group_ids, log_delivery_configurations, replication_group_create_time, data_tiering, network_type, ip_discovery, transit_encryption_mode, cluster_mode from aws_elasticache_replication_group where region = '{self.region}'",
                "database_elasticache_replication_groups.json"
            ),
            
            # ElastiCache 서브넷 그룹
            (
                "ElastiCache 서브넷 그룹",
                f"select cache_subnet_group_name, cache_subnet_group_description, vpc_id, subnets, arn, supported_network_types from aws_elasticache_subnet_group where region = '{self.region}'",
                "database_elasticache_subnet_groups.json"
            ),
            
            # ElastiCache 파라미터 그룹
            (
                "ElastiCache 파라미터 그룹",
                f"select cache_parameter_group_name, cache_parameter_group_family, description, is_global, arn from aws_elasticache_parameter_group where region = '{self.region}'",
                "database_elasticache_parameter_groups.json"
            ),
            
            # Redshift 클러스터
            (
                "Redshift 클러스터",
                f"select cluster_identifier, node_type, cluster_status, cluster_availability_status, modify_status, master_username, db_name, endpoint, cluster_create_time, automated_snapshot_retention_period, manual_snapshot_retention_period, cluster_security_groups, vpc_security_groups, cluster_parameter_groups, cluster_subnet_group_name, vpc_id, availability_zone, preferred_maintenance_window, pending_modified_values, cluster_version, allow_version_upgrade, number_of_nodes, publicly_accessible, encrypted, restore_status, data_transfer_progress, hsm_status, cluster_snapshot_copy_status, cluster_public_key, cluster_nodes, elastic_ip_status, cluster_revision_number, tags, kms_key_id, enhanced_vpc_routing, iam_roles, pending_actions, maintenance_track_name, elastic_resize_number_of_node_options, deferred_maintenance_windows, snapshot_schedule_identifier, snapshot_schedule_state, expected_next_snapshot_schedule_time, expected_next_snapshot_schedule_time_status, next_maintenance_window_start_time, resize_info, availability_zone_relocation_status, cluster_namespace_arn, total_storage_capacity_in_mega_bytes, aqua_configuration, default_iam_role_arn, reserved_node_exchange_status from aws_redshift_cluster where region = '{self.region}'",
                "database_redshift_clusters.json"
            ),
            
            # DocumentDB 클러스터
            (
                "DocumentDB 클러스터",
                f"select db_cluster_identifier, members, backup_retention_period, preferred_backup_window, preferred_maintenance_window, port, master_user_name, engine, engine_version, latest_restorable_time, multi_az, storage_encrypted, kms_key_id, db_cluster_resource_id, arn, associated_roles, vpc_security_groups, db_subnet_group, cluster_create_time, enabled_cloudwatch_logs_exports, deletion_protection, tags from aws_docdb_cluster where region = '{self.region}'",
                "database_docdb_clusters.json"
            ),
            
            # Neptune 클러스터
            (
                "Neptune 클러스터",
                f"select db_cluster_identifier, cluster_members, backup_retention_period, preferred_backup_window, preferred_maintenance_window, port, master_username, engine, engine_version, latest_restorable_time, multi_az, storage_encrypted, kms_key_id, db_cluster_resource_id, db_cluster_arn, associated_roles, vpc_security_groups, db_subnet_group_name, activity_stream_mode, activity_stream_status, activity_stream_kms_key_id, activity_stream_kinesis_stream_name, cluster_create_time, copy_tags_to_snapshot, cross_account_clone, enabled_cloudwatch_logs_exports, deletion_protection, tags from aws_neptune_cluster where region = '{self.region}'",
                "database_neptune_clusters.json"
            ),
            
            # MemoryDB 클러스터
            (
                "MemoryDB 클러스터",
                f"select name, description, status, pending_updates, number_of_shards, cluster_endpoint, node_type, engine_version, engine_patch_version, parameter_group_name, parameter_group_status, security_groups, subnet_group_name, tls_enabled, kms_key_id, arn, sns_topic_arn, sns_topic_status, snapshot_retention_limit, maintenance_window, snapshot_window, acl_name, auto_minor_version_upgrade, data_tiering from aws_memorydb_cluster where region = '{self.region}'",
                "database_memorydb_clusters.json"
            ),
            
            # DAX 클러스터
            (
                "DAX 클러스터",
                f"select cluster_name, description, arn, total_nodes, active_nodes, node_type, status, cluster_discovery_endpoint, node_ids_to_remove, nodes, preferred_maintenance_window, notification_configuration, subnet_group, security_groups, iam_role_arn, parameter_group, sse_description, cluster_endpoint_encryption_type, tags from aws_dax_cluster where region = '{self.region}'",
                "database_dax_clusters.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("🗄️ 데이터베이스 리소스 수집 시작...")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 쿼리 실행
        queries = self.get_database_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("데이터베이스 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("database_*.json")):
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
    collector = SteampipeDatabaseCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
