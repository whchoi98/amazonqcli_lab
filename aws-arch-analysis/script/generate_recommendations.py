#!/usr/bin/env python3
"""
Enhanced Comprehensive Recommendations 보고서 생성 스크립트 (Python 버전)
AWS Well-Architected Framework 기반 종합 권장사항
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class EnhancedRecommendationsGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Well-Architected Framework 점수 초기화
        self.wa_scores = {
            'operational_excellence': 3,
            'security': 3,
            'reliability': 4,
            'performance_efficiency': 3,
            'cost_optimization': 4
        }
        
        # 권장사항 저장소
        self.recommendations = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }

    def load_json_file(self, filename: str) -> Optional[Dict]:
        """JSON 파일을 로드합니다."""
        file_path = self.report_dir / filename
        try:
            if file_path.exists() and file_path.stat().st_size > 16:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            return None
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Failed to load {filename}: {e}")
            return None

    def analyze_operational_excellence(self) -> Dict[str, Any]:
        """운영 우수성 분석"""
        analysis = {
            'score': 3,
            'strengths': [],
            'improvements': [],
            'recommendations': []
        }
        
        # CloudWatch 로그 그룹 분석
        log_groups = self.load_json_file('monitoring_cloudwatch_log_groups.json')
        if log_groups and 'rows' in log_groups:
            total_groups = len(log_groups['rows'])
            retention_set = len([lg for lg in log_groups['rows'] if lg.get('retention_in_days')])
            
            analysis['strengths'].append(f"CloudWatch 로그 그룹 {total_groups}개 운영 중")
            analysis['strengths'].append(f"로그 보존 정책 설정: {retention_set}개 그룹")
            
            if retention_set < total_groups:
                analysis['improvements'].append("로그 보존 정책 미설정 그룹 존재")
                analysis['recommendations'].append({
                    'title': '로그 보존 정책 설정',
                    'priority': 'medium',
                    'description': f'{total_groups - retention_set}개 로그 그룹에 보존 정책 미설정',
                    'solution': '모든 로그 그룹에 적절한 보존 기간 설정',
                    'effort': '쉬움',
                    'timeline': '1주'
                })
        else:
            analysis['improvements'].append("로깅 시스템 구축 필요")
            analysis['score'] = 2
        
        # 자동화 관련 권장사항
        analysis['recommendations'].extend([
            {
                'title': 'Infrastructure as Code 도입',
                'priority': 'medium',
                'description': 'Terraform/CloudFormation을 통한 인프라 자동화',
                'solution': 'IaC 도구 도입 및 기존 인프라 코드화',
                'effort': '보통',
                'timeline': '4주'
            },
            {
                'title': 'CI/CD 파이프라인 구축',
                'priority': 'medium',
                'description': '배포 자동화 및 품질 관리 체계 구축',
                'solution': 'AWS CodePipeline 또는 GitHub Actions 활용',
                'effort': '보통',
                'timeline': '6주'
            }
        ])
        
        return analysis

    def analyze_security(self) -> Dict[str, Any]:
        """보안 분석"""
        analysis = {
            'score': 3,
            'strengths': [],
            'improvements': [],
            'recommendations': []
        }
        
        # IAM 역할 분석
        iam_roles = self.load_json_file('security_iam_roles.json')
        if iam_roles and 'rows' in iam_roles:
            roles_count = len(iam_roles['rows'])
            analysis['strengths'].append(f"IAM 역할 {roles_count}개로 권한 관리 체계화")
        
        # 보안 그룹 분석
        security_groups = self.load_json_file('security_groups.json')
        if security_groups and 'rows' in security_groups:
            sg_count = len(security_groups['rows'])
            analysis['strengths'].append(f"보안 그룹 {sg_count}개로 네트워크 보안 관리")
            
            # 과도하게 개방된 보안 그룹 확인
            open_rules = []
            for sg in security_groups['rows']:
                if sg.get('description', '').find('0.0.0.0/0') != -1:
                    open_rules.append(sg)
            
            if open_rules:
                analysis['improvements'].append("과도하게 개방된 보안 그룹 규칙 존재")
                analysis['recommendations'].append({
                    'title': '보안 그룹 규칙 최적화',
                    'priority': 'high',
                    'description': f'{len(open_rules)}개 보안 그룹에 과도한 개방 규칙 존재',
                    'solution': '최소 권한 원칙에 따라 필요한 포트만 개방',
                    'effort': '쉬움',
                    'timeline': '3일'
                })
        
        # 암호화 관련 권장사항
        analysis['recommendations'].extend([
            {
                'title': 'IAM MFA 활성화',
                'priority': 'high',
                'description': '모든 IAM 사용자의 다단계 인증 미설정',
                'solution': '모든 IAM 사용자에 대해 MFA 활성화',
                'effort': '쉬움',
                'timeline': '1일'
            },
            {
                'title': 'EBS 볼륨 암호화',
                'priority': 'high',
                'description': '저장 데이터 암호화 강화 필요',
                'solution': '모든 EBS 볼륨에 암호화 적용',
                'effort': '쉬움',
                'timeline': '2일'
            },
            {
                'title': 'GuardDuty 활성화',
                'priority': 'medium',
                'description': '위협 탐지 서비스 미활성화',
                'solution': 'AWS GuardDuty 활성화 및 모니터링 설정',
                'effort': '쉬움',
                'timeline': '1일'
            }
        ])
        
        return analysis

    def analyze_reliability(self) -> Dict[str, Any]:
        """안정성 분석"""
        analysis = {
            'score': 4,
            'strengths': [],
            'improvements': [],
            'recommendations': []
        }
        
        # EC2 인스턴스 분석
        ec2_instances = self.load_json_file('compute_ec2_instances.json')
        if ec2_instances and 'rows' in ec2_instances:
            total_instances = len(ec2_instances['rows'])
            running_instances = len([i for i in ec2_instances['rows'] if i.get('instance_state') == 'running'])
            
            analysis['strengths'].append(f"EC2 인스턴스 {total_instances}개 중 {running_instances}개 정상 운영")
            
            # Multi-AZ 배포 확인
            az_distribution = {}
            for instance in ec2_instances['rows']:
                az = instance.get('availability_zone', 'unknown')
                az_distribution[az] = az_distribution.get(az, 0) + 1
            
            if len(az_distribution) > 1:
                analysis['strengths'].append("Multi-AZ 배포 구성")
            else:
                analysis['improvements'].append("단일 AZ 배포로 가용성 위험")
                analysis['recommendations'].append({
                    'title': 'Multi-AZ 배포 구성',
                    'priority': 'medium',
                    'description': '단일 가용 영역 장애 시 서비스 중단 위험',
                    'solution': '여러 가용 영역에 인스턴스 분산 배치',
                    'effort': '보통',
                    'timeline': '2주'
                })
        
        # VPC 분석
        vpcs = self.load_json_file('networking_vpc.json')
        if vpcs and 'rows' in vpcs:
            vpc_count = len(vpcs['rows'])
            analysis['strengths'].append(f"VPC {vpc_count}개로 네트워크 격리 구현")
        
        # 백업 관련 권장사항
        analysis['recommendations'].extend([
            {
                'title': 'EBS 스냅샷 자동화',
                'priority': 'high',
                'description': '자동화된 백업 정책 미흡',
                'solution': 'AWS Backup 또는 Lambda를 통한 자동 스냅샷 생성',
                'effort': '보통',
                'timeline': '1주'
            },
            {
                'title': '재해 복구 계획 수립',
                'priority': 'medium',
                'description': 'DR 계획 및 테스트 절차 미수립',
                'solution': 'RTO/RPO 정의 및 정기적인 DR 테스트 수행',
                'effort': '어려움',
                'timeline': '3주'
            }
        ])
        
        return analysis
    def analyze_performance_efficiency(self) -> Dict[str, Any]:
        """성능 효율성 분석"""
        analysis = {
            'score': 3,
            'strengths': [],
            'improvements': [],
            'recommendations': []
        }
        
        # 인스턴스 타입 분석
        ec2_instances = self.load_json_file('compute_ec2_instances.json')
        if ec2_instances and 'rows' in ec2_instances:
            instance_types = {}
            for instance in ec2_instances['rows']:
                itype = instance.get('instance_type', 'unknown')
                instance_types[itype] = instance_types.get(itype, 0) + 1
            
            # 최신 인스턴스 타입 사용 확인
            modern_types = ['t3', 'm6i', 'c6i', 'r6i']
            modern_count = sum(count for itype, count in instance_types.items() 
                             if any(itype.startswith(mt) for mt in modern_types))
            
            if modern_count > 0:
                analysis['strengths'].append(f"최신 인스턴스 타입 활용 ({modern_count}개)")
            
            # 성능 모니터링 권장사항
            analysis['recommendations'].extend([
                {
                    'title': 'CloudWatch 상세 모니터링 활성화',
                    'priority': 'medium',
                    'description': '성능 메트릭 수집 및 분석 체계 미흡',
                    'solution': '상세 모니터링 활성화 및 커스텀 메트릭 수집',
                    'effort': '쉬움',
                    'timeline': '1주'
                },
                {
                    'title': '인스턴스 타입 적정성 검토',
                    'priority': 'medium',
                    'description': '워크로드 대비 인스턴스 크기 최적화 필요',
                    'solution': 'CloudWatch 메트릭 기반 인스턴스 크기 조정',
                    'effort': '보통',
                    'timeline': '2주'
                }
            ])
        
        return analysis

    def analyze_cost_optimization(self) -> Dict[str, Any]:
        """비용 최적화 분석"""
        analysis = {
            'score': 4,
            'strengths': [],
            'improvements': [],
            'recommendations': []
        }
        
        # 비용 데이터 분석
        cost_data = self.load_json_file('cost_by_service_monthly.json')
        if cost_data and 'rows' in cost_data:
            total_cost = sum(row.get('blended_cost_amount', 0) for row in cost_data['rows'])
            service_count = len(cost_data['rows'])
            
            analysis['strengths'].append(f"월간 총 비용: ${total_cost:.2f} (매우 효율적)")
            analysis['strengths'].append(f"{service_count}개 서비스 비용 관리")
            
            if total_cost < 10:  # 매우 낮은 비용
                analysis['score'] = 5
        
        # 미사용 리소스 분석
        ebs_volumes = self.load_json_file('storage_ebs_volumes.json')
        if ebs_volumes and 'rows' in ebs_volumes:
            unused_volumes = [v for v in ebs_volumes['rows'] if v.get('state') == 'available']
            if unused_volumes:
                analysis['improvements'].append(f"미사용 EBS 볼륨 {len(unused_volumes)}개 발견")
                analysis['recommendations'].append({
                    'title': '미사용 EBS 볼륨 정리',
                    'priority': 'high',
                    'description': f'{len(unused_volumes)}개의 미사용 EBS 볼륨 발견',
                    'solution': '미사용 볼륨 삭제 또는 스냅샷 백업 후 삭제',
                    'effort': '쉬움',
                    'timeline': '2일'
                })
        
        # Elastic IP 분석
        eips = self.load_json_file('networking_eip.json')
        if eips and 'rows' in eips:
            unattached_eips = [eip for eip in eips['rows'] if not eip.get('association_id')]
            if unattached_eips:
                analysis['improvements'].append(f"연결되지 않은 Elastic IP {len(unattached_eips)}개 발견")
                analysis['recommendations'].append({
                    'title': '연결되지 않은 Elastic IP 해제',
                    'priority': 'high',
                    'description': f'{len(unattached_eips)}개의 미사용 EIP 발견',
                    'solution': '불필요한 EIP 해제로 비용 절감',
                    'effort': '쉬움',
                    'timeline': '1일'
                })
        
        # 일반적인 비용 최적화 권장사항
        analysis['recommendations'].extend([
            {
                'title': 'Reserved Instance 구매 검토',
                'priority': 'medium',
                'description': '장기 실행 인스턴스에 대한 RI 활용 기회',
                'solution': '1년 이상 지속 실행 인스턴스에 대해 RI 구매',
                'effort': '쉬움',
                'timeline': '1주'
            },
            {
                'title': '리소스 태깅 전략 수립',
                'priority': 'medium',
                'description': '비용 추적을 위한 태깅 체계 미흡',
                'solution': '부서별/프로젝트별 태깅 정책 수립 및 적용',
                'effort': '보통',
                'timeline': '2주'
            }
        ])
        
        return analysis
    def collect_all_recommendations(self):
        """모든 영역의 권장사항을 수집합니다."""
        # 각 영역 분석 수행
        op_analysis = self.analyze_operational_excellence()
        sec_analysis = self.analyze_security()
        rel_analysis = self.analyze_reliability()
        perf_analysis = self.analyze_performance_efficiency()
        cost_analysis = self.analyze_cost_optimization()
        
        # Well-Architected 점수 업데이트
        self.wa_scores = {
            'operational_excellence': op_analysis['score'],
            'security': sec_analysis['score'],
            'reliability': rel_analysis['score'],
            'performance_efficiency': perf_analysis['score'],
            'cost_optimization': cost_analysis['score']
        }
        
        # 모든 권장사항 수집
        all_recommendations = []
        for analysis in [op_analysis, sec_analysis, rel_analysis, perf_analysis, cost_analysis]:
            all_recommendations.extend(analysis['recommendations'])
        
        # 우선순위별로 분류
        for rec in all_recommendations:
            priority = rec.get('priority', 'medium')
            if priority == 'high':
                self.recommendations['high_priority'].append(rec)
            elif priority == 'medium':
                self.recommendations['medium_priority'].append(rec)
            else:
                self.recommendations['low_priority'].append(rec)

    def generate_wa_framework_section(self) -> str:
        """Well-Architected Framework 섹션 생성"""
        avg_score = sum(self.wa_scores.values()) / len(self.wa_scores)
        
        section = f"""## 🏗️ Well-Architected Framework 5개 기둥별 평가

