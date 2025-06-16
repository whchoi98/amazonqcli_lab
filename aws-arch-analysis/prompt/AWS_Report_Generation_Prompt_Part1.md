# AWS 계정 종합 분석 보고서 생성 프롬프트 - Part 1: 메인 구조

## 🎯 프로젝트 개요

**목표**: AWS 계정의 전체 인프라를 분석하여 구조화된 HTML 보고서를 생성
**도구**: Steampipe + AWS CLI + HTML/CSS + Glow (마크다운 뷰어)
**결과물**: 10개의 상세 HTML 페이지 + 통합 스타일시트

## 📊 분석 대상 정보

- **AWS 계정**: 157148350697
- **분석 리전**: ap-northeast-2 (서울)
- **분석 일시**: 2025년 6월 15일
- **분석 도구**: Steampipe SQL 기반 분석 + AWS CLI
- **총 리소스**: 18개 EC2 인스턴스, 5개 VPC, 1개 EKS 클러스터

## 🏗️ HTML 보고서 구조

### 📁 디렉토리 구조
```
/home/ec2-user/amazonqcli_lab/report/
├── index.html (10KB) - 메인 네비게이션 페이지
├── networking.html (19KB) - Phase 1: 네트워킹 분석
├── computing.html (19KB) - Phase 2: 컴퓨팅 분석
├── storage.html (14KB) - Phase 3: 스토리지 분석
├── database.html (19KB) - Phase 4: 데이터베이스 분석
├── security.html (22KB) - Phase 5: 보안 분석
├── cost-optimization.html (22KB) - Phase 6: 비용 최적화
├── monitoring.html (23KB) - Phase 7: 모니터링 분석
├── recommendations.html (22KB) - Phase 8: 권장사항
├── implementation.html (6KB) - Phase 9: 구현 가이드
└── styles/
    └── main.css (4KB) - 통합 스타일시트
```

## 🎨 HTML 디자인 스타일 가이드

### 기본 HTML 구조
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Phase X: 제목]</title>
    <link rel="stylesheet" href="styles/main.css">
    <style>
        /* 페이지별 커스텀 스타일 */
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="index.html">🏠 홈</a> > <strong>[현재 페이지]</strong>
        </div>
        
        <div class="detail-page">
            <header>
                <h1>[아이콘] [제목]</h1>
                <p>[설명]</p>
            </header>
            
            <!-- 콘텐츠 섹션들 -->
            
            <div class="nav-buttons">
                <a href="[이전페이지].html" class="nav-btn">← 이전: [제목]</a>
                <a href="[다음페이지].html" class="nav-btn">다음: [제목] →</a>
            </div>
        </div>
    </div>
</body>
</html>
```

### CSS 스타일 특징
- **배경**: 그라디언트 (보라-파랑 계열)
- **컨테이너**: 흰색 배경 + 둥근 모서리 + 그림자
- **색상 팔레트**: #3498db (파란색), #28a745 (녹색), #ffc107 (노란색), #dc3545 (빨간색)
- **폰트**: Apple 시스템 폰트 스택
- **반응형**: 모바일부터 데스크톱까지 지원

### 주요 CSS 클래스
```css
.detail-page { /* 메인 콘텐츠 컨테이너 */ }
.analysis-table { /* 분석 테이블 */ }
.summary-grid { /* 요약 카드 그리드 */ }
.summary-card.success { /* 성공 카드 (녹색) */ }
.summary-card.warning { /* 경고 카드 (노란색) */ }
.action-grid { /* 액션 아이템 그리드 */ }
.action-card.high-priority { /* 높은 우선순위 (빨간색) */ }
.action-card.medium-priority { /* 중간 우선순위 (노란색) */ }
.action-card.low-priority { /* 낮은 우선순위 (파란색) */ }
```

## 📋 메인 인덱스 페이지 (index.html) 구조

### 1. 헤더 섹션
```html
<header class="report-header">
    <h1>🎯 AWS 계정 종합 분석 보고서</h1>
    <div class="report-meta">
        <div class="meta-item">
            <strong>분석 대상:</strong> AWS 계정 157148350697
        </div>
        <!-- 기타 메타 정보 -->
    </div>
