#!/bin/bash
# HTML 보고서 생성 스크립트 - 샘플 기반 동적 생성

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"
SAMPLE_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/sample"
SCRIPT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/script"

echo "🌐 HTML 보고서 생성 시작..."
echo "📁 출력 디렉토리: $HTML_DIR"

# HTML 디렉토리 및 assets 구조 생성
mkdir -p "$HTML_DIR"
mkdir -p "$HTML_DIR/assets/css"
mkdir -p "$HTML_DIR/assets/js"
mkdir -p "$HTML_DIR/assets/images"
mkdir -p "$HTML_DIR/data"

# 1. 메인 CSS 파일 생성
echo "🎨 CSS 스타일 파일 생성 중..."
cat > "$HTML_DIR/assets/css/style.css" << 'EOF'
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 0;
    text-align: center;
    margin-bottom: 30px;
    border-radius: 10px;
}

.nav-card {
    background: white;
    border-radius: 10px;
    padding: 25px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
}

.nav-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
}

.summary-section {
    background: white;
    border-radius: 10px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.metric-card {
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.priority-section {
    background: #fff3cd;
    border-left: 5px solid #ffc107;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
}
EOF

echo "✅ CSS 파일 생성 완료"

# 2. 반응형 CSS 파일 생성
echo "📱 반응형 CSS 파일 생성 중..."
cat > "$HTML_DIR/assets/css/responsive.css" << 'EOF'
/* 반응형 디자인 */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .nav-grid {
        grid-template-columns: 1fr;
    }
    
    .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .header h1 {
        font-size: 1.8em;
    }
}

@media (max-width: 480px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .nav-card {
        padding: 15px;
    }
}
EOF

# 3. 인쇄용 CSS 파일 생성
echo "🖨️ 인쇄용 CSS 파일 생성 중..."
cat > "$HTML_DIR/assets/css/print.css" << 'EOF'
@media print {
    .header {
        background: none !important;
        color: black !important;
    }
    
    .nav-card {
        box-shadow: none !important;
        border: 1px solid #ccc;
    }
    
    .priority-section {
        background: none !important;
        border: 1px solid #ffc107 !important;
    }
    
    .page-break {
        page-break-before: always;
    }
}
EOF

echo "✅ 모든 CSS 파일 생성 완료"

# 4. 메인 JavaScript 파일 생성
echo "⚡ JavaScript 파일 생성 중..."
cat > "$HTML_DIR/assets/js/main.js" << 'EOF'
function openReport(filename) {
    window.open(filename, '_blank');
}

document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.nav-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
EOF

# 5. 네비게이션 JavaScript 파일 생성
echo "🧭 네비게이션 JavaScript 파일 생성 중..."
cat > "$HTML_DIR/assets/js/navigation.js" << 'EOF'
// 네비게이션 기능
function navigateToReport(reportId) {
    const reportFiles = {
        'executive': '01-executive-summary.html',
        'networking': '02-networking-analysis.html',
        'compute': '03-compute-analysis.html',
        'database': '04-database-analysis.html',
        'storage': '05-storage-analysis.html',
        'security': '06-security-analysis.html',
        'application': '07-application-analysis.html',
        'monitoring': '08-monitoring-analysis.html',
        'cost': '09-cost-optimization.html',
        'recommendations': '10-recommendations.html'
    };
    
    if (reportFiles[reportId]) {
        window.open(reportFiles[reportId], '_blank');
    }
}

// 브레드크럼 네비게이션
function updateBreadcrumb(currentPage) {
    const breadcrumb = document.getElementById('breadcrumb');
    if (breadcrumb) {
        breadcrumb.innerHTML = `
            <a href="index.html">홈</a> > 
            <span class="current">${currentPage}</span>
        `;
    }
}
EOF

# 6. 차트 JavaScript 파일 생성
echo "📊 차트 JavaScript 파일 생성 중..."
cat > "$HTML_DIR/assets/js/charts.js" << 'EOF'
// 차트 생성 함수들
function createResourceChart(data) {
    // 리소스 분포 차트 생성 로직
    console.log('Creating resource chart with data:', data);
}

function createCostChart(data) {
    // 비용 트렌드 차트 생성 로직
    console.log('Creating cost chart with data:', data);
}

function createSecurityChart(data) {
    // 보안 점수 차트 생성 로직
    console.log('Creating security chart with data:', data);
}
EOF

# 7. 검색 JavaScript 파일 생성
echo "🔍 검색 JavaScript 파일 생성 중..."
cat > "$HTML_DIR/assets/js/search.js" << 'EOF'
// 검색 기능
function searchReports(query) {
    const searchResults = [];
    // 검색 로직 구현
    return searchResults;
}

function highlightSearchTerms(element, terms) {
    // 검색어 하이라이트 기능
    console.log('Highlighting terms:', terms);
}
EOF

echo "✅ 모든 JavaScript 파일 생성 완료"

# 8. 샘플 JSON 데이터 파일 생성
echo "📋 JSON 데이터 파일 생성 중..."
cat > "$HTML_DIR/data/resource-counts.json" << 'EOF'
{
    "vpc": 5,
    "ec2": 34,
    "rds": 2,
    "ebs": 34,
    "security_groups": 26,
    "iam_roles": 44
}
EOF

cat > "$HTML_DIR/data/cost-data.json" << 'EOF'
{
    "monthly_cost": 1200,
    "cost_trend": [1000, 1100, 1200],
    "cost_by_service": {
        "EC2": 600,
        "RDS": 300,
        "EBS": 200,
        "Other": 100
    }
}
EOF

cat > "$HTML_DIR/data/security-metrics.json" << 'EOF'
{
    "overall_score": 75,
    "iam_score": 70,
    "network_score": 80,
    "encryption_score": 75
}
EOF

echo "✅ JSON 데이터 파일 생성 완료"

echo "✅ JavaScript 파일 생성 완료"

# 9. 동적 index.html 생성 (실제 AWS 데이터 기반)
echo "📊 실제 AWS 데이터를 기반으로 index.html 생성 중..."
cd "$SCRIPT_DIR"
./generate-dynamic-index.sh
if [ $? -eq 0 ]; then
    echo "✅ 동적 index.html 생성 완료"
else
    echo "⚠️ 동적 생성 실패. 샘플 파일로 대체..."
    if [ -f "$SAMPLE_DIR/index.html" ]; then
        cp "$SAMPLE_DIR/index.html" "$HTML_DIR/index.html"
        echo "✅ 샘플 index.html 복사 완료"
    else
        echo "❌ 샘플 파일을 찾을 수 없습니다."
    fi
fi

# 10. Markdown 파일들을 HTML로 변환
echo "📝 Markdown 파일들을 HTML로 변환 중..."
if [ -f "$SCRIPT_DIR/convert-md-to-html.sh" ]; then
    cd "$SCRIPT_DIR"
    ./convert-md-to-html.sh
    if [ $? -eq 0 ]; then
        echo "✅ 모든 Markdown 파일이 HTML로 변환되었습니다!"
    else
        echo "⚠️ 일부 변환에서 오류가 발생했습니다."
    fi
else
    echo "❌ Markdown 변환 스크립트를 찾을 수 없습니다: $SCRIPT_DIR/convert-md-to-html.sh"
    echo "💡 수동으로 변환하려면: cd $SCRIPT_DIR && ./convert-md-to-html.sh"
fi

# 5. 결과 확인 및 요약
echo ""
echo "🎉 HTML 보고서 생성 완료!"
echo "📁 결과 위치: $HTML_DIR"
echo ""
echo "📋 생성된 파일들:"
ls -la "$HTML_DIR"/*.html 2>/dev/null | while read line; do
    echo "  📄 $line"
done

echo ""
echo "🚀 다음 단계:"
echo "  1. 메인 대시보드 확인: file://$HTML_DIR/index.html"
echo "  2. 브라우저에서 열기: firefox $HTML_DIR/index.html"
echo "  3. 최우선 조치 항목 검토"
echo "  4. 각 섹션별 상세 보고서 확인"

# 6. 간단한 웹 서버 시작 옵션 제공
echo ""
echo "💡 로컬 웹 서버로 확인하려면:"
echo "  cd $HTML_DIR && python3 -m http.server 8080"
echo "  그 후 브라우저에서 http://localhost:8080 접속"
