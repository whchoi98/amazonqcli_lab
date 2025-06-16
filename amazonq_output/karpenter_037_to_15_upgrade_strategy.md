# Karpenter 0.37 → v1.5 업그레이드 전략 가이드

## 1. 업그레이드 개요

### 1.1 주요 변경사항 요약
- **API 버전**: `v1beta1` → `v1` (안정화된 API)
- **리소스 타입**: `Provisioner` + `AWSNodePool` → `NodePool` + `EC2NodeClass`
- **태그 요구사항**: 엄격한 태그 검증 및 새로운 태그 구조
- **권한 변경**: 세분화된 IAM 권한 필요

### 1.2 업그레이드 위험도 평가
- **위험도**: **높음** (Breaking Changes 포함)
- **다운타임**: 계획된 다운타임 필요
- **롤백 복잡도**: 높음 (사전 백업 필수)

## 2. 사전 준비 단계 (Pre-Upgrade)

### 2.1 현재 환경 분석 및 백업

#### **Step 1: 현재 Karpenter 설정 백업**
```bash
#!/bin/bash
BACKUP_DIR="karpenter-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

# 현재 Karpenter 리소스 백업
echo "=== Provisioner 백업 ==="
kubectl get provisioner -o yaml > $BACKUP_DIR/provisioners.yaml

echo "=== AWSNodePool 백업 ==="
kubectl get awsnodepool -o yaml > $BACKUP_DIR/awsnodepools.yaml

echo "=== Karpenter 설정 백업 ==="
kubectl get deployment karpenter -n karpenter -o yaml > $BACKUP_DIR/karpenter-deployment.yaml
kubectl get configmap karpenter-global-settings -n karpenter -o yaml > $BACKUP_DIR/karpenter-configmap.yaml

echo "=== 현재 노드 상태 백업 ==="
kubectl get nodes -o wide > $BACKUP_DIR/current-nodes.txt
kubectl describe nodes > $BACKUP_DIR/nodes-detailed.txt

echo "백업 완료: $BACKUP_DIR"
```

#### **Step 2: 현재 워크로드 분석**
```bash
#!/bin/bash
# 현재 실행 중인 워크로드 분석
echo "=== 현재 파드 분포 분석 ==="
kubectl get pods -A -o wide | grep -v kube-system > workload-analysis.txt

echo "=== 노드별 파드 분포 ==="
for node in $(kubectl get nodes --no-headers | awk '{print $1}'); do
    echo "Node: $node"
    kubectl get pods -A --field-selector spec.nodeName=$node --no-headers | wc -l
done > node-pod-distribution.txt

echo "=== 리소스 사용량 분석 ==="
kubectl top nodes > resource-usage.txt
kubectl top pods -A > pod-resource-usage.txt
```

### 2.2 호환성 검증

#### **Step 3: EKS 버전 호환성 확인**
```bash
# EKS 클러스터 버전 확인
CLUSTER_VERSION=$(kubectl version --short | grep "Server Version" | awk '{print $3}')
echo "현재 EKS 버전: $CLUSTER_VERSION"

# Karpenter v1.5 호환성 확인 (EKS 1.23+ 필요)
if [[ "$CLUSTER_VERSION" < "v1.23" ]]; then
    echo "경고: EKS 버전 업그레이드가 먼저 필요합니다."
    exit 1
fi
```

#### **Step 4: 애드온 호환성 확인**
```bash
# 현재 설치된 애드온 확인
aws eks list-addons --cluster-name <cluster-name>

# AWS Load Balancer Controller 버전 확인
kubectl get deployment aws-load-balancer-controller -n kube-system -o jsonpath='{.spec.template.spec.containers[0].image}'

# VPC CNI 버전 확인
kubectl get daemonset aws-node -n kube-system -o jsonpath='{.spec.template.spec.containers[0].image}'
```

### 2.3 네트워크 태그 사전 준비

