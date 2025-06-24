#!/bin/bash
# HTML 보고서 생성 스크립트 - 샘플 기반 동적 생성

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"
SAMPLE_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/sample"
SCRIPT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/script"

echo "🌐 HTML 보고서 생성 시작..."
echo "📁 출력 디렉토리: $HTML_DIR"

# HTML 디렉토리 생성
mkdir -p "$HTML_DIR"
mkdir -p "$HTML_DIR/assets/css"
mkdir -p "$HTML_DIR/assets/js"

# 1. 기본 CSS 파일 생성
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

# 2. 기본 JavaScript 파일 생성
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

echo "✅ JavaScript 파일 생성 완료"

# 3. 동적 index.html 생성 (실제 AWS 데이터 기반)
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

# 4. Markdown 파일들을 HTML로 변환
echo "📝 Markdown 파일들을 HTML로 변환 중..."
if [ -f "$SCRIPT_DIR/convert-md-to-html.sh" ]; then
    ./convert-md-to-html.sh
else
    echo "⚠️ Markdown 변환 스크립트를 찾을 수 없습니다."
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
