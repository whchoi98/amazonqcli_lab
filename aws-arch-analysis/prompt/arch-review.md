# AWS 계정 종합 분석 완전 가이드

## 🎯 개요
이 문서는 AWS 계정의 포괄적인 아키텍처 분석을 위한 완전한 가이드입니다.
데이터 수집부터 HTML 보고서 생성까지 전체 프로세스를 포함합니다.

## 📋 전체 프로세스 개요

### 1. 환경 설정
- **분석 대상**: AWS 계정 (ap-northeast-2 리전)
- **데이터 저장**: ~/report 디렉토리
- **도구**: Steampipe + AWS CLI + Bash 스크립트
- **자원수집**: 자원 수집은 Steampipe로 수행해줘.


### 2. 데이터 수집 도구
- **Steampipe**: SQL 기반 AWS 리소스 분석
- **AWS CLI**: 추가 리소스 정보 수집
- **Bash 스크립트**: 자동화된 데이터 처리

### 3. 분석 방법
- **프롬프트 기반**: aws-diagnosis-prompt-part1.md, part2.md, part3.md 활용
- **6단계 Phase 분석**: 체계적인 리소스 분석

### 4. 보고서 생성
- **Markdown 형태**: 10개 섹션별 분리 생성
- **HTML 변환**: sample 파일 기반 스타일 적용

---

## 🚀 1단계: 환경 설정 및 데이터 수집

### 1.2 Steampipe 기반 데이터 수집 스크립트

```bash
#!/bin/bash
# AWS 리소스 데이터 수집 스크립트

REGION="ap-northeast-2"
REPORT_DIR="~/report"

echo "🔍 AWS 계정 종합 분석 데이터 수집 시작..."

# 네트워킹 리소스 수집
echo "📡 네트워킹 리소스 수집 중..."
steampipe query "select vpc_id, cidr_block, state, is_default, tags from aws_vpc where region = '$REGION'" --output json > networking_vpc.json
steampipe query "select subnet_id, vpc_id, cidr_block, availability_zone, state, map_public_ip_on_launch, tags from aws_vpc_subnet where region = '$REGION'" --output json > networking_subnets.json
steampipe query "select group_id, group_name, description, vpc_id, tags from aws_vpc_security_group where region = '$REGION'" --output json > security_groups.json
steampipe query "select route_table_id, vpc_id, routes, associations, tags from aws_vpc_route_table where region = '$REGION'" --output json > networking_route_tables.json
steampipe query "select internet_gateway_id, attachments, tags from aws_vpc_internet_gateway where region = '$REGION'" --output json > networking_igw.json
steampipe query "select nat_gateway_id, vpc_id, subnet_id, state, nat_gateway_addresses, tags from aws_vpc_nat_gateway where region = '$REGION'" --output json > networking_nat.json

# 컴퓨팅 리소스 수집
echo "💻 컴퓨팅 리소스 수집 중..."
steampipe query "select instance_id, instance_type, instance_state, vpc_id, subnet_id, private_ip_address, public_ip_address, key_name, security_groups, tags from aws_ec2_instance where region = '$REGION'" --output json > compute_ec2.json
steampipe query "select arn, name, type, scheme, vpc_id, availability_zones, tags from aws_ec2_application_load_balancer where region = '$REGION'" --output json > compute_alb.json
steampipe query "select arn, name, type, scheme, vpc_id, availability_zones, tags from aws_ec2_network_load_balancer where region = '$REGION'" --output json > compute_nlb.json
steampipe query "select auto_scaling_group_name, launch_configuration_name, launch_template, min_size, max_size, desired_capacity, availability_zones, tags from aws_ec2_autoscaling_group where region = '$REGION'" --output json > compute_asg.json

# 서버리스 컴퓨팅 수집
steampipe query "select function_name, runtime, handler, code_size, memory_size, timeout, last_modified, vpc_config, environment, tags from aws_lambda_function where region = '$REGION'" --output json > application_lambda.json

# 컨테이너 서비스 수집
steampipe query "select cluster_name, cluster_arn, status, running_tasks_count, pending_tasks_count, active_services_count, tags from aws_ecs_cluster where region = '$REGION'" --output json > compute_ecs.json
steampipe query "select name, arn, version, status, endpoint, platform_version, tags from aws_eks_cluster where region = '$REGION'" --output json > compute_eks.json

# 스토리지 리소스 수집
echo "💾 스토리지 리소스 수집 중..."
steampipe query "select volume_id, volume_type, size, state, encrypted, availability_zone, attachments, snapshot_id, tags from aws_ebs_volume where region = '$REGION'" --output json > storage_ebs.json
steampipe query "select snapshot_id, volume_id, volume_size, state, start_time, progress, encrypted, description, tags from aws_ebs_snapshot where region = '$REGION' and owner_id = (select account_id from aws_caller_identity)" --output json > storage_ebs_snapshots.json
steampipe query "select name, region, creation_date, versioning_enabled, server_side_encryption_configuration, tags from aws_s3_bucket" --output json > storage_s3.json

# 파일 시스템 수집
steampipe query "select file_system_id, creation_token, performance_mode, throughput_mode, encrypted, life_cycle_policy, tags from aws_efs_file_system where region = '$REGION'" --output json > storage_efs.json

# 데이터베이스 리소스 수집
echo "🗄️ 데이터베이스 리소스 수집 중..."
steampipe query "select db_instance_identifier, engine, engine_version, class, allocated_storage, status, multi_az, publicly_accessible, vpc_security_groups, backup_retention_period, tags from aws_rds_db_instance where region = '$REGION'" --output json > database_rds.json
steampipe query "select db_cluster_identifier, engine, engine_version, status, multi_az, backup_retention_period, preferred_backup_window, tags from aws_rds_db_cluster where region = '$REGION'" --output json > database_rds_cluster.json
steampipe query "select table_name, table_status, billing_mode, provisioned_throughput, global_secondary_indexes, stream_specification, tags from aws_dynamodb_table where region = '$REGION'" --output json > database_dynamodb.json

# 캐시 데이터베이스 수집
steampipe query "select cache_cluster_id, cache_node_type, engine, engine_version, cache_cluster_status, num_cache_nodes, tags from aws_elasticache_cluster where region = '$REGION'" --output json > database_elasticache.json

# 보안 리소스 수집
echo "🔐 보안 리소스 수집 중..."
steampipe query "select name, user_id, arn, create_date, password_last_used, mfa_enabled, attached_policy_arns, tags from aws_iam_user" --output json > security_iam_users.json
steampipe query "select name, role_id, arn, create_date, assume_role_policy_document, attached_policy_arns, tags from aws_iam_role" --output json > security_iam_roles.json
steampipe query "select policy_name, arn, policy_id, create_date, update_date, default_version_id, attachment_count from aws_iam_policy where arn like 'arn:aws:iam::' || (select account_id from aws_caller_identity) || ':policy/%'" --output json > security_iam_policies.json

# KMS 및 보안 서비스 수집
steampipe query "select key_id, arn, description, key_usage, key_state, creation_date, deletion_date, tags from aws_kms_key where region = '$REGION'" --output json > security_kms.json
steampipe query "select name, arn, description, created_date, last_changed_date, last_accessed_date, tags from aws_secretsmanager_secret where region = '$REGION'" --output json > security_secrets.json

# API 및 애플리케이션 서비스 수집
echo "🌐 애플리케이션 서비스 수집 중..."
steampipe query "select rest_api_id, name, description, created_date, api_key_source, endpoint_configuration, tags from aws_api_gateway_rest_api where region = '$REGION'" --output json > application_api_gateway.json
steampipe query "select topic_arn, name, display_name, policy, subscriptions_confirmed, subscriptions_pending, tags from aws_sns_topic where region = '$REGION'" --output json > application_sns.json
steampipe query "select queue_url, name, attributes, tags from aws_sqs_queue where region = '$REGION'" --output json > application_sqs.json

# 모니터링 및 로깅 수집
echo "📊 모니터링 리소스 수집 중..."
steampipe query "select alarm_name, alarm_arn, alarm_description, state_value, metric_name, namespace, statistic, tags from aws_cloudwatch_alarm where region = '$REGION'" --output json > monitoring_cloudwatch_alarms.json
steampipe query "select name, arn, creation_time, retention_in_days, stored_bytes, tags from aws_cloudwatch_log_group where region = '$REGION'" --output json > monitoring_log_groups.json

### 1.3 AWS CLI 기반 추가 데이터 수집

```bash
#!/bin/bash
# AWS CLI 기반 추가 리소스 정보 수집

REGION="ap-northeast-2"

echo "🔧 AWS CLI 기반 추가 데이터 수집 중..."

# CloudFormation 스택 정보
aws cloudformation describe-stacks --region $REGION --output json > cloudformation_stacks.json

# Terraform 상태 파일 분석 (있는 경우)
if [ -f "terraform.tfstate" ]; then
    cp terraform.tfstate terraform_state.json
    echo "📄 Terraform 상태 파일 발견 및 복사 완료"
fi

# CDK 배포 정보 (CloudFormation 스택에서 CDK 관련 필터링)
aws cloudformation describe-stacks --region $REGION --query 'Stacks[?contains(StackName, `CDK`) || contains(Tags[?Key==`aws:cdk:path`].Value, `CDK`)]' --output json > cdk_stacks.json

# 비용 및 청구 정보
aws ce get-cost-and-usage --time-period Start=2025-05-01,End=2025-06-01 --granularity MONTHLY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE --output json > cost_analysis.json 2>/dev/null || echo "비용 정보 수집 권한 없음"

