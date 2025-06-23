#!/bin/bash
# Security Analysis 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "🔐 Security Analysis 보고서 생성 중..."

cat > 06-security-analysis.md << 'MDEOF'
# 보안 및 자격 증명 분석

## 🔐 IAM 사용자 현황
MDEOF

# IAM 사용자 데이터 분석
if [ -f "security_iam_users.json" ] && [ -s "security_iam_users.json" ]; then
    IAM_USER_COUNT=$(jq '.rows | length' security_iam_users.json)
    echo "**총 IAM 사용자:** ${IAM_USER_COUNT}개" >> 06-security-analysis.md
    echo "" >> 06-security-analysis.md
    echo "| 사용자명 | 생성일 | 마지막 로그인 |" >> 06-security-analysis.md
    echo "|----------|--------|---------------|" >> 06-security-analysis.md
    jq -r '.rows[] | "| \(.user_name) | \(.create_date) | \(.password_last_used // "없음") |"' security_iam_users.json >> 06-security-analysis.md
else
    echo "IAM 사용자 데이터를 찾을 수 없습니다." >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

## 🎭 IAM 역할 현황
MDEOF

# IAM 역할 데이터 분석
if [ -f "security_iam_roles.json" ] && [ -s "security_iam_roles.json" ]; then
    IAM_ROLE_COUNT=$(jq '.rows | length' security_iam_roles.json)
    echo "**총 IAM 역할:** ${IAM_ROLE_COUNT}개" >> 06-security-analysis.md
    echo "" >> 06-security-analysis.md
    echo "| 역할명 | 생성일 |" >> 06-security-analysis.md
    echo "|--------|--------|" >> 06-security-analysis.md
    jq -r '.rows[] | "| \(.role_name) | \(.create_date) |"' security_iam_roles.json | head -10 >> 06-security-analysis.md
else
    echo "IAM 역할 데이터를 찾을 수 없습니다." >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

## 📋 보안 권장사항

### 🔴 높은 우선순위
1. **MFA 강제 적용**: 모든 IAM 사용자 MFA 설정
2. **루트 계정 보안**: 루트 계정 사용 최소화 및 MFA 설정
3. **액세스 키 순환**: 정기적인 액세스 키 교체

---
*보안 분석 완료*
MDEOF

echo "✅ Security Analysis 생성 완료: 06-security-analysis.md"
