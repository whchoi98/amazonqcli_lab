#!/usr/bin/env python3
"""
AWS IaC 분석 및 관리 리소스 데이터 수집 스크립트
Shell 스크립트와 동일한 쿼리 구조 사용
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timedelta

class SteampipeIaCCollector:
    def __init__(self, region: str = "ap-northeast-2"):
        self.region = region
        # 스크립트의 실제 위치를 기준으로 경로 설정
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self.report_dir = project_root / "aws-arch-analysis" / "report"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.total_count = 0
        self.success_count = 0
        self.error_log = self.report_dir / "iac_collection_errors.log"
        
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

    def execute_aws_command(self, description: str, command: str, output_file: str) -> bool:
        self.log_info(f"수집 중: {description}")
        self.total_count += 1
        
        try:
            # 작업 디렉토리를 report_dir로 변경
            os.chdir(self.report_dir)
            
            # 특별한 명령어 처리
            if "echo" in command:
                # echo 명령어는 직접 실행
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                # AWS CLI 명령어 실행
                result = subprocess.run(
                    command.split(),
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
                f.write(f"\nCommand failed: {command}\n")
                f.write(f"Error: {e.stderr}\n")
            
            return False

    def get_iac_commands(self) -> List[Tuple[str, str, str]]:
        """Shell 스크립트와 동일한 AWS CLI 명령어 구조 사용"""
        # 날짜 계산
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        return [
            # CloudFormation
            (
                "CloudFormation 스택 정보",
                f"aws cloudformation describe-stacks --region {self.region} --output json",
                "iac_cloudformation_stacks.json"
            ),
            
            # CloudFormation 스택 리소스 (첫 번째 스택이 있는 경우)
            (
                "CloudFormation 스택 리소스",
                f"aws cloudformation list-stack-resources --region {self.region} --stack-name dummy --output json 2>/dev/null || echo '[]'",
                "iac_cloudformation_resources.json"
            ),
            
            # CloudFormation 스택 이벤트
            (
                "CloudFormation 스택 이벤트",
                f"aws cloudformation describe-stack-events --region {self.region} --stack-name dummy --output json 2>/dev/null || echo '[]'",
                "iac_cloudformation_events.json"
            ),
            
            # AWS Config
            (
                "Config 구성 레코더",
                f"aws configservice describe-configuration-recorders --region {self.region} --output json",
                "iac_config_recorders.json"
            ),
            
            (
                "Config 규칙",
                f"aws configservice describe-config-rules --region {self.region} --output json",
                "iac_config_rules.json"
            ),
            
            (
                "Config 규정 준수",
                f"aws configservice describe-compliance-by-config-rule --region {self.region} --output json",
                "iac_config_compliance.json"
            ),
            
            # CloudTrail
            (
                "CloudTrail 정보",
                f"aws cloudtrail describe-trails --region {self.region} --output json",
                "iac_cloudtrail_trails.json"
            ),
            
            (
                "CloudTrail 이벤트 선택기",
                f"aws cloudtrail get-event-selectors --region {self.region} --trail-name dummy --output json 2>/dev/null || echo '{{}}'",
                "iac_cloudtrail_selectors.json"
            ),
            
            # Systems Manager
            (
                "SSM 파라미터",
                f"aws ssm describe-parameters --region {self.region} --output json",
                "iac_ssm_parameters.json"
            ),
            
            (
                "SSM 문서",
                f"aws ssm list-documents --region {self.region} --output json",
                "iac_ssm_documents.json"
            ),
            
            # Lambda (IaC 관련)
            (
                "Lambda 함수 목록",
                f"aws lambda list-functions --region {self.region} --output json",
                "iac_lambda_functions.json"
            ),
            
            # Cost Explorer (지난 30일)
            (
                "비용 분석",
                f"aws ce get-cost-and-usage --region us-east-1 --time-period Start={start_date},End={end_date} --granularity MONTHLY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE --output json",
                "iac_cost_analysis.json"
            ),
            
            # Organizations (조직 정보)
            (
                "조직 정보",
                "aws organizations describe-organization --region us-east-1 --output json 2>/dev/null || echo '{{}}'",
                "iac_organization_info.json"
            ),
            
            (
                "조직 계정",
                "aws organizations list-accounts --region us-east-1 --output json 2>/dev/null || echo '{{}}'",
                "iac_organization_accounts.json"
            )
        ]

    def collect_data(self):
        """데이터 수집 실행"""
        self.log_info("🏗️ Infrastructure as Code 분석 시작...")
        
        # 명령어 실행
        commands = self.get_iac_commands()
        for description, command, output_file in commands:
            self.execute_aws_command(description, command, output_file)
        
        # 결과 요약
        self.log_success("IaC 분석 및 관리 리소스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        # 파일 목록 및 크기 표시
        print(f"\n{self.BLUE}📁 생성된 파일 목록:{self.NC}")
        for file_path in sorted(self.report_dir.glob("iac_*.json")):
            file_size = file_path.stat().st_size
            if file_size > 100:
                print(f"{self.GREEN}✓ {file_path.name} ({file_size} bytes){self.NC}")
            else:
                print(f"{self.YELLOW}⚠ {file_path.name} ({file_size} bytes) - 데이터 없음{self.NC}")
        
        # 수집 통계
        print(f"\n{self.BLUE}📊 수집 통계:{self.NC}")
        print(f"총 명령어 수: {self.total_count}")
        print(f"성공한 명령어: {self.success_count}")
        print(f"실패한 명령어: {self.total_count - self.success_count}")
        print(f"성공률: {(self.success_count/self.total_count*100):.1f}%")
        
        if self.error_log.exists():
            print(f"\n{self.YELLOW}⚠️ 오류 로그: {self.error_log}{self.NC}")

def main():
    """메인 함수"""
    region = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-2')
    collector = SteampipeIaCCollector(region)
    collector.collect_data()

if __name__ == "__main__":
    main()
