#!/bin/bash
# Compute Analysis 보고서 생성 스크립트

REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
cd $REPORT_DIR

echo "💻 Compute Analysis 보고서 생성 중..."

cat > 03-compute-analysis.md << 'MDEOF'
# 컴퓨팅 리소스 분석

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
    
    # 모든 인스턴스 상세 목록 (head -10 제거)
    echo "### 인스턴스 상세 목록 (전체 ${EC2_COUNT}개)" >> 03-compute-analysis.md
    echo "| 인스턴스 ID | 타입 | 상태 | VPC ID | 프라이빗 IP | 태그 |" >> 03-compute-analysis.md
    echo "|-------------|------|------|--------|-------------|------|" >> 03-compute-analysis.md
    jq -r '.rows[] | "| \(.instance_id) | \(.instance_type) | \(.instance_state) | \(.vpc_id // "N/A") | \(.private_ip_address // "N/A") | \(.tags.Name // "N/A") |"' compute_ec2_instances.json >> 03-compute-analysis.md
    
    echo "" >> 03-compute-analysis.md
    echo "### 인스턴스 타입별 분포" >> 03-compute-analysis.md
    echo "| 인스턴스 타입 | 개수 | 비율 |" >> 03-compute-analysis.md
    echo "|---------------|------|------|" >> 03-compute-analysis.md
    
    # 인스턴스 타입별 분포 계산 (정확한 비율 계산)
    jq -r '.rows | group_by(.instance_type) | sort_by(-length) | .[] | "| \(.[0].instance_type) | \(length) | \((length * 100.0 / ('$EC2_COUNT')) | round)% |"' compute_ec2_instances.json >> 03-compute-analysis.md
    
    echo "" >> 03-compute-analysis.md
    echo "### VPC별 인스턴스 분포" >> 03-compute-analysis.md
    echo "| VPC ID | 개수 | 비율 | 용도 |" >> 03-compute-analysis.md
    echo "|--------|------|------|------|" >> 03-compute-analysis.md
    
    # VPC별 분포 계산 및 용도 매핑
    jq -r '.rows | group_by(.vpc_id) | sort_by(-length) | .[] | 
    if .[0].vpc_id | contains("0659f2506b8e73190") then
        "| \(.[0].vpc_id) | \(length) | \((length * 100.0 / ('$EC2_COUNT')) | round)% | DMZ VPC (EKS 워크샵 포함) |"
    elif .[0].vpc_id | contains("0e92e062c2971318a") then
        "| \(.[0].vpc_id) | \(length) | \((length * 100.0 / ('$EC2_COUNT')) | round)% | VPC01 |"
    elif .[0].vpc_id | contains("01d638528e5b0cc40") then
        "| \(.[0].vpc_id) | \(length) | \((length * 100.0 / ('$EC2_COUNT')) | round)% | VPC02 |"
    elif .[0].vpc_id | contains("0bb2c005ead840ef7") then
        "| \(.[0].vpc_id) | \(length) | \((length * 100.0 / ('$EC2_COUNT')) | round)% | 관리 VPC |"
    elif .[0].vpc_id | contains("01dac96d5cc2b0662") then
        "| \(.[0].vpc_id) | \(length) | \((length * 100.0 / ('$EC2_COUNT')) | round)% | Cloud9 워크스페이스 |"
    else
        "| \(.[0].vpc_id) | \(length) | \((length * 100.0 / ('$EC2_COUNT')) | round)% | 기타 |"
    end' compute_ec2_instances.json >> 03-compute-analysis.md
    
else
    echo "EC2 인스턴스 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'

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
    jq -r '.rows[] | "| \(.load_balancer_name // .name) | \(.type // .load_balancer_type) | \(.scheme) | \(.vpc_id) | \(.state.code // .load_balancer_state // "available") | \(.dns_name // "N/A") |"' compute_alb_detailed.json >> 03-compute-analysis.md
else
    echo "ALB 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'

### Target Groups
MDEOF

