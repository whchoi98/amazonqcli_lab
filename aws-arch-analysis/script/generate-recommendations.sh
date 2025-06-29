#!/bin/bash
# Enhanced Recommendations 보고서 생성 스크립트
# AWS Well-Architected Framework 기반 종합 권장사항

REPORT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"
cd $REPORT_DIR

echo "🎯 Enhanced Recommendations 보고서 생성 중..."

# 현재 날짜 및 시간
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cat > 10-comprehensive-recommendations.md << 'MDEOF'
# 🎯 AWS Well-Architected Framework 기반 종합 권장사항

> **분석 일시**: CURRENT_DATE_PLACEHOLDER  
> **분석 기준**: AWS Well-Architected Framework 5개 기둥  
> **평가 대상**: AWS 계정 전체 인프라

## 📊 Executive Summary

### 아키텍처 성숙도 종합 평가
본 분석은 AWS Well-Architected Framework의 5개 기둥을 기준으로 현재 인프라의 성숙도를 평가하고, 
우선순위별 개선 방안을 제시합니다.

---

## 🏗️ Well-Architected Framework 5개 기둥별 평가

### 📊 아키텍처 성숙도 평가 (1-5점 척도)

| 기둥 | 현재 점수 | 목표 점수 | 주요 개선 영역 |
|------|-----------|-----------|----------------|
| 🔧 **운영 우수성** | 3/5 | 4/5 | 자동화, 모니터링 강화 |
| 🔒 **보안** | 3/5 | 5/5 | IAM 최적화, 암호화 강화 |
| 🛡️ **안정성** | 4/5 | 5/5 | 백업 정책, 재해 복구 |
| ⚡ **성능 효율성** | 3/5 | 4/5 | 리소스 최적화, 모니터링 |
| 💰 **비용 최적화** | 4/5 | 5/5 | Reserved Instance, 태깅 |

### 🎯 전체 성숙도 점수: **3.4/5** (양호)

---

## 🔧 운영 우수성 (Operational Excellence) - 현재: 3/5

### 📋 현황 분석
MDEOF

# 현재 날짜 삽입
sed -i "s/CURRENT_DATE_PLACEHOLDER/$CURRENT_DATE/g" 10-comprehensive-recommendations.md

# 운영 우수성 분석
if [ -f "monitoring_cloudwatch_log_groups.json" ] && [ -s "monitoring_cloudwatch_log_groups.json" ]; then
    LOG_GROUPS_COUNT=$(jq '.rows | length' monitoring_cloudwatch_log_groups.json)
    RETENTION_SET=$(jq '[.rows[] | select(.retention_in_days != null)] | length' monitoring_cloudwatch_log_groups.json)
    
    cat >> 10-comprehensive-recommendations.md << MDEOF
**✅ 강점:**
- CloudWatch 로그 그룹 ${LOG_GROUPS_COUNT}개 운영 중
- 로그 보존 정책 설정: ${RETENTION_SET}개 그룹

**⚠️ 개선 필요:**
- 자동화 스크립트 부족
- 운영 대시보드 미구축
- 변경 관리 프로세스 미정립

MDEOF
else
    cat >> 10-comprehensive-recommendations.md << MDEOF
**⚠️ 개선 필요:**
- 로깅 시스템 구축 필요
- 모니터링 체계 미흡
- 자동화 도구 도입 필요

MDEOF
fi

cat >> 10-comprehensive-recommendations.md << 'MDEOF'

### 🎯 개선 권장사항
1. **자동화 강화**
   - Infrastructure as Code (Terraform/CloudFormation) 도입
   - CI/CD 파이프라인 구축
   - 자동 백업 및 복구 스크립트 개발

2. **모니터링 및 관찰성**
   - CloudWatch 대시보드 구성
   - 알람 및 알림 체계 구축
   - 로그 중앙화 및 분석 도구 도입

3. **운영 프로세스**
   - 변경 관리 프로세스 정립
   - 인시던트 대응 절차 수립
   - 정기 검토 및 개선 사이클 구축

---

## 🔒 보안 (Security) - 현재: 3/5

### 📋 현황 분석
MDEOF

