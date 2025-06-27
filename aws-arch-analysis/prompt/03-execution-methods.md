# AWS 계정 분석 - 실행 방법 가이드

## 🔧 계정 분석 실행 방법

### 방법 1: 🚀 종합 자동화 실행 (권장)

**한 번의 명령으로 모든 데이터 수집**:

```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script

# 방법 1-A: 빠른 실행 (환경 확인 포함)
./quick_collect.sh

# 방법 1-B: Python 스크립트 직접 실행
python3 collect_all_data.py
```

**실행 결과**:
- 9개 영역의 AWS 리소스 데이터 자동 수집
- 실시간 진행 상황 표시
- 성공/실패 통계 제공
- 총 114개 JSON 파일 생성 (약 1.5MB)
- 데이터 저장 위치: `~/amazonqcli_lab/aws-arch-analysis/report/`

### 방법 2: 단계별 수동 실행

#### Step 1: 개별 데이터 수집 실행
특정 영역만 수집하려는 경우:

```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script

# 개별 수집 스크립트 실행
python3 steampipe_networking_collection.py      # 네트워킹 데이터
python3 steampipe_compute_collection.py         # 컴퓨팅 데이터
python3 steampipe_container_collection.py       # 컨테이너 데이터
python3 steampipe_database_collection.py        # 데이터베이스 데이터
python3 steampipe_storage_collection.py         # 스토리지 데이터
python3 steampipe_security_collection.py        # 보안 데이터
python3 steampipe_application_collection.py     # 애플리케이션 데이터
python3 steampipe_monitoring_collection.py      # 모니터링 데이터
python3 steampipe_iac_analysis_collection.py    # IaC 분석 데이터
```

#### Step 2: 보고서 생성 실행
수집된 데이터를 바탕으로 분석 보고서 생성:

```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script

# 개별 보고서 생성 스크립트 (사용 가능한 경우)
python3 generate_executive_summary.py           # 경영진 요약
python3 generate-networking-report.py           # 네트워킹 분석
python3 generate-compute-report.py              # 컴퓨팅/컨테이너 분석 
python3 generate_storage_report.py              # 스토리지 분석
python3 generate_database_report.py             # 데이터베이스 분석
python3 generate_security_report.py             # 보안 분석
python3 generate-cost-report.py                 # 비용 최적화 
python3 generate-application-report.py          # 애플리케이션 분석
python3 generate_monitoring_report.py           # 모니터링 분석
python3 generate_recommendations.py             # 종합 권장사항
```

#### Step 3: HTML 변환 실행
Markdown 보고서를 웹 형태로 변환:

```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script

# HTML 변환 실행
./generate-html-reports.sh

# 또는 Python 변환기 직접 실행
python3 markdown-to-html-converter.py \
  --input ~/amazonqcli_lab/aws-arch-analysis/report/ \
  --output ~/amazonqcli_lab/html-report/
```


## 🔧 실행 전 사전 준비사항

### 환경 확인
```bash
# 1. AWS 자격 증명 확인
aws sts get-caller-identity

# 2. Steampipe 설치 및 AWS 플러그인 확인
steampipe plugin list
steampipe query "select account_id from aws_caller_identity"

# 3. Python 환경 확인
python3 --version
which python3
```

### 디렉토리 및 권한 설정
```bash
# 1. 필요한 디렉토리 생성
mkdir -p ~/amazonqcli_lab/aws-arch-analysis/report
mkdir -p ~/amazonqcli_lab/html-report

# 2. 스크립트 실행 권한 부여
chmod +x ~/amazonqcli_lab/aws-arch-analysis/script/*.sh
chmod +x ~/amazonqcli_lab/aws-arch-analysis/script/*.py
```

## 📊 실행 결과 확인

### 데이터 수집 결과 확인
```bash
# 수집된 JSON 데이터 확인
ls -la ~/amazonqcli_lab/aws-arch-analysis/report/*.json | wc -l
du -sh ~/amazonqcli_lab/aws-arch-analysis/report/

# 영역별 데이터 파일 확인
ls ~/amazonqcli_lab/aws-arch-analysis/report/networking_*.json
ls ~/amazonqcli_lab/aws-arch-analysis/report/compute_*.json
ls ~/amazonqcli_lab/aws-arch-analysis/report/database_*.json
ls ~/amazonqcli_lab/aws-arch-analysis/report/security_*.json
```

### 보고서 생성 결과 확인
```bash
# 생성된 Markdown 보고서 확인
ls -la ~/amazonqcli_lab/aws-arch-analysis/report/*.md

# HTML 보고서 확인
ls -la ~/amazonqcli_lab/html-report/*.html
```

### 로그 파일 확인
```bash
# 수집 로그 확인
ls ~/amazonqcli_lab/aws-arch-analysis/report/*.log

# 최근 로그 내용 확인
tail -20 ~/amazonqcli_lab/aws-arch-analysis/report/*_collection_errors.log
```

## ⚠️ 문제 해결 가이드

### 일반적인 오류 및 해결 방법

#### 1. 권한 오류
```bash
# IAM 권한 확인
aws iam get-user
aws sts get-caller-identity

# SCP 정책으로 인한 제한 확인
# 일부 서비스 접근이 제한될 수 있음 (S3, Lambda 등)
```

#### 2. Steampipe 연결 오류
```bash
# Steampipe 서비스 재시작
steampipe service restart

# AWS 플러그인 재설치
steampipe plugin install aws
```

#### 3. Python 스크립트 오류
```bash
# Python 경로 확인
which python3

# 필요한 패키지 설치
pip3 install --user pathlib subprocess json
```

#### 4. 데이터 수집 실패 시
```bash
# 개별 스크립트로 문제 영역 확인
cd ~/amazonqcli_lab/aws-arch-analysis/script
python3 steampipe_networking_collection.py  # 네트워킹만 테스트

# 로그 파일에서 상세 오류 확인
cat ~/amazonqcli_lab/aws-arch-analysis/report/*_errors.log
```

## 🎯 성공적인 실행을 위한 팁

1. **환경 확인**: 실행 전 반드시 AWS 자격 증명과 Steampipe 상태 확인
2. **단계별 실행**: 문제 발생 시 개별 스크립트로 문제 영역 파악
3. **로그 모니터링**: 실행 중 로그 파일을 통해 진행 상황 확인
4. **권한 제한 인지**: SCP로 인한 일부 서비스 접근 제한 상황 이해
5. **데이터 검증**: 수집 완료 후 JSON 파일 크기와 내용 확인

## 📈 예상 실행 시간

| 영역 | 예상 시간 | 주요 리소스 |
|------|-----------|-------------|
| 네트워킹 | 1-2초 | VPC, 서브넷, 보안그룹 |
| 컴퓨팅 | 1-2초 | EC2, EKS, ALB |
| 컨테이너 | 1-2초 | EKS, Kubernetes |
| 스토리지 | 2-3초 | EBS, S3 (제한적) |
| 데이터베이스 | 1-2초 | RDS, ElastiCache |
| 보안 | 3-4초 | IAM, KMS |
| 애플리케이션 | 1초 | API Gateway, EventBridge |
| 모니터링 | 1-2초 | CloudWatch |
| IaC 분석 | 15-20초 | CloudFormation, 태그 |

**전체 예상 시간**: 약 30-60초
