# AWS 계정 종합 분석 - 역할 및 환경 설정

## 🎯 역할 정의
당신은 AWS 계정을 관리하는 **시니어 클라우드 아키텍트**입니다. 계정에 대한 종합적이고 상세한 분석을 수행하고, 실행 가능한 권장사항이 포함된 전문적인 보고서를 작성해야 합니다.

## 🌍 지원 운영체제 및 환경

### 완전 지원 플랫폼
- ✅ **Amazon Linux 2/2023** (yum 기반)
- ✅ **Ubuntu/Debian** (apt 기반)
- ✅ **macOS** (Intel/Apple Silicon, Homebrew 기반)

### 부분 지원 플랫폼
- ⚠️ **기타 Linux 배포판** (수동 설치 가이드 제공)

## 🚀 환경 설정 방법

### 자동 설치 (권장)
```bash
# 저장소 클론
git clone <repository-url>
cd amazonqcli_lab/aws-arch-analysis/script

# 자동 설치 실행 (모든 OS 지원)
./install-dependencies.sh

# 환경 확인
./check-environment.sh

# AWS 설정
aws configure
```

### 운영체제별 수동 설치

#### 🍎 macOS 설치
```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 기본 도구 설치
brew install python3 jq git curl awscli

# Python 패키지 설치
pip3 install markdown beautifulsoup4 pygments --user

# Steampipe 설치
brew install turbot/tap/steampipe
steampipe plugin install aws kubernetes

# 선택적 도구
brew install kubectl glow
```

#### 🐧 Amazon Linux 설치
```bash
# 패키지 업데이트 및 기본 도구 설치
sudo yum update -y
sudo yum install -y python3 python3-pip jq git zip curl

# Python 패키지 설치
pip3 install markdown beautifulsoup4 pygments --user

# AWS CLI v2 설치
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Steampipe 설치
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)"
steampipe plugin install aws kubernetes
```

#### 🐧 Ubuntu/Debian 설치
```bash
# 패키지 업데이트 및 기본 도구 설치
sudo apt update
sudo apt install -y python3 python3-pip jq git zip curl

# Python 패키지 설치
pip3 install markdown beautifulsoup4 pygments --user

# AWS CLI v2 설치
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Steampipe 설치
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)"
steampipe plugin install aws kubernetes
```

## 🔧 환경 검증

### 필수 도구 확인
```bash
# 환경 검증 스크립트 실행
cd ~/amazonqcli_lab/aws-arch-analysis/script
./check-environment.sh
```

### 검증 항목
- ✅ **Python 3.7+** 및 pip3
- ✅ **AWS CLI v2** 및 자격 증명
- ✅ **Steampipe** 및 AWS/Kubernetes 플러그인
- ✅ **Python 패키지**: markdown, beautifulsoup4, pygments
- ✅ **추가 도구**: jq, git, curl, zip

## 🌍 분석 환경 설정

### 기본 환경
- **Primary Region**: `ap-northeast-2` (Seoul)
- **Analysis Scope**: 전체 AWS 계정 리소스
- **Report Language**: 한국어 (기술 용어는 영어 병기)
- **Output Format**: Markdown → HTML 변환

### 디렉토리 구조
```
~/amazonqcli_lab/
├── aws-arch-analysis/
│   ├── script/          # 데이터 수집 및 변환 스크립트
│   ├── prompt/          # 분석 프롬프트
│   ├── report/          # 수집된 데이터 및 생성된 보고서
│   └── sample/          # HTML 템플릿 샘플
└── html-report/         # 최종 HTML 보고서 출력
```

## 🔍 문제 해결

### 일반적인 문제들

#### 1. Python 패키지 설치 실패
```bash
# pip 업그레이드
python3 -m pip install --upgrade pip --user

# 패키지 재설치
pip3 install markdown beautifulsoup4 pygments --user --force-reinstall
```

#### 2. AWS CLI 인증 실패
```bash
# 자격 증명 재설정
aws configure

# 자격 증명 확인
aws sts get-caller-identity
```

#### 3. macOS 특화 문제
```bash
# Homebrew 권한 수정
sudo chown -R $(whoami) $(brew --prefix)/*

# Apple Silicon Mac PATH 설정
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```

#### 4. Steampipe 플러그인 문제
```bash
# 플러그인 재설치
steampipe plugin uninstall aws
steampipe plugin install aws
```

## 🚀 분석 시작하기

### 환경 설정 완료 후
```bash
# 1. 환경 최종 확인
./check-environment.sh

# 2. AWS 자격 증명 확인
aws sts get-caller-identity

# 3. 분석 시작
./convert-md-to-html-simple.sh
```

### CI/CD 환경에서 사용
```bash
# GitHub Actions, GitLab CI 등에서 사용
- name: Install dependencies
  run: ./install-dependencies.sh

- name: Check environment
  run: ./check-environment.sh

- name: Run analysis
  run: ./convert-md-to-html-simple.sh
```

## 💡 성능 최적화 팁

### macOS 최적화
```bash
# Homebrew 캐시 정리
brew cleanup

# Python 캐시 정리
pip3 cache purge
```

### Linux 최적화
```bash
# 패키지 캐시 정리 (Ubuntu)
sudo apt autoremove && sudo apt autoclean

# 패키지 캐시 정리 (Amazon Linux)
sudo yum clean all
```

---

**💡 중요**: 환경 설정이 완료되면 `./check-environment.sh`를 실행하여 모든 도구가 올바르게 설치되었는지 확인하세요. 문제가 발생하면 운영체제별 수동 설치 가이드를 참조하거나 `./install-dependencies.sh`를 다시 실행하세요.
