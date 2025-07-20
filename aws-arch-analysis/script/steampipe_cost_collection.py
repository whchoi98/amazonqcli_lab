#!/usr/bin/env python3
"""
AWS 비용 및 청구 리소스 데이터 수집 스크립트
Cost Explorer, Budgets, Savings Plans, CUR 등 모든 비용 관련 서비스 포함
"""

import os
import subprocess
import json
import glob
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class SteampipeCostCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = None):
        # 스크립트의 실제 위치를 기준으로 경로 설정
        if report_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent
            report_dir = str(project_root / "aws-arch-analysis" / "report")
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_cost_collection.log"
        self.error_log = self.report_dir / "steampipe_cost_errors.log"
        
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

    def log_category(self, category: str, message: str):
        print(f"{self.PURPLE}[{category}]{self.NC} {message}")
        with open(self.log_file, 'a') as f:
            f.write(f"[{category}] {message}\n")

    def check_steampipe(self) -> bool:
        """Steampipe 설치 및 AWS 플러그인 확인"""
        try:
            # Steampipe 설치 확인
            result = subprocess.run(['steampipe', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.log_info("Steampipe 설치 확인됨")
            
            # AWS 플러그인 확인
            result = subprocess.run(['steampipe', 'plugin', 'list'], 
                                  capture_output=True, text=True, check=True)
            if 'aws' not in result.stdout:
                self.log_warning("AWS 플러그인이 설치되지 않았습니다. 설치 중...")
                subprocess.run(['steampipe', 'plugin', 'install', 'aws'], check=True)
            
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_error("Steampipe가 설치되지 않았거나 AWS 플러그인을 찾을 수 없습니다.")
            print(f"{self.YELLOW}💡 Steampipe 설치 방법:{self.NC}")
            print("sudo /bin/sh -c \"$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)\"")
            print("steampipe plugin install aws")
            return False

    def execute_steampipe_query(self, description: str, query: str, output_file: str) -> bool:
        """Steampipe 쿼리 실행"""
        self.log_info(f"수집 중: {description}")
        
        try:
            # 출력 파일 경로
            output_path = self.report_dir / output_file
            
            # Steampipe 쿼리 실행
            result = subprocess.run([
                'steampipe', 'query', query, '--output', 'json'
            ], capture_output=True, text=True, cwd=self.report_dir)
            
            if result.returncode == 0:
                # 결과를 파일에 저장
                with open(output_path, 'w') as f:
                    f.write(result.stdout)
                
                # 파일 크기 확인
                file_size = output_path.stat().st_size
                
                if file_size > 50:  # 50바이트 이상이면 데이터가 있다고 판단
                    self.log_success(f"{description} 완료 ({output_file}, {file_size} bytes)")
                    return True
                else:
                    self.log_warning(f"{description} - 데이터 없음 ({output_file}, {file_size} bytes)")
                    return False
            else:
                self.log_error(f"{description} 실패 - {output_file}: {result.stderr}")
                with open(self.error_log, 'a') as f:
                    f.write(f"Query failed: {query}\n")
                    f.write(f"Error: {result.stderr}\n\n")
                return False
                
        except Exception as e:
            self.log_error(f"{description} 실행 중 오류: {str(e)}")
            return False

    def get_billing_queries(self) -> List[Tuple[str, str, str]]:
        """청구 및 계정 관련 쿼리 (실제 사용 가능한 테이블 기준)"""
        return [
            (
                "계정별 월간 비용",
                "select linked_account_id, linked_account_name, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_account_monthly order by period_start desc limit 12",
                "cost_by_account_monthly.json"
            ),
            (
                "계정별 일간 비용",
                "select linked_account_id, linked_account_name, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_account_daily order by period_start desc limit 30",
                "cost_by_account_daily.json"
            )
        ]

    def get_cost_explorer_queries(self) -> List[Tuple[str, str, str]]:
        """Cost Explorer 관련 쿼리 (실제 사용 가능한 테이블 기준)"""
        return [
            (
                "서비스별 월간 비용",
                "select service, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_service_monthly order by period_start desc, blended_cost_amount desc limit 50",
                "cost_by_service_monthly.json"
            ),
            (
                "서비스별 일간 비용",
                "select service, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_service_daily order by period_start desc, blended_cost_amount desc limit 100",
                "cost_by_service_daily.json"
            ),
            (
                "리소스별 월간 비용",
                "select resource_id, service, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_resource_monthly order by period_start desc, blended_cost_amount desc limit 50",
                "cost_by_resource_monthly.json"
            ),
            (
                "리소스별 일간 비용",
                "select resource_id, service, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_resource_daily order by period_start desc, blended_cost_amount desc limit 100",
                "cost_by_resource_daily.json"
            ),
            (
                "태그별 비용",
                "select tag_key, tag_value, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_tag order by period_start desc, blended_cost_amount desc limit 50",
                "cost_by_tag.json"
            )
        ]

    def get_budgets_queries(self) -> List[Tuple[str, str, str]]:
        """비용 예측 및 사용량 관련 쿼리"""
        return [
            (
                "월간 비용 예측",
                "select period_start, period_end, mean_value, prediction_interval_lower_bound, prediction_interval_upper_bound from aws_cost_forecast_monthly order by period_start desc limit 12",
                "cost_forecast_monthly.json"
            ),
            (
                "일간 비용 예측",
                "select period_start, period_end, mean_value, prediction_interval_lower_bound, prediction_interval_upper_bound from aws_cost_forecast_daily order by period_start desc limit 30",
                "cost_forecast_daily.json"
            ),
            (
                "비용 사용량 상세",
                "select service, usage_type, operation, availability_zone, resource_id, usage_start_date, usage_end_date, usage_quantity, blended_rate, blended_cost, unblended_rate, unblended_cost from aws_cost_usage order by usage_start_date desc limit 100",
                "cost_usage_details.json"
            )
        ]

    def get_cur_queries(self) -> List[Tuple[str, str, str]]:
        """비용 최적화 및 레코드 타입별 분석"""
        return [
            (
                "비용 최적화 권장사항",
                f"select recommendation_id, account_id, region, resource_arn, resource_id, resource_type, action_type, estimated_monthly_cost, estimated_monthly_savings, implementation_effort, last_refresh_timestamp, rollback_possible, source from aws_costoptimizationhub_recommendation where region = '{self.region}' limit 50",
                "cost_optimization_recommendations.json"
            ),
            (
                "레코드 타입별 월간 비용",
                "select record_type, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_record_type_monthly order by period_start desc limit 50",
                "cost_by_record_type_monthly.json"
            ),
            (
                "레코드 타입별 일간 비용",
                "select record_type, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_record_type_daily order by period_start desc limit 100",
                "cost_by_record_type_daily.json"
            )
        ]

    def get_savings_plans_queries(self) -> List[Tuple[str, str, str]]:
        """서비스 사용 타입별 비용 분석"""
        return [
            (
                "서비스 사용 타입별 월간 비용",
                "select service, usage_type, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_service_usage_type_monthly order by period_start desc, blended_cost_amount desc limit 100",
                "cost_by_service_usage_type_monthly.json"
            ),
            (
                "서비스 사용 타입별 일간 비용",
                "select service, usage_type, period_start, period_end, blended_cost_amount, blended_cost_unit, unblended_cost_amount, unblended_cost_unit from aws_cost_by_service_usage_type_daily order by period_start desc, blended_cost_amount desc limit 200",
                "cost_by_service_usage_type_daily.json"
            )
        ]

    def get_pricing_queries(self) -> List[Tuple[str, str, str]]:
        """가격 정보 관련 쿼리 (실제 스키마 기준)"""
        return [
            (
                "EC2 가격 정보",
                f"select service_code, sku, product_description, location, location_type, instance_type, vcpu, memory, storage, network_performance, operating_system, tenancy, pre_installed_sw, price_per_unit, currency, unit, price_description, effective_date from aws_pricing_product where service_code = 'AmazonEC2' and location = 'Asia Pacific (Seoul)' limit 20",
                "pricing_ec2.json"
            ),
            (
                "RDS 가격 정보",
                f"select service_code, sku, product_description, location, location_type, instance_type, vcpu, memory, storage_type, deployment_option, database_engine, license_model, price_per_unit, currency, unit, price_description from aws_pricing_product where service_code = 'AmazonRDS' and location = 'Asia Pacific (Seoul)' limit 20",
                "pricing_rds.json"
            ),
            (
                "가격 서비스 속성",
                "select service_code, attribute_name, attribute_value from aws_pricing_service_attribute where service_code in ('AmazonEC2', 'AmazonRDS', 'AmazonS3') limit 50",
                "pricing_service_attributes.json"
            )
        ]

    def collect_cost_data(self):
        """비용 관련 데이터 수집 실행"""
        self.log_info("💰 AWS 비용 및 청구 리소스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        # Steampipe 확인
        if not self.check_steampipe():
            return False
        
        # 계정별 비용 정보 수집
        self.log_category("ACCOUNT_COSTS", "💳 계정별 비용 정보 수집 시작...")
        billing_queries = self.get_billing_queries()
        for description, query, output_file in billing_queries:
            self.total_count += 1
            if self.execute_steampipe_query(description, query, output_file):
                self.success_count += 1
        
        # 서비스별 비용 분석 수집
        self.log_category("SERVICE_COSTS", "📊 서비스별 비용 분석 수집 시작...")
        ce_queries = self.get_cost_explorer_queries()
        for description, query, output_file in ce_queries:
            self.total_count += 1
            if self.execute_steampipe_query(description, query, output_file):
                self.success_count += 1
        
        # 비용 예측 및 사용량 수집
        self.log_category("FORECASTS", "🔮 비용 예측 및 사용량 데이터 수집 시작...")
        budget_queries = self.get_budgets_queries()
        for description, query, output_file in budget_queries:
            self.total_count += 1
            if self.execute_steampipe_query(description, query, output_file):
                self.success_count += 1
        
        # 비용 최적화 권장사항 수집
        self.log_category("OPTIMIZATION", "💡 비용 최적화 권장사항 수집 시작...")
        cur_queries = self.get_cur_queries()
        for description, query, output_file in cur_queries:
            self.total_count += 1
            if self.execute_steampipe_query(description, query, output_file):
                self.success_count += 1
        
        # 사용 타입별 비용 분석 수집
        self.log_category("USAGE_TYPES", "📈 사용 타입별 비용 분석 수집 시작...")
        savings_queries = self.get_savings_plans_queries()
        for description, query, output_file in savings_queries:
            self.total_count += 1
            if self.execute_steampipe_query(description, query, output_file):
                self.success_count += 1
        
        # 가격 정보 수집
        self.log_category("PRICING", "💲 AWS 서비스 가격 정보 수집 시작...")
        pricing_queries = self.get_pricing_queries()
        for description, query, output_file in pricing_queries:
            self.total_count += 1
            if self.execute_steampipe_query(description, query, output_file):
                self.success_count += 1
        
        return True

    def show_results(self):
        """수집 결과 표시"""
        self.log_success("AWS 비용 및 청구 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        cost_files = list(self.report_dir.glob("cost_*.json"))
        cost_files.sort()
        
        for file_path in cost_files:
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
        
        # 카테고리별 수집 현황
        print(f"\n{self.BLUE}📋 카테고리별 수집 현황:{self.NC}")
        print("💳 계정별 비용: 2개")
        print("📊 서비스별 비용 분석: 5개")
        print("🔮 비용 예측 및 사용량: 3개")
        print("💡 비용 최적화: 3개")
        print("📈 사용 타입별 분석: 2개")
        print("💲 가격 정보: 3개")
        print(f"📊 총 리소스 타입: {self.total_count}개")
        
        # 오류 로그 확인
        if self.error_log.exists() and self.error_log.stat().st_size > 0:
            self.log_warning(f"오류가 발생했습니다. {self.error_log.name} 파일을 확인하세요.")
            print(f"\n{self.YELLOW}최근 오류 (마지막 5줄):{self.NC}")
            try:
                with open(self.error_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(line.strip())
            except:
                pass
        
        # 다음 단계 안내
        print(f"\n{self.YELLOW}💡 다음 단계:{self.NC}")
        print("1. 수집된 비용 데이터를 바탕으로 비용 최적화 분석 진행")
        print("2. 예산 설정 및 비용 알림 구성 검토")
        print("3. Savings Plans 및 Reserved Instance 활용 분석")
        print("4. Cost Explorer를 통한 비용 트렌드 분석")
        print("5. 이상 비용 탐지 및 알림 설정 검토")
        print("6. CUR 보고서를 통한 상세 비용 분석")
        print("7. 서비스별 비용 최적화 기회 식별")
        
        self.log_info("🎉 AWS 비용 및 청구 리소스 데이터 수집이 완료되었습니다!")

def main():
    """메인 함수"""
    try:
        # 비용 데이터 수집기 초기화
        collector = SteampipeCostCollector()
        
        # 데이터 수집 실행
        if collector.collect_cost_data():
            # 결과 표시
            collector.show_results()
        else:
            print("❌ 데이터 수집 중 오류가 발생했습니다.")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