</header>
```

### 2. Executive Summary
```html
<section class="executive-summary">
    <h2>📋 Executive Summary</h2>
    <div class="summary-grid">
        <div class="summary-card success">
            <h3>✅ 강점</h3>
            <ul>
                <li>잘 구조화된 네트워킹 (5개 VPC)</li>
                <li>컨테이너 기반 워크로드 (EKS 1.31)</li>
                <!-- 기타 강점들 -->
            </ul>
        </div>
        <div class="summary-card warning">
            <h3>⚠️ 개선 기회</h3>
            <ul>
                <li>비용 최적화: 월 $420 절약 가능</li>
                <!-- 기타 개선사항들 -->
            </ul>
        </div>
    </div>
    
    <div class="cost-overview">
        <h3>💰 비용 분석 요약</h3>
        <div class="cost-metrics">
            <div class="metric">
                <span class="metric-value">$1,400</span>
                <span class="metric-label">현재 월간 비용</span>
            </div>
            <!-- 기타 메트릭들 -->
        </div>
    </div>
</section>
```

### 3. 네비게이션 카드 (9개 Phase)
```html
<section class="report-navigation">
    <h2>📚 상세 분석 보고서</h2>
    <div class="nav-grid">
        <a href="networking.html" class="nav-card">
            <div class="nav-icon">🌐</div>
            <h3>Phase 1: 네트워킹 분석</h3>
            <p>VPC, 서브넷, Transit Gateway, 보안 그룹 분석</p>
            <div class="nav-stats">
                <span>5개 VPC</span>
                <span>35개 서브넷</span>
                <span>1개 TGW</span>
            </div>
        </a>
        <!-- 나머지 8개 Phase 카드들 -->
    </div>
</section>
```

### 4. 빠른 실행 섹션
```html
<section class="quick-actions">
    <h2>🚀 빠른 실행</h2>
    <div class="action-grid">
        <div class="action-card high-priority">
            <h3>🔴 High Priority</h3>
            <ul>
                <li>Reserved Instance 구매</li>
                <li>EBS 볼륨 암호화</li>
                <!-- 기타 항목들 -->
            </ul>
            <div class="action-impact">예상 절약: $280/월</div>
        </div>
        <!-- Medium, Low Priority 카드들 -->
    </div>
</section>
```

## 🔧 사용된 도구 및 기술

### 1. 데이터 수집 도구
- **Steampipe**: SQL 기반 AWS 리소스 분석
- **AWS CLI**: 추가 리소스 정보 수집
- **Bash 스크립트**: 자동화된 데이터 처리

### 2. 보고서 생성 도구
- **HTML5**: 구조화된 웹 페이지
- **CSS3**: 모던 스타일링 (그라디언트, 플렉스박스, 그리드)
- **JavaScript**: 없음 (순수 HTML/CSS)

### 3. 문서화 도구
- **Glow**: 마크다운 뷰어 (터미널에서 보고서 미리보기)
- **Markdown**: 프롬프트 및 문서 작성

### 4. 개발 환경
- **Amazon Linux 2**: EC2 인스턴스
- **VSCode**: 코드 편집기
- **Git**: 버전 관리

## 📊 분석 결과 요약

### 현재 상태
- **총 월간 비용**: $1,400
- **주요 리소스**: 18개 EC2, 5개 VPC, 1개 EKS
- **보안 상태**: 부분적 암호화 (50%)
- **모니터링**: 기본 수준 (30% 가시성)

### 최적화 기회
- **비용 절약**: $524/월 (37% 절감)
- **보안 강화**: EBS 암호화, 보안 그룹 최적화
- **모니터링 개선**: CloudWatch Agent, Container Insights
- **운영 효율성**: 자동화, 알람, 대시보드

이것은 Part 1입니다. 계속해서 각 Phase별 상세 프롬프트를 작성하겠습니다.