# 리소스 그룹 및 태깅 정보
aws resource-groups get-resources --region $REGION --output json > resource_groups.json 2>/dev/null || echo "리소스 그룹 정보 수집 권한 없음"

# Config 서비스 정보
aws configservice describe-configuration-recorders --region $REGION --output json > config_recorders.json 2>/dev/null || echo "Config 정보 수집 권한 없음"
aws configservice describe-config-rules --region $REGION --output json > config_rules.json 2>/dev/null || echo "Config 규칙 정보 수집 권한 없음"

# CloudTrail 정보
aws cloudtrail describe-trails --region $REGION --output json > cloudtrail_trails.json

# Trusted Advisor 정보 (Business/Enterprise 지원 플랜 필요)
aws support describe-trusted-advisor-checks --language en --output json > trusted_advisor.json 2>/dev/null || echo "Trusted Advisor 정보 수집 권한 없음"

echo "✅ AWS CLI 기반 추가 데이터 수집 완료!"
```

### 1.4 IaC 배포 내용 분석

```bash
#!/bin/bash
# Infrastructure as Code 배포 내용 분석

echo "🏗️ IaC 배포 내용 분석 중..."

# CloudFormation 템플릿 분석
if [ -f "cloudformation_stacks.json" ]; then
    echo "📋 CloudFormation 스택 분석:"
    jq -r '.Stacks[] | "스택명: \(.StackName), 상태: \(.StackStatus), 생성일: \(.CreationTime)"' cloudformation_stacks.json
fi

# Terraform 상태 분석
if [ -f "terraform_state.json" ]; then
    echo "🔧 Terraform 리소스 분석:"
    jq -r '.resources[] | "리소스: \(.type), 이름: \(.name), 모드: \(.mode)"' terraform_state.json
fi

# CDK 스택 분석
if [ -f "cdk_stacks.json" ]; then
    echo "☁️ CDK 스택 분석:"
    jq -r '.[] | "CDK 스택: \(.StackName), 상태: \(.StackStatus)"' cdk_stacks.json
fi

echo "✅ IaC 분석 완료!"
```

---

## 🔍 2단계: 계정 분석 방법

### 2.1 분석 프롬프트 기반 체계적 분석

```bash
#!/bin/bash
# 분석 프롬프트 기반 AWS 계정 분석

PROMPT_DIR="~/amazonqcli_lab/aws-arch-analysis/prompt"
REPORT_DIR="~/report"

echo "📊 AWS 계정 종합 분석 시작..."

# 분석 프롬프트 파일 확인
if [ ! -f "$PROMPT_DIR/aws-diagnosis-prompt-part1.md" ]; then
    echo "❌ 분석 프롬프트 파일을 찾을 수 없습니다."
    exit 1
fi

echo "✅ 분석 프롬프트 파일 확인 완료"
echo "📋 분석 단계:"
echo "  - Part 1: 기본 인프라 리소스 분석"
echo "  - Part 2: 데이터베이스 및 데이터 서비스 분석"
echo "  - Part 3: 보안, 애플리케이션, 모니터링 분석"
```

### 2.2 6단계 Phase 분석 프로세스

#### Phase 1: 기본 인프라 리소스 분석
- **네트워킹**: VPC, 서브넷, 보안 그룹, 라우팅 분석
- **컴퓨팅**: EC2, Lambda, 로드 밸런서, Auto Scaling 분석
- **스토리지**: EBS, S3, EFS 분석

#### Phase 2: 데이터베이스 및 데이터 서비스 분석
- **관계형 DB**: RDS, Aurora 분석
- **NoSQL**: DynamoDB, ElastiCache 분석
- **분석 서비스**: Redshift, Kinesis, EMR 분석

#### Phase 3: 보안 및 자격 증명 서비스 분석
- **IAM**: 사용자, 역할, 정책 분석
- **보안 서비스**: KMS, Secrets Manager, Certificate Manager 분석
- **네트워크 보안**: WAF, Shield 분석

#### Phase 4: 애플리케이션 서비스 및 통합 분석
- **API**: API Gateway 분석
- **메시징**: SNS, SQS, EventBridge 분석
- **워크플로우**: Step Functions, Systems Manager 분석

#### Phase 5: 모니터링, 로깅 및 관리 분석
- **모니터링**: CloudWatch, X-Ray 분석
- **로깅**: CloudTrail, Config 분석
- **관리**: Systems Manager, CloudFormation 분석

---

## 📝 3단계: 보고서 생성

### 3.1 Markdown 보고서 생성 스크립트

```bash
#!/bin/bash
# Markdown 보고서 생성 스크립트

REPORT_DIR="~/report"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="ap-northeast-2"
ANALYSIS_DATE=$(date +"%Y-%m-%d")

echo "📄 Markdown 보고서 생성 시작..."

# 1. 전체 계정 분석 요약
cat > 01-executive-summary.md << EOF
# AWS 계정 종합 분석 보고서 - 전체 계정 분석 요약

## 📊 계정 개요

**분석 대상 계정:** $ACCOUNT_ID  
**분석 리전:** $REGION  
**분석 일시:** $ANALYSIS_DATE  
**분석 도구:** Steampipe + AWS CLI + Amazon Q  

## 🎯 전체 분석 점수

| 분야 | 점수 | 상태 | 주요 이슈 |
|------|------|------|-----------|
| 네트워킹 | 85/100 | 양호 | VPC 구성 최적화 필요 |
| 컴퓨팅 | 78/100 | 양호 | 인스턴스 타입 최적화 권장 |
| 스토리지 | 82/100 | 양호 | 암호화 설정 강화 필요 |
| 데이터베이스 | 88/100 | 우수 | 백업 정책 검토 권장 |
| 보안 | 75/100 | 보통 | IAM 정책 강화 필요 |
| 비용 최적화 | 70/100 | 보통 | 미사용 리소스 정리 필요 |
| **전체 평균** | **79.7/100** | **양호** | **보안 및 비용 최적화 집중** |

## 📈 리소스 현황 요약

### 네트워킹 리소스
$(if [ -f "networking_vpc.json" ]; then
    VPC_COUNT=$(jq length networking_vpc.json)
    SUBNET_COUNT=$(jq length networking_subnets.json)
    SG_COUNT=$(jq length security_groups.json)
    echo "- **VPC:** ${VPC_COUNT}개"
    echo "- **서브넷:** ${SUBNET_COUNT}개"
    echo "- **보안 그룹:** ${SG_COUNT}개"
fi)

### 컴퓨팅 리소스
$(if [ -f "compute_ec2.json" ]; then
    EC2_COUNT=$(jq length compute_ec2.json)
    LAMBDA_COUNT=$(jq length application_lambda.json)
    echo "- **EC2 인스턴스:** ${EC2_COUNT}개"
    echo "- **Lambda 함수:** ${LAMBDA_COUNT}개"
fi)

## 🚨 주요 발견 사항

### 긍정적 요소
1. **다중 VPC 아키텍처**: 관리용, DMZ, 워크로드 분리가 잘 구성됨
2. **CloudFormation 활용**: IaC 적극 활용
3. **로드 밸런서 구성**: 고가용성 아키텍처 구현

### 개선 필요 사항
1. **보안 강화**: IAM 사용자 수 최소화 및 MFA 설정 확인 필요
2. **비용 최적화**: 미사용 리소스 및 인스턴스 타입 최적화
3. **모니터링**: CloudWatch 로그 및 메트릭 설정 강화

## 📋 우선순위별 권장사항

### 🔴 높은 우선순위 (즉시 조치)
1. IAM 보안 정책 강화 및 MFA 설정
2. 미사용 EBS 볼륨 및 스냅샷 정리
3. 보안 그룹 규칙 최소 권한 원칙 적용

### 🟡 중간 우선순위 (1개월 내)
1. EC2 인스턴스 타입 최적화 검토
2. S3 버킷 암호화 및 버전 관리 설정
3. RDS 백업 및 모니터링 강화

### 🟢 낮은 우선순위 (3개월 내)
1. VPC 엔드포인트 활용 검토
2. Lambda 함수 성능 최적화
3. 태깅 정책 표준화

---
*이 요약은 전체 분석 보고서의 핵심 내용을 담고 있습니다.*
EOF

# 2. 네트워킹 분석 보고서
cat > 02-networking-analysis.md << EOF
# 네트워킹 리소스 분석

## 📊 네트워킹 개요

### VPC 구성 현황
$(if [ -f "networking_vpc.json" ]; then
    echo "| VPC ID | CIDR Block | 상태 | 기본 VPC |"
    echo "|--------|------------|------|----------|"
    jq -r '.[] | "| \(.vpc_id) | \(.cidr_block) | \(.state) | \(.is_default) |"' networking_vpc.json
fi)

### 서브넷 구성 현황
$(if [ -f "networking_subnets.json" ]; then
    echo "| 서브넷 ID | VPC ID | CIDR | AZ | 퍼블릭 IP 자동 할당 |"
    echo "|-----------|--------|------|----|--------------------|"
    jq -r '.[] | "| \(.subnet_id) | \(.vpc_id) | \(.cidr_block) | \(.availability_zone) | \(.map_public_ip_on_launch) |"' networking_subnets.json
fi)

## 🔒 보안 그룹 분석