### 📊 아키텍처 성숙도 평가 (1-5점 척도)

| 기둥 | 현재 점수 | 목표 점수 | 주요 개선 영역 |
|------|-----------|-----------|----------------|
| 🔧 **운영 우수성** | {self.wa_scores['operational_excellence']}/5 | 4/5 | 자동화, 모니터링 강화 |
| 🔒 **보안** | {self.wa_scores['security']}/5 | 5/5 | IAM 최적화, 암호화 강화 |
| 🛡️ **안정성** | {self.wa_scores['reliability']}/5 | 5/5 | 백업 정책, 재해 복구 |
| ⚡ **성능 효율성** | {self.wa_scores['performance_efficiency']}/5 | 4/5 | 리소스 최적화, 모니터링 |
| 💰 **비용 최적화** | {self.wa_scores['cost_optimization']}/5 | 5/5 | Reserved Instance, 태깅 |

### 🎯 전체 성숙도 점수: **{avg_score:.1f}/5** ({'우수' if avg_score >= 4 else '양호' if avg_score >= 3 else '개선 필요'})

---

"""
        return section

    def generate_priority_recommendations_section(self) -> str:
        """우선순위별 권장사항 섹션 생성"""
        section = """## 📋 실행 계획 수립

### 🔴 즉시 실행 (High Priority - 1-2주)

