#!/usr/bin/env python3
"""
종합 권장사항 보고서 생성 스크립트 (Python 버전)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class RecommendationsGenerator:
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

    def analyze_security_issues(self) -> List[Dict[str, Any]]:
        """보안 이슈를 분석합니다."""
        issues = []
        
        # IAM 사용자 MFA 확인
        iam_users = self.load_json_file("security_iam_users.json")
        if iam_users:
            users_without_mfa = [u for u in iam_users if not u.get('mfa_enabled', False)]
            if users_without_mfa:
                issues.append({
                    "category": "보안",
                    "priority": "높음",
                    "title": "IAM 사용자 MFA 미설정",
                    "description": f"{len(users_without_mfa)}개의 IAM 사용자가 MFA를 사용하지 않습니다.",
                    "impact": "계정 보안 위험 증가",
                    "solution": "모든 IAM 사용자에 대해 MFA를 활성화하세요.",
                    "effort": "쉬움",
                    "timeline": "1주"
                })
        
        return issues

    def analyze_cost_optimization(self) -> List[Dict[str, Any]]:
        """비용 최적화 기회를 분석합니다."""
        opportunities = []
        
        # 미사용 EBS 볼륨
        ebs_data = self.load_json_file("storage_ebs_volumes.json")
        if ebs_data:
            unused_volumes = [v for v in ebs_data if v.get('state') == 'available']
            if unused_volumes:
                opportunities.append({
                    "category": "비용 최적화",
                    "priority": "높음",
                    "title": "미사용 EBS 볼륨 정리",
                    "description": f"{len(unused_volumes)}개의 미사용 EBS 볼륨이 발견되었습니다.",
                    "impact": "월 비용 절감",
                    "solution": "미사용 볼륨을 삭제하거나 스냅샷으로 백업 후 삭제하세요.",
                    "effort": "쉬움",
                    "timeline": "1주"
                })
        
        return opportunities

    def write_priority_recommendations(self, report_file, all_recommendations: List[Dict[str, Any]]) -> None:
        """우선순위별 권장사항을 작성합니다."""
        high_priority = [r for r in all_recommendations if r['priority'] == '높음']
        medium_priority = [r for r in all_recommendations if r['priority'] == '중간']
        low_priority = [r for r in all_recommendations if r['priority'] == '낮음']
        
        # 높은 우선순위
        report_file.write("## 🔴 높은 우선순위 (즉시 조치)\n\n")
        for i, rec in enumerate(high_priority, 1):
            report_file.write(f"### {i}. {rec['title']}\n")
            report_file.write(f"**카테고리**: {rec['category']}\n")
            report_file.write(f"**설명**: {rec['description']}\n")
            report_file.write(f"**영향**: {rec['impact']}\n")
            report_file.write(f"**해결방안**: {rec['solution']}\n")
            report_file.write(f"**구현 난이도**: {rec['effort']}\n")
            report_file.write(f"**예상 기간**: {rec['timeline']}\n\n")
        
        # 중간 우선순위
        if medium_priority:
            report_file.write("## 🟡 중간 우선순위 (1-3개월)\n\n")
            for i, rec in enumerate(medium_priority, 1):
                report_file.write(f"### {i}. {rec['title']}\n")
                report_file.write(f"**설명**: {rec['description']}\n")
                report_file.write(f"**해결방안**: {rec['solution']}\n\n")
        
        # 낮은 우선순위
        if low_priority:
            report_file.write("## 🟢 낮은 우선순위 (3-6개월)\n\n")
            for i, rec in enumerate(low_priority, 1):
                report_file.write(f"### {i}. {rec['title']}\n")
                report_file.write(f"**설명**: {rec['description']}\n")
                report_file.write(f"**해결방안**: {rec['solution']}\n\n")

    def write_implementation_roadmap(self, report_file) -> None:
        """구현 로드맵을 작성합니다."""
        report_file.write("## 🗓️ 구현 로드맵\n\n")
        
        report_file.write("### 1개월 내 (즉시 조치)\n")
        report_file.write("- [ ] IAM 사용자 MFA 활성화\n")
        report_file.write("- [ ] 미사용 리소스 정리\n")
        report_file.write("- [ ] 기본 보안 설정 강화\n\n")
        
        report_file.write("### 3개월 내 (단기 개선)\n")
        report_file.write("- [ ] 모니터링 및 알람 설정\n")
        report_file.write("- [ ] 백업 정책 수립\n")
        report_file.write("- [ ] 네트워크 보안 강화\n\n")
        
        report_file.write("### 6개월 내 (중장기 개선)\n")
        report_file.write("- [ ] Infrastructure as Code 도입\n")
        report_file.write("- [ ] 재해 복구 계획 수립\n")
        report_file.write("- [ ] 비용 최적화 전략 실행\n\n")

    def generate_report(self):
        """종합 권장사항 보고서를 생성합니다."""
        print("🛠️ Comprehensive Recommendations 보고서 생성 중...")
        
        # 각 영역별 분석 수행
        security_issues = self.analyze_security_issues()
        cost_opportunities = self.analyze_cost_optimization()
        
        # 모든 권장사항 통합
        all_recommendations = security_issues + cost_opportunities
        
        # 보고서 파일 생성
        report_path = self.report_dir / "10-comprehensive-recommendations.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 종합 권장사항\n\n")
                
                # 개요
                report_file.write("## 📋 권장사항 개요\n\n")
                report_file.write("본 문서는 AWS 인프라 분석 결과를 바탕으로 도출된 종합적인 개선 권장사항을 제시합니다.\n\n")
                
                # 우선순위별 권장사항
                self.write_priority_recommendations(report_file, all_recommendations)
                
                # 구현 로드맵
                self.write_implementation_roadmap(report_file)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*종합 권장사항 분석 완료*\n")
            
            print("✅ Comprehensive Recommendations 생성 완료: 10-comprehensive-recommendations.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="종합 권장사항 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = RecommendationsGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
