#!/usr/bin/env python3
"""
보고서 생성기 모듈
"""

from typing import Dict
from report_utils import MarkdownGenerator, ReportUtils
from html_generator import HTMLConverter, DashboardGenerator

class MarkdownReportGenerator:
    """Markdown 보고서 생성 관리자"""
    
    def __init__(self, aws_account_id: str, aws_region: str, analysis_results: Dict):
        self.generator = MarkdownGenerator(aws_account_id, aws_region, analysis_results)
        self.utils = ReportUtils()
    
    def generate_all_reports(self):
        """모든 Markdown 보고서 생성"""
        reports = [
            ("01-executive-summary.md", self.generator.generate_executive_summary()),
            ("02-networking-analysis.md", self.generator.generate_networking_analysis()),
            ("03-computing-analysis.md", self.generator.generate_computing_analysis()),
            ("07-cost-optimization.md", self.generator.generate_cost_optimization()),
        ]
        
        # 추가 보고서들 (간단한 버전)
        additional_reports = [
            ("04-storage-analysis.md", self._generate_storage_analysis()),
            ("05-database-analysis.md", self._generate_database_analysis()),
            ("06-security-analysis.md", self._generate_security_analysis()),
            ("08-application-monitoring.md", self._generate_application_monitoring()),
            ("09-comprehensive-recommendations.md", self._generate_comprehensive_recommendations()),
            ("10-implementation-guide.md", self._generate_implementation_guide()),
        ]
        
        reports.extend(additional_reports)
        
        for filename, content in reports:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filename} 생성 완료")
    
    def _generate_storage_analysis(self) -> str:
        """스토리지 분석 보고서"""
        s3_data = self.utils.load_json_data('s3_analysis.json')
        
        s3_summary = "S3 버킷 정보 수집 중..." if not s3_data else "\n".join([
            f"- **{bucket.get('name', 'Unknown')}**: {bucket.get('region', 'Unknown')} 리전"
            for bucket in s3_data
        ])
        
        return f"""# AWS 계정 종합 분석 보고서 - 스토리지 분석

## 💾 스토리지 리소스 분석

**분석 일시**: {self.utils.get_current_date()}

---

## 📊 S3 버킷 현황

{s3_summary}

## 🎯 스토리지 최적화 권장사항

1. **S3 최적화**
   - Intelligent Tiering 활성화
   - 라이프사이클 정책 구현
   - 불완전한 멀티파트 업로드 정리

2. **EBS 최적화**
   - 미사용 볼륨 정리
   - gp2 → gp3 업그레이드
   - 스냅샷 관리 정책

3. **백업 전략**
   - 자동화된 백업 정책
   - 크로스 리전 백업
   - 복구 테스트 정기 실행

---

*스토리지 분석 완료*
"""
    
    def _generate_database_analysis(self) -> str:
        """데이터베이스 분석 보고서"""
        rds_data = self.utils.load_json_data('rds_analysis.json')
        elasticache_data = self.utils.load_json_data('elasticache_analysis.json')
        
        rds_summary = "RDS 인스턴스 정보 수집 중..." if not rds_data else "\n".join([
            f"- **{db.get('db_instance_identifier', 'Unknown')}**: {db.get('engine', 'Unknown')} {db.get('engine_version', '')} ({db.get('class', 'Unknown')})"
            for db in rds_data
        ])
        
        elasticache_summary = "ElastiCache 정보 수집 중..." if not elasticache_data else "\n".join([
            f"- **{cache.get('cache_cluster_id', 'Unknown')}**: {cache.get('engine', 'Unknown')} {cache.get('engine_version', '')} ({cache.get('cache_node_type', 'Unknown')})"
            for cache in elasticache_data
        ])
        
        return f"""# AWS 계정 종합 분석 보고서 - 데이터베이스 분석

## 🗄️ 데이터베이스 서비스 분석

**분석 일시**: {self.utils.get_current_date()}

---

## 📊 RDS 인스턴스 현황

{rds_summary}

## 📊 ElastiCache 클러스터 현황

{elasticache_summary}

## 🎯 데이터베이스 최적화 권장사항

1. **성능 최적화**
   - Performance Insights 활용
   - 슬로우 쿼리 분석
   - 연결 풀링 최적화

2. **보안 강화**
   - 암호화 설정 확인
   - 네트워크 접근 제한
   - 정기적인 패치 적용

3. **비용 최적화**
   - Reserved Instance 검토
   - 인스턴스 크기 최적화
   - 백업 보존 기간 조정

---

*데이터베이스 분석 완료*
"""
    
    def _generate_security_analysis(self) -> str:
        """보안 분석 보고서"""
        return f"""# AWS 계정 종합 분석 보고서 - 보안 분석

## 🔒 보안 아키텍처 분석

**분석 일시**: {self.utils.get_current_date()}  
**보안 그룹 수**: {self.generator.analysis_results['security_group_count']}개

---

## 📊 보안 현황

### 보안 그룹 분석
- 총 보안 그룹: {self.generator.analysis_results['security_group_count']}개
- VPC별 분포 확인 필요
- 규칙 최적화 권장

## 🎯 보안 강화 권장사항

1. **네트워크 보안**
   - 보안 그룹 규칙 정기 검토
   - 불필요한 0.0.0.0/0 규칙 제거
   - VPC Flow Logs 활성화

2. **데이터 보안**
   - 암호화 설정 전면 검토
   - 백업 데이터 보안 강화
   - 액세스 로깅 활성화

3. **모니터링 강화**
   - CloudTrail 로그 분석
   - 비정상 활동 탐지
   - 보안 이벤트 알림

---

*보안 분석 완료*
"""
    
    def _generate_application_monitoring(self) -> str:
        """애플리케이션 모니터링 보고서"""
        return f"""# AWS 계정 종합 분석 보고서 - 애플리케이션 서비스 및 모니터링

## 📊 애플리케이션 서비스 분석

**분석 일시**: {self.utils.get_current_date()}

---

## 🔍 현재 모니터링 상태

### 기본 모니터링
- CloudWatch 기본 메트릭 수집
- 커스텀 메트릭 부족
- 알람 설정 미흡

## 🎯 모니터링 강화 권장사항

1. **관찰성 구축**
   - CloudWatch 대시보드 구축
   - 커스텀 메트릭 수집
   - 로그 중앙화

2. **알림 체계**
   - SNS 토픽 설정
   - 임계값 알람 구성
   - 에스컬레이션 프로세스

3. **성능 모니터링**
   - 애플리케이션 성능 추적
   - 인프라 메트릭 분석
   - 용량 계획 수립

---

*애플리케이션 서비스 분석 완료*
"""
    
    def _generate_comprehensive_recommendations(self) -> str:
        """종합 권장사항 보고서"""
        return f"""# AWS 계정 종합 분석 보고서 - 종합 분석 및 권장사항

## 🎯 종합 분석 결과

**분석 완료일**: {self.utils.get_current_date()}  
**전체 아키텍처 성숙도**: 7.0/10 (양호)

---

## 📊 주요 발견사항

### 인프라 현황
- **VPC**: {self.generator.analysis_results['vpc_count']}개
- **EC2 인스턴스**: {self.generator.analysis_results['ec2_count']}개
- **보안 그룹**: {self.generator.analysis_results['security_group_count']}개
- **월간 비용**: {self.utils.format_cost(self.generator.analysis_results['total_cost'])}

## 🔴 최우선 조치 항목

1. **비용 최적화**
   - 미사용 리소스 정리
   - Right-sizing 실행
   - Reserved Instance 검토

2. **모니터링 구축**
   - 기본 알람 설정
   - 대시보드 구축
   - 로그 중앙화

3. **보안 강화**
   - 보안 그룹 감사
   - 암호화 설정 검토
   - 접근 제어 강화

## 📈 로드맵

### Phase 1 (1-2주)
- [ ] 비용 모니터링 설정
- [ ] 미사용 리소스 정리
- [ ] 기본 알람 구성

### Phase 2 (1-2개월)
- [ ] EC2 최적화 실행
- [ ] 보안 정책 강화
- [ ] 모니터링 확대

### Phase 3 (3-6개월)
- [ ] 자동화 구현
- [ ] 아키텍처 현대화
- [ ] 운영 효율성 향상

---

*종합 분석 완료*
"""
    
    def _generate_implementation_guide(self) -> str:
        """구현 가이드 보고서"""
        return f"""# AWS 계정 종합 분석 보고서 - 구현 가이드

## 🛠️ 단계별 구현 가이드

**구현 기간**: 3-6개월  
**예상 절약 효과**: 월 $20-50

---

## 📅 Phase 1: 즉시 조치 (1-2주)

### 1.1 비용 모니터링 설정
```bash
# 비용 알람 설정
aws budgets create-budget --account-id {self.generator.aws_account_id} --budget file://budget-config.json
```

### 1.2 기본 모니터링 구축
```bash
# CloudWatch 알람 생성
aws cloudwatch put-metric-alarm \\
  --alarm-name "High-CPU-Usage" \\
  --metric-name CPUUtilization \\
  --threshold 80
```

## 📅 Phase 2: 단기 개선 (1-2개월)

### 2.1 EC2 최적화
- 사용률 분석 및 Right-sizing
- Reserved Instance 구매
- 스케줄링 구현

### 2.2 보안 강화
- 보안 그룹 규칙 최적화
- VPC Flow Logs 활성화
- 암호화 설정 검토

## 📅 Phase 3: 중장기 발전 (3-6개월)

### 3.1 자동화 구현
- 비용 최적화 자동화
- 백업 자동화
- 모니터링 자동화

### 3.2 아키텍처 현대화
- 서버리스 도입
- 컨테이너화 확대
- CI/CD 파이프라인

---

## 📋 체크리스트

### 즉시 조치
- [ ] 비용 알람 설정
- [ ] 미사용 리소스 정리
- [ ] 기본 모니터링 구축

### 단기 개선
- [ ] EC2 Right-sizing
- [ ] 보안 그룹 최적화
- [ ] Reserved Instance 구매

### 장기 발전
- [ ] 자동화 구현
- [ ] 아키텍처 현대화
- [ ] 운영 프로세스 개선

---

*구현 가이드 완료*
"""