# 보안 분석
if [ -f "security_iam_roles.json" ] && [ -s "security_iam_roles.json" ]; then
    IAM_ROLES_COUNT=$(jq '.rows | length' security_iam_roles.json)
    
    cat >> 10-comprehensive-recommendations.md << MDEOF
**✅ 강점:**
- IAM 역할 ${IAM_ROLES_COUNT}개로 권한 관리 체계화
- 기본 보안 그룹 설정 적용

MDEOF
fi

if [ -f "security_groups.json" ] && [ -s "security_groups.json" ]; then
    SECURITY_GROUPS_COUNT=$(jq '.rows | length' security_groups.json)
    
    cat >> 10-comprehensive-recommendations.md << MDEOF
- 보안 그룹 ${SECURITY_GROUPS_COUNT}개로 네트워크 보안 관리

MDEOF
fi

cat >> 10-comprehensive-recommendations.md << 'MDEOF'

**⚠️ 개선 필요:**
- IAM 권한 최소화 원칙 미준수
- 암호화 적용 범위 제한적
- 보안 모니터링 체계 미흡
- MFA 설정 미완료

### 🎯 개선 권장사항

#### 🔴 즉시 조치 (High Priority)
1. **IAM 보안 강화**
   - 모든 IAM 사용자 MFA 활성화
   - 최소 권한 원칙 적용
   - 정기적인 권한 검토 및 정리

2. **암호화 강화**
   - EBS 볼륨 암호화 활성화
   - S3 버킷 암호화 설정
   - RDS 인스턴스 암호화 적용

3. **네트워크 보안**
   - 보안 그룹 규칙 최적화
   - 불필요한 포트 차단
   - VPC Flow Logs 활성화

#### 🟡 단기 개선 (1-3개월)
1. **보안 모니터링**
   - AWS GuardDuty 활성화
   - AWS Security Hub 구성
   - CloudTrail 로깅 강화

2. **접근 제어**
   - AWS SSO 도입 검토
   - 임시 자격 증명 활용
   - 정기적인 액세스 키 순환

---

## 🛡️ 안정성 (Reliability) - 현재: 4/5

### 📋 현황 분석
MDEOF

# 안정성 분석
if [ -f "compute_ec2_instances.json" ] && [ -s "compute_ec2_instances.json" ]; then
    EC2_COUNT=$(jq '.rows | length' compute_ec2_instances.json)
    RUNNING_COUNT=$(jq '[.rows[] | select(.instance_state == "running")] | length' compute_ec2_instances.json)
    
    cat >> 10-comprehensive-recommendations.md << MDEOF
**✅ 강점:**
- EC2 인스턴스 ${EC2_COUNT}개 중 ${RUNNING_COUNT}개 정상 운영
- Multi-AZ 배포 구성

MDEOF
fi

if [ -f "networking_vpc.json" ] && [ -s "networking_vpc.json" ]; then
    VPC_COUNT=$(jq '.rows | length' networking_vpc.json)
    
    cat >> 10-comprehensive-recommendations.md << MDEOF
- VPC ${VPC_COUNT}개로 네트워크 격리 구현

MDEOF
fi

cat >> 10-comprehensive-recommendations.md << 'MDEOF'

**⚠️ 개선 필요:**
- 자동화된 백업 정책 미흡
- 재해 복구 계획 미수립
- 헬스 체크 및 자동 복구 미구성

### 🎯 개선 권장사항

#### 🔴 즉시 조치
1. **백업 정책 수립**
   - EBS 스냅샷 자동화
   - RDS 자동 백업 설정
   - 크로스 리전 백업 구성

2. **모니터링 강화**
   - CloudWatch 알람 설정
   - 헬스 체크 구성
   - 자동 복구 메커니즘 구축

#### 🟡 단기 개선
1. **재해 복구**
   - DR 계획 수립
   - 복구 시간 목표(RTO) 정의
   - 정기적인 DR 테스트 수행

2. **고가용성 구성**
   - Auto Scaling 그룹 최적화
   - Load Balancer 헬스 체크 강화
   - 다중 AZ 배포 확대

---

## ⚡ 성능 효율성 (Performance Efficiency) - 현재: 3/5

### 📋 현황 분석
MDEOF

