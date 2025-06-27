#!/usr/bin/env python3
"""
Enhanced Cost Analysis Report Generator
수집된 비용 데이터를 바탕으로 종합적인 비용 분석 보고서 생성
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class CostReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 데이터 파일 경로
        self.data_files = {
            'service_monthly': 'cost_by_service_monthly.json',
            'service_daily': 'cost_by_service_daily.json',
            'usage_type_monthly': 'cost_by_service_usage_type_monthly.json',
            'usage_type_daily': 'cost_by_service_usage_type_daily.json',
            'record_type_monthly': 'cost_by_record_type_monthly.json',
            'record_type_daily': 'cost_by_record_type_daily.json'
        }
        
        # 비용 통계 초기화
        self.cost_stats = {
            'total_monthly_cost': 0.0,
            'top_service_cost': 0.0,
            'top_service_name': '',
            'service_count': 0,
            'daily_records': 0
        }

    def load_json_data(self, filename: str) -> Optional[Dict]:
        """JSON 데이터 파일 로드"""
        file_path = self.report_dir / filename
        try:
            if file_path.exists() and file_path.stat().st_size > 16:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('rows') and len(data['rows']) > 0:
                        return data
            return None
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.warning(f"데이터 파일 로드 실패: {filename} - {e}")
            return None

    def format_currency(self, amount: float) -> str:
        """통화 형식 포맷팅"""
        return f"${amount:,.2f}"

    def calculate_percentage(self, part: float, total: float) -> str:
        """백분율 계산"""
        if total == 0:
            return "0.0"
        return f"{(part * 100 / total):.1f}"

    def get_service_short_name(self, service_name: str) -> str:
        """서비스명 단축"""
        service_mappings = {
            'Amazon Elastic Compute Cloud - Compute': 'EC2 Compute',
            'AWS Network Firewall': 'Network Firewall',
            'Amazon Virtual Private Cloud': 'VPC',
            'Amazon Relational Database Service': 'RDS',
            'Amazon Simple Storage Service': 'S3',
            'Amazon CloudWatch': 'CloudWatch',
            'AWS Lambda': 'Lambda'
        }
        return service_mappings.get(service_name, service_name[:30])

    def analyze_cost_data(self):
        """비용 데이터 분석"""
        # 서비스별 월간 비용 분석
        service_monthly_data = self.load_json_data(self.data_files['service_monthly'])
        if service_monthly_data:
            rows = service_monthly_data['rows']
            self.cost_stats['service_count'] = len(rows)
            self.cost_stats['total_monthly_cost'] = sum(row.get('blended_cost_amount', 0) for row in rows)
            
            if rows:
                self.cost_stats['top_service_cost'] = rows[0].get('blended_cost_amount', 0)
                self.cost_stats['top_service_name'] = rows[0].get('service', '')
        
        # 일간 비용 데이터 분석
        service_daily_data = self.load_json_data(self.data_files['service_daily'])
        if service_daily_data:
            self.cost_stats['daily_records'] = len(service_daily_data['rows'])

    def generate_executive_summary(self) -> str:
        """Executive Summary 생성"""
        total_cost = self.cost_stats['total_monthly_cost']
        service_count = self.cost_stats['service_count']
        top_service = self.cost_stats['top_service_name']
        top_cost = self.cost_stats['top_service_cost']
        avg_cost = total_cost / service_count if service_count > 0 else 0
        
        summary = f"""# 💰 AWS 비용 분석 종합 보고서

> **분석 일시**: {self.current_time}  
> **분석 대상**: AWS 계정 내 모든 서비스 비용  
> **분석 리전**: ap-northeast-2 (서울)

## 📊 Executive Summary

### 비용 현황 개요

**📈 월간 비용 요약 (현재 월)**
- **총 월간 비용**: {self.format_currency(total_cost)} USD
- **활성 서비스 수**: {service_count}개
- **최고 비용 서비스**: {self.get_service_short_name(top_service)} ({self.format_currency(top_cost)})
- **평균 서비스 비용**: {self.format_currency(avg_cost)} USD