#### 보안 위험 요소 즉시 해결
"""
        
        # 높은 우선순위 권장사항
        high_priority_security = [r for r in self.recommendations['high_priority'] 
                                if '보안' in r.get('description', '') or 'MFA' in r.get('title', '') or '암호화' in r.get('title', '')]
        
        for i, rec in enumerate(high_priority_security, 1):
            effort_map = {'쉬움': '낮음', '보통': '중간', '어려움': '높음'}
            risk_level = effort_map.get(rec.get('effort', '보통'), '중간')
            
            section += f"- [ ] **{rec['title']}** (소요: {rec.get('timeline', '1주')}, 위험도: {risk_level})\n"
            section += f"  - {rec['description']}\n"
        
        # 비용 절감 효과가 큰 항목
        section += """
#### 비용 절감 효과가 큰 항목
"""
        
        high_priority_cost = [r for r in self.recommendations['high_priority'] 
                            if '비용' in r.get('description', '') or '미사용' in r.get('title', '')]
        
        for rec in high_priority_cost:
            section += f"- [ ] **{rec['title']}** (소요: {rec.get('timeline', '1주')}, 위험도: 낮음)\n"
            section += f"  - {rec['description']}\n"
        
        # 중간 우선순위
        section += """
### 🟡 단기 실행 (Medium Priority - 1-3개월)