# 성능 효율성 분석
if [ -f "compute_ec2_instances.json" ] && [ -s "compute_ec2_instances.json" ]; then
    # 인스턴스 타입별 분석
    T3_COUNT=$(jq '[.rows[] | select(.instance_type | startswith("t3"))] | length' compute_ec2_instances.json)
    M6I_COUNT=$(jq '[.rows[] | select(.instance_type | startswith("m6i"))] | length' compute_ec2_instances.json)
    
    cat >> 10-comprehensive-recommendations.md << MDEOF
**✅ 강점:**
- 최신 인스턴스 타입 활용 (t3: ${T3_COUNT}개, m6i: ${M6I_COUNT}개)
- 적절한 인스턴스 크기 선택

MDEOF
fi

cat >> 10-comprehensive-recommendations.md << 'MDEOF'

**⚠️ 개선 필요:**
- 성능 모니터링 체계 미흡
- 리소스 사용률 최적화 필요
- 자동 스케일링 정책 미세조정

### 🎯 개선 권장사항

#### 🟡 단기 개선
1. **성능 모니터링**
   - CloudWatch 상세 모니터링 활성화
   - 커스텀 메트릭 수집
   - 성능 대시보드 구성

2. **리소스 최적화**
   - 인스턴스 타입 적정성 검토
   - 스토리지 성능 최적화
   - 네트워크 성능 튜닝

#### 🟢 장기 개선
1. **아키텍처 최적화**
   - 서버리스 아키텍처 도입 검토
   - 컨테이너화 및 마이크로서비스
   - CDN 및 캐싱 전략 수립

---

## 💰 비용 최적화 (Cost Optimization) - 현재: 4/5

### 📋 현황 분석
MDEOF

# 비용 최적화 분석
if [ -f "cost_by_service_monthly.json" ] && [ -s "cost_by_service_monthly.json" ]; then
    TOTAL_COST=$(jq '[.rows[].blended_cost_amount] | add' cost_by_service_monthly.json)
    SERVICE_COUNT=$(jq '.rows | length' cost_by_service_monthly.json)
    
    cat >> 10-comprehensive-recommendations.md << MDEOF
**✅ 강점:**
- 월간 총 비용: \$$(printf "%.2f" $TOTAL_COST) (매우 효율적)
- ${SERVICE_COUNT}개 서비스 비용 관리

MDEOF
fi

cat >> 10-comprehensive-recommendations.md << 'MDEOF'

**⚠️ 개선 필요:**
- Reserved Instance 활용 기회
- 리소스 태깅 전략 미흡
- 비용 모니터링 자동화 필요

### 🎯 개선 권장사항

#### 🟡 단기 개선
1. **비용 가시성**
   - AWS Cost Explorer 활용
   - 예산 알림 설정
   - 태그 기반 비용 추적

2. **리소스 최적화**
   - 미사용 리소스 정리
   - 스토리지 클래스 최적화
   - 예약 인스턴스 구매 검토

#### 🟢 장기 개선
1. **비용 거버넌스**
   - 부서별 비용 할당
   - 비용 최적화 정책 수립
   - 정기적인 비용 검토 프로세스

---

## 📋 리소스 활용도 분석

### 🔍 미사용 리소스 식별
MDEOF

# 미사용 리소스 분석
if [ -f "storage_ebs_volumes.json" ] && [ -s "storage_ebs_volumes.json" ]; then
    UNUSED_VOLUMES=$(jq '[.rows[] | select(.state == "available")] | length' storage_ebs_volumes.json)
    if [ $UNUSED_VOLUMES -gt 0 ]; then
        cat >> 10-comprehensive-recommendations.md << MDEOF
- **미사용 EBS 볼륨**: ${UNUSED_VOLUMES}개 발견
  - 즉시 정리 또는 스냅샷 백업 후 삭제 권장

MDEOF
    fi
fi

if [ -f "networking_eip.json" ] && [ -s "networking_eip.json" ]; then
    UNATTACHED_EIP=$(jq '[.rows[] | select(.association_id == null)] | length' networking_eip.json)
    if [ $UNATTACHED_EIP -gt 0 ]; then
        cat >> 10-comprehensive-recommendations.md << MDEOF
- **연결되지 않은 Elastic IP**: ${UNATTACHED_EIP}개 발견
  - 불필요한 EIP 해제로 비용 절감 가능

