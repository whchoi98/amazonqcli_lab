#!/bin/bash
# Cost Analysis 보고서 생성 스크립트 (Enhanced Version)
# 수집된 비용 데이터를 바탕으로 종합적인 비용 분석 보고서 생성

REPORT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"
cd $REPORT_DIR

echo "💰 Cost Analysis 보고서 생성 중..."

# 현재 날짜 및 시간
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cat > 07-cost-analysis.md << 'MDEOF'
# 💰 AWS 비용 분석 종합 보고서

> **분석 일시**: CURRENT_DATE_PLACEHOLDER  
> **분석 대상**: AWS 계정 내 모든 서비스 비용  
> **분석 리전**: ap-northeast-2 (서울)

## 📊 Executive Summary

### 비용 현황 개요
MDEOF

# 현재 날짜 삽입
sed -i "s/CURRENT_DATE_PLACEHOLDER/$CURRENT_DATE/g" 07-cost-analysis.md

# 비용 데이터 초기화
TOTAL_MONTHLY_COST=0
TOP_SERVICE_COST=0
TOP_SERVICE_NAME=""
SERVICE_COUNT=0

# 서비스별 월간 비용 분석
if [ -f "cost_by_service_monthly.json" ] && [ -s "cost_by_service_monthly.json" ]; then
    SERVICE_COUNT=$(jq '.rows | length' cost_by_service_monthly.json)
    
    if [ $SERVICE_COUNT -gt 0 ]; then
        # 총 월간 비용 계산
        TOTAL_MONTHLY_COST=$(jq '[.rows[].blended_cost_amount] | add' cost_by_service_monthly.json)
        
        # 최고 비용 서비스 정보
        TOP_SERVICE_COST=$(jq -r '.rows[0].blended_cost_amount' cost_by_service_monthly.json)
        TOP_SERVICE_NAME=$(jq -r '.rows[0].service' cost_by_service_monthly.json)
        
        cat >> 07-cost-analysis.md << MDEOF

**📈 월간 비용 요약 (현재 월)**
- **총 월간 비용**: \$$(printf "%.2f" $TOTAL_MONTHLY_COST) USD
- **활성 서비스 수**: ${SERVICE_COUNT}개
- **최고 비용 서비스**: ${TOP_SERVICE_NAME} (\$$(printf "%.2f" $TOP_SERVICE_COST))
- **평균 서비스 비용**: \$$(echo "scale=2; $TOTAL_MONTHLY_COST / $SERVICE_COUNT" | bc -l) USD

MDEOF
    fi
fi

cat >> 07-cost-analysis.md << 'MDEOF'

---

## 📊 서비스별 비용 분석

### 월간 서비스별 비용 현황
MDEOF

# 서비스별 월간 비용 상세 분석
if [ -f "cost_by_service_monthly.json" ] && [ -s "cost_by_service_monthly.json" ]; then
    cat >> 07-cost-analysis.md << MDEOF

#### 📋 상위 서비스별 월간 비용

| 순위 | 서비스명 | 월간 비용 (USD) | 비용 비율 | 기간 |
|------|----------|----------------|-----------|------|
MDEOF
    
    # 상위 10개 서비스 표시
    RANK=1
    jq -r '.rows[0:10][] | "\(.service)|\(.blended_cost_amount)|\(.period_start)|\(.period_end)"' cost_by_service_monthly.json | while IFS='|' read -r service cost start_date end_date; do
        PERCENTAGE=$(echo "scale=1; $cost * 100 / $TOTAL_MONTHLY_COST" | bc -l)
        FORMATTED_COST=$(printf "%.2f" $cost)
        PERIOD=$(echo $start_date | cut -d'T' -f1)" ~ "$(echo $end_date | cut -d'T' -f1)
        echo "| $RANK | $service | \$$FORMATTED_COST | ${PERCENTAGE}% | $PERIOD |" >> 07-cost-analysis.md
        RANK=$((RANK + 1))
    done
    
    cat >> 07-cost-analysis.md << MDEOF

#### 💡 서비스별 비용 분석

