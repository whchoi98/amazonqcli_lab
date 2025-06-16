# EKS v1.30 → v1.33 업그레이드 유의사항 가이드

## 업그레이드 개요

### 업그레이드 경로
- **v1.30** → **v1.31** → **v1.32** → **v1.33**
- **단계별 업그레이드 필수** (한 번에 여러 버전 업그레이드 불가)

### 전체 업그레이드 일정
- **예상 소요 시간**: 각 버전당 2-4시간 (총 8-16시간)
- **권장 업그레이드 간격**: 각 버전 간 1-2주 안정화 기간

## 주요 Breaking Changes 및 유의사항

### 1. EKS v1.33 주요 변경사항

#### **🚨 Amazon Linux 2 AMI 지원 중단**
```bash
# ❌ EKS 1.33부터 AL2 AMI 제공 중단
# ✅ 마이그레이션 필요
```

**필수 조치:**
- **Amazon Linux 2023 (AL2023)** 또는 **Bottlerocket**으로 마이그레이션
- **EKS Auto Mode** 채택 고려

**마이그레이션 방법:**
```bash
# AL2023으로 마이그레이션
aws eks create-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name al2023-nodes \
  --ami-type AL2023_x86_64_STANDARD \
  --instance-types m5.large \
  --subnets subnet-xxx subnet-yyy

# 기존 AL2 노드 그룹 제거
aws eks delete-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name al2-nodes
```

#### **Dynamic Resource Allocation (Beta) 활성화**
- GPU 등 특수 리소스 스케줄링 개선
- Beta API 사용 시 주의 (향후 변경 가능성)

#### **Sidecar Containers 안정화**
```yaml
# Sidecar 컨테이너 새로운 구문
apiVersion: v1
kind: Pod
spec:
  initContainers:
  - name: sidecar
    image: sidecar:latest
    restartPolicy: Always  # 새로운 필드
  containers:
  - name: app
    image: app:latest
```

#### **Endpoints API 공식 Deprecated**
```bash
# ❌ Deprecated (경고 메시지 발생)
kubectl get endpoints

# ✅ 권장 대안
kubectl get endpointslices
```

**마이그레이션 필요:**
```yaml
# 기존 코드 수정 필요
# endpoints → endpointslices API 사용
```

#### **EFA (Elastic Fabric Adapter) 지원**
- 기본 보안 그룹에 EFA 트래픽 규칙 자동 추가
- AI/ML 워크로드 성능 향상

### 2. EKS v1.32 주요 변경사항

#### **FlowSchema API 제거**
```yaml
# ❌ 제거된 API (v1.32부터)
apiVersion: flowcontrol.apiserver.k8s.io/v1beta3
kind: FlowSchema

# ✅ 최신 API 사용 필요
apiVersion: flowcontrol.apiserver.k8s.io/v1
kind: FlowSchema
```

#### **ServiceAccount 어노테이션 Deprecated**
```yaml
# ❌ Deprecated
metadata:
  annotations:
    kubernetes.io/enforce-mountable-secrets: "true"

# ✅ 네임스페이스 분리 권장
```

#### **Anonymous Authentication 제한 (v1.32)**
```bash
# 허용되는 익명 접근 엔드포인트
/healthz
/livez  
/readyz

# 기타 모든 엔드포인트: 401 Unauthorized
```

### 3. EKS v1.31 주요 변경사항

#### **kubelet 플래그 제거**
```bash
# ❌ 제거된 플래그 (v1.31부터)
--keep-terminated-pod-volumes

# 부트스트랩 스크립트에서 제거 필요
```

#### **VolumeAttributesClass Beta 활성화**
```yaml
# 새로운 기능: 볼륨 속성 동적 변경
apiVersion: storage.k8s.io/v1beta1
kind: VolumeAttributesClass
metadata:
  name: fast-ssd
spec:
  driverName: ebs.csi.aws.com
  parameters:
    type: gp3
    throughput: "1000"
```

#### **AppArmor 안정화**
```yaml
# 기존 어노테이션 방식 (Deprecated)
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: runtime/default

# 새로운 필드 방식 (권장)
spec:
  containers:
  - name: app
    securityContext:
      appArmorProfile:
        type: RuntimeDefault
```

### 4. EKS v1.30 주요 변경사항

#### **기본 AMI 변경**
```bash
# v1.30부터 새 노드 그룹 기본값
# AL2 → AL2023 변경
```

#### **Zone ID 라벨 추가**
```yaml
# 새로 추가되는 노드 라벨
topology.k8s.aws/zone-id: use1-az1
```

#### **gp2 StorageClass 기본값 제거**
```yaml
# 기존 (v1.29 이하)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"  # 자동 추가됨
  name: gp2

# v1.30부터 기본 어노테이션 제거됨
# 명시적으로 StorageClass 지정 필요
```

#### **IAM 권한 추가 요구**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeAvailabilityZones"  // 새로 추가 필요
      ],
      "Resource": "*"
    }
  ]
}
```

## 단계별 업그레이드 전략

### Phase 1: v1.30 → v1.31

#### **사전 준비**
```bash
# 1. kubelet 플래그 확인 및 제거
# 노드 그룹 Launch Template 확인
aws ec2 describe-launch-template-versions \
  --launch-template-id lt-xxx \
  --query 'LaunchTemplateVersions[0].LaunchTemplateData.UserData'

# 2. AppArmor 어노테이션 → 필드 마이그레이션
kubectl get pods -A -o yaml | grep "apparmor.security.beta"
```

#### **업그레이드 실행**
```bash
# 컨트롤 플레인 업그레이드
aws eks update-cluster-version \
  --name my-cluster \
  --version 1.31

