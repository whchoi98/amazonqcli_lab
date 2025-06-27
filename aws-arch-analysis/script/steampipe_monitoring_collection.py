#!/usr/bin/env python3
"""
AWS 모니터링 및 로깅 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeMonitoringCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        self.report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "monitoring_collection_errors.log"
        
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
            
            # echo 명령어 처리 (빈 배열 반환용)
            if query.startswith("echo"):
                result_stdout = "[]"
            else:
                result = subprocess.run(
                    ["steampipe", "query", query, "--output", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                result_stdout = result.stdout
            
            output_path = self.report_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result_stdout)
            
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

    def get_monitoring_queries(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 쿼리 구조 사용"""
        return [
            # CloudWatch 알람 상세 정보
            (
                "CloudWatch 알람 상세 정보",
                f"select name, arn, alarm_description, alarm_configuration_updated_timestamp, actions_enabled, ok_actions, alarm_actions, insufficient_data_actions, state_value, state_reason, state_reason_data, state_updated_timestamp, metric_name, namespace, statistic, extended_statistic, dimensions, period, evaluation_periods, datapoints_to_alarm, threshold, comparison_operator, treat_missing_data, evaluate_low_sample_count_percentile, metrics, tags from aws_cloudwatch_alarm where region = '{self.region}'",
                "monitoring_cloudwatch_alarms.json"
            ),
            
            # CloudWatch 로그 그룹 상세 정보
            (
                "CloudWatch 로그 그룹 상세 정보",
                f"select name, arn, creation_time, retention_in_days, metric_filter_count, stored_bytes, kms_key_id, tags from aws_cloudwatch_log_group where region = '{self.region}'",
                "monitoring_cloudwatch_log_groups.json"
            ),
            
            # CloudWatch 로그 스트림
            (
                "CloudWatch 로그 스트림",
                f"select arn, log_group_name, name, creation_time, first_event_timestamp, last_event_timestamp, last_ingestion_time, upload_sequence_token from aws_cloudwatch_log_stream where region = '{self.region}'",
                "monitoring_cloudwatch_log_streams.json"
            ),
            
            # CloudWatch 메트릭 필터
            (
                "CloudWatch 메트릭 필터",
                f"select name, log_group_name, filter_pattern, metric_transformation_name, metric_transformation_namespace, metric_transformation_value, creation_time from aws_cloudwatch_log_metric_filter where region = '{self.region}'",
                "monitoring_cloudwatch_metric_filters.json"
            ),
            
            # CloudWatch 대시보드 - 빈 배열 반환
            (
                "CloudWatch 대시보드",
                "echo '[]'",
                "monitoring_cloudwatch_dashboards.json"
            ),
            
            # CloudWatch Insights 쿼리 - 빈 배열 반환
            (
                "CloudWatch Insights 쿼리",
                "echo '[]'",
                "monitoring_cloudwatch_insights_queries.json"
            ),
            
            # CloudWatch 복합 알람 - 빈 배열 반환
            (
                "CloudWatch 복합 알람",
                "echo '[]'",
                "monitoring_cloudwatch_composite_alarms.json"
            ),
            
            # X-Ray 추적 구성 - 빈 배열 반환
            (
                "X-Ray 추적 구성",
                "echo '[]'",
                "monitoring_xray_tracing_config.json"
            ),
            
            # X-Ray 서비스 맵 - 빈 배열 반환
            (
                "X-Ray 서비스 맵",
                "echo '[]'",
                "monitoring_xray_services.json"
            ),
            
            # X-Ray 암호화 구성 - 빈 배열 반환
            (
                "X-Ray 암호화 구성",
                "echo '[]'",
                "monitoring_xray_encryption_config.json"
            ),
            
            # CloudWatch Application Insights 애플리케이션 - 빈 배열 반환
            (
                "CloudWatch Application Insights 애플리케이션",
                "echo '[]'",
                "monitoring_application_insights.json"
            ),
            
            # CloudWatch Container Insights - 빈 배열 반환
            (
                "CloudWatch Container Insights",
                "echo '[]'",
                "monitoring_container_insights.json"
            ),
            
            # CloudWatch Synthetics Canary - 빈 배열 반환
            (
                "CloudWatch Synthetics Canary",
                "echo '[]'",
                "monitoring_synthetics_canaries.json"
            ),
            
            # CloudWatch RUM 앱 모니터 - 빈 배열 반환
            (
                "CloudWatch RUM 앱 모니터",
                "echo '[]'",
                "monitoring_rum_app_monitors.json"
            ),
            
            # CloudWatch Evidently 프로젝트 - 빈 배열 반환
            (
                "CloudWatch Evidently 프로젝트",
                "echo '[]'",
                "monitoring_evidently_projects.json"
            ),
            
            # AWS Systems Manager OpsCenter OpsItems - 빈 배열 반환
            (
                "AWS Systems Manager OpsCenter OpsItems",
                "echo '[]'",
                "monitoring_ssm_ops_items.json"
            ),
            
            # AWS Personal Health Dashboard 이벤트
            (
                "AWS Personal Health Dashboard 이벤트",
                f"select arn, service, event_type_code, event_type_category, region, availability_zone, start_time, end_time, last_updated_time, status_code, event_scope_code from aws_health_event where region = '{self.region}'",
                "monitoring_health_events.json"
            ),
            
            # AWS Cost and Usage Reports - 빈 배열 반환
            (
                "AWS Cost and Usage Reports",
                "echo '[]'",
                "monitoring_cost_usage_reports.json"
            ),
            
            # AWS Budgets - 빈 배열 반환
            (
                "AWS Budgets",
                "echo '[]'",
                "monitoring_budgets.json"
            ),
            
            # AWS Cost Explorer 비용 카테고리 - 빈 배열 반환
            (
                "AWS Cost Explorer 비용 카테고리",
                "echo '[]'",
                "monitoring_cost_categories.json"
            ),
            
            # AWS Resource Groups - 빈 배열 반환
            (
                "AWS Resource Groups",
                "echo '[]'",
                "monitoring_resource_groups.json"
            ),
            
            # AWS Systems Manager Compliance - 빈 배열 반환
            (
                "AWS Systems Manager Compliance",
                "echo '[]'",
                "monitoring_ssm_compliance.json"
            ),
            
            # AWS Config 적합성 팩
            (
                "AWS Config 적합성 팩",
                f"select name, arn, conformance_pack_id, delivery_s3_bucket, delivery_s3_key_prefix, input_parameters, last_update_requested_time, created_by from aws_config_conformance_pack where region = '{self.region}'",
                "monitoring_config_conformance_packs.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("📊 모니터링 및 로깅 리소스 수집 시작...")
        
        # Steampipe 플러그인 확인
        self.check_steampipe_plugin()
        
        # 쿼리 실행
        queries = self.get_monitoring_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        # 결과 요약
        self.log_success("모니터링 및 로깅 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("monitoring_*.json")):
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
    collector = SteampipeMonitoringCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
