# Steampipe 설치 및 사용 가이드

## Steampipe란?

Steampipe는 클라우드 인프라를 SQL로 쿼리할 수 있는 오픈소스 도구입니다. AWS, Azure, GCP 등 다양한 클라우드 서비스의 리소스를 표준 SQL 문법으로 조회하고 분석할 수 있습니다.

## 주요 특징

- **SQL 기반 쿼리**: 익숙한 SQL 문법으로 클라우드 리소스 조회
- **실시간 데이터**: API를 통해 실시간 클라우드 데이터 접근
- **다양한 플러그인**: AWS, Azure, GCP, Kubernetes 등 100+ 플러그인 지원
- **보안 및 컴플라이언스**: 보안 정책 및 컴플라이언스 체크 가능
- **확장성**: 커스텀 플러그인 개발 가능

## 설치 완료 상태

✅ **Steampipe v1.1.4** 설치 완료  
✅ **AWS 플러그인 v1.14.1** 설치 완료

## 기본 사용법

### 1. Steampipe 서비스 시작

```bash
# Steampipe 서비스 시작
steampipe service start

# 대화형 쿼리 모드 시작
steampipe query
```

### 2. 기본 AWS 리소스 조회

```sql
-- EC2 인스턴스 목록 조회
SELECT 
    instance_id,
    instance_type,
    instance_state,
    availability_zone,
    public_ip_address,
    private_ip_address
FROM aws_ec2_instance;

-- S3 버킷 목록 조회
SELECT 
    name,
    region,
    creation_date,
    versioning_enabled,
    public_access_block_configuration
FROM aws_s3_bucket;

-- IAM 사용자 목록 조회
SELECT 
    name,
    user_id,
    create_date,
    password_last_used,
    mfa_enabled
FROM aws_iam_user;
```

### 3. 보안 및 컴플라이언스 체크

```sql
-- 퍼블릭 액세스가 허용된 S3 버킷 찾기
SELECT 
    name,
    region,
    public_access_block_configuration
FROM aws_s3_bucket
WHERE public_access_block_configuration ->> 'BlockPublicAcls' = 'false'
   OR public_access_block_configuration ->> 'BlockPublicPolicy' = 'false';

-- 루트 액세스 키가 있는 계정 확인
SELECT 
    account_id,
    access_key_1_active,
    access_key_2_active
FROM aws_iam_account_summary
WHERE access_key_1_active = true 
   OR access_key_2_active = true;

-- 보안 그룹에서 0.0.0.0/0으로 열린 포트 확인
SELECT 
    group_id,
    group_name,
    ip_permissions
FROM aws_ec2_security_group
WHERE ip_permissions @> '[{"IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]';
```

### 4. 비용 분석 쿼리

```sql
-- 리전별 EC2 인스턴스 수 및 타입 분포
SELECT 
    region,
    instance_type,
    COUNT(*) as instance_count
FROM aws_ec2_instance
WHERE instance_state = 'running'
GROUP BY region, instance_type
ORDER BY region, instance_count DESC;

-- 사용하지 않는 EBS 볼륨 찾기
SELECT 
    volume_id,
    size,
    volume_type,
    state,
    availability_zone,
    create_time
FROM aws_ebs_volume
WHERE state = 'available';
```

### 5. 네트워크 분석

```sql
-- VPC 및 서브넷 정보
SELECT 
    v.vpc_id,
    v.cidr_block as vpc_cidr,
    v.is_default,
    s.subnet_id,
    s.cidr_block as subnet_cidr,
    s.availability_zone
FROM aws_vpc v
LEFT JOIN aws_vpc_subnet s ON v.vpc_id = s.vpc_id
ORDER BY v.vpc_id, s.subnet_id;

-- 인터넷 게이트웨이가 연결된 VPC
SELECT 
    v.vpc_id,
    v.cidr_block,
    i.internet_gateway_id,
    i.state
FROM aws_vpc v
JOIN aws_vpc_internet_gateway i ON v.vpc_id = ANY(i.attachments[*].vpc_id);
```

