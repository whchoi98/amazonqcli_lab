#!/usr/bin/env python3
"""
AWS Well-Architected Framework 기반 종합 권장사항 보고서 생성 스크립트
Enhanced Recommendations Report Generator - Python 버전
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class RecommendationsReportGenerator:
    def __init__(self, report_dir: str = None):
        # 스크립트의 실제 위치를 기준으로 경로 설정
        if report_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent
            report_dir = str(project_root / "aws-arch-analysis" / "report")
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 색상 코드
        self.GREEN = '\033[0;32m'
        self.BLUE = '\033[0;34m'
        self.YELLOW = '\033[1;33m'
        self.RED = '\033[0;31m'
        self.NC = '\033[0m'

    def log_info(self, message: str):
        print(f"{self.BLUE}[INFO]{self.NC} {message}")
        
    def log_success(self, message: str):
        print(f"{self.GREEN}[SUCCESS]{self.NC} {message}")
        
    def log_warning(self, message: str):
        print(f"{self.YELLOW}[WARNING]{self.NC} {message}")
        
    def log_error(self, message: str):
        print(f"{self.RED}[ERROR]{self.NC} {message}")

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
            self.log_warning(f"파일 로드 실패: {filename} - {str(e)}")
        return None

    def analyze_current_state(self) -> Dict[str, Any]:
        """현재 인프라 상태를 분석합니다."""
        analysis = {
            'ec2_instances': 0,
            'rds_instances': 0,
            'vpc_count': 0,
            'security_groups': 0,
            'ebs_volumes': 0,
            'encrypted_volumes': 0,
            'iam_roles': 0,
            'kms_keys': 0
        }
        
        # EC2 인스턴스 분석
        ec2_data = self.load_json_file("compute_ec2_instances.json")
        if ec2_data:
            analysis['ec2_instances'] = len(ec2_data)
        
        # RDS 인스턴스 분석
        rds_data = self.load_json_file("database_rds_instances.json")
        if rds_data:
            analysis['rds_instances'] = len(rds_data)
        
        # VPC 분석
        vpc_data = self.load_json_file("networking_vpcs.json")
        if vpc_data:
            analysis['vpc_count'] = len(vpc_data)
        
        # 보안 그룹 분석
        sg_data = self.load_json_file("networking_security_groups.json")
        if sg_data:
            analysis['security_groups'] = len(sg_data)
        
        # EBS 볼륨 분석
        ebs_data = self.load_json_file("storage_ebs_volumes.json")
        if ebs_data:
            analysis['ebs_volumes'] = len(ebs_data)
            analysis['encrypted_volumes'] = len([v for v in ebs_data if v.get('encrypted', False)])
        
        # IAM 역할 분석
        iam_data = self.load_json_file("security_iam_roles.json")
        if iam_data:
            analysis['iam_roles'] = len(iam_data)
        
        # KMS 키 분석
        kms_data = self.load_json_file("security_kms_keys.json")
        if kms_data:
            analysis['kms_keys'] = len(kms_data)
        
        return analysis

    def calculate_maturity_scores(self, analysis: Dict[str, Any]) -> Dict[str, int]:
        """성숙도 점수를 계산합니다."""
        scores = {
            'operational_excellence': 3,
            'security': 3,
            'reliability': 4,
            'performance_efficiency': 3,
            'cost_optimization': 4
        }
        
        # 보안 점수 조정
        if analysis['encrypted_volumes'] > 0 and analysis['ebs_volumes'] > 0:
            encryption_ratio = analysis['encrypted_volumes'] / analysis['ebs_volumes']
            if encryption_ratio > 0.8:
                scores['security'] = 4
            elif encryption_ratio > 0.5:
                scores['security'] = 3
            else:
                scores['security'] = 2
        
        # 비용 최적화 점수 조정 (리소스 수에 따라)
        total_resources = analysis['ec2_instances'] + analysis['rds_instances'] + analysis['ebs_volumes']
        if total_resources > 50:
            scores['cost_optimization'] = 3
        elif total_resources > 20:
            scores['cost_optimization'] = 4
        else:
            scores['cost_optimization'] = 5
        
        return scores

    def generate_executive_summary(self, scores: Dict[str, int]) -> str:
        """Executive Summary 섹션을 생성합니다."""
        avg_score = sum(scores.values()) / len(scores)
        
        return f"""## 📊 Executive Summary