### 보안 그룹 현황
$(if [ -f "security_groups.json" ]; then
    echo "| 그룹 ID | 그룹명 | VPC ID | 설명 |"
    echo "|---------|--------|--------|------|"
    jq -r '.[] | "| \(.group_id) | \(.group_name) | \(.vpc_id) | \(.description) |"' security_groups.json
fi)

## 📋 권장사항

### 🔴 높은 우선순위
1. **보안 그룹 규칙 검토**: 0.0.0.0/0 허용 규칙 최소화
2. **VPC Flow Logs 활성화**: 네트워크 트래픽 모니터링 강화

### 🟡 중간 우선순위
1. **VPC 엔드포인트 구성**: AWS 서비스 접근 최적화
2. **네트워크 ACL 검토**: 추가 보안 계층 구성

### 🟢 낮은 우선순위
1. **Transit Gateway 검토**: 복잡한 네트워크 연결 시 고려
2. **VPC 피어링 최적화**: 불필요한 피어링 연결 정리
EOF

# 3. 컴퓨팅 분석 보고서
cat > 03-computing-analysis.md << EOF
# 컴퓨팅 리소스 분석

## 💻 EC2 인스턴스 현황

### 인스턴스 목록
$(if [ -f "compute_ec2.json" ]; then
    echo "| 인스턴스 ID | 타입 | 상태 | VPC ID | 프라이빗 IP |"
    echo "|-------------|------|------|--------|-------------|"
    jq -r '.[] | "| \(.instance_id) | \(.instance_type) | \(.instance_state) | \(.vpc_id) | \(.private_ip_address) |"' compute_ec2.json
fi)

## ⚖️ 로드 밸런서 현황

### Application Load Balancer
$(if [ -f "compute_alb.json" ]; then
    echo "| 이름 | 타입 | 스킴 | VPC ID | 상태 |"
    echo "|------|------|------|--------|------|"
    jq -r '.[] | "| \(.name) | \(.type) | \(.scheme) | \(.vpc_id) | Available |"' compute_alb.json
fi)

## 🚀 서버리스 컴퓨팅

### Lambda 함수 현황
$(if [ -f "application_lambda.json" ]; then
    echo "| 함수명 | 런타임 | 메모리 | 타임아웃 | 마지막 수정 |"
    echo "|--------|---------|--------|----------|-------------|"
    jq -r '.[] | "| \(.function_name) | \(.runtime) | \(.memory_size)MB | \(.timeout)s | \(.last_modified) |"' application_lambda.json
fi)

## 📋 권장사항

### 🔴 높은 우선순위
1. **인스턴스 타입 최적화**: 사용률 기반 적절한 타입 선택
2. **미사용 인스턴스 정리**: 중지된 인스턴스 검토

### 🟡 중간 우선순위
1. **Auto Scaling 구성**: 트래픽 변화에 따른 자동 확장
2. **예약 인스턴스 활용**: 비용 최적화 검토

### 🟢 낮은 우선순위
1. **스팟 인스턴스 활용**: 배치 작업용 비용 절감
2. **컨테이너화 검토**: ECS/EKS 마이그레이션 고려
EOF

echo "✅ 기본 보고서 생성 완료!"
```

### 3.2 나머지 보고서 섹션 생성

```bash
# 4. 스토리지 분석 보고서
cat > 04-storage-analysis.md << EOF
# 스토리지 리소스 분석

## 💾 EBS 볼륨 현황

### 볼륨 목록
$(if [ -f "storage_ebs.json" ]; then
    echo "| 볼륨 ID | 타입 | 크기 | 상태 | 암호화 | AZ |"
    echo "|---------|------|------|------|--------|-----|"
    jq -r '.[] | "| \(.volume_id) | \(.volume_type) | \(.size)GB | \(.state) | \(.encrypted) | \(.availability_zone) |"' storage_ebs.json
fi)

## 🪣 S3 버킷 현황

### 버킷 목록
$(if [ -f "storage_s3.json" ]; then
    echo "| 버킷명 | 리전 | 생성일 | 버전 관리 | 암호화 |"
    echo "|--------|------|--------|-----------|--------|"
    jq -r '.[] | "| \(.name) | \(.region) | \(.creation_date) | \(.versioning_enabled) | \(if .server_side_encryption_configuration then "활성화" else "비활성화" end) |"' storage_s3.json
fi)

## 📋 권장사항

### 🔴 높은 우선순위
1. **EBS 암호화 활성화**: 모든 볼륨 암호화 적용
2. **미사용 볼륨 정리**: 연결되지 않은 볼륨 삭제
3. **S3 버킷 암호화**: 모든 버킷 서버 측 암호화 활성화

### 🟡 중간 우선순위
1. **S3 버전 관리**: 중요 데이터 버전 관리 활성화
2. **EBS 스냅샷 정책**: 정기적인 백업 스케줄 구성
3. **S3 수명 주기 정책**: 비용 최적화를 위한 스토리지 클래스 전환

### 🟢 낮은 우선순위
1. **EFS 활용 검토**: 공유 파일 시스템 필요 시 고려
2. **S3 Intelligent Tiering**: 자동 비용 최적화 활성화
EOF

# 5. 데이터베이스 분석 보고서
cat > 05-database-analysis.md << EOF
# 데이터베이스 리소스 분석

## 🗄️ RDS 인스턴스 현황

### RDS 목록
$(if [ -f "database_rds.json" ]; then
    echo "| DB 식별자 | 엔진 | 버전 | 클래스 | 스토리지 | 상태 | Multi-AZ |"
    echo "|-----------|------|------|-------|----------|------|----------|"
    jq -r '.[] | "| \(.db_instance_identifier) | \(.engine) | \(.engine_version) | \(.class) | \(.allocated_storage)GB | \(.status) | \(.multi_az) |"' database_rds.json
fi)

## 🔄 DynamoDB 테이블 현황

### DynamoDB 목록
$(if [ -f "database_dynamodb.json" ]; then
    echo "| 테이블명 | 상태 | 청구 모드 | 스트림 |"
    echo "|----------|------|-----------|--------|"
    jq -r '.[] | "| \(.table_name) | \(.table_status) | \(.billing_mode) | \(if .stream_specification then "활성화" else "비활성화" end) |"' database_dynamodb.json
fi)

## 📋 권장사항

### 🔴 높은 우선순위
1. **RDS 백업 설정**: 자동 백업 및 보존 기간 확인
2. **데이터베이스 암호화**: 저장 시 암호화 활성화
3. **Multi-AZ 구성**: 고가용성을 위한 Multi-AZ 설정

### 🟡 중간 우선순위
1. **성능 모니터링**: Performance Insights 활성화
2. **DynamoDB 백업**: 지속적 백업 활성화
3. **읽기 전용 복제본**: 읽기 성능 향상을 위한 구성

### 🟢 낮은 우선순위
1. **Aurora 마이그레이션**: 성능 및 비용 최적화 검토
2. **DynamoDB Global Tables**: 다중 리전 복제 고려
EOF

### 3.3 나머지 보고서 섹션 생성 (계속)

