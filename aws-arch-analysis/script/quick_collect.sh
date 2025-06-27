#!/bin/bash

# AWS 계정 종합 데이터 수집 - 빠른 실행 스크립트
# 사용법: ./quick_collect.sh

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 스크립트 시작
echo "=========================================="
log_info "🚀 AWS 계정 종합 데이터 수집 시작"
echo "=========================================="

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$HOME/amazonqcli_lab/aws-arch-analysis/report"

log_info "📁 스크립트 위치: $SCRIPT_DIR"
log_info "📁 데이터 저장 위치: $REPORT_DIR"

# 디렉토리 생성
mkdir -p "$REPORT_DIR"

# Python 및 Steampipe 확인
log_info "🔍 환경 확인 중..."

if ! command -v python3 &> /dev/null; then
    log_error "Python3가 설치되어 있지 않습니다."
    exit 1
fi

if ! command -v steampipe &> /dev/null; then
    log_error "Steampipe가 설치되어 있지 않습니다."
    exit 1
fi

# AWS 자격 증명 확인
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS 자격 증명이 구성되어 있지 않습니다."
    exit 1
fi

log_success "환경 확인 완료"

# 데이터 수집 실행
log_info "📊 데이터 수집 시작..."
cd "$SCRIPT_DIR"

if python3 collect_all_data.py; then
    log_success "데이터 수집 완료!"
    
    # 결과 요약
    echo ""
    echo "=========================================="
    log_info "📊 수집 결과 요약"
    echo "=========================================="
    
    JSON_COUNT=$(find "$REPORT_DIR" -name "*.json" | wc -l)
    LOG_COUNT=$(find "$REPORT_DIR" -name "*.log" | wc -l)
    TOTAL_SIZE=$(du -sh "$REPORT_DIR" | cut -f1)
    
    log_info "📁 JSON 파일: $JSON_COUNT 개"
    log_info "📁 로그 파일: $LOG_COUNT 개"
    log_info "💾 총 크기: $TOTAL_SIZE"
    log_info "📂 저장 위치: $REPORT_DIR"
    
    echo ""
    log_success "🎉 AWS 계정 데이터 수집이 완료되었습니다!"
    log_info "💡 다음 단계: 수집된 데이터를 바탕으로 분석 보고서를 생성하세요."
    
else
    log_error "데이터 수집 중 오류가 발생했습니다."
    log_info "💡 로그 파일을 확인하여 문제를 해결하세요: $REPORT_DIR/*.log"
    exit 1
fi