#### **Step 5: 필수 태그 사전 적용**
```bash
#!/bin/bash
CLUSTER_NAME="your-cluster-name"
VPC_ID="your-vpc-id"

echo "=== 사전 태그 적용 시작 ==="

# VPC 태그 추가 (기존 태그 유지하면서)
aws ec2 create-tags --resources $VPC_ID --tags \
    Key=karpenter.sh/discovery,Value=$CLUSTER_NAME

# 서브넷 태그 추가
for subnet in $(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text); do
    # 기존 태그 확인
    EXISTING_TAGS=$(aws ec2 describe-subnets --subnet-ids $subnet --query 'Subnets[0].Tags')
    
    # 새 태그 추가
    aws ec2 create-tags --resources $subnet --tags \
        Key=karpenter.sh/discovery,Value=$CLUSTER_NAME
done

# 보안 그룹 태그 추가
for sg in $(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:kubernetes.io/cluster/$CLUSTER_NAME,Values=owned" --query 'SecurityGroups[*].GroupId' --output text); do
    aws ec2 create-tags --resources $sg --tags \
        Key=karpenter.sh/discovery,Value=$CLUSTER_NAME
done

echo "=== 사전 태그 적용 완료 ==="
```

## 3. 업그레이드 실행 전략

### 3.1 Blue-Green 업그레이드 전략 (권장)

#### **Phase 1: 새로운 NodePool 준비**
```yaml
# new-nodepool-v1.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default-v1
spec:
  template:
    metadata:
      labels:
        karpenter-version: "v1"
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
      nodeClassRef:
        apiVersion: karpenter.k8s.aws/v1
        kind: EC2NodeClass
        name: default-v1
      taints:
        - key: karpenter-version
          value: "v1"
          effect: NoSchedule
  limits:
    cpu: 1000
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 30s
---
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default-v1
spec:
  amiFamily: AL2
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: "your-cluster-name"
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: "your-cluster-name"
  instanceStorePolicy: RAID0
  userData: |
    #!/bin/bash
    /etc/eks/bootstrap.sh your-cluster-name
    echo "Karpenter v1 node ready"
```

#### **Phase 2: Karpenter v1.5 설치 (병렬 실행)**
```bash
#!/bin/bash
# Karpenter v1.5 설치 (기존 v0.37과 병렬)

# 새로운 네임스페이스에 v1.5 설치
kubectl create namespace karpenter-v1

# Helm으로 v1.5 설치
helm repo add karpenter https://charts.karpenter.sh/
helm repo update

helm install karpenter-v1 karpenter/karpenter \
  --version "1.5.0" \
  --namespace "karpenter-v1" \
  --create-namespace \
  --set "settings.clusterName=your-cluster-name" \
  --set "settings.interruptionQueue=your-cluster-name" \
  --set "controller.resources.requests.cpu=1" \
  --set "controller.resources.requests.memory=1Gi" \
  --set "controller.resources.limits.cpu=1" \
  --set "controller.resources.limits.memory=1Gi" \
  --wait
```

### 3.2 단계별 워크로드 마이그레이션

#### **Phase 3: 테스트 워크로드 마이그레이션**
```bash
#!/bin/bash
# 테스트 워크로드 배포
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-workload-v1
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: test-v1
  template:
    metadata:
      labels:
        app: test-v1
    spec:
      tolerations:
        - key: karpenter-version
          value: "v1"
          effect: NoSchedule
      nodeSelector:
        karpenter-version: "v1"
      containers:
      - name: nginx
        image: nginx:latest
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
EOF

# 테스트 워크로드 상태 확인
kubectl get pods -l app=test-v1 -o wide
kubectl describe pods -l app=test-v1
```

