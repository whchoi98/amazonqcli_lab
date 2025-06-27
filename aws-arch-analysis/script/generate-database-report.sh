#!/bin/bash
# Database Analysis 보고서 생성 스크립트 (Enhanced Version)

REPORT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"
cd $REPORT_DIR

echo "🗄️ Enhanced Database Analysis 보고서 생성 중..."

# 현재 날짜 및 시간
CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cat > 05-database-analysis.md << 'MDEOF'
# 🗄️ 데이터베이스 리소스 종합 분석

> **분석 일시**: CURRENT_DATE_PLACEHOLDER  
> **분석 대상**: AWS 계정 내 모든 데이터베이스 서비스  
> **분석 리전**: ap-northeast-2 (서울)

## 📊 Executive Summary

### 데이터베이스 서비스 현황 개요
MDEOF

# 현재 날짜 삽입
sed -i "s/CURRENT_DATE_PLACEHOLDER/$CURRENT_DATE/g" 05-database-analysis.md

# Executive Summary 생성
TOTAL_SERVICES=0
ACTIVE_SERVICES=0

# 서비스별 카운트 초기화
RDS_INSTANCES=0
RDS_CLUSTERS=0
ELASTICACHE_CLUSTERS=0
OPENSEARCH_DOMAINS=0
ATHENA_WORKGROUPS=0