---

"""
        return summary

    def analyze_service_costs(self) -> str:
        """서비스별 비용 분석"""
        service_data = self.load_json_data(self.data_files['service_monthly'])
        
        if not service_data:
            return """## 📊 서비스별 비용 분석

### 월간 서비스별 비용 현황
❌ 서비스별 월간 비용 데이터를 찾을 수 없습니다.

"""
        
        rows = service_data['rows'][:10]  # 상위 10개 서비스
        total_cost = self.cost_stats['total_monthly_cost']
        
        analysis = """## 📊 서비스별 비용 분석

### 월간 서비스별 비용 현황

#### 📋 상위 서비스별 월간 비용

| 순위 | 서비스명 | 월간 비용 (USD) | 비용 비율 | 기간 |
|------|----------|----------------|-----------|------|
"""
        
        for i, row in enumerate(rows, 1):
            service = self.get_service_short_name(row.get('service', ''))
            cost = row.get('blended_cost_amount', 0)
            percentage = self.calculate_percentage(cost, total_cost)
            start_date = row.get('period_start', '').split('T')[0]
            end_date = row.get('period_end', '').split('T')[0]
            period = f"{start_date} ~ {end_date}"
            
            analysis += f"| {i} | {service} | {self.format_currency(cost)} | {percentage}% | {period} |\n"
        
        # 주요 서비스 분석
        analysis += """
#### 💡 서비스별 비용 분석

**주요 비용 서비스 분석**:
"""
        
        for row in rows[:3]:  # 상위 3개 서비스
            service = row.get('service', '')
            cost = row.get('blended_cost_amount', 0)
            percentage = self.calculate_percentage(cost, total_cost)
            
            if 'Elastic Compute Cloud' in service:
                analysis += f"- **EC2 컴퓨팅**: {self.format_currency(cost)} ({percentage}%) - 인스턴스 타입 최적화 및 Reserved Instance 검토 권장\n"
            elif 'Network Firewall' in service:
                analysis += f"- **Network Firewall**: {self.format_currency(cost)} ({percentage}%) - 방화벽 정책 최적화 및 사용량 검토 필요\n"
            elif 'Virtual Private Cloud' in service:
                analysis += f"- **VPC 네트워킹**: {self.format_currency(cost)} ({percentage}%) - NAT Gateway 및 데이터 전송 비용 최적화 검토\n"
            elif 'Relational Database Service' in service:
                analysis += f"- **RDS 데이터베이스**: {self.format_currency(cost)} ({percentage}%) - 인스턴스 크기 조정 및 Reserved Instance 활용 검토\n"
            else:
                analysis += f"- **{self.get_service_short_name(service)}**: {self.format_currency(cost)} ({percentage}%) - 사용량 패턴 분석 및 최적화 검토 권장\n"
        
        return analysis

    def analyze_daily_trends(self) -> str:
        """일간 비용 트렌드 분석"""
        daily_data = self.load_json_data(self.data_files['service_daily'])
        
        if not daily_data:
            return """### 일간 비용 트렌드 분석
❌ 일간 비용 데이터를 찾을 수 없습니다.

"""
        
        rows = daily_data['rows']
        daily_records = len(rows)
        
        # 최근 일간 비용 계산
        latest_daily_cost = sum(row.get('blended_cost_amount', 0) for row in rows if row.get('period_start', '').startswith('2025-06-26'))
        previous_daily_cost = sum(row.get('blended_cost_amount', 0) for row in rows if row.get('period_start', '').startswith('2025-06-25'))
        
        trend = "📈 증가" if latest_daily_cost > previous_daily_cost else "📉 감소"
        
        analysis = f"""### 일간 비용 트렌드 분석

**📈 일간 비용 트렌드**
- **총 일간 기록 수**: {daily_records}개
- **최근 일간 비용**: {self.format_currency(latest_daily_cost)} USD
- **전일 대비 변화**: {trend}

#### 📋 최근 5일간 주요 서비스 비용

