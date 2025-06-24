#!/bin/bash
# Networking Analysis 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "🌐 Networking Analysis 보고서 생성 중..."

cat > 02-networking-analysis.md << 'MDEOF'
# 네트워킹 리소스 분석

## 📊 네트워킹 개요

### VPC 구성 현황
MDEOF

# VPC 데이터가 있는 경우 테이블 생성
if [ -f "networking_vpc.json" ] && [ -s "networking_vpc.json" ]; then
    VPC_COUNT=$(jq '.rows | length' networking_vpc.json)
    DEFAULT_VPC_COUNT=$(jq '[.rows[] | select(.is_default == true)] | length' networking_vpc.json)
    echo "**총 VPC 수:** ${VPC_COUNT}개 (기본 VPC: ${DEFAULT_VPC_COUNT}개)" >> 02-networking-analysis.md
    echo "" >> 02-networking-analysis.md
    echo "| VPC ID | CIDR Block | 상태 | 기본 VPC | 태그 |" >> 02-networking-analysis.md
    echo "|--------|------------|------|----------|------|" >> 02-networking-analysis.md
    jq -r '.rows[] | "| \(.vpc_id) | \(.cidr_block) | \(.state) | \(.is_default) | \(.tags.Name // "N/A") |"' networking_vpc.json >> 02-networking-analysis.md
else
    echo "VPC 데이터를 찾을 수 없습니다." >> 02-networking-analysis.md
fi

cat >> 02-networking-analysis.md << 'MDEOF'

## 🔒 보안 그룹 분석

### 보안 그룹 현황
MDEOF

# 보안 그룹 데이터가 있는 경우 요약 정보 생성
if [ -f "security_groups.json" ] && [ -s "security_groups.json" ]; then
    SG_COUNT=$(jq '.rows | length' security_groups.json)
    echo "**총 보안 그룹 수:** ${SG_COUNT}개" >> 02-networking-analysis.md
    echo "" >> 02-networking-analysis.md
    echo "| 그룹 ID | 그룹명 | VPC ID | 설명 |" >> 02-networking-analysis.md
    echo "|---------|--------|--------|------|" >> 02-networking-analysis.md
    jq -r '.rows[] | "| \(.group_id) | \(.group_name // "N/A") | \(.vpc_id) | \(.description // "설명 없음") |"' security_groups.json | head -10 >> 02-networking-analysis.md
    if [ $SG_COUNT -gt 10 ]; then
        echo "*(상위 10개만 표시, 총 ${SG_COUNT}개)*" >> 02-networking-analysis.md
    fi
    
    # VPC별 보안 그룹 분포
    echo "" >> 02-networking-analysis.md
    echo "### VPC별 보안 그룹 분포" >> 02-networking-analysis.md
    echo "| VPC ID | 보안 그룹 수 |" >> 02-networking-analysis.md
    echo "|--------|--------------|" >> 02-networking-analysis.md
    jq -r '.rows | group_by(.vpc_id) | .[] | "| \(.[0].vpc_id) | \(length) |"' security_groups.json >> 02-networking-analysis.md
else
    echo "보안 그룹 데이터를 찾을 수 없습니다." >> 02-networking-analysis.md
fi

cat >> 02-networking-analysis.md << 'MDEOF'

## 🌐 라우팅 테이블 분석

### 라우팅 테이블 현황
MDEOF

# 라우팅 테이블 데이터가 있는 경우
if [ -f "networking_route_tables.json" ] && [ -s "networking_route_tables.json" ]; then
    RT_COUNT=$(jq '.rows | length' networking_route_tables.json)
    MAIN_RT_COUNT=$(jq '[.rows[] | select(.main == true)] | length' networking_route_tables.json)
    echo "**총 라우팅 테이블 수:** ${RT_COUNT}개 (메인 테이블: ${MAIN_RT_COUNT}개)" >> 02-networking-analysis.md
    echo "" >> 02-networking-analysis.md
    echo "| 라우팅 테이블 ID | VPC ID | 메인 테이블 | 연결된 서브넷 수 |" >> 02-networking-analysis.md
    echo "|------------------|--------|-------------|------------------|" >> 02-networking-analysis.md
    jq -r '.rows[] | "| \(.route_table_id) | \(.vpc_id) | \(.main) | \(.associations | length) |"' networking_route_tables.json | head -10 >> 02-networking-analysis.md
