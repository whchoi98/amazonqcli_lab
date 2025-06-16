#!/bin/bash

# DMZVPC에 EKS 클러스터를 배포하는 스크립트
# dmz_eks_shell.sh에 의해 자동 생성됨

set -e

# 환경 변수 로드
source ~/.bash_profile

echo "🚀 DMZVPC EKS 클러스터 배포 시작"
echo "======================================================"
echo "📋 배포 정보:"
echo "   - 클러스터 이름: ${EKSCLUSTER_NAME}"
echo "   - 버전: ${EKS_VERSION}"
echo "   - 리전: ap-northeast-2"
echo "   - VPC ID: ${VPCID}"
echo "   - Private Subnet A: ${PRIVATE_SUBNET_A}"
echo "   - Private Subnet B: ${PRIVATE_SUBNET_B}"
echo "   - 인스턴스 타입: ${INSTANCE_TYPE}"
echo "   - Managed 노드 그룹:"
echo "     · Public: ${PUBLIC_MGMD_NODE}"
echo "     · Private: ${PRIVATE_MGMD_NODE}"
echo "======================================================"

# EKS 클러스터 구성 파일 생성
echo ""
echo "🔄 EKS 클러스터 구성 파일 생성 중..."

cat > ~/amazonqcli_lab/eksworkshop.yaml << YAML_EOF
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: ${EKSCLUSTER_NAME}
  region: ap-northeast-2
  version: "${EKS_VERSION}"

vpc:
  id: "${VPCID}"
  subnets:
    private:
      private-subnet-a:
        id: "${PRIVATE_SUBNET_A}"
      private-subnet-b:
        id: "${PRIVATE_SUBNET_B}"

secretsEncryption:
  keyARN: ${MASTER_ARN}
  # Set encryption key ARN for secrets
  # 비밀값 암호화를 위한 키 ARN 설정

managedNodeGroups:
  - name: ${PRIVATE_MGMD_NODE}
    instanceType: ${INSTANCE_TYPE}
    desiredCapacity: 8
    minSize: 4
    maxSize: 8
    volumeSize: 50
    volumeType: gp3
    volumeEncrypted: true
    # Node volume configuration
    # 노드 볼륨 설정
    amiFamily: AmazonLinux2
    # Use Amazon Linux 2 AMI
    # Amazon Linux 2 AMI 사용
    labels:
      nodegroup-type: "${PRIVATE_MGMD_NODE}"
      # Label for node group
    privateNetworking: true
    subnets:
      - "${PRIVATE_SUBNET_A}"
      - "${PRIVATE_SUBNET_B}"
    ssh:
      enableSsm: true
    iam:
      withAddonPolicies:
        imageBuilder: true
        autoScaler: true
        externalDNS: true
        certManager: true
        ebs: true
        efs: true
        awsLoadBalancerController: true
        cloudWatch: true

cloudWatch:
    clusterLogging:
        enableTypes: ["api", "audit", "authenticator", "controllerManager", "scheduler"]
        # Enable CloudWatch logging for specified components
        # 지정된 구성 요소에 대해 CloudWatch 로깅 활성화

iam:
  withOIDC: true
  # Enable IAM OIDC provider for the cluster
  # 클러스터에 IAM OIDC 프로바이더 활성화

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
    # Enable add-ons for network, storage, and DN

YAML_EOF

echo "✅ EKS 클러스터 구성 파일 생성 완료"

echo ""
echo "======================================================"
echo "📋 클러스터 정보:"
echo "   - 이름: ${EKSCLUSTER_NAME}"
echo "   - 버전: ${EKS_VERSION}"
echo "   - 리전: ap-northeast-2"
echo "   - VPC ID: ${VPCID}"
echo "======================================================"
