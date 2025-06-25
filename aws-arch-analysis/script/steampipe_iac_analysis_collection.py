#!/usr/bin/env python3
"""
Steampipe 기반 IaC 분석 리소스 데이터 수집 스크립트 (Python 버전)
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

class SteampipeIaCCollector:
    def __init__(self, region: str = "ap-northeast-2", report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.region = region
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.report_dir / "steampipe_iac_collection.log"
        self.error_log = self.report_dir / "steampipe_iac_errors.log"
        
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

    def get_iac_queries(self) -> List[Tuple[str, str, str]]:
        return [
            # CloudFormation 스택
            (
                "CloudFormation 스택",
                f"select stack_name, stack_id, description, creation_time, last_updated_time, stack_status, stack_status_reason, disable_rollback, notification_arns, timeout_in_minutes, capabilities, outputs, role_arn, tags, enable_termination_protection, parent_id, root_id, drift_information from aws_cloudformation_stack where region = '{self.region}'",
                "iac_cloudformation_stacks.json"
            ),
            
            # Lambda 함수 (IaC 관점)
            (
                "Lambda 함수",
                f"select function_name, function_arn, runtime, role, handler, code_size, description, timeout, memory_size, last_modified, code_sha256, version, vpc_config, environment, dead_letter_config, kms_key_arn, tracing_config, master_arn, revision_id, layers, state, state_reason, state_reason_code, last_update_status, last_update_status_reason, last_update_status_reason_code, file_system_configs, image_config_response, signing_profile_version_arn, signing_job_arn, architectures, ephemeral_storage, snap_start, runtime_version_config, logging_config, tags from aws_lambda_function where region = '{self.region}'",
                "iac_lambda_functions.json"
            )
        ]

    def run_collection(self):
        self.log_info("🚀 Steampipe 기반 IaC 분석 데이터 수집 시작")
        self.log_info(f"Region: {self.region}")
        self.log_info(f"Report Directory: {self.report_dir}")
        
        self.log_info("🏗️ IaC 분석 리소스 수집 시작...")
        
        queries = self.get_iac_queries()
        for description, query, output_file in queries:
            self.execute_steampipe_query(description, query, output_file)
        
        self.log_success("IaC 분석 데이터 수집 완료!")
        self.log_info(f"성공: {self.success_count}/{self.total_count}")
        
        if self.success_count < self.total_count:
            self.log_warning(f"일부 오류가 발생했습니다. {self.error_log} 파일을 확인하세요.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Steampipe 기반 IaC 분석 데이터 수집")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "ap-northeast-2"), help="AWS 리전")
    parser.add_argument("--report-dir", default=os.getenv("REPORT_DIR", "/home/ec2-user/amazonqcli_lab/report"), help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    collector = SteampipeIaCCollector(args.region, args.report_dir)
    collector.run_collection()

if __name__ == "__main__":
    main()
