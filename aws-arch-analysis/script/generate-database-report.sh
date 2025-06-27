#!/bin/bash
# Database Analysis 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "🗄️ Database Analysis 보고서 생성 중..."

cat > 04-database-analysis.md << 'MDEOF'
# 데이터베이스 리소스 분석

## 🗄️ RDS 인스턴스 현황

### RDS 개요
MDEOF

# RDS 인스턴스 데이터 분석
if [ -f "database_rds_instances.json" ] && [ -s "database_rds_instances.json" ]; then
    RDS_COUNT=$(jq '.rows | length' database_rds_instances.json)
    AVAILABLE_COUNT=$(jq '[.rows[] | select(.status == "available")] | length' database_rds_instances.json)
    echo "**총 RDS 인스턴스:** ${RDS_COUNT}개 (사용 가능: ${AVAILABLE_COUNT}개)" >> 04-database-analysis.md
    echo "" >> 04-database-analysis.md
    echo "| DB 식별자 | 엔진 | 버전 | 클래스 | 스토리지 | 상태 | Multi-AZ |" >> 04-database-analysis.md
    echo "|-----------|------|------|-------|----------|------|----------|" >> 04-database-analysis.md
    jq -r '.rows[] | "| \(.db_instance_identifier) | \(.engine) | \(.engine_version) | \(.class) | \(.allocated_storage)GB | \(.status) | \(.multi_az) |"' database_rds_instances.json >> 04-database-analysis.md
    
    echo "" >> 04-database-analysis.md
    echo "### 엔진별 분포" >> 04-database-analysis.md
    echo "| 엔진 | 개수 |" >> 04-database-analysis.md
    echo "|------|------|" >> 04-database-analysis.md
    jq -r '.rows | group_by(.engine) | .[] | "| \(.[0].engine) | \(length) |"' database_rds_instances.json >> 04-database-analysis.md
else
    echo "RDS 인스턴스 데이터를 찾을 수 없습니다." >> 04-database-analysis.md
fi

cat >> 04-database-analysis.md << 'MDEOF'

### RDS 클러스터 (Aurora)
MDEOF

# RDS 클러스터 데이터 분석
if [ -f "database_rds_clusters.json" ] && [ -s "database_rds_clusters.json" ]; then
    CLUSTER_COUNT=$(jq '.rows | length' database_rds_clusters.json)
    echo "**총 RDS 클러스터:** ${CLUSTER_COUNT}개" >> 04-database-analysis.md
    echo "" >> 04-database-analysis.md
    echo "| 클러스터 식별자 | 엔진 | 버전 | 상태 | 멤버 수 | 백업 보존 |" >> 04-database-analysis.md
    echo "|-----------------|------|------|------|---------|-----------|" >> 04-database-analysis.md
    jq -r '.rows[] | "| \(.db_cluster_identifier) | \(.engine) | \(.engine_version) | \(.status) | \(.db_cluster_members | length) | \(.backup_retention_period)일 |"' database_rds_clusters.json >> 04-database-analysis.md
else
    echo "RDS 클러스터 데이터를 찾을 수 없습니다." >> 04-database-analysis.md
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

cat >> 04-database-analysis.md << 'MDEOF'

## ⚡ ElastiCache 클러스터 현황

### ElastiCache 개요
MDEOF

# ElastiCache 클러스터 데이터 분석
if [ -f "database_elasticache_clusters.json" ] && [ -s "database_elasticache_clusters.json" ]; then
    CACHE_COUNT=$(jq '.rows | length' database_elasticache_clusters.json)
    echo "**총 ElastiCache 클러스터:** ${CACHE_COUNT}개" >> 04-database-analysis.md
    echo "" >> 04-database-analysis.md
    echo "| 클러스터 ID | 엔진 | 버전 | 노드 타입 | 상태 | 노드 수 |" >> 04-database-analysis.md
    echo "|-------------|------|------|-----------|------|---------|" >> 04-database-analysis.md
    jq -r '.rows[] | "| \(.cache_cluster_id) | \(.engine) | \(.engine_version) | \(.cache_node_type) | \(.cache_cluster_status) | \(.num_cache_nodes) |"' database_elasticache_clusters.json >> 04-database-analysis.md
else
    echo "ElastiCache 클러스터 데이터를 찾을 수 없습니다." >> 04-database-analysis.md
fi

cat >> 04-database-analysis.md << 'MDEOF'

### ElastiCache 복제 그룹
MDEOF

# ElastiCache 복제 그룹 데이터 분석
if [ -f "database_elasticache_replication_groups.json" ] && [ -s "database_elasticache_replication_groups.json" ]; then
    REPL_COUNT=$(jq '.rows | length' database_elasticache_replication_groups.json)
    echo "**총 복제 그룹:** ${REPL_COUNT}개" >> 04-database-analysis.md
    echo "" >> 04-database-analysis.md
    echo "| 복제 그룹 ID | 설명 | 상태 | 노드 타입 | 멤버 클러스터 수 |" >> 04-database-analysis.md
    echo "|--------------|------|------|-----------|------------------|" >> 04-database-analysis.md
    jq -r '.rows[] | "| \(.replication_group_id) | \(.description) | \(.status) | \(.cache_node_type) | \(.member_clusters | length) |"' database_elasticache_replication_groups.json >> 04-database-analysis.md