#### **Phase 4: 프로덕션 워크로드 점진적 마이그레이션**
```bash
#!/bin/bash
# 워크로드별 점진적 마이그레이션 스크립트

NAMESPACES=("app1" "app2" "app3")  # 마이그레이션할 네임스페이스 목록

for ns in "${NAMESPACES[@]}"; do
    echo "=== $ns 네임스페이스 마이그레이션 시작 ==="
    
    # 현재 워크로드 확인
    kubectl get deployments -n $ns
    
    # 각 Deployment에 toleration 및 nodeSelector 추가
    for deploy in $(kubectl get deployments -n $ns --no-headers | awk '{print $1}'); do
        echo "마이그레이션 중: $deploy"
        
        # Deployment 패치
        kubectl patch deployment $deploy -n $ns -p '{
            "spec": {
                "template": {
                    "spec": {
                        "tolerations": [
                            {
                                "key": "karpenter-version",
                                "value": "v1",
                                "effect": "NoSchedule"
                            }
                        ],
                        "nodeSelector": {
                            "karpenter-version": "v1"
                        }
                    }
                }
            }
        }'
        
        # 롤아웃 상태 확인
        kubectl rollout status deployment/$deploy -n $ns --timeout=300s
        
        if [ $? -eq 0 ]; then
            echo "✅ $deploy 마이그레이션 성공"
        else
            echo "❌ $deploy 마이그레이션 실패"
            exit 1
        fi
    done
    
    echo "=== $ns 네임스페이스 마이그레이션 완료 ==="
    sleep 30  # 안정화 대기
done
```

## 4. 검증 및 정리 단계

### 4.1 마이그레이션 검증

#### **Step 6: 전체 시스템 검증**
```bash
#!/bin/bash
echo "=== Karpenter v1.5 업그레이드 검증 ==="

# 1. Karpenter v1 컨트롤러 상태 확인
echo "1. Karpenter v1 컨트롤러 상태:"
kubectl get pods -n karpenter-v1
kubectl logs -n karpenter-v1 deployment/karpenter-v1 --tail=50

# 2. NodePool 상태 확인
echo "2. NodePool 상태:"
kubectl get nodepool
kubectl get ec2nodeclass

# 3. 노드 상태 확인
echo "3. 새로운 노드 상태:"
kubectl get nodes -l karpenter-version=v1

# 4. 워크로드 상태 확인
echo "4. 워크로드 상태:"
kubectl get pods -A -o wide | grep -v kube-system

# 5. 리소스 사용량 확인
echo "5. 리소스 사용량:"
kubectl top nodes
kubectl top pods -A

# 6. 이벤트 확인
echo "6. 최근 이벤트:"
kubectl get events --sort-by='.lastTimestamp' | tail -20
```

### 4.2 기존 Karpenter v0.37 정리

#### **Step 7: 안전한 구버전 제거**
```bash
#!/bin/bash
echo "=== 기존 Karpenter v0.37 정리 시작 ==="

# 1. 기존 노드 드레인 및 제거
echo "1. 기존 노드 드레인:"
for node in $(kubectl get nodes -l karpenter.sh/provisioner-name --no-headers | awk '{print $1}'); do
    echo "드레인 중: $node"
    kubectl drain $node --ignore-daemonsets --delete-emptydir-data --force --timeout=300s
    
    if [ $? -eq 0 ]; then
        echo "✅ $node 드레인 완료"
    else
        echo "❌ $node 드레인 실패"
    fi
done

# 2. 기존 Provisioner 및 AWSNodePool 제거
echo "2. 기존 리소스 제거:"
kubectl delete provisioner --all
kubectl delete awsnodepool --all

# 3. 기존 Karpenter v0.37 제거
echo "3. Karpenter v0.37 제거:"
helm uninstall karpenter -n karpenter

# 4. 네임스페이스 정리
kubectl delete namespace karpenter

echo "=== 기존 Karpenter v0.37 정리 완료 ==="
```

### 4.3 최종 설정 최적화

