# Phase 3: 실행 방법론 - 권장 프롬프트

## 🎯 목표
수집된 데이터를 바탕으로 10개의 전문적인 분석 보고서를 생성합니다.

## 📋 권장 프롬프트

```
수집된 데이터를 바탕으로 전문적인 분석 보고서를 생성하겠습니다.

**목표**: 실제 수집된 AWS 데이터를 기반으로 10개의 상세한 분석 보고서 생성

다음 순서로 실행해주세요:

1. **전체 분석 프로세스 실행** (권장):
   ```bash
   cd ~/amazonqcli_lab/aws-arch-analysis/script
   ./run-complete-analysis.sh
   ```
   - 데이터 수집부터 보고서 생성까지 전체 프로세스 자동 실행
   - 약 30초 소요 예상

2. **개별 보고서 생성** (필요시 또는 문제 해결용):

   **경영진 요약 보고서**:
   ```bash
   ./generate-executive-summary.sh
   ```
   - 전체 분석 점수 (79.7/100 예상)
   - 주요 발견사항 및 우선순위별 권장사항

   **네트워킹 분석 보고서**:
   ```bash
   ./generate-networking-report.sh
   ```
   - 5개 VPC, 36개 서브넷, 26개 보안 그룹 분석
   - 네트워크 아키텍처 최적화 방안

   **컴퓨팅 분석 보고서**:
   ```bash
   ./generate-compute-report.sh
   ```
   - 34개 EC2 인스턴스 분석
   - Auto Scaling, Load Balancer 구성 검토

   **데이터베이스 분석 보고서**:
   ```bash
   ./generate-database-report.sh
   ```
   - 2개 RDS 인스턴스, Aurora 클러스터 분석
   - ElastiCache 구성 검토

   **스토리지 분석 보고서**:
   ```bash
   ./generate-storage-report.sh
   ```
   - 34개 EBS 볼륨 분석
   - 스토리지 최적화 및 백업 전략

   **보안 분석 보고서**:
   ```bash
   ./generate-security-report.sh
   ```
   - 44개 IAM 역할 분석
   - KMS 키 관리 및 보안 강화 방안

   **애플리케이션 분석 보고서**:
   ```bash
   ./generate-application-report.sh
   ```
   - EventBridge, 애플리케이션 서비스 분석
   - 서버리스 아키텍처 검토

   **모니터링 분석 보고서**:
   ```bash
   ./generate-monitoring-report.sh
   ```
   - 8개 CloudWatch 로그 그룹 분석
   - 모니터링 강화 및 알람 설정 방안

   **비용 최적화 보고서**:
   ```bash
   ./generate-cost-report.sh
   ```
   - 리소스 사용률 분석
   - 비용 최적화 기회 식별

   **종합 권장사항 보고서**:
   ```bash
   ./generate-recommendations.sh
   ```
   - 우선순위별 실행 계획
   - 단계별 구현 로드맵

3. **품질 검증**:
   ```bash
   # 생성된 보고서 확인
   ls -la ~/amazonqcli_lab/report/*.md
   
   # 파일 크기 확인 (최소 100바이트 이상)
   wc -c ~/amazonqcli_lab/report/*.md
   
   # 내용 미리보기
   head -20 ~/amazonqcli_lab/report/01-executive-summary.md
   ```

4. **보고서 내용 검증**:
   각 보고서가 다음을 포함하는지 확인해주세요:
   - 실제 수집된 데이터 기반 분석
   - 구체적인 수치와 통계
   - 실행 가능한 권장사항
   - 우선순위별 분류
   - 예상 효과 및 비용

생성된 10개 보고서의 주요 내용을 요약하여 보고해주세요.
```

## 📊 예상 생성 결과
- **01-executive-summary.md**: 전체 점수 79.7/100
- **02-networking-analysis.md**: VPC 5개, 서브넷 36개 분석
- **03-compute-analysis.md**: EC2 34개, ALB, ASG 분석
- **04-database-analysis.md**: RDS 2개, Aurora, ElastiCache 분석
- **05-storage-analysis.md**: EBS 34개, 스토리지 최적화
- **06-security-analysis.md**: IAM 44개 역할, 보안 강화
- **07-application-analysis.md**: EventBridge, 애플리케이션 서비스
- **08-monitoring-analysis.md**: CloudWatch 8개 로그 그룹
- **09-cost-optimization.md**: 비용 최적화 기회
- **10-recommendations.md**: 우선순위별 권장사항

## ✅ 완료 기준
- [ ] 10개 Markdown 파일 생성 완료
- [ ] 각 파일 크기 100바이트 이상 확인
- [ ] 실제 데이터 기반 내용 확인
- [ ] 구체적인 권장사항 포함 확인

## 🔗 다음 단계
Phase 4: 보고서 생성 가이드 (`prompt-phase4.md`)
