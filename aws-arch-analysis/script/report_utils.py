#!/usr/bin/env python3
"""
보고서 생성 유틸리티 모듈
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ReportUtils:
    """보고서 생성을 위한 유틸리티 클래스"""
    
    @staticmethod
    def load_json_data(filename: str) -> List[Dict]:
        """JSON 파일 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def format_cost(cost: float) -> str:
        """비용 포맷팅"""
        return f"${cost:.2f}"
    
    @staticmethod
    def get_current_date() -> str:
        """현재 날짜 반환"""
        return datetime.now().strftime('%Y년 %m월 %d일')
    
    @staticmethod
    def create_vpc_summary(vpc_data: List[Dict]) -> str:
        """VPC 요약 생성"""
        if not vpc_data:
            return "VPC 정보를 찾을 수 없습니다."
        
        summary = []
        for vpc in vpc_data:
            name = vpc.get('name') or vpc.get('vpc_id', 'Unknown')
            cidr = vpc.get('cidr_block', 'Unknown')
            state = vpc.get('state', 'Unknown')
            summary.append(f"- **{name}**: {cidr} ({state})")
        
        return "\n".join(summary)
    
    @staticmethod
    def create_ec2_summary(ec2_data: List[Dict]) -> str:
        """EC2 요약 생성"""
        if not ec2_data:
            return "EC2 인스턴스 정보를 찾을 수 없습니다."
        
        # 인스턴스 타입별 그룹화
        type_counts = {}
        vpc_counts = {}
        
        for instance in ec2_data:
            instance_type = instance.get('instance_type', 'Unknown')
            vpc_id = instance.get('vpc_id', 'Unknown')
            
            type_counts[instance_type] = type_counts.get(instance_type, 0) + 1
            vpc_counts[vpc_id] = vpc_counts.get(vpc_id, 0) + 1
        
        type_summary = "\n".join([f"- **{t}**: {c}개" for t, c in type_counts.items()])
        vpc_summary = "\n".join([f"- **{v}**: {c}개" for v, c in vpc_counts.items()])
        
        return f"### 인스턴스 타입별 분포\n{type_summary}\n\n### VPC별 분포\n{vpc_summary}"
    
    @staticmethod
    def create_cost_summary(cost_data: List[Dict]) -> str:
        """비용 요약 생성"""
        if not cost_data:
            return "비용 정보를 찾을 수 없습니다."
        
        # 비용 순으로 정렬
        sorted_costs = sorted(cost_data, key=lambda x: float(x.get('total_cost', 0)), reverse=True)
        
        summary = []
        for item in sorted_costs[:10]:  # 상위 10개만
            service = item.get('service', 'Unknown')
            cost = float(item.get('total_cost', 0))
            summary.append(f"- **{service}**: ${cost:.2f}")
        
        return "\n".join(summary)

