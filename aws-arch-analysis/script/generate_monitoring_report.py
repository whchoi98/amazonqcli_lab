#!/usr/bin/env python3
"""
모니터링 분석 보고서 생성 스크립트 (Python 버전)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class MonitoringReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
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

    def write_cloudwatch_analysis(self, report_file, log_groups: Optional[List], alarms: Optional[List]) -> None:
        """CloudWatch 분석 섹션을 작성합니다."""
        report_file.write("## 📊 CloudWatch 모니터링 현황\n\n")
        
        # 로그 그룹 분석
        report_file.write("### CloudWatch 로그 그룹\n")
        if not log_groups:
            report_file.write("CloudWatch 로그 그룹 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_log_groups = len(log_groups)
            with_retention = len([lg for lg in log_groups if lg.get('retention_in_days')])
            
            report_file.write(f"**총 로그 그룹:** {total_log_groups}개\n")
            report_file.write(f"- **보존 기간 설정:** {with_retention}개\n\n")
        
        # 알람 분석
        report_file.write("### CloudWatch 알람\n")
        if not alarms:
            report_file.write("CloudWatch 알람 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_alarms = len(alarms)
            ok_alarms = len([a for a in alarms if a.get('state_value') == 'OK'])
            alarm_alarms = len([a for a in alarms if a.get('state_value') == 'ALARM'])
            
            report_file.write(f"**총 CloudWatch 알람:** {total_alarms}개\n")
            report_file.write(f"- **정상 상태:** {ok_alarms}개\n")
            report_file.write(f"- **알람 상태:** {alarm_alarms}개\n\n")

    def write_ssm_analysis(self, report_file, ssm_params: Optional[List]) -> None:
        """Systems Manager 분석 섹션을 작성합니다."""
        report_file.write("## ⚙️ Systems Manager 현황\n\n")
        
        if not ssm_params:
            report_file.write("Systems Manager 파라미터 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_params = len(ssm_params)
        secure_params = len([p for p in ssm_params if p.get('type') == 'SecureString'])
        
        report_file.write(f"**총 SSM 파라미터:** {total_params}개\n")
        report_file.write(f"- **보안 문자열:** {secure_params}개\n\n")

    def write_monitoring_recommendations(self, report_file, log_groups: Optional[List], alarms: Optional[List]) -> None:
        """모니터링 권장사항 섹션을 작성합니다."""
        report_file.write("## 📋 모니터링 개선 권장사항\n\n")
        
        report_file.write("### 🔴 높은 우선순위\n")
        
        recommendations = []
        
        if log_groups:
            no_retention = [lg for lg in log_groups if not lg.get('retention_in_days')]
            if no_retention:
                recommendations.append(f"**로그 보존 정책**: {len(no_retention)}개의 로그 그룹에 보존 기간이 설정되지 않았습니다. 비용 절약을 위해 적절한 보존 기간을 설정하세요.")
        
        if not recommendations:
            recommendations = [
                "**핵심 메트릭 모니터링**: CPU, 메모리, 디스크 사용률에 대한 알람을 설정하세요.",
                "**로그 중앙화**: 모든 애플리케이션 로그를 CloudWatch Logs로 중앙화하세요."
            ]
        
        for i, rec in enumerate(recommendations, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n### 🟡 중간 우선순위\n")
        report_file.write("1. **대시보드 구성**: 주요 메트릭을 한눈에 볼 수 있는 대시보드를 구성하세요.\n")
        report_file.write("2. **알림 채널**: SNS를 통한 알람 알림 채널을 설정하세요.\n")
        report_file.write("3. **X-Ray 추적**: 애플리케이션 성능 분석을 위한 X-Ray를 활성화하세요.\n\n")
        
        report_file.write("### 🟢 낮은 우선순위\n")
        report_file.write("1. **사용자 정의 메트릭**: 비즈니스 메트릭을 CloudWatch로 전송하세요.\n")
        report_file.write("2. **로그 인사이트**: CloudWatch Logs Insights를 활용한 로그 분석을 수행하세요.\n")
        report_file.write("3. **컨테이너 인사이트**: ECS/EKS 환경에서 Container Insights를 활성화하세요.\n\n")

    def generate_report(self):
        """모니터링 분석 보고서를 생성합니다."""
        print("📊 Monitoring Analysis 보고서 생성 중...")
        
        # 데이터 파일 로드
        log_groups = self.load_json_file("monitoring_cloudwatch_log_groups.json")
        alarms = self.load_json_file("monitoring_cloudwatch_alarms.json")
        ssm_params = self.load_json_file("monitoring_ssm_parameters.json")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "09-monitoring-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 모니터링 분석\n\n")
                
                # 각 섹션 작성
                self.write_cloudwatch_analysis(report_file, log_groups, alarms)
                self.write_ssm_analysis(report_file, ssm_params)
                self.write_monitoring_recommendations(report_file, log_groups, alarms)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*모니터링 분석 완료*\n")
            
            print("✅ Monitoring Analysis 생성 완료: 09-monitoring-analysis.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="모니터링 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = MonitoringReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