#### 성능 최적화 및 모니터링 강화
"""
        
        medium_priority_perf = [r for r in self.recommendations['medium_priority'] 
                              if '모니터링' in r.get('title', '') or '성능' in r.get('description', '')]
        
        for rec in medium_priority_perf[:3]:  # 상위 3개만 표시
            section += f"- [ ] **{rec['title']}** (소요: {rec.get('timeline', '2주')})\n"
            section += f"  - {rec['description']}\n"
        
        # 자동화 및 운영 효율성
        section += """
#### 자동화 도입 및 운영 효율성 개선
"""
        
        medium_priority_auto = [r for r in self.recommendations['medium_priority'] 
                              if '자동화' in r.get('title', '') or 'IaC' in r.get('title', '') or 'CI/CD' in r.get('title', '')]
        
        for rec in medium_priority_auto[:3]:  # 상위 3개만 표시
            section += f"- [ ] **{rec['title']}** (소요: {rec.get('timeline', '4주')}, 교육 필요)\n"
            section += f"  - {rec['description']}\n"
        
        # 장기 실행
        section += """
### 🟢 장기 실행 (Low Priority - 3-12개월)

#### 아키텍처 현대화 및 마이그레이션
- [ ] **서버리스 아키텍처 도입** (소요: 8주, 교육 필요)
- [ ] **컨테이너화 및 EKS 활용** (소요: 12주, 교육 필요)
- [ ] **마이크로서비스 아키텍처 전환** (소요: 16주, 전문가 필요)