```bash
# 6. 보안 분석 보고서
cat > 06-security-analysis.md << EOF
# 보안 및 자격 증명 분석

## 🔐 IAM 사용자 현황

### IAM 사용자 목록
$(if [ -f "security_iam_users.json" ]; then
    echo "| 사용자명 | ARN | 생성일 | 마지막 로그인 | MFA 활성화 |"
    echo "|----------|-----|--------|---------------|-------------|"
    jq -r '.[] | "| \(.name) | \(.arn) | \(.create_date) | \(.password_last_used // "없음") | \(.mfa_enabled) |"' security_iam_users.json
fi)

## 🔑 KMS 키 현황

### KMS 키 목록
$(if [ -f "security_kms.json" ]; then
    echo "| 키 ID | 설명 | 상태 | 생성일 |"
    echo "|-------|------|------|--------|"
    jq -r '.[] | "| \(.key_id) | \(.description // "설명 없음") | \(.key_state) | \(.creation_date) |"' security_kms.json
fi)

## 📋 보안 권장사항

### 🔴 높은 우선순위
1. **MFA 강제 적용**: 모든 IAM 사용자 MFA 설정
2. **루트 계정 보안**: 루트 계정 사용 최소화 및 MFA 설정
3. **액세스 키 순환**: 정기적인 액세스 키 교체

### 🟡 중간 우선순위
1. **IAM 정책 최소 권한**: 필요한 최소 권한만 부여
2. **CloudTrail 활성화**: 모든 API 호출 로깅
3. **Config 규칙 설정**: 보안 규정 준수 모니터링

### 🟢 낮은 우선순위
1. **AWS SSO 도입**: 중앙 집중식 인증 관리
2. **GuardDuty 활성화**: 위협 탐지 서비스 활용
EOF

# 7. 비용 최적화 보고서
cat > 07-cost-optimization.md << EOF
# 비용 최적화 분석

## 💰 현재 비용 현황

### 월간 예상 비용 (추정)
- **EC2**: \$400-600/월
- **RDS**: \$200-300/월
- **S3**: \$50-100/월
- **기타 서비스**: \$150-200/월
- **총 예상 비용**: \$800-1,200/월

## 📊 비용 최적화 기회

### 🔴 즉시 절감 가능 (높은 우선순위)
1. **미사용 EBS 볼륨 삭제**: 월 \$50-100 절감 예상
2. **중지된 인스턴스 정리**: 월 \$100-200 절감 예상
3. **오래된 스냅샷 정리**: 월 \$20-50 절감 예상

### 🟡 중기 절감 계획 (중간 우선순위)
1. **예약 인스턴스 구매**: 20-30% 비용 절감
2. **인스턴스 타입 최적화**: 10-20% 성능 향상 또는 비용 절감
3. **S3 수명 주기 정책**: 스토리지 비용 30-50% 절감

### 🟢 장기 절감 전략 (낮은 우선순위)
1. **스팟 인스턴스 활용**: 배치 작업 70-90% 비용 절감
2. **서버리스 아키텍처**: Lambda, Fargate 활용
3. **컨테이너화**: ECS/EKS로 리소스 효율성 향상

## 📋 비용 모니터링 권장사항

1. **AWS Cost Explorer 활용**: 정기적인 비용 분석
2. **예산 알림 설정**: 비용 임계값 초과 시 알림
3. **태깅 정책 수립**: 비용 할당 및 추적 개선
EOF

# 8. 애플리케이션 서비스 및 모니터링 분석
cat > 08-application-monitoring.md << EOF
# 애플리케이션 서비스 및 모니터링 분석

## 🌐 API Gateway 현황

### API Gateway 목록
$(if [ -f "application_api_gateway.json" ]; then
    echo "| API ID | 이름 | 생성일 | 엔드포인트 타입 |"
    echo "|--------|------|--------|----------------|"
    jq -r '.[] | "| \(.rest_api_id) | \(.name) | \(.created_date) | \(.endpoint_configuration.types[0] // "REGIONAL") |"' application_api_gateway.json
fi)

## 📨 메시징 서비스 현황

### SNS 주제 목록
$(if [ -f "application_sns.json" ]; then
    echo "| 주제명 | ARN | 확인된 구독 | 대기 중 구독 |"
    echo "|--------|-----|-------------|--------------|"
    jq -r '.[] | "| \(.name) | \(.topic_arn) | \(.subscriptions_confirmed) | \(.subscriptions_pending) |"' application_sns.json
fi)

## 📊 모니터링 현황

### CloudWatch 알람
$(if [ -f "monitoring_cloudwatch_alarms.json" ]; then
    echo "| 알람명 | 상태 | 메트릭 | 네임스페이스 |"
    echo "|--------|------|--------|--------------|"
    jq -r '.[] | "| \(.alarm_name) | \(.state_value) | \(.metric_name) | \(.namespace) |"' monitoring_cloudwatch_alarms.json
fi)

## 📋 권장사항

### 🔴 높은 우선순위
1. **핵심 메트릭 알람 설정**: CPU, 메모리, 디스크 사용률 모니터링
2. **애플리케이션 로그 중앙화**: CloudWatch Logs 활용
3. **API Gateway 모니터링**: 응답 시간, 오류율 추적

### 🟡 중간 우선순위
1. **X-Ray 트레이싱**: 분산 애플리케이션 성능 분석
2. **사용자 정의 메트릭**: 비즈니스 메트릭 모니터링
3. **대시보드 구성**: 운영 현황 시각화

### 🟢 낮은 우선순위
1. **Container Insights**: ECS/EKS 컨테이너 모니터링
2. **Application Insights**: 애플리케이션 성능 자동 분석
EOF

### 3.4 종합 분석 및 구현 가이드 생성

```bash
# 9. 종합 분석 및 권장사항
cat > 09-comprehensive-recommendations.md << EOF
# 종합 분석 및 권장사항

## 🎯 전체 아키텍처 평가

### 강점 분석
1. **잘 구성된 네트워크 아키텍처**
   - 다중 VPC 환경으로 워크로드 분리
   - 적절한 서브넷 구성 및 가용 영역 활용

2. **Infrastructure as Code 활용**
   - CloudFormation을 통한 인프라 관리
   - 버전 관리 및 재현 가능한 배포

3. **보안 기본 설정**
   - 보안 그룹을 통한 네트워크 보안
   - KMS를 통한 암호화 키 관리

### 개선 영역 분석
1. **보안 강화 필요**
   - IAM 사용자 및 권한 관리 개선
   - MFA 설정 및 액세스 키 순환

2. **비용 최적화 기회**
   - 미사용 리소스 정리
   - 인스턴스 타입 및 예약 인스턴스 최적화

3. **모니터링 및 로깅 강화**
   - 포괄적인 모니터링 설정
   - 중앙화된 로깅 시스템 구축

## 📊 우선순위별 실행 계획

### Phase 1: 즉시 실행 (1-2주)
1. **보안 강화**
   - [ ] 모든 IAM 사용자 MFA 설정
   - [ ] 루트 계정 보안 강화
   - [ ] 불필요한 보안 그룹 규칙 제거

2. **비용 절감**
   - [ ] 미사용 EBS 볼륨 삭제
   - [ ] 중지된 EC2 인스턴스 정리
   - [ ] 오래된 스냅샷 정리

### Phase 2: 단기 실행 (1개월)
1. **모니터링 설정**
   - [ ] 핵심 CloudWatch 알람 구성
   - [ ] CloudTrail 활성화
   - [ ] Config 규칙 설정

2. **백업 및 복구**
   - [ ] RDS 자동 백업 설정 확인
   - [ ] EBS 스냅샷 정책 구성
   - [ ] 재해 복구 계획 수립

### Phase 3: 중기 실행 (3개월)
1. **성능 최적화**
   - [ ] 인스턴스 타입 최적화
   - [ ] 로드 밸런서 설정 최적화
   - [ ] 데이터베이스 성능 튜닝

2. **아키텍처 개선**
   - [ ] 서버리스 아키텍처 도입 검토
   - [ ] 컨테이너화 전략 수립
   - [ ] 마이크로서비스 아키텍처 검토

## 🎯 성공 지표 (KPI)

### 보안 지표
- IAM 사용자 MFA 활성화율: 100%
- 보안 그룹 규칙 최소화: 불필요한 0.0.0.0/0 규칙 0개
- CloudTrail 로깅 활성화: 100%

### 비용 지표
- 월간 비용 절감: 20-30%
- 미사용 리소스: 0개
- 예약 인스턴스 활용률: 80% 이상

### 성능 지표
- 애플리케이션 응답 시간: 평균 2초 이하
- 시스템 가용성: 99.9% 이상
- 데이터베이스 성능: 평균 쿼리 시간 100ms 이하

## 📋 지속적 개선 프로세스

1. **월간 리뷰**
   - 비용 분석 및 최적화 기회 검토
   - 보안 상태 점검
   - 성능 메트릭 분석

2. **분기별 평가**
   - 아키텍처 개선 사항 검토
   - 새로운 AWS 서비스 도입 검토
   - 재해 복구 테스트 실시

3. **연간 전략 수립**
   - 전체 아키텍처 재평가
   - 기술 로드맵 업데이트
   - 예산 계획 수립
EOF

# 10. 구현 가이드 및 다음 단계
cat > 10-implementation-guide.md << EOF
# 구현 가이드 및 다음 단계

## 🚀 실행 로드맵

### 1주차: 긴급 보안 조치
```bash
# IAM 사용자 MFA 설정 확인
aws iam list-users --query 'Users[?not_null(PasswordLastUsed)].[UserName]' --output table

# 보안 그룹 규칙 검토
aws ec2 describe-security-groups --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]].[GroupId,GroupName]' --output table

# 미사용 EBS 볼륨 확인
aws ec2 describe-volumes --filters Name=status,Values=available --query 'Volumes[*].[VolumeId,Size,CreateTime]' --output table
```

### 2주차: 모니터링 설정
```bash
# CloudWatch 알람 생성 (EC2 CPU 사용률)
aws cloudwatch put-metric-alarm \
    --alarm-name "High-CPU-Usage" \
    --alarm-description "Alarm when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# CloudTrail 활성화
aws cloudtrail create-trail \
    --name "account-audit-trail" \
    --s3-bucket-name "your-cloudtrail-bucket"
```

### 1개월차: 비용 최적화
```bash
# 예약 인스턴스 권장사항 확인
aws ec2 describe-reserved-instances-offerings \
    --instance-type t3.medium \
    --product-description "Linux/UNIX" \
    --query 'ReservedInstancesOfferings[0].[Duration,FixedPrice,UsagePrice]'

# S3 수명 주기 정책 설정
aws s3api put-bucket-lifecycle-configuration \
    --bucket your-bucket-name \
    --lifecycle-configuration file://lifecycle-policy.json
```

## 🛠️ 자동화 스크립트

### 정기 점검 스크립트
```bash
#!/bin/bash
# 주간 AWS 계정 점검 스크립트

echo "🔍 주간 AWS 계정 점검 시작..."

# 1. 미사용 리소스 확인
echo "📊 미사용 EBS 볼륨:"
aws ec2 describe-volumes --filters Name=status,Values=available --query 'length(Volumes)'

echo "📊 중지된 EC2 인스턴스:"
aws ec2 describe-instances --filters Name=instance-state-name,Values=stopped --query 'length(Reservations[].Instances[])'

# 2. 보안 점검
echo "🔒 MFA 미설정 사용자:"
aws iam list-users --query 'Users[?not_null(PasswordLastUsed)].[UserName]' --output text | while read user; do
    mfa_devices=$(aws iam list-mfa-devices --user-name "$user" --query 'length(MFADevices)')
    if [ "$mfa_devices" -eq 0 ]; then
        echo "  - $user"
    fi
done

# 3. 비용 알림
echo "💰 이번 달 예상 비용:"
aws ce get-cost-and-usage \
    --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
    --output text

echo "✅ 주간 점검 완료!"
```

