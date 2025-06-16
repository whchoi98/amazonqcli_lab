# AWS Load Balancer Controller - IRSA 및 VPC 태그 구조 재검토 가이드

## 1. IRSA (IAM Roles for Service Accounts) 적용 여부 및 IAM 정책 확인

### 1.1 기존 대비 세분화된 IAM 정책의 이유

#### v2.13.x에서 변경된 주요 권한들:

**새로 추가된 권한:**
```json
{
    "Effect": "Allow",
    "Action": [
        "ec2:DescribeAvailabilityZones",
        "ec2:DescribeAccountAttributes",
        "ec2:DescribeAddresses",
        "ec2:DescribeInternetGateways",
        "ec2:DescribeVpcPeeringConnections",
        "ec2:DescribeInstances",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DescribeVpcs",
        "ec2:DescribeRegions",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "elasticloadbalancing:DescribeLoadBalancers",
        "elasticloadbalancing:DescribeLoadBalancerAttributes",
        "elasticloadbalancing:DescribeListeners",
        "elasticloadbalancing:DescribeListenerCertificates",
        "elasticloadbalancing:DescribeSSLPolicies",
        "elasticloadbalancing:DescribeRules",
        "elasticloadbalancing:DescribeTargetGroups",
        "elasticloadbalancing:DescribeTargetGroupAttributes",
        "elasticloadbalancing:DescribeTargetHealth",
        "elasticloadbalancing:DescribeTags"
    ],
    "Resource": "*"
}
```

**세분화된 리소스별 권한:**
```json
{
    "Effect": "Allow",
    "Action": [
        "cognito-idp:DescribeUserPoolClient",
        "acm:ListCertificates",
        "acm:DescribeCertificate",
        "iam:CreateServiceLinkedRole"
    ],
    "Resource": "*"
}
```

### 1.2 IRSA 설정 확인 방법

```bash
# 1. 현재 IRSA 설정 확인
kubectl get serviceaccount aws-load-balancer-controller -n kube-system -o yaml

# 2. OIDC 제공자 확인
aws eks describe-cluster --name <cluster-name> --query "cluster.identity.oidc.issuer" --output text

# 3. IAM 역할 신뢰 정책 확인
aws iam get-role --role-name AmazonEKSLoadBalancerControllerRole --query 'Role.AssumeRolePolicyDocument'
```

### 1.3 최신 IAM 정책 적용

```bash
# 최신 IAM 정책 다운로드
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.13.2/docs/install/iam_policy.json

# 기존 정책 업데이트
aws iam put-role-policy \
    --role-name AmazonEKSLoadBalancerControllerRole \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json
```

## 2. VPC 태그, 보안그룹, 서브넷 태그 구조 재검토 이유

### 2.1 Karpenter v1.5 + EKS 1.33 환경에서의 변경사항

#### **주요 변경 이유:**

1. **Karpenter의 노드 프로비저닝 방식 변화**
2. **EKS 1.33의 새로운 네트워킹 기능**
3. **AWS Load Balancer Controller의 향상된 서브넷 선택 로직**
4. **보안 그룹 관리 방식의 개선**

### 2.2 필수 VPC 태그 구조

#### **클러스터 레벨 태그:**
```bash
# VPC 태그
kubernetes.io/cluster/<cluster-name> = shared|owned

# 퍼블릭 서브넷 태그 (ALB용)
kubernetes.io/cluster/<cluster-name> = shared|owned
kubernetes.io/role/elb = 1

# 프라이빗 서브넷 태그 (NLB용)
kubernetes.io/cluster/<cluster-name> = shared|owned
kubernetes.io/role/internal-elb = 1
```

#### **Karpenter 관련 추가 태그:**
```bash
# Karpenter가 사용할 서브넷
karpenter.sh/discovery = <cluster-name>

# 보안 그룹
karpenter.sh/discovery = <cluster-name>
```

### 2.3 보안 그룹 태그 구조 재검토

#### **기존 vs 새로운 구조:**

**기존 구조:**
```bash
kubernetes.io/cluster/<cluster-name> = owned
```

