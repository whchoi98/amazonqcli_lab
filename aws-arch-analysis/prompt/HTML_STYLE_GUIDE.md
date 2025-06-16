# AWS 보고서 HTML 스타일 가이드

## 🎨 스타일 적용 방법

### 1. CSS 파일 참조
```html
<link rel="stylesheet" href="main.css">
```

### 2. 기본 HTML 구조

#### 메인 인덱스 페이지 (index.html)
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS 계정 종합 분석 보고서 - 인덱스</title>
    <link rel="stylesheet" href="main.css">
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>🎯 AWS 계정 종합 분석 보고서</h1>
            <div class="report-meta">
                <div class="meta-item">
                    <strong>분석 대상:</strong> AWS 계정 {account_id}
                </div>
                <!-- 추가 메타 정보 -->
            </div>
        </header>

        <section class="executive-summary">
            <h2>📋 Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card success">
                    <h3>✅ 강점</h3>
                    <ul><!-- 강점 목록 --></ul>
                </div>
                <div class="summary-card warning">
                    <h3>⚠️ 개선 기회</h3>
                    <ul><!-- 개선 사항 목록 --></ul>
                </div>
            </div>

            <div class="cost-overview">
                <h3>💰 비용 분석 개요</h3>
                <div class="cost-metrics">
                    <div class="metric">
                        <span class="metric-value">$2,129</span>
                        <span>월간 현재 비용</span>
                    </div>
                    <!-- 추가 메트릭 -->
                </div>
            </div>
        </section>

        <section class="executive-summary">
            <h2>📚 상세 분석 보고서</h2>
            <div class="nav-grid">
                <a href="networking_analysis.html" class="nav-card">
                    <div class="nav-icon">🌐</div>
                    <h3>Phase 1: 네트워킹 분석</h3>
                    <p>VPC, 서브넷, 보안 그룹, 라우팅 분석</p>
                    <div class="nav-stats">
                        <span>VPC {vpc_count}개</span>
                        <span>보안그룹 {sg_count}개</span>
                    </div>
                </a>
                <!-- 추가 네비게이션 카드 -->
            </div>
        </section>

        <section class="executive-summary">
            <h2>🎯 우선순위별 실행 계획</h2>
            <div class="action-grid">
                <div class="action-card high-priority">
                    <h3>🔴 즉시 실행 (1-2주)</h3>
                    <ul><!-- 고우선순위 작업 --></ul>
                </div>
                <div class="action-card medium-priority">
                    <h3>🟡 1개월 내 (Medium)</h3>
                    <ul><!-- 중간우선순위 작업 --></ul>
                </div>
                <div class="action-card low-priority">
                    <h3>🟢 3개월 내 (Low)</h3>
                    <ul><!-- 낮은우선순위 작업 --></ul>
                </div>
            </div>
        </section>

        <footer class="report-footer">
            <div class="footer-content">
                <div>
                    <h4>📊 분석 정보</h4>
                    <p>생성일시: {current_time}</p>
                    <p>분석 도구: Steampipe + Python + AWS CLI</p>
                </div>
                <!-- 추가 푸터 콘텐츠 -->
            </div>
        </footer>
    </div>
</body>
</html>
```

#### 상세 분석 페이지 템플릿
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AWS 계정 종합 분석 보고서</title>
    <link rel="stylesheet" href="main.css">
    <style>
        .detail-content {
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .breadcrumb {
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .breadcrumb a {
            color: #3498db;
            text-decoration: none;
        }
        /* 테이블 스타일 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        th {
            background: #3498db;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }
        tr:hover {
            background: #f8f9fa;
        }
        /* 헤딩 스타일 */
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; margin-top: 30px; }
        h3 { color: #7f8c8d; }
        /* 코드 스타일 */
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="breadcrumb">
            <a href="index.html">🏠 홈</a> > 
            <span>{title}</span>
        </nav>
        
        <div class="detail-content">
            {html_content}
        </div>
        
        <footer class="report-footer">
            <div class="footer-content">
                <div>
                    <h4>📊 분석 정보</h4>
                    <p>생성일시: {current_time}</p>
                    <p>분석 도구: Steampipe + Python + AWS CLI</p>
                </div>
                <div>
                    <h4>🔗 네비게이션</h4>
                    <p><a href="index.html">메인 대시보드로 돌아가기</a></p>
                </div>
            </div>
        </footer>
    </div>
</body>
</html>
```

## 🎯 주요 CSS 클래스

### 레이아웃 클래스
- `.container`: 메인 컨테이너
- `.report-header`: 보고서 헤더
- `.executive-summary`: 섹션 컨테이너
- `.detail-content`: 상세 페이지 콘텐츠

### 메타 정보
- `.report-meta`: 메타 정보 그리드
- `.meta-item`: 개별 메타 항목

### 요약 카드
- `.summary-grid`: 요약 카드 그리드
- `.summary-card.success`: 성공/강점 카드 (녹색)
- `.summary-card.warning`: 경고/개선 카드 (노란색)

### 비용 개요
- `.cost-overview`: 비용 개요 섹션
- `.cost-metrics`: 비용 메트릭 그리드
- `.metric`: 개별 메트릭
- `.metric-value`: 메트릭 값 (큰 숫자)

### 네비게이션
- `.nav-grid`: 네비게이션 카드 그리드
- `.nav-card`: 개별 네비게이션 카드
- `.nav-icon`: 네비게이션 아이콘
- `.nav-stats`: 네비게이션 통계

### 액션 카드
- `.action-grid`: 액션 카드 그리드
- `.action-card.high-priority`: 높은 우선순위 (빨간색)
- `.action-card.medium-priority`: 중간 우선순위 (노란색)
- `.action-card.low-priority`: 낮은 우선순위 (파란색)

### 푸터
- `.report-footer`: 보고서 푸터
- `.footer-content`: 푸터 콘텐츠 그리드

## 🔧 Python 구현 예시

```python
def create_html_with_ref_style(title, content, account_id, current_time):
    """ 스타일을 적용한 HTML 생성"""
    
    # CSS 파일 복사
    ref_css_path = '/home/ec2-user/amazonqcli_lab/main.css'
    target_css_path = 'reports/main.css'
    shutil.copy2(ref_css_path, target_css_path)
    
    # HTML 템플릿 적용
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" href="main.css">
    </head>
    <body>
        <div class="container">
            {content}
        </div>
    </body>
    </html>
    """
    
    return html_template
```

## 📱 반응형 디자인

스타일은 자동으로 반응형 디자인을 지원합니다:

```css
@media (max-width: 768px) {
    .summary-grid { grid-template-columns: 1fr; }
    .nav-grid { grid-template-columns: 1fr; }
    .action-grid { grid-template-columns: 1fr; }
}
```

## 🎨 색상 팔레트

- **주요 색상**: #3498db (파란색)
- **성공/강점**: #28a745 (녹색)
- **경고/개선**: #ffc107 (노란색)
- **위험/긴급**: #dc3545 (빨간색)
- **정보**: #17a2b8 (청록색)
- **배경**: linear-gradient(135deg, #667eea 0%, #764ba2 100%)

## 📋 체크리스트

HTML 보고서 생성 시 확인사항:

- [ ] `~/amazonqcli_lab/main.css` 파일 복사
- [ ] `<link rel="stylesheet" href="main.css">` 포함
- [ ] 적절한 CSS 클래스 사용
- [ ] 반응형 디자인 고려
- [ ] 네비게이션 링크 연결
- [ ] 메타 정보 업데이트
- [ ] 푸터 정보 포함

이 가이드를 따라 일관된 스타일의 AWS 분석 보고서를 생성할 수 있습니다.