# RDS 인스턴스 카운트
if [ -f "database_rds_instances.json" ] && [ -s "database_rds_instances.json" ]; then
    RDS_INSTANCES=$(jq '.rows | length' database_rds_instances.json)
    if [ $RDS_INSTANCES -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

# RDS 클러스터 카운트
if [ -f "database_rds_clusters.json" ] && [ -s "database_rds_clusters.json" ]; then
    RDS_CLUSTERS=$(jq '.rows | length' database_rds_clusters.json)
    if [ $RDS_CLUSTERS -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

# ElastiCache 클러스터 카운트
if [ -f "database_elasticache_clusters.json" ] && [ -s "database_elasticache_clusters.json" ]; then
    ELASTICACHE_CLUSTERS=$(jq '.rows | length' database_elasticache_clusters.json)
    if [ $ELASTICACHE_CLUSTERS -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

# OpenSearch 도메인 카운트
if [ -f "database_opensearch_domains.json" ] && [ -s "database_opensearch_domains.json" ]; then
    OPENSEARCH_DOMAINS=$(jq '.rows | length' database_opensearch_domains.json)
    if [ $OPENSEARCH_DOMAINS -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

# Athena 워크그룹 카운트
if [ -f "database_athena_workgroups.json" ] && [ -s "database_athena_workgroups.json" ]; then
    ATHENA_WORKGROUPS=$(jq '.rows | length' database_athena_workgroups.json)
    if [ $ATHENA_WORKGROUPS -gt 0 ]; then
        ACTIVE_SERVICES=$((ACTIVE_SERVICES + 1))
    fi
fi

TOTAL_SERVICES=5  # RDS, ElastiCache, OpenSearch, Athena, DynamoDB

# Executive Summary 작성
cat >> 05-database-analysis.md << MDEOF

| 서비스 | 리소스 수 | 상태 |
|--------|-----------|------|
| 🏛️ RDS 인스턴스 | ${RDS_INSTANCES}개 | $([ $RDS_INSTANCES -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 🏛️ RDS 클러스터 (Aurora) | ${RDS_CLUSTERS}개 | $([ $RDS_CLUSTERS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| ⚡ ElastiCache 클러스터 | ${ELASTICACHE_CLUSTERS}개 | $([ $ELASTICACHE_CLUSTERS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 🔍 OpenSearch 도메인 | ${OPENSEARCH_DOMAINS}개 | $([ $OPENSEARCH_DOMAINS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |
| 📊 Athena 워크그룹 | ${ATHENA_WORKGROUPS}개 | $([ $ATHENA_WORKGROUPS -gt 0 ] && echo "✅ 활성" || echo "❌ 없음") |

**활성 데이터베이스 서비스**: ${ACTIVE_SERVICES}/${TOTAL_SERVICES}개

---

## 🏛️ Amazon RDS 상세 분석

### RDS 인스턴스 현황
MDEOF
# RDS 인스턴스 상세 분석
if [ -f "database_rds_instances.json" ] && [ -s "database_rds_instances.json" ]; then
    RDS_COUNT=$(jq '.rows | length' database_rds_instances.json)
    AVAILABLE_COUNT=$(jq '[.rows[] | select(.status == "available")] | length' database_rds_instances.json)
    ENCRYPTED_COUNT=$(jq '[.rows[] | select(.storage_encrypted == true)] | length' database_rds_instances.json)
    MULTI_AZ_COUNT=$(jq '[.rows[] | select(.multi_az == true)] | length' database_rds_instances.json)
    
    cat >> 05-database-analysis.md << MDEOF

**📈 RDS 인스턴스 통계**
- **총 인스턴스 수**: ${RDS_COUNT}개
- **사용 가능한 인스턴스**: ${AVAILABLE_COUNT}개 ($(echo "scale=1; $AVAILABLE_COUNT * 100 / $RDS_COUNT" | bc -l)%)
- **암호화된 인스턴스**: ${ENCRYPTED_COUNT}개 ($(echo "scale=1; $ENCRYPTED_COUNT * 100 / $RDS_COUNT" | bc -l)%)
- **Multi-AZ 구성**: ${MULTI_AZ_COUNT}개 ($(echo "scale=1; $MULTI_AZ_COUNT * 100 / $RDS_COUNT" | bc -l)%)

#### 📋 RDS 인스턴스 상세 목록

| DB 식별자 | 엔진 | 버전 | 클래스 | 스토리지 | 상태 | Multi-AZ | 암호화 | 공개 접근 |
|-----------|------|------|-------|----------|------|----------|--------|-----------|
MDEOF
    
    jq -r '.rows[] | "| \(.db_instance_identifier) | \(.engine) | \(.engine_version) | \(.class) | \(.allocated_storage)GB (\(.storage_type)) | \(.status) | \(if .multi_az then "✅" else "❌" end) | \(if .storage_encrypted then "🔒" else "🔓" end) | \(if .publicly_accessible then "🌐" else "🔒" end) |"' database_rds_instances.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

#### 🔧 엔진별 분포 및 버전 분석

| 엔진 | 개수 | 최신 버전 | 권장사항 |
|------|------|-----------|----------|
MDEOF
    
    # 엔진별 분석
    jq -r '.rows | group_by(.engine) | .[] | "\(.[0].engine)|\(length)|\(.[0].engine_version)|버전 업데이트 검토"' database_rds_instances.json | while IFS='|' read -r engine count version recommendation; do
        echo "| $engine | $count개 | $version | $recommendation |" >> 05-database-analysis.md
    done
    
    cat >> 05-database-analysis.md << MDEOF

#### 🔐 보안 설정 분석

**암호화 현황**:
- 저장 시 암호화: ${ENCRYPTED_COUNT}/${RDS_COUNT}개 인스턴스
- 권장사항: $([ $ENCRYPTED_COUNT -eq $RDS_COUNT ] && echo "✅ 모든 인스턴스가 암호화됨" || echo "⚠️ 암호화되지 않은 인스턴스 존재")

**네트워크 보안**:
MDEOF
    
    PUBLIC_COUNT=$(jq '[.rows[] | select(.publicly_accessible == true)] | length' database_rds_instances.json)
    echo "- 공개 접근 가능: ${PUBLIC_COUNT}/${RDS_COUNT}개 인스턴스" >> 05-database-analysis.md
    echo "- 권장사항: $([ $PUBLIC_COUNT -eq 0 ] && echo "✅ 모든 인스턴스가 비공개" || echo "⚠️ 공개 접근 가능한 인스턴스 검토 필요")" >> 05-database-analysis.md
    
else
    echo "❌ RDS 인스턴스 데이터를 찾을 수 없습니다." >> 05-database-analysis.md
fi

cat >> 05-database-analysis.md << 'MDEOF'

### RDS 클러스터 (Aurora) 분석
MDEOF

# RDS 클러스터 상세 분석
if [ -f "database_rds_clusters.json" ] && [ -s "database_rds_clusters.json" ]; then
    CLUSTER_COUNT=$(jq '.rows | length' database_rds_clusters.json)
    AVAILABLE_CLUSTERS=$(jq '[.rows[] | select(.status == "available")] | length' database_rds_clusters.json)
    ENCRYPTED_CLUSTERS=$(jq '[.rows[] | select(.storage_encrypted == true)] | length' database_rds_clusters.json)
    
    cat >> 05-database-analysis.md << MDEOF

**📈 Aurora 클러스터 통계**
- **총 클러스터 수**: ${CLUSTER_COUNT}개
- **사용 가능한 클러스터**: ${AVAILABLE_CLUSTERS}개
- **암호화된 클러스터**: ${ENCRYPTED_CLUSTERS}개 ($(echo "scale=1; $ENCRYPTED_CLUSTERS * 100 / $CLUSTER_COUNT" | bc -l)%)

#### 📋 Aurora 클러스터 상세 목록

| 클러스터 식별자 | 엔진 | 버전 | 상태 | 멤버 수 | 백업 보존 | 암호화 | 엔드포인트 |
|-----------------|------|------|------|---------|-----------|--------|------------|
MDEOF
    
    jq -r '.rows[] | "| \(.db_cluster_identifier) | \(.engine) | \(.engine_version) | \(.status) | \(.members | length) | \(.backup_retention_period)일 | \(if .storage_encrypted then "🔒" else "🔓" end) | \(.endpoint) |"' database_rds_clusters.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

#### 🔄 백업 및 복구 설정

**백업 보존 기간 분석**:
MDEOF
    
    # 백업 보존 기간별 분석
    jq -r '.rows | group_by(.backup_retention_period) | .[] | "- \(.[] | .backup_retention_period)일: \(length)개 클러스터"' database_rds_clusters.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

**백업 윈도우**:
MDEOF
    
    jq -r '.rows[] | "- \(.db_cluster_identifier): \(.preferred_backup_window) (유지보수: \(.preferred_maintenance_window))"' database_rds_clusters.json >> 05-database-analysis.md
    
else
    echo "❌ RDS 클러스터 데이터를 찾을 수 없습니다." >> 05-database-analysis.md
fi

cat >> 04-database-analysis.md << 'MDEOF'

## 🔄 DynamoDB 테이블 현황

### DynamoDB 개요
MDEOF

# DynamoDB 테이블 데이터 분석
if [ -f "database_dynamodb_tables.json" ] && [ -s "database_dynamodb_tables.json" ]; then
    DYNAMO_COUNT=$(jq '.rows | length' database_dynamodb_tables.json)
    echo "**총 DynamoDB 테이블:** ${DYNAMO_COUNT}개" >> 04-database-analysis.md
    echo "" >> 04-database-analysis.md
    echo "| 테이블명 | 상태 | 청구 모드 | 읽기 용량 | 쓰기 용량 |" >> 04-database-analysis.md
    echo "|----------|------|-----------|-----------|-----------|" >> 04-database-analysis.md
    jq -r '.rows[] | "| \(.table_name) | \(.table_status) | \(.billing_mode_summary.billing_mode // "N/A") | \(.provisioned_throughput.read_capacity_units // "N/A") | \(.provisioned_throughput.write_capacity_units // "N/A") |"' database_dynamodb_tables.json >> 04-database-analysis.md
else
    echo "DynamoDB 테이블 데이터를 찾을 수 없습니다." >> 04-database-analysis.md
fi

cat >> 05-database-analysis.md << 'MDEOF'

---

## ⚡ Amazon ElastiCache 상세 분석

### ElastiCache 클러스터 현황
MDEOF

# ElastiCache 클러스터 상세 분석
if [ -f "database_elasticache_clusters.json" ] && [ -s "database_elasticache_clusters.json" ]; then
    CACHE_COUNT=$(jq '.rows | length' database_elasticache_clusters.json)
    AVAILABLE_CACHE=$(jq '[.rows[] | select(.cache_cluster_status == "available")] | length' database_elasticache_clusters.json)
    
    cat >> 05-database-analysis.md << MDEOF

**📈 ElastiCache 클러스터 통계**
- **총 클러스터 수**: ${CACHE_COUNT}개
- **사용 가능한 클러스터**: ${AVAILABLE_CACHE}개
- **가용성**: $(echo "scale=1; $AVAILABLE_CACHE * 100 / $CACHE_COUNT" | bc -l)%

#### 📋 ElastiCache 클러스터 상세 목록

| 클러스터 ID | 엔진 | 버전 | 노드 타입 | 상태 | 노드 수 | AZ | 복제 그룹 |
|-------------|------|------|-----------|------|---------|----|-----------| 
MDEOF
    
    jq -r '.rows[] | "| \(.cache_cluster_id) | \(.engine) | \(.engine_version) | \(.cache_node_type) | \(.cache_cluster_status) | \(.num_cache_nodes) | \(.preferred_availability_zone // "N/A") | \(.replication_group_id // "없음") |"' database_elasticache_clusters.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

#### 🔧 엔진별 분포

| 엔진 | 클러스터 수 | 평균 노드 수 | 주요 노드 타입 |
|------|-------------|--------------|----------------|
MDEOF
    
    # 엔진별 통계
    jq -r '.rows | group_by(.engine) | .[] | "\(.[0].engine)|\(length)|\((map(.num_cache_nodes) | add) / length)|\(.[0].cache_node_type)"' database_elasticache_clusters.json | while IFS='|' read -r engine count avg_nodes node_type; do
        echo "| $engine | $count개 | $(printf "%.1f" $avg_nodes)개 | $node_type |" >> 05-database-analysis.md
    done
    
    cat >> 05-database-analysis.md << MDEOF

#### ⚙️ 유지보수 및 업그레이드 설정

**자동 마이너 버전 업그레이드**:
MDEOF
    
    AUTO_UPGRADE_COUNT=$(jq '[.rows[] | select(.auto_minor_version_upgrade == true)] | length' database_elasticache_clusters.json)
    echo "- 활성화된 클러스터: ${AUTO_UPGRADE_COUNT}/${CACHE_COUNT}개" >> 05-database-analysis.md
    echo "- 권장사항: $([ $AUTO_UPGRADE_COUNT -eq $CACHE_COUNT ] && echo "✅ 모든 클러스터에서 활성화됨" || echo "⚠️ 일부 클러스터에서 비활성화됨")" >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

**유지보수 윈도우**:
MDEOF
    
    jq -r '.rows[] | "- \(.cache_cluster_id): \(.preferred_maintenance_window)"' database_elasticache_clusters.json >> 05-database-analysis.md
    
else
    echo "❌ ElastiCache 클러스터 데이터를 찾을 수 없습니다." >> 05-database-analysis.md
fi

cat >> 05-database-analysis.md << 'MDEOF'

### ElastiCache 복제 그룹 분석
MDEOF

# ElastiCache 복제 그룹 분석
if [ -f "database_elasticache_replication_groups.json" ] && [ -s "database_elasticache_replication_groups.json" ]; then
    REPL_COUNT=$(jq '.rows | length' database_elasticache_replication_groups.json)
    AVAILABLE_REPL=$(jq '[.rows[] | select(.status == "available")] | length' database_elasticache_replication_groups.json)
    
    cat >> 05-database-analysis.md << MDEOF

**📈 복제 그룹 통계**
- **총 복제 그룹**: ${REPL_COUNT}개
- **사용 가능한 그룹**: ${AVAILABLE_REPL}개

#### 📋 복제 그룹 상세 목록

| 복제 그룹 ID | 설명 | 상태 | 노드 타입 | 멤버 수 | 자동 장애조치 | Multi-AZ |
|--------------|------|------|-----------|---------|---------------|----------|
MDEOF
    
    jq -r '.rows[] | "| \(.replication_group_id) | \(.description) | \(.status) | \(.cache_node_type // "N/A") | \(.member_clusters | length) | \(if .automatic_failover == "enabled" then "✅" else "❌" end) | \(if .multi_az == "enabled" then "✅" else "❌" end) |"' database_elasticache_replication_groups.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

#### 🔐 보안 및 암호화 설정

**전송 중 암호화**:
MDEOF
    
    TRANSIT_ENCRYPTED=$(jq '[.rows[] | select(.transit_encryption_enabled == true)] | length' database_elasticache_replication_groups.json)
    echo "- 활성화된 그룹: ${TRANSIT_ENCRYPTED}/${REPL_COUNT}개" >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

**저장 시 암호화**:
MDEOF
    
    REST_ENCRYPTED=$(jq '[.rows[] | select(.at_rest_encryption_enabled == true)] | length' database_elasticache_replication_groups.json)
    echo "- 활성화된 그룹: ${REST_ENCRYPTED}/${REPL_COUNT}개" >> 05-database-analysis.md
    
else
    echo "❌ ElastiCache 복제 그룹 데이터를 찾을 수 없습니다." >> 05-database-analysis.md
fi

cat >> 05-database-analysis.md << 'MDEOF'

---

## 🔍 Amazon OpenSearch 상세 분석

### OpenSearch 도메인 현황
MDEOF

# OpenSearch 도메인 분석
if [ -f "database_opensearch_domains.json" ] && [ -s "database_opensearch_domains.json" ]; then
    OPENSEARCH_COUNT=$(jq '.rows | length' database_opensearch_domains.json)
    PROCESSING_COUNT=$(jq '[.rows[] | select(.processing == true)] | length' database_opensearch_domains.json)
    
    cat >> 05-database-analysis.md << MDEOF

**📈 OpenSearch 도메인 통계**
- **총 도메인 수**: ${OPENSEARCH_COUNT}개
- **처리 중인 도메인**: ${PROCESSING_COUNT}개

#### 📋 OpenSearch 도메인 상세 목록

| 도메인명 | 엔진 버전 | 엔드포인트 | 처리 상태 | 생성일 | 삭제일 |
|----------|-----------|------------|-----------|--------|--------|
MDEOF
    
    jq -r '.rows[] | "| \(.domain_name) | \(.engine_version) | \(.endpoint // "N/A") | \(if .processing then "🔄 처리중" else "✅ 완료" end) | \(.created // "N/A") | \(.deleted // "N/A") |"' database_opensearch_domains.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

#### ⚙️ 클러스터 구성 분석

**인스턴스 구성**:
MDEOF
    
    jq -r '.rows[] | "- **\(.domain_name)**: \(.cluster_config.instance_type // "N/A") (\(.cluster_config.instance_count // 0)개 인스턴스)"' database_opensearch_domains.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

#### 🔐 보안 및 네트워크 설정

**VPC 구성**:
MDEOF
    
    jq -r '.rows[] | if .vpc_options then "- **\(.domain_name)**: VPC 내부 배치 (서브넷: \(.vpc_options.subnet_ids | length)개)" else "- **\(.domain_name)**: 퍼블릭 액세스" end' database_opensearch_domains.json >> 05-database-analysis.md
    
    cat >> 05-database-analysis.md << MDEOF

**저장 시 암호화**:
MDEOF
    
    jq -r '.rows[] | "- **\(.domain_name)**: \(if .encryption_at_rest_options.enabled then "🔒 활성화" else "🔓 비활성화" end)"' database_opensearch_domains.json >> 05-database-analysis.md
    
else
    echo "❌ OpenSearch 도메인 데이터를 찾을 수 없습니다." >> 05-database-analysis.md
fi

cat >> 05-database-analysis.md << 'MDEOF'

---

## 📊 Amazon Athena 분석

### Athena 워크그룹 현황
MDEOF

# Athena 워크그룹 분석
if [ -f "database_athena_workgroups.json" ] && [ -s "database_athena_workgroups.json" ]; then
    ATHENA_COUNT=$(jq '.rows | length' database_athena_workgroups.json)
    ENABLED_COUNT=$(jq '[.rows[] | select(.state == "ENABLED")] | length' database_athena_workgroups.json)
    
    cat >> 05-database-analysis.md << MDEOF

**📈 Athena 워크그룹 통계**
- **총 워크그룹 수**: ${ATHENA_COUNT}개
- **활성화된 워크그룹**: ${ENABLED_COUNT}개

#### 📋 Athena 워크그룹 상세 목록

| 워크그룹명 | 설명 | 상태 | 생성일 | 출력 위치 | 암호화 |
|------------|------|------|--------|-----------|--------|
MDEOF
    
    jq -r '.rows[] | "| \(.name) | \(.description // "N/A") | \(.state) | \(.creation_time // "N/A") | \(.output_location // "N/A") | \(.encryption_option // "없음") |"' database_athena_workgroups.json >> 05-database-analysis.md
    
else
    echo "❌ Athena 워크그룹 데이터를 찾을 수 없습니다." >> 05-database-analysis.md
fi

cat >> 05-database-analysis.md << 'MDEOF'

---

## 📋 종합 권장사항 및 개선 계획

### 🔴 높은 우선순위 (즉시 조치 필요)

#### 보안 강화
MDEOF

# 보안 권장사항 생성
if [ -f "database_rds_instances.json" ] && [ -s "database_rds_instances.json" ]; then
    UNENCRYPTED_RDS=$(jq '[.rows[] | select(.storage_encrypted == false)] | length' database_rds_instances.json)
    PUBLIC_RDS=$(jq '[.rows[] | select(.publicly_accessible == true)] | length' database_rds_instances.json)
    
    if [ $UNENCRYPTED_RDS -gt 0 ]; then
        echo "1. **RDS 암호화 미적용**: ${UNENCRYPTED_RDS}개 인스턴스에 저장 시 암호화 적용 필요" >> 05-database-analysis.md
    fi
    
    if [ $PUBLIC_RDS -gt 0 ]; then
        echo "2. **RDS 공개 접근**: ${PUBLIC_RDS}개 인스턴스의 공개 접근 설정 검토 및 제한 필요" >> 05-database-analysis.md
    fi
fi

if [ -f "database_elasticache_replication_groups.json" ] && [ -s "database_elasticache_replication_groups.json" ]; then
    UNENCRYPTED_CACHE=$(jq '[.rows[] | select(.at_rest_encryption_enabled == false or .transit_encryption_enabled == false)] | length' database_elasticache_replication_groups.json)
    
    if [ $UNENCRYPTED_CACHE -gt 0 ]; then
        echo "3. **ElastiCache 암호화**: ${UNENCRYPTED_CACHE}개 복제 그룹에 전송/저장 암호화 적용 필요" >> 05-database-analysis.md
    fi
fi

cat >> 05-database-analysis.md << 'MDEOF'

#### 고가용성 구성
MDEOF

if [ -f "database_rds_instances.json" ] && [ -s "database_rds_instances.json" ]; then
    NON_MULTI_AZ=$(jq '[.rows[] | select(.multi_az == false)] | length' database_rds_instances.json)
    
    if [ $NON_MULTI_AZ -gt 0 ]; then
        echo "1. **Multi-AZ 미구성**: ${NON_MULTI_AZ}개 RDS 인스턴스에 Multi-AZ 구성 검토" >> 05-database-analysis.md
    fi
fi

if [ -f "database_elasticache_replication_groups.json" ] && [ -s "database_elasticache_replication_groups.json" ]; then
    NON_FAILOVER_CACHE=$(jq '[.rows[] | select(.automatic_failover != "enabled")] | length' database_elasticache_replication_groups.json)
    
    if [ $NON_FAILOVER_CACHE -gt 0 ]; then
        echo "2. **ElastiCache 자동 장애조치**: ${NON_FAILOVER_CACHE}개 복제 그룹에 자동 장애조치 활성화 필요" >> 05-database-analysis.md
    fi
fi

cat >> 05-database-analysis.md << 'MDEOF'

### 🟡 중간 우선순위 (1-3개월 내 조치)

#### 성능 최적화
1. **Performance Insights 활성화**: RDS 인스턴스 성능 모니터링 강화
2. **ElastiCache 노드 타입 최적화**: 워크로드에 맞는 인스턴스 타입 검토
3. **OpenSearch 클러스터 크기 조정**: 사용 패턴 기반 최적화

#### 백업 및 복구
1. **백업 보존 기간 표준화**: 비즈니스 요구사항에 맞는 백업 정책 수립
2. **Point-in-Time Recovery 테스트**: 정기적인 복구 테스트 수행
3. **Cross-Region 백업**: 재해 복구를 위한 다중 리전 백업 고려

### 🟢 낮은 우선순위 (장기 계획)

#### 비용 최적화
1. **Reserved Instance 활용**: 장기 실행 데이터베이스 비용 절감
2. **Aurora Serverless 검토**: 가변 워크로드에 대한 서버리스 옵션 평가
3. **스토리지 타입 최적화**: gp3 스토리지 활용 검토

#### 현대화 및 마이그레이션
1. **Aurora 마이그레이션**: 기존 RDS를 Aurora로 마이그레이션 검토
2. **DynamoDB 활용**: NoSQL 요구사항에 대한 DynamoDB 도입 검토
3. **OpenSearch 최신 버전**: 엔진 버전 업그레이드 계획

---

## 📊 모니터링 및 알림 설정

### 권장 CloudWatch 메트릭
1. **RDS**: CPU 사용률, 연결 수, 읽기/쓰기 지연시간
2. **ElastiCache**: CPU 사용률, 메모리 사용률, 캐시 히트율
3. **OpenSearch**: 클러스터 상태, 검색 지연시간, 인덱싱 속도

### 알림 임계값 권장사항
- **RDS CPU**: 80% 이상 지속 시 알림
- **ElastiCache 메모리**: 90% 이상 사용 시 알림
- **OpenSearch 클러스터**: Yellow/Red 상태 시 즉시 알림

---

## 💰 예상 비용 분석

### 월간 예상 비용 (추정)
MDEOF

# 비용 추정 (대략적)
if [ -f "database_rds_instances.json" ] && [ -s "database_rds_instances.json" ]; then
    echo "- **RDS 인스턴스**: 인스턴스 타입 및 스토리지 기반 비용 계산 필요" >> 05-database-analysis.md
fi

if [ -f "database_elasticache_clusters.json" ] && [ -s "database_elasticache_clusters.json" ]; then
    echo "- **ElastiCache**: 노드 타입 및 개수 기반 비용 계산 필요" >> 05-database-analysis.md
fi

if [ -f "database_opensearch_domains.json" ] && [ -s "database_opensearch_domains.json" ]; then
    echo "- **OpenSearch**: 인스턴스 타입 및 스토리지 기반 비용 계산 필요" >> 05-database-analysis.md
fi

cat >> 05-database-analysis.md << 'MDEOF'

### 비용 최적화 기회
1. **인스턴스 크기 조정**: 사용률 모니터링 후 적절한 크기로 조정
2. **예약 인스턴스**: 1년 또는 3년 약정으로 최대 75% 비용 절감
3. **스토리지 최적화**: 사용하지 않는 스냅샷 정리 및 스토리지 타입 최적화

---

*📅 분석 완료 시간: CURRENT_DATE_PLACEHOLDER*  
*🔄 다음 분석 권장 주기: 월 1회*

---
MDEOF

echo "✅ Enhanced Database Analysis 생성 완료: 05-database-analysis.md"
