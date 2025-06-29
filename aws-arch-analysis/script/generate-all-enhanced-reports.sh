#!/bin/bash

# Enhanced AWS 계정 분석 보고서 일괄 생성 스크립트
# 모든 보고서를 새로운 데이터 기반 권장사항 기준으로 생성

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 시작 시간 기록
START_TIME=$(date +%s)
START_DATETIME=$(date '+%Y-%m-%d %H:%M:%S')

echo -e "${PURPLE}🚀 Enhanced AWS 계정 분석 보고서 일괄 생성${NC}"
echo "============================================================"
echo "📅 시작 시간: $START_DATETIME"
echo "📁 작업 디렉토리: $SCRIPT_DIR"
echo ""

# Python 환경 확인
if ! command -v python3 &> /dev/null; then
    log_error "Python3가 설치되지 않았습니다."
    exit 1
fi

# 베이스 클래스 파일 확인
if [ ! -f "recommendation_base.py" ]; then
    log_error "recommendation_base.py 파일이 없습니다. 먼저 베이스 클래스를 생성하세요."
    exit 1
fi

# 보고서 생성 함수
generate_report() {
    local script_name="$1"
    local report_name="$2"
    local icon="$3"
    
    log_info "${icon} ${report_name} 생성 중..."
    
    if [ -f "$script_name" ]; then
        if python3 "$script_name"; then
            log_success "${icon} ${report_name} 생성 완료"
            return 0
        else
            log_error "${icon} ${report_name} 생성 실패"
            return 1
        fi
    else
        log_warning "${icon} ${report_name} 스크립트 파일이 없습니다: $script_name"
        return 1
    fi
}

# 성공/실패 카운터
SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

# 보고서 생성 (의존성 순서 고려)
declare -a REPORTS=(
    "generate-networking-report.py:네트워킹 분석:🌐"
    "generate-compute-report.py:컴퓨팅 분석:💻"
    "generate_storage_report.py:스토리지 분석:💾"
    "generate_database_report.py:데이터베이스 분석:🗄️"
    "generate_security_report.py:보안 분석:🛡️"
    "generate-cost-report.py:비용 최적화:💰"
    "generate-application-report.py:애플리케이션 분석:🌐"
    "generate_monitoring_report.py:모니터링 분석:📈"
    "generate_recommendations.py:종합 권장사항:🎯"
    "generate_executive_summary.py:경영진 요약:📊"
)

echo "📋 보고서 생성 시작..."
echo ""

for report_info in "${REPORTS[@]}"; do
    IFS=':' read -r script_name report_name icon <<< "$report_info"
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    
    if generate_report "$script_name" "$report_name" "$icon"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo ""
done

# 종료 시간 계산
END_TIME=$(date +%s)
END_DATETIME=$(date '+%Y-%m-%d %H:%M:%S')
DURATION=$((END_TIME - START_TIME))

# 결과 요약
echo "============================================================"
echo -e "${PURPLE}📋 보고서 생성 결과 요약${NC}"
echo "============================================================"

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    log_success "모든 보고서 생성 완료: ${SUCCESS_COUNT}/${TOTAL_COUNT}"
else
    log_warning "일부 보고서 생성 실패: 성공 ${SUCCESS_COUNT}개, 실패 ${FAIL_COUNT}개"
fi

echo ""
echo "⏱️ 총 소요 시간: ${DURATION}초"
echo "📅 완료 시간: $END_DATETIME"

# 생성된 파일 확인
REPORT_DIR="../report"
if [ -d "$REPORT_DIR" ]; then
    MD_COUNT=$(find "$REPORT_DIR" -name "*.md" | wc -l)
    TOTAL_SIZE=$(find "$REPORT_DIR" -name "*.md" -exec stat -f%z {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}' || \
                 find "$REPORT_DIR" -name "*.md" -exec stat -c%s {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
    
    echo ""
    echo "📁 생성된 보고서 파일:"
    echo "   - 파일 수: ${MD_COUNT}개"
    echo "   - 총 크기: ${TOTAL_SIZE} bytes ($((TOTAL_SIZE / 1024)) KB)"
    echo "   - 위치: $(realpath "$REPORT_DIR")"
fi

# 권장사항 개선 사항 안내
echo ""
echo "🎯 Enhanced 권장사항 생성 기준 적용 완료:"
echo "   ✅ 데이터 기반 동적 권장사항 생성"
echo "   ✅ 우선순위별 분류 (높음/중간/낮음)"
echo "   ✅ 정량적 효과 및 구현 난이도 포함"
echo "   ✅ 실행 가능한 구체적 가이드 제공"
echo "   ✅ 보안, 비용, 성능, 컴플라이언스 기준 통일"

# HTML 변환 안내
echo ""
echo "💡 다음 단계:"
echo "   1. 생성된 Markdown 보고서 검토"
echo "   2. HTML 변환: ./convert-md-to-html.sh 실행"
echo "   3. 보고서 압축: ./compress-html-reports.sh 실행"

# 종료 코드 설정
if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    echo ""
    log_success "🎉 모든 보고서가 성공적으로 생성되었습니다!"
    exit 0
else
    echo ""
    log_error "⚠️ 일부 보고서 생성에 실패했습니다. 로그를 확인하세요."
    exit 1
fi