**주요 비용 서비스 분석**:
MDEOF
    
    # 상위 3개 서비스에 대한 분석
    jq -r '.rows[0:3][] | "\(.service)|\(.blended_cost_amount)"' cost_by_service_monthly.json | while IFS='|' read -r service cost; do
        FORMATTED_COST=$(printf "%.2f" $cost)
        PERCENTAGE=$(echo "scale=1; $cost * 100 / $TOTAL_MONTHLY_COST" | bc -l)
        
        case "$service" in
            *"Elastic Compute Cloud"*)
                echo "- **EC2 컴퓨팅**: \$$FORMATTED_COST (${PERCENTAGE}%) - 인스턴스 타입 최적화 및 Reserved Instance 검토 권장" >> 07-cost-analysis.md
                ;;
            *"Network Firewall"*)
                echo "- **Network Firewall**: \$$FORMATTED_COST (${PERCENTAGE}%) - 방화벽 정책 최적화 및 사용량 검토 필요" >> 07-cost-analysis.md
                ;;
            *"Virtual Private Cloud"*)
                echo "- **VPC 네트워킹**: \$$FORMATTED_COST (${PERCENTAGE}%) - NAT Gateway 및 데이터 전송 비용 최적화 검토" >> 07-cost-analysis.md
                ;;
            *"Relational Database Service"*)
                echo "- **RDS 데이터베이스**: \$$FORMATTED_COST (${PERCENTAGE}%) - 인스턴스 크기 조정 및 Reserved Instance 활용 검토" >> 07-cost-analysis.md
                ;;
            *)
                echo "- **$service**: \$$FORMATTED_COST (${PERCENTAGE}%) - 사용량 패턴 분석 및 최적화 검토 권장" >> 07-cost-analysis.md
                ;;
        esac
    done
    
else
    echo "❌ 서비스별 월간 비용 데이터를 찾을 수 없습니다." >> 07-cost-analysis.md
fi

cat >> 07-cost-analysis.md << 'MDEOF'

### 일간 비용 트렌드 분석
MDEOF

# 일간 비용 트렌드 분석
if [ -f "cost_by_service_daily.json" ] && [ -s "cost_by_service_daily.json" ]; then
    DAILY_RECORDS=$(jq '.rows | length' cost_by_service_daily.json)
    LATEST_DAILY_COST=$(jq '[.rows[] | select(.period_start | startswith("2025-06-26"))] | map(.blended_cost_amount) | add // 0' cost_by_service_daily.json)
    PREVIOUS_DAILY_COST=$(jq '[.rows[] | select(.period_start | startswith("2025-06-25"))] | map(.blended_cost_amount) | add // 0' cost_by_service_daily.json)
    
    cat >> 07-cost-analysis.md << MDEOF

**📈 일간 비용 트렌드**
- **총 일간 기록 수**: ${DAILY_RECORDS}개
- **최근 일간 비용**: \$$(printf "%.2f" $LATEST_DAILY_COST) USD
- **전일 대비 변화**: $(if (( $(echo "$LATEST_DAILY_COST > $PREVIOUS_DAILY_COST" | bc -l) )); then echo "📈 증가"; else echo "📉 감소"; fi)

#### 📋 최근 5일간 주요 서비스 비용

| 날짜 | 서비스 | 일간 비용 (USD) | 비고 |
|------|--------|----------------|------|
MDEOF
    
    # 최근 5일간 상위 서비스 비용 표시
    jq -r '.rows[] | select(.period_start >= "2025-06-22") | "\(.period_start)|\(.service)|\(.blended_cost_amount)"' cost_by_service_daily.json | sort -r | head -15 | while IFS='|' read -r date service cost; do
        FORMATTED_DATE=$(echo $date | cut -d'T' -f1)
        FORMATTED_COST=$(printf "%.2f" $cost)
        
        # 서비스명 단축
        SHORT_SERVICE=$(echo "$service" | sed 's/Amazon Elastic Compute Cloud - Compute/EC2 Compute/' | sed 's/AWS Network Firewall/Network Firewall/' | sed 's/Amazon Virtual Private Cloud/VPC/')
        
        echo "| $FORMATTED_DATE | $SHORT_SERVICE | \$$FORMATTED_COST | - |" >> 07-cost-analysis.md
    done
    