**새로운 구조 (v1.5 + EKS 1.33):**
```bash
# 클러스터 보안 그룹
kubernetes.io/cluster/<cluster-name> = owned
kubernetes.io/created-for/pvc/namespace = <namespace>
kubernetes.io/created-for/pvc/name = <pvc-name>

# Karpenter 노드 보안 그룹
karpenter.sh/discovery = <cluster-name>
karpenter.sh/nodepool = <nodepool-name>

# Load Balancer 보안 그룹
elbv2.k8s.aws/cluster = <cluster-name>
elbv2.k8s.aws/resource = LoadBalancer
```

### 2.4 서브넷 태그 세분화

#### **ALB를 위한 퍼블릭 서브넷:**
```bash
kubernetes.io/cluster/<cluster-name> = shared
kubernetes.io/role/elb = 1
# 새로 추가
elbv2.k8s.aws/cluster = <cluster-name>
karpenter.sh/discovery = <cluster-name>  # Karpenter가 퍼블릭 서브넷도 인식하도록
```

#### **NLB를 위한 프라이빗 서브넷:**
```bash
kubernetes.io/cluster/<cluster-name> = shared
kubernetes.io/role/internal-elb = 1
# 새로 추가
elbv2.k8s.aws/cluster = <cluster-name>
karpenter.sh/discovery = <cluster-name>
```

### 2.5 재검토가 필요한 이유

#### **1. 향상된 서브넷 자동 검색:**
- LBC v2.13.x는 더 정교한 서브넷 선택 알고리즘 사용
- 잘못된 태그로 인한 서브넷 선택 오류 방지

#### **2. Karpenter와의 통합:**
- Karpenter v1.5는 더 엄격한 태그 검증 수행
- 노드 프로비저닝 시 네트워크 리소스 충돌 방지

#### **3. 보안 강화:**
- 세분화된 보안 그룹 태그로 리소스 격리 개선
- 의도하지 않은 네트워크 액세스 방지

#### **4. 성능 최적화:**
- 태그 기반 리소스 검색 성능 향상
- 불필요한 API 호출 감소

## 3. 검증 및 적용 방법

### 3.1 현재 태그 상태 확인

```bash
# VPC 태그 확인
aws ec2 describe-vpcs --vpc-ids <vpc-id> --query 'Vpcs[0].Tags'

# 서브넷 태그 확인
aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>" --query 'Subnets[*].[SubnetId,Tags]'

# 보안 그룹 태그 확인
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=<vpc-id>" --query 'SecurityGroups[*].[GroupId,Tags]'
```

### 3.2 태그 업데이트 스크립트

```bash
#!/bin/bash
CLUSTER_NAME="your-cluster-name"
VPC_ID="vpc-xxxxxxxxx"

# VPC 태그 업데이트
aws ec2 create-tags --resources $VPC_ID --tags Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared

# 퍼블릭 서브넷 태그 업데이트
for subnet in $(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" --query 'Subnets[*].SubnetId' --output text); do
    aws ec2 create-tags --resources $subnet --tags \
        Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared \
        Key=kubernetes.io/role/elb,Value=1 \
        Key=karpenter.sh/discovery,Value=$CLUSTER_NAME
done

# 프라이빗 서브넷 태그 업데이트
for subnet in $(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=false" --query 'Subnets[*].SubnetId' --output text); do
    aws ec2 create-tags --resources $subnet --tags \
        Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared \
        Key=kubernetes.io/role/internal-elb,Value=1 \
        Key=karpenter.sh/discovery,Value=$CLUSTER_NAME
done
```

## 4. 결론

Karpenter v1.5와 EKS 1.33 환경에서는:

1. **IRSA 정책 업데이트**: 세분화된 권한으로 보안 강화
2. **VPC 태그 재구성**: Karpenter와 LBC의 원활한 통합
3. **보안 그룹 태그 세분화**: 리소스 격리 및 보안 향상
4. **서브넷 태그 표준화**: 자동 검색 및 성능 최적화

이러한 변경사항을 적용하면 더 안정적이고 효율적인 Kubernetes 클러스터 운영이 가능합니다.
