#!/bin/bash
# Application Analysis 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "🌐 Application Analysis 보고서 생성 중..."

cat > 07-application-analysis.md << 'MDEOF'
# 애플리케이션 서비스 분석

## 🌐 API Gateway 현황
MDEOF

# API Gateway 데이터 분석
if [ -f "application_api_gateway_rest_apis.json" ] && [ -s "application_api_gateway_rest_apis.json" ]; then
    API_COUNT=$(jq length application_api_gateway_rest_apis.json)
    echo "**총 API Gateway:** ${API_COUNT}개" >> 07-application-analysis.md
else
    echo "API Gateway 데이터를 찾을 수 없습니다." >> 07-application-analysis.md
fi

cat >> 07-application-analysis.md << 'MDEOF'

## 📨 메시징 서비스 현황
MDEOF

# SNS/SQS 데이터 분석
if [ -f "application_sns_topics.json" ] && [ -s "application_sns_topics.json" ]; then
    SNS_COUNT=$(jq length application_sns_topics.json)
    echo "**총 SNS 토픽:** ${SNS_COUNT}개" >> 07-application-analysis.md
else
    echo "SNS 토픽 데이터를 찾을 수 없습니다." >> 07-application-analysis.md
fi

cat >> 07-application-analysis.md << 'MDEOF'

## 📋 애플리케이션 권장사항

### 🔴 높은 우선순위
1. **API Gateway 모니터링**: 응답 시간, 오류율 추적
2. **메시지 큐 최적화**: DLQ 설정 및 메시지 보존 기간 조정

---
*애플리케이션 분석 완료*
MDEOF

echo "✅ Application Analysis 생성 완료: 07-application-analysis.md"