else
    echo "❌ 일간 비용 데이터를 찾을 수 없습니다." >> 07-cost-analysis.md
fi

cat >> 07-cost-analysis.md << 'MDEOF'

---

## 📈 사용량 타입별 상세 분석

### 서비스 사용 타입별 비용 분석
MDEOF

# 사용 타입별 월간 비용 분석
if [ -f "cost_by_service_usage_type_monthly.json" ] && [ -s "cost_by_service_usage_type_monthly.json" ]; then
    USAGE_TYPE_COUNT=$(jq '.rows | length' cost_by_service_usage_type_monthly.json)
    
    cat >> 07-cost-analysis.md << MDEOF

**📊 사용 타입별 통계**
- **총 사용 타입 수**: ${USAGE_TYPE_COUNT}개
- **분석 기간**: 현재 월 ($(date '+%Y-%m'))

#### 📋 상위 사용 타입별 월간 비용

| 순위 | 서비스 | 사용 타입 | 월간 비용 (USD) | 비용 비율 |
|------|--------|-----------|----------------|-----------|
MDEOF
    
    # 상위 15개 사용 타입 표시
    RANK=1
    jq -r '.rows[0:15][] | "\(.service)|\(.usage_type)|\(.blended_cost_amount)"' cost_by_service_usage_type_monthly.json | while IFS='|' read -r service usage_type cost; do
        FORMATTED_COST=$(printf "%.2f" $cost)
        PERCENTAGE=$(echo "scale=1; $cost * 100 / $TOTAL_MONTHLY_COST" | bc -l)
        
        # 서비스명 및 사용 타입 단축
        SHORT_SERVICE=$(echo "$service" | sed 's/Amazon Elastic Compute Cloud - Compute/EC2/' | sed 's/AWS Network Firewall/Network FW/' | sed 's/Amazon Virtual Private Cloud/VPC/')
        SHORT_USAGE=$(echo "$usage_type" | cut -c1-30)
        
        echo "| $RANK | $SHORT_SERVICE | $SHORT_USAGE | \$$FORMATTED_COST | ${PERCENTAGE}% |" >> 07-cost-analysis.md
        RANK=$((RANK + 1))
    done
    
    cat >> 07-cost-analysis.md << MDEOF

#### 💡 사용 타입별 최적화 권장사항

**EC2 관련 최적화**:
MDEOF
    
    # EC2 관련 사용 타입 분석
    EC2_USAGE_COST=$(jq '[.rows[] | select(.service | contains("Elastic Compute Cloud")) | .blended_cost_amount] | add // 0' cost_by_service_usage_type_monthly.json)
    if (( $(echo "$EC2_USAGE_COST > 0" | bc -l) )); then
        echo "- EC2 총 비용: \$$(printf "%.2f" $EC2_USAGE_COST) - 인스턴스 타입 최적화 및 Spot Instance 활용 검토" >> 07-cost-analysis.md
        echo "- Reserved Instance 구매를 통한 최대 75% 비용 절감 가능" >> 07-cost-analysis.md
    fi
    
    # Network Firewall 관련 분석
    NFW_USAGE_COST=$(jq '[.rows[] | select(.service | contains("Network Firewall")) | .blended_cost_amount] | add // 0' cost_by_service_usage_type_monthly.json)
    if (( $(echo "$NFW_USAGE_COST > 0" | bc -l) )); then
        echo "- Network Firewall 비용: \$$(printf "%.2f" $NFW_USAGE_COST) - 정책 최적화 및 불필요한 규칙 정리 권장" >> 07-cost-analysis.md
    fi
    
    # VPC 관련 분석
    VPC_USAGE_COST=$(jq '[.rows[] | select(.service | contains("Virtual Private Cloud")) | .blended_cost_amount] | add // 0' cost_by_service_usage_type_monthly.json)
    if (( $(echo "$VPC_USAGE_COST > 0" | bc -l) )); then
        echo "- VPC 네트워킹 비용: \$$(printf "%.2f" $VPC_USAGE_COST) - NAT Gateway 최적화 및 VPC Endpoint 활용 검토" >> 07-cost-analysis.md
    fi
    
