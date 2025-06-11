#!/bin/bash

# DMZVPC의 VPC와 Subnet 정보를 추출하여 환경 변수로 저장하고,
# 이를 기반으로 dmz_eksctl_shell.sh를 생성하는 스크립트

set -e

# bash_profile에 환경변수를 추가하는 함수
append_to_bash_profile() {
    local var_name="$1"
    local var_value="$2"
    
    # 기존 변수가 있으면 제거
    sed -i "/^export ${var_name}=/d" ~/.bash_profile 2>/dev/null || true
    
    # 새 변수 추가
    echo "export ${var_name}=\"${var_value}\"" >> ~/.bash_profile
    
    # 현재 세션에도 적용
    export "${var_name}=${var_value}"
}

echo "🚀 DMZVPC 환경 변수 추출 시작"
echo "======================================================"

# VPC/Subnet 정보 추출
echo "🧭 [1/5] DMZVPC VPC/Subnet 정보 추출 중..."

# VPC ID 추출
VPCID=$(aws cloudformation describe-stacks \
  --stack-name DMZVPC \
  --query 'Stacks[0].Outputs[?OutputKey==`VPC`].OutputValue' \
  --output text)

# Private Subnet A ID 추출
PRIVATE_SUBNET_A=$(aws cloudformation describe-stacks \
  --stack-name DMZVPC \
  --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnetA`].OutputValue' \
  --output text)

# Private Subnet B ID 추출
PRIVATE_SUBNET_B=$(aws cloudformation describe-stacks \
  --stack-name DMZVPC \
  --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnetB`].OutputValue' \
  --output text)

echo "✅ DMZVPC 및 Subnet ID 환경변수 저장 완료"
echo "   VPC ID: ${VPCID}"
echo "   Private Subnet A: ${PRIVATE_SUBNET_A}"
echo "   Private Subnet B: ${PRIVATE_SUBNET_B}"

# 값 검증
if [ -z "${VPCID}" ] || [ -z "${PRIVATE_SUBNET_A}" ] || [ -z "${PRIVATE_SUBNET_B}" ]; then
    echo "❌ VPC 또는 Subnet 정보를 가져오는데 실패했습니다."
    echo "   DMZVPC 스택이 올바르게 배포되어 있는지 확인하세요."
    exit 1
fi

# EKS 관련 환경변수 설정
echo ""
echo "🔧 [2/5] EKS 환경변수 설정 중..."

EKSCLUSTER_NAME="eksworkshop"
EKS_VERSION="1.31"
INSTANCE_TYPE="m6i.xlarge"
PRIVATE_MGMD_NODE="managed-backend-workloads"

echo "✅ EKS 환경변수 설정 완료"

# bash_profile에 환경변수 저장
echo ""
echo "📝 [3/5] bash_profile에 환경변수 저장 중..."

append_to_bash_profile "VPCID" "$VPCID"
append_to_bash_profile "PRIVATE_SUBNET_A" "$PRIVATE_SUBNET_A"
append_to_bash_profile "PRIVATE_SUBNET_B" "$PRIVATE_SUBNET_B"
append_to_bash_profile "EKSCLUSTER_NAME" "$EKSCLUSTER_NAME"
append_to_bash_profile "EKS_VERSION" "$EKS_VERSION"
append_to_bash_profile "INSTANCE_TYPE" "$INSTANCE_TYPE"
append_to_bash_profile "PUBLIC_MGMD_NODE" "$PUBLIC_MGMD_NODE"
append_to_bash_profile "PRIVATE_MGMD_NODE" "$PRIVATE_MGMD_NODE"

echo "✅ bash_profile에 환경변수 저장 완료"

# dmz_eksctl_shell.sh 생성
echo ""
echo "📝 [4/5] dmz_eksctl_shell.sh 생성 중..."

cat > dmz_eksctl_shell.sh << 'EOF'
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
echo "🔄 [1/3] EKS 클러스터 구성 파일 생성 중..."

cat > ~/amazonqcli_lab/ekscluster.yaml << YAML_EOF
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

nodeGroups:
  - name: ${PRIVATE_SELFMGMD_NODE}
    instanceType: ${INSTANCE_TYPE}
    desiredCapacity: 2
    minSize: 1
    maxSize: 4
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

managedNodeGroups:
  - name: ${PRIVATE_MGMD_NODE}
    instanceType: ${INSTANCE_TYPE}
    desiredCapacity: 8
    minSize: 4
    maxSize: 8
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
EOF

# bash_profile 다시 로드
source ~/.bash_profile

echo ""
echo "======================================================"
echo "✅ dmz_eksctl_shell.sh 생성 및 환경변수 설정 완료!"
echo ""
echo "📋 bash_profile에 저장된 환경변수:"
echo "export VPCID=\"${VPCID}\""
echo "export PRIVATE_SUBNET_A=\"${PRIVATE_SUBNET_A}\""
echo "export PRIVATE_SUBNET_B=\"${PRIVATE_SUBNET_B}\""
echo "export EKSCLUSTER_NAME=\"${EKSCLUSTER_NAME}\""
echo "export EKS_VERSION=\"${EKS_VERSION}\""
echo "export INSTANCE_TYPE=\"${INSTANCE_TYPE}\""
echo "export PUBLIC_MGMD_NODE=\"${PUBLIC_MGMD_NODE}\""
echo "export PRIVATE_MGMD_NODE=\"${PRIVATE_MGMD_NODE}\""
echo ""
echo "💡 다음 단계:"
echo "1. 환경변수가 bash_profile에 저장되었습니다"
echo "2. 새 터미널에서도 환경변수가 자동으로 로드됩니다"
echo "3. EKS 클러스터를 배포하세요"
echo "======================================================"
