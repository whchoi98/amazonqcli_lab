#!/usr/bin/env python3
"""
간단한 비용 최적화 보고서 생성기
수집된 비용 데이터를 바탕으로 기본적인 비용 분석 보고서 생성
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SimpleCostReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def load_json_data(self, filename: str):
        """JSON 데이터 파일 로드"""
        file_path = self.report_dir / filename
        try:
            if file_path.exists() and file_path.stat().st_size > 16:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            return None
        except Exception as e:
            print(f"Warning: Failed to load {filename}: {e}")
            return None

    def format_currency(self, amount):
        """통화 형식 포맷팅"""
        if amount is None:
            return "$0.00"
        return f"${float(amount):,.2f}"

    def generate_report(self):
        """비용 최적화 보고서 생성"""
        print("💰 Simple Cost Analysis 보고서 생성 중...")
        
        # 데이터 로드
        service_monthly = self.load_json_data('cost_by_service_monthly.json')
        service_daily = self.load_json_data('cost_by_service_daily.json')
        
        # 보고서 내용 생성
        report_content = f"""# 💰 비용 최적화 종합 분석

> **분석 일시**: {self.current_time}  
> **분석 대상**: AWS 계정 내 모든 서비스 비용  
> **분석 리전**: ap-northeast-2 (서울)

이 보고서는 AWS 계정의 비용 구조에 대한 종합적인 분석을 제공하며, 서비스별 비용 분포, 사용량 패턴, 비용 최적화 기회를 평가합니다.

이 보고서는 AWS 환경의 비용 현황을 분석하고 최적화 방안을 제시합니다.

## 📊 비용 현황 요약

"""
        
        # 서비스별 월간 비용 분석
        if service_monthly and 'rows' in service_monthly and len(service_monthly['rows']) > 0:
            rows = service_monthly['rows']
            total_cost = sum(row.get('blended_cost_amount', 0) for row in rows)
            
            report_content += f"""### 월간 총 비용
**총 비용:** {self.format_currency(total_cost)}
**분석 서비스 수:** {len(rows)}개

### 상위 비용 서비스 (Top 10)

| 순위 | 서비스명 | 월간 비용 | 비율 |
|------|----------|-----------|------|
"""
            
            for i, row in enumerate(rows[:10], 1):
                service_name = row.get('service', 'Unknown')
                cost = row.get('blended_cost_amount', 0)
                percentage = (cost * 100 / total_cost) if total_cost > 0 else 0
                
                report_content += f"| {i} | {service_name[:40]} | {self.format_currency(cost)} | {percentage:.1f}% |\n"
        else:
            report_content += """### 월간 비용 데이터
❌ 월간 비용 데이터를 찾을 수 없습니다.

"""

        # 일간 비용 트렌드
        if service_daily and 'rows' in service_daily and len(service_daily['rows']) > 0:
            daily_rows = service_daily['rows']
            report_content += f"""
### 일간 비용 트렌드
**일간 데이터 포인트:** {len(daily_rows)}개
**분석 기간:** 최근 데이터 기준

"""
        else:
            report_content += """
### 일간 비용 트렌드
❌ 일간 비용 데이터를 찾을 수 없습니다.

"""

        # 비용 최적화 권장사항
        report_content += """## 💡 비용 최적화 권장사항

### 🔴 즉시 실행 (High Priority)

1. **미사용 리소스 정리**
   - 중지된 EC2 인스턴스의 EBS 볼륨 정리
   - 연결되지 않은 Elastic IP 해제
   - 미사용 로드 밸런서 삭제

2. **예약 인스턴스 활용**
   - 지속적으로 실행되는 EC2 인스턴스에 대해 예약 인스턴스 구매 검토
   - RDS 인스턴스에 대한 예약 인스턴스 고려

3. **스토리지 최적화**
   - S3 스토리지 클래스 최적화 (Intelligent Tiering 활용)
   - 오래된 스냅샷 정리 정책 수립

### 🟡 중기 실행 (Medium Priority)

1. **Auto Scaling 최적화**
   - EC2 Auto Scaling 정책 검토 및 최적화
   - 사용량 패턴에 따른 스케줄링 적용

2. **모니터링 강화**
   - CloudWatch를 통한 비용 알람 설정
   - 예산 관리 도구 활용

3. **리소스 태깅**
   - 비용 추적을 위한 일관된 태깅 전략 수립
   - 부서별/프로젝트별 비용 할당

### 🟢 장기 실행 (Low Priority)

1. **아키텍처 최적화**
   - 서버리스 아키텍처 도입 검토
   - 컨테이너화를 통한 리소스 효율성 향상

2. **멀티 클라우드 전략**
   - 워크로드별 최적 클라우드 플랫폼 선택
   - 하이브리드 클라우드 구성 검토

## 📈 모니터링 및 추적

### 권장 모니터링 도구
- **AWS Cost Explorer**: 비용 트렌드 분석
- **AWS Budgets**: 예산 설정 및 알람
- **AWS Trusted Advisor**: 비용 최적화 권장사항
- **CloudWatch**: 리소스 사용률 모니터링

### 정기 검토 일정
- **주간**: 비용 트렌드 확인
- **월간**: 예산 대비 실적 검토
- **분기별**: 아키텍처 최적화 검토
- **연간**: 전체 비용 전략 재평가

---

## 📞 추가 지원

이 보고서에 대한 질문이나 추가 분석이 필요한 경우:
- AWS Support 케이스 생성
- AWS Well-Architected Review 수행
- AWS Professional Services 문의

*비용 최적화 분석 완료*
"""

        return report_content

    def save_report(self, content):
        """보고서 파일 저장"""
        report_path = self.report_dir / "07-cost-optimization.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Cost Optimization 생성 완료: 07-cost-optimization.md")
            print(f"📁 보고서 위치: {report_path}")
            
            # 파일 크기 정보 출력
            file_size = report_path.stat().st_size
            print(f"📊 보고서 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            return False
        
        return True

def main():
    """메인 함수"""
    try:
        generator = SimpleCostReportGenerator()
        report_content = generator.generate_report()
        generator.save_report(report_content)
        print("🎉 비용 최적화 보고서 생성이 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
