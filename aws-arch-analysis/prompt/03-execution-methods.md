# AWS 계정 분석 - 실행 방법 가이드

## 🔧 계정 분석 실행 방법

### 방법 1: 전체 자동화 실행 

**실행 단계**:
1. **데이터 수집**: 모든 Steampipe 수집 스크립트 실행
2. **Markdown 보고서 생성**: 10개 섹션 보고서 자동 생성
3. **HTML 변환**: 웹 기반 보고서 생성

### 방법 2: 단계별 수동 실행

#### Step 1: 데이터 수집 실행
```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script

# 메인 데이터 수집 스크립트 실행
./aws-comprehensive-analysis.sh

# 또는 개별 수집 스크립트 실행
./steampipe_networking_collection.sh      # 네트워킹 데이터
./steampipe_compute_collection.sh         # 컴퓨팅 데이터
./steampipe_container_collection.sh       # 컨테이너 데이터
./steampipe_database_collection.sh        # 데이터베이스 데이터
./steampipe_storage_collection.sh         # 스토리지 데이터
./steampipe_security_collection.sh        # 보안 데이터
./steampipe_application_collection.sh     # 애플리케이션 데이터
./steampipe_monitoring_collection.sh      # 모니터링 데이터
./steampipe_iac_analysis_collection.sh    # IaC 분석 데이터
```

#### Step 2: 보고서 생성 실행
```bash
# 모든 보고서 일괄 생성
./generate-all-reports.sh

# 또는 개별 보고서 생성
./generate-executive-summary.sh           # 경영진 요약
./generate-networking-report.sh           # 네트워킹 분석
./generate-compute-report.py              # 컴퓨팅 분석 (Python)
./generate-storage-report.sh              # 스토리지 분석
./generate-database-report.sh             # 데이터베이스 분석
./generate-security-report.sh             # 보안 분석
./generate-cost-report.py                 # 비용 최적화 (Python)
./generate-application-report.py          # 애플리케이션 분석 (Python)
./generate-monitoring-report.sh           # 모니터링 분석
./generate-recommendations.sh             # 종합 권장사항
```

#### Step 3: HTML 변환 실행
```bash
# HTML 보고서 생성
./generate-html-reports.sh

# 또는 Python 변환기 직접 실행
python3 markdown-to-html-converter.py \
  --input ~/amazonqcli_lab/report/ \
  --output ~/amazonqcli_lab/html-report/ \
  --template ~/amazonqcli_lab/aws-arch-analysis/sample/
```

### 방법 3: 특정 영역만 분석
```bash
# 네트워킹만 분석
./steampipe_networking_collection.sh
./generate-networking-report.sh

# 비용 최적화만 분석
./steampipe_compute_collection.sh
./steampipe_database_collection.sh
./steampipe_storage_collection.sh
./generate-cost-report.py

# 보안만 분석
./steampipe_security_collection.sh
./generate-security-report.sh
```

### 실행 전 사전 준비사항
```bash
# 1. 스크립트 실행 권한 부여
chmod +x ~/amazonqcli_lab/aws-arch-analysis/script/*.sh
chmod +x ~/amazonqcli_lab/aws-arch-analysis/script/*.py

# 2. 필요한 디렉토리 생성
mkdir -p ~/amazonqcli_lab/report
mkdir -p ~/amazonqcli_lab/html-report

# 3. AWS 자격 증명 확인
aws sts get-caller-identity

# 4. Steampipe 설치 및 AWS 플러그인 확인
steampipe plugin list
steampipe query "select account_id from aws_caller_identity"
```

### 실행 결과 확인
```bash
# 수집된 JSON 데이터 확인
ls -la ~/amazonqcli_lab/report/*.json

# 생성된 Markdown 보고서 확인
ls -la ~/amazonqcli_lab/report/*.md

# HTML 보고서 확인
ls -la ~/amazonqcli_lab/html-report/*.html

# 데이터 품질 검증
jq . ~/amazonqcli_lab/report/compute_ec2_instances.json | head -20
```

### 오류 발생 시 대응 방법
```bash
# 로그 파일 확인
tail -f ~/amazonqcli_lab/report/analysis.log

# 개별 스크립트 디버그 실행
bash -x ./steampipe_compute_collection.sh

# 데이터 수집 상태 확인
./aws-comprehensive-analysis.sh --check-only

# 부분 재실행 (특정 서비스만)
./steampipe_compute_collection.sh --service ec2
```
