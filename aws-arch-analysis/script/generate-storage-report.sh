#!/bin/bash
# Storage Analysis 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "💾 Storage Analysis 보고서 생성 중..."

cat > 05-storage-analysis.md << 'MDEOF'
# 스토리지 리소스 분석

## 💾 EBS 볼륨 현황

### EBS 볼륨 개요
MDEOF

# EBS 볼륨 데이터 분석
if [ -f "storage_ebs_volumes.json" ] && [ -s "storage_ebs_volumes.json" ]; then
    EBS_COUNT=$(jq '.rows | length' storage_ebs_volumes.json)
    ENCRYPTED_COUNT=$(jq '[.rows[] | select(.encrypted == true)] | length' storage_ebs_volumes.json)
    AVAILABLE_COUNT=$(jq '[.rows[] | select(.state == "available")] | length' storage_ebs_volumes.json)
    IN_USE_COUNT=$(jq '[.rows[] | select(.state == "in-use")] | length' storage_ebs_volumes.json)
    TOTAL_SIZE=$(jq '[.rows[] | .size] | add' storage_ebs_volumes.json)
    
    echo "**총 EBS 볼륨:** ${EBS_COUNT}개" >> 05-storage-analysis.md
    echo "- **사용 중:** ${IN_USE_COUNT}개" >> 05-storage-analysis.md
    echo "- **미사용 볼륨:** ${AVAILABLE_COUNT}개" >> 05-storage-analysis.md
    echo "- **암호화된 볼륨:** ${ENCRYPTED_COUNT}개" >> 05-storage-analysis.md
    echo "- **총 스토리지 크기:** ${TOTAL_SIZE}GB" >> 05-storage-analysis.md
    echo "" >> 05-storage-analysis.md
    
    echo "### EBS 볼륨 상세 목록" >> 05-storage-analysis.md
    echo "| 볼륨 ID | 타입 | 크기 | 상태 | 암호화 | AZ | 연결된 인스턴스 |" >> 05-storage-analysis.md
    echo "|---------|------|------|------|--------|----|--------------------|" >> 05-storage-analysis.md
    jq -r '.rows[] | "| \(.volume_id) | \(.volume_type) | \(.size)GB | \(.state) | \(.encrypted) | \(.availability_zone) | \(.attachments[0].instance_id // "없음") |"' storage_ebs_volumes.json | head -10 >> 05-storage-analysis.md
    
    echo "" >> 05-storage-analysis.md
    echo "### 볼륨 타입별 분포" >> 05-storage-analysis.md
    echo "| 볼륨 타입 | 개수 | 총 크기 |" >> 05-storage-analysis.md
    echo "|-----------|------|---------|" >> 05-storage-analysis.md
    jq -r '.rows | group_by(.volume_type) | .[] | "\(.[0].volume_type) | \(length) | \([.[] | .size] | add)GB"' storage_ebs_volumes.json >> 05-storage-analysis.md
else
    echo "EBS 볼륨 데이터를 찾을 수 없습니다." >> 05-storage-analysis.md
fi

cat >> 05-storage-analysis.md << 'MDEOF'

## 🪣 S3 버킷 현황

### S3 버킷 개요
MDEOF

# S3 버킷 데이터 분석
if [ -f "storage_s3_buckets.json" ] && [ -s "storage_s3_buckets.json" ]; then
    S3_COUNT=$(jq '.rows | length' storage_s3_buckets.json)
    echo "**총 S3 버킷:** ${S3_COUNT}개" >> 05-storage-analysis.md
    echo "" >> 05-storage-analysis.md
    if [ $S3_COUNT -gt 0 ]; then
        echo "| 버킷명 | 리전 | 생성일 | 버전 관리 |" >> 05-storage-analysis.md
        echo "|--------|------|--------|-----------|" >> 05-storage-analysis.md
        jq -r '.rows[] | "| \(.name) | \(.region // "N/A") | \(.creation_date) | \(.versioning_enabled // false) |"' storage_s3_buckets.json >> 05-storage-analysis.md
    fi
else
    echo "S3 버킷 데이터를 찾을 수 없습니다." >> 05-storage-analysis.md
fi

cat >> 05-storage-analysis.md << 'MDEOF'

## 📁 EFS 파일 시스템 현황

### EFS 개요
MDEOF

