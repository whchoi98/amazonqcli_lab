# AWS 아키텍처 분석 보고서 Markdown → HTML 변환 프롬프트

## 🎯 변환 목표
AWS 아키텍처 진단 프롬프트(aws-diagnosis-prompt.md, aws-diagnosis-prompt-part2.md, aws-diagnosis-prompt-part3.md)를 통해 생성된 Markdown 보고서를 전문적이고 시각적으로 매력적인 HTML 보고서로 변환합니다.

## 📋 변환 요구사항

### 1. 기본 HTML 구조 생성
```
다음 구조로 HTML 파일들을 생성해주세요:

**메인 파일:**
□ index.html - 전체 보고서 개요 및 네비게이션
□ styles/main.css - 스타일시트 (기존 참조 파일 복사)

**상세 분석 페이지:**
□ networking.html - Phase 1: 네트워킹 리소스 분석
□ computing.html - Phase 1: 컴퓨팅 리소스 분석  
□ storage.html - Phase 1: 스토리지 리소스 분석
□ database.html - Phase 2: 데이터베이스 및 데이터 서비스 분석
□ security.html - Phase 3: 보안 및 자격 증명 서비스 분석
□ monitoring.html - Phase 5: 모니터링, 로깅 및 관리 서비스 분석
□ cost-optimization.html - Phase 6: 비용 최적화 분석
□ recommendations.html - Phase 6: 종합 권장사항 및 실행 계획
□ implementation.html - 구현 가이드 및 다음 단계
```

### 2. 메인 인덱스 페이지 (index.html) 구성
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS 계정 종합 분석 보고서</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>🎯 AWS 계정 종합 분석 보고서</h1>
            <div class="report-meta">
                <div class="meta-item">
                    <strong>분석 대상:</strong> AWS 계정 {account_id}
                </div>
                <div class="meta-item">
                    <strong>분석 리전:</strong> {region}
                </div>
                <div class="meta-item">
                    <strong>분석 일시:</strong> {analysis_date}
                </div>
                <div class="meta-item">
                    <strong>분석 도구:</strong> Steampipe + AWS CLI + Python
                </div>
            </div>
        </header>

        <section class="executive-summary">
            <h2>📋 Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card success">
                    <h3>✅ 주요 강점</h3>
                    <ul>
                        <!-- Markdown에서 추출한 강점 목록 -->
                    </ul>
                </div>
                <div class="summary-card warning">
                    <h3>⚠️ 개선 기회</h3>
                    <ul>
                        <!-- Markdown에서 추출한 개선사항 목록 -->
                    </ul>
                </div>
            </div>

            <div class="cost-overview">
                <h3>💰 비용 분석 개요</h3>
                <div class="cost-metrics">
                    <div class="metric">
                        <span class="metric-value">${monthly_cost}</span>
                        <span>월간 현재 비용</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${potential_savings}</span>
                        <span>절약 가능 비용</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">{resource_count}</span>
                        <span>총 리소스 수</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">{security_score}/5</span>
                        <span>보안 점수</span>
                    </div>
                </div>
            </div>
        </section>

        <section class="executive-summary">
            <h2>📚 상세 분석 보고서</h2>
            <div class="nav-grid">
                <a href="networking.html" class="nav-card">
                    <div class="nav-icon">🌐</div>
                    <h3>네트워킹 분석</h3>
                    <p>VPC, 서브넷, 보안 그룹, 라우팅 분석</p>
                    <div class="nav-stats">
                        <span>VPC {vpc_count}개</span>
                        <span>보안그룹 {sg_count}개</span>
                    </div>
                </a>
                
                <a href="computing.html" class="nav-card">
                    <div class="nav-icon">💻</div>
                    <h3>컴퓨팅 분석</h3>
                    <p>EC2, Lambda, ECS/EKS, Auto Scaling 분석</p>
                    <div class="nav-stats">
                        <span>EC2 {ec2_count}개</span>
                        <span>Lambda {lambda_count}개</span>
                    </div>
                </a>
                
                <a href="storage.html" class="nav-card">
                    <div class="nav-icon">💾</div>
                    <h3>스토리지 분석</h3>
                    <p>S3, EBS, EFS 스토리지 리소스 분석</p>
                    <div class="nav-stats">
                        <span>S3 버킷 {s3_count}개</span>
                        <span>EBS {ebs_count}개</span>
                    </div>
                </a>
                
                <a href="database.html" class="nav-card">
                    <div class="nav-icon">🗄️</div>
                    <h3>데이터베이스 분석</h3>
                    <p>RDS, DynamoDB, ElastiCache 분석</p>
                    <div class="nav-stats">
                        <span>RDS {rds_count}개</span>
                        <span>DynamoDB {dynamo_count}개</span>
                    </div>
                </a>
                
                <a href="security.html" class="nav-card">
                    <div class="nav-icon">🔐</div>
                    <h3>보안 분석</h3>
                    <p>IAM, KMS, WAF, GuardDuty 보안 분석</p>
                    <div class="nav-stats">
                        <span>IAM 사용자 {iam_users}개</span>
                        <span>IAM 역할 {iam_roles}개</span>
                    </div>
                </a>
                
                <a href="monitoring.html" class="nav-card">
                    <div class="nav-icon">📊</div>
                    <h3>모니터링 분석</h3>
                    <p>CloudWatch, X-Ray, Config 모니터링 분석</p>
                    <div class="nav-stats">
                        <span>알람 {alarms_count}개</span>
                        <span>로그그룹 {log_groups}개</span>
                    </div>
                </a>
                
                <a href="cost-optimization.html" class="nav-card">
                    <div class="nav-icon">💰</div>
                    <h3>비용 최적화</h3>
                    <p>비용 분석 및 최적화 기회</p>
                    <div class="nav-stats">
                        <span>절약 기회 {savings_opportunities}개</span>
                        <span>예상 절약 ${estimated_savings}</span>
                    </div>
                </a>
                
                <a href="recommendations.html" class="nav-card">
                    <div class="nav-icon">🎯</div>
                    <h3>권장사항</h3>
                    <p>종합 권장사항 및 실행 계획</p>
                    <div class="nav-stats">
                        <span>고우선순위 {high_priority}개</span>
                        <span>중우선순위 {medium_priority}개</span>
                    </div>
                </a>
                
                <a href="implementation.html" class="nav-card">
                    <div class="nav-icon">🚀</div>
                    <h3>구현 가이드</h3>
                    <p>실행 계획 및 다음 단계</p>
                    <div class="nav-stats">
                        <span>즉시 실행 {immediate_actions}개</span>
                        <span>단기 실행 {short_term}개</span>
                    </div>
                </a>
            </div>
        </section>

        <section class="executive-summary">
            <h2>🎯 우선순위별 실행 계획</h2>
            <div class="action-grid">
                <div class="action-card high-priority">
                    <h3>🔴 즉시 실행 (1-2주)</h3>
                    <ul>
                        <!-- 고우선순위 작업 목록 -->
                    </ul>
                </div>
                <div class="action-card medium-priority">
                    <h3>🟡 단기 실행 (1-3개월)</h3>
                    <ul>
                        <!-- 중간우선순위 작업 목록 -->
                    </ul>
                </div>
                <div class="action-card low-priority">
                    <h3>🟢 장기 실행 (3-12개월)</h3>
                    <ul>
                        <!-- 낮은우선순위 작업 목록 -->
                    </ul>
                </div>
            </div>
        </section>

        <footer class="report-footer">
            <div class="footer-content">
                <div>
                    <h4>📊 분석 정보</h4>
                    <p>생성일시: {current_time}</p>
                    <p>분석 도구: Steampipe + Python + AWS CLI</p>
                    <p>보고서 버전: v1.0</p>
                </div>
                <div>
                    <h4>🔗 추가 리소스</h4>
                    <p><a href="https://aws.amazon.com/well-architected/">AWS Well-Architected Framework</a></p>
                    <p><a href="https://aws.amazon.com/pricing/services/">AWS 요금 계산기</a></p>
                </div>
            </div>
        </footer>
    </div>
