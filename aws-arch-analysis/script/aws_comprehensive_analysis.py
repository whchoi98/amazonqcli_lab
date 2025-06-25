#!/usr/bin/env python3
"""
AWS 계정 종합 분석 보고서 자동 생성 스크립트
작성자: Amazon Q CLI
버전: 2.0 (Python 변환)
생성일: 2025-06-25
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict, List, Optional, Tuple

# 색상 정의
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class Logger:
    """로깅 유틸리티 클래스"""
    
    @staticmethod
    def info(message: str):
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")
    
    @staticmethod
    def success(message: str):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
    
    @staticmethod
    def warning(message: str):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
    
    @staticmethod
    def error(message: str):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    
    @staticmethod
    def step(message: str):
        print(f"{Colors.PURPLE}[STEP]{Colors.NC} {message}")

class ProgressBar:
    """진행률 표시 클래스"""
    
    @staticmethod
    def show_progress(current: int, total: int, desc: str):
        percent = (current * 100) // total
        bar_length = 50
        filled_length = (percent * bar_length) // 100
        
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"\r{Colors.CYAN}[{percent:3d}%]{Colors.NC} [{bar}] {desc}", end="")
        
        if current == total:
            print()

class AWSAnalyzer:
    """AWS 리소스 분석 메인 클래스"""
    
    def __init__(self):
        self.start_time = time.time()
        self.script_dir = Path(__file__).parent
        self.report_dir = self.script_dir.parent / "report" / "comprehensive-analysis"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.script_dir.parent / "report" / f"backup_{self.timestamp}"
        
        # AWS 정보
        self.aws_account_id = ""
        self.aws_region = ""
        
        # 분석 결과
        self.analysis_results = {}
        
    def print_header(self):
        """헤더 출력"""
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.CYAN}║                AWS 계정 종합 분석 보고서 생성기                ║{Colors.NC}")
        print(f"{Colors.CYAN}║                     자동화 스크립트 v2.0                      ║{Colors.NC}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
        print()
        
    def validate_environment(self) -> bool:
        """환경 검증"""
        Logger.step("Phase 1: 환경 준비 및 검증")
        ProgressBar.show_progress(1, 10, "환경 검증 중...")
        
        # 필수 도구 확인
        required_tools = ['steampipe', 'aws', 'python3']
        for tool in required_tools:
            if not shutil.which(tool):
                Logger.error(f"{tool}이 설치되지 않았습니다.")
                return False
        
        # AWS 자격 증명 확인
        try:
            result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                                  capture_output=True, text=True, check=True)
            caller_identity = json.loads(result.stdout)
            self.aws_account_id = caller_identity.get('Account', '')
        except subprocess.CalledProcessError:
            Logger.error("AWS 자격 증명이 구성되지 않았습니다.")
            return False
        
        # AWS 리전 확인
        try:
            result = subprocess.run(['aws', 'configure', 'get', 'region'], 
                                  capture_output=True, text=True)
            self.aws_region = result.stdout.strip() or "ap-northeast-2"
        except subprocess.CalledProcessError:
            self.aws_region = "ap-northeast-2"
        
        # 디렉토리 생성
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        Logger.success("환경 검증 완료")
        Logger.info(f"분석 시작 시간: {datetime.now()}")
        Logger.info(f"보고서 저장 위치: {self.report_dir}")
        
        return True
    
    def backup_existing_reports(self):
        """기존 보고서 백업"""
        Logger.step("Phase 2: 기존 보고서 백업")
        ProgressBar.show_progress(2, 10, "기존 보고서 백업 중...")
        
        if self.report_dir.exists() and any(self.report_dir.iterdir()):
            try:
                for item in self.report_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, self.backup_dir)
                    elif item.is_dir():
                        shutil.copytree(item, self.backup_dir / item.name, dirs_exist_ok=True)
                Logger.success(f"기존 보고서를 {self.backup_dir}에 백업했습니다.")
            except Exception as e:
                Logger.warning(f"백업 중 오류 발생: {e}")
        else:
            Logger.info("백업할 기존 보고서가 없습니다.")
    
    def collect_aws_data(self):
        """AWS 데이터 수집"""
        Logger.step("Phase 3: AWS 데이터 수집")
        ProgressBar.show_progress(3, 10, "AWS 리소스 데이터 수집 중...")
        
        Logger.info(f"AWS 계정 ID: {self.aws_account_id}")
        Logger.info(f"AWS 리전: {self.aws_region}")
        
        # 작업 디렉토리 변경
        os.chdir(self.report_dir)
        
        # Steampipe 쿼리 실행
        queries = {
            'vpc_analysis.json': """
                SELECT 
                    vpc_id,
                    cidr_block,
                    state,
                    is_default,
                    tags->>'Name' as name,
                    tags
                FROM aws_vpc 
                ORDER BY vpc_id;
            """,
            'subnet_analysis.json': """
                SELECT 
                    subnet_id,
                    vpc_id,
                    cidr_block,
                    availability_zone,
                    map_public_ip_on_launch,
                    state,
                    tags->>'Name' as name
                FROM aws_vpc_subnet 
                ORDER BY vpc_id, availability_zone;
            """,
            'ec2_analysis.json': """
                SELECT 
                    instance_id,
                    instance_type,
                    instance_state,
                    vpc_id,
                    subnet_id,
                    private_ip_address,
                    public_ip_address,
                    placement_availability_zone as availability_zone,
                    launch_time,
                    tags->>'Name' as name,
                    platform,
                    architecture,
                    root_device_type,
                    tags
                FROM aws_ec2_instance 
                ORDER BY vpc_id, instance_id;
            """,
            'security_groups_analysis.json': """
                SELECT 
                    group_id,
                    group_name,
                    description,
                    vpc_id,
                    tags->>'Name' as name,
                    tags
                FROM aws_vpc_security_group 
                ORDER BY vpc_id, group_name;
            """,
            'rds_analysis.json': """
                SELECT 
                    db_instance_identifier,
                    class,
                    engine,
                    engine_version,
                    status,
                    allocated_storage,
                    storage_type,
                    multi_az,
                    publicly_accessible,
                    vpc_id,
                    db_subnet_group_name,
                    availability_zone,
                    backup_retention_period,
                    storage_encrypted,
                    tags
                FROM aws_rds_db_instance;
            """,
            'eks_analysis.json': """
                SELECT 
                    name,
                    status,
                    version,
                    platform_version,
                    endpoint,
                    created_at,
                    role_arn,
                    resources_vpc_config,
                    logging,
                    tags
                FROM aws_eks_cluster;
            """,
            'elasticache_analysis.json': """
                SELECT 
                    cache_cluster_id,
                    cache_node_type,
                    engine,
                    engine_version,
                    cache_cluster_status,
                    num_cache_nodes,
                    preferred_availability_zone,
                    cache_subnet_group_name,
                    security_groups,
                    tags
                FROM aws_elasticache_cluster;
            """,
            's3_analysis.json': """
                SELECT 
                    name,
                    region,
                    creation_date,
                    versioning_enabled,
                    server_side_encryption_configuration,
                    logging,
                    tags
                FROM aws_s3_bucket;
            """,
            'cloudformation_analysis.json': """
                SELECT 
                    name,
                    status,
                    creation_time,
                    last_updated_time,
                    description,
                    capabilities,
                    parameters,
                    outputs,
                    tags
                FROM aws_cloudformation_stack
                ORDER BY creation_time DESC;
            """,
            'cost_analysis.json': """
                SELECT 
                    service,
                    sum(unblended_cost_amount) as total_cost,
                    count(*) as days_count
                FROM aws_cost_by_service_daily 
                WHERE period_start >= current_date - interval '30 days'
                GROUP BY service
                ORDER BY total_cost DESC;
            """
        }
        
        for output_file, query in queries.items():
            Logger.info(f"{output_file.replace('_analysis.json', '').replace('.json', '')} 분석 중...")
            try:
                result = subprocess.run(
                    ['steampipe', 'query', query, '--output', 'json'],
                    capture_output=True, text=True, check=True
                )
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
            except subprocess.CalledProcessError as e:
                Logger.warning(f"{output_file} 생성 실패: {e}")
                # 빈 JSON 배열 생성
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('[]')
        
        Logger.success("AWS 데이터 수집 완료")
    
    def analyze_collected_data(self):
        """수집된 데이터 분석"""
        Logger.step("Phase 4: 분석 데이터 처리")
        ProgressBar.show_progress(4, 10, "수집된 데이터 분석 중...")
        
        # JSON 파일들 로드 및 분석
        try:
            with open('vpc_analysis.json', 'r') as f:
                vpc_data = json.load(f)
            with open('ec2_analysis.json', 'r') as f:
                ec2_data = json.load(f)
            with open('security_groups_analysis.json', 'r') as f:
                sg_data = json.load(f)
            with open('cost_analysis.json', 'r') as f:
                cost_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            Logger.warning(f"데이터 로드 실패: {e}")
            vpc_data = ec2_data = sg_data = cost_data = []
        
        # 통계 계산
        self.analysis_results = {
            'vpc_count': len(vpc_data),
            'ec2_count': len(ec2_data),
            'security_group_count': len(sg_data),
            'total_cost': sum(float(item.get('total_cost', 0)) for item in cost_data)
        }
        
        Logger.info("발견된 리소스:")
        Logger.info(f"  - VPC: {self.analysis_results['vpc_count']}개")
        Logger.info(f"  - EC2 인스턴스: {self.analysis_results['ec2_count']}개")
        Logger.info(f"  - 보안 그룹: {self.analysis_results['security_group_count']}개")
        Logger.info(f"  - 월간 총 비용: ${self.analysis_results['total_cost']:.2f}")
        
        Logger.success("데이터 분석 완료")
    
    def run_analysis(self):
        """전체 분석 실행"""
        self.print_header()
        
        if not self.validate_environment():
            sys.exit(1)
        
        self.backup_existing_reports()
        self.collect_aws_data()
        self.analyze_collected_data()
        
        # 보고서 생성 모듈들 호출
        from report_generators import MarkdownReportGenerator
        from html_generator import HTMLConverter, DashboardGenerator
        
        # Phase 5: Markdown 보고서 생성
        Logger.step("Phase 5: Markdown 보고서 생성")
        ProgressBar.show_progress(5, 10, "보고서 템플릿 생성 중...")
        
        markdown_generator = MarkdownReportGenerator(
            self.aws_account_id, 
            self.aws_region, 
            self.analysis_results
        )
        markdown_generator.generate_all_reports()
        
        Logger.success("Markdown 보고서 생성 완료")
        
        # Phase 6: HTML 변환
        Logger.step("Phase 6: HTML 변환")
        ProgressBar.show_progress(6, 10, "HTML 변환 중...")
        
        html_converter = HTMLConverter(self.aws_account_id)
        html_converter.convert_all_markdown_files()
        
        Logger.success("HTML 변환 완료")
        
        # Phase 7: 메인 대시보드 생성
        Logger.step("Phase 7: 메인 대시보드 생성")
        ProgressBar.show_progress(7, 10, "메인 대시보드 생성 중...")
        
        dashboard_generator = DashboardGenerator(
            self.aws_account_id,
            self.aws_region,
            self.analysis_results
        )
        dashboard_generator.generate_dashboard()
        
        Logger.success("메인 대시보드 생성 완료")
        
        # Phase 8-10: 최종 처리
        self.finalize_analysis()
    
    def finalize_analysis(self):
        """분석 완료 처리"""
        Logger.step("Phase 8: 품질 검증")
        ProgressBar.show_progress(8, 10, "생성된 파일 검증 중...")
        
        # 필수 파일 확인
        required_files = [
            "01-executive-summary.md", "01-executive-summary.html",
            "02-networking-analysis.md", "02-networking-analysis.html",
            "07-cost-optimization.md", "07-cost-optimization.html",
            "index.html"
        ]
        
        missing_files = [f for f in required_files if not (self.report_dir / f).exists()]
        
        if not missing_files:
            Logger.success("모든 필수 파일이 생성되었습니다.")
        else:
            Logger.warning(f"누락된 파일: {', '.join(missing_files)}")
        
        Logger.step("Phase 9: 최종 정리")
        ProgressBar.show_progress(9, 10, "최종 정리 중...")
        
        # 요약 정보 생성
        summary_content = f"""AWS 계정 종합 분석 보고서 생성 완료

