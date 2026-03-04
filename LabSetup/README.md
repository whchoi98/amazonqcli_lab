# LabSetup - Kiro CLI Lab 환경 구축

Kiro CLI와 MCP(Model Context Protocol) 서버를 활용한 AWS 인프라 실습 환경을 자동으로 구축하는 스크립트 모음입니다.

## 📋 목차

- [개요](#개요)
- [아키텍처](#아키텍처)
- [사전 요구사항](#사전-요구사항)
- [빠른 시작](#빠른-시작)
- [상세 가이드](#상세-가이드)
- [파일 구조](#파일-구조)
- [문제 해결](#문제-해결)
- [정리](#정리)

## 🚀 개요

이 디렉토리는 AWS 클라우드 환경에서 Kiro CLI를 활용한 실습 환경을 자동으로 구축합니다. 네트워킹 인프라부터 개발 도구, AI 지원 도구까지 포괄적인 환경을 제공합니다.

### 주요 특징
- **자동화된 인프라 배포**: CloudFormation을 통한 일관된 환경 구축
- **병렬 배포 지원**: 여러 VPC를 동시에 배포하여 시간 단축
- **개발 도구 통합**: VSCode, AWS CLI, kubectl, helm 등 필수 도구 자동 설치
- **AI 지원**: Kiro CLI와 MCP 서버 연동으로 향상된 개발 경험

## 🏗️ 아키텍처

### 네트워킹 구성
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    DMZ VPC      │    │     VPC01       │    │     VPC02       │
│  (Public/NAT)   │    │   (Private)     │    │   (Private)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │    Transit Gateway        │
                    │   (Cross-VPC Routing)     │
                    └───────────────────────────┘
```

### 서비스 구성
- **DMZ VPC**: 퍼블릭 서브넷, NAT Gateway, Redis, OpenSearch
- **VPC01**: 프라이빗 워크로드, Aurora MySQL
- **VPC02**: 추가 워크로드 영역
- **EKS**: 컨테이너 오케스트레이션 (선택적)

## 📋 사전 요구사항

- **AWS CLI 구성 완료**
  ```bash
  aws configure
  aws sts get-caller-identity
  ```
- **필요한 IAM 권한**
  - VPC, EC2, RDS, ElastiCache 관리 권한
  - CloudFormation 스택 생성/수정/삭제 권한
  - S3 버킷 생성 및 객체 업로드 권한
- **운영 체제**: Linux/macOS (bash 스크립트 실행 환경)

## 🚀 빠른 시작

### 1. 스크립트 실행 권한 부여
```bash
chmod +x *.sh
```

### 2. 기본 인프라 배포 (병렬 실행)
```bash
# 모든 VPC 동시 배포 (약 10-15분 소요)
./0.deploy-all-vpcs.sh

# Transit Gateway 배포
./0.deploy-tgw.sh
```

### 3. 개발 환경 설정
```bash
# VSCode 및 개발 도구 설치 (약 5-10분 소요)
./1.vscode-tools-installer.sh

# AWS 환경 변수 설정
./2.set-aws-env.sh

# KMS 키 구성
./3.kms-setup.sh
```

### 4. Kiro CLI 및 MCP 설정
```bash
# Python 3.12, uv, Node.js 설치
./4.install_core_mcp.sh

# MCP 구성 파일 생성
./5.setup-mcp-config.sh
```

## 📖 상세 가이드

### Phase 1: 네트워킹 인프라

#### 1. VPC 배포 (`0.deploy-all-vpcs.sh`)
- **기능**: DMZ VPC, VPC01, VPC02를 병렬로 배포
- **소요 시간**: 약 10-15분
- **특징**: 
  - S3 버킷 자동 생성 및 템플릿 업로드
  - 배포 상태 실시간 모니터링
  - 병렬 배포로 시간 단축

**배포 리소스:**
- **DMZ VPC**: 퍼블릭/프라이빗 서브넷, NAT Gateway, Internet Gateway
- **VPC01/VPC02**: 프라이빗 서브넷, 라우팅 테이블

#### 2. Transit Gateway 구성 (`0.deploy-tgw.sh`)
- **기능**: VPC 간 연결 및 라우팅 설정
- **구성 요소**:
  - Transit Gateway 생성
  - VPC Attachment 구성
  - 라우팅 테이블 설정

### Phase 2: 개발 환경 구성

#### 3. 개발 도구 설치 (`1.vscode-tools-installer.sh`)
**설치되는 도구:**
- **AWS CLI**: 최신 버전 + 자동완성
- **Session Manager Plugin**: EC2 인스턴스 접근
- **kubectl** (v1.31.3): Kubernetes 클러스터 관리
- **eksctl**: EKS 클러스터 생성/관리
- **Helm** (v3.16.4): Kubernetes 패키지 관리
- **k9s** (v0.32.7): Kubernetes 클러스터 모니터링
- **추가 도구**: fzf, jq, gettext, bash-completion

#### 4. AWS 환경 설정 (`2.set-aws-env.sh`)
- AWS CLI 프로파일 구성
- 환경 변수 설정
- 리전 및 계정 정보 확인

#### 5. KMS 설정 (`3.kms-setup.sh`)
- 암호화용 KMS 키 생성
- 키 정책 및 별칭 구성

### Phase 3: Kiro CLI 및 MCP

#### 6. 핵심 런타임 설치 (`4.install_core_mcp.sh`)
**설치 구성요소:**
- **Python 3.12**: 최신 Python 런타임
- **uv**: 고성능 Python 패키지 관리자
- **Node.js**: JavaScript 런타임 (MCP 서버용)

#### 7. MCP 구성 (`5.setup-mcp-config.sh`)
- MCP 서버 구성 파일 생성 (`~/.kiro/settings/mcp.json`)
- Kiro CLI와 MCP 연동 설정
- 필요한 의존성 패키지 설치

## 🔧 선택적 서비스 배포

### Redis 클러스터
```bash
./0.deploy-redis.sh
```
- **위치**: DMZ VPC
- **구성**: ElastiCache Redis 클러스터
- **템플릿**: `redis-cluster-stack.yml`

### Aurora MySQL
```bash
./0.deploy-aurora.sh
```
- **위치**: VPC01
- **구성**: Aurora MySQL 클러스터 (Multi-AZ)
- **템플릿**: `aurora-mysql-stack.yml`

### OpenSearch
```bash
./deploy-opensearch.sh
```
- **위치**: DMZ VPC
- **구성**: OpenSearch 클러스터
- **템플릿**: `opensearch-stack.yml`

### EKS 클러스터
```bash
# EKS 클러스터 생성
./dmz_eks_shell.sh

# eksctl 구성 및 배포
./dmz_eksctl_shell.sh

# 클러스터 구성 확인 (dry-run)
eksctl create cluster --config-file=/home/ec2-user/amazonqcli_lab/LabSetup/eksworkshop.yaml --dry-run

# 실제 클러스터 생성
eksctl create cluster --config-file=/home/ec2-user/amazonqcli_lab/LabSetup/eksworkshop.yaml

# 정리 (필요시)
./dmz_eks_cleanup.sh
```

## 📁 파일 구조

```
LabSetup/
├── 인프라 배포 스크립트
│   ├── 0.deploy-all-vpcs.sh          # VPC 일괄 배포
│   ├── 0.deploy-tgw.sh               # Transit Gateway 배포
│   ├── 0.deploy-redis.sh             # Redis 배포
│   └── 0.deploy-aurora.sh            # Aurora MySQL 배포
├── 환경 설정 스크립트
│   ├── 1.vscode-tools-installer.sh   # 개발 도구 설치
│   ├── 2.set-aws-env.sh              # AWS 환경 설정
│   └── 3.kms-setup.sh                # KMS 키 설정
├── MCP 및 Q CLI 설정
│   ├── 4.install_core_mcp.sh         # 핵심 런타임 설치
│   └── 5.setup-mcp-config.sh         # MCP 구성
├── EKS 관리 스크립트
│   ├── dmz_eks_shell.sh              # EKS 클러스터 생성
│   ├── dmz_eksctl_shell.sh           # eksctl 구성
│   └── dmz_eks_cleanup.sh            # EKS 정리
├── 추가 서비스
│   └── deploy-opensearch.sh          # OpenSearch 배포
└── CloudFormation 템플릿
    ├── 1.DMZVPC.yml                  # DMZ VPC 템플릿
    ├── 2.VPC01.yml                   # VPC01 템플릿
    ├── 3.VPC02.yml                   # VPC02 템플릿
    ├── 4.TGW.yml                     # Transit Gateway 템플릿
    ├── aurora-mysql-stack.yml        # Aurora MySQL 템플릿
    ├── redis-cluster-stack.yml       # Redis 클러스터 템플릿
    └── opensearch-stack.yml          # OpenSearch 템플릿
```

## 🔍 문제 해결

### 일반적인 문제

#### 1. 권한 오류
```bash
# IAM 권한 확인
aws sts get-caller-identity
aws iam get-user

# 필요한 권한이 있는지 확인
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
  --action-names cloudformation:CreateStack \
  --resource-arns "*"
```

#### 2. 스크립트 실행 권한
```bash
chmod +x *.sh
```

#### 3. 리전 설정 확인
```bash
# 현재 리전 확인
aws configure get region

# 환경 변수로 리전 설정
export AWS_DEFAULT_REGION=ap-northeast-2
```

#### 4. 서비스 한도 확인
- VPC 한도: 계정당 5개 (기본값)
- 서브넷 한도: VPC당 200개
- 보안 그룹 한도: VPC당 2500개

### 배포 상태 확인
```bash
# CloudFormation 스택 상태 확인
aws cloudformation describe-stacks \
  --stack-name dmz-vpc-stack \
  --query 'Stacks[0].StackStatus'

# 스택 이벤트 확인
aws cloudformation describe-stack-events \
  --stack-name dmz-vpc-stack \
  --query 'StackEvents[0:5].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId]' \
  --output table
```

### 로그 확인
각 스크립트는 상세한 실행 로그를 제공합니다:
- ✅ 성공 단계
- ❌ 오류 발생 시 상세 정보
- 📊 진행 상황 표시

## 🧹 정리

### 전체 환경 정리 (역순)
```bash
# EKS 클러스터 정리 (배포한 경우)
./dmz_eks_cleanup.sh

# CloudFormation 스택 삭제 (의존성 순서 고려)
aws cloudformation delete-stack --stack-name opensearch-stack
aws cloudformation delete-stack --stack-name aurora-mysql-stack  
aws cloudformation delete-stack --stack-name redis-cluster-stack
aws cloudformation delete-stack --stack-name tgw-stack
aws cloudformation delete-stack --stack-name vpc02-stack
aws cloudformation delete-stack --stack-name vpc01-stack
aws cloudformation delete-stack --stack-name dmz-vpc-stack

# S3 버킷 정리 (필요시)
aws s3 rb s3://$(aws iam list-account-aliases --query 'AccountAliases[0]' --output text)-$(date +%Y%m%d)-cf-template --force
```

### 선택적 정리
```bash
# 특정 스택만 삭제
aws cloudformation delete-stack --stack-name [스택이름]

# 삭제 상태 확인
aws cloudformation describe-stacks --stack-name [스택이름] --query 'Stacks[0].StackStatus'
```

## 📊 실행 순서 요약

1. **인프라 구축** (Phase 1)
   ```bash
   ./0.deploy-all-vpcs.sh    # VPC 배포 (병렬)
   ./0.deploy-tgw.sh         # Transit Gateway
   ```

2. **개발 환경** (Phase 2)
   ```bash
   ./1.vscode-tools-installer.sh  # 개발 도구
   ./2.set-aws-env.sh            # AWS 환경
   ./3.kms-setup.sh              # KMS 설정
   ```

3. **AI 도구** (Phase 3)
   ```bash
   ./4.install_core_mcp.sh       # 런타임 설치
   ./5.setup-mcp-config.sh       # MCP 구성
   ```

4. **선택적 서비스**
   ```bash
   ./0.deploy-redis.sh           # Redis (선택)
   ./0.deploy-aurora.sh          # Aurora (선택)
   ./deploy-opensearch.sh        # OpenSearch (선택)
   
   # EKS 클러스터 (선택)
   ./dmz_eks_shell.sh           # EKS 환경 준비
   ./dmz_eksctl_shell.sh        # eksctl 구성
   eksctl create cluster --config-file=/home/ec2-user/amazonqcli_lab/LabSetup/eksworkshop.yaml --dry-run
   eksctl create cluster --config-file=/home/ec2-user/amazonqcli_lab/LabSetup/eksworkshop.yaml
   ```

## ⚠️ 주의사항

- 이 실습 환경은 학습 및 개발 목적으로 설계되었습니다
- 프로덕션 환경 사용 전 보안 검토 및 비용 최적화 필요
- 리소스 사용 후 반드시 정리하여 불필요한 비용 발생 방지
- 기본 리전은 `ap-northeast-2` (서울)로 설정되어 있습니다

## 💡 팁

- 병렬 배포를 통해 전체 구축 시간을 약 50% 단축
- 각 단계별로 로그를 확인하여 문제 조기 발견
- AWS 서비스 한도를 미리 확인하여 배포 실패 방지
- MCP 설정 후 Kiro CLI 로그인하여 /mcp 명령으로 MCP 서버 로딩 확인 가능

---

**📞 지원**: 문제 발생 시 각 스크립트의 로그를 확인하거나 AWS CloudFormation 콘솔에서 스택 상태를 점검하세요.
