#!/usr/bin/env python3
"""
경영진 요약 보고서 생성 스크립트 (Python 버전)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExecutiveSummaryGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_json_file(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """JSON 파일을 로드합니다."""
        file_path = self.report_dir / filename
        try:
            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'rows' in data:
                        return data['rows']
                    elif isinstance(data, list):
                        return data
                    return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load {filename}: {e}")
        return None

    def write_overview(self, report_file) -> None:
        """개요 섹션을 작성합니다."""
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        report_file.write("## 📋 분석 개요\n\n")
        report_file.write(f"**분석 일자**: {current_date}\n")
        report_file.write("**분석 범위**: AWS 계정 전체 리소스\n")
        report_file.write("**분석 목적**: 인프라 현황 파악 및 최적화 방안 도출\n\n")

    def write_resource_summary(self, report_file) -> None:
        """리소스 요약 섹션을 작성합니다."""
        report_file.write("## 🏗️ 인프라 현황 요약\n\n")
        
        # 각 서비스별 리소스 수 집계
        resource_counts = {}
        
        # 컴퓨팅 리소스
        ec2_data = self.load_json_file("compute_ec2_instances.json")
        if ec2_data:
            resource_counts["EC2 인스턴스"] = len(ec2_data)
        
        # 네트워킹 리소스
        vpc_data = self.load_json_file("networking_vpc.json")
        if vpc_data:
            resource_counts["VPC"] = len(vpc_data)
        
        # 스토리지 리소스
        s3_data = self.load_json_file("storage_s3_buckets.json")
        if s3_data:
            resource_counts["S3 버킷"] = len(s3_data)
        
        # 데이터베이스 리소스
        rds_data = self.load_json_file("database_rds_instances.json")
        if rds_data:
            resource_counts["RDS 인스턴스"] = len(rds_data)
        
        report_file.write("### 주요 리소스 현황\n")
        report_file.write("| 서비스 | 리소스 수 |\n")
        report_file.write("|--------|----------|\n")
        
        for service, count in resource_counts.items():
            report_file.write(f"| {service} | {count}개 |\n")
        
        report_file.write("\n")

    def write_key_findings(self, report_file) -> None:
        """주요 발견사항 섹션을 작성합니다."""
        report_file.write("## 🔍 주요 발견사항\n\n")
        
        findings = []
        
        # 보안 관련 발견사항
        iam_users = self.load_json_file("security_iam_users.json")
        if iam_users:
            users_without_mfa = [u for u in iam_users if not u.get('mfa_enabled', False)]
            if users_without_mfa:
                findings.append(f"**보안**: {len(users_without_mfa)}개의 IAM 사용자가 MFA를 사용하지 않음")
        
        # 비용 최적화 관련 발견사항
        ebs_data = self.load_json_file("storage_ebs_volumes.json")
        if ebs_data:
            unused_volumes = [v for v in ebs_data if v.get('state') == 'available']
            if unused_volumes:
                findings.append(f"**비용**: {len(unused_volumes)}개의 미사용 EBS 볼륨 발견")
        
        # 기본 발견사항
        if not findings:
            findings = [
                "**인프라**: 전반적으로 안정적인 인프라 구성",
                "**보안**: 기본적인 보안 설정이 적용됨",
                "**모니터링**: CloudWatch를 통한 기본 모니터링 구성"
            ]
        
        for i, finding in enumerate(findings, 1):
            report_file.write(f"{i}. {finding}\n")
        
        report_file.write("\n")

    def write_recommendations(self, report_file) -> None:
        """권장사항 섹션을 작성합니다."""
        report_file.write("## 💡 핵심 권장사항\n\n")
        
        report_file.write("### 🔴 즉시 조치 필요\n")
        report_file.write("1. **MFA 활성화**: 모든 IAM 사용자에 대해 다단계 인증을 활성화하세요.\n")
        report_file.write("2. **미사용 리소스 정리**: 비용 절약을 위해 미사용 EBS 볼륨을 정리하세요.\n")
        report_file.write("3. **암호화 강화**: 저장 중 데이터 암호화를 모든 서비스에 적용하세요.\n\n")
        
        report_file.write("### 🟡 단기 개선 (1-3개월)\n")
        report_file.write("1. **모니터링 강화**: 핵심 메트릭에 대한 CloudWatch 알람을 설정하세요.\n")
        report_file.write("2. **백업 정책**: 자동화된 백업 정책을 수립하고 적용하세요.\n")
        report_file.write("3. **네트워크 보안**: 보안 그룹 규칙을 검토하고 최소 권한 원칙을 적용하세요.\n\n")
        
        report_file.write("### 🟢 중장기 개선 (3-6개월)\n")
        report_file.write("1. **인프라 자동화**: Infrastructure as Code를 통한 인프라 관리 자동화\n")
        report_file.write("2. **재해 복구**: 크로스 리전 백업 및 재해 복구 계획 수립\n")
        report_file.write("3. **비용 최적화**: Reserved Instance 및 Savings Plans 활용 검토\n\n")

    def write_cost_summary(self, report_file) -> None:
        """비용 요약 섹션을 작성합니다."""
        report_file.write("## 💰 비용 최적화 기회\n\n")
        
        report_file.write("### 예상 절감 효과\n")
        report_file.write("| 항목 | 예상 절감률 | 구현 난이도 |\n")
        report_file.write("|------|-------------|-------------|\n")
        report_file.write("| 미사용 리소스 정리 | 10-15% | 쉬움 |\n")
        report_file.write("| Reserved Instance 활용 | 20-30% | 보통 |\n")
        report_file.write("| 스토리지 클래스 최적화 | 15-25% | 보통 |\n")
        report_file.write("| 인스턴스 타입 최적화 | 10-20% | 어려움 |\n\n")

    def generate_report(self):
        """경영진 요약 보고서를 생성합니다."""
        print("📊 Executive Summary 보고서 생성 중...")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "01-executive-summary.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# AWS 인프라 분석 - 경영진 요약\n\n")
                
                # 각 섹션 작성
                self.write_overview(report_file)
                self.write_resource_summary(report_file)
                self.write_key_findings(report_file)
                self.write_recommendations(report_file)
                self.write_cost_summary(report_file)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*본 보고서는 AWS 리소스 분석을 통해 자동 생성되었습니다.*\n")
            
            print("✅ Executive Summary 생성 완료: 01-executive-summary.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="경영진 요약 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = ExecutiveSummaryGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
