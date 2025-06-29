#!/bin/bash
# HTML 변환 결과 자동 검증 스크립트

HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"
REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"

echo "🔍 HTML 변환 결과 검증 시작..."
echo "📅 검증 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 전역 변수
TOTAL_ERRORS=0
TOTAL_WARNINGS=0

# 에러 카운터 함수
add_error() {
    ((TOTAL_ERRORS++))
    echo "❌ $1"
}

add_warning() {
    ((TOTAL_WARNINGS++))
    echo "⚠️ $1"
}

add_success() {
    echo "✅ $1"
}

# 1. HTML 파일 개수 검증
echo "📊 Step 1: HTML 파일 개수 검증"
html_count=$(ls "$HTML_DIR"/*.html 2>/dev/null | wc -l)
echo "생성된 HTML 파일: $html_count개"

if [ "$html_count" -eq 11 ]; then
    add_success "HTML 파일 개수: 11개 (정상)"
else
    add_error "HTML 파일 개수: $html_count개 (11개 필요)"
fi
echo ""

# 2. 개별 파일 존재 확인
echo "📋 Step 2: 개별 파일 존재 확인"
required_files=(
    "index.html:메인 대시보드"
    "01-executive-summary.html:경영진 요약"
    "02-networking-analysis.html:네트워킹 분석"
    "03-compute-analysis.html:컴퓨팅 분석"
    "05-database-analysis.html:데이터베이스 분석"
    "05-storage-analysis.html:스토리지 분석"
    "06-security-analysis.html:보안 분석"
    "07-application-analysis.html:애플리케이션 분석"
    "08-monitoring-analysis.html:모니터링 분석"
    "09-cost-optimization.html:비용 최적화"
    "10-recommendations.html:종합 권장사항"
)

for file_info in "${required_files[@]}"; do
    filename=$(echo "$file_info" | cut -d: -f1)
    description=$(echo "$file_info" | cut -d: -f2)
    
    if [ -f "$HTML_DIR/$filename" ]; then
        add_success "$filename ($description)"
    else
        add_error "누락: $filename ($description)"
    fi
done
echo ""

# 3. 파일 크기 검증
echo "📊 Step 3: 파일 크기 검증 (최소 3KB)"
for html_file in "$HTML_DIR"/*.html; do
    if [ -f "$html_file" ]; then
        filename=$(basename "$html_file")
        filesize=$(stat -f%z "$html_file" 2>/dev/null || stat -c%s "$html_file" 2>/dev/null)
        
        if [ "$filesize" -gt 3072 ]; then  # 3KB = 3072 bytes
            add_success "$filename ($(($filesize / 1024))KB)"
        else
            add_warning "$filename ($(($filesize / 1024))KB) - 크기가 작음"
        fi
    fi
done
echo ""

# 4. Assets 폴더 구조 검증
echo "🎨 Step 4: Assets 폴더 구조 검증"
assets_dirs=("css" "js" "images")
for dir in "${assets_dirs[@]}"; do
    if [ -d "$HTML_DIR/assets/$dir" ]; then
        file_count=$(ls "$HTML_DIR/assets/$dir" 2>/dev/null | wc -l)
        if [ "$file_count" -gt 0 ]; then
            add_success "assets/$dir 폴더 ($file_count개 파일)"
        else
            add_warning "assets/$dir 폴더가 비어있음"
        fi
    else
        add_error "assets/$dir 폴더 누락"
    fi
done

# data 폴더 확인
if [ -d "$HTML_DIR/data" ]; then
    data_file_count=$(ls "$HTML_DIR/data"/*.json 2>/dev/null | wc -l)
    if [ "$data_file_count" -gt 0 ]; then
        add_success "data 폴더 ($data_file_count개 JSON 파일)"
    else
        add_warning "data 폴더가 비어있음"
    fi
else
    add_error "data 폴더 누락"
fi
echo ""

# 5. 네비게이션 링크 검증
echo "🔗 Step 5: 네비게이션 링크 검증"
for html_file in "$HTML_DIR"/*.html; do
    if [ -f "$html_file" ]; then
        filename=$(basename "$html_file")
        if grep -q "href.*\.html" "$html_file"; then
            add_success "$filename: 네비게이션 링크 포함"
        else
            add_warning "$filename: 네비게이션 링크 누락"
        fi
    fi
done
echo ""

# 6. Markdown 소스 파일 확인
echo "📝 Step 6: Markdown 소스 파일 확인"
md_count=$(ls "$REPORT_DIR"/*.md 2>/dev/null | wc -l)
if [ "$md_count" -eq 10 ]; then
    add_success "Markdown 파일: 10개 (정상)"
else
    add_warning "Markdown 파일: $md_count개 (10개 권장)"
fi
echo ""

# 최종 결과 요약
echo "🎯 검증 결과 요약"
echo "===================="
echo "✅ 성공: $((11 + 11 + $md_count + 4 - $TOTAL_ERRORS - $TOTAL_WARNINGS))개"
echo "⚠️ 경고: $TOTAL_WARNINGS개"
echo "❌ 오류: $TOTAL_ERRORS개"
echo ""

if [ "$TOTAL_ERRORS" -eq 0 ] && [ "$TOTAL_WARNINGS" -eq 0 ]; then
    echo "🎉 완벽! 모든 검증 통과"
    echo "🌐 웹 서버 실행: cd $HTML_DIR && python3 -m http.server 8080"
    exit 0
elif [ "$TOTAL_ERRORS" -eq 0 ]; then
    echo "✅ 기본 요구사항 충족 (경고 $TOTAL_WARNINGS개)"
    echo "🌐 웹 서버 실행: cd $HTML_DIR && python3 -m http.server 8080"
    exit 0
else
    echo "❌ 문제 발견! 해결 필요"
    echo "🔧 문제 해결: ./troubleshoot-html-conversion.sh"
    exit 1
fi