## 고급 사용법

### 1. 조인 쿼리 예제

```sql
-- EC2 인스턴스와 연결된 보안 그룹 정보
SELECT 
    i.instance_id,
    i.instance_type,
    i.instance_state,
    sg.group_id,
    sg.group_name,
    sg.description
FROM aws_ec2_instance i
CROSS JOIN JSONB_ARRAY_ELEMENTS(i.security_groups) AS sg_ref
JOIN aws_ec2_security_group sg ON sg.group_id = sg_ref ->> 'GroupId'
WHERE i.instance_state = 'running';
```

### 2. JSON 데이터 처리

```sql
-- S3 버킷 정책 분석
SELECT 
    name,
    region,
    policy -> 'Statement' as policy_statements
FROM aws_s3_bucket
WHERE policy IS NOT NULL;

-- EC2 인스턴스 태그 분석
SELECT 
    instance_id,
    tags ->> 'Name' as instance_name,
    tags ->> 'Environment' as environment,
    tags ->> 'Owner' as owner
FROM aws_ec2_instance
WHERE tags IS NOT NULL;
```

### 3. 시간 기반 분석

```sql
-- 최근 7일 내 생성된 리소스
SELECT 
    instance_id,
    instance_type,
    launch_time,
    instance_state
FROM aws_ec2_instance
WHERE launch_time >= NOW() - INTERVAL '7 days'
ORDER BY launch_time DESC;
```

## 유용한 명령어

```bash
# 사용 가능한 테이블 목록 확인
steampipe query "SELECT table_name FROM information_schema.tables WHERE table_schema = 'aws' ORDER BY table_name;"

# 특정 테이블의 스키마 확인
steampipe query "DESCRIBE aws_ec2_instance;"

# 쿼리 결과를 CSV로 출력
steampipe query "SELECT * FROM aws_s3_bucket;" --output csv

# 쿼리 결과를 JSON으로 출력
steampipe query "SELECT * FROM aws_s3_bucket;" --output json
```

## 설정 파일

Steampipe 설정은 `~/.steampipe/config/` 디렉터리에 저장됩니다:

```bash
# 설정 디렉터리 확인
ls -la ~/.steampipe/config/

# AWS 연결 설정 확인
cat ~/.steampipe/config/aws.spc
```

## 추가 플러그인 설치

```bash
# Azure 플러그인 설치
steampipe plugin install azure

# GCP 플러그인 설치
steampipe plugin install gcp

# Kubernetes 플러그인 설치
steampipe plugin install kubernetes

# 설치된 플러그인 목록 확인
steampipe plugin list
```

## 문제 해결

### 1. AWS 자격 증명 문제
```bash
# AWS CLI 설정 확인
aws configure list

# AWS 자격 증명 테스트
aws sts get-caller-identity
```

### 2. 연결 테스트
```bash
# Steampipe 연결 테스트
steampipe query "SELECT account_id FROM aws_caller_identity;"
```

### 3. 로그 확인
```bash
# Steampipe 로그 확인
steampipe service logs
```

## 보안 모범 사례

1. **최소 권한 원칙**: Steampipe용 IAM 역할에는 읽기 전용 권한만 부여
2. **자격 증명 관리**: AWS 자격 증명을 안전하게 관리
3. **네트워크 보안**: 필요한 경우에만 외부 접근 허용
4. **정기적 업데이트**: Steampipe와 플러그인을 정기적으로 업데이트

## 참고 자료

- [Steampipe 공식 문서](https://steampipe.io/docs)
- [AWS 플러그인 문서](https://hub.steampipe.io/plugins/turbot/aws)
- [Steampipe Hub](https://hub.steampipe.io/)
- [SQL 쿼리 예제](https://steampipe.io/docs/query/overview)

---

**설치 완료!** 이제 `steampipe query` 명령어로 AWS 리소스를 SQL로 조회할 수 있습니다.
