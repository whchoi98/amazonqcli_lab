# Karpenter 0.37 → 1.5 업그레이드 시 VPC/보안그룹/서브넷 태그 재검토 이유

## 1. Karpenter 0.37 vs 1.5 주요 변경사항

### 1.1 아키텍처 변경 (v0.37 → v1.0+)

#### **Beta → Stable API 전환**
- **v0.37**: `karpenter.sh/v1beta1` API 사용
- **v1.5**: `karpenter.sh/v1` API 사용 (완전히 안정화된 API)

#### **NodePool과 EC2NodeClass 도입**


```yaml
# v1.5 (NodePool + EC2NodeClass)
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      nodeClassRef:
        apiVersion: karpenter.k8s.aws/v1
        kind: EC2NodeClass
        name: default
---
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
```

### 1.2 태그 검색 및 관리 방식의 근본적 변화

#### **v0.37의 태그 검색 방식:**
- 단순한 태그 매칭
- 느슨한 검증 로직
- 기본 태그만으로 리소스 식별

#### **v1.5의 태그 검색 방식:**
- **엄격한 태그 검증**
- **계층적 태그 구조 요구**
- **성능 최적화된 리소스 검색**
- **보안 강화된 리소스 격리**

## 2. 태그 구조 변경이 필요한 구체적 이유

### 2.1 서브넷 태그 요구사항 변화

#### **v0.37에서 충분했던 태그:**
```bash
# 기본 클러스터 태그만으로 동작
kubernetes.io/cluster/<cluster-name> = owned
```

#### **v1.5에서 필요한 태그:**
```bash
# 클러스터 식별
kubernetes.io/cluster/<cluster-name> = shared

# Karpenter 전용 검색 태그 (필수)
karpenter.sh/discovery = <cluster-name>

# 역할별 서브넷 구분 (강화됨)
kubernetes.io/role/elb = 1                    # 퍼블릭 서브넷
kubernetes.io/role/internal-elb = 1           # 프라이빗 서브넷

# 새로 추가된 성능 최적화 태그
karpenter.k8s.aws/cluster = <cluster-name>
```

### 2.2 보안 그룹 태그 요구사항 강화

#### **v0.37 보안 그룹 태그:**
```bash
kubernetes.io/cluster/<cluster-name> = owned
```

#### **v1.5 보안 그룹 태그:**
```bash
# 기본 클러스터 태그
kubernetes.io/cluster/<cluster-name> = owned

# Karpenter 검색 태그 (필수)
karpenter.sh/discovery = <cluster-name>

# NodePool별 세분화 (새로 추가)
karpenter.sh/nodepool = <nodepool-name>

# 역할별 보안 그룹 구분 (새로 추가)
karpenter.k8s.aws/security-group-type = cluster|node|additional
```

### 2.3 VPC 태그 요구사항

#### **v0.37 VPC 태그:**
```bash
kubernetes.io/cluster/<cluster-name> = shared
```

#### **v1.5 VPC 태그:**
```bash
# 기본 클러스터 태그
kubernetes.io/cluster/<cluster-name> = shared

# Karpenter 검색 최적화 (새로 추가)
karpenter.sh/discovery = <cluster-name>

# 네트워크 성능 최적화 태그 (새로 추가)
karpenter.k8s.aws/vpc-id = <vpc-id>
```

## 3. 변경이 필요한 핵심 이유

### 3.1 성능 최적화

#### **v0.37의 리소스 검색:**
- 모든 리소스를 순차적으로 스캔
- 태그 기반 필터링이 비효율적
- API 호출 횟수가 많음

#### **v1.5의 리소스 검색:**
- `karpenter.sh/discovery` 태그로 즉시 필터링
- 계층적 태그 구조로 빠른 검색
- API 호출 최소화

### 3.2 보안 강화

#### **v0.37의 보안 모델:**
- 클러스터 레벨에서만 리소스 격리
- 느슨한 권한 관리

#### **v1.5의 보안 모델:**
- NodePool 레벨에서 세분화된 격리
- 역할 기반 리소스 접근 제어
- 최소 권한 원칙 적용

### 3.3 안정성 향상

#### **v0.37의 리소스 관리:**
- 태그 불일치 시 예측 불가능한 동작
- 리소스 충돌 가능성

#### **v1.5의 리소스 관리:**
- 엄격한 태그 검증으로 오류 방지
- 명확한 리소스 소유권 관리

## 4. 마이그레이션 체크리스트

### 4.1 현재 태그 상태 확인

```bash
#!/bin/bash
CLUSTER_NAME="your-cluster-name"
VPC_ID="your-vpc-id"

echo "=== 현재 VPC 태그 확인 ==="
aws ec2 describe-vpcs --vpc-ids $VPC_ID --query 'Vpcs[0].Tags'

echo "=== 현재 서브넷 태그 확인 ==="
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[*].[SubnetId,Tags[?Key==`karpenter.sh/discovery`].Value]'

echo "=== 현재 보안 그룹 태그 확인 ==="
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[*].[GroupId,Tags[?Key==`karpenter.sh/discovery`].Value]'
```

