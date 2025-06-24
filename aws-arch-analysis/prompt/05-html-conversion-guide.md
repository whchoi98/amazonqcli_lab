# AWS 계정 분석 - HTML 변환 가이드

## 🔄 HTML 변환 프로세스

### HTML 변환 스크립트 활용

#### 자동 HTML 변환 실행
```bash
# 메인 HTML 변환 스크립트 실행
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-html-reports.sh
```

**변환 과정**:
1. **Markdown 파일 검증**: 문법 및 구조 확인
2. **템플릿 적용**: `~/amazonqcli_lab/aws-arch-analysis/sample/` 참조
3. **HTML 파일 생성**: `~/amazonqcli_lab/html-report/` 디렉토리에 생성
4. **네비게이션 구성**: 보고서 간 연결 및 목차 생성

#### Python 변환기 직접 활용
```bash
# 고급 변환 옵션 사용
python3 markdown-to-html-converter.py \
  --input ~/amazonqcli_lab/report/ \
  --output ~/amazonqcli_lab/html-report/ \
  --template ~/amazonqcli_lab/aws-arch-analysis/sample/ \
  --style professional \
  --include-toc \
  --responsive
```

**변환기 옵션**:
- `--input`: Markdown 파일 입력 디렉토리
- `--output`: HTML 파일 출력 디렉토리  
- `--template`: HTML 템플릿 디렉토리
- `--style`: 스타일 테마 (professional, modern, classic)
- `--include-toc`: 목차 자동 생성
- `--responsive`: 반응형 디자인 적용

### HTML 템플릿 참조
**템플릿 위치**: `~/amazonqcli_lab/aws-arch-analysis/sample/`

#### 사용 가능한 템플릿
- `index.html` - 메인 대시보드 템플릿
- `report-template.html` - 개별 보고서 템플릿
- `executive-summary.html` - 경영진 요약 템플릿
- `technical-report.html` - 기술 분석 템플릿

#### 템플릿 구성 요소
```html
<!-- 공통 헤더 -->
<header class="report-header">
  <nav class="report-navigation">
    <!-- 보고서 간 네비게이션 -->
  </nav>
</header>

<!-- 메인 콘텐츠 -->
<main class="report-content">
  <!-- Markdown 변환 내용 -->
</main>

<!-- 사이드바 (목차) -->
<aside class="report-sidebar">
  <!-- 자동 생성 목차 -->
</aside>

<!-- 푸터 -->
<footer class="report-footer">
  <!-- 생성 정보 및 링크 -->
</footer>
```

### 변환 결과물 구조
```
~/amazonqcli_lab/html-report/
├── index.html                          # 메인 대시보드
├── 01-executive-summary.html           # 경영진 요약
├── 02-networking-analysis.html         # 네트워킹 분석
├── 03-compute-analysis.html            # 컴퓨팅 분석
├── 04-storage-analysis.html            # 스토리지 분석
├── 05-database-analysis.html           # 데이터베이스 분석
├── 06-security-analysis.html           # 보안 분석
├── 07-cost-optimization.html           # 비용 최적화
├── 08-application-analysis.html        # 애플리케이션 분석
├── 09-monitoring-analysis.html         # 모니터링 분석
├── 10-comprehensive-recommendations.html # 종합 권장사항
├── assets/                             # CSS, JS, 이미지
│   ├── css/
│   │   ├── main.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── navigation.js
│   │   └── charts.js
│   └── images/
└── data/                               # JSON 데이터 (차트용)
    ├── cost-data.json
    ├── resource-counts.json
    └── recommendations.json
```

### HTML 품질 검증 및 최적화

#### Step 1: 자동 검증
```bash
# HTML 문법 검증
html5validator ~/amazonqcli_lab/html-report/*.html

# 링크 검증
linkchecker ~/amazonqcli_lab/html-report/index.html

# 접근성 검증
axe ~/amazonqcli_lab/html-report/index.html
```

#### Step 2: 성능 최적화
```bash
# CSS/JS 압축
./optimize-html-assets.sh

# 이미지 최적화
./optimize-images.sh

# 캐시 설정 확인
./check-cache-headers.sh
```

#### Step 3: 브라우저 호환성 테스트
- **Chrome/Edge**: 최신 버전 지원
- **Firefox**: 최신 버전 지원  
- **Safari**: 최신 버전 지원
- **모바일**: 반응형 디자인 확인

### 고급 HTML 기능

#### 대화형 차트 및 그래프
```javascript
// 비용 트렌드 차트
const costChart = new Chart(ctx, {
    type: 'line',
    data: costData,
    options: chartOptions
});

// 리소스 분포 파이 차트
const resourceChart = new Chart(ctx, {
    type: 'doughnut',
    data: resourceData,
    options: pieOptions
});
```

#### 검색 및 필터링 기능
```javascript
// 보고서 내 검색
function searchReports(query) {
    // 전체 보고서에서 키워드 검색
}

// 권장사항 필터링
function filterRecommendations(priority, category) {
    // 우선순위 및 카테고리별 필터링
}
```

#### 인쇄 최적화
```css
@media print {
    .report-navigation { display: none; }
    .report-content { margin: 0; }
    .page-break { page-break-before: always; }
}
```

### 배포 및 공유

#### 로컬 웹 서버 실행
```bash
# Python 웹 서버
cd ~/amazonqcli_lab/html-report
python3 -m http.server 8080

# 브라우저에서 확인
# http://localhost:8080
```

#### 정적 웹사이트 배포 (선택사항)
```bash
# S3 정적 웹사이트 배포
aws s3 sync ~/amazonqcli_lab/html-report/ s3://your-report-bucket/ --delete
aws s3 website s3://your-report-bucket --index-document index.html

# CloudFront 배포 (선택사항)
aws cloudfront create-distribution --distribution-config file://distribution-config.json
```

### 변환 프로세스 자동화
```bash
# 전체 프로세스 자동화 스크립트
#!/bin/bash
# auto-generate-reports.sh

# 1. 데이터 수집
./aws-comprehensive-analysis.sh

# 2. Markdown 보고서 생성  
./generate-all-reports.sh

# 3. HTML 변환
./generate-html-reports.sh

# 4. 품질 검증
./validate-html-reports.sh

# 5. 배포 (선택사항)
# ./deploy-reports.sh

echo "✅ 전체 보고서 생성 프로세스 완료"
echo "🌐 HTML 보고서: file://$(pwd)/html-report/index.html"
```