| 날짜 | 서비스 | 일간 비용 (USD) | 비고 |
|------|--------|----------------|------|
"""
        
        # 최근 5일간 데이터 필터링 및 정렬
        recent_rows = [row for row in rows if row.get('period_start', '') >= '2025-06-22']
        recent_rows.sort(key=lambda x: x.get('period_start', ''), reverse=True)
        
        for row in recent_rows[:15]:  # 상위 15개 표시
            date = row.get('period_start', '').split('T')[0]
            service = self.get_service_short_name(row.get('service', ''))
            cost = row.get('blended_cost_amount', 0)
            
            analysis += f"| {date} | {service} | {self.format_currency(cost)} | - |\n"
        
        return analysis

    def analyze_usage_types(self) -> str:
        """사용량 타입별 분석"""
        usage_data = self.load_json_data(self.data_files['usage_type_monthly'])
        
        if not usage_data:
            return """---

## 📈 사용량 타입별 상세 분석

### 서비스 사용 타입별 비용 분석
❌ 사용 타입별 비용 데이터를 찾을 수 없습니다.

"""
        
        rows = usage_data['rows'][:15]  # 상위 15개
        usage_type_count = len(usage_data['rows'])
        total_cost = self.cost_stats['total_monthly_cost']
        
        analysis = f"""---

## 📈 사용량 타입별 상세 분석

### 서비스 사용 타입별 비용 분석

**📊 사용 타입별 통계**
- **총 사용 타입 수**: {usage_type_count}개
- **분석 기간**: 현재 월 ({datetime.now().strftime('%Y-%m')})

#### 📋 상위 사용 타입별 월간 비용

| 순위 | 서비스 | 사용 타입 | 월간 비용 (USD) | 비용 비율 |
|------|--------|-----------|----------------|-----------|
"""
        
        for i, row in enumerate(rows, 1):
            service = self.get_service_short_name(row.get('service', ''))
            usage_type = row.get('usage_type', '')[:30]  # 30자로 제한
            cost = row.get('blended_cost_amount', 0)
            percentage = self.calculate_percentage(cost, total_cost)
            
            analysis += f"| {i} | {service} | {usage_type} | {self.format_currency(cost)} | {percentage}% |\n"
        
        # 최적화 권장사항
        analysis += """
#### 💡 사용 타입별 최적화 권장사항

**EC2 관련 최적화**:
"""
        
        # EC2, Network Firewall, VPC 비용 계산
        ec2_cost = sum(row.get('blended_cost_amount', 0) for row in usage_data['rows'] if 'Elastic Compute Cloud' in row.get('service', ''))
        nfw_cost = sum(row.get('blended_cost_amount', 0) for row in usage_data['rows'] if 'Network Firewall' in row.get('service', ''))
        vpc_cost = sum(row.get('blended_cost_amount', 0) for row in usage_data['rows'] if 'Virtual Private Cloud' in row.get('service', ''))
        
        if ec2_cost > 0:
            analysis += f"- EC2 총 비용: {self.format_currency(ec2_cost)} - 인스턴스 타입 최적화 및 Spot Instance 활용 검토\n"
            analysis += "- Reserved Instance 구매를 통한 최대 75% 비용 절감 가능\n"
        
        if nfw_cost > 0:
            analysis += f"- Network Firewall 비용: {self.format_currency(nfw_cost)} - 정책 최적화 및 불필요한 규칙 정리 권장\n"
        
        if vpc_cost > 0:
            analysis += f"- VPC 네트워킹 비용: {self.format_currency(vpc_cost)} - NAT Gateway 최적화 및 VPC Endpoint 활용 검토\n"
        
        return analysis

    def analyze_record_types(self) -> str:
        """레코드 타입별 분석"""
        record_data = self.load_json_data(self.data_files['record_type_monthly'])
        
        if not record_data:
            return """---

## 📋 레코드 타입별 비용 분석

### 비용 구성 요소 분석
❌ 레코드 타입별 비용 데이터를 찾을 수 없습니다.

