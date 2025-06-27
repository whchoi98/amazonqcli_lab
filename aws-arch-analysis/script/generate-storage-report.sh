#!/bin/bash
# 확장된 스토리지 분석 보고서 생성 스크립트 (Shell 버전)

REPORT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"
cd $REPORT_DIR

echo "💾 확장된 Storage Analysis 보고서 생성 중..."

# 보고서 헤더
cat > 04-storage-analysis.md << 'EOF'
# 스토리지 리소스 분석

## 💾 EBS 볼륨 현황

### EBS 볼륨 개요
EOF

# EBS 볼륨 분석
if [ -f "storage_ebs_volumes.json" ] && [ -s "storage_ebs_volumes.json" ]; then
    EBS_COUNT=$(jq '.rows | length' storage_ebs_volumes.json)
    IN_USE_COUNT=$(jq '[.rows[] | select(.state == "in-use")] | length' storage_ebs_volumes.json)
    AVAILABLE_COUNT=$(jq '[.rows[] | select(.state == "available")] | length' storage_ebs_volumes.json)
    ENCRYPTED_COUNT=$(jq '[.rows[] | select(.encrypted == true)] | length' storage_ebs_volumes.json)
    TOTAL_SIZE=$(jq '[.rows[].size] | add' storage_ebs_volumes.json)
    
    {
        echo "**총 EBS 볼륨:** ${EBS_COUNT}개"
        echo "- **사용 중:** ${IN_USE_COUNT}개"
        echo "- **사용 가능:** ${AVAILABLE_COUNT}개"
        echo "- **암호화됨:** ${ENCRYPTED_COUNT}개"
        echo "- **총 용량:** ${TOTAL_SIZE} GB"
        echo ""
        echo "### EBS 볼륨 상세 목록 (전체 ${EBS_COUNT}개)"
        echo "| 볼륨 ID | 타입 | 크기(GB) | 상태 | 암호화 | 가용영역 |"
        echo "|---------|------|----------|------|--------|----------|"
    } >> 04-storage-analysis.md
    
    jq -r '.rows[] | "| \(.volume_id) | \(.volume_type) | \(.size) | \(.state) | \(if .encrypted then "예" else "아니오" end) | \(.availability_zone) |"' storage_ebs_volumes.json >> 04-storage-analysis.md
else
    echo "EBS 볼륨 데이터를 찾을 수 없습니다." >> 04-storage-analysis.md
fi

# 성능 분석 및 권장사항 추가
cat >> 04-storage-analysis.md << 'EOF'

## 📊 EBS 성능 분석

EOF

if [ -f "storage_ebs_volume_metric_read_ops.json" ] && [ -s "storage_ebs_volume_metric_read_ops.json" ]; then
    READ_METRICS_COUNT=$(jq '.rows | length' storage_ebs_volume_metric_read_ops.json)
    echo "**읽기 IOPS 데이터 포인트:** ${READ_METRICS_COUNT}개" >> 04-storage-analysis.md
fi

if [ -f "storage_ebs_volume_metric_write_ops.json" ] && [ -s "storage_ebs_volume_metric_write_ops.json" ]; then
    WRITE_METRICS_COUNT=$(jq '.rows | length' storage_ebs_volume_metric_write_ops.json)
    echo "**쓰기 IOPS 데이터 포인트:** ${WRITE_METRICS_COUNT}개" >> 04-storage-analysis.md
fi

cat >> 04-storage-analysis.md << 'EOF'

## 📋 스토리지 최적화 권장사항

### 🔴 높은 우선순위
1. **EBS 볼륨 암호화**: 암호화되지 않은 볼륨에 대한 암호화 활성화
2. **미사용 EBS 볼륨 정리**: 'available' 상태의 볼륨 검토 및 정리
3. **S3 버킷 보안**: 퍼블릭 액세스 설정 검토 및 제한

### 🟡 중간 우선순위
1. **EBS 볼륨 타입 최적화**: 워크로드에 맞는 적절한 볼륨 타입 선택
2. **S3 라이프사이클 정책**: 데이터 사용 패턴에 따른 스토리지 클래스 최적화
3. **백업 정책 수립**: 중요 데이터에 대한 자동 백업 설정

### 🟢 낮은 우선순위
1. **EBS 성능 모니터링**: IOPS 사용률 기반 볼륨 타입 조정
2. **S3 버전 관리**: 중요 데이터에 대한 버전 관리 활성화
3. **파일 시스템 최적화**: EFS/FSx 성능 모드 및 처리량 설정 검토

---
*스토리지 리소스 분석 완료*
EOF

echo "✅ 확장된 Storage Analysis 생성 완료: 04-storage-analysis.md"