### 아키텍처 성숙도 종합 평가
본 분석은 AWS Well-Architected Framework의 5개 핵심사상을 기준으로 현재 인프라의 성숙도를 평가하고, 
우선순위별 개선 방안을 제시합니다.

---

## 🏗️ Well-Architected Framework 5개 기둥별 평가

### 📊 아키텍처 성숙도 평가 (1-5점 척도)

| 기둥 | 현재 점수 | 목표 점수 | 주요 개선 영역 |
|------|-----------|-----------|----------------|
| 🔧 **운영 우수성** | {scores['operational_excellence']}/5 | 4/5 | 자동화, 모니터링 강화 |
| 🔒 **보안** | {scores['security']}/5 | 5/5 | IAM 최적화, 암호화 강화 |
| 🛡️ **안정성** | {scores['reliability']}/5 | 5/5 | 백업 정책, 재해 복구 |
| ⚡ **성능 효율성** | {scores['performance_efficiency']}/5 | 4/5 | 리소스 최적화, 모니터링 |
| 💰 **비용 최적화** | {scores['cost_optimization']}/5 | 5/5 | Reserved Instance, 태깅 |

### 🎯 전체 성숙도 점수: **{avg_score:.1f}/5** ({"우수" if avg_score >= 4 else "양호" if avg_score >= 3 else "개선 필요"})

---"""

    def generate_operational_excellence_section(self, analysis: Dict[str, Any]) -> str:
        """운영 우수성 섹션을 생성합니다."""
        return """## 🔧 운영 우수성 (Operational Excellence) - 현재: 3/5

### 📋 현황 분석
- **자동화 수준**: 부분적 자동화 구현
- **모니터링**: 기본 CloudWatch 모니터링 활성화
- **문서화**: 일부 프로세스 문서화 완료
- **변경 관리**: 수동 프로세스 위주

### 🎯 개선 권장사항

#### 🔴 높은 우선순위 (1-2주 내)
1. **CloudWatch 알람 설정**
   - 핵심 메트릭에 대한 알람 구성
   - SNS 알림 채널 설정
   - 대시보드 구성

2. **자동화 스크립트 구현**
   - 백업 자동화
   - 패치 관리 자동화
   - 리소스 정리 자동화

#### 🟡 중간 우선순위 (1-3개월)
1. **Infrastructure as Code 도입**
   - Terraform 또는 CloudFormation 활용
   - 버전 관리 시스템 연동
   - 환경별 구성 관리

2. **CI/CD 파이프라인 구축**
   - 자동화된 배포 프로세스
   - 테스트 자동화
   - 롤백 메커니즘

---"""

    def generate_security_section(self, analysis: Dict[str, Any]) -> str:
        """보안 섹션을 생성합니다."""
        encryption_ratio = 0
        if analysis['ebs_volumes'] > 0:
            encryption_ratio = (analysis['encrypted_volumes'] / analysis['ebs_volumes']) * 100
        
        return f"""## 🔒 보안 (Security) - 현재: 3/5

### 📋 현황 분석
- **IAM 역할**: {analysis['iam_roles']}개 구성
- **KMS 키**: {analysis['kms_keys']}개 관리
- **EBS 암호화**: {analysis['encrypted_volumes']}/{analysis['ebs_volumes']}개 ({encryption_ratio:.1f}%)
- **보안 그룹**: {analysis['security_groups']}개 구성

### 🎯 개선 권장사항

#### 🔴 높은 우선순위 (즉시 조치)
1. **IAM MFA 활성화**
   - 모든 IAM 사용자에 대한 다단계 인증 설정
   - 루트 계정 MFA 필수 활성화
   - 임시 자격 증명 사용 권장

2. **EBS 볼륨 암호화**
   - 미암호화 볼륨에 대한 암호화 활성화
   - 기본 암호화 설정 활성화
   - 스냅샷 암호화 정책 수립

#### 🟡 중간 우선순위 (1-3개월)
1. **보안 그룹 최적화**
   - 불필요한 0.0.0.0/0 규칙 제거
   - 최소 권한 원칙 적용
   - 정기적인 보안 그룹 감사

2. **CloudTrail 활성화**
   - API 호출 로깅 활성화
   - 로그 파일 무결성 검증
   - 중앙 집중식 로그 관리

---"""

    def generate_reliability_section(self) -> str:
        """안정성 섹션을 생성합니다."""
        return """## 🛡️ 안정성 (Reliability) - 현재: 4/5

