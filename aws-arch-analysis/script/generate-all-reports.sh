#!/bin/bash
# 전체 보고서 생성 마스터 스크립트

SCRIPT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/script"
REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"

echo "🚀 AWS 아키텍처 분석 보고서 생성 시작..."
echo "📅 시작 시간: $(date)"

# 보고서 디렉토리로 이동
cd $REPORT_DIR

# 모든 보고서 생성
echo "📊 1/10: Executive Summary 생성 중..."
bash $SCRIPT_DIR/generate-executive-summary.sh

echo "🌐 2/10: Networking Analysis 생성 중..."
bash $SCRIPT_DIR/generate-networking-report.sh

echo "💻 3/10: Compute Analysis 생성 중..."
bash $SCRIPT_DIR/generate-compute-report.sh

echo "🗄️ 4/10: Database Analysis 생성 중..."
bash $SCRIPT_DIR/generate-database-report.sh

echo "💾 5/10: Storage Analysis 생성 중..."
bash $SCRIPT_DIR/generate-storage-report.sh

echo "🔐 6/10: Security Analysis 생성 중..."
bash $SCRIPT_DIR/generate-security-report.sh

echo "🌐 7/10: Application Analysis 생성 중..."
bash $SCRIPT_DIR/generate-application-report.sh

echo "📊 8/10: Monitoring Analysis 생성 중..."
bash $SCRIPT_DIR/generate-monitoring-report.sh

echo "💰 9/10: Cost Optimization 생성 중..."
bash $SCRIPT_DIR/generate-cost-report.sh

echo "🎯 10/10: Recommendations 생성 중..."
bash $SCRIPT_DIR/generate-recommendations.sh

echo "🎉 모든 보고서 생성 완료!"
echo "📁 생성된 파일:"
ls -la *.md