else
    echo "❌ 사용 타입별 비용 데이터를 찾을 수 없습니다." >> 07-cost-analysis.md
fi

cat >> 07-cost-analysis.md << 'MDEOF'

---

## 📋 레코드 타입별 비용 분석

### 비용 구성 요소 분석
MDEOF

# 레코드 타입별 분석
if [ -f "cost_by_record_type_monthly.json" ] && [ -s "cost_by_record_type_monthly.json" ]; then
    cat >> 07-cost-analysis.md << MDEOF

#### 📊 레코드 타입별 월간 비용

| 레코드 타입 | 월간 비용 (USD) | 비용 비율 | 설명 |
|-------------|----------------|-----------|------|
MDEOF
    
    jq -r '.rows[] | "\(.record_type)|\(.blended_cost_amount)"' cost_by_record_type_monthly.json | while IFS='|' read -r record_type cost; do
        FORMATTED_COST=$(printf "%.2f" $cost)
        PERCENTAGE=$(echo "scale=1; $cost * 100 / $TOTAL_MONTHLY_COST" | bc -l)
        
        case "$record_type" in
            "Usage")
                DESCRIPTION="실제 서비스 사용량 기반 비용"
                ;;
            "Tax")
                DESCRIPTION="세금 및 부가세"
                ;;
            "Credit")
                DESCRIPTION="크레딧 및 할인"
                ;;
            "Fee")
                DESCRIPTION="서비스 수수료"
                ;;
            *)
                DESCRIPTION="기타 비용 항목"
                ;;
        esac
        
        echo "| $record_type | \$$FORMATTED_COST | ${PERCENTAGE}% | $DESCRIPTION |" >> 07-cost-analysis.md
    done
    
else
    echo "❌ 레코드 타입별 비용 데이터를 찾을 수 없습니다." >> 07-cost-analysis.md
fi

cat >> 07-cost-analysis.md << 'MDEOF'

---

## 💡 비용 최적화 권장사항

### 🔴 높은 우선순위 (즉시 조치)

#### 주요 서비스 최적화
MDEOF

# 비용 최적화 권장사항 생성
if [ -f "cost_by_service_monthly.json" ] && [ -s "cost_by_service_monthly.json" ]; then
    # EC2 비용이 높은 경우
    EC2_COST=$(jq '[.rows[] | select(.service | contains("Elastic Compute Cloud")) | .blended_cost_amount] | add // 0' cost_by_service_monthly.json)
    if (( $(echo "$EC2_COST > 200" | bc -l) )); then
        echo "1. **EC2 인스턴스 최적화**: 월 \$$(printf "%.0f" $EC2_COST) - Reserved Instance로 최대 75% 절감 가능" >> 07-cost-analysis.md
        echo "   - 인스턴스 타입 적정성 검토" >> 07-cost-analysis.md
        echo "   - Spot Instance 활용 검토" >> 07-cost-analysis.md
        echo "   - 미사용 인스턴스 정리" >> 07-cost-analysis.md
    fi
    
    # Network Firewall 비용이 높은 경우
    NFW_COST=$(jq '[.rows[] | select(.service | contains("Network Firewall")) | .blended_cost_amount] | add // 0' cost_by_service_monthly.json)
    if (( $(echo "$NFW_COST > 100" | bc -l) )); then
        echo "2. **Network Firewall 최적화**: 월 \$$(printf "%.0f" $NFW_COST) - 정책 및 규칙 최적화 필요" >> 07-cost-analysis.md
        echo "   - 불필요한 방화벽 규칙 정리" >> 07-cost-analysis.md
        echo "   - 방화벽 엔드포인트 수 최적화" >> 07-cost-analysis.md
    fi
    
    # VPC 비용이 높은 경우
    VPC_COST=$(jq '[.rows[] | select(.service | contains("Virtual Private Cloud")) | .blended_cost_amount] | add // 0' cost_by_service_monthly.json)
    if (( $(echo "$VPC_COST > 50" | bc -l) )); then
        echo "3. **VPC 네트워킹 최적화**: 월 \$$(printf "%.0f" $VPC_COST) - NAT Gateway 및 데이터 전송 최적화" >> 07-cost-analysis.md
        echo "   - NAT Gateway를 NAT Instance로 대체 검토" >> 07-cost-analysis.md
        echo "   - VPC Endpoint 활용으로 데이터 전송 비용 절감" >> 07-cost-analysis.md
    fi