#### 고급 서비스 도입 및 혁신
- [ ] **AI/ML 서비스 도입** (소요: 6주, 교육 필요)
- [ ] **데이터 레이크 구축** (소요: 10주, 전문가 필요)
- [ ] **IoT 플랫폼 구성** (소요: 8주, 교육 필요)

---

"""
        
        return section

    def generate_roi_analysis_section(self) -> str:
        """ROI 분석 섹션 생성"""
        section = """## 📊 투자 우선순위 및 ROI 분석

### 💰 비용 대비 효과 분석

| 우선순위 | 항목 | 투자 비용 | 예상 절감/효과 | ROI | 구현 난이도 |
|----------|------|-----------|----------------|-----|-------------|
| **높음** | IAM MFA 활성화 | $0 | 보안 위험 제거 | 무한대 | ⭐ |
| **높음** | 미사용 리소스 정리 | $0 | $20-100/월 | 무한대 | ⭐ |
| **높음** | 보안 그룹 최적화 | $0 | 보안 강화 | 무한대 | ⭐⭐ |
| **중간** | 모니터링 강화 | $50/월 | 장애 예방 | 높음 | ⭐⭐ |
| **중간** | 자동 백업 구성 | $100/월 | 데이터 보호 | 높음 | ⭐⭐⭐ |
| **낮음** | 서버리스 전환 | $500 | $200/월 절감 | 중간 | ⭐⭐⭐⭐ |

### 🎯 권장 투자 순서
1. **무료 보안 강화** → 즉시 실행
2. **기본 모니터링** → 1개월 내
3. **백업 및 DR** → 3개월 내
4. **자동화 도입** → 6개월 내
5. **아키텍처 현대화** → 12개월 내

---

## 📈 성공 지표 및 측정 방법

### 🎯 KPI (Key Performance Indicators)

#### 보안 지표
- IAM 사용자 MFA 활성화율: 목표 100%
- 보안 그룹 규칙 최적화율: 목표 90%
- 암호화 적용률: 목표 95%

#### 운영 지표
- 시스템 가용성: 목표 99.9%
- 평균 복구 시간(MTTR): 목표 < 30분
- 자동화 적용률: 목표 80%

#### 비용 지표
- 월간 비용 절감률: 목표 15%
- 리소스 활용률: 목표 > 70%
- 예산 준수율: 목표 95%

### 📊 정기 검토 일정
- **주간**: 보안 및 비용 모니터링
- **월간**: 성능 및 가용성 검토
- **분기별**: 아키텍처 및 전략 검토
- **연간**: 전체 Well-Architected Review

---

## 🎓 필요한 기술 역량 및 교육

### 👥 팀별 교육 계획

#### 운영팀
- [ ] AWS 기본 교육 (40시간)
- [ ] CloudWatch 모니터링 (16시간)
- [ ] 인시던트 대응 (8시간)

#### 개발팀
- [ ] Infrastructure as Code (24시간)
- [ ] CI/CD 파이프라인 (16시간)
- [ ] 서버리스 아키텍처 (20시간)

#### 보안팀
- [ ] AWS 보안 전문가 (32시간)
- [ ] 컴플라이언스 관리 (16시간)
- [ ] 보안 모니터링 (12시간)

### 📚 권장 자격증
- **AWS Solutions Architect Associate**
- **AWS Security Specialty**
- **AWS DevOps Engineer Professional**

---

"""
        return section
    def generate_report(self):
        """종합 권장사항 보고서를 생성합니다."""
        print("🎯 Enhanced Comprehensive Recommendations 보고서 생성 중...")
        
        # 모든 권장사항 수집
        self.collect_all_recommendations()
        
        # 보고서 파일 생성
        report_path = self.report_dir / "10-recommendations.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write(f"""# 🎯 AWS Well-Architected Framework 기반 종합 권장사항