</body>
</html>
```

### 3. 상세 분석 페이지 템플릿
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - AWS 계정 종합 분석 보고서</title>
    <link rel="stylesheet" href="styles/main.css">
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
        .breadcrumb a:hover {
            text-decoration: underline;
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
        tr:last-child td {
            border-bottom: none;
        }
        
        /* 상태 배지 */
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status-running { background: #d4edda; color: #155724; }
        .status-stopped { background: #f8d7da; color: #721c24; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-success { background: #d1ecf1; color: #0c5460; }
        
        /* 메트릭 카드 */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        .metric-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        
        /* 권장사항 박스 */
        .recommendation-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .recommendation-box h4 {
            margin-top: 0;
            color: white;
        }
        
        /* 위험도 표시 */
        .risk-high { border-left: 5px solid #dc3545; }
        .risk-medium { border-left: 5px solid #ffc107; }
        .risk-low { border-left: 5px solid #28a745; }
        
        /* 헤딩 스타일 */
        h1 { 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 10px; 
        }
        h2 { 
            color: #34495e; 
            border-bottom: 2px solid #ecf0f1; 
            padding-bottom: 5px; 
            margin-top: 30px; 
        }
        h3 { 
            color: #7f8c8d; 
        }
        
        /* 코드 스타일 */
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
            color: #e83e8c;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }
        pre code {
            background: none;
            padding: 0;
            color: #333;
        }
        
        /* 리스트 스타일 */
        ul li {
            margin-bottom: 8px;
        }
        
        /* 체크리스트 스타일 */
        .checklist {
            list-style: none;
            padding-left: 0;
        }
        .checklist li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .checklist li:before {
            content: "□ ";
            color: #3498db;
            font-weight: bold;
            margin-right: 8px;
        }
        .checklist li.completed:before {
            content: "✅ ";
        }
        
        /* 네비게이션 버튼 */
        .nav-buttons {
            display: flex;
            justify-content: space-between;
            margin: 30px 0;
        }
        .nav-button {
            background: #3498db;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s;
        }
        .nav-button:hover {
            background: #2980b9;
            color: white;
        }
        .nav-button.disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="breadcrumb">
            <a href="index.html">🏠 홈</a> > 
            <span>{page_title}</span>
        </nav>
        
        <div class="detail-content">
            <!-- Markdown 콘텐츠를 HTML로 변환하여 삽입 -->
            {converted_html_content}
        </div>
        
        <div class="nav-buttons">
            <a href="{prev_page}" class="nav-button {prev_disabled}">← 이전 페이지</a>
            <a href="index.html" class="nav-button">📋 목차로</a>
            <a href="{next_page}" class="nav-button {next_disabled}">다음 페이지 →</a>
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

### 4. Markdown → HTML 변환 규칙

#### 4.1 헤딩 변환
```
# 제목 → <h1>제목</h1>
## 제목 → <h2>제목</h2>
### 제목 → <h3>제목</h3>
```

#### 4.2 체크리스트 변환
```
□ 항목 → <ul class="checklist"><li>항목</li></ul>
✅ 완료 항목 → <ul class="checklist"><li class="completed">완료 항목</li></ul>
```

#### 4.3 테이블 변환
```
Markdown 테이블을 HTML <table> 태그로 변환하고 스타일 적용
```

#### 4.4 코드 블록 변환
```
```code``` → <pre><code>code</code></pre>
`inline code` → <code>inline code</code>
```

#### 4.5 상태 배지 변환
```
**실행 중** → <span class="status-badge status-running">실행 중</span>
**중지됨** → <span class="status-badge status-stopped">중지됨</span>
**경고** → <span class="status-badge status-warning">경고</span>
**정상** → <span class="status-badge status-success">정상</span>
```

#### 4.6 메트릭 정보 변환
```
비용: $1,234 → 
<div class="metric-card">
    <div class="metric-value">$1,234</div>
    <div class="metric-label">월간 비용</div>