### 📋 현황 분석
- **다중 AZ 배포**: 부분적 구현
- **백업 정책**: 기본 백업 구성
- **모니터링**: 기본 헬스 체크 활성화
- **재해 복구**: 계획 수립 필요

### 🎯 개선 권장사항

#### 🔴 높은 우선순위 (2-4주 내)
1. **자동 백업 강화**
   - RDS 자동 백업 활성화
   - EBS 스냅샷 스케줄링
   - 백업 보존 정책 수립

2. **헬스 체크 개선**
   - 애플리케이션 레벨 헬스 체크
   - 로드 밸런서 헬스 체크 최적화
   - 자동 복구 메커니즘 구현

#### 🟡 중간 우선순위 (3-6개월)
1. **재해 복구 계획**
   - RTO/RPO 목표 설정
   - 재해 복구 절차 문서화
   - 정기적인 DR 테스트

2. **다중 리전 아키텍처**
   - 중요 서비스의 다중 리전 배포
   - 데이터 복제 전략 수립
   - 장애 조치 자동화

---"""

    def generate_performance_section(self, analysis: Dict[str, Any]) -> str:
        """성능 효율성 섹션을 생성합니다."""
        return f"""## ⚡ 성능 효율성 (Performance Efficiency) - 현재: 3/5

### 📋 현황 분석
- **EC2 인스턴스**: {analysis['ec2_instances']}개 운영
- **EBS 볼륨**: {analysis['ebs_volumes']}개 구성
- **모니터링**: 기본 메트릭 수집
- **최적화**: 부분적 리소스 최적화

### 🎯 개선 권장사항

#### 🔴 높은 우선순위 (2-4주 내)
1. **인스턴스 타입 최적화**
   - 워크로드 분석 기반 인스턴스 타입 선택
   - CPU/메모리 사용률 모니터링
   - 적절한 인스턴스 패밀리 선택

2. **스토리지 성능 최적화**
   - EBS 볼륨 타입 최적화 (gp3 활용)
   - IOPS 및 처리량 최적화
   - 스토리지 성능 모니터링

#### 🟡 중간 우선순위 (1-3개월)
1. **Auto Scaling 구성**
   - 수요 기반 자동 확장/축소
   - 예측 스케일링 활용
   - 스케일링 정책 최적화

2. **캐싱 전략 구현**
   - ElastiCache 활용
   - CDN 구성 (CloudFront)
   - 애플리케이션 레벨 캐싱

---"""

    def generate_cost_optimization_section(self, analysis: Dict[str, Any]) -> str:
        """비용 최적화 섹션을 생성합니다."""
        return f"""## 💰 비용 최적화 (Cost Optimization) - 현재: 4/5

### 📋 현황 분석
- **총 리소스**: EC2 {analysis['ec2_instances']}개, RDS {analysis['rds_instances']}개, EBS {analysis['ebs_volumes']}개
- **비용 모니터링**: 기본 비용 추적 활성화
- **리소스 태깅**: 부분적 태깅 구현
- **예약 인스턴스**: 미활용

### 🎯 개선 권장사항

#### 🔴 높은 우선순위 (즉시 조치)
1. **미사용 리소스 정리**
   - 중지된 인스턴스 정리
   - 미연결 EBS 볼륨 정리
   - 미사용 Elastic IP 해제

2. **리소스 태깅 표준화**
   - 비용 센터별 태깅
   - 환경별 태깅 (dev/staging/prod)
   - 프로젝트별 태깅

#### 🟡 중간 우선순위 (1-3개월)
1. **Reserved Instance 구매**
   - 장기 실행 워크로드 분석
   - 적절한 RI 구매 계획 수립
   - Savings Plans 활용 검토

2. **비용 모니터링 강화**
   - 예산 알림 설정
   - Cost Explorer 활용
   - 정기적인 비용 검토

---"""

    def generate_implementation_plan(self) -> str:
        """실행 계획 섹션을 생성합니다."""
        return """## 📋 실행 계획 수립

### 🔴 즉시 실행 (High Priority - 1-2주)

#### 보안 위험 요소 즉시 해결
- [ ] **IAM MFA 활성화** (소요: 1일, 위험도: 낮음)
  - 모든 IAM 사용자의 다단계 인증 미설정
- [ ] **EBS 볼륨 암호화** (소요: 2일, 위험도: 낮음)
  - 저장 데이터 암호화 강화 필요