else
    echo "ElastiCache 복제 그룹 데이터를 찾을 수 없습니다." >> 04-database-analysis.md
fi

cat >> 04-database-analysis.md << 'MDEOF'

## 📊 기타 데이터베이스 서비스

### Redshift 클러스터
MDEOF

# Redshift 클러스터 데이터 분석
if [ -f "database_redshift_clusters.json" ] && [ -s "database_redshift_clusters.json" ]; then
    REDSHIFT_COUNT=$(jq '.rows | length' database_redshift_clusters.json)
    echo "**총 Redshift 클러스터:** ${REDSHIFT_COUNT}개" >> 04-database-analysis.md
    echo "" >> 04-database-analysis.md
    if [ $REDSHIFT_COUNT -gt 0 ]; then
        echo "| 클러스터 식별자 | 노드 타입 | 노드 수 | 상태 | 데이터베이스명 |" >> 04-database-analysis.md
        echo "|-----------------|-----------|---------|------|---------------|" >> 04-database-analysis.md
        jq -r '.rows[] | "| \(.cluster_identifier) | \(.node_type) | \(.number_of_nodes) | \(.cluster_status) | \(.db_name) |"' database_redshift_clusters.json >> 04-database-analysis.md
    fi
else
    echo "Redshift 클러스터 데이터를 찾을 수 없습니다." >> 04-database-analysis.md
fi

cat >> 04-database-analysis.md << 'MDEOF'

### DocumentDB 클러스터
MDEOF

# DocumentDB 클러스터 데이터 분석
if [ -f "database_docdb_clusters.json" ] && [ -s "database_docdb_clusters.json" ]; then
    DOCDB_COUNT=$(jq '.rows | length' database_docdb_clusters.json)
    echo "**총 DocumentDB 클러스터:** ${DOCDB_COUNT}개" >> 04-database-analysis.md
    echo "" >> 04-database-analysis.md
    if [ $DOCDB_COUNT -gt 0 ]; then
        echo "| 클러스터 식별자 | 엔진 | 상태 | 멤버 수 |" >> 04-database-analysis.md
        echo "|-----------------|------|------|---------|" >> 04-database-analysis.md
        jq -r '.rows[] | "| \(.db_cluster_identifier) | \(.engine) | \(.status) | \(.db_cluster_members | length) |"' database_docdb_clusters.json >> 04-database-analysis.md
    fi
else
    echo "DocumentDB 클러스터 데이터를 찾을 수 없습니다." >> 04-database-analysis.md
fi

cat >> 04-database-analysis.md << 'MDEOF'

## 📋 데이터베이스 권장사항

### 🔴 높은 우선순위
1. **RDS 백업 설정**: 자동 백업 및 보존 기간 확인
2. **데이터베이스 암호화**: 저장 시 암호화 활성화
3. **Multi-AZ 구성**: 고가용성을 위한 Multi-AZ 설정

### 🟡 중간 우선순위
1. **성능 모니터링**: Performance Insights 활성화
2. **DynamoDB 백업**: 지속적 백업 활성화
3. **읽기 전용 복제본**: 읽기 성능 향상을 위한 구성

### 🟢 낮은 우선순위
1. **Aurora 마이그레이션**: 성능 및 비용 최적화 검토
2. **DynamoDB Global Tables**: 다중 리전 복제 고려
3. **ElastiCache 최적화**: 캐시 전략 및 TTL 설정

## 🔒 데이터베이스 보안 분석

### 보안 설정 현황
MDEOF

# RDS 보안 설정 분석
if [ -f "database_rds_instances.json" ] && [ -s "database_rds_instances.json" ]; then
    TOTAL_RDS=$(jq '.rows | length' database_rds_instances.json)
    MULTI_AZ_COUNT=$(jq '[.rows[] | select(.multi_az == true)] | length' database_rds_instances.json)
    echo "- **Multi-AZ 구성**: ${MULTI_AZ_COUNT}/${TOTAL_RDS}개 인스턴스" >> 04-database-analysis.md
    echo "- **백업 설정**: 자동 백업 활성화 상태 검토 필요" >> 04-database-analysis.md
fi

cat >> 04-database-analysis.md << 'MDEOF'

## 💰 데이터베이스 비용 최적화

### 비용 절감 기회
1. **인스턴스 타입 최적화**: 사용률 기반 적절한 크기 조정
2. **예약 인스턴스**: 장기 실행 데이터베이스 비용 절감
3. **스토리지 최적화**: gp3 스토리지 타입 활용 검토

---
*데이터베이스 분석 완료*
MDEOF

echo "✅ Database Analysis 생성 완료: 04-database-analysis.md"
