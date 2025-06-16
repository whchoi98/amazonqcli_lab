# Karpenter NodePool 개념 도입 버전

## NodePool 개념이 생긴 버전: **Karpenter v1.0.0**

### 릴리스 정보
- **버전**: v1.0.0
- **릴리스 날짜**: 2024년 8월 14일
- **중요도**: Major Release (Breaking Changes)

## 주요 변경사항

### 1. API 구조 변화

#### **Before v1.0.0 (v0.37 이하)**
```yaml
# Provisioner (v1beta1)
apiVersion: karpenter.sh/v1beta1
kind: Provisioner
metadata:
  name: default
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot"]
  limits:
    resources:
      cpu: 1000
  providerRef:
    name: default
---
# AWSNodePool (v1beta1)
apiVersion: karpenter.k8s.aws/v1beta1
kind: AWSNodePool
metadata:
  name: default
spec:
  amiFamily: AL2
  subnetSelector:
    karpenter.sh/discovery: "cluster-name"
  securityGroupSelector:
    karpenter.sh/discovery: "cluster-name"
```

#### **After v1.0.0 (v1.0+)**
```yaml
# NodePool (v1)
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot"]
      nodeClassRef:
        apiVersion: karpenter.k8s.aws/v1
        kind: EC2NodeClass
        name: default
  limits:
    cpu: 1000
---
# EC2NodeClass (v1)
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: "cluster-name"
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: "cluster-name"
```

### 2. 개념적 변화

#### **NodePool의 새로운 역할**
- **통합된 노드 관리**: Provisioner의 기능을 흡수하여 단일 리소스로 통합
- **템플릿 기반 구조**: `template` 섹션을 통한 명확한 노드 템플릿 정의
- **향상된 스케줄링**: 더 정교한 노드 선택 및 배치 로직

#### **EC2NodeClass의 분리**
- **AWS 특화 설정**: AWS 관련 설정을 별도 리소스로 분리
- **재사용성**: 여러 NodePool에서 동일한 EC2NodeClass 참조 가능
- **명확한 책임 분리**: 인프라 설정과 스케줄링 정책의 분리

### 3. v1.0.0의 주요 기능

#### **새로운 기능들**
1. **Conversion Webhooks**: v1beta1에서 v1으로 자동 변환
2. **Enhanced AMI Selection**: 더 정교한 AMI 선택 로직
3. **Kubelet Configuration**: EC2NodeClass에서 kubelet 설정 지원
4. **Improved Tagging**: `eks:eks-cluster-name` 태그 자동 추가
5. **Disruption Budgets**: 더 세분화된 중단 예산 관리

#### **Breaking Changes**
1. **API Version**: `v1beta1` → `v1`
2. **Resource Names**: `Provisioner` → `NodePool`, `AWSNodePool` → `EC2NodeClass`
3. **Tag Requirements**: 더 엄격한 태그 검증
4. **Metrics Port**: 기본 메트릭 포트 변경
5. **Environment Variables**: 일부 환경 변수 제거

## 마이그레이션 영향

### 1. 자동 변환 지원
```bash
# v1.0.0부터 Conversion Webhook 지원
# 기존 v1beta1 리소스가 자동으로 v1으로 변환됨
kubectl get provisioner -o yaml  # 자동으로 NodePool로 변환되어 표시
```

### 2. 태그 요구사항 강화
```bash
# v1.0.0부터 필수 태그
karpenter.sh/discovery = <cluster-name>

# 자동 추가되는 태그
eks:eks-cluster-name = <cluster-name>
```

### 3. 새로운 선택자 구조
```yaml
# v0.37 이하
subnetSelector:
  karpenter.sh/discovery: "cluster-name"

# v1.0.0 이상
subnetSelectorTerms:
  - tags:
      karpenter.sh/discovery: "cluster-name"
```

## 업그레이드 고려사항

### 1. 호환성
- **EKS 버전**: 1.23+ 필요
- **Kubernetes**: 1.23+ 필요
- **Helm Chart**: 새로운 차트 구조

### 2. 기능 개선
- **성능**: 더 빠른 노드 프로비저닝
- **안정성**: 향상된 오류 처리
- **확장성**: 더 나은 대규모 클러스터 지원

### 3. 운영 변화
- **모니터링**: 새로운 메트릭 구조
- **로깅**: 향상된 로그 형식
- **디버깅**: 더 나은 문제 진단 도구

## 결론

**NodePool 개념은 Karpenter v1.0.0 (2024년 8월 14일)에서 도입되었습니다.**

이는 Karpenter의 가장 중요한 아키텍처 변화 중 하나로:

1. **API 안정화**: Beta에서 Stable API로 전환
2. **구조 개선**: 더 명확하고 유연한 리소스 구조
3. **기능 강화**: 향상된 노드 관리 및 스케줄링 기능
4. **운영 개선**: 더 나은 모니터링 및 디버깅 도구

v0.37에서 v1.5로 업그레이드 시에는 이러한 근본적인 변화를 이해하고 적절한 마이그레이션 전략을 수립하는 것이 중요합니다.
