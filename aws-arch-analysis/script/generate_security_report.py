#!/usr/bin/env python3
"""
보안 분석 보고서 생성 스크립트 (Python 버전)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class SecurityReportGenerator:
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

    def write_iam_analysis(self, report_file, iam_users: Optional[List], iam_roles: Optional[List]) -> None:
        """IAM 분석 섹션을 작성합니다."""
        report_file.write("## 👤 IAM (Identity and Access Management) 현황\n\n")
        
        # IAM 사용자 분석
        report_file.write("### IAM 사용자\n")
        if not iam_users:
            report_file.write("IAM 사용자 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_users = len(iam_users)
            mfa_enabled_users = len([u for u in iam_users if u.get('mfa_enabled', False)])
            users_with_access_keys = len([u for u in iam_users if u.get('access_keys')])
            
            report_file.write(f"**총 IAM 사용자:** {total_users}개\n")
            report_file.write(f"- **MFA 활성화:** {mfa_enabled_users}개\n")
            report_file.write(f"- **액세스 키 보유:** {users_with_access_keys}개\n\n")
        
        # IAM 역할 분석
        report_file.write("### IAM 역할\n")
        if not iam_roles:
            report_file.write("IAM 역할 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_roles = len(iam_roles)
            service_roles = len([r for r in iam_roles if 'service-role' in r.get('path', '')])
            
            report_file.write(f"**총 IAM 역할:** {total_roles}개\n")
            report_file.write(f"- **서비스 역할:** {service_roles}개\n\n")

    def write_security_services_analysis(self, report_file, cloudtrail_data: Optional[List], guardduty_data: Optional[List]) -> None:
        """보안 서비스 분석 섹션을 작성합니다."""
        report_file.write("## 🛡️ 보안 서비스 현황\n\n")
        
        # CloudTrail 분석
        report_file.write("### AWS CloudTrail\n")
        if not cloudtrail_data:
            report_file.write("CloudTrail 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_trails = len(cloudtrail_data)
            active_trails = len([t for t in cloudtrail_data if t.get('is_logging', False)])
            multi_region_trails = len([t for t in cloudtrail_data if t.get('is_multi_region_trail', False)])
            
            report_file.write(f"**총 CloudTrail:** {total_trails}개\n")
            report_file.write(f"- **활성 상태:** {active_trails}개\n")
            report_file.write(f"- **멀티 리전:** {multi_region_trails}개\n\n")
        
        # GuardDuty 분석
        report_file.write("### Amazon GuardDuty\n")
        if not guardduty_data:
            report_file.write("GuardDuty 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_detectors = len(guardduty_data)
            enabled_detectors = len([d for d in guardduty_data if d.get('status') == 'ENABLED'])
            
            report_file.write(f"**총 GuardDuty 탐지기:** {total_detectors}개\n")
            report_file.write(f"- **활성화된 탐지기:** {enabled_detectors}개\n\n")

    def write_encryption_analysis(self, report_file, kms_data: Optional[List]) -> None:
        """암호화 분석 섹션을 작성합니다."""
        report_file.write("## 🔐 암호화 및 키 관리\n\n")
        
        if not kms_data:
            report_file.write("KMS 키 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_keys = len(kms_data)
        customer_managed_keys = len([k for k in kms_data if k.get('key_manager') == 'CUSTOMER'])
        enabled_keys = len([k for k in kms_data if k.get('enabled', False)])
        
        report_file.write(f"**총 KMS 키:** {total_keys}개\n")
        report_file.write(f"- **고객 관리형 키:** {customer_managed_keys}개\n")
        report_file.write(f"- **활성화된 키:** {enabled_keys}개\n\n")

    def write_security_recommendations(self, report_file, iam_users: Optional[List], cloudtrail_data: Optional[List]) -> None:
        """보안 권장사항 섹션을 작성합니다."""
        report_file.write("## 📋 보안 강화 권장사항\n\n")
        
        report_file.write("### 🔴 높은 우선순위\n")
        
        recommendations = []
        
        # IAM 관련 권장사항
        if iam_users:
            users_without_mfa = [u for u in iam_users if not u.get('mfa_enabled', False)]
            if users_without_mfa:
                recommendations.append(f"**MFA 활성화**: {len(users_without_mfa)}개의 사용자가 MFA를 사용하지 않습니다. 모든 사용자에 대해 MFA를 활성화하세요.")
        
        # CloudTrail 관련 권장사항
        if cloudtrail_data:
            inactive_trails = [t for t in cloudtrail_data if not t.get('is_logging', False)]
            if inactive_trails:
                recommendations.append(f"**CloudTrail 활성화**: {len(inactive_trails)}개의 비활성 CloudTrail이 있습니다. 감사 로깅을 위해 활성화하세요.")
        
        # 기본 권장사항
        if not recommendations:
            recommendations = [
                "**최소 권한 원칙**: IAM 정책을 검토하여 최소 권한 원칙을 적용하세요.",
                "**정기적인 액세스 검토**: 사용자 및 역할의 권한을 정기적으로 검토하세요."
            ]
        
        for i, rec in enumerate(recommendations, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n### 🟡 중간 우선순위\n")
        report_file.write("1. **보안 그룹 검토**: 불필요하게 열린 포트가 있는지 보안 그룹을 검토하세요.\n")
        report_file.write("2. **암호화 정책**: 저장 중 및 전송 중 데이터 암호화 정책을 수립하세요.\n")
        report_file.write("3. **Config 규칙**: AWS Config를 통한 컴플라이언스 모니터링을 설정하세요.\n\n")
        
        report_file.write("### 🟢 낮은 우선순위\n")
        report_file.write("1. **Security Hub**: 중앙 집중식 보안 관리를 위한 Security Hub를 활성화하세요.\n")
        report_file.write("2. **VPC Flow Logs**: 네트워크 트래픽 모니터링을 위한 VPC Flow Logs를 활성화하세요.\n")
        report_file.write("3. **WAF 구성**: 웹 애플리케이션 보호를 위한 AWS WAF 구성을 고려하세요.\n\n")

    def generate_report(self):
        """보안 분석 보고서를 생성합니다."""
        print("🔒 Security Analysis 보고서 생성 중...")
        
        # 데이터 파일 로드
        iam_users = self.load_json_file("security_iam_users.json")
        iam_roles = self.load_json_file("security_iam_roles.json")
        kms_data = self.load_json_file("security_kms_keys.json")
        cloudtrail_data = self.load_json_file("security_cloudtrail.json")
        guardduty_data = self.load_json_file("security_guardduty_detectors.json")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "06-security-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 보안 분석\n\n")
                
                # 각 섹션 작성
                self.write_iam_analysis(report_file, iam_users, iam_roles)
                self.write_security_services_analysis(report_file, cloudtrail_data, guardduty_data)
                self.write_encryption_analysis(report_file, kms_data)
                self.write_security_recommendations(report_file, iam_users, cloudtrail_data)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*보안 분석 완료*\n")
            
            print("✅ Security Analysis 생성 완료: 06-security-analysis.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="보안 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = SecurityReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
