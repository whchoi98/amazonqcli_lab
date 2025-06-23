#!/bin/bash
# Monitoring Analysis 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "📊 Monitoring Analysis 보고서 생성 중..."

cat > 08-monitoring-analysis.md << 'MDEOF'
# 모니터링 및 로깅 분석

## 📊 CloudWatch 현황

### CloudWatch 알람
MDEOF

# CloudWatch 알람 데이터 분석
if [ -f "monitoring_cloudwatch_alarms.json" ] && [ -s "monitoring_cloudwatch_alarms.json" ]; then
    ALARM_COUNT=$(jq '.rows | length' monitoring_cloudwatch_alarms.json)
    echo "**총 CloudWatch 알람:** ${ALARM_COUNT}개" >> 08-monitoring-analysis.md
    if [ $ALARM_COUNT -gt 0 ]; then
        echo "" >> 08-monitoring-analysis.md
        echo "| 알람명 | 상태 | 메트릭 | 네임스페이스 |" >> 08-monitoring-analysis.md
        echo "|--------|------|--------|--------------|" >> 08-monitoring-analysis.md
        jq -r '.rows[] | "| \(.alarm_name) | \(.state_value) | \(.metric_name) | \(.namespace) |"' monitoring_cloudwatch_alarms.json >> 08-monitoring-analysis.md
    fi
else
    echo "**총 CloudWatch 알람:** 0개" >> 08-monitoring-analysis.md
    echo "⚠️ CloudWatch 알람이 설정되지 않았습니다." >> 08-monitoring-analysis.md
fi

cat >> 08-monitoring-analysis.md << 'MDEOF'

### CloudWatch 로그 그룹
MDEOF

# CloudWatch 로그 그룹 데이터 분석
if [ -f "monitoring_cloudwatch_log_groups.json" ] && [ -s "monitoring_cloudwatch_log_groups.json" ]; then
    LOG_GROUP_COUNT=$(jq '.rows | length' monitoring_cloudwatch_log_groups.json)
    TOTAL_SIZE=$(jq '[.rows[] | .stored_bytes] | add' monitoring_cloudwatch_log_groups.json 2>/dev/null || echo "0")
    echo "**총 CloudWatch 로그 그룹:** ${LOG_GROUP_COUNT}개" >> 08-monitoring-analysis.md
    echo "**총 저장된 로그 크기:** $(echo \"scale=2; $TOTAL_SIZE / 1024 / 1024\" | bc -l 2>/dev/null || echo \"N/A\")MB" >> 08-monitoring-analysis.md
    echo "" >> 08-monitoring-analysis.md
    echo "| 로그 그룹명 | 보존 기간 | 저장 크기 |" >> 08-monitoring-analysis.md
    echo "|-------------|-----------|-----------|" >> 08-monitoring-analysis.md
    jq -r '.rows[] | "| \(.name) | \(.retention_in_days // "무제한")일 | \((.stored_bytes / 1024 / 1024 * 100 | floor) / 100)MB |"' monitoring_cloudwatch_log_groups.json | head -10 >> 08-monitoring-analysis.md
else
    echo "CloudWatch 로그 그룹 데이터를 찾을 수 없습니다." >> 08-monitoring-analysis.md
fi

cat >> 08-monitoring-analysis.md << 'MDEOF'

### CloudWatch 로그 스트림
MDEOF

# CloudWatch 로그 스트림 데이터 분석
if [ -f "monitoring_cloudwatch_log_streams.json" ] && [ -s "monitoring_cloudwatch_log_streams.json" ]; then
    STREAM_COUNT=$(jq '.rows | length' monitoring_cloudwatch_log_streams.json)
    echo "**총 CloudWatch 로그 스트림:** ${STREAM_COUNT}개" >> 08-monitoring-analysis.md
    echo "" >> 08-monitoring-analysis.md
    echo "### 로그 그룹별 스트림 분포" >> 08-monitoring-analysis.md
    echo "| 로그 그룹 | 스트림 수 |" >> 08-monitoring-analysis.md
    echo "|-----------|-----------|" >> 08-monitoring-analysis.md
    jq -r '.rows | group_by(.log_group_name) | .[] | "| \(.[0].log_group_name) | \(length) |"' monitoring_cloudwatch_log_streams.json | head -10 >> 08-monitoring-analysis.md
else
    echo "CloudWatch 로그 스트림 데이터를 찾을 수 없습니다." >> 08-monitoring-analysis.md
fi

cat >> 08-monitoring-analysis.md << 'MDEOF'

## 🏥 AWS Health 이벤트

### Health 이벤트 현황
MDEOF

# Health 이벤트 데이터 분석
if [ -f "monitoring_health_events.json" ] && [ -s "monitoring_health_events.json" ]; then
    HEALTH_COUNT=$(jq '.rows | length' monitoring_health_events.json)
    echo "**총 Health 이벤트:** ${HEALTH_COUNT}개" >> 08-monitoring-analysis.md
    if [ $HEALTH_COUNT -gt 0 ]; then
        echo "" >> 08-monitoring-analysis.md
        echo "| 이벤트 타입 | 상태 | 시작 시간 | 서비스 |" >> 08-monitoring-analysis.md
        echo "|-------------|------|-----------|---------|" >> 08-monitoring-analysis.md
        jq -r '.rows[] | "| \(.event_type_category) | \(.status_code) | \(.start_time) | \(.service) |"' monitoring_health_events.json | head -5 >> 08-monitoring-analysis.md
    fi
else
    echo "Health 이벤트 데이터를 찾을 수 없습니다." >> 08-monitoring-analysis.md
fi

cat >> 08-monitoring-analysis.md << 'MDEOF'

## 📋 모니터링 권장사항

### 🔴 높은 우선순위
1. **핵심 메트릭 알람 설정**: CPU, 메모리, 디스크 사용률 모니터링
2. **로그 보존 정책**: 불필요한 로그 정리 및 보존 기간 설정
3. **애플리케이션 로그 중앙화**: CloudWatch Logs 활용

### 🟡 중간 우선순위
1. **대시보드 구성**: 운영 현황 시각화
2. **사용자 정의 메트릭**: 비즈니스 메트릭 모니터링
3. **알림 채널 설정**: SNS를 통한 알람 전송

### 🟢 낮은 우선순위
1. **X-Ray 트레이싱**: 분산 애플리케이션 성능 분석
2. **Container Insights**: ECS/EKS 컨테이너 모니터링
3. **Application Insights**: 애플리케이션 성능 자동 분석

## 💰 모니터링 비용 최적화

### 비용 절감 기회
MDEOF

# 모니터링 비용 최적화 분석
if [ -f "monitoring_cloudwatch_log_groups.json" ] && [ -s "monitoring_cloudwatch_log_groups.json" ]; then
    UNLIMITED_RETENTION=$(jq '[.rows[] | select(.retention_in_days == null)] | length' monitoring_cloudwatch_log_groups.json)
    if [ $UNLIMITED_RETENTION -gt 0 ]; then
        echo "1. **로그 보존 정책**: ${UNLIMITED_RETENTION}개 로그 그룹이 무제한 보존 설정" >> 08-monitoring-analysis.md
    fi
fi

cat >> 08-monitoring-analysis.md << 'MDEOF'
2. **불필요한 로그 스트림**: 오래된 로그 스트림 정리
3. **메트릭 필터 최적화**: 불필요한 메트릭 필터 제거

---
*모니터링 분석 완료*
MDEOF

echo "✅ Monitoring Analysis 생성 완료: 08-monitoring-analysis.md"