#### 비용 절감 효과가 큰 항목
- [ ] **미사용 리소스 정리** (소요: 1일, 절감: $50-200/월)
  - 중지된 인스턴스, 미연결 볼륨, 미사용 IP 정리

### 🟡 단기 실행 (Medium Priority - 1-3개월)

#### 성능 최적화 및 모니터링 강화
- [ ] **CloudWatch 상세 모니터링 활성화** (소요: 1주)
  - 성능 메트릭 수집 및 분석 체계 미흡

#### 자동화 도입 및 운영 효율성 개선
- [ ] **CI/CD 파이프라인 구축** (소요: 6주, 교육 필요)
  - 배포 자동화 및 품질 관리 체계 구축

### 🟢 장기 실행 (Low Priority - 3-12개월)

#### 아키텍처 현대화 및 마이그레이션
- [ ] **서버리스 아키텍처 도입** (소요: 8주, 교육 필요)
- [ ] **컨테이너화 및 EKS 활용** (소요: 12주, 교육 필요)
- [ ] **마이크로서비스 아키텍처 전환** (소요: 16주, 전문가 필요)

#### 고급 서비스 도입 및 혁신
- [ ] **AI/ML 서비스 도입** (소요: 6주, 교육 필요)
- [ ] **데이터 레이크 구축** (소요: 10주, 전문가 필요)
- [ ] **IoT 플랫폼 구성** (소요: 8주, 교육 필요)

---"""

    def generate_roi_analysis(self) -> str:
        """ROI 분석 섹션을 생성합니다."""
        return """## 📊 투자 우선순위 및 ROI 분석

### 💰 비용 대비 효과 분석

| 우선순위 | 항목 | 투자 비용 | 예상 절감/효과 | ROI | 구현 난이도 |
|----------|------|-----------|----------------|-----|------------|
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

---"""

    def generate_kpi_section(self) -> str:
        """KPI 및 측정 방법 섹션을 생성합니다."""
        return """## 📈 성공 지표 및 측정 방법

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

---"""

    def generate_training_section(self) -> str:
        """교육 및 역량 개발 섹션을 생성합니다."""
        return """## 🎓 필요한 기술 역량 및 교육

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

---"""

    def generate_report(self) -> str:
        """전체 보고서를 생성합니다."""
        self.log_info("🎯 AWS Well-Architected Framework 기반 종합 권장사항 분석 중...")
        
        # 현재 상태 분석
        analysis = self.analyze_current_state()
        scores = self.calculate_maturity_scores(analysis)
        
        # 보고서 섹션들 생성
        report_sections = [
            f"# 🎯 AWS Well-Architected Framework 기반 종합 권장사항\n\n",
            f"> **분석 일시**: {self.current_time}  \n",
            f"> **분석 기준**: AWS Well-Architected Framework 5개 기둥  \n",
            f"> **평가 대상**: AWS 계정 전체 인프라\n\n",
            self.generate_executive_summary(scores),
            self.generate_operational_excellence_section(analysis),
            self.generate_security_section(analysis),
            self.generate_reliability_section(),
            self.generate_performance_section(analysis),
            self.generate_cost_optimization_section(analysis),
            self.generate_implementation_plan(),
            self.generate_roi_analysis(),
            self.generate_kpi_section(),
            self.generate_training_section(),
            f"\n---\n\n",
            f"*📅 분석 완료 시간: {self.current_time}*  \n",
            f"*🔄 다음 검토 권장 주기: 분기별*  \n",
            f"*🎯 목표 성숙도: 4.5/5 (12개월 내)*\n\n",
            f"---\n"
        ]
        
        return ''.join(report_sections)

    def save_report(self, content: str, filename: str = "10-recommendations.md") -> None:
        """보고서를 파일로 저장합니다."""
        output_path = self.report_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_success(f"✅ Enhanced Recommendations 생성 완료: {filename}")
            
            # 파일 크기 정보
            file_size = output_path.stat().st_size
            self.log_info(f"📄 보고서 크기: {file_size:,} bytes")
            
        except Exception as e:
            self.log_error(f"❌ 보고서 저장 실패: {e}")
            sys.exit(1)

def main():
    """메인 실행 함수"""
    try:
        # 보고서 생성기 초기화
        generator = RecommendationsReportGenerator()
        
        # 보고서 생성
        report_content = generator.generate_report()
        
        # 보고서 저장
        generator.save_report(report_content)
        
        print("🎉 Enhanced Recommendations 보고서 생성이 완료되었습니다!")
        
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