# EFS 파일 시스템 데이터 분석
if [ -f "storage_efs_file_systems.json" ] && [ -s "storage_efs_file_systems.json" ]; then
    EFS_COUNT=$(jq '.rows | length' storage_efs_file_systems.json)
    echo "**총 EFS 파일 시스템:** ${EFS_COUNT}개" >> 05-storage-analysis.md
    echo "" >> 05-storage-analysis.md
    if [ $EFS_COUNT -gt 0 ]; then
        echo "| 파일 시스템 ID | 이름 | 상태 | 성능 모드 | 암호화 |" >> 05-storage-analysis.md
        echo "|----------------|------|------|-----------|--------|" >> 05-storage-analysis.md
        jq -r '.rows[] | "| \(.file_system_id) | \(.name // "N/A") | \(.life_cycle_state) | \(.performance_mode) | \(.encrypted) |"' storage_efs_file_systems.json >> 05-storage-analysis.md
    fi
else
    echo "EFS 파일 시스템 데이터를 찾을 수 없습니다." >> 05-storage-analysis.md
fi

cat >> 05-storage-analysis.md << 'MDEOF'

## 💿 AWS Backup 현황

### Backup 볼트
MDEOF

# AWS Backup 볼트 데이터 분석
if [ -f "storage_backup_vaults.json" ] && [ -s "storage_backup_vaults.json" ]; then
    VAULT_COUNT=$(jq '.rows | length' storage_backup_vaults.json)
    echo "**총 Backup 볼트:** ${VAULT_COUNT}개" >> 05-storage-analysis.md
    echo "" >> 05-storage-analysis.md
    if [ $VAULT_COUNT -gt 0 ]; then
        echo "| 볼트명 | 복구 지점 수 | 암호화 키 |" >> 05-storage-analysis.md
        echo "|--------|---------------|-----------|" >> 05-storage-analysis.md
        jq -r '.rows[] | "| \(.name) | \(.number_of_recovery_points // 0) | \(.encryption_key_arn // "기본값") |"' storage_backup_vaults.json >> 05-storage-analysis.md
    fi
else
    echo "AWS Backup 볼트 데이터를 찾을 수 없습니다." >> 05-storage-analysis.md
fi

cat >> 05-storage-analysis.md << 'MDEOF'

## 📋 스토리지 권장사항

### 🔴 높은 우선순위
1. **EBS 암호화 활성화**: 모든 볼륨 암호화 적용
2. **미사용 볼륨 정리**: 연결되지 않은 볼륨 삭제
3. **백업 정책 수립**: 중요 데이터 정기 백업 설정

### 🟡 중간 우선순위
1. **S3 버킷 암호화**: 모든 버킷 서버 측 암호화 활성화
2. **EBS 스냅샷 정책**: 정기적인 백업 스케줄 구성
3. **S3 수명 주기 정책**: 비용 최적화를 위한 스토리지 클래스 전환

### 🟢 낮은 우선순위
1. **EFS 활용 검토**: 공유 파일 시스템 필요 시 고려
2. **S3 Intelligent Tiering**: 자동 비용 최적화 활성화
3. **FSx 성능 최적화**: 워크로드에 맞는 파일 시스템 타입 선택

## 💰 스토리지 비용 최적화

### 비용 절감 기회
MDEOF

# 비용 최적화 분석
if [ -f "storage_ebs_volumes.json" ] && [ -s "storage_ebs_volumes.json" ]; then
    AVAILABLE_VOLUMES=$(jq '[.rows[] | select(.state == "available")] | length' storage_ebs_volumes.json)
    AVAILABLE_SIZE=$(jq '[.rows[] | select(.state == "available") | .size] | add' storage_ebs_volumes.json 2>/dev/null || echo "0")
    if [ $AVAILABLE_VOLUMES -gt 0 ]; then
        echo "1. **미사용 EBS 볼륨**: ${AVAILABLE_VOLUMES}개 (${AVAILABLE_SIZE}GB) - 월 약 \$$(echo \"$AVAILABLE_SIZE * 0.1\" | bc -l 2>/dev/null || echo \"N/A\") 절감 가능" >> 05-storage-analysis.md
    fi
fi

cat >> 05-storage-analysis.md << 'MDEOF'
2. **EBS 볼륨 타입 최적화**: gp3로 마이그레이션하여 비용 절감
3. **스냅샷 정리**: 오래된 스냅샷 삭제로 스토리지 비용 절감

---
*스토리지 분석 완료*
MDEOF

echo "✅ Storage Analysis 생성 완료: 05-storage-analysis.md"