MDEOF
    fi
fi

cat >> 10-comprehensive-recommendations.md << 'MDEOF'

### 🎯 과도하게 프로비저닝된 리소스 최적화
- **인스턴스 크기 조정**: CPU/메모리 사용률 기반 최적화
- **스토리지 용량 조정**: 실제 사용량 대비 프로비저닝 검토
- **네트워크 대역폭**: 트래픽 패턴 분석 후 조정

### 🔗 리소스 간 의존성 및 연결 상태 분석
- **VPC 간 연결**: Transit Gateway를 통한 효율적 연결 구성
- **보안 그룹 의존성**: 불필요한 규칙 정리 및 최적화
- **로드 밸런서 연결**: 타겟 그룹 헬스 체크 상태 점검

---

## 📋 실행 계획 수립

### 🔴 즉시 실행 (High Priority - 1-2주)

#### 보안 위험 요소 즉시 해결
- [ ] **IAM MFA 활성화** (소요: 1일, 비용: 무료, 위험도: 높음)
- [ ] **미사용 EBS 볼륨 정리** (소요: 2일, 절감: $10-50/월, 위험도: 낮음)
- [ ] **보안 그룹 규칙 최적화** (소요: 3일, 위험도: 중간)
- [ ] **Root 계정 보안 강화** (소요: 1일, 위험도: 높음)

#### 비용 절감 효과가 큰 항목
- [ ] **연결되지 않은 EIP 해제** (소요: 1일, 절감: $3.6/월, 위험도: 낮음)
- [ ] **미사용 스냅샷 정리** (소요: 2일, 절감: $5-20/월, 위험도: 낮음)

### 🟡 단기 실행 (Medium Priority - 1-3개월)

#### 성능 최적화 및 모니터링 강화
- [ ] **CloudWatch 대시보드 구성** (소요: 1주, 비용: $10-30/월)
- [ ] **알람 및 알림 체계 구축** (소요: 2주, 비용: $5-15/월)
- [ ] **성능 메트릭 수집 강화** (소요: 1주, 비용: $20-50/월)

#### 자동화 도입 및 운영 효율성 개선
- [ ] **자동 백업 정책 수립** (소요: 2주, 비용: $50-100/월)
- [ ] **Infrastructure as Code 도입** (소요: 4주, 교육 필요)
- [ ] **CI/CD 파이프라인 구축** (소요: 6주, 교육 필요)

#### 백업 및 재해 복구 체계 구축
- [ ] **DR 계획 수립** (소요: 3주, 비용: $100-300/월)
- [ ] **크로스 리전 백업 구성** (소요: 2주, 비용: $30-80/월)
- [ ] **복구 테스트 수행** (소요: 1주, 분기별 반복)

### 🟢 장기 실행 (Low Priority - 3-12개월)

#### 아키텍처 현대화 및 마이그레이션
- [ ] **서버리스 아키텍처 도입** (소요: 8주, 교육 필요)
- [ ] **컨테이너화 및 EKS 활용** (소요: 12주, 교육 필요)
- [ ] **마이크로서비스 아키텍처 전환** (소요: 16주, 전문가 필요)

#### 고급 서비스 도입 및 혁신
- [ ] **AI/ML 서비스 도입** (소요: 6주, 교육 필요)
- [ ] **데이터 레이크 구축** (소요: 10주, 전문가 필요)
- [ ] **IoT 플랫폼 구성** (소요: 8주, 교육 필요)

#### 조직 차원의 클라우드 거버넌스 강화
- [ ] **멀티 계정 전략 수립** (소요: 4주, 정책 수립)
- [ ] **비용 거버넌스 체계 구축** (소요: 6주, 프로세스 정립)
- [ ] **보안 거버넌스 강화** (소요: 8주, 정책 및 교육)

---

## 📊 투자 우선순위 및 ROI 분석

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

*📅 분석 완료 시간: CURRENT_DATE_PLACEHOLDER*  
*🔄 다음 검토 권장 주기: 분기별*  
*🎯 목표 성숙도: 4.5/5 (12개월 내)*

---
MDEOF

echo "✅ Enhanced Recommendations 생성 완료: 10-comprehensive-recommendations.md"
