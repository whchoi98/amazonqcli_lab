#!/bin/bash
# Markdown을 HTML로 변환하는 스크립트 (간단한 버전)

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"

echo "📝 Markdown 파일들을 HTML로 변환 시작..."

# HTML 템플릿 함수
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
        /* 테이블 전용 스타일 - 헤더 폰트 색상 수정 */
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
        
        /* 점수 컬럼 스타일링 */
        .analysis-table td:nth-child(2) {
            font-weight: bold;
            color: #2c3e50;
        }
        
        /* 상태 컬럼 스타일링 */
        .analysis-table td:nth-child(3) {
            font-weight: bold;
        }
        
        /* 리스트 스타일 개선 */
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
            <a href="04-database-analysis.html">🗄️ 데이터베이스</a>
            <a href="05-storage-analysis.html">💾 스토리지</a>
            <a href="06-security-analysis.html">🔒 보안</a>
            <a href="07-application-analysis.html">📱 애플리케이션</a>
            <a href="08-monitoring-analysis.html">📊 모니터링</a>
            <a href="09-cost-optimization.html">💰 비용</a>
            <a href="10-recommendations.html">🎯 권장사항</a>
        </nav>
        
        <main class="report-content">
            $content
        </main>
        
        <footer class="report-footer">
            <p>생성일: $(date '+%Y-%m-%d %H:%M:%S')</p>
            <p>AWS 계정: 613137910751 | 리전: ap-northeast-2</p>
        </footer>
    </div>
    
    <script src="assets/js/main.js"></script>
    <script src="assets/js/navigation.js"></script>
</body>
</html>
EOF
}