### 4.2 필수 태그 업데이트 스크립트

```bash
#!/bin/bash
CLUSTER_NAME="your-cluster-name"
VPC_ID="your-vpc-id"

echo "=== VPC 태그 업데이트 ==="
aws ec2 create-tags --resources $VPC_ID --tags \
  Key=karpenter.sh/discovery,Value=$CLUSTER_NAME \
  Key=karpenter.k8s.aws/vpc-id,Value=$VPC_ID

echo "=== 퍼블릭 서브넷 태그 업데이트 ==="
for subnet in $(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" \
  --query 'Subnets[*].SubnetId' --output text); do
  
  aws ec2 create-tags --resources $subnet --tags \
    Key=karpenter.sh/discovery,Value=$CLUSTER_NAME \
    Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared \
    Key=kubernetes.io/role/elb,Value=1 \
    Key=karpenter.k8s.aws/cluster,Value=$CLUSTER_NAME
done

echo "=== 프라이빗 서브넷 태그 업데이트 ==="
for subnet in $(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=false" \
  --query 'Subnets[*].SubnetId' --output text); do
  
  aws ec2 create-tags --resources $subnet --tags \
    Key=karpenter.sh/discovery,Value=$CLUSTER_NAME \
    Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared \
    Key=kubernetes.io/role/internal-elb,Value=1 \
    Key=karpenter.k8s.aws/cluster,Value=$CLUSTER_NAME
done

echo "=== 보안 그룹 태그 업데이트 ==="
# 클러스터 보안 그룹 찾기 및 태그 업데이트
CLUSTER_SG=$(aws eks describe-cluster --name $CLUSTER_NAME \
  --query 'cluster.resourcesVpcConfig.clusterSecurityGroupId' --output text)

if [ "$CLUSTER_SG" != "None" ]; then
  aws ec2 create-tags --resources $CLUSTER_SG --tags \
    Key=karpenter.sh/discovery,Value=$CLUSTER_NAME \
    Key=karpenter.k8s.aws/security-group-type,Value=cluster
fi

# 노드 그룹 보안 그룹 태그 업데이트
for sg in $(aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:kubernetes.io/cluster/$CLUSTER_NAME,Values=owned" \
  --query 'SecurityGroups[*].GroupId' --output text); do
  
  aws ec2 create-tags --resources $sg --tags \
    Key=karpenter.sh/discovery,Value=$CLUSTER_NAME \
    Key=karpenter.k8s.aws/security-group-type,Value=node
done
```

### 4.3 검증 스크립트

```bash
#!/bin/bash
CLUSTER_NAME="your-cluster-name"

echo "=== Karpenter v1.5 태그 요구사항 검증 ==="

# 서브넷 검증
echo "서브넷 태그 검증:"
aws ec2 describe-subnets \
  --filters "Name=tag:karpenter.sh/discovery,Values=$CLUSTER_NAME" \
  --query 'Subnets[*].[SubnetId,Tags[?Key==`kubernetes.io/role/elb`||Key==`kubernetes.io/role/internal-elb`].Key]' \
  --output table

# 보안 그룹 검증
echo "보안 그룹 태그 검증:"
aws ec2 describe-security-groups \
  --filters "Name=tag:karpenter.sh/discovery,Values=$CLUSTER_NAME" \
  --query 'SecurityGroups[*].[GroupId,Tags[?Key==`karpenter.k8s.aws/security-group-type`].Value]' \
  --output table

# VPC 검증
echo "VPC 태그 검증:"
aws ec2 describe-vpcs \
  --filters "Name=tag:karpenter.sh/discovery,Values=$CLUSTER_NAME" \
  --query 'Vpcs[*].[VpcId,Tags[?Key==`karpenter.k8s.aws/vpc-id`].Value]' \
  --output table
```

## 5. 업그레이드 후 확인사항

### 5.1 Karpenter 로그 확인
```bash
kubectl logs -n karpenter deployment/karpenter -f
```

### 5.2 NodePool 상태 확인
```bash
kubectl get nodepool -o wide
kubectl get ec2nodeclass -o wide
```

### 5.3 노드 프로비저닝 테스트
```bash
# 테스트 파드 배포
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
      - name: test
        image: nginx
        resources:
          requests:
            cpu: 1
            memory: 1Gi
EOF
```

## 6. 결론

Karpenter 0.37에서 1.5로 업그레이드 시 태그 구조 재검토가 필요한 이유:

1. **API 안정화**: Beta → Stable API 전환으로 인한 엄격한 검증
2. **성능 최적화**: `karpenter.sh/discovery` 태그 기반 빠른 리소스 검색
3. **보안 강화**: NodePool 레벨 세분화된 리소스 격리
4. **안정성 향상**: 명확한 태그 구조로 리소스 충돌 방지
5. **호환성 보장**: AWS Load Balancer Controller와의 완벽한 통합

이러한 변경사항을 적용하지 않으면 Karpenter v1.5에서 노드 프로비저닝 실패, 성능 저하, 보안 취약점 등의 문제가 발생할 수 있습니다.
