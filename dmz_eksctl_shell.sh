#!/bin/bash
# dmz_eksctl_shell.sh: DMZPVPC용 eksctl yaml 생성 및 실행 스크립트
# Private subnet에 managed node group을 설치하도록 구성

set -e

echo "🚀 DMZPVPC EKS 클러스터 생성 시작"
echo 'export AWS_REGION=ap-northeast-2' >> ~/.bash_profile
source ~/.bash_profile

# 환경 변수 로드 확인
if [[ -z "$VPC_ID" || -z "$PrivateSubnetA" || -z "$PrivateSubnetB" ]]; then
    echo "❌ 환경 변수가 설정되지 않았습니다. 먼저 ./dmz_eks_shell.sh를 실행하세요."
    exit 1
fi

echo "📋 사용할 환경 변수:"
echo "   VPC_ID: $VPC_ID"
echo "   PrivateSubnetA: $PrivateSubnetA"
echo "   PrivateSubnetB: $PrivateSubnetB"
echo "   EKSCLUSTER_NAME: $EKSCLUSTER_NAME"
echo "   EKS_VERSION: $EKS_VERSION"

# EKS 클러스터 구성 YAML 파일 생성
cat << EOF > ~/amazonqcli_lab/dmz-eks-cluster.yaml
---
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: ${EKSCLUSTER_NAME}
  region: ${AWS_REGION}
  version: "${EKS_VERSION}"

vpc: 
  id: ${VPC_ID}
  subnets:
    private:
      PrivateSubnetA:
        az: ${AWS_REGION}a
        id: ${PrivateSubnetA}
      PrivateSubnetB:
        az: ${AWS_REGION}b
        id: ${PrivateSubnetB}

# Private subnet에만 managed node group 설치
managedNodeGroups:
  - name: ${PRIVATE_MGMD_NODE}
    instanceType: ${INSTANCE_TYPE}
    subnets:
      - ${PrivateSubnetA}
      - ${PrivateSubnetB}
    desiredCapacity: 8
    minSize: 4
    maxSize: 12
    volumeSize: 50
    volumeType: gp3
    volumeEncrypted: true
    amiFamily: AmazonLinux2
    labels:
      nodegroup-type: "${PRIVATE_MGMD_NODE}"
      environment: "dmz-private"
    privateNetworking: true
    iam:
      withAddonPolicies:
        autoScaler: true
        cloudWatch: true
        ebs: true
        fsx: true
        efs: true

cloudWatch:
  clusterLogging:
    enableTypes: ["api", "audit", "authenticator", "controllerManager", "scheduler"]

iam:
  withOIDC: true

addons:
- name: vpc-cni
  attachPolicyARNs:
    - arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
- name: coredns
  version: latest
- name: kube-proxy
  version: latest
- name: aws-ebs-csi-driver
  wellKnownPolicies:
    ebsCSIController: true
EOF

echo "✅ EKS 클러스터 구성 파일 생성 완료: ~/amazonqcli_lab/dmz-eks-cluster.yaml"
echo ""
echo "📄 생성된 구성 요약:"
echo "   - 클러스터 이름: ${EKSCLUSTER_NAME}"
echo "   - EKS 버전: ${EKS_VERSION}"
echo "   - VPC: ${VPC_ID}"
echo "   - Private Subnet A: ${PrivateSubnetA}"
echo "   - Private Subnet B: ${PrivateSubnetB}"
echo "   - Managed Node Group: ${PRIVATE_MGMD_NODE}"
echo "   - 인스턴스 타입: ${INSTANCE_TYPE}"
echo "   - 노드 수: 2 (최소 1, 최대 4)"
echo ""
echo "🚀 EKS 클러스터 생성을 시작합니다..."
echo "⏰ 예상 소요 시간: 15-20분"

# EKS 클러스터 생성 실행
eksctl create cluster -f ~/amazonqcli_lab/dmz-eks-cluster.yaml

echo ""
echo "🎉 EKS 클러스터 생성이 완료되었습니다!"
echo ""
echo "💡 다음 단계:"
echo "   1. kubectl 컨텍스트 확인: kubectl config current-context"
echo "   2. 노드 확인: kubectl get nodes"
echo "   3. 클러스터 정보 확인: kubectl cluster-info"
echo "   4. K9s로 클러스터 관리: k9s"
EOF