# 노드 그룹 업그레이드 (Launch Template 수정 후)
aws eks update-nodegroup-version \
  --cluster-name my-cluster \
  --nodegroup-name my-nodegroup
```

### Phase 2: v1.31 → v1.32

#### **사전 준비**
```bash
# 1. FlowSchema API 버전 확인
kubectl get flowschema -o yaml | grep "apiVersion.*v1beta3"

# 2. ServiceAccount 어노테이션 확인
kubectl get serviceaccounts -A -o yaml | grep "enforce-mountable-secrets"

# 3. Anonymous 접근 테스트
curl -k https://cluster-endpoint/api/v1/namespaces  # 401 예상
```

#### **업그레이드 실행**
```bash
# 컨트롤 플레인 업그레이드
aws eks update-cluster-version \
  --name my-cluster \
  --version 1.32
```

### Phase 3: v1.32 → v1.33

#### **사전 준비 (가장 중요)**
```bash
# 1. AL2 노드 그룹 확인
aws eks describe-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name my-nodegroup \
  --query 'nodegroup.amiType'

# 2. AL2023 노드 그룹 생성
aws eks create-nodegroup \
  --cluster-name my-cluster \
  --nodegroup-name al2023-nodes \
  --ami-type AL2023_x86_64_STANDARD

# 3. 워크로드 마이그레이션
kubectl drain node-name --ignore-daemonsets --delete-emptydir-data

# 4. Endpoints API 사용 확인
grep -r "endpoints" . --include="*.yaml" --include="*.go"
```

#### **업그레이드 실행**
```bash
# 컨트롤 플레인 업그레이드
aws eks update-cluster-version \
  --name my-cluster \
  --version 1.33

# AL2023 노드 그룹만 유지
```

## 애드온 호환성 확인

### 필수 애드온 업그레이드

#### **AWS Load Balancer Controller**
```bash
# v1.33 호환 버전: v2.13.0+
helm upgrade aws-load-balancer-controller eks/aws-load-balancer-controller \
  --version 1.13.0 \
  -n kube-system
```

#### **Amazon EBS CSI Driver**
```bash
# VolumeAttributesClass 지원: v1.35.0+
aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name aws-ebs-csi-driver \
  --addon-version v1.35.0-eksbuild.1
```

#### **VPC CNI**
```bash
# 최신 버전으로 업그레이드
aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name vpc-cni \
  --addon-version v1.18.1-eksbuild.1
```

#### **CoreDNS**
```bash
# EKS 1.33 호환 버전
aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name coredns \
  --addon-version v1.11.1-eksbuild.8
```

## 검증 및 테스트

### 업그레이드 후 검증 스크립트

```bash
#!/bin/bash
echo "=== EKS 업그레이드 검증 ==="

# 1. 클러스터 버전 확인
echo "클러스터 버전:"
aws eks describe-cluster --name my-cluster --query 'cluster.version'

# 2. 노드 상태 확인
echo "노드 상태:"
kubectl get nodes -o wide

# 3. 파드 상태 확인
echo "파드 상태:"
kubectl get pods -A | grep -v Running

# 4. 애드온 상태 확인
echo "애드온 상태:"
aws eks list-addons --cluster-name my-cluster

# 5. API 접근 테스트
echo "API 접근 테스트:"
kubectl get namespaces > /dev/null && echo "✅ API 정상" || echo "❌ API 오류"

# 6. 워크로드 테스트
echo "워크로드 테스트:"
kubectl run test-pod --image=nginx --rm -it --restart=Never -- curl -s http://kubernetes.default.svc.cluster.local
```

## 롤백 계획

### 긴급 롤백 절차
```bash
# 1. 노드 그룹 롤백 (가능한 경우)
aws eks update-nodegroup-version \
  --cluster-name my-cluster \
  --nodegroup-name my-nodegroup \
  --launch-template version=previous

# 2. 애드온 롤백
aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name aws-load-balancer-controller \
  --addon-version previous-version

# 3. 워크로드 재배포
kubectl rollout undo deployment/my-app
```

## 업그레이드 체크리스트

### 사전 체크리스트
- [ ] 현재 환경 백업 완료
- [ ] AL2 → AL2023 마이그레이션 계획 수립
- [ ] FlowSchema API 버전 확인 및 수정
- [ ] Endpoints → EndpointSlices 마이그레이션
- [ ] AppArmor 어노테이션 → 필드 변경
- [ ] kubelet 플래그 제거
- [ ] IAM 권한 업데이트
- [ ] 애드온 호환성 확인

### 업그레이드 실행 체크리스트
- [ ] v1.30 → v1.31 업그레이드 완료
- [ ] v1.31 → v1.32 업그레이드 완료
- [ ] v1.32 → v1.33 업그레이드 완료
- [ ] 모든 애드온 업그레이드 완료
- [ ] AL2023 노드 그룹 마이그레이션 완료

### 사후 검증 체크리스트
- [ ] 클러스터 상태 정상 확인
- [ ] 모든 워크로드 정상 동작 확인
- [ ] 네트워킹 정상 동작 확인
- [ ] 스토리지 정상 동작 확인
- [ ] 모니터링 및 로깅 정상 확인

## 예상 다운타임 및 위험도

### 다운타임 예상
- **컨트롤 플레인 업그레이드**: 각 버전당 10-15분
- **노드 그룹 업그레이드**: 각 버전당 30-60분
- **AL2 → AL2023 마이그레이션**: 1-2시간

### 위험도 평가
- **v1.30 → v1.31**: 중간 (kubelet 플래그 제거)
- **v1.31 → v1.32**: 높음 (Anonymous auth 제한, API 제거)
- **v1.32 → v1.33**: 매우 높음 (AL2 AMI 지원 중단)

이 가이드를 따라 단계별로 신중하게 업그레이드를 진행하시기 바랍니다.