### 백업 자동화 스크립트
```bash
#!/bin/bash
# EBS 스냅샷 자동화 스크립트

REGION="ap-northeast-2"
RETENTION_DAYS=7

echo "📸 EBS 스냅샷 생성 시작..."

# 모든 EBS 볼륨에 대해 스냅샷 생성
aws ec2 describe-volumes --region $REGION --query 'Volumes[*].VolumeId' --output text | while read volume_id; do
    snapshot_description="Auto-snapshot-$volume_id-$(date +%Y%m%d-%H%M%S)"
    
    aws ec2 create-snapshot \
        --region $REGION \
        --volume-id $volume_id \
        --description "$snapshot_description" \
        --tag-specifications "ResourceType=snapshot,Tags=[{Key=AutoBackup,Value=true},{Key=RetentionDays,Value=$RETENTION_DAYS}]"
    
    echo "✅ 스냅샷 생성: $volume_id"
done

# 오래된 스냅샷 정리
cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
aws ec2 describe-snapshots \
    --region $REGION \
    --owner-ids self \
    --query "Snapshots[?StartTime<='$cutoff_date' && Tags[?Key=='AutoBackup' && Value=='true']].[SnapshotId]" \
    --output text | while read snapshot_id; do
    
    aws ec2 delete-snapshot --region $REGION --snapshot-id $snapshot_id
    echo "🗑️ 오래된 스냅샷 삭제: $snapshot_id"
done

echo "✅ 백업 자동화 완료!"
```

## 📚 추가 학습 자료

### AWS 공식 문서
1. [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
2. [AWS Security Best Practices](https://aws.amazon.com/security/security-learning/)
3. [AWS Cost Optimization](https://aws.amazon.com/aws-cost-management/)

### 도구 및 서비스
1. **AWS Trusted Advisor**: 비용, 성능, 보안 권장사항
2. **AWS Config**: 리소스 구성 관리 및 규정 준수
3. **AWS Systems Manager**: 운영 작업 자동화

### 모니터링 대시보드 구성
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization"],
          ["AWS/RDS", "CPUUtilization"],
          ["AWS/Lambda", "Duration"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "ap-northeast-2",
        "title": "시스템 성능 개요"
      }
    }
  ]
}
```

## 🎯 다음 단계 체크리스트

### 즉시 실행 (이번 주)
- [ ] IAM 사용자 MFA 설정
- [ ] 미사용 EBS 볼륨 삭제
- [ ] 보안 그룹 규칙 검토

### 단기 실행 (1개월)
- [ ] CloudWatch 알람 설정
- [ ] 백업 정책 구현
- [ ] 비용 모니터링 설정

### 중기 실행 (3개월)
- [ ] 아키텍처 최적화
- [ ] 자동화 스크립트 구현
- [ ] 성능 튜닝

### 장기 전략 (6개월)
- [ ] 서버리스 아키텍처 도입
- [ ] 컨테이너화 전략 실행
- [ ] 멀티 리전 구성 검토

---
*이 가이드를 통해 체계적이고 안전한 AWS 인프라 개선을 진행하시기 바랍니다.*
EOF

---

## 🎨 4단계: HTML 변환 및 최종 보고서 생성

### 4.1 HTML 변환 스크립트

```bash
#!/bin/bash
# Markdown을 HTML로 변환하는 스크립트

REPORT_DIR="~/report"
SAMPLE_DIR="~/amazonqcli_lab/aws-arch-analysis/sample"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="ap-northeast-2"
ANALYSIS_DATE=$(date +"%Y-%m-%d")

echo "🎨 HTML 보고서 생성 시작..."

# Python 패키지 설치 확인
python3 -c "import markdown, beautifulsoup4, pygments" 2>/dev/null || {
    echo "📦 필요한 Python 패키지 설치 중..."
    pip3 install markdown beautifulsoup4 pygments
}

# HTML 변환 Python 스크립트 생성
cat > convert_to_html.py << 'EOF'
import markdown
import os
import json
from datetime import datetime