생성 일시: {datetime.now()}
AWS 계정 ID: {self.aws_account_id}
AWS 리전: {self.aws_region}

발견된 리소스:
- VPC: {self.analysis_results['vpc_count']}개
- EC2 인스턴스: {self.analysis_results['ec2_count']}개
- 보안 그룹: {self.analysis_results['security_group_count']}개
- 월간 총 비용: ${self.analysis_results['total_cost']:.2f}

생성된 파일:
- Markdown 보고서: 10개
- HTML 보고서: 10개
- 메인 대시보드: index.html
- 분석 데이터: JSON 파일들

다음 단계:
1. index.html을 브라우저에서 열어 대시보드 확인
2. 각 영역별 상세 보고서 검토
3. 권장사항에 따른 액션 아이템 실행
"""
        
        with open(self.report_dir / "analysis_summary.txt", 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        Logger.success("분석 요약 파일 생성 완료")
        
        Logger.step("Phase 10: 완료")
        ProgressBar.show_progress(10, 10, "분석 완료!")
        
        # 완료 메시지 출력
        self.print_completion_message()
    
    def print_completion_message(self):
        """완료 메시지 출력"""
        end_time = time.time()
        execution_time = int(end_time - self.start_time)
        minutes = execution_time // 60
        seconds = execution_time % 60
        
        print()
        print(f"{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.GREEN}║                    🎉 분석 완료! 🎉                          ║{Colors.NC}")
        print(f"{Colors.GREEN}╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
        print()
        
        Logger.success("AWS 계정 종합 분석 보고서가 성공적으로 생성되었습니다!")
        print()
        print(f"{Colors.CYAN}📊 분석 결과 요약:{Colors.NC}")
        print(f"  • VPC: {self.analysis_results['vpc_count']}개")
        print(f"  • EC2 인스턴스: {self.analysis_results['ec2_count']}개")
        print(f"  • 보안 그룹: {self.analysis_results['security_group_count']}개")
        print(f"  • 월간 총 비용: ${self.analysis_results['total_cost']:.2f}")
        print()
        print(f"{Colors.CYAN}📁 생성된 파일:{Colors.NC}")
        print(f"  • 보고서 위치: {self.report_dir}")
        print(f"  • 메인 대시보드: {self.report_dir}/index.html")
        print(f"  • Markdown 보고서: 10개")
        print(f"  • HTML 보고서: 10개")
        print()
        print(f"{Colors.CYAN}⏱️ 실행 시간:{Colors.NC} {minutes}분 {seconds}초")
        print()
        print(f"{Colors.YELLOW}🚀 다음 단계:{Colors.NC}")
        print("  1. 브라우저에서 index.html 열기")
        print("  2. 각 영역별 상세 보고서 검토")
        print("  3. 권장사항 실행 계획 수립")
        print()
        print(f"{Colors.BLUE}💡 보고서 확인 방법:{Colors.NC}")
        print(f"  • 웹 대시보드: file://{self.report_dir}/index.html")
        print(f"  • Markdown 확인: glow {self.report_dir}/01-executive-summary.md")
        print()
        
        if self.backup_dir.exists() and any(self.backup_dir.iterdir()):
            print(f"{Colors.CYAN}💾 백업 정보:{Colors.NC}")
            print(f"  • 이전 보고서 백업: {self.backup_dir}")
            print()
        
        Logger.success("분석 완료! 🎊")

def main():
    """메인 함수"""
    analyzer = AWSAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