"""
        
        rows = record_data['rows']
        total_cost = self.cost_stats['total_monthly_cost']
        
        analysis = """---

## 📋 레코드 타입별 비용 분석

### 비용 구성 요소 분석

#### 📊 레코드 타입별 월간 비용

| 레코드 타입 | 월간 비용 (USD) | 비용 비율 | 설명 |
|-------------|----------------|-----------|------|
"""
        
        record_descriptions = {
            'Usage': '실제 서비스 사용량 기반 비용',
            'Tax': '세금 및 부가세',
            'Credit': '크레딧 및 할인',
            'Fee': '서비스 수수료'
        }
        
        for row in rows:
            record_type = row.get('record_type', '')
            cost = row.get('blended_cost_amount', 0)
            percentage = self.calculate_percentage(cost, total_cost)
            description = record_descriptions.get(record_type, '기타 비용 항목')
            
            analysis += f"| {record_type} | {self.format_currency(cost)} | {percentage}% | {description} |\n"
        
        return analysis

    def generate_recommendations(self) -> str:
        """비용 최적화 권장사항 생성"""
        service_data = self.load_json_data(self.data_files['service_monthly'])
        
        recommendations = """---

## 💡 비용 최적화 권장사항

### 🔴 높은 우선순위 (즉시 조치)

#### 주요 서비스 최적화
"""
        
        if service_data:
            rows = service_data['rows']
            
            # 주요 서비스별 최적화 권장사항
            for row in rows:
                service = row.get('service', '')
                cost = row.get('blended_cost_amount', 0)
                
                if 'Elastic Compute Cloud' in service and cost > 200:
                    recommendations += f"1. **EC2 인스턴스 최적화**: 월 {self.format_currency(cost)} - Reserved Instance로 최대 75% 절감 가능\n"
                    recommendations += "   - 인스턴스 타입 적정성 검토\n"
                    recommendations += "   - Spot Instance 활용 검토\n"
                    recommendations += "   - 미사용 인스턴스 정리\n"
                    break
            
            for row in rows:
                service = row.get('service', '')
                cost = row.get('blended_cost_amount', 0)
                
                if 'Network Firewall' in service and cost > 100:
                    recommendations += f"2. **Network Firewall 최적화**: 월 {self.format_currency(cost)} - 정책 및 규칙 최적화 필요\n"
                    recommendations += "   - 불필요한 방화벽 규칙 정리\n"
                    recommendations += "   - 방화벽 엔드포인트 수 최적화\n"
                    break
            
            for row in rows:
                service = row.get('service', '')
                cost = row.get('blended_cost_amount', 0)
                
                if 'Virtual Private Cloud' in service and cost > 50:
                    recommendations += f"3. **VPC 네트워킹 최적화**: 월 {self.format_currency(cost)} - NAT Gateway 및 데이터 전송 최적화\n"
                    recommendations += "   - NAT Gateway를 NAT Instance로 대체 검토\n"
                    recommendations += "   - VPC Endpoint 활용으로 데이터 전송 비용 절감\n"
                    break
        
        recommendations += """
### 🟡 중간 우선순위 (1-3개월 내)

#### 비용 모니터링 및 관리
1. **예산 설정**: 월간 예산 알림 설정으로 비용 초과 방지
2. **Cost Explorer 활용**: 정기적인 비용 트렌드 분석
3. **태그 기반 비용 관리**: 리소스 태깅을 통한 부서별/프로젝트별 비용 추적
4. **Reserved Instance 계획**: 장기 사용 리소스에 대한 RI 구매 계획 수립

#### 자동화 및 스케줄링
1. **Auto Scaling 최적화**: 수요에 따른 자동 확장/축소 설정
2. **스케줄링 기반 운영**: 개발/테스트 환경의 시간 기반 운영
3. **Lambda 활용**: 서버리스 아키텍처로 비용 효율성 개선

### 🟢 낮은 우선순위 (장기 계획)

