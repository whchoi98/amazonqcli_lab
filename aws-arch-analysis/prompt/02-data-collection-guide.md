# AWS 계정 분석 - 데이터 수집 가이드

## 📊 데이터 수집 전략

### 기존 스크립트 기반 데이터 수집
**위치**: `~/amazonqcli_lab/aws-arch-analysis/script/`

#### 1. Steampipe 기반 데이터 수집 스크립트
다음 스크립트들을 **순차적으로** 실행하여 AWS 리소스 데이터를 수집합니다:

##### 1.1 네트워킹 데이터 수집
```bash
# 실행 스크립트: steampipe_networking_collection.sh
# 수집 데이터:
# - VPC, 서브넷, 라우팅 테이블
# - 보안 그룹, NACL
# - 인터넷 게이트웨이, NAT 게이트웨이
# - VPC 엔드포인트, 피어링 연결
```

##### 1.2 컴퓨팅 데이터 수집
```bash
# 실행 스크립트: steampipe_compute_collection.sh
# 수집 데이터:
# - EC2 인스턴스 (상태, 타입, 메트릭)
# - Auto Scaling 그룹
# - Elastic Load Balancer (ALB, NLB, CLB)
# - Target Groups
```

##### 1.3 컨테이너 서비스 데이터 수집
```bash
# 실행 스크립트: steampipe_container_collection.sh
# 수집 데이터:
# - ECS 클러스터, 서비스, 태스크
# - EKS 클러스터, 노드 그룹
# - ECR 리포지토리
# - Fargate 서비스
```

##### 1.4 데이터베이스 데이터 수집
```bash
# 실행 스크립트: steampipe_database_collection.sh
# 수집 데이터:
# - RDS 인스턴스, 클러스터
# - DynamoDB 테이블
# - ElastiCache 클러스터
# - DocumentDB, Neptune
```

##### 1.5 스토리지 데이터 수집
```bash
# 실행 스크립트: steampipe_storage_collection.sh
# 수집 데이터:
# - S3 버킷 (설정, 정책, 메트릭)
# - EBS 볼륨, 스냅샷
# - EFS 파일 시스템
# - FSx 파일 시스템
```

##### 1.6 보안 데이터 수집
```bash
# 실행 스크립트: steampipe_security_collection.sh
# 수집 데이터:
# - IAM 사용자, 역할, 정책
# - KMS 키, 암호화 상태
# - CloudTrail, Config 설정
# - GuardDuty, Security Hub 결과
```

##### 1.7 애플리케이션 서비스 데이터 수집
```bash
# 실행 스크립트: steampipe_application_collection.sh
# 수집 데이터:
# - API Gateway (REST, HTTP API)
# - Lambda 함수
# - SNS 토픽, SQS 큐
# - EventBridge 규칙
```

##### 1.8 모니터링 데이터 수집
```bash
# 실행 스크립트: steampipe_monitoring_collection.sh
# 수집 데이터:
# - CloudWatch 로그 그룹, 메트릭
# - X-Ray 서비스 맵
# - Systems Manager 파라미터
# - CloudFormation 스택
```

##### 1.9 Infrastructure as Code 분석
```bash
# 실행 스크립트: steampipe_iac_analysis_collection.sh
# 수집 데이터:
# - CloudFormation 스택, 템플릿
# - Terraform 상태 분석
# - CDK 구성 분석
# - 리소스 태깅 현황
```

#### 2. 종합 데이터 수집 실행
```bash
# 메인 수집 스크립트: aws-comprehensive-analysis.sh
# 모든 개별 수집 스크립트를 순차 실행
# 진행률 표시 및 오류 처리 포함
# 수집 완료 후 데이터 검증 수행
```

### 데이터 수집 결과물
모든 수집된 데이터는 `~/amazonqcli_lab/report/` 디렉토리에 JSON 형태로 저장됩니다:

#### 네트워킹 관련 파일
- `networking_vpc.json` - VPC 정보
- `networking_subnets.json` - 서브넷 정보
- `security_groups.json` - 보안 그룹 정보
- `networking_route_tables.json` - 라우팅 테이블

#### 컴퓨팅 관련 파일
- `compute_ec2_instances.json` - EC2 인스턴스
- `compute_asg_detailed.json` - Auto Scaling 그룹
- `compute_alb_detailed.json` - Application Load Balancer
- `compute_target_groups.json` - Target Groups

#### 데이터베이스 관련 파일
- `database_rds_instances.json` - RDS 인스턴스
- `database_dynamodb_tables.json` - DynamoDB 테이블
- `database_elasticache_clusters.json` - ElastiCache

#### 스토리지 관련 파일
- `storage_s3_buckets.json` - S3 버킷
- `storage_ebs_volumes.json` - EBS 볼륨
- `storage_efs_filesystems.json` - EFS 파일 시스템

#### 보안 관련 파일
- `security_iam_users.json` - IAM 사용자
- `security_iam_roles.json` - IAM 역할
- `security_kms_keys.json` - KMS 키

#### 애플리케이션 관련 파일
- `application_api_gateway_rest_apis.json` - API Gateway
- `iac_lambda_functions.json` - Lambda 함수
- `application_sns_topics.json` - SNS 토픽