# Target Groups 데이터 분석
if [ -f "compute_target_groups.json" ] && [ -s "compute_target_groups.json" ]; then
    TG_COUNT=$(jq '.rows | length' compute_target_groups.json)
    echo "**총 Target Group 수:** ${TG_COUNT}개" >> 03-compute-analysis.md
    echo "" >> 03-compute-analysis.md
    echo "| Target Group 이름 | 프로토콜 | 포트 | VPC ID | 헬스체크 경로 |" >> 03-compute-analysis.md
    echo "|-------------------|----------|------|--------|---------------|" >> 03-compute-analysis.md
    jq -r '.rows[] | "| \(.target_group_name) | \(.protocol) | \(.port) | \(.vpc_id) | \(.health_check_path // "N/A") |"' compute_target_groups.json >> 03-compute-analysis.md
else
    echo "Target Group 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'

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

cat >> 03-compute-analysis.md << 'MDEOF'

## 🚀 서버리스 컴퓨팅

### Lambda 함수 현황
MDEOF

# Lambda 함수 데이터 분석 (여러 파일 확인)
LAMBDA_FOUND=false
for lambda_file in "compute_lambda_functions.json" "iac_lambda_functions.json"; do
    if [ -f "$lambda_file" ] && [ -s "$lambda_file" ]; then
        # JSON 구조 확인
        if jq -e '.rows' "$lambda_file" > /dev/null 2>&1; then
            # Steampipe 형식
            LAMBDA_COUNT=$(jq '.rows | length' "$lambda_file")
            if [ $LAMBDA_COUNT -gt 0 ]; then
                echo "**총 Lambda 함수:** ${LAMBDA_COUNT}개" >> 03-compute-analysis.md
                echo "" >> 03-compute-analysis.md
                echo "| 함수명 | 런타임 | 메모리 | 타임아웃 | 마지막 수정 | 코드 크기 |" >> 03-compute-analysis.md
                echo "|--------|---------|--------|----------|-------------|-----------|" >> 03-compute-analysis.md
                jq -r '.rows[] | "| \(.name // .function_name) | \(.runtime) | \(.memory_size // 128)MB | \(.timeout // 3)s | \(.last_modified) | \(.code_size // 0)B |"' "$lambda_file" >> 03-compute-analysis.md
                LAMBDA_FOUND=true
                break
            fi
        elif jq -e '.Functions' "$lambda_file" > /dev/null 2>&1; then
            # AWS CLI 형식
            LAMBDA_COUNT=$(jq '.Functions | length' "$lambda_file")
            if [ $LAMBDA_COUNT -gt 0 ]; then
                echo "**총 Lambda 함수:** ${LAMBDA_COUNT}개" >> 03-compute-analysis.md
                echo "" >> 03-compute-analysis.md
                echo "| 함수명 | 런타임 | 메모리 | 타임아웃 | 마지막 수정 | 코드 크기 |" >> 03-compute-analysis.md
                echo "|--------|---------|--------|----------|-------------|-----------|" >> 03-compute-analysis.md
                jq -r '.Functions[] | "| \(.FunctionName) | \(.Runtime) | \(.MemorySize)MB | \(.Timeout)s | \(.LastModified) | \(.CodeSize)B |"' "$lambda_file" >> 03-compute-analysis.md
                LAMBDA_FOUND=true
                break
            fi
        fi
    fi
done