#### 아키텍처 최적화
1. **서버리스 마이그레이션**: 적절한 워크로드의 서버리스 전환
2. **컨테이너화**: ECS/EKS를 통한 리소스 효율성 개선
3. **멀티 리전 최적화**: 지역별 비용 효율성을 고려한 리소스 배치

"""
        return recommendations

    def generate_cost_forecast(self) -> str:
        """비용 예측 및 목표 생성"""
        total_cost = self.cost_stats['total_monthly_cost']
        current_day = datetime.now().day
        days_in_month = 30  # 평균 월 일수
        
        projected_cost = total_cost * days_in_month / current_day if current_day > 0 else total_cost
        daily_avg = total_cost / current_day if current_day > 0 else 0
        
        forecast = f"""---

## 📊 비용 예측 및 목표

### 월간 비용 예측
- **현재까지 비용**: {self.format_currency(total_cost)} USD ({current_day}일 기준)
- **월말 예상 비용**: {self.format_currency(projected_cost)} USD
- **일평균 비용**: {self.format_currency(daily_avg)} USD

### 비용 절감 목표
- **단기 목표 (3개월)**: 월간 비용 10-15% 절감 ({self.format_currency(projected_cost * 0.1)}-{self.format_currency(projected_cost * 0.15)} 절약)
- **중기 목표 (6개월)**: Reserved Instance 활용으로 20-30% 절감
- **장기 목표 (1년)**: 아키텍처 최적화로 전체 비용 30-40% 절감

---

## 💰 투자 우선순위 및 ROI 분석

### 비용 대비 효과 분석
1. **즉시 적용 가능 (무료)**
   - 미사용 리소스 정리
   - 인스턴스 타입 최적화
   - 스케줄링 기반 운영

2. **저비용 고효과 (월 $10-50)**
   - 예산 알림 설정
   - CloudWatch 모니터링 강화
   - 자동화 스크립트 구현

3. **중간 투자 (월 $50-200)**
   - Reserved Instance 구매
   - Savings Plans 활용
   - 전문 비용 최적화 도구

4. **고투자 장기 효과 (월 $200+)**
   - 아키텍처 재설계
   - 멀티 클라우드 전략
   - 전문 컨설팅 서비스

---

*📅 분석 완료 시간: {self.current_time}*  
*🔄 다음 비용 검토 권장 주기: 주 1회*  
*💰 비용 최적화 목표: 월간 비용 20% 절감*

---
"""
        return forecast

    def generate_report(self) -> str:
        """전체 보고서 생성"""
        self.logger.info("💰 Enhanced Cost Analysis 보고서 생성 시작...")
        
        # 비용 데이터 분석
        self.analyze_cost_data()
        
        # 각 섹션 생성
        executive_summary = self.generate_executive_summary()
        service_analysis = self.analyze_service_costs()
        daily_trends = self.analyze_daily_trends()
        usage_analysis = self.analyze_usage_types()
        record_analysis = self.analyze_record_types()
        recommendations = self.generate_recommendations()
        forecast = self.generate_cost_forecast()
        
        # 전체 보고서 조합
        full_report = (
            executive_summary +
            service_analysis +
            daily_trends +
            usage_analysis +
            record_analysis +
            recommendations +
            forecast
        )
        
        return full_report

    def save_report(self, content: str, filename: str = "07-cost-analysis.md") -> None:
        """보고서를 파일로 저장"""
        output_path = self.report_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"✅ Enhanced Cost Analysis 생성 완료: {filename}")
            
            # 파일 크기 정보
            file_size = output_path.stat().st_size
            self.logger.info(f"📄 보고서 크기: {file_size:,} bytes")
            
        except Exception as e:
            self.logger.error(f"❌ 보고서 저장 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    try:
        # 보고서 생성기 초기화
        generator = CostReportGenerator()
        
        # 보고서 생성
        report_content = generator.generate_report()
        
        # 보고서 저장
        generator.save_report(report_content)
        
        print("🎉 Enhanced Cost Analysis 보고서 생성이 완료되었습니다!")
        
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