else
    echo "라우팅 테이블 데이터를 찾을 수 없습니다." >> 02-networking-analysis.md
fi

cat >> 02-networking-analysis.md << 'MDEOF'

## 🔌 네트워크 게이트웨이

### 인터넷 게이트웨이
MDEOF

# 인터넷 게이트웨이 데이터가 있는 경우
if [ -f "networking_igw.json" ] && [ -s "networking_igw.json" ]; then
    IGW_COUNT=$(jq '.rows | length' networking_igw.json)
    echo "**총 인터넷 게이트웨이 수:** ${IGW_COUNT}개" >> 02-networking-analysis.md
    echo "" >> 02-networking-analysis.md
    echo "| IGW ID | 상태 | 연결된 VPC |" >> 02-networking-analysis.md
    echo "|--------|------|------------|" >> 02-networking-analysis.md
    jq -r '.rows[] | "| \(.internet_gateway_id) | \(.state) | \(.attachments[0].vpc_id // "없음") |"' networking_igw.json >> 02-networking-analysis.md
else
    echo "인터넷 게이트웨이 데이터를 찾을 수 없습니다." >> 02-networking-analysis.md
fi

cat >> 02-networking-analysis.md << 'MDEOF'

### Elastic IP 주소
MDEOF

# Elastic IP 데이터 분석
if [ -f "networking_eip.json" ] && [ -s "networking_eip.json" ]; then
    EIP_COUNT=$(jq '.rows | length' networking_eip.json)
    ASSOCIATED_EIP=$(jq '[.rows[] | select(.association_id != null)] | length' networking_eip.json)
    echo "**총 Elastic IP:** ${EIP_COUNT}개 (연결됨: ${ASSOCIATED_EIP}개)" >> 02-networking-analysis.md
    echo "" >> 02-networking-analysis.md
    echo "| 할당 ID | 공인 IP | 연결된 인스턴스 | 도메인 |" >> 02-networking-analysis.md
    echo "|---------|---------|-----------------|--------|" >> 02-networking-analysis.md
    jq -r '.rows[] | "| \(.allocation_id) | \(.public_ip) | \(.instance_id // "없음") | \(.domain) |"' networking_eip.json >> 02-networking-analysis.md
else
    echo "Elastic IP 데이터를 찾을 수 없습니다." >> 02-networking-analysis.md
fi

cat >> 02-networking-analysis.md << 'MDEOF'

## 🛡️ 네트워크 ACL 분석

### Network ACL 현황
MDEOF

# Network ACL 데이터 분석
if [ -f "networking_acl.json" ] && [ -s "networking_acl.json" ]; then
    ACL_COUNT=$(jq '.rows | length' networking_acl.json)
    DEFAULT_ACL_COUNT=$(jq '[.rows[] | select(.is_default == true)] | length' networking_acl.json)
    echo "**총 Network ACL:** ${ACL_COUNT}개 (기본 ACL: ${DEFAULT_ACL_COUNT}개)" >> 02-networking-analysis.md
    echo "" >> 02-networking-analysis.md
    echo "| ACL ID | VPC ID | 기본 ACL | 연결된 서브넷 수 |" >> 02-networking-analysis.md
    echo "|--------|--------|----------|------------------|" >> 02-networking-analysis.md
    jq -r '.rows[] | "| \(.network_acl_id) | \(.vpc_id) | \(.is_default) | \(.associations | length) |"' networking_acl.json | head -5 >> 02-networking-analysis.md
