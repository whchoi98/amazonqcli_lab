# Karpenter v1.5 + EKS 1.33 환경에서 AWS Load Balancer Controller 추천 버전

## 추천 버전: **v2.13.2** (최신 안정 버전)

### 버전 호환성 정보

#### 현재 환경
- **Karpenter**: v1.5.0 (2025년 5월 23일 릴리스)
- **EKS**: 1.33
- **추천 LBC**: v2.13.2 (2025년 5월 15일 릴리스)

#### 호환성 근거

1. **최신 안정 버전**: v2.13.2는 현재 가장 최신의 안정 버전입니다.

2. **EKS 1.33 지원**: AWS Load Balancer Controller v2.13.x 시리즈는 최신 EKS 버전들을 완전히 지원합니다.

3. **Karpenter 호환성**: Karpenter v1.5.0과 LBC v2.13.2는 동일한 시기에 릴리스되어 상호 호환성이 보장됩니다.

### 설치 방법 (Helm 사용)

```bash
# Helm 차트 저장소 추가
helm repo add eks https://aws.github.io/eks-charts
helm repo update eks

# AWS Load Balancer Controller 설치
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=<your-cluster-name> \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --version 1.13.2
```

### 주요 기능 및 개선사항

#### v2.13.x 시리즈의 주요 특징:
- **향상된 보안**: 최신 보안 패치 적용
- **성능 최적화**: 더 나은 리소스 관리 및 응답 시간
- **EKS 최신 버전 지원**: EKS 1.33과 완전 호환
- **Karpenter 통합**: 노드 스케일링과 로드 밸런싱의 원활한 연동

#### 주요 기능:
- **Application Load Balancer (ALB)** 지원 (Kubernetes Ingress)
- **Network Load Balancer (NLB)** 지원 (LoadBalancer 타입 서비스)
- **IP 및 Instance 타겟 모드** 지원
- **AWS WAF 통합** 지원
- **SSL/TLS 종료** 지원

### 업그레이드 시 주의사항

1. **기존 설치가 있는 경우**:
   ```bash
   # 업그레이드 전 CRD 업데이트
   wget https://raw.githubusercontent.com/aws/eks-charts/master/stable/aws-load-balancer-controller/crds/crds.yaml
   kubectl apply -f crds.yaml
   
   # Helm 업그레이드
   helm upgrade aws-load-balancer-controller eks/aws-load-balancer-controller \
     -n kube-system \
     --version 1.13.2
   ```

2. **IAM 정책 확인**: 최신 IAM 정책이 적용되어 있는지 확인
   ```bash
   curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.13.2/docs/install/iam_policy.json
   ```

### 검증 방법

설치 후 다음 명령어로 정상 동작을 확인하세요:

```bash
# 컨트롤러 파드 상태 확인
kubectl get deployment -n kube-system aws-load-balancer-controller

# 로그 확인
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# 버전 확인
kubectl get deployment aws-load-balancer-controller -n kube-system -o yaml | grep image:
```

### 결론

Karpenter v1.5와 EKS 1.33 환경에서는 **AWS Load Balancer Controller v2.13.2**를 사용하는 것을 강력히 추천합니다. 이 조합은 최신 기능, 보안 패치, 그리고 최적의 성능을 제공합니다.
