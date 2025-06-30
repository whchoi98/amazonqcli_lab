# AWS Architecture Analysis - AWS 계정 종합 분석 도구

AWS 계정의 전체 리소스를 분석하고 전문적인 보고서를 생성하는 종합 분석 도구입니다.

## 📋 목차

- [개요](#개요)
- [사전 요구사항](#사전-요구사항)
- [빠른 시작](#빠른-시작)
- [단계별 실행 가이드](#단계별-실행-가이드)
- [디렉토리 구조](#디렉토리-구조)
- [생성되는 보고서](#생성되는-보고서)
- [문제 해결](#문제-해결)

## 🚀 개요

이 도구는 AWS 계정의 모든 리소스를 체계적으로 분석하여 다음과 같은 전문적인 보고서를 생성합니다:

### 주요 특징
- **종합적 분석**: 9개 영역(네트워킹, 컴퓨팅, 스토리지, 데이터베이스 등)의 완전한 분석
- **데이터 기반 권장사항**: 실제 리소스 데이터에서 도출된 정량적 개선안
- **전문적 보고서**: Markdown → HTML 변환으로 시각적으로 우수한 보고서
- **자동화된 프로세스**: 01~04 단계의 순차적 실행으로 완전 자동화

### 분석 영역
- 🌐 **네트워킹**: VPC, 서브넷, 보안그룹, 라우팅 등
- 💻 **컴퓨팅**: EC2, EKS, Auto Scaling, Load Balancer 등
- 📦 **컨테이너**: ECS, EKS, ECR, Kubernetes 리소스 등
- 💾 **스토리지**: EBS, S3, EFS, FSx, Backup 등
- 🗄️ **데이터베이스**: RDS, Aurora, ElastiCache, DynamoDB 등
- 🔒 **보안**: IAM, KMS, Secrets Manager, WAF 등
- 📊 **모니터링**: CloudWatch, CloudTrail, Config 등
- 🏗️ **애플리케이션**: Lambda, API Gateway, SQS, SNS 등
- 💰 **비용**: Cost Explorer, Billing, 리소스 최적화 등

## 📋 사전 요구사항

### AWS 환경
- **AWS CLI 구성 완료**
- **적절한 IAM 권한** (ReadOnly 권한 최소 필요)
- **Amazon Q CLI Profile 설정 권장** (보안 및 관리 편의성)

### 시스템 요구사항
- **Python 3.8+**
- **Steampipe** (AWS 리소스 쿼리용)
- **필수 Python 패키지**: boto3, pandas, jinja2

### Amazon Q CLI Profile 설정 (강력 권장)

보안과 관리 편의성을 위해 Amazon Q CLI Profile을 생성하여 사용하는 것을 강력히 권장합니다:

```bash
# Amazon Q CLI 프로파일 생성
q configure --profile aws-analysis
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: ap-northeast-2
# Default output format: json

# 프로파일 확인
q --profile aws-analysis aws sts get-caller-identity

# 기본 프로파일로 설정
q configure set-default-profile aws-analysis
```

**Amazon Q CLI Profile 사용의 장점:**
- 기본 AWS 자격 증명과 분리하여 안전한 분석 환경 구성
- 여러 계정 분석 시 프로파일 전환으로 간편한 관리
- 실수로 인한 다른 계정 접근 방지
- Amazon Q의 AI 기능과 AWS 리소스 접근을 통합 관리

## 🚀 빠른 시작 (Amazon Q CLI 자연어 실행)

### 1. 환경 준비
```
aws-arch-analysis 디렉토리로 이동해서 Amazon Q CLI Profile을 설정해줘.
분석용 프로파일을 'aws-analysis'로 생성하고 ap-northeast-2 리전으로 설정해줘.
```

### 2. Amazon Q CLI Profile 설정 (권장)
```
Amazon Q CLI 분석을 위한 전용 프로파일을 생성해줘.
q configure --profile aws-analysis 명령어로 새 프로파일을 만들고,
q configure set-default-profile aws-analysis로 기본 프로파일을 설정한 다음
q --profile aws-analysis aws sts get-caller-identity로 프로파일이 제대로 동작하는지 확인해줘.
```

### 3. 01~04 단계 순차 실행 (자연어 프롬프트)

**01단계 프롬프트:**
```
01-role-and-environment.md를 실행해줘.
```

**02단계 프롬프트:**
```
02-data-collection-guide.md를 실행해줘.
```

**03단계 프롬프트:**
```
03-report-generation-guide.md를 실행해줘.
```

**04단계 프롬프트:**
```
04-html-conversion-guide.md를 실행해줘.
```

## 📖 단계별 실행 가이드 (Amazon Q CLI 자연어 실행)

### 01단계: 역할 및 환경 설정

**목적**: 분석 환경과 역할 정의 확인

**Amazon Q CLI에서 실행할 프롬프트:**
```
01-role-and-environment.md를 실행해줘.
```

**주요 내용:**
- 시니어 클라우드 아키텍트 역할 정의
- Primary Region: `ap-northeast-2` (Seoul)
- 분석 범위: 전체 AWS 계정 리소스
- 출력 형식: 한국어 (기술 용어 영어 병기)

### 02단계: 데이터 수집

**목적**: AWS 계정의 모든 리소스 데이터 수집

**Amazon Q CLI에서 실행할 프롬프트:**
```
02-data-collection-guide.md 파일을 참고해서 AWS 계정의 모든 리소스 데이터를 수집해줘.
```

**수집되는 데이터:**
- 9개 영역의 AWS 리소스 정보
- 실시간 진행 상황 표시
- 성공/실패 통계 및 상세 결과
- 타임아웃 처리 (스크립트당 5분)

**예상 소요 시간**: 10-20분 (계정 규모에 따라 변동)

### 03단계: 보고서 생성

**목적**: 수집된 데이터를 기반으로 전문적인 분석 보고서 생성

**Amazon Q CLI에서 실행할 프롬프트:**
```
03-report-generation-guide.md 파일을 기반으로 수집된 AWS 데이터를 분석해서 Enhanced 보고서를 생성해줘.
경영진 요약부터 종합 권장사항까지 10개의 전문적인 분석 보고서를 만들어줘.
각 보고서는 데이터 기반의 정량적 권장사항을 포함하고, 우선순위별로 분류해서 실행 가능한 개선안을 제시해줘.
```

**생성되는 보고서:**
1. **01-executive-summary.md** - 경영진 요약 보고서
2. **02-networking-analysis.md** - 네트워킹 분석
3. **03-compute-analysis.md** - 컴퓨팅 분석
4. **04-storage-analysis.md** - 스토리지 분석
5. **05-database-analysis.md** - 데이터베이스 분석
6. **06-security-analysis.md** - 보안 분석
7. **07-monitoring-analysis.md** - 모니터링 분석
8. **08-application-analysis.md** - 애플리케이션 분석
9. **09-cost-analysis.md** - 비용 분석
10. **10-recommendations.md** - 종합 권장사항

**Enhanced 권장사항 특징:**
- 🔴 **높은 우선순위**: 보안 위험, 높은 비용 영향 (즉시 실행)
- 🟡 **중간 우선순위**: 성능 개선, 중간 비용 영향 (1-3개월)
- 🟢 **낮은 우선순위**: 운영 효율성, 장기적 개선 (3-6개월)

### 04단계: HTML 변환

**목적**: Markdown 보고서를 전문적인 HTML 형식으로 변환

**Amazon Q CLI에서 실행할 프롬프트:**
```
04-html-conversion-guide.md 파일을 참고해서 생성된 10개의 Markdown 보고서를 전문적인 HTML 형식으로 변환해줘.
script/convert-md-to-html-simple.sh 스크립트를 실행해서 시각적으로 우수한 HTML 보고서를 만들고,
필요하면 script/generate-html-reports.sh로 index.html과 assets 폴더까지 포함한 완전한 웹 보고서를 생성해줘.
그라데이션 헤더, 호버 효과, 권장사항 박스 등 전문적인 스타일링을 적용해줘.
```

**변환 결과:**
- **10개 HTML 보고서** (Markdown → HTML)
- **index.html** (메인 대시보드)
- **assets 폴더** (CSS, JS 스타일링)
- **전문적 스타일링** (그라데이션, 호버 효과, 권장사항 박스)


## 📁 디렉토리 구조

```
aws-arch-analysis/
├── prompt/                           # 분석 프롬프트 및 가이드
│   ├── 01-role-and-environment.md    # 01단계: 역할 및 환경 설정
│   ├── 02-data-collection-guide.md   # 02단계: 데이터 수집 가이드
│   ├── 03-report-generation-guide.md # 03단계: 보고서 생성 가이드
│   ├── 04-html-conversion-guide.md   # 04단계: HTML 변환 가이드
│   └── [기타 프롬프트 파일들]
├── script/                           # 실행 스크립트
│   ├── collect_all_data.py          # 종합 데이터 수집
│   ├── generate_all_reports.py      # 전체 보고서 생성
│   ├── convert-md-to-html-simple.sh # 간단 HTML 변환
│   ├── generate-html-reports.sh     # 고급 HTML 변환
│   ├── validate-html-conversion.sh  # 변환 검증
│   └── [개별 수집/생성 스크립트들]
├── sample/                          # 샘플 파일
└── report/                          # 생성된 보고서 (자동 생성)
    ├── data/                        # 수집된 원본 데이터
    ├── markdown/                    # Markdown 보고서
    └── html/                        # HTML 보고서
```

## 📊 생성되는 보고서

### Markdown 보고서 (10개)
1. **01-executive-summary.md** - 경영진 요약
2. **02-networking-analysis.md** - 네트워킹 분석
3. **03-compute-analysis.md** - 컴퓨팅 분석
4. **04-storage-analysis.md** - 스토리지 분석
5. **05-database-analysis.md** - 데이터베이스 분석
6. **06-security-analysis.md** - 보안 분석
7. **07-monitoring-analysis.md** - 모니터링 분석
8. **08-application-analysis.md** - 애플리케이션 분석
9. **09-cost-analysis.md** - 비용 분석
10. **10-recommendations.md** - 종합 권장사항

### HTML 보고서 (11개)
- **index.html** - 메인 대시보드
- **10개 HTML 보고서** (Markdown에서 변환)
- **assets/** - CSS/JS 스타일링 파일

### 보고서 특징
- **데이터 기반 분석**: 실제 AWS 리소스 데이터 활용
- **정량적 권장사항**: 구체적인 비용 절감액, 영향 리소스 수
- **우선순위 분류**: 3단계 우선순위 (높음/중간/낮음)
- **실행 가능성**: 구현 난이도와 예상 효과 명시
- **전문적 스타일링**: 시각적으로 우수한 HTML 보고서

## 🔍 문제 해결

### 일반적인 문제

#### 1. AWS 권한 오류
```bash
# 현재 자격 증명 확인
aws sts get-caller-identity

# 필요한 권한 확인 (ReadOnly 최소 필요)
aws iam get-user
aws iam list-attached-user-policies --user-name [username]
```

#### 2. Steampipe 연결 오류
```bash
# Steampipe 상태 확인
steampipe service status

# AWS 플러그인 확인
steampipe plugin list

# 연결 테스트
steampipe query "select account_id from aws_caller_identity"
```

#### 3. Python 의존성 오류
```bash
# 필수 패키지 설치
pip3 install boto3 pandas jinja2 markdown

# 가상환경 사용 (권장)
python3 -m venv aws-analysis-env
source aws-analysis-env/bin/activate
pip install -r requirements.txt
```

#### 4. Amazon Q CLI Profile 관련 오류
```bash
# Amazon Q CLI 프로파일 목록 확인
q configure list-profiles

# 특정 프로파일로 실행
q --profile aws-analysis chat "script/collect_all_data.py를 실행해줘"

# 기본 프로파일 확인
q configure get-default-profile
```

### 데이터 수집 문제

#### 타임아웃 오류
- 각 스크립트는 5분 타임아웃 설정
- 대용량 계정의 경우 개별 스크립트 실행 고려

#### 부분 실패
- `collect_all_data.py`는 부분 실패 시에도 계속 진행
- 실패한 영역은 개별 스크립트로 재실행 가능

### HTML 변환 문제

#### 변환 실패
```bash
# 변환 상태 확인
./validate-html-conversion.sh

# 문제 해결 스크립트 실행
./troubleshoot-html-conversion.sh

# 간단 변환으로 대체
./convert-md-to-html-simple.sh
```

#### 스타일링 문제
```bash
# assets 폴더 재생성
./generate-html-reports.sh

# CSS/JS 파일 확인
ls -la report/html/assets/
```

## 💡 사용 팁 (Amazon Q CLI 활용)

### 효율적인 분석을 위한 자연어 프롬프트

**1. Amazon Q CLI Profile 설정 프롬프트:**
```
Amazon Q CLI 분석을 위한 전용 프로파일을 생성하고 설정해줘. 
보안과 관리 편의성을 위해 'aws-analysis' 프로파일을 만들어서 사용하고 싶어.
```

**2. 단계별 실행 프롬프트:**
```
AWS 계정 분석을 01~04 단계로 순차적으로 실행해줘.
각 단계의 프롬프트 파일을 읽어서 체계적으로 분석을 진행하고 싶어.
```

**3. 정기적 분석 프롬프트:**
```
월 1회 정기 AWS 계정 분석을 자동화하고 싶어.
이전 분석 결과와 비교해서 변화된 부분을 중심으로 보고서를 만들어줘.
```

**4. 권한 최소화 확인 프롬프트:**
```
AWS 분석에 필요한 최소 권한을 확인해줘.
ReadOnly 권한으로 안전한 분석 환경을 구성하고 싶어.
```

### 대용량 계정 분석 프롬프트

**병렬 처리 프롬프트:**
```
대용량 AWS 계정이라서 분석 시간이 오래 걸려.
개별 영역별 스크립트를 병렬로 실행해서 시간을 단축하고 싶어.
```

**선택적 분석 프롬프트:**
```
전체 분석 대신 특정 영역(네트워킹, 보안, 비용)만 분석하고 싶어.
해당 영역의 스크립트만 실행해서 빠르게 결과를 확인하고 싶어.
```

**리전 제한 프롬프트:**
```
글로벌 계정이지만 주요 리전(ap-northeast-2, us-east-1)만 분석하고 싶어.
특정 리전으로 제한해서 효율적으로 분석을 진행해줘.
```

### 보고서 활용 프롬프트

**경영진 보고 프롬프트:**
```
01-executive-summary.html 보고서를 경영진에게 보고하려고 해.
핵심 내용을 요약해서 프레젠테이션용 자료로 만들어줘.
```

**기술팀 검토 프롬프트:**
```
개별 영역 보고서를 기술팀과 검토하려고 해.
각 보고서의 주요 발견사항과 권장사항을 정리해줘.
```

**액션 플랜 프롬프트:**
```
10-recommendations.html의 권장사항을 우선순위별로 실행 계획을 세우고 싶어.
높은 우선순위부터 단계적으로 실행할 수 있는 액션 플랜을 만들어줘.
```

## 📞 지원

- **스크립트 오류**: 각 스크립트의 로그 파일 확인
- **AWS 권한**: IAM 정책 및 권한 검토
- **Steampipe 문제**: Steampipe 공식 문서 참조
- **HTML 변환**: 변환 검증 스크립트 활용

---

**⚠️ 주의사항**: 
- 이 도구는 ReadOnly 권한으로 동작하며 AWS 리소스를 변경하지 않습니다
- 생성된 보고서에는 민감한 정보가 포함될 수 있으므로 적절한 보안 조치 필요
- 대용량 계정의 경우 데이터 수집에 상당한 시간이 소요될 수 있습니다

**💡 권장사항**:
- Amazon Q CLI Profile을 사용하여 안전하고 체계적인 분석 환경 구성
- 01~04 단계를 순차적으로 실행하여 완전한 분석 수행
- 정기적인 분석을 통해 AWS 계정의 지속적인 최적화 달성