# 개선된 Markdown을 HTML로 변환하는 함수
convert_markdown_to_html() {
    local md_file="$1"
    local html_file="$2"
    local title="$3"
    
    if [ -f "$REPORT_DIR/$md_file" ]; then
        echo "🔄 변환 중: $md_file → $html_file"
        
        # Python을 사용한 고급 Markdown 변환
        python3 << EOF
import re
import sys

def convert_markdown_table(text):
    """Markdown 테이블을 HTML 테이블로 변환"""
    lines = text.split('\n')
    result = []
    in_table = False
    table_rows = []
    
    for line in lines:
        # 테이블 행 감지 (| 로 시작하거나 포함)
        if '|' in line and line.strip():
            # 구분선 제거 (|---|---|--- 형태)
            if re.match(r'^\s*\|[\s\-\|:]+\|\s*$', line):
                continue
                
            if not in_table:
                in_table = True
                table_rows = []
            
            # 테이블 행 처리
            cells = [cell.strip() for cell in line.split('|')]
            # 빈 첫 번째와 마지막 셀 제거
            if cells and not cells[0]:
                cells = cells[1:]
            if cells and not cells[-1]:
                cells = cells[:-1]
            
            table_rows.append(cells)
        else:
            # 테이블이 끝났을 때 HTML로 변환
            if in_table and table_rows:
                result.append(convert_table_to_html(table_rows))
                table_rows = []
                in_table = False
            
            result.append(line)
    
    # 마지막에 테이블이 있는 경우
    if in_table and table_rows:
        result.append(convert_table_to_html(table_rows))
    
    return '\n'.join(result)

def convert_table_to_html(table_rows):
    """테이블 행들을 HTML 테이블로 변환"""
    if not table_rows:
        return ""
    
    html = ['<table class="analysis-table">']
    
    # 첫 번째 행을 헤더로 처리
    if table_rows:
        html.append('  <thead>')
        html.append('    <tr>')
        for cell in table_rows[0]:
            # 볼드 텍스트 처리
            cell_content = process_markdown_formatting(cell)
            html.append(f'      <th>{cell_content}</th>')
        html.append('    </tr>')
        html.append('  </thead>')
    
    # 나머지 행들을 데이터로 처리
    if len(table_rows) > 1:
        html.append('  <tbody>')
        for row in table_rows[1:]:
            html.append('    <tr>')
            for cell in row:
                cell_content = process_markdown_formatting(cell)
                html.append(f'      <td>{cell_content}</td>')
            html.append('    </tr>')
        html.append('  </tbody>')
    
    html.append('</table>')
    return '\n'.join(html)

def process_markdown_formatting(text):
    """Markdown 포맷팅을 HTML로 변환"""
    # 볼드 텍스트 (**text** -> <strong>text</strong>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # 이탤릭 텍스트 (*text* -> <em>text</em>)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # 인라인 코드 (\`code\` -> <code>code</code>)
    text = re.sub(r'\`(.*?)\`', r'<code>\1</code>', text)
    
    return text

def convert_markdown_lists(text):
    """Markdown 리스트를 HTML 리스트로 변환"""
    lines = text.split('\n')
    result = []
    in_list = False
    list_items = []
    
    for line in lines:
        # 리스트 항목 감지 (- 또는 * 로 시작)
        if re.match(r'^\s*[-*]\s+', line):
            if not in_list:
                in_list = True
                list_items = []
            
            # 리스트 항목 내용 추출
            item_content = re.sub(r'^\s*[-*]\s+', '', line)
            item_content = process_markdown_formatting(item_content)
            list_items.append(item_content)
        else:
            # 리스트가 끝났을 때 HTML로 변환
            if in_list and list_items:
                result.append('<ul>')
                for item in list_items:
                    result.append(f'  <li>{item}</li>')
                result.append('</ul>')
                list_items = []
                in_list = False
            
            result.append(line)
    
    # 마지막에 리스트가 있는 경우
    if in_list and list_items:
        result.append('<ul>')
        for item in list_items:
            result.append(f'  <li>{item}</li>')
        result.append('</ul>')
    
    return '\n'.join(result)

def convert_markdown_headers(text):
    """Markdown 헤더를 HTML 헤더로 변환"""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        # 헤더 감지 (# ## ### 등)
        header_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if header_match:
            level = len(header_match.group(1))
            content = process_markdown_formatting(header_match.group(2))
            result.append(f'<h{level}>{content}</h{level}>')
        else:
            result.append(line)
    
    return '\n'.join(result)

def convert_markdown_to_html(markdown_content):
    """전체 Markdown을 HTML로 변환"""
    # 1. 테이블 변환
    html_content = convert_markdown_table(markdown_content)
    
    # 2. 리스트 변환
    html_content = convert_markdown_lists(html_content)
    
    # 3. 헤더 변환
    html_content = convert_markdown_headers(html_content)
    
    # 4. 단락 처리 (빈 줄로 구분된 텍스트를 <p> 태그로 감싸기)
    paragraphs = html_content.split('\n\n')
    processed_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            # 이미 HTML 태그로 시작하는 경우 그대로 유지
            if para.startswith(('<h', '<table', '<ul', '<ol', '<div')):
                processed_paragraphs.append(para)
            else:
                # 일반 텍스트는 <p> 태그로 감싸기
                para = process_markdown_formatting(para)
                processed_paragraphs.append(f'<p>{para}</p>')
    
    return '\n\n'.join(processed_paragraphs)

# 파일 읽기 및 변환
try:
    with open('$REPORT_DIR/$md_file', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    html_content = convert_markdown_to_html(markdown_content)
    print(html_content)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF
        
        # Python 스크립트의 출력을 content 변수에 저장
        content=$(python3 << EOF
import re
import sys

def convert_markdown_table(text):
    """Markdown 테이블을 HTML 테이블로 변환"""
    lines = text.split('\n')
    result = []
    in_table = False
    table_rows = []
    
    for line in lines:
        # 테이블 행 감지 (| 로 시작하거나 포함)
        if '|' in line and line.strip():
            # 구분선 제거 (|---|---|--- 형태)
            if re.match(r'^\s*\|[\s\-\|:]+\|\s*$', line):
                continue
                
            if not in_table:
                in_table = True
                table_rows = []
            
            # 테이블 행 처리
            cells = [cell.strip() for cell in line.split('|')]
            # 빈 첫 번째와 마지막 셀 제거
            if cells and not cells[0]:
                cells = cells[1:]
            if cells and not cells[-1]:
                cells = cells[:-1]
            
            table_rows.append(cells)
        else:
            # 테이블이 끝났을 때 HTML로 변환
            if in_table and table_rows:
                result.append(convert_table_to_html(table_rows))
                table_rows = []
                in_table = False
            
            result.append(line)
    
    # 마지막에 테이블이 있는 경우
    if in_table and table_rows:
        result.append(convert_table_to_html(table_rows))
    
    return '\n'.join(result)

def convert_table_to_html(table_rows):
    """테이블 행들을 HTML 테이블로 변환"""
    if not table_rows:
        return ""
    
    html = ['<table class="analysis-table">']
    
    # 첫 번째 행을 헤더로 처리
    if table_rows:
        html.append('  <thead>')
        html.append('    <tr>')
        for cell in table_rows[0]:
            # 볼드 텍스트 처리
            cell_content = process_markdown_formatting(cell)
            html.append(f'      <th>{cell_content}</th>')
        html.append('    </tr>')
        html.append('  </thead>')
    
    # 나머지 행들을 데이터로 처리
    if len(table_rows) > 1:
        html.append('  <tbody>')
        for row in table_rows[1:]:
            html.append('    <tr>')
            for cell in row:
                cell_content = process_markdown_formatting(cell)
                html.append(f'      <td>{cell_content}</td>')
            html.append('    </tr>')
        html.append('  </tbody>')
    
    html.append('</table>')
    return '\n'.join(html)

def process_markdown_formatting(text):
    """Markdown 포맷팅을 HTML로 변환"""
    # 볼드 텍스트 (**text** -> <strong>text</strong>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # 이탤릭 텍스트 (*text* -> <em>text</em>)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # 인라인 코드 (\`code\` -> <code>code</code>)
    text = re.sub(r'\`(.*?)\`', r'<code>\1</code>', text)
    
    return text

def convert_markdown_lists(text):
    """Markdown 리스트를 HTML 리스트로 변환"""
    lines = text.split('\n')
    result = []
    in_list = False
    list_items = []
    
    for line in lines:
        # 리스트 항목 감지 (- 또는 * 로 시작)
        if re.match(r'^\s*[-*]\s+', line):
            if not in_list:
                in_list = True
                list_items = []
            
            # 리스트 항목 내용 추출
            item_content = re.sub(r'^\s*[-*]\s+', '', line)
            item_content = process_markdown_formatting(item_content)
            list_items.append(item_content)
        else:
            # 리스트가 끝났을 때 HTML로 변환
            if in_list and list_items:
                result.append('<ul>')
                for item in list_items:
                    result.append(f'  <li>{item}</li>')
                result.append('</ul>')
                list_items = []
                in_list = False
            
            result.append(line)
    
    # 마지막에 리스트가 있는 경우
    if in_list and list_items:
        result.append('<ul>')
        for item in list_items:
            result.append(f'  <li>{item}</li>')
        result.append('</ul>')
    
    return '\n'.join(result)

def convert_markdown_headers(text):
    """Markdown 헤더를 HTML 헤더로 변환"""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        # 헤더 감지 (# ## ### 등)
        header_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if header_match:
            level = len(header_match.group(1))
            content = process_markdown_formatting(header_match.group(2))
            result.append(f'<h{level}>{content}</h{level}>')
        else:
            result.append(line)
    
    return '\n'.join(result)

def convert_markdown_to_html(markdown_content):
    """전체 Markdown을 HTML로 변환"""
    # 1. 테이블 변환
    html_content = convert_markdown_table(markdown_content)
    
    # 2. 리스트 변환
    html_content = convert_markdown_lists(html_content)
    
    # 3. 헤더 변환
    html_content = convert_markdown_headers(html_content)
    
    # 4. 단락 처리 (빈 줄로 구분된 텍스트를 <p> 태그로 감싸기)
    paragraphs = html_content.split('\n\n')
    processed_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            # 이미 HTML 태그로 시작하는 경우 그대로 유지
            if para.startswith(('<h', '<table', '<ul', '<ol', '<div')):
                processed_paragraphs.append(para)
            else:
                # 일반 텍스트는 <p> 태그로 감싸기
                para = process_markdown_formatting(para)
                processed_paragraphs.append(f'<p>{para}</p>')
    
    return '\n\n'.join(processed_paragraphs)

# 파일 읽기 및 변환
try:
    with open('$REPORT_DIR/$md_file', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    html_content = convert_markdown_to_html(markdown_content)
    print(html_content)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF
)
        
        generate_html_template "$title" "$content" "$html_file"
        echo "✅ 완료: $html_file"
    else
        echo "⚠️ 파일 없음: $md_file"
    fi
}

# 각 Markdown 파일을 HTML로 변환
echo "📋 변환할 파일 목록:"
ls -la "$REPORT_DIR"/*.md

echo ""
echo "🔄 변환 시작..."

convert_markdown_to_html "01-executive-summary.md" "01-executive-summary.html" "경영진 요약"
convert_markdown_to_html "02-networking-analysis.md" "02-networking-analysis.html" "네트워킹 분석"
convert_markdown_to_html "03-compute-analysis.md" "03-compute-analysis.html" "컴퓨팅 분석"
convert_markdown_to_html "04-database-analysis.md" "04-database-analysis.html" "데이터베이스 분석"
convert_markdown_to_html "05-storage-analysis.md" "05-storage-analysis.html" "스토리지 분석"
convert_markdown_to_html "06-security-analysis.md" "06-security-analysis.html" "보안 분석"
convert_markdown_to_html "07-application-analysis.md" "07-application-analysis.html" "애플리케이션 분석"
convert_markdown_to_html "08-monitoring-analysis.md" "08-monitoring-analysis.html" "모니터링 분석"
convert_markdown_to_html "09-cost-optimization.md" "09-cost-optimization.html" "비용 최적화"
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
