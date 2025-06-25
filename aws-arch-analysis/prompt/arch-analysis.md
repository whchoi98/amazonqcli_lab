# AWS 계정 종합 분석 보고서 - 메인 가이드

## 📋 개요
이 가이드는 AWS 계정에 대한 종합적인 분석을 수행하고 전문적인 보고서를 생성하기 위한 단계별 프롬프트입니다.
리전은 ap-northeast-2를 대상으로 합니다.

## 역할
당신의 역할은 AWS 계정 전체를 분석하고 관리하는 아키텍트,DevOps,FinOps 역할입니다.

## 🗂️ 프롬프트 구조

### 단계별 가이드 파일
단계별 가이드를 수행합니다.
1. **[01-role-and-environment.md](~/amazonqcli_lab/aws-arch-analysis/prompt/01-role-and-environment.md)** - 역할 정의 및 환경 설정
2. **[02-data-collection-guide.md](~/amazonqcli_lab/aws-arch-analysis/prompt//02-data-collection-guide.md)** - 데이터 수집 전략
3. **[03-execution-methods.md](~/amazonqcli_lab/aws-arch-analysis/prompt//03-execution-methods.md)** - 실행 방법론
4. **[04-report-generation-guide.md](~/amazonqcli_lab/aws-arch-analysis/prompt//04-report-generation-guide.md)** - 보고서 생성 가이드
5. **[05-html-conversion-guide.md](~/amazonqcli_lab/aws-arch-analysis/prompt//05-html-conversion-guide.md)** - HTML 변환 및 배포

### 데이터 수집 실행
데이터 수집은 아래에서 처럼 9개의 shell을 모두 수행하고, steampipe 기반의 SQL로 데이터를 수집하고, JSON으로 결과를 저장합니다.
```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script

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

### 리포트 생성
리포트는 아래에서 처럼 markdown을 생성합니다.
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

## 📊 생성되는 보고서
- **01-executive-summary.md** - 경영진 요약
- **02-networking-analysis.md** - 네트워킹 분석
- **03-compute-analysis.md** - 컴퓨팅 분석
- **04-storage-analysis.md** - 스토리지 분석
- **05-database-analysis.md** - 데이터베이스 분석
- **06-security-analysis.md** - 보안 분석
- **07-cost-optimization.md** - 비용 최적화
- **08-application-analysis.md** - 애플리케이션 분석
- **09-monitoring-analysis.md** - 모니터링 분석
- **10-comprehensive-recommendations.md** - 종합 권장사항

#### HTML 변환 실행
```bash
# HTML 보고서 생성
./generate-html-reports.sh

# 또는 Python 변환기 직접 실행
python3 markdown-to-html-converter.py \
  --input ~/amazonqcli_lab/report/ \
  --output ~/amazonqcli_lab/html-report/ \
  --template ~/amazonqcli_lab/aws-arch-analysis/sample/



## 🎯 사용 방법
1. 각 프롬프트 파일을 순서대로 읽고 따라하세요
2. 체크리스트를 활용하여 진행 상황을 확인하세요
3. 필요에 따라 특정 섹션만 선택적으로 실행하세요

---
**📌 참고**: 상세한 내용은 각 개별 프롬프트 파일을 참조하세요.