#### **Step 8: v1.5 설정 최적화**
```bash
#!/bin/bash
# Karpenter v1을 기본 네임스페이스로 이동
kubectl create namespace karpenter

# 기존 v1 설치 제거 후 재설치
helm uninstall karpenter-v1 -n karpenter-v1

# 최종 설치
helm install karpenter karpenter/karpenter \
  --version "1.5.0" \
  --namespace "karpenter" \
  --create-namespace \
  --set "settings.clusterName=your-cluster-name" \
  --set "settings.interruptionQueue=your-cluster-name" \
  --set "controller.resources.requests.cpu=1" \
  --set "controller.resources.requests.memory=1Gi" \
  --set "controller.resources.limits.cpu=2" \
  --set "controller.resources.limits.memory=2Gi" \
  --wait

# NodePool 최적화
kubectl apply -f - <<EOF
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["m5.large", "m5.xlarge", "m5.2xlarge", "c5.large", "c5.xlarge"]
      nodeClassRef:
        apiVersion: karpenter.k8s.aws/v1
        kind: EC2NodeClass
        name: default
  limits:
    cpu: 1000
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 30s
EOF
```

## 5. 롤백 계획

### 5.1 긴급 롤백 절차
```bash
#!/bin/bash
echo "=== 긴급 롤백 시작 ==="

# 1. Karpenter v1.5 중지
kubectl scale deployment karpenter -n karpenter --replicas=0

# 2. 백업에서 v0.37 복원
kubectl apply -f karpenter-backup-*/provisioners.yaml
kubectl apply -f karpenter-backup-*/awsnodepools.yaml

# 3. v0.37 재설치
helm install karpenter karpenter/karpenter \
  --version "0.37.0" \
  --namespace "karpenter" \
  --create-namespace

echo "=== 긴급 롤백 완료 ==="
```

## 6. 모니터링 및 알림 설정

### 6.1 업그레이드 모니터링
```yaml
# karpenter-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: karpenter-monitoring
  namespace: karpenter
data:
  alerts.yaml: |
    groups:
    - name: karpenter-upgrade
      rules:
      - alert: KarpenterNodeProvisioningFailed
        expr: increase(karpenter_nodes_created_total[5m]) == 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Karpenter 노드 프로비저닝 실패"
      
      - alert: KarpenterHighMemoryUsage
        expr: container_memory_usage_bytes{pod=~"karpenter.*"} / container_spec_memory_limit_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Karpenter 메모리 사용량 높음"
```

## 7. 업그레이드 체크리스트

### 7.1 사전 체크리스트
- [ ] 현재 환경 백업 완료
- [ ] EKS 버전 호환성 확인
- [ ] 네트워크 태그 사전 적용
- [ ] 테스트 환경에서 업그레이드 검증
- [ ] 롤백 계획 수립
- [ ] 모니터링 설정 완료

### 7.2 업그레이드 실행 체크리스트
- [ ] Blue-Green 환경 구성
- [ ] Karpenter v1.5 병렬 설치
- [ ] 테스트 워크로드 마이그레이션
- [ ] 프로덕션 워크로드 점진적 마이그레이션
- [ ] 전체 시스템 검증
- [ ] 기존 버전 정리

### 7.3 사후 체크리스트
- [ ] 성능 모니터링 (24시간)
- [ ] 비용 최적화 확인
- [ ] 문서 업데이트
- [ ] 팀 교육 실시
- [ ] 다음 업그레이드 계획 수립

## 8. 예상 다운타임 및 영향도

### 8.1 다운타임 예상
- **전체 업그레이드 시간**: 4-6시간
- **실제 서비스 다운타임**: 15-30분 (워크로드별 순차 마이그레이션)
- **완전 안정화**: 24시간

### 8.2 위험 요소 및 대응
- **노드 프로비저닝 실패**: 즉시 롤백
- **워크로드 스케줄링 실패**: 기존 노드로 임시 복원
- **네트워크 연결 문제**: 태그 설정 재확인

이 전략을 통해 안전하고 체계적인 Karpenter 업그레이드를 수행할 수 있습니다.