if [ "$LAMBDA_FOUND" = false ]; then
    echo "Lambda 함수 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'

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
        jq -r '.rows[] | "| \(.nodegroup_name) | \(.cluster_name) | \(.instance_types[0] // "N/A") | \(.scaling_config.desired_size // "N/A") | \(.status) |"' compute_eks_node_groups.json >> 03-compute-analysis.md
    fi
    
    # EKS Addon 정보
    if [ -f "compute_eks_addons.json" ] && [ -s "compute_eks_addons.json" ]; then
        ADDON_COUNT=$(jq '.rows | length' compute_eks_addons.json)
        echo "" >> 03-compute-analysis.md
        echo "### EKS 애드온" >> 03-compute-analysis.md
        echo "**총 애드온:** ${ADDON_COUNT}개" >> 03-compute-analysis.md
        echo "" >> 03-compute-analysis.md
        echo "| 애드온명 | 클러스터 | 버전 | 상태 | 게시자 | 마지막 수정 |" >> 03-compute-analysis.md
        echo "|----------|----------|------|------|--------|-------------|" >> 03-compute-analysis.md
        jq -r '.rows[] | "| \(.addon_name) | \(.cluster_name) | \(.addon_version) | \(.status) | \(.publisher // "AWS") | \(.modified_at[0:10]) |"' compute_eks_addons.json >> 03-compute-analysis.md
        
        # 애드온별 상세 분석
        echo "" >> 03-compute-analysis.md
        echo "#### 애드온 상세 분석" >> 03-compute-analysis.md
        
        # 핵심 애드온 버전 체크
        echo "**핵심 애드온 버전 현황:**" >> 03-compute-analysis.md
        echo "" >> 03-compute-analysis.md
        
        # VPC CNI 버전 체크
        VPC_CNI_VERSION=$(jq -r '.rows[] | select(.addon_name == "vpc-cni") | .addon_version' compute_eks_addons.json 2>/dev/null)
        if [ "$VPC_CNI_VERSION" != "null" ] && [ -n "$VPC_CNI_VERSION" ]; then
            echo "- **VPC CNI**: $VPC_CNI_VERSION" >> 03-compute-analysis.md
        fi
        
        # CoreDNS 버전 체크
        COREDNS_VERSION=$(jq -r '.rows[] | select(.addon_name == "coredns") | .addon_version' compute_eks_addons.json 2>/dev/null)
        if [ "$COREDNS_VERSION" != "null" ] && [ -n "$COREDNS_VERSION" ]; then
            echo "- **CoreDNS**: $COREDNS_VERSION" >> 03-compute-analysis.md
        fi
        
        # Kube-proxy 버전 체크
        KUBE_PROXY_VERSION=$(jq -r '.rows[] | select(.addon_name == "kube-proxy") | .addon_version' compute_eks_addons.json 2>/dev/null)
        if [ "$KUBE_PROXY_VERSION" != "null" ] && [ -n "$KUBE_PROXY_VERSION" ]; then
            echo "- **Kube-proxy**: $KUBE_PROXY_VERSION" >> 03-compute-analysis.md
        fi
        
        # EBS CSI Driver 버전 체크
        EBS_CSI_VERSION=$(jq -r '.rows[] | select(.addon_name == "aws-ebs-csi-driver") | .addon_version' compute_eks_addons.json 2>/dev/null)
        if [ "$EBS_CSI_VERSION" != "null" ] && [ -n "$EBS_CSI_VERSION" ]; then
            echo "- **AWS EBS CSI Driver**: $EBS_CSI_VERSION" >> 03-compute-analysis.md
        fi
        
        # Metrics Server 버전 체크
        METRICS_SERVER_VERSION=$(jq -r '.rows[] | select(.addon_name == "metrics-server") | .addon_version' compute_eks_addons.json 2>/dev/null)
        if [ "$METRICS_SERVER_VERSION" != "null" ] && [ -n "$METRICS_SERVER_VERSION" ]; then
            echo "- **Metrics Server**: $METRICS_SERVER_VERSION" >> 03-compute-analysis.md
        fi
        
        # 애드온 상태 분석
        echo "" >> 03-compute-analysis.md
        ACTIVE_ADDONS=$(jq '[.rows[] | select(.status == "ACTIVE")] | length' compute_eks_addons.json)
        INACTIVE_ADDONS=$(jq '[.rows[] | select(.status != "ACTIVE")] | length' compute_eks_addons.json)
        
        echo "**애드온 상태 요약:**" >> 03-compute-analysis.md
        echo "- **활성 상태**: ${ACTIVE_ADDONS}개" >> 03-compute-analysis.md
        echo "- **비활성/문제**: ${INACTIVE_ADDONS}개" >> 03-compute-analysis.md
        
        # 건강 상태 이슈 체크
        HEALTH_ISSUES=$(jq '[.rows[] | select(.health_issues | length > 0)] | length' compute_eks_addons.json)
        if [ $HEALTH_ISSUES -gt 0 ]; then
            echo "- **⚠️ 건강 상태 이슈**: ${HEALTH_ISSUES}개 애드온에서 문제 발견" >> 03-compute-analysis.md
        else
            echo "- **✅ 건강 상태**: 모든 애드온 정상" >> 03-compute-analysis.md
        fi
    fi