else
    echo "Network ACL 데이터를 찾을 수 없습니다." >> 02-networking-analysis.md
fi

cat >> 02-networking-analysis.md << 'MDEOF'

## 📋 네트워킹 권장사항

### 🔴 높은 우선순위
1. **보안 그룹 규칙 검토**: 0.0.0.0/0 허용 규칙 최소화
2. **VPC Flow Logs 활성화**: 네트워크 트래픽 모니터링 강화
3. **미사용 Elastic IP 정리**: 연결되지 않은 EIP 해제

### 🟡 중간 우선순위
1. **VPC 엔드포인트 구성**: AWS 서비스 접근 최적화
2. **서브넷 구성 최적화**: 퍼블릭/프라이빗 서브넷 적절한 분리
3. **라우팅 테이블 정리**: 불필요한 라우팅 규칙 제거

### 🟢 낮은 우선순위
1. **Transit Gateway 검토**: 복잡한 네트워크 연결 시 고려
2. **VPC 피어링 최적화**: 불필요한 피어링 연결 정리
3. **DNS 설정 최적화**: Route 53 Private Hosted Zone 활용

## 📊 네트워킹 보안 점검

### 보안 그룹 분석 결과
MDEOF

# 보안 그룹 보안 분석
if [ -f "security_groups.json" ] && [ -s "security_groups.json" ]; then
    # 0.0.0.0/0 허용 규칙 확인
    OPEN_RULES=$(jq '[.rows[] | select(.ip_permissions[]?.ip_ranges[]?.cidr_ip == "0.0.0.0/0")] | length' security_groups.json 2>/dev/null || echo "0")
    echo "- **전체 오픈 규칙 (0.0.0.0/0)**: ${OPEN_RULES}개 보안 그룹에서 발견" >> 02-networking-analysis.md
    
    # SSH 포트 22 오픈 확인
    SSH_OPEN=$(jq '[.rows[] | select(.ip_permissions[]? | .from_port == 22 and .ip_ranges[]?.cidr_ip == "0.0.0.0/0")] | length' security_groups.json 2>/dev/null || echo "0")
    echo "- **SSH 포트 22 전체 오픈**: ${SSH_OPEN}개 보안 그룹" >> 02-networking-analysis.md
    
    # RDP 포트 3389 오픈 확인
    RDP_OPEN=$(jq '[.rows[] | select(.ip_permissions[]? | .from_port == 3389 and .ip_ranges[]?.cidr_ip == "0.0.0.0/0")] | length' security_groups.json 2>/dev/null || echo "0")
    echo "- **RDP 포트 3389 전체 오픈**: ${RDP_OPEN}개 보안 그룹" >> 02-networking-analysis.md
else
    echo "- 보안 그룹 데이터 분석 불가" >> 02-networking-analysis.md
fi

cat >> 02-networking-analysis.md << 'MDEOF'

## 💰 네트워킹 비용 최적화

### 비용 절감 기회
MDEOF

# 비용 최적화 분석
if [ -f "networking_eip.json" ] && [ -s "networking_eip.json" ]; then
    UNASSOCIATED_EIP=$(jq '[.rows[] | select(.association_id == null)] | length' networking_eip.json)
    if [ $UNASSOCIATED_EIP -gt 0 ]; then
        echo "1. **미사용 Elastic IP**: ${UNASSOCIATED_EIP}개 (월 $$(echo \"$UNASSOCIATED_EIP * 3.6\" | bc -l 2>/dev/null || echo \"N/A\") 절감 가능)" >> 02-networking-analysis.md
    fi
fi

cat >> 02-networking-analysis.md << 'MDEOF'
2. **NAT Gateway 최적화**: 불필요한 NAT Gateway 제거 검토
3. **데이터 전송 비용**: 같은 AZ 내 통신 최대화

---
*네트워킹 분석 완료*
MDEOF

echo "✅ Networking Analysis 생성 완료: 02-networking-analysis.md"
