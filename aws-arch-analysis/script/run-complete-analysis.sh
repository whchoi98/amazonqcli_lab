#!/bin/bash
# AWS 아키텍처 분석 전체 프로세스 실행 스크립트

SCRIPT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/script"
REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"

echo "🚀 AWS 아키텍처 분석 전체 프로세스 시작..."
echo "📅 시작 시간: $(date)"
echo "🏗️ 분석 단계: 데이터 수집 → Markdown 보고서 → HTML 보고서"
echo ""

# 1단계: 데이터 수집 (이미 완료된 경우 스킵)
if [ ! -f "$REPORT_DIR/compute_ec2_instances.json" ]; then
    echo "📊 1단계: 데이터 수집 실행 중..."
    cd "$SCRIPT_DIR"
    ./02-collect-data.sh
    if [ $? -ne 0 ]; then
        echo "❌ 데이터 수집 실패"
        exit 1
    fi
    echo "✅ 데이터 수집 완료"
else
    echo "✅ 데이터 수집 이미 완료 (스킵)"
fi

echo ""

# 2단계: Markdown 보고서 생성
echo "📝 2단계: Markdown 보고서 생성 중..."
cd "$SCRIPT_DIR"
./generate-all-reports.sh
if [ $? -ne 0 ]; then
    echo "❌ Markdown 보고서 생성 실패"
    exit 1
fi
echo "✅ Markdown 보고서 생성 완료"

echo ""

# 3단계: HTML 보고서 생성
echo "🌐 3단계: HTML 보고서 생성 중..."
cd "$SCRIPT_DIR"
./generate-html-reports.sh
if [ $? -ne 0 ]; then
    echo "❌ HTML 보고서 생성 실패"
    exit 1
fi
echo "✅ HTML 보고서 생성 완료"

echo ""
echo "🎉 AWS 아키텍처 분석 전체 프로세스 완료!"
echo "📅 완료 시간: $(date)"
echo ""
echo "📋 생성된 결과물:"
echo "  📁 JSON 데이터: $REPORT_DIR/*.json"
echo "  📝 Markdown 보고서: $REPORT_DIR/*.md"
echo "  🌐 HTML 보고서: $HTML_DIR/*.html"
echo ""
echo "🚀 다음 단계:"
echo "  1. HTML 보고서 확인: file://$HTML_DIR/index.html"
echo "  2. 권장사항 검토 및 실행 계획 수립"
echo "  3. 정기적인 분석 스케줄 설정"
echo ""
echo "📊 분석 결과 요약:"
if [ -f "$REPORT_DIR/01-executive-summary.md" ]; then
    echo "  - VPC: $(jq '.rows | length' $REPORT_DIR/networking_vpc.json 2>/dev/null || echo 'N/A')개"
    echo "  - EC2: $(jq '.rows | length' $REPORT_DIR/compute_ec2_instances.json 2>/dev/null || echo 'N/A')개"
    echo "  - RDS: $(jq '.rows | length' $REPORT_DIR/database_rds_instances.json 2>/dev/null || echo 'N/A')개"
    echo "  - EBS: $(jq '.rows | length' $REPORT_DIR/storage_ebs_volumes.json 2>/dev/null || echo 'N/A')개"
    echo "  - 보안 그룹: $(jq '.rows | length' $REPORT_DIR/security_groups.json 2>/dev/null || echo 'N/A')개"
fi
