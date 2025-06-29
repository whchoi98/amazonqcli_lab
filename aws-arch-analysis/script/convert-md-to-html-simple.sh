#!/bin/bash
# 간단한 Markdown to HTML 변환 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"
HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"
SCRIPT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/script"

echo "📝 Markdown 파일들을 HTML로 변환 시작..."

# HTML 템플릿 생성 함수
generate_html_template() {
    local title="$1"
    local content="$2"
    local filename="$3"
    
    cat > "$HTML_DIR/$filename" << EOF
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title - AWS 계정 분석 보고서</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/responsive.css">
    <link rel="stylesheet" href="assets/css/print.css">
    <style>
        .report-nav {
            background: #f8f9fa;
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .report-nav a {
            padding: 8px 12px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .report-nav a:hover {
            background: #0056b3;
        }
        .report-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            line-height: 1.6;
        }
        .report-content h1 { color: #2c3e50; margin-bottom: 20px; }
        .report-content h2 { color: #34495e; margin: 25px 0 15px 0; }
        .report-content h3 { color: #7f8c8d; margin: 20px 0 10px 0; }
        
        /* 테이블 스타일 */
        .analysis-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .analysis-table thead {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: #ffffff !important;
        }
        
        .analysis-table th {
            color: #ffffff !important;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 13px;
            letter-spacing: 0.5px;
            padding: 15px 12px;
            text-align: left;
            border-bottom: 2px solid #34495e;
        }
        
        .analysis-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            background-color: #ffffff;
        }
        
        .analysis-table tbody tr:hover {
            background-color: #f8f9fa !important;
            transform: translateY(-1px);
            transition: all 0.2s ease;
        }
        
        .analysis-table tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .analysis-table tbody tr:nth-child(odd) {
            background-color: white;
        }
        
        /* 리스트 스타일 */
        .report-content ul {
            list-style-type: none;
            padding-left: 0;
        }
        
        .report-content li {
            padding: 8px 0;
            border-left: 3px solid #3498db;
            padding-left: 15px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 0 4px 4px 0;
        }
        
        .report-content li:hover {
            background: #e9ecef;
            transform: translateX(5px);
            transition: all 0.2s ease;
        }
        
        /* 권장사항 스타일 */
        .recommendation-item {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 8px 8px 0;
            transition: all 0.3s ease;
        }
        
        .recommendation-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .recommendation-number {
            color: #007bff;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .report-content table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .report-content th, .report-content td { 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }
        .report-content th { background-color: #f2f2f2; }
        .report-content code { 
            background: #f4f4f4; 
            padding: 2px 4px; 
            border-radius: 3px; 
            font-family: monospace; 
        }
        .report-content pre { 
            background: #f8f8f8; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto; 
        }
        .report-footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>$title</h1>
            <p>AWS 계정 종합 분석 보고서</p>
        </div>
        
        <nav class="report-nav">
            <a href="index.html">🏠 홈</a>
            <a href="01-executive-summary.html">📊 요약</a>
            <a href="02-networking-analysis.html">🌐 네트워킹</a>
            <a href="03-compute-analysis.html">💻 컴퓨팅</a>
            <a href="04-storage-analysis.html">💾 스토리지</a>
            <a href="05-database-analysis.html">🗄️ 데이터베이스</a>
            <a href="06-security-analysis.html">🔒 보안</a>
            <a href="07-cost-optimization.html">💰 비용</a>
            <a href="08-application-analysis.html">📱 애플리케이션</a>
            <a href="09-monitoring-analysis.html">📊 모니터링</a>
            <a href="10-recommendations.html">🎯 권장사항</a>
        </nav>
        
        <main class="report-content">
            $content
        </main>
        
        <footer class="report-footer">
            <p>생성일: $(date '+%Y-%m-%d %H:%M:%S')</p>
            <p>AWS 계정: 861013826542 | 리전: ap-northeast-2</p>
        </footer>
    </div>
    
    <script src="assets/js/main.js"></script>
    <script src="assets/js/navigation.js"></script>
</body>
</html>
EOF
}

# Markdown을 HTML로 변환하는 함수
convert_markdown_to_html() {
    local md_file="$1"
    local html_file="$2"
    local title="$3"
    
    if [ -f "$REPORT_DIR/$md_file" ]; then
        echo "🔄 변환 중: $md_file → $html_file"
        
        # Python 스크립트를 사용하여 변환
        content=$(python3 "$SCRIPT_DIR/simple-md-to-html.py" "$md_file")
        
        generate_html_template "$title" "$content" "$html_file"
        echo "✅ 완료: $html_file"
    else
        echo "⚠️ 파일 없음: $md_file"
    fi
}

# Python 스크립트 실행 권한 부여
chmod +x "$SCRIPT_DIR/simple-md-to-html.py"

# 각 Markdown 파일을 HTML로 변환
echo "📋 변환할 파일 목록:"
ls -la "$REPORT_DIR"/*.md

echo ""
echo "🔄 변환 시작..."

convert_markdown_to_html "01-executive-summary.md" "01-executive-summary.html" "경영진 요약"
convert_markdown_to_html "02-networking-analysis.md" "02-networking-analysis.html" "네트워킹 분석"
convert_markdown_to_html "03-compute-analysis.md" "03-compute-analysis.html" "컴퓨팅 분석"
convert_markdown_to_html "04-storage-analysis.md" "04-storage-analysis.html" "스토리지 분석"
convert_markdown_to_html "05-database-analysis.md" "05-database-analysis.html" "데이터베이스 분석"
convert_markdown_to_html "06-security-analysis.md" "06-security-analysis.html" "보안 분석"
convert_markdown_to_html "07-cost-optimization.md" "07-cost-optimization.html" "비용 최적화"
convert_markdown_to_html "08-application-analysis.md" "08-application-analysis.html" "애플리케이션 분석"
convert_markdown_to_html "09-monitoring-analysis.md" "09-monitoring-analysis.html" "모니터링 분석"
convert_markdown_to_html "10-recommendations.md" "10-recommendations.html" "종합 권장사항"

echo ""
echo "🎉 Markdown → HTML 변환 완료!"
echo "📁 생성된 HTML 파일들:"
ls -la "$HTML_DIR"/*.html

echo ""
echo "📊 변환 결과 검증:"
html_count=$(ls "$HTML_DIR"/*.html 2>/dev/null | wc -l)
echo "생성된 HTML 파일: $html_count개"

if [ "$html_count" -eq 11 ]; then
    echo "✅ 성공: 11개 파일 모두 생성됨 (index.html + 10개 보고서)"
else
    echo "⚠️ 주의: $html_count개 생성됨 (11개 예상)"
fi

echo ""
echo "🌐 브라우저에서 확인:"
echo "  메인 대시보드: file://$HTML_DIR/index.html"
echo "  개별 보고서: file://$HTML_DIR/01-executive-summary.html"
