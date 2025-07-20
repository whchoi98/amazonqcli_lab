#!/usr/bin/env python3
"""
완전한 데이터베이스 리소스 데이터 수집 스크립트 (RDS, NoSQL, 분석 서비스 포함)
Shell 스크립트와 동일한 기능 및 출력 형식 제공
"""

import os
import subprocess
import glob
from pathlib import Path
from typing import List, Tuple

class SteampipeDatabaseCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = None):
        # 스크립트의 실제 위치를 기준으로 경로 설정
        if report_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent
            report_dir = str(project_root / "aws-arch-analysis" / "report")
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_database_collection.log"
        self.error_log = self.report_dir / "steampipe_database_errors.log"
        
        # 로그 파일 초기화
        self.log_file.write_text("")
        self.error_log.write_text("")
        
        self.success_count = 0
        self.total_count = 0
        
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

    def log_rds(self, message: str):
        print(f"{self.PURPLE}[RDS]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[RDS] {message}\n")

    def log_nosql(self, message: str):
        print(f"{self.CYAN}[NoSQL]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[NoSQL] {message}\n")

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

    def get_rds_queries(self) -> List[Tuple[str, str, str]]:
        """RDS 기본 리소스 쿼리 (실제 스키마 기준)"""
        return [
            (
                "RDS DB 인스턴스",
                f"select db_instance_identifier, class, engine, engine_version, status, allocated_storage, storage_type, storage_encrypted, multi_az, publicly_accessible, vpc_security_groups, db_subnet_group_name, backup_retention_period, preferred_backup_window, preferred_maintenance_window, auto_minor_version_upgrade, deletion_protection, tags from aws_rds_db_instance where region = '{self.region}'",
                "database_rds_instances.json"
            ),
            (
                "RDS DB 클러스터",
                f"select db_cluster_identifier, engine, engine_version, database_name, members, vpc_security_groups, db_subnet_group, backup_retention_period, preferred_backup_window, preferred_maintenance_window, multi_az, storage_encrypted, kms_key_id, endpoint, reader_endpoint, status, deletion_protection, tags from aws_rds_db_cluster where region = '{self.region}'",
                "database_rds_clusters.json"
            ),
            (
                "RDS 서브넷 그룹",
                f"select name, description, vpc_id, status, subnets, tags from aws_rds_db_subnet_group where region = '{self.region}'",
                "database_rds_subnet_groups.json"
            ),
            (
                "RDS 파라미터 그룹",
                f"select name, description, db_parameter_group_family, tags from aws_rds_db_parameter_group where region = '{self.region}'",
                "database_rds_parameter_groups.json"
            ),
            (
                "RDS 스냅샷",
                f"select db_snapshot_identifier, db_instance_identifier, create_time, engine, allocated_storage, status, encrypted, kms_key_id, tags from aws_rds_db_snapshot where region = '{self.region}'",
                "database_rds_snapshots.json"
            )
        ]

    def get_dynamodb_queries(self) -> List[Tuple[str, str, str]]:
        """DynamoDB 관련 리소스 쿼리 (실제 스키마 기준)"""
        return [
            (
                "DynamoDB 테이블",
                f"select name, table_status, creation_date_time, billing_mode, read_capacity, write_capacity, stream_specification, deletion_protection_enabled, table_size_bytes, item_count, tags from aws_dynamodb_table where region = '{self.region}'",
                "database_dynamodb_tables.json"
            ),
            (
                "DynamoDB 백업",
                f"select name, table_name, backup_status, backup_type, backup_creation_datetime, backup_size_bytes from aws_dynamodb_backup where region = '{self.region}'",
                "database_dynamodb_backups.json"
            )
        ]

    def get_elasticache_queries(self) -> List[Tuple[str, str, str]]:
        """ElastiCache 관련 리소스 쿼리 (실제 스키마 기준)"""
        return [
            (
                "ElastiCache 클러스터",
                f"select cache_cluster_id, cache_node_type, engine, engine_version, cache_cluster_status, num_cache_nodes, preferred_availability_zone, cache_cluster_create_time, preferred_maintenance_window, auto_minor_version_upgrade, security_groups, replication_group_id from aws_elasticache_cluster where region = '{self.region}'",
                "database_elasticache_clusters.json"
            ),
            (
                "ElastiCache 복제 그룹",
                f"select replication_group_id, description, status, member_clusters, automatic_failover, multi_az, cache_node_type, auth_token_enabled, transit_encryption_enabled, at_rest_encryption_enabled from aws_elasticache_replication_group where region = '{self.region}'",
                "database_elasticache_replication_groups.json"
            )
        ]

    def get_warehouse_queries(self) -> List[Tuple[str, str, str]]:
        """데이터 웨어하우스 관련 리소스 쿼리 (실제 스키마 기준)"""
        return [
            (
                "Redshift 클러스터",
                f"select cluster_identifier, node_type, cluster_status, master_username, db_name, endpoint, cluster_create_time, number_of_nodes, publicly_accessible, encrypted, vpc_id, tags from aws_redshift_cluster where region = '{self.region}'",
                "database_redshift_clusters.json"
            ),
            (
                "OpenSearch 도메인",
                f"select domain_name, engine_version, endpoint, processing, created, deleted, cluster_config, ebs_options, vpc_options, encryption_at_rest_options, tags from aws_opensearch_domain where region = '{self.region}'",
                "database_opensearch_domains.json"
            )
        ]

    def get_bigdata_queries(self) -> List[Tuple[str, str, str]]:
        """빅데이터 처리 관련 리소스 쿼리 (실제 스키마 기준)"""
        return [
            (
                "EMR 클러스터",
                f"select id, name, status, ec2_instance_attributes, log_uri, release_label, auto_terminate, termination_protected, applications, service_role, tags from aws_emr_cluster where region = '{self.region}'",
                "database_emr_clusters.json"
            ),
            (
                "Kinesis 스트림",
                f"select stream_name, stream_status, retention_period_hours, open_shard_count, stream_creation_timestamp, encryption_type, tags from aws_kinesis_stream where region = '{self.region}'",
                "database_kinesis_streams.json"
            ),
            (
                "Glue 데이터베이스",
                f"select name, description, location_uri, create_time from aws_glue_catalog_database where region = '{self.region}'",
                "database_glue_databases.json"
            ),
            (
                "Athena 워크그룹",
                f"select name, description, state, creation_time, output_location, encryption_option from aws_athena_workgroup where region = '{self.region}'",
                "database_athena_workgroups.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("🗄️ 완전한 데이터베이스 리소스 데이터 수집 시작 (RDS, NoSQL, 분석 서비스 포함)")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # RDS 리소스 수집
        self.log_rds("🏛️ RDS 인스턴스 및 클러스터 수집 시작...")
        rds_queries = self.get_rds_queries()
        for description, query, output_file in rds_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # DynamoDB 리소스 수집
        self.log_nosql("🔥 DynamoDB 리소스 수집 시작...")
        dynamodb_queries = self.get_dynamodb_queries()
        for description, query, output_file in dynamodb_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # ElastiCache 리소스 수집
        self.log_nosql("⚡ ElastiCache 리소스 수집 시작...")
        elasticache_queries = self.get_elasticache_queries()
        for description, query, output_file in elasticache_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 데이터 웨어하우스 서비스 수집
        self.log_info("🏢 데이터 웨어하우스 서비스 수집 시작...")
        warehouse_queries = self.get_warehouse_queries()
        for description, query, output_file in warehouse_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 빅데이터 처리 서비스 수집
        self.log_info("🚀 빅데이터 처리 서비스 수집 시작...")
        bigdata_queries = self.get_bigdata_queries()
        for description, query, output_file in bigdata_queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("완전한 데이터베이스 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # Shell 스크립트와 동일한 출력 형식
        self.display_file_list()
        self.display_statistics()
        self.display_error_summary()
        self.display_next_steps()
        
        self.log_info("🎉 완전한 데이터베이스 리소스 데이터 수집이 완료되었습니다!")

    def display_file_list(self):
        """생성된 파일 목록 표시 (Shell 스크립트와 동일한 형식)"""
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        
        # 데이터베이스 관련 파일들 검색
        files_found = list(self.report_dir.glob("database_*.json"))
        files_found.sort()
        
        for file_path in files_found:
            file_size = file_path.stat().st_size
            if file_size > 100:
                print(f"{self.GREEN}✓ {file_path.name} ({file_size} bytes){self.NC}")
            else:
                print(f"{self.YELLOW}⚠ {file_path.name} ({file_size} bytes) - 데이터 없음{self.NC}")

    def display_statistics(self):
        """수집 통계 표시 (Shell 스크립트와 동일한 형식)"""
        print(f"\n{self.BLUE}📊 수집 통계:{self.NC}")
        print(f"총 쿼리 수: {self.total_count}")
        print(f"성공한 쿼리: {self.success_count}")
        print(f"실패한 쿼리: {self.total_count - self.success_count}")
        
        # 카테고리별 수집 현황
        print(f"\n{self.BLUE}📋 카테고리별 수집 현황:{self.NC}")
        print("🏛️  RDS 리소스: 5개")
        print("🔥 DynamoDB: 2개")
        print("⚡ ElastiCache: 2개")
        print("🏢 데이터 웨어하우스: 2개")
        print("🚀 빅데이터 처리: 4개")
        print("📊 총 리소스 타입: 15개")

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
        """다음 단계 안내 (Shell 스크립트와 동일)"""
        print(f"\n{self.YELLOW}💡 다음 단계:{self.NC}")
        print("1. 수집된 완전한 데이터베이스 데이터를 바탕으로 상세 분석 진행")
        print("2. RDS 인스턴스 성능 및 비용 최적화 분석")
        print("3. DynamoDB 테이블 구성 및 성능 검토")
        print("4. ElastiCache 클러스터 최적화 분석")
        print("5. 데이터 웨어하우스 및 분석 서비스 활용도 분석")
        print("6. 빅데이터 처리 파이프라인 최적화")
        print("7. 데이터베이스 백업 및 보안 설정 종합 검토")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="완전한 데이터베이스 리소스 데이터 수집 (RDS, NoSQL, 분석 서비스 포함)")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    # 스크립트의 실제 위치를 기준으로 기본 경로 설정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    default_report_dir = str(project_root / "aws-arch-analysis" / "report")
    
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", default_report_dir), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeDatabaseCollector(args.region, args.report_dir)
    collector.collect_data()

if __name__ == "__main__":
    main()
