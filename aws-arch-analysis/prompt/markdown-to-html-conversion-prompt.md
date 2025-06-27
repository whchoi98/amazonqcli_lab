# AWS 아키텍처 분석 보고서 Markdown → HTML 변환 프롬프트

## 🎯 변환 목표
AWS 아키텍처 진단 프롬프트(aws-diagnosis-prompt-part1.md, aws-diagnosis-prompt-part2.md, aws-diagnosis-prompt-part3.md)를 통해 생성된 Markdown 보고서를 전문적이고 시각적으로 매력적인 HTML 보고서로 변환합니다.

## 📋 변환 요구사항

### 1. 기본 HTML 구조 생성
```
다음 구조로 HTML 파일들을 생성해주세요:

**메인 파일:**
□ index.html - 전체 보고서 개요 및 네비게이션 (sample/index.html 스타일 참조)

**상세 분석 페이지:**
□ 01-executive-summary.html - 전체 계정 분석 요약
□ 02-networking-analysis.html - 네트워킹 리소스 분석
□ 03-computing-analysis.html - 컴퓨팅 리소스 분석  
□ 04-storage-analysis.html - 스토리지 리소스 분석
□ 05-database-analysis.html - 데이터베이스 및 데이터 서비스 분석
□ 06-security-analysis.html - 보안 및 자격 증명 서비스 분석
□ 07-cost-optimization.html - 비용 최적화 분석
□ 08-application-monitoring.html - 애플리케이션 서비스 및 모니터링 분석
□ 09-comprehensive-recommendations.html - 종합 분석 및 권장사항
□ 10-implementation-guide.html - 구현 가이드 및 다음 단계
```

