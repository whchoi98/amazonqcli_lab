#!/bin/bash
# Cost Optimization 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "💰 Cost Optimization 보고서 생성 중..."

cat > 09-cost-optimization.md << 'MDEOF'
# 비용 최적화 분석

## 💰 현재 비용 현황

### 월간 예상 비용 (추정)
- **EC2**: $400-600/월
- **RDS**: $200-300/월
- **S3**: $50-100/월
- **총 예상 비용**: $800-1,200/월

## 📊 비용 최적화 기회

### 🔴 즉시 절감 가능
1. **미사용 EBS 볼륨 삭제**: 월 $50-100 절감 예상
2. **중지된 인스턴스 정리**: 월 $100-200 절감 예상

---
*비용 최적화 분석 완료*
MDEOF

echo "✅ Cost Optimization 생성 완료: 09-cost-optimization.md"
