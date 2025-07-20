#!/usr/bin/env python3
"""
AWS CLI 기반 애플리케이션 서비스 리소스 데이터 수집 스크립트
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class AWSApplicationCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = None):
        # 스크립트의 실제 위치를 기준으로 경로 설정
        if report_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent
            report_dir = str(project_root / "aws-arch-analysis" / "report")
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 로깅 설정
        self.setup_logging()
        
        # 성공/실패 카운터
        self.success_count = 0
        self.total_count = 0

    def setup_logging(self):
        """로깅 설정"""
        log_file = self.report_dir / "aws_cli_application_collection.log"
        error_log_file = self.report_dir / "aws_cli_application_errors.log"
        
        # 메인 로거
        self.logger = logging.getLogger('application_collector')
        self.logger.setLevel(logging.INFO)
        
        # 파일 핸들러
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # 에러 파일 핸들러
        self.error_logger = logging.getLogger('application_collector_errors')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        
        # 포맷터
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.error_logger.addHandler(error_handler)

    def log_info(self, message: str):
        """정보 로그"""
        print(f"\033[0;34m[INFO]\033[0m {message}")
        self.logger.info(message)

    def log_success(self, message: str):
        """성공 로그"""
        print(f"\033[0;32m[SUCCESS]\033[0m {message}")
        self.logger.info(f"SUCCESS: {message}")

    def log_warning(self, message: str):
        """경고 로그"""
        print(f"\033[1;33m[WARNING]\033[0m {message}")
        self.logger.warning(message)

    def log_error(self, message: str):
        """에러 로그"""
        print(f"\033[0;31m[ERROR]\033[0m {message}")
        self.logger.error(message)
        self.error_logger.error(message)

    def execute_aws_command(self, description: str, command: List[str], output_file: str, jq_filter: Optional[str] = None) -> bool:
        """AWS CLI 명령 실행"""
        self.log_info(f"수집 중: {description}")
        self.total_count += 1
        
        try:
            # AWS CLI 명령 실행
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            # JSON 파싱 및 필터링
            data = json.loads(result.stdout)
            
            if jq_filter:
                # jq 필터 적용 (간단한 경우만 처리)
                if jq_filter.startswith('.') and ' | map(' in jq_filter:
                    # 복잡한 jq 필터는 subprocess로 처리
                    jq_cmd = ['jq', jq_filter]
                    jq_result = subprocess.run(jq_cmd, input=result.stdout, capture_output=True, text=True)
                    if jq_result.returncode == 0:
                        data = json.loads(jq_result.stdout)
                    else:
                        self.log_warning(f"jq 필터 적용 실패: {jq_result.stderr}")
            
            # 파일에 저장
            output_path = self.report_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            file_size = output_path.stat().st_size
            if file_size > 50:
                self.log_success(f"{description} 완료 ({output_file}, {file_size} bytes)")
                self.success_count += 1
                return True
            else:
                self.log_warning(f"{description} - 데이터 없음 ({output_file}, {file_size} bytes)")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log_error(f"{description} 실패: {e.stderr}")
            # 빈 배열로 파일 생성
            with open(self.report_dir / output_file, 'w') as f:
                json.dump([], f)
            return False
        except json.JSONDecodeError as e:
            self.log_error(f"{description} JSON 파싱 실패: {e}")
            with open(self.report_dir / output_file, 'w') as f:
                json.dump([], f)
            return False
        except Exception as e:
            self.log_error(f"{description} 예상치 못한 오류: {e}")
            with open(self.report_dir / output_file, 'w') as f:
                json.dump([], f)
            return False

    def collect_api_gateway_data(self):
        """API Gateway 데이터 수집"""
        # REST APIs
        self.execute_aws_command(
            "API Gateway REST APIs",
            ["aws", "apigateway", "get-rest-apis", "--region", self.region, "--output", "json"],
            "application_api_gateway_rest_apis.json",
            ".items"
        )
        
        # HTTP APIs (API Gateway v2)
        self.execute_aws_command(
            "API Gateway HTTP APIs",
            ["aws", "apigatewayv2", "get-apis", "--region", self.region, "--output", "json"],
            "application_api_gateway_http_apis.json",
            ".Items"
        )

    def collect_lambda_data(self):
        """Lambda 함수 데이터 수집"""
        self.execute_aws_command(
            "Lambda Functions",
            ["aws", "lambda", "list-functions", "--region", self.region, "--output", "json"],
            "iac_lambda_functions.json",
            ".Functions"
        )

    def collect_sns_data(self):
        """SNS 데이터 수집"""
        self.execute_aws_command(
            "SNS Topics",
            ["aws", "sns", "list-topics", "--region", self.region, "--output", "json"],
            "application_sns_topics.json",
            ".Topics"
        )

    def collect_sqs_data(self):
        """SQS 데이터 수집"""
        self.execute_aws_command(
            "SQS Queues",
            ["aws", "sqs", "list-queues", "--region", self.region, "--output", "json"],
            "application_sqs_queues.json",
            ".QueueUrls"
        )

    def collect_eventbridge_data(self):
        """EventBridge 데이터 수집"""
        # Event Buses
        self.execute_aws_command(
            "EventBridge Event Buses",
            ["aws", "events", "list-event-buses", "--region", self.region, "--output", "json"],
            "application_eventbridge_buses.json",
            ".EventBuses"
        )
        
        # Event Rules
        self.execute_aws_command(
            "EventBridge Rules",
            ["aws", "events", "list-rules", "--region", self.region, "--output", "json"],
            "application_eventbridge_rules.json",
            ".Rules"
        )

    def collect_step_functions_data(self):
        """Step Functions 데이터 수집"""
        self.execute_aws_command(
            "Step Functions State Machines",
            ["aws", "stepfunctions", "list-state-machines", "--region", self.region, "--output", "json"],
            "application_step_functions.json",
            ".stateMachines"
        )

    def collect_kinesis_data(self):
        """Kinesis 데이터 수집"""
        # Kinesis Streams
        self.execute_aws_command(
            "Kinesis Data Streams",
            ["aws", "kinesis", "list-streams", "--region", self.region, "--output", "json"],
            "application_kinesis_streams.json",
            ".StreamNames"
        )
        
        # Kinesis Firehose
        self.execute_aws_command(
            "Kinesis Data Firehose",
            ["aws", "firehose", "list-delivery-streams", "--region", self.region, "--output", "json"],
            "application_kinesis_firehose.json",
            ".DeliveryStreamNames"
        )

    def collect_cognito_data(self):
        """Cognito 데이터 수집"""
        # User Pools
        self.execute_aws_command(
            "Cognito User Pools",
            ["aws", "cognito-idp", "list-user-pools", "--max-results", "60", "--region", self.region, "--output", "json"],
            "application_cognito_user_pools.json",
            ".UserPools"
        )
        
        # Identity Pools
        self.execute_aws_command(
            "Cognito Identity Pools",
            ["aws", "cognito-identity", "list-identity-pools", "--max-results", "60", "--region", self.region, "--output", "json"],
            "application_cognito_identity_pools.json",
            ".IdentityPools"
        )

    def collect_app_sync_data(self):
        """AppSync 데이터 수집"""
        self.execute_aws_command(
            "AppSync GraphQL APIs",
            ["aws", "appsync", "list-graphql-apis", "--region", self.region, "--output", "json"],
            "application_appsync_apis.json",
            ".graphqlApis"
        )

    def collect_ses_data(self):
        """SES 데이터 수집"""
        # SES Identities
        self.execute_aws_command(
            "SES Identities",
            ["aws", "ses", "list-identities", "--region", self.region, "--output", "json"],
            "application_ses_identities.json",
            ".Identities"
        )

    def check_aws_credentials(self) -> bool:
        """AWS 자격 증명 확인"""
        try:
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True, text=True, check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def run_collection(self):
        """전체 수집 프로세스 실행"""
        self.log_info("🚀 AWS CLI 기반 애플리케이션 서비스 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        # AWS 자격 증명 확인
        self.log_info("AWS CLI 연결 확인 중...")
        if not self.check_aws_credentials():
            self.log_error("AWS CLI 연결 실패")
            sys.exit(1)
        
        self.log_info("📱 애플리케이션 서비스 리소스 수집 시작...")
        
        # 각 서비스별 데이터 수집
        self.collect_api_gateway_data()
        self.collect_lambda_data()
        self.collect_sns_data()
        self.collect_sqs_data()
        self.collect_eventbridge_data()
        self.collect_step_functions_data()
        self.collect_kinesis_data()
        self.collect_cognito_data()
        self.collect_app_sync_data()
        self.collect_ses_data()
        
        # 결과 요약
        self.log_success("애플리케이션 서비스 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.report_dir}/aws_cli_application_errors.log 파일을 확인하세요.")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AWS 애플리케이션 서비스 데이터 수집")
    parser.add_argument("--region", default="ap-northeast-2", help="AWS 리전")
    # 스크립트의 실제 위치를 기준으로 기본 경로 설정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    default_report_dir = str(project_root / "aws-arch-analysis" / "report")
    
    parser.add_argument("--report-dir", default=default_report_dir, help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = AWSApplicationCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