### 2. 메인 인덱스 페이지 (index.html) 구성
**sample/index.html 스타일을 완전히 따라 다음 구조를 사용:**

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS 계정 종합 분석 보고서</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6; color: #333; background-color: #f5f5f5;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px 0; text-align: center;
            margin-bottom: 30px; border-radius: 10px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px; margin-bottom: 40px;
        }
        .nav-card {
            background: white; border-radius: 10px; padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }
        .nav-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        .nav-card h3 { color: #667eea; margin-bottom: 15px; font-size: 1.3em; }
        .nav-card p { color: #666; margin-bottom: 15px; }
        .score { 
            display: inline-block; padding: 5px 15px; border-radius: 20px;
            font-weight: bold; font-size: 0.9em;
        }
        .score.excellent { background-color: #d4edda; color: #155724; }
        .score.good { background-color: #d1ecf1; color: #0c5460; }
        .score.fair { background-color: #fff3cd; color: #856404; }
        .score.poor { background-color: #f8d7da; color: #721c24; }
        .summary-section {
            background: white; border-radius: 10px; padding: 30px;
            margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .summary-section h2 { color: #667eea; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 AWS 계정 종합 분석 보고서</h1>
            <p>계정 ID: {account_id} | 리전: {region} | 분석일: {analysis_date}</p>
        </div>

        <div class="summary-section">
            <h2>📋 분석 개요</h2>
            <p><strong>분석 도구:</strong> Steampipe + AWS CLI + Amazon Q</p>
            <p><strong>총 리소스:</strong> {total_resources}개</p>
            <p><strong>월간 예상 비용:</strong> ${monthly_cost}</p>
        </div>

        <div class="nav-grid">
            <!-- 각 분석 섹션별 카드 -->
            <div class="nav-card" onclick="location.href='01-executive-summary.html'">
                <h3>📊 전체 계정 분석 요약</h3>
                <p>AWS 계정의 전반적인 상태와 주요 지표를 요약합니다.</p>
                <span class="score {overall_score_class}">{overall_score}</span>
            </div>
            <!-- 추가 카드들... -->
        </div>
    </div>
</body>
</html>
```

### 3. 상세 분석 페이지 스타일 (02-networking-analysis.html 등)
**sample/02-networking-analysis.html 스타일을 완전히 따라 다음 구조를 사용:**

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{페이지 제목}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6; color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { 
            max-width: 1200px; margin: 0 auto; 
            background: white; border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; text-align: center;
        }
        .header h1 { font-size: 2.2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .content { padding: 40px; }
        .nav-back { 
            display: inline-block; margin-bottom: 20px; 
            padding: 10px 20px; background: #667eea; color: white;
            text-decoration: none; border-radius: 5px;
            transition: background 0.3s ease;
        }
        .nav-back:hover { background: #5a6fd8; }
        h1, h2, h3, h4, h5, h6 { 
            color: #2c3e50; margin: 30px 0 15px 0; 
            font-weight: 600;
        }
        h1 { font-size: 2.2em; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        h2 { font-size: 1.8em; color: #667eea; }
        h3 { font-size: 1.4em; color: #5a6fd8; }
        p { margin: 15px 0; }
        table { 
            width: 100%; border-collapse: collapse; margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px; overflow: hidden;
        }
        th { 
            background: #667eea; color: white; padding: 15px;
            text-align: left; font-weight: 600;
        }
        td { padding: 12px 15px; border-bottom: 1px solid #eee; }
        tr:nth-child(even) { background: #f8f9fa; }
        tr:hover { background: #e3f2fd; }
        code { 
            background: #f4f4f4; padding: 2px 6px; 
            border-radius: 4px; font-family: 'Monaco', 'Consolas', monospace;
        }
        pre { 
            background: #2c3e50; color: #ecf0f1; padding: 20px;
            border-radius: 8px; overflow-x: auto; margin: 20px 0;
        }
        pre code { background: none; color: inherit; }
        ul, ol { margin: 15px 0; padding-left: 30px; }
        li { margin: 8px 0; }
        blockquote { 
            border-left: 4px solid #667eea; padding: 15px 20px;
            background: #f8f9fa; margin: 20px 0; border-radius: 0 8px 8px 0;
        }
        .score { 
            display: inline-block; padding: 5px 15px; border-radius: 20px;
            font-weight: bold; font-size: 0.9em;
        }
        .score.excellent { background-color: #d4edda; color: #155724; }
        .score.good { background-color: #d1ecf1; color: #0c5460; }
        .score.fair { background-color: #fff3cd; color: #856404; }
        .score.poor { background-color: #f8d7da; color: #721c24; }
        .priority-high { color: #dc3545; font-weight: bold; }
        .priority-medium { color: #ffc107; font-weight: bold; }
        .priority-low { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{페이지 제목}</h1>
            <p>AWS 계정 종합 분석 보고서</p>
        </div>
        <div class="content">
            <a href="index.html" class="nav-back">← 메인 페이지로 돌아가기</a>
            <!-- 여기에 Markdown 변환 내용 삽입 -->
        </div>
    </div>
</body>
</html>
```

## 🎨 스타일링 가이드라인

### 색상 체계 (sample 파일들과 동일하게 적용)
- **주요 그라데이션:** `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **텍스트 색상:** `#2c3e50` (제목), `#333` (본문)
- **배경색:** `#f5f5f5` (전체), `white` (카드)
- **강조색:** `#667eea` (링크, 제목)

### 점수 표시 색상
- **Excellent (90-100%):** `#d4edda` 배경, `#155724` 텍스트
- **Good (70-89%):** `#d1ecf1` 배경, `#0c5460` 텍스트  
- **Fair (50-69%):** `#fff3cd` 배경, `#856404` 텍스트
- **Poor (0-49%):** `#f8d7da` 배경, `#721c24` 텍스트

### 우선순위 색상
- **High Priority:** `#dc3545` (빨간색)
- **Medium Priority:** `#ffc107` (노란색)
- **Low Priority:** `#28a745` (초록색)

## 📊 데이터 시각화 요구사항

### 1. 테이블 스타일링
- 헤더: `#667eea` 배경, 흰색 텍스트
- 짝수 행: `#f8f9fa` 배경
- 호버 효과: `#e3f2fd` 배경
- 둥근 모서리와 그림자 효과 적용

### 2. 코드 블록
- 인라인 코드: `#f4f4f4` 배경
- 코드 블록: `#2c3e50` 배경, `#ecf0f1` 텍스트
- Monaco/Consolas 폰트 사용

### 3. 인용구 (blockquote)
- 왼쪽 보더: `4px solid #667eea`
- 배경: `#f8f9fa`
- 둥근 모서리 (오른쪽만)

## 🔗 네비게이션 요구사항

### 1. 메인 페이지 네비게이션
- 그리드 레이아웃 (최소 300px 너비)
- 호버 시 위로 5px 이동 효과
- 그림자 효과 강화

### 2. 상세 페이지 네비게이션
- "← 메인 페이지로 돌아가기" 버튼
- 각 페이지 간 이동 링크 (선택사항)

## 📱 반응형 디자인

### 1. 모바일 최적화
- 최대 너비: 1200px
- 그리드: `repeat(auto-fit, minmax(300px, 1fr))`
- 패딩 조정: 모바일에서 20px

### 2. 타이포그래피
- 제목: 2.5em (메인), 2.2em (상세)
- 본문: 1.6 line-height
- 폰트: Segoe UI, Tahoma, Geneva, Verdana, sans-serif

## 🚀 변환 실행 지침

### 1. Markdown 파싱
- 제목 레벨에 따른 적절한 HTML 태그 적용
- 테이블을 HTML table로 변환
- 코드 블록을 pre/code 태그로 변환
- 리스트를 ul/ol 태그로 변환

### 2. 메타데이터 치환
- `{account_id}`, `{region}`, `{analysis_date}` 등 실제 값으로 치환
- 점수 클래스 (`{score_class}`) 적절한 CSS 클래스로 치환
- 우선순위 클래스 적절한 색상으로 치환

### 3. 파일 생성
- 각 섹션별로 별도 HTML 파일 생성
- 일관된 네비게이션 구조 유지
- 크로스 링크 정확성 확인

### 4. 품질 검증
- HTML 유효성 검사
- 모든 링크 작동 확인
- 반응형 디자인 테스트
- 브라우저 호환성 확인

---

**참고:** 이 프롬프트는 sample 디렉토리의 HTML 파일들을 기반으로 작성되었으며, 동일한 시각적 스타일과 사용자 경험을 제공하도록 설계되었습니다.