</div>
```

#### 4.7 권장사항 박스 변환
```
**권장사항:** 내용 → 
<div class="recommendation-box">
    <h4>💡 권장사항</h4>
    <p>내용</p>
</div>
```

#### 4.8 위험도 표시 변환
```
**높은 위험:** → <div class="risk-high">
**중간 위험:** → <div class="risk-medium">  
**낮은 위험:** → <div class="risk-low">
```

### 5. 변환 프로세스

#### 5.1 전처리
```
1. Markdown 파일 읽기
2. 메타데이터 추출 (계정 ID, 리전, 날짜 등)
3. 섹션별 콘텐츠 분리
4. 통계 정보 추출 (리소스 개수, 비용 등)
```

#### 5.2 HTML 생성
```
1. 메인 index.html 생성
2. 각 Phase별 상세 페이지 생성
3. CSS 파일 복사
4. 네비게이션 링크 연결
5. 메타데이터 삽입
```

#### 5.3 후처리
```
1. HTML 유효성 검사
2. 링크 연결 확인
3. 이미지 및 리소스 경로 확인
4. 반응형 디자인 테스트
```

### 6. 출력 파일 구조
```
reports/
├── index.html                 # 메인 대시보드
├── networking.html           # 네트워킹 분석
├── computing.html            # 컴퓨팅 분석
├── storage.html              # 스토리지 분석
├── database.html             # 데이터베이스 분석
├── security.html             # 보안 분석
├── monitoring.html           # 모니터링 분석
├── cost-optimization.html    # 비용 최적화
├── recommendations.html      # 권장사항
├── implementation.html       # 구현 가이드
└── styles/
    └── main.css             # 스타일시트
```

### 7. 품질 보증 체크리스트
```
□ 모든 Markdown 콘텐츠가 HTML로 정확히 변환됨
□ CSS 스타일이 모든 페이지에 적용됨
□ 네비게이션 링크가 정상 작동함
□ 테이블과 리스트가 올바르게 렌더링됨
□ 반응형 디자인이 모바일에서 정상 작동함
□ 메타데이터가 정확히 삽입됨
□ 코드 블록과 인라인 코드가 올바르게 표시됨
□ 상태 배지와 메트릭 카드가 정상 표시됨
□ 권장사항 박스가 올바르게 스타일링됨
□ 브라우저 호환성 확인 완료
```

이 프롬프트를 사용하여 AWS 아키텍처 분석 Markdown 보고서를 전문적인 HTML 보고서로 변환할 수 있습니다.