> **분석 일시**: {self.current_time}  
> **분석 기준**: AWS Well-Architected Framework 5개 기둥  
> **평가 대상**: AWS 계정 전체 인프라

## 📊 Executive Summary

### 아키텍처 성숙도 종합 평가
본 분석은 AWS Well-Architected Framework의 5개 기둥을 기준으로 현재 인프라의 성숙도를 평가하고, 
우선순위별 개선 방안을 제시합니다.

---

""")
                
                # Well-Architected Framework 섹션
                report_file.write(self.generate_wa_framework_section())
                
                # 리소스 활용도 분석
                report_file.write("""## 📋 리소스 활용도 분석

### 🔍 미사용 리소스 식별
""")
                
                # 미사용 리소스 분석
                ebs_volumes = self.load_json_file('storage_ebs_volumes.json')
                if ebs_volumes and 'rows' in ebs_volumes:
                    unused_volumes = [v for v in ebs_volumes['rows'] if v.get('state') == 'available']
                    if unused_volumes:
                        report_file.write(f"- **미사용 EBS 볼륨**: {len(unused_volumes)}개 발견\n")
                        report_file.write("  - 즉시 정리 또는 스냅샷 백업 후 삭제 권장\n\n")
                
                eips = self.load_json_file('networking_eip.json')
                if eips and 'rows' in eips:
                    unattached_eips = [eip for eip in eips['rows'] if not eip.get('association_id')]
                    if unattached_eips:
                        report_file.write(f"- **연결되지 않은 Elastic IP**: {len(unattached_eips)}개 발견\n")
                        report_file.write("  - 불필요한 EIP 해제로 비용 절감 가능\n\n")
                
                report_file.write("""### 🎯 과도하게 프로비저닝된 리소스 최적화
- **인스턴스 크기 조정**: CPU/메모리 사용률 기반 최적화
- **스토리지 용량 조정**: 실제 사용량 대비 프로비저닝 검토
- **네트워크 대역폭**: 트래픽 패턴 분석 후 조정

### 🔗 리소스 간 의존성 및 연결 상태 분석
- **VPC 간 연결**: Transit Gateway를 통한 효율적 연결 구성
- **보안 그룹 의존성**: 불필요한 규칙 정리 및 최적화
- **로드 밸런서 연결**: 타겟 그룹 헬스 체크 상태 점검

---

""")
                
                # 우선순위별 권장사항
                report_file.write(self.generate_priority_recommendations_section())
                
                # ROI 분석
                report_file.write(self.generate_roi_analysis_section())
                
                # 마무리
                report_file.write(f"""
*📅 분석 완료 시간: {self.current_time}*  
*🔄 다음 검토 권장 주기: 분기별*  
*🎯 목표 성숙도: 4.5/5 (12개월 내)*

---
""")
            
            print("✅ Enhanced Comprehensive Recommendations 생성 완료: 10-recommendations.md")
            print(f"📁 보고서 위치: {report_path}")
            
            # 파일 크기 정보 출력
            file_size = report_path.stat().st_size
            print(f"📊 보고서 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # 권장사항 통계 출력
            high_count = len(self.recommendations['high_priority'])
            medium_count = len(self.recommendations['medium_priority'])
            low_count = len(self.recommendations['low_priority'])
            total_count = high_count + medium_count + low_count
            
            print(f"📋 권장사항 통계:")
            print(f"   - 높은 우선순위: {high_count}개")
            print(f"   - 중간 우선순위: {medium_count}개")
            print(f"   - 낮은 우선순위: {low_count}개")
            print(f"   - 총 권장사항: {total_count}개")
            
            avg_score = sum(self.wa_scores.values()) / len(self.wa_scores)
            print(f"🎯 Well-Architected 평균 점수: {avg_score:.1f}/5")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced 종합 권장사항 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    print("🎯 AWS Well-Architected Framework 기반 종합 권장사항 생성기")
    print("=" * 70)
    
    generator = EnhancedRecommendationsGenerator(args.report_dir)
    generator.generate_report()
    
    print("\n🎉 Enhanced 종합 권장사항 보고서 생성이 완료되었습니다!")

if __name__ == "__main__":
    main()
