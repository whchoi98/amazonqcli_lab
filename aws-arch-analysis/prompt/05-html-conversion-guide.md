# AWS 계정 분석 - HTML 변환 가이드

## 🎯 핵심 목표

**반드시 달성해야 할 목표:**
- ✅ **10개 Markdown 파일**을 **10개 HTML 파일**로 완전 변환
- ✅ **index.html + 10개 보고서 = 총 11개 HTML 파일** 생성
- ✅ **assets 폴더** (CSS, JS) 완전 구성

## 🚀 실행 방법

### Step 1: 완전 자동 HTML 변환 (권장)
```bash
# 메인 HTML 변환 스크립트 실행 - 모든 것을 자동으로 처리
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-html-reports.sh
```

### Step 2: 변환 결과 검증
```bash
# 자동 검증 스크립트 실행
./validate-html-conversion.sh
```

### Step 3: 문제 해결 (필요시)
```bash
# 문제 진단 및 해결
./troubleshoot-html-conversion.sh
```

## 📋 필수 생성 파일 목록

### Markdown 파일 (입력) - 10개
```
01-executive-summary.md      → 01-executive-summary.html
02-networking-analysis.md    → 02-networking-analysis.html
03-compute-analysis.md       → 03-compute-analysis.html
04-database-analysis.md      → 04-database-analysis.html
05-storage-analysis.md       → 05-storage-analysis.html
06-security-analysis.md      → 06-security-analysis.html
07-application-analysis.md   → 07-application-analysis.html
08-monitoring-analysis.md    → 08-monitoring-analysis.html
09-cost-optimization.md      → 09-cost-optimization.html
10-recommendations.md        → 10-recommendations.html
```

### HTML 파일 (출력) - 11개
```
index.html                   # 메인 대시보드
01-executive-summary.html    # 경영진 요약
02-networking-analysis.html  # 네트워킹 분석
03-compute-analysis.html     # 컴퓨팅 분석
04-database-analysis.html    # 데이터베이스 분석
05-storage-analysis.html     # 스토리지 분석
06-security-analysis.html    # 보안 분석
07-application-analysis.html # 애플리케이션 분석
08-monitoring-analysis.html  # 모니터링 분석
09-cost-optimization.html    # 비용 최적화
10-recommendations.html      # 종합 권장사항
```

## 🔍 성공 기준

### ✅ 최종 확인 사항
- [ ] HTML 파일 개수: **정확히 11개**
- [ ] 각 파일 크기: **3KB 이상**
- [ ] 네비게이션 링크: **모든 파일에 포함**
- [ ] Assets 폴더: **CSS, JS 파일 완전 구성**

### 🌐 최종 테스트
```bash
# 웹 서버 실행하여 실제 확인
cd ~/amazonqcli_lab/html-report
python3 -m http.server 8080

# 브라우저에서 http://localhost:8080 접속
# - 메인 대시보드 로딩 확인
# - 각 보고서 링크 클릭 테스트
# - 네비게이션 메뉴 작동 확인
```

## 🆘 문제 발생 시

### 빠른 해결 방법
```bash
# 1. 전체 재실행
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-html-reports.sh

# 2. 검증 실행
./validate-html-conversion.sh

# 3. 문제 진단
./troubleshoot-html-conversion.sh
```

---

## 📚 상세 스크립트 참조

모든 상세한 검증 로직과 문제 해결 방법은 다음 스크립트들에서 처리됩니다:

- **`validate-html-conversion.sh`**: 변환 결과 자동 검증
- **`troubleshoot-html-conversion.sh`**: 문제 진단 및 해결
- **`convert-md-to-html.sh`**: Markdown → HTML 변환 엔진

---

**💡 핵심**: 이 가이드의 목표는 **10개 Markdown → 11개 HTML (index.html 포함)** 완전 변환입니다!
