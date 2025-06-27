# Phase 2: 데이터 수집 전략 - 권장 프롬프트

## 🎯 목표
AWS 계정의 모든 리소스에 대한 체계적이고 완전한 데이터 수집을 수행합니다.

## 📋 권장 프롬프트

```
이제 AWS 계정의 모든 리소스에 대한 체계적인 데이터 수집을 시작하겠습니다.

**중요**: 이전 분석 결과에 따라 최적화된 수집 전략을 사용합니다:
- 네트워킹: Python 스크립트 (14/18 성공률로 우수)
- 나머지 영역: Shell 스크립트 (더 안정적인 성능)

다음 8개 영역에 대해 순차적으로 데이터 수집을 실행해주세요:

1. **네트워킹 리소스** (Python 스크립트 사용):
   ```bash
   cd ~/amazonqcli_lab/aws-arch-analysis/script
   ./steampipe_networking_collection.py
   ```
   - 수집 대상: VPC, 서브넷, 보안 그룹, 라우팅 테이블, NAT Gateway, IGW, VPC 엔드포인트
   - 예상 성공률: 13-14/18 (72-78%)

2. **컴퓨팅 리소스** (Shell 스크립트 사용):
   ```bash
   ./steampipe_compute_collection.sh
   ```
   - 수집 대상: EC2 인스턴스, Auto Scaling, Load Balancer, Lambda 함수
   - 예상 성공률: 6/21 (29%)

3. **데이터베이스 리소스** (Shell 스크립트 사용):
   ```bash
   ./steampipe_database_collection.sh
   ```
   - 수집 대상: RDS, Aurora, DynamoDB, ElastiCache, Redshift
   - 예상 성공률: 10/20 (50%)

4. **스토리지 리소스** (Shell 스크립트 사용):
   ```bash
   ./steampipe_storage_collection.sh
   ```
   - 수집 대상: EBS 볼륨, S3 버킷, EFS, 백업 정책
   - 예상 성공률: 1/25 (권한 제한으로 낮음)

5. **보안 리소스** (Shell 스크립트 사용):
   ```bash
   ./steampipe_security_collection.sh
   ```
   - 수집 대상: IAM 역할/정책, KMS 키, 보안 그룹 규칙
   - 예상 성공률: 5/27 (권한 제한으로 낮음)

6. **애플리케이션 서비스** (Shell 스크립트 사용):
   ```bash
   ./steampipe_application_collection.sh
   ```
   - 수집 대상: API Gateway, SNS, SQS, EventBridge, Lambda
   - 예상 성공률: 2/17 (권한 제한으로 낮음)

7. **모니터링 서비스** (Shell 스크립트 사용):
   ```bash
   ./steampipe_monitoring_collection.sh
   ```
   - 수집 대상: CloudWatch 로그/알람, X-Ray, 비용 모니터링
   - 예상 성공률: 2/26 (권한 제한으로 낮음)

8. **컨테이너 서비스** (Shell 스크립트 사용):
   ```bash
   ./steampipe_container_collection.sh
   ```
   - 수집 대상: EKS, ECS, ECR, Fargate
   - 예상 성공률: 낮음 (권한 제한)

각 스크립트 실행 후 다음을 확인해주세요:
- 생성된 JSON 파일 개수
- 성공/실패 통계
- 오류 로그 내용
- 수집된 데이터의 품질

전체 데이터 수집이 완료되면 수집 결과를 요약하여 보고해주세요.
```

## 📊 예상 수집 결과
- **총 JSON 파일**: 150+ 개
- **네트워킹**: 13-14개 파일 (우수)
- **데이터베이스**: 10개 파일 (양호)
- **컴퓨팅**: 6개 파일 (보통)
- **기타 영역**: 권한 제한으로 제한적

## ✅ 완료 기준
- [ ] 8개 영역 모든 스크립트 실행 완료
- [ ] 수집 결과 통계 확인 완료
- [ ] 오류 로그 검토 완료
- [ ] 데이터 품질 검증 완료

## 🔗 다음 단계
Phase 3: 실행 방법론 (`prompt-phase3.md`)
