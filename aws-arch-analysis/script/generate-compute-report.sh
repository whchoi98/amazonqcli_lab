#!/bin/bash
# Compute Analysis 보고서 생성 스크립트

# 스크립트의 실제 위치를 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPORT_DIR="${PROJECT_ROOT}/aws-arch-analysis/report"
cd $REPORT_DIR

echo "💻 Compute Analysis 보고서 생성 중..."

cat > 03-compute-analysis.md << MDEOF
# 💻 컴퓨팅 리소스 종합 분석

> **분석 일시**: $(date +"%Y-%m-%d %H:%M:%S")  
> **분석 대상**: AWS 계정 내 모든 컴퓨팅 리소스  
> **분석 리전**: ap-northeast-2 (서울)

이 보고서는 AWS 계정의 컴퓨팅 인프라에 대한 종합적인 분석을 제공하며, EC2 인스턴스, EKS 클러스터, Lambda 함수, Auto Scaling 그룹 등의 구성 상태와 성능 최적화 방안을 평가합니다.

## 💻 EC2 인스턴스 현황

### 인스턴스 개요
MDEOF

# EC2 인스턴스 데이터 분석
if [ -f "compute_ec2_instances.json" ] && [ -s "compute_ec2_instances.json" ]; then
    EC2_COUNT=$(jq '.rows | length' compute_ec2_instances.json)
    RUNNING_COUNT=$(jq '[.rows[] | select(.instance_state == "running")] | length' compute_ec2_instances.json)
    STOPPED_COUNT=$(jq '[.rows[] | select(.instance_state == "stopped")] | length' compute_ec2_instances.json)
    
    echo "**총 EC2 인스턴스:** ${EC2_COUNT}개" >> 03-compute-analysis.md
    echo "- **실행 중:** ${RUNNING_COUNT}개" >> 03-compute-analysis.md
    echo "- **중지됨:** ${STOPPED_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    
    echo "### 인스턴스 상세 목록" >> 03-compute-analysis.md
    echo "| 인스턴스 ID | 타입 | 상태 | VPC ID | 프라이빗 IP | 태그 |" >> 03-compute-analysis.md
    echo "|-------------|------|------|--------|-------------|------|" >> 03-compute-analysis.md
    jq -r '.rows[] | "| \(.instance_id) | \(.instance_type) | \(.instance_state) | \(.vpc_id // "N/A") | \(.private_ip_address // "N/A") | \(.tags.Name // "N/A") |"' compute_ec2_instances.json | head -10 >> 03-compute-analysis.md
    
    echo "" >> 03-compute-analysis.md
    echo "### 인스턴스 타입별 분포" >> 03-compute-analysis.md
    echo "| 인스턴스 타입 | 개수 | 비율 |" >> 03-compute-analysis.md
    echo "|---------------|------|------|" >> 03-compute-analysis.md
    jq -r '.rows | group_by(.instance_type) | .[] | "\(.[0].instance_type) | \(length) | \((length * 100 / ('$EC2_COUNT')) | floor)%"' compute_ec2_instances.json >> 03-compute-analysis.md
else
    echo "EC2 인스턴스 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << MDEOF

## ⚖️ 로드 밸런서 현황

### Application Load Balancer
MDEOF

# ALB 데이터 분석
if [ -f "compute_alb_detailed.json" ] && [ -s "compute_alb_detailed.json" ]; then
    ALB_COUNT=$(jq '.rows | length' compute_alb_detailed.json)
    echo "**총 ALB 수:** ${ALB_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    echo "| 이름 | 타입 | 스킴 | VPC ID | 상태 | DNS 이름 |" >> 03-compute-analysis.md
    echo "|------|------|------|--------|------|----------|" >> 03-compute-analysis.md
    jq -r '.rows[] | "| \(.load_balancer_name // .name) | \(.type) | \(.scheme) | \(.vpc_id) | \(.state.code // "available") | \(.dns_name // "N/A") |"' compute_alb_detailed.json >> 03-compute-analysis.md
else
    echo "ALB 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << MDEOF

### Target Groups
MDEOF

# Target Groups 데이터 분석
if [ -f "compute_target_groups.json" ] && [ -s "compute_target_groups.json" ]; then
    TG_COUNT=$(jq '.rows | length' compute_target_groups.json)
    echo "**총 Target Group 수:** ${TG_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    echo "| Target Group 이름 | 프로토콜 | 포트 | VPC ID | 헬스체크 경로 |" >> 03-compute-analysis.md
    echo "|-------------------|----------|------|--------|---------------|" >> 03-compute-analysis.md
    jq -r '.rows[] | "| \(.target_group_name) | \(.protocol) | \(.port) | \(.vpc_id) | \(.health_check_path // "N/A") |"' compute_target_groups.json | head -5 >> 03-compute-analysis.md
else
    echo "Target Group 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << MDEOF

### Auto Scaling 그룹
MDEOF

# ASG 데이터 분석
if [ -f "compute_asg_detailed.json" ] && [ -s "compute_asg_detailed.json" ]; then
    ASG_COUNT=$(jq '.rows | length' compute_asg_detailed.json)
    echo "**총 ASG 수:** ${ASG_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    echo "| ASG 이름 | 최소 | 원하는 | 최대 | 현재 인스턴스 | 헬스체크 타입 |" >> 03-compute-analysis.md
    echo "|----------|------|---------|------|---------------|---------------|" >> 03-compute-analysis.md
    jq -r '.rows[] | "| \(.auto_scaling_group_name) | \(.min_size) | \(.desired_capacity) | \(.max_size) | \(.instances | length) | \(.health_check_type) |"' compute_asg_detailed.json >> 03-compute-analysis.md
else
    echo "Auto Scaling 그룹 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << MDEOF

## 🚀 서버리스 컴퓨팅