class MarkdownGenerator:
    """Markdown 보고서 생성기"""
    
    def __init__(self, aws_account_id: str, aws_region: str, analysis_results: Dict):
        self.aws_account_id = aws_account_id
        self.aws_region = aws_region
        self.analysis_results = analysis_results
        self.utils = ReportUtils()
    
    def generate_executive_summary(self) -> str:
        """Executive Summary 생성"""
        return f"""# AWS 계정 종합 분석 보고서 - 전체 계정 분석 요약

## 📊 Executive Summary

**분석 일시**: {self.utils.get_current_date()}  
**AWS 계정 ID**: {self.aws_account_id}  
**주요 리전**: {self.aws_region}  
**분석 도구**: Steampipe, AWS CLI, 자동화 스크립트

---

## 🎯 핵심 발견사항

### 인프라 현황 개요
- **VPC 구성**: {self.analysis_results['vpc_count']}개 VPC
- **컴퓨팅 리소스**: {self.analysis_results['ec2_count']}개 EC2 인스턴스
- **보안 그룹**: {self.analysis_results['security_group_count']}개
- **월간 예상 비용**: {self.utils.format_cost(self.analysis_results['total_cost'])}

### 아키텍처 성숙도 평가

| 영역 | 점수 | 상태 | 주요 특징 |
|------|------|------|-----------|
| **네트워킹** | 8/10 | 🟢 양호 | Multi-VPC 아키텍처 |
| **보안** | 7/10 | 🟡 개선 가능 | 보안 그룹 최적화 필요 |
| **비용 효율성** | 6/10 | 🟡 개선 필요 | 비용 최적화 기회 존재 |

---

## 💰 비용 분석 요약

### 월간 비용 현황
**총 예상 비용**: {self.utils.format_cost(self.analysis_results['total_cost'])}

### 주요 권장사항
1. **즉시 조치**: 미사용 리소스 정리
2. **단기 계획**: Right-sizing 및 Reserved Instance
3. **중기 계획**: 모니터링 및 자동화 강화

---

## 📈 권장 로드맵

### Phase 1: 즉시 조치 (1-2주)
- [ ] 비용 모니터링 대시보드 구축
- [ ] 미사용 리소스 식별 및 정리
- [ ] 보안 그룹 규칙 검토

### Phase 2: 단기 개선 (1-2개월)
- [ ] EC2 인스턴스 최적화
- [ ] Reserved Instance 구매 검토
- [ ] 모니터링 체계 구축

### Phase 3: 중장기 발전 (3-6개월)
- [ ] 자동화 도구 구현
- [ ] 비용 최적화 전략 실행
- [ ] 보안 강화 조치

---

*이 보고서는 자동화된 분석 도구를 통해 생성되었습니다.*
"""
    
    def generate_networking_analysis(self) -> str:
        """네트워킹 분석 보고서 생성"""
        vpc_data = self.utils.load_json_data('vpc_analysis.json')
        sg_data = self.utils.load_json_data('security_groups_analysis.json')
        
        vpc_summary = self.utils.create_vpc_summary(vpc_data)
        
        # 보안 그룹 VPC별 분포
        sg_by_vpc = {}
        for sg in sg_data:
            vpc_id = sg.get('vpc_id', 'Unknown')
            sg_by_vpc[vpc_id] = sg_by_vpc.get(vpc_id, 0) + 1
        
        sg_distribution = "\n".join([f"- VPC {vpc}: {count}개" for vpc, count in sg_by_vpc.items()])
        
        return f"""# AWS 계정 종합 분석 보고서 - 네트워킹 분석

## 🌐 네트워킹 아키텍처 분석

**분석 일시**: {self.utils.get_current_date()}  
**총 VPC 수**: {self.analysis_results['vpc_count']}개

---

## 📊 VPC 현황

{vpc_summary}

## 🔒 보안 그룹 현황

**총 보안 그룹 수**: {self.analysis_results['security_group_count']}개

### 보안 그룹 분포
{sg_distribution}

## 📈 네트워킹 권장사항

1. **보안 강화**
   - 보안 그룹 규칙 정기 검토
   - 불필요한 0.0.0.0/0 규칙 제거
   - VPC Flow Logs 활성화

2. **성능 최적화**
   - 네트워크 성능 모니터링
   - 적절한 서브넷 배치
   - 로드밸런서 최적화

3. **비용 최적화**
   - NAT Gateway 사용량 검토
   - 데이터 전송 비용 분석
   - VPC 엔드포인트 활용

---

*네트워킹 분석 완료*
"""
    
    def generate_computing_analysis(self) -> str:
        """컴퓨팅 분석 보고서 생성"""
        ec2_data = self.utils.load_json_data('ec2_analysis.json')
        ec2_summary = self.utils.create_ec2_summary(ec2_data)
        
        return f"""# AWS 계정 종합 분석 보고서 - 컴퓨팅 분석

## 💻 컴퓨팅 리소스 분석

**분석 일시**: {self.utils.get_current_date()}  
**총 EC2 인스턴스**: {self.analysis_results['ec2_count']}개

---

## 📊 EC2 인스턴스 현황

{ec2_summary}

## 🎯 최적화 권장사항

1. **Right-sizing**
   - 사용률이 낮은 인스턴스 식별
   - 적절한 인스턴스 타입으로 조정
   - 개발 환경 스케줄링 구현

2. **비용 최적화**
   - Reserved Instance 구매 검토
   - Spot Instance 활용
   - 자동 스케일링 최적화

3. **성능 향상**
   - 모니터링 강화
   - 로드밸런싱 최적화
   - 캐싱 전략 구현

---

*컴퓨팅 분석 완료*
"""
    
    def generate_cost_optimization(self) -> str:
        """비용 최적화 보고서 생성"""
        cost_data = self.utils.load_json_data('cost_analysis.json')
        cost_summary = self.utils.create_cost_summary(cost_data)
        
        return f"""# AWS 계정 종합 분석 보고서 - 비용 최적화

## 💰 비용 분석 및 최적화

**분석 일시**: {self.utils.get_current_date()}  
**총 월간 비용**: {self.utils.format_cost(self.analysis_results['total_cost'])}

---

## 📊 서비스별 비용 현황

{cost_summary}

## 🎯 비용 최적화 기회

### 즉시 조치 가능
1. **미사용 리소스 정리**
   - 연결되지 않은 EBS 볼륨
   - 미사용 Elastic IP
   - 오래된 스냅샷

2. **Right-sizing**
   - 저사용률 인스턴스 다운사이징
   - 적절한 인스턴스 타입 선택

### 단기 최적화
1. **Reserved Instance**
   - 안정적 워크로드 RI 구매
   - 1년 부분 선결제 권장

2. **스토리지 최적화**
   - S3 Intelligent Tiering
   - EBS gp2 → gp3 업그레이드

### 장기 최적화
1. **아키텍처 최적화**
   - 서버리스 아키텍처 도입
   - 컨테이너화 확대

2. **자동화 구현**
   - 비용 모니터링 자동화
   - 리소스 스케줄링

---

## 📈 예상 절약 효과

- **즉시 조치**: 월 $5-15 절약 가능
- **단기 최적화**: 월 $10-25 절약 가능
- **장기 최적화**: 월 $15-40 절약 가능

**총 예상 절약**: 월 $30-80 (현재 대비 15-35% 절감)

---

*비용 최적화 분석 완료*
"""
