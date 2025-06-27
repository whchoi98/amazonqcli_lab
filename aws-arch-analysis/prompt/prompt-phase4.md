# Phase 4: 보고서 생성 가이드 - 권장 프롬프트

## 🎯 목표
생성된 10개 Markdown 보고서의 품질을 검증하고 완성도를 높입니다.

## 📋 권장 프롬프트

```
이제 생성된 Markdown 보고서들을 검토하고 완성도를 높이겠습니다.

**목표**: 10개 보고서의 품질 검증 및 내용 완성도 확인

다음 10개 보고서가 모두 생성되었는지 확인하고 내용을 검토해주세요:

1. **01-executive-summary.md** (경영진 요약):
   - 전체 분석 점수: 79.7/100 (양호)
   - 주요 발견사항: VPC 5개, EC2 34개, RDS 2개
   - 우선순위별 권장사항 포함 여부 확인

2. **02-networking-analysis.md** (네트워킹 분석):
   - 5개 VPC 상세 분석
   - 36개 서브넷 구성 검토
   - 26개 보안 그룹 규칙 분석
   - 네트워크 최적화 방안

3. **03-compute-analysis.md** (컴퓨팅 분석):
   - 34개 EC2 인스턴스 분석
   - 인스턴스 타입별 분포 (m6i.xlarge: 8개, t3.small: 24개 등)
   - Auto Scaling 그룹 및 Load Balancer 구성
   - 서버리스 컴퓨팅 활용 방안

4. **04-database-analysis.md** (데이터베이스 분석):
   - 2개 RDS 인스턴스 상세 분석
   - Aurora MySQL 클러스터 구성
   - ElastiCache 클러스터 분석
   - 데이터베이스 성능 최적화 방안

5. **05-storage-analysis.md** (스토리지 분석):
   - 34개 EBS 볼륨 분석
   - 스토리지 타입별 최적화
   - 백업 및 스냅샷 정책
   - 비용 최적화 기회

6. **06-security-analysis.md** (보안 분석):
   - 44개 IAM 역할 권한 분석
   - KMS 키 관리 현황
   - 보안 그룹 규칙 검토
   - 보안 강화 권장사항

7. **07-application-analysis.md** (애플리케이션 분석):
   - EventBridge 규칙 분석
   - API Gateway 구성 (있는 경우)
   - 서버리스 아키텍처 검토
   - 애플리케이션 최적화 방안

8. **08-monitoring-analysis.md** (모니터링 분석):
   - 8개 CloudWatch 로그 그룹 분석
   - 알람 설정 현황 (0개 - 개선 필요)
   - 모니터링 강화 방안
   - 대시보드 구성 권장사항

9. **09-cost-optimization.md** (비용 최적화):
   - 리소스별 비용 분석
   - 미사용 리소스 식별
   - 예약 인스턴스 활용 방안
   - 비용 절감 기회

10. **10-recommendations.md** (종합 권장사항):
    - 🔴 높은 우선순위: IAM 보안 강화, 미사용 리소스 정리
    - 🟡 중간 우선순위: 모니터링 강화, 백업 정책 수립
    - 🟢 낮은 우선순위: 컨테이너 최적화, 네트워크 최적화

**검증 기준**:

1. **파일 존재 및 크기 확인**:
   ```bash
   ls -la ~/amazonqcli_lab/report/*.md
   wc -c ~/amazonqcli_lab/report/*.md | grep -v total
   ```

2. **내용 품질 확인**:
   - ✅ 실제 수집된 데이터 기반 분석
   - ✅ 구체적인 수치와 통계 포함
   - ✅ 실행 가능한 권장사항
   - ✅ 우선순위별 분류
   - ✅ 예상 효과 및 비용 언급

3. **각 보고서 미리보기**:
   ```bash
   for file in ~/amazonqcli_lab/report/*.md; do
     echo "=== $(basename $file) ==="
     head -10 "$file"
     echo ""
   done
   ```

각 보고서의 주요 내용과 품질을 검토한 후, 다음을 보고해주세요:
- 생성된 보고서 개수
- 각 보고서의 크기 및 내용 품질
- 개선이 필요한 부분
- 다음 단계 진행 준비 상태
```

## 📊 품질 검증 체크리스트

### 파일 기본 요구사항
- [ ] 10개 파일 모두 존재
- [ ] 각 파일 크기 100바이트 이상
- [ ] 파일명 규칙 준수 (01-10번)

### 내용 품질 요구사항
- [ ] 실제 데이터 기반 분석
- [ ] 구체적인 수치 포함
- [ ] 실행 가능한 권장사항
- [ ] 우선순위별 분류
- [ ] 예상 효과 언급

### 보고서별 핵심 내용
- [ ] Executive Summary: 전체 점수 및 주요 발견사항
- [ ] Networking: VPC/서브넷/보안그룹 분석
- [ ] Compute: EC2/ASG/ALB 분석
- [ ] Database: RDS/Aurora/ElastiCache 분석
- [ ] Storage: EBS/백업 정책 분석
- [ ] Security: IAM/KMS 보안 분석
- [ ] Application: 애플리케이션 서비스 분석
- [ ] Monitoring: CloudWatch/알람 분석
- [ ] Cost: 비용 최적화 기회
- [ ] Recommendations: 우선순위별 권장사항

## ✅ 완료 기준
- [ ] 10개 보고서 품질 검증 완료
- [ ] 내용 완성도 확인 완료
- [ ] 개선 사항 식별 완료
- [ ] HTML 변환 준비 완료

## 🔗 다음 단계
Phase 5: HTML 변환 및 배포 (`prompt-phase5.md`)