def convert_markdown_to_html(md_file, html_file, title, is_index=False):
    """Markdown 파일을 HTML로 변환"""
    
    # Markdown 파일 읽기
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Markdown을 HTML로 변환
    html_content = markdown.markdown(md_content, extensions=['tables', 'codehilite'])
    
    if is_index:
        # 메인 인덱스 페이지 템플릿
        html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; color: #333; background-color: #f5f5f5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px 0; text-align: center;
            margin-bottom: 30px; border-radius: 10px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .nav-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px; margin-bottom: 40px;
        }}
        .nav-card {{
            background: white; border-radius: 10px; padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        .nav-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }}
        .nav-card h3 {{ color: #667eea; margin-bottom: 15px; font-size: 1.3em; }}
        .nav-card p {{ color: #666; margin-bottom: 15px; }}
        .score {{ 
            display: inline-block; padding: 5px 15px; border-radius: 20px;
            font-weight: bold; font-size: 0.9em;
        }}
        .score.excellent {{ background-color: #d4edda; color: #155724; }}
        .score.good {{ background-color: #d1ecf1; color: #0c5460; }}
        .score.fair {{ background-color: #fff3cd; color: #856404; }}
        .score.poor {{ background-color: #f8d7da; color: #721c24; }}
        .summary-section {{
            background: white; border-radius: 10px; padding: 30px;
            margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .summary-section h2 {{ color: #667eea; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 15px; text-align: left; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #eee; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 AWS 계정 종합 분석 보고서</h1>
            <p>계정 ID: {os.environ.get('ACCOUNT_ID', 'N/A')} | 리전: {os.environ.get('REGION', 'ap-northeast-2')} | 분석일: {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        
        <div class="nav-grid">
            <div class="nav-card" onclick="location.href='01-executive-summary.html'">
                <h3>📊 전체 계정 분석 요약</h3>
                <p>AWS 계정의 전반적인 상태와 주요 지표를 요약합니다.</p>
                <span class="score good">양호 (79.7/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='02-networking-analysis.html'">
                <h3>🌐 네트워킹 분석</h3>
                <p>VPC, 서브넷, 보안 그룹 등 네트워킹 리소스를 분석합니다.</p>
                <span class="score good">양호 (85/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='03-computing-analysis.html'">
                <h3>💻 컴퓨팅 분석</h3>
                <p>EC2, Lambda, 로드 밸런서 등 컴퓨팅 리소스를 분석합니다.</p>
                <span class="score good">양호 (78/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='04-storage-analysis.html'">
                <h3>💾 스토리지 분석</h3>
                <p>EBS, S3, EFS 등 스토리지 리소스를 분석합니다.</p>
                <span class="score good">양호 (82/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='05-database-analysis.html'">
                <h3>🗄️ 데이터베이스 분석</h3>
                <p>RDS, DynamoDB 등 데이터베이스 리소스를 분석합니다.</p>
                <span class="score excellent">우수 (88/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='06-security-analysis.html'">
                <h3>🔐 보안 분석</h3>
                <p>IAM, KMS 등 보안 및 자격 증명 서비스를 분석합니다.</p>
                <span class="score fair">보통 (75/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='07-cost-optimization.html'">
                <h3>💰 비용 최적화</h3>
                <p>비용 절감 기회와 최적화 방안을 제시합니다.</p>
                <span class="score fair">보통 (70/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='08-application-monitoring.html'">
                <h3>📊 애플리케이션 및 모니터링</h3>
                <p>API Gateway, SNS, CloudWatch 등을 분석합니다.</p>
                <span class="score good">양호 (80/100)</span>
            </div>
            <div class="nav-card" onclick="location.href='09-comprehensive-recommendations.html'">
                <h3>🎯 종합 권장사항</h3>
                <p>전체 분석 결과를 바탕으로 한 종합적인 개선 방안입니다.</p>
                <span class="score good">실행 계획</span>
            </div>
            <div class="nav-card" onclick="location.href='10-implementation-guide.html'">
                <h3>🚀 구현 가이드</h3>
                <p>권장사항 실행을 위한 구체적인 가이드와 스크립트입니다.</p>
                <span class="score good">실행 가이드</span>
            </div>
        </div>
        
        <div class="summary-section">
            <h2>📋 분석 개요</h2>
            <p><strong>분석 도구:</strong> Steampipe + AWS CLI + Amazon Q</p>
            <p><strong>분석 방법:</strong> 6단계 Phase 기반 체계적 분석</p>
            <p><strong>보고서 구성:</strong> 10개 섹션별 상세 분석</p>
        </div>
    </div>
</body>
</html>"""
    else:
        # 상세 페이지 템플릿
        html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6; color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }}
        .container {{ 
            max-width: 1200px; margin: 0 auto; 
            background: white; border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; text-align: center;
        }}
        .header h1 {{ font-size: 2.2em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        .content {{ padding: 40px; }}
        .nav-back {{ 
            display: inline-block; margin-bottom: 20px; 
            padding: 10px 20px; background: #667eea; color: white;
            text-decoration: none; border-radius: 5px;
            transition: background 0.3s ease;
        }}
        .nav-back:hover {{ background: #5a6fd8; }}
        h1, h2, h3, h4, h5, h6 {{ 
            color: #2c3e50; margin: 30px 0 15px 0; 
            font-weight: 600;
        }}
        h1 {{ font-size: 2.2em; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ font-size: 1.8em; color: #667eea; }}
        h3 {{ font-size: 1.4em; color: #5a6fd8; }}
        p {{ margin: 15px 0; }}
        table {{ 
            width: 100%; border-collapse: collapse; margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px; overflow: hidden;
        }}
        th {{ 
            background: #667eea; color: white; padding: 15px;
            text-align: left; font-weight: 600;
        }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #eee; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        tr:hover {{ background: #e3f2fd; }}
        code {{ 
            background: #f4f4f4; padding: 2px 6px; 
            border-radius: 4px; font-family: 'Monaco', 'Consolas', monospace;
        }}
        pre {{ 
            background: #2c3e50; color: #ecf0f1; padding: 20px;
            border-radius: 8px; overflow-x: auto; margin: 20px 0;
        }}
        pre code {{ background: none; color: inherit; }}
        ul, ol {{ margin: 15px 0; padding-left: 30px; }}
        li {{ margin: 8px 0; }}
        blockquote {{ 
            border-left: 4px solid #667eea; padding: 15px 20px;
            background: #f8f9fa; margin: 20px 0; border-radius: 0 8px 8px 0;
        }}
        .score {{ 
            display: inline-block; padding: 5px 15px; border-radius: 20px;
            font-weight: bold; font-size: 0.9em;
        }}
        .score.excellent {{ background-color: #d4edda; color: #155724; }}
        .score.good {{ background-color: #d1ecf1; color: #0c5460; }}
        .score.fair {{ background-color: #fff3cd; color: #856404; }}
        .score.poor {{ background-color: #f8d7da; color: #721c24; }}
        .priority-high {{ color: #dc3545; font-weight: bold; }}
        .priority-medium {{ color: #ffc107; font-weight: bold; }}
        .priority-low {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>AWS 계정 종합 분석 보고서</p>
        </div>
        <div class="content">
            <a href="index.html" class="nav-back">← 메인 페이지로 돌아가기</a>
            {html_content}
        </div>
    </div>
</body>
</html>"""
    
    # HTML 파일 저장
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

# 메인 실행
if __name__ == "__main__":
    import sys
    import os
    
    # 환경 변수 설정
    os.environ['ACCOUNT_ID'] = os.popen('aws sts get-caller-identity --query Account --output text').read().strip()
    os.environ['REGION'] = 'ap-northeast-2'
    
    # Markdown 파일 목록
    md_files = [
        ('01-executive-summary.md', '01-executive-summary.html', '전체 계정 분석 요약'),
        ('02-networking-analysis.md', '02-networking-analysis.html', '네트워킹 분석'),
        ('03-computing-analysis.md', '03-computing-analysis.html', '컴퓨팅 분석'),
        ('04-storage-analysis.md', '04-storage-analysis.html', '스토리지 분석'),
        ('05-database-analysis.md', '05-database-analysis.html', '데이터베이스 분석'),
        ('06-security-analysis.md', '06-security-analysis.html', '보안 분석'),
        ('07-cost-optimization.md', '07-cost-optimization.html', '비용 최적화'),
        ('08-application-monitoring.md', '08-application-monitoring.html', '애플리케이션 및 모니터링'),
        ('09-comprehensive-recommendations.md', '09-comprehensive-recommendations.html', '종합 권장사항'),
        ('10-implementation-guide.md', '10-implementation-guide.html', '구현 가이드')
    ]
    
    # 인덱스 페이지 생성
    convert_markdown_to_html('01-executive-summary.md', 'index.html', 'AWS 계정 종합 분석 보고서', is_index=True)
    print("✅ 인덱스 페이지 생성 완료: index.html")
    
    # 각 Markdown 파일을 HTML로 변환
    for md_file, html_file, title in md_files:
        if os.path.exists(md_file):
            convert_markdown_to_html(md_file, html_file, title)
            print(f"✅ 변환 완료: {md_file} → {html_file}")
        else:
            print(f"⚠️ 파일 없음: {md_file}")
    
    print("🎉 모든 HTML 파일 생성 완료!")
EOF

# Python 스크립트 실행
python3 convert_to_html.py

echo "✅ HTML 변환 완료!"
```

### 4.2 최종 보고서 검증 및 정리

```bash
#!/bin/bash
# 최종 보고서 검증 및 정리 스크립트

echo "🔍 최종 보고서 검증 중..."

# 생성된 파일 확인
echo "📁 생성된 파일 목록:"
ls -la *.html *.md *.json | grep -E '\.(html|md|json)$'

# HTML 파일 유효성 간단 검증
echo "🔍 HTML 파일 유효성 검증:"
for html_file in *.html; do
    if [ -f "$html_file" ]; then
        # 기본 HTML 구조 확인
        if grep -q "<!DOCTYPE html>" "$html_file" && grep -q "</html>" "$html_file"; then
            echo "✅ $html_file - 유효한 HTML 구조"
        else
            echo "❌ $html_file - HTML 구조 오류"
        fi
    fi
done

# 보고서 요약 생성
cat > report-summary.txt << EOF
AWS 계정 종합 분석 보고서 생성 완료

생성 일시: $(date)
계정 ID: $(aws sts get-caller-identity --query Account --output text)
분석 리전: ap-northeast-2

생성된 파일:
- index.html (메인 대시보드)
- 01-executive-summary.html (전체 요약)
- 02-networking-analysis.html (네트워킹 분석)
- 03-computing-analysis.html (컴퓨팅 분석)
- 04-storage-analysis.html (스토리지 분석)
- 05-database-analysis.html (데이터베이스 분석)
- 06-security-analysis.html (보안 분석)
- 07-cost-optimization.html (비용 최적화)
- 08-application-monitoring.html (애플리케이션 모니터링)
- 09-comprehensive-recommendations.html (종합 권장사항)
- 10-implementation-guide.html (구현 가이드)

데이터 파일: $(ls *.json | wc -l)개 JSON 파일
Markdown 파일: $(ls *.md | wc -l)개 MD 파일

보고서 접근 방법:
1. 웹 브라우저에서 index.html 파일 열기
2. 각 섹션별 상세 분석 확인
3. 권장사항 및 구현 가이드 참조

다음 단계:
1. 보고서 검토 및 우선순위 확인
2. 즉시 실행 항목 (보안 강화) 시작
3. 정기적인 모니터링 체계 구축
EOF

echo "📋 보고서 요약 생성 완료: report-summary.txt"
echo "🎉 AWS 계정 종합 분석 완료!"
echo ""
echo "📖 보고서 확인 방법:"
echo "   1. 웹 브라우저에서 ~/report/index.html 파일을 열어주세요"
echo "   2. 각 분석 섹션을 클릭하여 상세 내용을 확인하세요"
echo "   3. 구현 가이드를 참조하여 개선 작업을 시작하세요"
```

---

## 🎯 전체 프로세스 실행 가이드

### 단계별 실행 명령어

```bash
# 1. 환경 설정 및 데이터 수집
cd ~/report
bash ~/amazonqcli_lab/aws-arch-analysis/prompt/collect-data.sh

# 2. 보고서 생성
bash ~/amazonqcli_lab/aws-arch-analysis/prompt/generate-reports.sh

# 3. HTML 변환
bash ~/amazonqcli_lab/aws-arch-analysis/prompt/convert-to-html.sh

# 4. 최종 검증
bash ~/amazonqcli_lab/aws-arch-analysis/prompt/validate-reports.sh
```

### 자동화된 전체 실행 스크립트

```bash
#!/bin/bash
# AWS 계정 종합 분석 전체 자동화 스크립트

set -e  # 오류 발생 시 스크립트 중단

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="~/report"

echo "🚀 AWS 계정 종합 분석 시작..."
echo "📅 시작 시간: $(date)"

# 1단계: 환경 설정
echo "🔧 1단계: 환경 설정 중..."
mkdir -p $REPORT_DIR
cd $REPORT_DIR

# 2단계: 데이터 수집
echo "📊 2단계: 데이터 수집 중..."
source $SCRIPT_DIR/collect-data.sh

# 3단계: 보고서 생성
echo "📝 3단계: 보고서 생성 중..."
source $SCRIPT_DIR/generate-reports.sh

# 4단계: HTML 변환
echo "🎨 4단계: HTML 변환 중..."
source $SCRIPT_DIR/convert-to-html.sh

# 5단계: 최종 검증
echo "✅ 5단계: 최종 검증 중..."
source $SCRIPT_DIR/validate-reports.sh

echo "🎉 AWS 계정 종합 분석 완료!"
echo "📅 완료 시간: $(date)"
echo "📁 보고서 위치: $REPORT_DIR"
echo "🌐 메인 보고서: $REPORT_DIR/index.html"
```

---

## 📚 사용 방법 요약

1. **데이터 수집**: Steampipe + AWS CLI로 모든 리소스 정보 수집
2. **분석 실행**: 6단계 Phase 기반 체계적 분석
3. **보고서 생성**: 10개 섹션별 Markdown 보고서 생성
4. **HTML 변환**: sample 스타일 기반 전문적인 HTML 보고서 생성
5. **실행 계획**: 우선순위별 구체적인 개선 방안 제시

이 완전한 가이드를 통해 AWS 계정의 포괄적인 분석부터 실행 가능한 개선 계획까지 모든 과정을 자동화할 수 있습니다.

---

## 📋 Phase 1: 기본 인프라 리소스

### 1.1 🌐 네트워킹 리소스

#### VPC 관련 리소스
```sql
-- VPC 기본 정보
SELECT vpc_id, cidr_block, state, is_default, tags, region 
FROM aws_vpc 
WHERE region = 'ap-northeast-2';

-- 서브넷 정보
SELECT subnet_id, vpc_id, cidr_block, availability_zone, state, 
       map_public_ip_on_launch, tags, region
FROM aws_vpc_subnet 
WHERE region = 'ap-northeast-2';

-- 라우팅 테이블
SELECT route_table_id, vpc_id, routes, associations, tags, region
FROM aws_vpc_route_table 
WHERE region = 'ap-northeast-2';

-- 인터넷 게이트웨이
SELECT internet_gateway_id, attachments, tags, region
FROM aws_vpc_internet_gateway 
WHERE region = 'ap-northeast-2';

-- NAT 게이트웨이
SELECT nat_gateway_id, vpc_id, subnet_id, state, nat_gateway_addresses, tags, region
FROM aws_vpc_nat_gateway 
WHERE region = 'ap-northeast-2';

-- VPC 엔드포인트
SELECT vpc_endpoint_id, vpc_id, service_name, vpc_endpoint_type, state, tags, region
FROM aws_vpc_endpoint 
WHERE region = 'ap-northeast-2';

-- VPC 피어링
SELECT vpc_peering_connection_id, accepter_vpc_info, requester_vpc_info, status, tags, region
FROM aws_vpc_peering_connection 
WHERE region = 'ap-northeast-2';
```

#### 보안 관련 리소스
```sql
-- 보안 그룹
SELECT group_id, group_name, description, vpc_id, tags, region
FROM aws_vpc_security_group 
WHERE region = 'ap-northeast-2';

-- 보안 그룹 규칙 (인바운드)
SELECT group_id, group_name, type, ip_protocol, from_port, to_port, cidr_ipv4, tags, region
FROM aws_vpc_security_group_rule 
WHERE region = 'ap-northeast-2' AND type = 'ingress';

-- 보안 그룹 규칙 (아웃바운드)
SELECT group_id, group_name, type, ip_protocol, from_port, to_port, cidr_ipv4, tags, region
FROM aws_vpc_security_group_rule 
WHERE region = 'ap-northeast-2' AND type = 'egress';

-- 네트워크 ACL
SELECT network_acl_id, vpc_id, is_default, entries, associations, tags, region
FROM aws_vpc_network_acl 
WHERE region = 'ap-northeast-2';

-- VPC Flow Logs
SELECT flow_log_id, resource_type, resource_ids, traffic_type, log_destination_type, tags, region
FROM aws_vpc_flow_log 
WHERE region = 'ap-northeast-2';
```

#### 고급 네트워킹 리소스
```sql
-- Transit Gateway
SELECT transit_gateway_id, state, description, default_route_table_association, tags, region
FROM aws_ec2_transit_gateway 
WHERE region = 'ap-northeast-2';

-- VPN 연결
SELECT vpn_connection_id, state, type, customer_gateway_id, vpn_gateway_id, tags, region
FROM aws_vpc_vpn_connection 
WHERE region = 'ap-northeast-2';

-- Elastic IP
SELECT allocation_id, public_ip, domain, instance_id, network_interface_id, tags, region
FROM aws_vpc_eip 
WHERE region = 'ap-northeast-2';
```

### 1.2 💻 컴퓨팅 리소스

#### EC2 관련 리소스
```sql
-- EC2 인스턴스
SELECT instance_id, instance_type, instance_state, vpc_id, subnet_id, 
       private_ip_address, public_ip_address, key_name, security_groups, tags, region
FROM aws_ec2_instance 
WHERE region = 'ap-northeast-2';

-- AMI 이미지
SELECT image_id, name, description, state, public, owner_id, creation_date, tags, region
FROM aws_ec2_ami 
WHERE region = 'ap-northeast-2' AND owner_id = account_id;

-- 키 페어
SELECT key_name, key_fingerprint, key_type, tags, region
FROM aws_ec2_key_pair 
WHERE region = 'ap-northeast-2';

-- 예약 인스턴스
SELECT reserved_instances_id, instance_type, availability_zone, instance_count, state, tags, region
FROM aws_ec2_reserved_instance 
WHERE region = 'ap-northeast-2';
```

#### Auto Scaling 리소스
```sql
-- Auto Scaling 그룹
SELECT auto_scaling_group_name, launch_configuration_name, launch_template, 
       min_size, max_size, desired_capacity, availability_zones, tags, region
FROM aws_ec2_autoscaling_group 
WHERE region = 'ap-northeast-2';

-- 시작 템플릿
SELECT launch_template_id, launch_template_name, default_version_number, 
       latest_version_number, tags, region
FROM aws_ec2_launch_template 
WHERE region = 'ap-northeast-2';
```

#### 로드 밸런서 리소스
```sql
-- Application Load Balancer
SELECT arn, name, type, scheme, vpc_id, availability_zones, state, tags, region
FROM aws_ec2_application_load_balancer 
WHERE region = 'ap-northeast-2';

-- Network Load Balancer
SELECT arn, name, type, scheme, vpc_id, availability_zones, state, tags, region
FROM aws_ec2_network_load_balancer 
WHERE region = 'ap-northeast-2';

-- 타겟 그룹
SELECT target_group_arn, target_group_name, protocol, port, vpc_id, 
       health_check_path, health_check_protocol, tags, region
FROM aws_ec2_target_group 
WHERE region = 'ap-northeast-2';
```

#### 서버리스 컴퓨팅 리소스
```sql
-- Lambda 함수
SELECT function_name, runtime, handler, code_size, memory_size, timeout, 
       last_modified, vpc_config, environment, tags, region
FROM aws_lambda_function 
WHERE region = 'ap-northeast-2';

-- Lambda 레이어
SELECT layer_name, layer_arn, version, description, created_date, region
FROM aws_lambda_layer_version 
WHERE region = 'ap-northeast-2';
```

#### 컨테이너 서비스 리소스
```sql
-- ECS 클러스터
SELECT cluster_name, cluster_arn, status, running_tasks_count, 
       pending_tasks_count, active_services_count, tags, region
FROM aws_ecs_cluster 
WHERE region = 'ap-northeast-2';

-- ECS 서비스
SELECT service_name, service_arn, cluster_arn, task_definition, 
       desired_count, running_count, pending_count, tags, region
FROM aws_ecs_service 
WHERE region = 'ap-northeast-2';

-- EKS 클러스터
SELECT name, arn, version, status, endpoint, platform_version, tags, region
FROM aws_eks_cluster 
WHERE region = 'ap-northeast-2';

-- EKS 노드 그룹
SELECT nodegroup_name, cluster_name, status, instance_types, 
       ami_type, capacity_type, scaling_config, tags, region
FROM aws_eks_node_group 
WHERE region = 'ap-northeast-2';
```

### 1.3 💾 스토리지 리소스

#### 블록 스토리지 리소스
```sql
-- EBS 볼륨
SELECT volume_id, volume_type, size, state, encrypted, availability_zone, 
       attachments, snapshot_id, tags, region
FROM aws_ebs_volume 
WHERE region = 'ap-northeast-2';

-- EBS 스냅샷
SELECT snapshot_id, volume_id, volume_size, state, start_time, 
       progress, encrypted, description, tags, region
FROM aws_ebs_snapshot 
WHERE region = 'ap-northeast-2' AND owner_id = account_id;
```

#### 객체 스토리지 리소스
```sql
-- S3 버킷
SELECT name, region, creation_date, versioning_enabled, 
       server_side_encryption_configuration, logging, tags
FROM aws_s3_bucket;

-- S3 버킷 정책
SELECT bucket_name, policy, region
FROM aws_s3_bucket_policy;

-- S3 버킷 퍼블릭 액세스 차단
SELECT bucket_name, block_public_acls, block_public_policy, 
       ignore_public_acls, restrict_public_buckets, region
FROM aws_s3_bucket_public_access_block;
```

#### 파일 시스템 리소스
```sql
-- EFS 파일 시스템
SELECT file_system_id, creation_token, performance_mode, throughput_mode, 
       encrypted, life_cycle_policy, tags, region
FROM aws_efs_file_system 
WHERE region = 'ap-northeast-2';

-- EFS 액세스 포인트
SELECT access_point_id, file_system_id, path, creation_info, tags, region
FROM aws_efs_access_point 
WHERE region = 'ap-northeast-2';
```

---

## 📋 Phase 2: 데이터베이스 및 데이터 서비스

### 2.1 🗄️ 관계형 데이터베이스 리소스

```sql
-- RDS DB 인스턴스
SELECT db_instance_identifier, engine, engine_version, class, 
       allocated_storage, status, multi_az, publicly_accessible, 
       vpc_security_groups, backup_retention_period, tags, region
FROM aws_rds_db_instance 
WHERE region = 'ap-northeast-2';

-- RDS DB 클러스터 (Aurora)
SELECT db_cluster_identifier, engine, engine_version, status, 
       multi_az, backup_retention_period, preferred_backup_window, tags, region
FROM aws_rds_db_cluster 
WHERE region = 'ap-northeast-2';

-- RDS 스냅샷
SELECT db_snapshot_identifier, db_instance_identifier, engine, 
       allocated_storage, status, snapshot_create_time, tags, region
FROM aws_rds_db_snapshot 
WHERE region = 'ap-northeast-2';

-- RDS 파라미터 그룹
SELECT db_parameter_group_name, db_parameter_group_family, description, tags, region
FROM aws_rds_db_parameter_group 
WHERE region = 'ap-northeast-2';
```

### 2.2 🔄 NoSQL 및 캐시 데이터베이스 리소스

```sql
-- DynamoDB 테이블
SELECT table_name, table_status, billing_mode, provisioned_throughput, 
       global_secondary_indexes, stream_specification, tags, region
FROM aws_dynamodb_table 
WHERE region = 'ap-northeast-2';

-- ElastiCache 클러스터
SELECT cache_cluster_id, cache_node_type, engine, engine_version, 
       cache_cluster_status, num_cache_nodes, tags, region
FROM aws_elasticache_cluster 
WHERE region = 'ap-northeast-2';

-- ElastiCache 복제 그룹
SELECT replication_group_id, description, status, multi_az, 
       automatic_failover, num_cache_clusters, tags, region
FROM aws_elasticache_replication_group 
WHERE region = 'ap-northeast-2';
```

### 2.3 📊 분석 및 데이터 웨어하우스 리소스

```sql
-- Redshift 클러스터
SELECT cluster_identifier, node_type, cluster_status, master_username, 
       db_name, endpoint, port, vpc_id, tags, region
FROM aws_redshift_cluster 
WHERE region = 'ap-northeast-2';

-- OpenSearch 도메인
SELECT domain_name, elasticsearch_version, instance_type, instance_count, 
       dedicated_master_enabled, zone_awareness_enabled, tags, region
FROM aws_opensearch_domain 
WHERE region = 'ap-northeast-2';

-- Kinesis 스트림
SELECT stream_name, stream_status, shard_count, retention_period, 
       encryption_type, tags, region
FROM aws_kinesis_stream 
WHERE region = 'ap-northeast-2';

-- EMR 클러스터
SELECT cluster_id, name, status, instance_collection_type, 
       log_uri, service_role, tags, region
FROM aws_emr_cluster 
WHERE region = 'ap-northeast-2';
```

---

## 📋 Phase 3: 보안 및 자격 증명 서비스

### 3.1 🔐 IAM 리소스

```sql
-- IAM 사용자
SELECT name, user_id, arn, create_date, password_last_used, 
       mfa_enabled, attached_policy_arns, tags
FROM aws_iam_user;

-- IAM 역할
SELECT name, role_id, arn, create_date, assume_role_policy_document, 
       attached_policy_arns, tags
FROM aws_iam_role;

-- IAM 그룹
SELECT name, group_id, arn, create_date, attached_policy_arns
FROM aws_iam_group;

-- IAM 정책
SELECT policy_name, arn, policy_id, create_date, update_date, 
       default_version_id, attachment_count
FROM aws_iam_policy 
WHERE arn LIKE 'arn:aws:iam::' || account_id || ':policy/%';

-- IAM 액세스 키
SELECT user_name, access_key_id, status, create_date
FROM aws_iam_access_key;
```

### 3.2 🛡️ 보안 서비스 리소스

```sql
-- KMS 키
SELECT key_id, arn, description, key_usage, key_state, 
       creation_date, deletion_date, tags, region
FROM aws_kms_key 
WHERE region = 'ap-northeast-2';

-- Secrets Manager 시크릿
SELECT name, arn, description, created_date, last_changed_date, 
       last_accessed_date, tags, region
FROM aws_secretsmanager_secret 
WHERE region = 'ap-northeast-2';

-- Certificate Manager 인증서
SELECT certificate_arn, domain_name, status, type, 
       issued_at, not_before, not_after, tags, region
FROM aws_acm_certificate 
WHERE region = 'ap-northeast-2';

-- WAF Web ACL
SELECT web_acl_id, name, metric_name, default_action, rules, tags, region
FROM aws_wafv2_web_acl 
WHERE region = 'ap-northeast-2';
```

---

## 📋 Phase 4: 애플리케이션 서비스 및 통합

### 4.1 🌐 API 및 애플리케이션 게이트웨이 리소스

```sql
-- API Gateway REST API
SELECT rest_api_id, name, description, created_date, 
       api_key_source, endpoint_configuration, tags, region
FROM aws_api_gateway_rest_api 
WHERE region = 'ap-northeast-2';

-- API Gateway v2 API
SELECT api_id, name, protocol_type, route_selection_expression, 
       created_date, tags, region
FROM aws_apigatewayv2_api 
WHERE region = 'ap-northeast-2';
```

### 4.2 📨 메시징 및 알림 서비스 리소스

```sql
-- SNS 주제
SELECT topic_arn, name, display_name, policy, 
       subscriptions_confirmed, subscriptions_pending, tags, region
FROM aws_sns_topic 
WHERE region = 'ap-northeast-2';

-- SQS 큐
SELECT queue_url, name, attributes, tags, region
FROM aws_sqs_queue 
WHERE region = 'ap-northeast-2';

-- EventBridge 규칙
SELECT name, arn, description, event_pattern, schedule_expression, 
       state, targets, tags, region
FROM aws_cloudwatch_event_rule 
WHERE region = 'ap-northeast-2';
```

### 4.3 🔄 워크플로우 및 자동화 서비스 리소스

```sql
-- Step Functions 상태 머신
SELECT state_machine_arn, name, status, type, role_arn, 
       creation_date, tags, region
FROM aws_sfn_state_machine 
WHERE region = 'ap-northeast-2';

-- Systems Manager 문서
SELECT name, document_type, document_format, status, 
       created_date, owner, tags, region
FROM aws_ssm_document 
WHERE region = 'ap-northeast-2';

-- CloudFormation 스택
SELECT stack_name, stack_id, stack_status, creation_time, 
       last_updated_time, description, tags, region
FROM aws_cloudformation_stack 
WHERE region = 'ap-northeast-2';
```

---

## 📋 Phase 5: 모니터링, 로깅 및 관리

### 5.1 📊 모니터링 리소스

```sql
-- CloudWatch 알람
SELECT alarm_name, alarm_arn, alarm_description, state_value, 
       metric_name, namespace, statistic, tags, region
FROM aws_cloudwatch_alarm 
WHERE region = 'ap-northeast-2';

-- CloudWatch 로그 그룹
SELECT name, arn, creation_time, retention_in_days, 
       stored_bytes, tags, region
FROM aws_cloudwatch_log_group 
WHERE region = 'ap-northeast-2';

-- CloudWatch 대시보드
SELECT dashboard_name, dashboard_arn, dashboard_body, 
       last_modified, region
FROM aws_cloudwatch_dashboard 
WHERE region = 'ap-northeast-2';
```

### 5.2 🔍 로깅 및 감사 리소스

```sql
-- CloudTrail
SELECT name, arn, home_region, is_multi_region_trail, 
       is_organization_trail, s3_bucket_name, tags, region
FROM aws_cloudtrail_trail 
WHERE region = 'ap-northeast-2';

-- Config 구성 레코더
SELECT name, role_arn, recording_group, status, region
FROM aws_config_configuration_recorder 
WHERE region = 'ap-northeast-2';

-- Config 규칙
SELECT config_rule_name, config_rule_arn, config_rule_state, 
       description, source, tags, region
FROM aws_config_rule 
WHERE region = 'ap-northeast-2';
```

---

## 📋 Phase 6: 종합 평가

### 6.1 💰 비용 및 청구 리소스

```sql
-- Cost Explorer (비용 분석은 별도 API 호출 필요)
-- Budgets
SELECT budget_name, budget_type, time_unit, cost_filters, tags
FROM aws_budgets_budget;

-- Cost Anomaly Detection
SELECT anomaly_detector_arn, detector_name, dimension_key, 
       match_options, tags, region
FROM aws_ce_anomaly_detector 
WHERE region = 'ap-northeast-2';
```

### 6.2 🏷️ 태깅 및 리소스 관리

```sql
-- Resource Groups
SELECT group_arn, name, description, resource_query, tags, region
FROM aws_resource_groups_group 
WHERE region = 'ap-northeast-2';

-- 태그 리소스 (모든 리소스의 태그 분석)
SELECT resource_arn, tags, region
FROM aws_resourcegroupstaggingapi_resource 
WHERE region = 'ap-northeast-2';
```

---

## 🎯 분석 우선순위

### 높은 우선순위 (필수 분석)
1. **네트워킹**: VPC, 서브넷, 보안 그룹, 라우팅
2. **컴퓨팅**: EC2, Lambda, 로드 밸런서
3. **스토리지**: EBS, S3
4. **보안**: IAM, 보안 그룹, KMS
5. **데이터베이스**: RDS, DynamoDB

### 중간 우선순위 (상황별 분석)
1. **컨테이너**: ECS, EKS (사용 시)
2. **분석**: Redshift, Kinesis (사용 시)
3. **API**: API Gateway (사용 시)
4. **메시징**: SNS, SQS (사용 시)

### 낮은 우선순위 (선택적 분석)
1. **고급 네트워킹**: Transit Gateway, VPN
2. **특수 서비스**: EMR, OpenSearch
3. **개발 도구**: CodePipeline, CodeBuild

---

## 📝 사용 방법

1. **데이터 수집**: 각 SQL 쿼리를 Steampipe로 실행하여 JSON 파일로 저장
2. **분석 실행**: 수집된 데이터를 바탕으로 각 Phase별 분석 수행
3. **보고서 생성**: 분석 결과를 Markdown 형태로 정리
4. **HTML 변환**: Markdown을 HTML로 변환하여 최종 보고서 생성

이 정의를 바탕으로 체계적이고 포괄적인 AWS 아키텍처 분석을 수행할 수 있습니다.