else
    echo "EKS 클러스터 데이터를 찾을 수 없습니다." >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'

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
    echo "**총 ECS 클러스터:** 0개" >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'


## 📋 컴퓨팅 권장사항

### 🔴 높은 우선순위
1. **인스턴스 타입 최적화**: 사용률 기반 적절한 타입 선택
2. **미사용 인스턴스 정리**: 중지된 인스턴스 검토 및 정리
3. **Auto Scaling 정책**: 트래픽 패턴에 맞는 스케일링 정책 설정
MDEOF

# EKS Addon 관련 권장사항 추가
if [ -f "compute_eks_addons.json" ] && [ -s "compute_eks_addons.json" ]; then
    ADDON_COUNT=$(jq '.rows | length' compute_eks_addons.json)
    if [ $ADDON_COUNT -gt 0 ]; then
        echo "4. **EKS 애드온 업데이트**: 보안 및 성능 향상을 위한 최신 버전 유지" >> 03-compute-analysis.md
        
        # 특정 애드온 버전 체크 및 권장사항
        HEALTH_ISSUES=$(jq '[.rows[] | select(.health_issues | length > 0)] | length' compute_eks_addons.json)
        if [ $HEALTH_ISSUES -gt 0 ]; then
            echo "5. **⚠️ EKS 애드온 건강 상태**: ${HEALTH_ISSUES}개 애드온의 문제 해결 필요" >> 03-compute-analysis.md
        fi
    fi
fi

cat >> 03-compute-analysis.md << 'MDEOF'

### 🟡 중간 우선순위
1. **예약 인스턴스 활용**: 비용 최적화를 위한 RI 구매 검토
2. **Lambda 성능 최적화**: 메모리 및 타임아웃 설정 조정
3. **로드 밸런서 최적화**: Target Group 헬스체크 설정 검토
MDEOF

# EKS 관련 중간 우선순위 권장사항 추가
if [ -f "compute_eks_addons.json" ] && [ -s "compute_eks_addons.json" ]; then
    echo "4. **EKS 애드온 모니터링**: 애드온 성능 및 리소스 사용량 모니터링 설정" >> 03-compute-analysis.md
    echo "5. **EKS 클러스터 버전 호환성**: 클러스터 버전과 애드온 버전 호환성 검토" >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'

### 🟢 낮은 우선순위
1. **스팟 인스턴스 활용**: 배치 작업용 비용 절감
2. **컨테이너화 검토**: ECS/EKS 마이그레이션 고려
3. **Graviton 인스턴스**: ARM 기반 인스턴스 성능/비용 검토
MDEOF

# EKS 관련 낮은 우선순위 권장사항 추가
if [ -f "compute_eks_addons.json" ] && [ -s "compute_eks_addons.json" ]; then
    echo "4. **EKS 애드온 자동화**: Terraform/CDK를 통한 애드온 관리 자동화" >> 03-compute-analysis.md
    echo "5. **추가 애드온 검토**: AWS Load Balancer Controller, Cluster Autoscaler 등 추가 애드온 도입 검토" >> 03-compute-analysis.md
fi

cat >> 03-compute-analysis.md << 'MDEOF'

## 💰 비용 최적화 기회

### 즉시 절감 가능
MDEOF

# 비용 최적화 분석
if [ -f "compute_ec2_instances.json" ] && [ -s "compute_ec2_instances.json" ]; then
    STOPPED_INSTANCES=$(jq '[.rows[] | select(.instance_state == "stopped")] | length' compute_ec2_instances.json)
    if [ $STOPPED_INSTANCES -gt 0 ]; then
        echo "1. **중지된 인스턴스**: ${STOPPED_INSTANCES}개 (EBS 비용 발생 중)" >> 03-compute-analysis.md
    else
        echo "1. **중지된 인스턴스**: 없음 (양호)" >> 03-compute-analysis.md
    fi
fi

cat >> 03-compute-analysis.md << 'MDEOF'
2. **오버프로비저닝**: 사용률 낮은 인스턴스 타입 다운사이징
3. **예약 인스턴스**: 장기 실행 워크로드 비용 절감

---
*컴퓨팅 분석 완료*
MDEOF

echo "✅ Compute Analysis 생성 완료: 03-compute-analysis.md"
