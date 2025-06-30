#!/bin/bash
# HTML 보고서 자동 압축 스크립트

# 스크립트의 실제 위치를 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# 상대 경로로 디렉토리 설정
HTML_DIR="${PROJECT_ROOT}/html-report"

echo "📦 HTML 보고서 압축 파일 생성 중..."

# 현재 날짜와 시간으로 파일명 생성
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BASE_NAME="aws-analysis-html-report_${TIMESTAMP}"

# 상위 디렉토리로 이동하여 압축
CURRENT_DIR=$(pwd)
cd "$(dirname "$HTML_DIR")"

# ZIP 파일 생성
echo "🗜️ ZIP 파일 생성 중..."
zip -r "${BASE_NAME}.zip" "$(basename "$HTML_DIR")" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    ZIP_SIZE=$(du -h "${BASE_NAME}.zip" | cut -f1)
    echo "✅ ZIP 파일 생성 완료: ${BASE_NAME}.zip (${ZIP_SIZE})"
else
    echo "❌ ZIP 파일 생성 실패"
fi

# TAR.GZ 파일 생성
echo "🗜️ TAR.GZ 파일 생성 중..."
tar -czf "${BASE_NAME}.tar.gz" "$(basename "$HTML_DIR")" 2>/dev/null
if [ $? -eq 0 ]; then
    TAR_SIZE=$(du -h "${BASE_NAME}.tar.gz" | cut -f1)
    echo "✅ TAR.GZ 파일 생성 완료: ${BASE_NAME}.tar.gz (${TAR_SIZE})"
else
    echo "❌ TAR.GZ 파일 생성 실패"
fi

# 압축 파일을 HTML 디렉토리에도 복사 (웹 다운로드용)
if [ -f "${BASE_NAME}.zip" ]; then
    cp "${BASE_NAME}.zip" "$HTML_DIR/"
    echo "📋 웹 다운로드용 ZIP 파일 복사 완료"
fi

if [ -f "${BASE_NAME}.tar.gz" ]; then
    cp "${BASE_NAME}.tar.gz" "$HTML_DIR/"
    echo "📋 웹 다운로드용 TAR.GZ 파일 복사 완료"
fi

# 원래 디렉토리로 복귀
cd "$CURRENT_DIR"

echo ""
echo "📦 압축 파일 생성 완료!"
echo "📍 위치: $(dirname "$HTML_DIR")"
echo "📍 웹 다운로드: http://localhost:8080 (웹 서버 실행 시)"

# 파일 크기 비교 및 권장사항
if [ -f "$(dirname "$HTML_DIR")/${BASE_NAME}.zip" ] && [ -f "$(dirname "$HTML_DIR")/${BASE_NAME}.tar.gz" ]; then
    zip_bytes=$(du -b "$(dirname "$HTML_DIR")/${BASE_NAME}.zip" | cut -f1)
    tar_bytes=$(du -b "$(dirname "$HTML_DIR")/${BASE_NAME}.tar.gz" | cut -f1)
    
    echo ""
    echo "📊 압축 파일 비교:"
    echo "  🗜️ ZIP: ${ZIP_SIZE} (${zip_bytes} bytes)"
    echo "  🗜️ TAR.GZ: ${TAR_SIZE} (${tar_bytes} bytes)"
    
    if [ "$tar_bytes" -lt "$zip_bytes" ]; then
        savings=$((zip_bytes - tar_bytes))
        savings_percent=$(( (savings * 100) / zip_bytes ))
        echo "  💡 권장: TAR.GZ 파일 (${savings_percent}% 더 작음)"
    else
        echo "  💡 권장: ZIP 파일 (더 넓은 호환성)"
    fi
fi

echo ""
echo "🚀 다운로드 방법:"
echo "  1. 직접 다운로드: $(dirname "$HTML_DIR")/${BASE_NAME}.zip"
echo "  2. 웹 다운로드: http://localhost:8080/${BASE_NAME}.zip"
echo "  3. 명령어: cd $HTML_DIR && python3 -m http.server 8080"
