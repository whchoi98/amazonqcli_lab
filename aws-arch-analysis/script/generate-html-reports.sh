#!/bin/bash
# HTML 보고서 생성 스크립트

SCRIPT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/script"
REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"

echo "🌐 HTML 보고서 생성 시작..."
echo "📅 시작 시간: $(date)"

# Python 및 필요한 패키지 설치 확인
echo "🔧 필요한 패키지 설치 확인 중..."

# Python3 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되지 않았습니다."
    echo "설치 명령어: sudo yum install -y python3"
    exit 1
fi

# pip3 설치 확인
if ! command -v pip3 &> /dev/null; then
    echo "📦 pip3 설치 중..."
    sudo yum install -y python3-pip
fi

# markdown 패키지 설치 확인
if ! python3 -c "import markdown" 2>/dev/null; then
    echo "📦 markdown 패키지 설치 중..."
    pip3 install --user markdown
fi

# Markdown 파일 존재 확인
if [ ! -d "$REPORT_DIR" ] || [ ! -f "$REPORT_DIR/01-executive-summary.md" ]; then
    echo "❌ Markdown 보고서가 생성되지 않았습니다."
    echo "먼저 다음 명령어를 실행하세요:"
    echo "  cd $SCRIPT_DIR && ./generate-all-reports.sh"
    exit 1
fi

# HTML 출력 디렉토리 생성
mkdir -p "$HTML_DIR"

# Python 변환 스크립트 실행
echo "🔄 Markdown → HTML 변환 실행 중..."
cd "$SCRIPT_DIR"
python3 markdown-to-html-converter.py

# 결과 확인
if [ -f "$HTML_DIR/index.html" ]; then
    echo "✅ HTML 보고서 생성 성공!"
    echo "📁 출력 디렉토리: $HTML_DIR"
    echo "🌐 메인 페이지: $HTML_DIR/index.html"
    echo ""
    echo "📋 생성된 HTML 파일:"
    ls -la "$HTML_DIR"/*.html
    echo ""
    echo "🚀 브라우저에서 확인하려면:"
    echo "  file://$HTML_DIR/index.html"
else
    echo "❌ HTML 보고서 생성 실패"
    exit 1
fi

echo "📅 완료 시간: $(date)"
echo "🎉 HTML 보고서 생성 완료!"
