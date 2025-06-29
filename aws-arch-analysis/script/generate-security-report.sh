#!/bin/bash
# Security Analysis 보고서 생성 스크립트 (Enhanced Version)
# 수집된 보안 데이터를 바탕으로 종합적인 보안 태세 분석 보고서 생성

REPORT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"
cd $REPORT_DIR

echo "🛡️ Security Analysis 보고서 생성 중..."

# 현재 날짜 및 시간
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cat > 06-security-analysis.md << 'MDEOF'
# 🛡️ AWS 보안 리소스 종합 분석

> **분석 일시**: CURRENT_DATE_PLACEHOLDER  
> **분석 대상**: AWS 계정 내 모든 보안 서비스  
> **분석 리전**: ap-northeast-2 (서울)

## 📊 Executive Summary

### 보안 서비스 현황 개요
MDEOF

# 현재 날짜 삽입
sed -i "s/CURRENT_DATE_PLACEHOLDER/$CURRENT_DATE/g" 06-security-analysis.md

# 보안 서비스별 카운트 초기화
IAM_ROLES=0
IAM_USERS=0
IAM_GROUPS=0
KMS_KEYS=0
KMS_ALIASES=0
SECURITY_GROUPS=0
ACTIVE_SERVICES=0

# IAM 역할 카운트
if [ -f "security_iam_roles.json" ] && [ -s "security_iam_roles.json" ]; then
    IAM_ROLES=$(jq '.rows | length' security_iam_roles.json)
    if [ $IAM_ROLES -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

# IAM 사용자 카운트
if [ -f "security_iam_users.json" ] && [ -s "security_iam_users.json" ]; then
    IAM_USERS=$(jq '.rows | length' security_iam_users.json)
fi

# IAM 그룹 카운트
if [ -f "security_iam_groups.json" ] && [ -s "security_iam_groups.json" ]; then
    IAM_GROUPS=$(jq '.rows | length' security_iam_groups.json)
fi

# KMS 키 카운트
if [ -f "security_kms_keys.json" ] && [ -s "security_kms_keys.json" ]; then
    KMS_KEYS=$(jq '.rows | length' security_kms_keys.json)
    if [ $KMS_KEYS -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

# KMS 별칭 카운트
if [ -f "security_kms_aliases.json" ] && [ -s "security_kms_aliases.json" ]; then
    KMS_ALIASES=$(jq '.rows | length' security_kms_aliases.json)
fi

# 보안 그룹 카운트
if [ -f "security_groups.json" ] && [ -s "security_groups.json" ]; then
    SECURITY_GROUPS=$(jq '.rows | length' security_groups.json)
    if [ $SECURITY_GROUPS -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

TOTAL_SERVICES=6  # IAM, KMS, Security Groups, GuardDuty, Security Hub, CloudTrail

# Executive Summary 작성
cat >> 06-security-analysis.md << MDEOF

| 보안 서비스 | 리소스 수 | 상태 |
|-------------|-----------|------|
| 🔐 IAM 역할 | ${IAM_ROLES}개 | $([ $IAM_ROLES -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 👥 IAM 사용자 | ${IAM_USERS}개 | $([ $IAM_USERS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 👥 IAM 그룹 | ${IAM_GROUPS}개 | $([ $IAM_GROUPS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 🔑 KMS 키 | ${KMS_KEYS}개 | $([ $KMS_KEYS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 🏷️ KMS 별칭 | ${KMS_ALIASES}개 | $([ $KMS_ALIASES -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 🛡️ 보안 그룹 | ${SECURITY_GROUPS}개 | $([ $SECURITY_GROUPS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |

**활성 보안 서비스**: ${ACTIVE_SERVICES}/${TOTAL_SERVICES}개

---

## 🔐 IAM (Identity and Access Management) 상세 분석

### IAM 계정 요약
MDEOF
# IAM 계정 요약 분석
if [ -f "security_iam_account_summary.json" ] && [ -s "security_iam_account_summary.json" ]; then
    ACCOUNT_MFA=$(jq -r '.rows[0].account_mfa_enabled' security_iam_account_summary.json)
    TOTAL_USERS=$(jq -r '.rows[0].users' security_iam_account_summary.json)
    TOTAL_GROUPS=$(jq -r '.rows[0].groups' security_iam_account_summary.json)
    TOTAL_POLICIES=$(jq -r '.rows[0].policies' security_iam_account_summary.json)
    MFA_DEVICES=$(jq -r '.rows[0].mfa_devices' security_iam_account_summary.json)
    MFA_IN_USE=$(jq -r '.rows[0].mfa_devices_in_use' security_iam_account_summary.json)
    
    cat >> 06-security-analysis.md << MDEOF

**📈 IAM 계정 통계**
- **계정 MFA 활성화**: $([ "$ACCOUNT_MFA" = "true" ] && echo "✅ 활성화" || echo "❌ 비활성화")
- **총 사용자 수**: ${TOTAL_USERS}개
- **총 그룹 수**: ${TOTAL_GROUPS}개
- **고객 관리형 정책**: ${TOTAL_POLICIES}개
- **MFA 디바이스**: ${MFA_DEVICES}개 (사용 중: ${MFA_IN_USE}개)

#### 🔒 보안 권장사항 (계정 레벨)
$([ "$ACCOUNT_MFA" = "false" ] && echo "⚠️ **긴급**: 루트 계정 MFA 활성화 필요" || echo "✅ 루트 계정 MFA 활성화됨")
$([ $MFA_DEVICES -eq 0 ] && echo "⚠️ **권장**: 사용자 MFA 디바이스 설정 권장" || echo "✅ MFA 디바이스 구성됨")

MDEOF
else
    echo "❌ IAM 계정 요약 데이터를 찾을 수 없습니다." >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

### IAM 역할 분석
MDEOF

# IAM 역할 상세 분석
if [ -f "security_iam_roles.json" ] && [ -s "security_iam_roles.json" ]; then
    TOTAL_ROLES=$(jq '.rows | length' security_iam_roles.json)
    SERVICE_ROLES=$(jq '[.rows[] | select(.assume_role_policy_document | contains("Service"))] | length' security_iam_roles.json)
    CROSS_ACCOUNT_ROLES=$(jq '[.rows[] | select(.assume_role_policy_document | contains("AWS"))] | length' security_iam_roles.json)
    UNUSED_ROLES=$(jq '[.rows[] | select(.role_last_used_date == null)] | length' security_iam_roles.json)
    
    cat >> 06-security-analysis.md << MDEOF

**📈 IAM 역할 통계**
- **총 역할 수**: ${TOTAL_ROLES}개
- **서비스 역할**: ${SERVICE_ROLES}개
- **크로스 계정 역할**: ${CROSS_ACCOUNT_ROLES}개
- **미사용 역할**: ${UNUSED_ROLES}개

#### 📋 주요 IAM 역할 목록

| 역할명 | 생성일 | 마지막 사용 | 신뢰 관계 | 정책 수 |
|--------|--------|-------------|-----------|---------|
MDEOF
    
    # 상위 10개 역할 표시
    jq -r '.rows[0:10][] | "| \(.name) | \(.create_date // "N/A") | \(.role_last_used_date // "미사용") | \(if .assume_role_policy_document | contains("Service") then "서비스" elif .assume_role_policy_document | contains("AWS") then "크로스계정" else "기타" end) | \(.attached_policy_arns | length) |"' security_iam_roles.json >> 06-security-analysis.md
    
    cat >> 06-security-analysis.md << MDEOF

#### 🔍 역할 보안 분석

**서비스별 역할 분포**:
MDEOF
    
    # 서비스별 역할 분석
    jq -r '.rows[] | .assume_role_policy_document' security_iam_roles.json | grep -o '"Service":"[^"]*"' | sort | uniq -c | sort -nr | head -5 | while read count service; do
        service_name=$(echo $service | sed 's/"Service":"//g' | sed 's/"//g')
        echo "- **${service_name}**: ${count}개 역할" >> 06-security-analysis.md
    done
    
    cat >> 06-security-analysis.md << MDEOF

**보안 권장사항**:
- $([ $UNUSED_ROLES -gt 0 ] && echo "⚠️ **${UNUSED_ROLES}개 미사용 역할** 정리 검토 필요" || echo "✅ 모든 역할이 사용 중")
- $([ $CROSS_ACCOUNT_ROLES -gt 0 ] && echo "🔍 **${CROSS_ACCOUNT_ROLES}개 크로스 계정 역할** 신뢰 관계 검토 필요" || echo "✅ 크로스 계정 역할 없음")
- 🔒 정기적인 역할 권한 검토 및 최소 권한 원칙 적용 권장

MDEOF
else
    echo "❌ IAM 역할 데이터를 찾을 수 없습니다." >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

---

## 🔑 KMS (Key Management Service) 분석

### 암호화 키 관리 현황
MDEOF

# KMS 키 분석
if [ -f "security_kms_keys.json" ] && [ -s "security_kms_keys.json" ]; then
    TOTAL_KEYS=$(jq '.rows | length' security_kms_keys.json)
    CUSTOMER_KEYS=$(jq '[.rows[] | select(.key_manager == "CUSTOMER")] | length' security_kms_keys.json)
    AWS_KEYS=$(jq '[.rows[] | select(.key_manager == "AWS")] | length' security_kms_keys.json)
    ENABLED_KEYS=$(jq '[.rows[] | select(.enabled == true)] | length' security_kms_keys.json)
    ROTATION_ENABLED=$(jq '[.rows[] | select(.key_rotation_enabled == true)] | length' security_kms_keys.json)
    MULTI_REGION_KEYS=$(jq '[.rows[] | select(.multi_region == true)] | length' security_kms_keys.json)
    
    cat >> 06-security-analysis.md << MDEOF

**📈 KMS 키 통계**
- **총 키 수**: ${TOTAL_KEYS}개
- **고객 관리형 키**: ${CUSTOMER_KEYS}개
- **AWS 관리형 키**: ${AWS_KEYS}개
- **활성화된 키**: ${ENABLED_KEYS}개
- **자동 순환 활성화**: ${ROTATION_ENABLED}개
- **다중 리전 키**: ${MULTI_REGION_KEYS}개

#### 📋 KMS 키 상세 목록

| 키 ID | 설명 | 상태 | 키 관리자 | 자동 순환 | 다중 리전 |
|-------|------|------|-----------|-----------|-----------|
MDEOF
    
    # 고객 관리형 키만 표시
    jq -r '.rows[] | select(.key_manager == "CUSTOMER") | "| \(.id[0:8])... | \(.description // "설명 없음") | \(if .enabled then "✅ 활성" else "❌ 비활성" end) | \(.key_manager) | \(if .key_rotation_enabled then "✅" else "❌" end) | \(if .multi_region then "✅" else "❌" end) |"' security_kms_keys.json >> 06-security-analysis.md
    
    cat >> 06-security-analysis.md << MDEOF

#### 🔐 암호화 보안 분석

**키 사용 현황**:
- **대칭 키**: $(jq '[.rows[] | select(.key_usage == "ENCRYPT_DECRYPT")] | length' security_kms_keys.json)개
- **비대칭 키**: $(jq '[.rows[] | select(.key_usage != "ENCRYPT_DECRYPT")] | length' security_kms_keys.json)개

**보안 권장사항**:
- $([ $ROTATION_ENABLED -lt $CUSTOMER_KEYS ] && echo "⚠️ **$(($CUSTOMER_KEYS - $ROTATION_ENABLED))개 키** 자동 순환 비활성화 - 활성화 권장" || echo "✅ 모든 고객 관리형 키에서 자동 순환 활성화됨")
- 🔒 키 정책 정기 검토 및 최소 권한 원칙 적용
- 📊 CloudTrail을 통한 키 사용 모니터링 권장

MDEOF
else
    echo "❌ KMS 키 데이터를 찾을 수 없습니다." >> 06-security-analysis.md
fi

# KMS 별칭 분석
if [ -f "security_kms_aliases.json" ] && [ -s "security_kms_aliases.json" ]; then
    TOTAL_ALIASES=$(jq '.rows | length' security_kms_aliases.json)
    
    cat >> 06-security-analysis.md << MDEOF

### KMS 별칭 관리

**📈 KMS 별칭 통계**
- **총 별칭 수**: ${TOTAL_ALIASES}개

#### 📋 KMS 별칭 목록

| 별칭명 | 대상 키 ID | 생성일 |
|--------|------------|--------|
MDEOF
    
    jq -r '.rows[] | "| \(.alias_name) | \(.target_key_id[0:8])... | \(.creation_date // "N/A") |"' security_kms_aliases.json >> 06-security-analysis.md
fi
cat >> 06-security-analysis.md << 'MDEOF'

---

## 🛡️ 네트워크 보안 분석

### 보안 그룹 (Security Groups) 현황
MDEOF

# 보안 그룹 분석
if [ -f "security_groups.json" ] && [ -s "security_groups.json" ]; then
    TOTAL_SG=$(jq '.rows | length' security_groups.json)
    DEFAULT_SG=$(jq '[.rows[] | select(.group_name == "default")] | length' security_groups.json)
    UNUSED_SG=$(jq '[.rows[] | select(.ip_permissions == [] and .ip_permissions_egress | length <= 1)] | length' security_groups.json)
    
    cat >> 06-security-analysis.md << MDEOF

**📈 보안 그룹 통계**
- **총 보안 그룹 수**: ${TOTAL_SG}개
- **기본 보안 그룹**: ${DEFAULT_SG}개
- **미사용 보안 그룹**: ${UNUSED_SG}개

#### 📋 주요 보안 그룹 목록

| 그룹명 | 그룹 ID | VPC ID | 설명 | 인바운드 규칙 | 아웃바운드 규칙 |
|--------|---------|--------|------|---------------|----------------|
MDEOF
    
    # 상위 10개 보안 그룹 표시
    jq -r '.rows[0:10][] | "| \(.group_name) | \(.group_id) | \(.vpc_id // "EC2-Classic") | \(.description // "설명 없음") | \(.ip_permissions | length) | \(.ip_permissions_egress | length) |"' security_groups.json >> 06-security-analysis.md
    
    cat >> 06-security-analysis.md << MDEOF

#### 🔍 보안 그룹 보안 분석

**위험한 규칙 검사**:
MDEOF
    
    # 위험한 인바운드 규칙 검사 (0.0.0.0/0 허용)
    OPEN_SSH=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 22 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    OPEN_RDP=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 3389 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    OPEN_HTTP=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 80 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    OPEN_HTTPS=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 443 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    
    cat >> 06-security-analysis.md << MDEOF
- **SSH (22) 전체 개방**: ${OPEN_SSH}개 $([ $OPEN_SSH -gt 0 ] && echo "⚠️ 위험" || echo "✅ 안전")
- **RDP (3389) 전체 개방**: ${OPEN_RDP}개 $([ $OPEN_RDP -gt 0 ] && echo "⚠️ 위험" || echo "✅ 안전")
- **HTTP (80) 전체 개방**: ${OPEN_HTTP}개 $([ $OPEN_HTTP -gt 0 ] && echo "ℹ️ 확인 필요" || echo "✅ 안전")
- **HTTPS (443) 전체 개방**: ${OPEN_HTTPS}개 $([ $OPEN_HTTPS -gt 0 ] && echo "ℹ️ 확인 필요" || echo "✅ 안전")

**보안 권장사항**:
$([ $OPEN_SSH -gt 0 ] && echo "🚨 **긴급**: SSH 포트 전체 개방 보안 그룹 ${OPEN_SSH}개 - 즉시 제한 필요")
$([ $OPEN_RDP -gt 0 ] && echo "🚨 **긴급**: RDP 포트 전체 개방 보안 그룹 ${OPEN_RDP}개 - 즉시 제한 필요")
$([ $UNUSED_SG -gt 0 ] && echo "🧹 **정리**: 미사용 보안 그룹 ${UNUSED_SG}개 정리 권장")
- 🔒 최소 권한 원칙에 따른 포트 및 소스 IP 제한
- 📊 정기적인 보안 그룹 규칙 검토 및 감사

MDEOF
else
    echo "❌ 보안 그룹 데이터를 찾을 수 없습니다." >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

---

## 🔍 위협 탐지 및 모니터링

### GuardDuty 위협 탐지
MDEOF

# GuardDuty 분석
if [ -f "security_guardduty_detectors.json" ] && [ -s "security_guardduty_detectors.json" ]; then
    GUARDDUTY_COUNT=$(jq '.rows | length' security_guardduty_detectors.json)
    
    if [ $GUARDDUTY_COUNT -gt 0 ]; then
        GUARDDUTY_STATUS=$(jq -r '.rows[0].status' security_guardduty_detectors.json)
        
        cat >> 06-security-analysis.md << MDEOF

**📈 GuardDuty 현황**
- **탐지기 수**: ${GUARDDUTY_COUNT}개
- **상태**: $([ "$GUARDDUTY_STATUS" = "ENABLED" ] && echo "✅ 활성화" || echo "❌ 비활성화")

#### 📋 GuardDuty 탐지기 상세

| 탐지기 ID | 상태 | 생성일 | 업데이트일 | 발견사항 게시 빈도 |
|-----------|------|--------|------------|-------------------|
MDEOF
        
        jq -r '.rows[] | "| \(.detector_id) | \(.status) | \(.created_at // "N/A") | \(.updated_at // "N/A") | \(.finding_publishing_frequency // "N/A") |"' security_guardduty_detectors.json >> 06-security-analysis.md
        
        cat >> 06-security-analysis.md << MDEOF

**보안 권장사항**:
$([ "$GUARDDUTY_STATUS" = "ENABLED" ] && echo "✅ GuardDuty 활성화됨 - 지속적인 모니터링 중" || echo "⚠️ GuardDuty 비활성화 - 활성화 권장")
- 📊 정기적인 GuardDuty 발견사항 검토 및 대응
- 🔔 중요 위협에 대한 알림 설정 권장

MDEOF
    else
        echo "**GuardDuty 상태**: ❌ 비활성화" >> 06-security-analysis.md
        echo "" >> 06-security-analysis.md
        echo "**보안 권장사항**:" >> 06-security-analysis.md
        echo "🚨 **긴급**: GuardDuty 활성화하여 지능형 위협 탐지 기능 활용 권장" >> 06-security-analysis.md
    fi
else
    echo "**GuardDuty 상태**: ❌ 데이터 없음" >> 06-security-analysis.md
    echo "" >> 06-security-analysis.md
    echo "**보안 권장사항**:" >> 06-security-analysis.md
    echo "🚨 **긴급**: GuardDuty 서비스 활성화 및 구성 필요" >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

### Security Hub 중앙 보안 관리
MDEOF

# Security Hub 분석
if [ -f "security_securityhub_hub.json" ] && [ -s "security_securityhub_hub.json" ]; then
    SECURITYHUB_COUNT=$(jq '.rows | length' security_securityhub_hub.json)
    
    if [ $SECURITYHUB_COUNT -gt 0 ]; then
        cat >> 06-security-analysis.md << MDEOF

**📈 Security Hub 현황**
- **허브 수**: ${SECURITYHUB_COUNT}개
- **상태**: ✅ 활성화

#### 📋 Security Hub 상세

| 허브 ARN | 구독일 | 자동 제어 활성화 |
|----------|--------|------------------|
MDEOF
        
        jq -r '.rows[] | "| \(.hub_arn) | \(.subscribed_at // "N/A") | \(if .auto_enable_controls then "✅" else "❌" end) |"' security_securityhub_hub.json >> 06-security-analysis.md
        
        cat >> 06-security-analysis.md << MDEOF

**보안 권장사항**:
- ✅ Security Hub 활성화됨 - 중앙 집중식 보안 관리 가능
- 📊 정기적인 보안 표준 준수 상태 검토
- 🔔 중요 보안 발견사항에 대한 알림 설정

MDEOF
    else
        echo "**Security Hub 상태**: ❌ 비활성화" >> 06-security-analysis.md
    fi
else
    echo "**Security Hub 상태**: ❌ 데이터 없음" >> 06-security-analysis.md
    echo "" >> 06-security-analysis.md
    echo "**보안 권장사항**:" >> 06-security-analysis.md
    echo "🚨 **권장**: Security Hub 활성화하여 중앙 집중식 보안 관리 구현" >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

---

## 📊 감사 및 규정 준수

### CloudTrail 감사 로깅
MDEOF

# CloudTrail 분석
if [ -f "security_cloudtrail_trails.json" ] && [ -s "security_cloudtrail_trails.json" ]; then
    CLOUDTRAIL_COUNT=$(jq '.rows | length' security_cloudtrail_trails.json)
    
    if [ $CLOUDTRAIL_COUNT -gt 0 ]; then
        MULTI_REGION_TRAILS=$(jq '[.rows[] | select(.is_multi_region_trail == true)] | length' security_cloudtrail_trails.json)
        LOG_VALIDATION_TRAILS=$(jq '[.rows[] | select(.log_file_validation_enabled == true)] | length' security_cloudtrail_trails.json)
        
        cat >> 06-security-analysis.md << MDEOF

**📈 CloudTrail 현황**
- **총 추적 수**: ${CLOUDTRAIL_COUNT}개
- **다중 리전 추적**: ${MULTI_REGION_TRAILS}개
- **로그 파일 검증 활성화**: ${LOG_VALIDATION_TRAILS}개

#### 📋 CloudTrail 추적 상세

| 추적명 | S3 버킷 | 다중 리전 | 로그 검증 | KMS 암호화 |
|--------|---------|-----------|-----------|------------|
MDEOF
        
        jq -r '.rows[] | "| \(.name) | \(.s3_bucket_name) | \(if .is_multi_region_trail then "✅" else "❌" end) | \(if .log_file_validation_enabled then "✅" else "❌" end) | \(if .kms_key_id then "✅" else "❌" end) |"' security_cloudtrail_trails.json >> 06-security-analysis.md
        
        cat >> 06-security-analysis.md << MDEOF

**보안 권장사항**:
$([ $MULTI_REGION_TRAILS -eq 0 ] && echo "⚠️ **권장**: 다중 리전 CloudTrail 구성으로 전체 계정 활동 추적")
$([ $LOG_VALIDATION_TRAILS -lt $CLOUDTRAIL_COUNT ] && echo "⚠️ **권장**: 모든 CloudTrail에서 로그 파일 검증 활성화")
- 🔒 CloudTrail 로그 KMS 암호화 적용
- 📊 CloudWatch Logs 통합으로 실시간 모니터링 구현

MDEOF
    else
        echo "**CloudTrail 상태**: ❌ 추적 없음" >> 06-security-analysis.md
    fi
else
    echo "**CloudTrail 상태**: ❌ 데이터 없음" >> 06-security-analysis.md
    echo "" >> 06-security-analysis.md
    echo "**보안 권장사항**:" >> 06-security-analysis.md
    echo "🚨 **긴급**: CloudTrail 활성화하여 API 호출 감사 로깅 구현 필요" >> 06-security-analysis.md
fi
cat >> 06-security-analysis.md << 'MDEOF'

---

## 📋 종합 보안 권장사항 및 개선 계획

### 🔴 높은 우선순위 (즉시 조치 필요)

#### 계정 보안 강화
MDEOF

# 긴급 보안 권장사항 생성
URGENT_RECOMMENDATIONS=""

# 계정 MFA 확인
if [ -f "security_iam_account_summary.json" ] && [ -s "security_iam_account_summary.json" ]; then
    ACCOUNT_MFA=$(jq -r '.rows[0].account_mfa_enabled' security_iam_account_summary.json)
    if [ "$ACCOUNT_MFA" = "false" ]; then
        URGENT_RECOMMENDATIONS="${URGENT_RECOMMENDATIONS}1. **루트 계정 MFA 활성화**: 루트 계정에 다중 인증 설정 즉시 필요\n"
    fi
fi

# 위험한 보안 그룹 확인
if [ -f "security_groups.json" ] && [ -s "security_groups.json" ]; then
    OPEN_SSH=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 22 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    OPEN_RDP=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 3389 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    
    if [ $OPEN_SSH -gt 0 ]; then
        URGENT_RECOMMENDATIONS="${URGENT_RECOMMENDATIONS}2. **SSH 포트 보안**: ${OPEN_SSH}개 보안 그룹에서 SSH(22) 포트 전체 개방 - 즉시 제한 필요\n"
    fi
    
    if [ $OPEN_RDP -gt 0 ]; then
        URGENT_RECOMMENDATIONS="${URGENT_RECOMMENDATIONS}3. **RDP 포트 보안**: ${OPEN_RDP}개 보안 그룹에서 RDP(3389) 포트 전체 개방 - 즉시 제한 필요\n"
    fi
fi

# KMS 키 순환 확인
if [ -f "security_kms_keys.json" ] && [ -s "security_kms_keys.json" ]; then
    CUSTOMER_KEYS=$(jq '[.rows[] | select(.key_manager == "CUSTOMER")] | length' security_kms_keys.json)
    ROTATION_ENABLED=$(jq '[.rows[] | select(.key_rotation_enabled == true)] | length' security_kms_keys.json)
    
    if [ $ROTATION_ENABLED -lt $CUSTOMER_KEYS ]; then
        URGENT_RECOMMENDATIONS="${URGENT_RECOMMENDATIONS}4. **KMS 키 순환**: $(($CUSTOMER_KEYS - $ROTATION_ENABLED))개 고객 관리형 키에서 자동 순환 비활성화 - 활성화 권장\n"
    fi
fi

if [ -n "$URGENT_RECOMMENDATIONS" ]; then
    echo -e "$URGENT_RECOMMENDATIONS" >> 06-security-analysis.md
else
    echo "✅ 긴급 조치가 필요한 보안 이슈가 발견되지 않았습니다." >> 06-security-analysis.md
fi

cat >> 06-security-analysis.md << 'MDEOF'

### 🟡 중간 우선순위 (1-3개월 내 조치)

#### 보안 모니터링 강화
1. **GuardDuty 활성화**: 지능형 위협 탐지를 위한 GuardDuty 서비스 활성화
2. **Security Hub 구성**: 중앙 집중식 보안 관리를 위한 Security Hub 활성화
3. **CloudTrail 다중 리전**: 전체 계정 활동 추적을 위한 다중 리전 CloudTrail 구성
4. **Config 규칙 설정**: 리소스 구성 변경 모니터링 및 규정 준수 확인

#### IAM 권한 최적화
1. **미사용 역할 정리**: 장기간 사용되지 않은 IAM 역할 검토 및 정리
2. **권한 경계 설정**: 중요 역할에 대한 권한 경계(Permission Boundary) 적용
3. **액세스 분석기**: IAM Access Analyzer를 통한 외부 액세스 검토
4. **정기 권한 검토**: 분기별 IAM 권한 및 정책 검토 프로세스 수립

### 🟢 낮은 우선순위 (장기 계획)

#### 고급 보안 기능
1. **AWS SSO 도입**: 중앙 집중식 사용자 관리 및 Single Sign-On 구현
2. **Secrets Manager 활용**: 하드코딩된 자격 증명을 Secrets Manager로 이전
3. **Parameter Store 암호화**: SSM Parameter Store의 민감한 데이터 암호화
4. **VPC Flow Logs**: 네트워크 트래픽 분석을 위한 VPC Flow Logs 활성화

#### 규정 준수 및 거버넌스
1. **AWS Config 규칙**: 조직 정책에 맞는 Config 규칙 설정
2. **AWS Organizations**: 다중 계정 환경에서의 중앙 집중식 관리
3. **Service Control Policies**: 계정별 서비스 사용 제한 정책 적용
4. **정기 보안 감사**: 월간/분기별 보안 상태 점검 및 개선

---

## 📊 보안 점수 및 평가

### 보안 성숙도 평가
MDEOF

# 보안 점수 계산
SECURITY_SCORE=0
MAX_SCORE=100

# IAM 보안 점수 (30점)
IAM_SCORE=0
if [ -f "security_iam_account_summary.json" ] && [ -s "security_iam_account_summary.json" ]; then
    ACCOUNT_MFA=$(jq -r '.rows[0].account_mfa_enabled' security_iam_account_summary.json)
    [ "$ACCOUNT_MFA" = "true" ] && IAM_SCORE=$((IAM_SCORE + 10))
    
    MFA_DEVICES=$(jq -r '.rows[0].mfa_devices' security_iam_account_summary.json)
    [ $MFA_DEVICES -gt 0 ] && IAM_SCORE=$((IAM_SCORE + 5))
    
    # IAM 역할 존재 여부
    if [ -f "security_iam_roles.json" ] && [ -s "security_iam_roles.json" ]; then
        TOTAL_ROLES=$(jq '.rows | length' security_iam_roles.json)
        [ $TOTAL_ROLES -gt 0 ] && IAM_SCORE=$((IAM_SCORE + 15))
    fi
fi

# KMS 보안 점수 (20점)
KMS_SCORE=0
if [ -f "security_kms_keys.json" ] && [ -s "security_kms_keys.json" ]; then
    CUSTOMER_KEYS=$(jq '[.rows[] | select(.key_manager == "CUSTOMER")] | length' security_kms_keys.json)
    [ $CUSTOMER_KEYS -gt 0 ] && KMS_SCORE=$((KMS_SCORE + 10))
    
    ROTATION_ENABLED=$(jq '[.rows[] | select(.key_rotation_enabled == true)] | length' security_kms_keys.json)
    [ $ROTATION_ENABLED -gt 0 ] && KMS_SCORE=$((KMS_SCORE + 10))
fi

# 네트워크 보안 점수 (25점)
NETWORK_SCORE=0
if [ -f "security_groups.json" ] && [ -s "security_groups.json" ]; then
    TOTAL_SG=$(jq '.rows | length' security_groups.json)
    [ $TOTAL_SG -gt 0 ] && NETWORK_SCORE=$((NETWORK_SCORE + 10))
    
    OPEN_SSH=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 22 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    OPEN_RDP=$(jq '[.rows[] | select(.ip_permissions[]? | select(.from_port == 3389 and (.ip_ranges[]?.cidr_ip == "0.0.0.0/0" or .ipv6_ranges[]?.cidr_ipv6 == "::/0")))] | length' security_groups.json)
    
    [ $OPEN_SSH -eq 0 ] && NETWORK_SCORE=$((NETWORK_SCORE + 8))
    [ $OPEN_RDP -eq 0 ] && NETWORK_SCORE=$((NETWORK_SCORE + 7))
fi

# 모니터링 보안 점수 (25점)
MONITORING_SCORE=0
if [ -f "security_guardduty_detectors.json" ] && [ -s "security_guardduty_detectors.json" ]; then
    GUARDDUTY_COUNT=$(jq '.rows | length' security_guardduty_detectors.json)
    [ $GUARDDUTY_COUNT -gt 0 ] && MONITORING_SCORE=$((MONITORING_SCORE + 10))
fi

if [ -f "security_securityhub_hub.json" ] && [ -s "security_securityhub_hub.json" ]; then
    SECURITYHUB_COUNT=$(jq '.rows | length' security_securityhub_hub.json)
    [ $SECURITYHUB_COUNT -gt 0 ] && MONITORING_SCORE=$((MONITORING_SCORE + 10))
fi

if [ -f "security_cloudtrail_trails.json" ] && [ -s "security_cloudtrail_trails.json" ]; then
    CLOUDTRAIL_COUNT=$(jq '.rows | length' security_cloudtrail_trails.json)
    [ $CLOUDTRAIL_COUNT -gt 0 ] && MONITORING_SCORE=$((MONITORING_SCORE + 5))
fi

SECURITY_SCORE=$((IAM_SCORE + KMS_SCORE + NETWORK_SCORE + MONITORING_SCORE))

cat >> 06-security-analysis.md << MDEOF

**🎯 전체 보안 점수: ${SECURITY_SCORE}/${MAX_SCORE}점**

| 영역 | 점수 | 만점 | 평가 |
|------|------|------|------|
| 🔐 IAM 보안 | ${IAM_SCORE} | 30 | $([ $IAM_SCORE -ge 25 ] && echo "우수" || [ $IAM_SCORE -ge 15 ] && echo "보통" || echo "개선 필요") |
| 🔑 KMS 암호화 | ${KMS_SCORE} | 20 | $([ $KMS_SCORE -ge 15 ] && echo "우수" || [ $KMS_SCORE -ge 10 ] && echo "보통" || echo "개선 필요") |
| 🛡️ 네트워크 보안 | ${NETWORK_SCORE} | 25 | $([ $NETWORK_SCORE -ge 20 ] && echo "우수" || [ $NETWORK_SCORE -ge 15 ] && echo "보통" || echo "개선 필요") |
| 📊 보안 모니터링 | ${MONITORING_SCORE} | 25 | $([ $MONITORING_SCORE -ge 20 ] && echo "우수" || [ $MONITORING_SCORE -ge 10 ] && echo "보통" || echo "개선 필요") |

### 보안 성숙도 등급
$([ $SECURITY_SCORE -ge 80 ] && echo "🏆 **우수 (A등급)**: 높은 수준의 보안 태세 유지" || [ $SECURITY_SCORE -ge 60 ] && echo "✅ **양호 (B등급)**: 기본적인 보안 요구사항 충족, 일부 개선 필요" || [ $SECURITY_SCORE -ge 40 ] && echo "⚠️ **보통 (C등급)**: 중요한 보안 개선 사항 존재" || echo "🚨 **미흡 (D등급)**: 즉시 보안 강화 조치 필요")

---

## 💰 보안 투자 우선순위

### 비용 대비 효과 분석
1. **무료 보안 강화** (즉시 적용 가능)
   - 루트 계정 MFA 활성화
   - 보안 그룹 규칙 최적화
   - IAM 정책 최소 권한 적용
   - KMS 키 자동 순환 활성화

2. **저비용 고효과** (월 $10-50)
   - GuardDuty 활성화
   - Security Hub 기본 구성
   - CloudTrail 로그 파일 검증

3. **중간 비용** (월 $50-200)
   - Config 규칙 설정
   - VPC Flow Logs 활성화
   - Secrets Manager 도입

4. **고비용 장기 투자** (월 $200+)
   - AWS SSO 구현
   - 다중 계정 거버넌스
   - 고급 보안 모니터링

---

*📅 분석 완료 시간: CURRENT_DATE_PLACEHOLDER*  
*🔄 다음 보안 검토 권장 주기: 월 1회*  
*📊 보안 점수 목표: 80점 이상 (A등급)*

---
MDEOF

echo "✅ Security Analysis 생성 완료: 06-security-analysis.md"
