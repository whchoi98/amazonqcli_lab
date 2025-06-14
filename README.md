
# Amazon Q CLI Lab 환경 구축 가이드

이 저장소는 Amazon Q CLI와 MCP(Model Context Protocol) 서버를 활용한 AWS 인프라 실습 환경을 구축하기 위한 스크립트와 CloudFormation 템플릿을 제공합니다.

## 📋 목차

- [아키텍처 개요](#아키텍처-개요)
- [사전 요구사항](#사전-요구사항)
- [빠른 시작](#빠른-시작)
- [상세 배포 가이드](#상세-배포-가이드)
- [선택적 서비스 배포](#선택적-서비스-배포)
- [파일 구조](#파일-구조)
- [문제 해결](#문제-해결)
- [정리](#정리)

## 🏗️ 아키텍처 개요

이 실습 환경은 다음과 같은 AWS 리소스를 구성합니다:

- **네트워킹**: DMZ VPC, VPC01, VPC02와 Transit Gateway를 통한 연결
- **개발 환경**: VSCode 도구, AWS CLI, Amazon Q CLI
- **보안**: KMS 키 관리, IAM 역할 및 정책
- **선택적 서비스**: Redis, Aurora MySQL, OpenSearch, EKS

## 📋 사전 요구사항

- AWS CLI 구성 완료
- 적절한 IAM 권한 (VPC, EC2, RDS, ElastiCache, OpenSearch, EKS 등)
- Linux/macOS 환경 (bash 스크립트 실행)
- Git 설치

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/whchoi98/amazonqcli_lab.git
cd ~/amazonqcli_lab/
```

### 2. 기본 인프라 배포

```bash
# VPC 및 네트워킹 구성
./0.depoly-all-vpcs.sh

# Transit Gateway 배포
./0.deploy-tgw.sh
```

### 3. 개발 환경 설정

```bash
# VSCode 도구 설치
./1.vscode-tools-installer.sh

# AWS 환경 변수 설정
./2.set-aws-env.sh

# KMS 키 구성
./3.kms-setup.sh
```

### 4. Amazon Q CLI 및 MCP 설정

```bash
# 핵심 MCP 서버 설치
./4.install_core_mcp.sh

# MCP 구성 설정
./5.setup-mcp-config.sh
```

## 📖 상세 배포 가이드

### 네트워킹 구성

#### 1. VPC 배포 (`0.depoly-all-vpcs.sh`)
- **DMZ VPC** (`1.DMZVPC.yml`): 퍼블릭 서브넷과 NAT Gateway
- **VPC01** (`2.VPC01.yml`): 프라이빗 서브넷 구성
- **VPC02** (`3.VPC02.yml`): 추가 워크로드용 VPC

#### 2. Transit Gateway 구성 (`0.deploy-tgw.sh`)
- VPC 간 연결을 위한 Transit Gateway 배포 (`4.TGW.yml`)
- 라우팅 테이블 및 연결 설정

### 개발 환경 구성

#### 3. VSCode 도구 설치 (`1.vscode-tools-installer.sh`)
- 필수 개발 도구 및 확장 프로그램 설치
- AWS 관련 도구 구성

#### 4. AWS 환경 설정 (`2.set-aws-env.sh`)
- AWS CLI 프로파일 구성
- 환경 변수 설정

#### 5. KMS 설정 (`3.kms-setup.sh`)
- 암호화를 위한 KMS 키 생성
- 키 정책 구성

### Amazon Q CLI 및 MCP 구성

#### 6. MCP 서버 설치 (`4.install_core_mcp.sh`)
- 핵심 MCP 서버 패키지 설치
- 의존성 관리

#### 7. MCP 구성 (`5.setup-mcp-config.sh`)
- MCP 서버 구성 파일 생성
- Amazon Q CLI와 MCP 연동 설정

## 🔧 선택적 서비스 배포

### Option 1: Redis 클러스터 배포

```bash
./0.deploy-redis.sh
```
- DMZ VPC에 ElastiCache Redis 클러스터 배포
- 템플릿: `redis-cluster-stack.yml`

### Option 2: Aurora MySQL 배포

```bash
./0.deploy-aurora.sh
```
- VPC01에 Aurora MySQL 클러스터 배포
- 템플릿: `aurora-mysql-stack.yml`

### Option 3: OpenSearch 배포

```bash
./deploy-opensearch.sh
```
- DMZ VPC에 OpenSearch 클러스터 배포
- 템플릿: `opensearch-stack.yml`

### Option 4: EKS 클러스터 배포

```bash
# EKS 클러스터 생성
./dmz_eks_shell.sh

# eksctl을 사용한 추가 구성
./dmz_eksctl_shell.sh

# ekscluster 배포
eksctl create cluster --config-file=~/amazonqcli_lab/eksworkshop.yaml --dry-run
eksctl create cluster --config-file=~/amazonqcli_lab/eksworkshop.yaml

# 정리 (필요시)
./dmz_eks_cleanup.sh
```

## 📁 파일 구조

```
amazonqcli_lab/
├── README.md                          # 이 파일
├── 0.depoly-all-vpcs.sh              # VPC 일괄 배포 스크립트
├── 0.deploy-tgw.sh                   # Transit Gateway 배포
├── 0.deploy-redis.sh                 # Redis 배포
├── 0.deploy-aurora.sh                # Aurora MySQL 배포
├── deploy-opensearch.sh              # OpenSearch 배포
├── 1.vscode-tools-installer.sh       # VSCode 도구 설치
├── 2.set-aws-env.sh                  # AWS 환경 설정
├── 3.kms-setup.sh                    # KMS 키 설정
├── 4.install_core_mcp.sh             # MCP 서버 설치
├── 5.setup-mcp-config.sh             # MCP 구성 설정
├── dmz_eks_shell.sh                  # EKS 클러스터 생성
├── dmz_eksctl_shell.sh               # eksctl 구성
├── dmz_eks_cleanup.sh                # EKS 정리
├── 1.DMZVPC.yml                      # DMZ VPC CloudFormation 템플릿
├── 2.VPC01.yml                       # VPC01 CloudFormation 템플릿
├── 3.VPC02.yml                       # VPC02 CloudFormation 템플릿
├── 4.TGW.yml                         # Transit Gateway 템플릿
├── redis-cluster-stack.yml           # Redis 클러스터 템플릿
├── aurora-mysql-stack.yml            # Aurora MySQL 템플릿
└── opensearch-stack.yml              # OpenSearch 템플릿
```

## 🔍 문제 해결

### 일반적인 문제

1. **권한 오류**
   - IAM 사용자/역할에 필요한 권한이 있는지 확인
   - AWS CLI 구성 상태 확인: `aws sts get-caller-identity`

2. **스크립트 실행 권한**
   ```bash
   chmod +x *.sh
   ```

3. **리전 설정**
   - 스크립트에서 사용하는 AWS 리전이 올바른지 확인
   - 환경 변수 `AWS_DEFAULT_REGION` 설정

4. **리소스 한도**
   - VPC, 서브넷, 보안 그룹 등의 AWS 서비스 한도 확인
   - 필요시 AWS Support를 통해 한도 증가 요청

### 로그 확인

각 스크립트는 실행 로그를 출력합니다. 오류 발생 시 로그를 확인하여 문제를 진단하세요.

## 🧹 정리

실습 완료 후 리소스 정리:

```bash
# EKS 클러스터 정리 (배포한 경우)
./dmz_eks_cleanup.sh

# CloudFormation 스택 삭제 (역순으로)
aws cloudformation delete-stack --stack-name opensearch-stack
aws cloudformation delete-stack --stack-name aurora-mysql-stack
aws cloudformation delete-stack --stack-name redis-cluster-stack
aws cloudformation delete-stack --stack-name tgw-stack
aws cloudformation delete-stack --stack-name vpc02-stack
aws cloudformation delete-stack --stack-name vpc01-stack
aws cloudformation delete-stack --stack-name dmz-vpc-stack
```

## 📞 지원

문제가 발생하거나 질문이 있으시면:
- GitHub Issues를 통해 문의
- AWS 문서 참조
- Amazon Q CLI 도움말: `q --help`

---

**주의**: 이 실습 환경은 학습 목적으로 설계되었습니다. 프로덕션 환경에서 사용하기 전에 보안 및 비용 최적화를 검토하세요.

