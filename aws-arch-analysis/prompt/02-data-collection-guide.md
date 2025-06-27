# AWS 계정 분석 - 데이터 수집 가이드

## 📊 데이터 수집 전략

### Steampipe 기반 종합 데이터 수집
**위치**: `~/amazonqcli_lab/aws-arch-analysis/script/`

#### 1. 🚀 종합 데이터 수집 실행 (권장)
모든 AWS 리소스 데이터를 한 번에 수집하는 통합 스크립트를 사용합니다:


**방법 : Python 스크립트 직접 실행**
```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script
python3 collect_all_data.py
```

**주요 기능:**
- 9개 영역의 데이터를 순차적으로 자동 수집
- 실시간 진행 상황 및 소요 시간 표시
- 성공/실패 통계 및 상세 결과 제공
- 타임아웃 처리 (스크립트당 5분)
- 최종 요약 보고서 자동 생성

**수집 영역:**
1. **네트워킹**: VPC, 서브넷, 보안그룹, 라우팅 테이블, Transit Gateway 등
2. **컴퓨팅**: EC2, EKS, Auto Scaling, Load Balancer 등
3. **컨테이너**: ECS, EKS, ECR, Kubernetes 리소스 등
4. **스토리지**: EBS, S3, EFS, FSx, Backup 등
5. **데이터베이스**: RDS, Aurora, ElastiCache, DynamoDB 등
6. **보안**: IAM, KMS, Secrets Manager, GuardDuty 등
7. **애플리케이션**: API Gateway, Lambda, SNS, SQS 등
8. **모니터링**: CloudWatch, X-Ray, Config 등
9. **IaC 분석**: CloudFormation, 태그 분석 등

#### 2. 개별 영역 데이터 수집 (선택적)
특정 영역만 수집하려는 경우 개별 스크립트를 실행할 수 있습니다:

```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script

# 네트워킹 데이터만 수집
python3 steampipe_networking_collection.py

# 컴퓨팅 데이터만 수집
python3 steampipe_compute_collection.py

# 데이터베이스 데이터만 수집
python3 steampipe_database_collection.py

# 보안 데이터만 수집
python3 steampipe_security_collection.py
```

### 📁 데이터 수집 결과물
모든 수집된 데이터는 `~/amazonqcli_lab/aws-arch-analysis/report/` 디렉토리에 JSON 형태로 저장됩니다:

```
~/amazonqcli_lab/aws-arch-analysis/report/
├── networking_*.json          # 네트워킹 관련 데이터
├── compute_*.json             # 컴퓨팅 관련 데이터
├── database_*.json            # 데이터베이스 관련 데이터
├── security_*.json            # 보안 관련 데이터
├── application_*.json         # 애플리케이션 관련 데이터
├── monitoring_*.json          # 모니터링 관련 데이터
├── k8s_*.json                # Kubernetes 관련 데이터
└── *.log                     # 수집 로그 파일
```

### ⚠️ 주의사항
- 일부 AWS 서비스에 대한 접근이 SCP(Service Control Policy)로 제한되어 있어 모든 데이터를 수집할 수 없습니다
- Steampipe 플러그인 버전과 일부 쿼리가 호환되지 않을 수 있습니다