### Lambda 함수 현황
MDEOF

# Lambda 함수 데이터 분석
if [ -f "iac_lambda_functions.json" ] && [ -s "iac_lambda_functions.json" ]; then
    LAMBDA_COUNT=$(jq '.Functions | length' iac_lambda_functions.json)
    echo "**총 Lambda 함수:** ${LAMBDA_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    echo "| 함수명 | 런타임 | 메모리 | 타임아웃 | 마지막 수정 | 코드 크기 |" >> 03-compute-analysis.md
    echo "|--------|---------|--------|----------|-------------|-----------|" >> 03-compute-analysis.md
    jq -r '.Functions[] | "| \(.FunctionName) | \(.Runtime) | \(.MemorySize)MB | \(.Timeout)s | \(.LastModified) | \(.CodeSize)B |"' iac_lambda_functions.json >> 03-compute-analysis.md
else
    echo "Lambda 함수 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << MDEOF

## 🐳 컨테이너 서비스

### EKS 클러스터
MDEOF

# EKS 클러스터 데이터 분석
if [ -f "compute_eks_clusters.json" ] && [ -s "compute_eks_clusters.json" ]; then
    EKS_COUNT=$(jq '.rows | length' compute_eks_clusters.json)
    echo "**총 EKS 클러스터:** ${EKS_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    echo "| 클러스터명 | 버전 | 상태 | 엔드포인트 | 플랫폼 버전 |" >> 03-compute-analysis.md
    echo "|------------|------|------|------------|-------------|" >> 03-compute-analysis.md
    jq -r '.rows[] | "| \(.name) | \(.version) | \(.status) | \(.endpoint[0:50])... | \(.platform_version) |"' compute_eks_clusters.json >> 03-compute-analysis.md
    
    # EKS 노드 그룹 정보
    if [ -f "compute_eks_node_groups.json" ] && [ -s "compute_eks_node_groups.json" ]; then
        NODE_GROUP_COUNT=$(jq '.rows | length' compute_eks_node_groups.json)
        echo "" >> 03-compute-analysis.md
        echo "### EKS 노드 그룹" >> 03-compute-analysis.md
        echo "**총 노드 그룹:** ${NODE_GROUP_COUNT}개" >> 03-compute-analysis.md
        echo "" >> 03-compute-analysis.md
        echo "| 노드 그룹명 | 클러스터 | 인스턴스 타입 | 원하는 크기 | 상태 |" >> 03-compute-analysis.md
        echo "|-------------|----------|---------------|-------------|------|" >> 03-compute-analysis.md
        jq -r '.rows[] | "| \(.nodegroup_name) | \(.cluster_name) | \(.instance_types[0]) | \(.scaling_config.desired_size) | \(.status) |"' compute_eks_node_groups.json >> 03-compute-analysis.md
    fi
else
    echo "EKS 클러스터 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << MDEOF

### ECS 클러스터
MDEOF

# ECS 클러스터 데이터 분석
if [ -f "compute_ecs_clusters.json" ] && [ -s "compute_ecs_clusters.json" ]; then
    ECS_COUNT=$(jq '.rows | length' compute_ecs_clusters.json)
    echo "**총 ECS 클러스터:** ${ECS_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    if [ $ECS_COUNT -gt 0 ]; then
        echo "| 클러스터명 | 상태 | 활성 서비스 | 실행 중 태스크 | 등록된 인스턴스 |" >> 03-compute-analysis.md
        echo "|------------|------|-------------|---------------|------------------|" >> 03-compute-analysis.md
        jq -r '.rows[] | "| \(.cluster_name) | \(.status) | \(.active_services_count // 0) | \(.running_tasks_count // 0) | \(.registered_container_instances_count // 0) |"' compute_ecs_clusters.json >> 03-compute-analysis.md
    fi
else
    echo "ECS 클러스터 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << MDEOF

## 📋 컴퓨팅 권장사항

### 🔴 높은 우선순위
1. **인스턴스 타입 최적화**: 사용률 기반 적절한 타입 선택
2. **미사용 인스턴스 정리**: 중지된 인스턴스 검토 및 정리
3. **Auto Scaling 정책**: 트래픽 패턴에 맞는 스케일링 정책 설정

### 🟡 중간 우선순위
1. **예약 인스턴스 활용**: 비용 최적화를 위한 RI 구매 검토
2. **Lambda 성능 최적화**: 메모리 및 타임아웃 설정 조정
3. **로드 밸런서 최적화**: Target Group 헬스체크 설정 검토

### 🟢 낮은 우선순위
1. **스팟 인스턴스 활용**: 배치 작업용 비용 절감
2. **컨테이너화 검토**: ECS/EKS 마이그레이션 고려
3. **Graviton 인스턴스**: ARM 기반 인스턴스 성능/비용 검토

## 💰 비용 최적화 기회

### 즉시 절감 가능
MDEOF

# 비용 최적화 분석
if [ -f "compute_ec2_instances.json" ] && [ -s "compute_ec2_instances.json" ]; then
    STOPPED_INSTANCES=$(jq '[.rows[] | select(.instance_state == "stopped")] | length' compute_ec2_instances.json)
    if [ $STOPPED_INSTANCES -gt 0 ]; then
        echo "1. **중지된 인스턴스**: ${STOPPED_INSTANCES}개 (EBS 비용 발생 중)" >> 03-compute-analysis.md
    fi
fi

cat >> 03-compute-analysis.md << MDEOF
2. **오버프로비저닝**: 사용률 낮은 인스턴스 타입 다운사이징
3. **예약 인스턴스**: 장기 실행 워크로드 비용 절감

---
*컴퓨팅 분석 완료*
MDEOF

echo "✅ Compute Analysis 생성 완료: 03-compute-analysis.md"