fi

cat >> 07-cost-analysis.md << 'MDEOF'

### 🟡 중간 우선순위 (1-3개월 내)

#### 비용 모니터링 및 관리
1. **예산 설정**: 월간 예산 알림 설정으로 비용 초과 방지
2. **Cost Explorer 활용**: 정기적인 비용 트렌드 분석
3. **태그 기반 비용 관리**: 리소스 태깅을 통한 부서별/프로젝트별 비용 추적
4. **Reserved Instance 계획**: 장기 사용 리소스에 대한 RI 구매 계획 수립

#### 자동화 및 스케줄링
1. **Auto Scaling 최적화**: 수요에 따른 자동 확장/축소 설정
2. **스케줄링 기반 운영**: 개발/테스트 환경의 시간 기반 운영
3. **Lambda 활용**: 서버리스 아키텍처로 비용 효율성 개선

### 🟢 낮은 우선순위 (장기 계획)

#### 아키텍처 최적화
1. **서버리스 마이그레이션**: 적절한 워크로드의 서버리스 전환
2. **컨테이너화**: ECS/EKS를 통한 리소스 효율성 개선
3. **멀티 리전 최적화**: 지역별 비용 효율성을 고려한 리소스 배치

---

## 📊 비용 예측 및 목표

### 월간 비용 예측
MDEOF

# 비용 예측 계산
if [ -f "cost_by_service_monthly.json" ] && [ -s "cost_by_service_monthly.json" ]; then
    CURRENT_MONTH_DAYS=$(date +%d)
    TOTAL_MONTH_DAYS=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%d)
    PROJECTED_MONTHLY_COST=$(echo "scale=2; $TOTAL_MONTHLY_COST * $TOTAL_MONTH_DAYS / $CURRENT_MONTH_DAYS" | bc -l)
    
    cat >> 07-cost-analysis.md << MDEOF
- **현재까지 비용**: \$$(printf "%.2f" $TOTAL_MONTHLY_COST) USD (${CURRENT_MONTH_DAYS}일 기준)
- **월말 예상 비용**: \$$(printf "%.2f" $PROJECTED_MONTHLY_COST) USD
- **일평균 비용**: \$$(echo "scale=2; $TOTAL_MONTHLY_COST / $CURRENT_MONTH_DAYS" | bc -l) USD

### 비용 절감 목표
- **단기 목표 (3개월)**: 월간 비용 10-15% 절감 (\$$(echo "scale=0; $PROJECTED_MONTHLY_COST * 0.1" | bc -l)-\$$(echo "scale=0; $PROJECTED_MONTHLY_COST * 0.15" | bc -l) 절약)
- **중기 목표 (6개월)**: Reserved Instance 활용으로 20-30% 절감
- **장기 목표 (1년)**: 아키텍처 최적화로 전체 비용 30-40% 절감

MDEOF
fi

cat >> 07-cost-analysis.md << 'MDEOF'

---

## 💰 투자 우선순위 및 ROI 분석

### 비용 대비 효과 분석
1. **즉시 적용 가능 (무료)**
   - 미사용 리소스 정리
   - 인스턴스 타입 최적화
   - 스케줄링 기반 운영

2. **저비용 고효과 (월 $10-50)**
   - 예산 알림 설정
   - CloudWatch 모니터링 강화
   - 자동화 스크립트 구현

3. **중간 투자 (월 $50-200)**
   - Reserved Instance 구매
   - Savings Plans 활용
   - 전문 비용 최적화 도구

4. **고투자 장기 효과 (월 $200+)**
   - 아키텍처 재설계
   - 멀티 클라우드 전략
   - 전문 컨설팅 서비스

---

*📅 분석 완료 시간: CURRENT_DATE_PLACEHOLDER*  
*🔄 다음 비용 검토 권장 주기: 주 1회*  
*💰 비용 최적화 목표: 월간 비용 20% 절감*

---
MDEOF

echo "✅ Cost Analysis 생성 완료: 07-cost-analysis.md"
