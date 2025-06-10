#!/bin/bash
# dmz_eks_shell.sh: DMZPVPC EKS 환경 변수 설정 스크립트
# EKS 버전은 사용자로부터 입력받고, 관련 변수는 .bash_profile에 저장

set -e

cd ~/amazonqcli_lab || exit 1

echo "🧭 [1/4] DMZPVPC VPC/Subnet 정보 추출 중..."

# VPC 스택 이름 정의 (DMZPVPC CloudFormation 스택 이름)
export VPC_STACK_NAME="DMZPVPC"

# VPC ID 조회 (CloudFormation 스택에서 VPC ID 추출)
export VPC_ID=$(aws cloudformation describe-stacks --stack-name ${VPC_STACK_NAME} --query 'Stacks[0].Outputs[?OutputKey==`VPC`].OutputValue' --output text)

# Private Subnet ID 조회 (DMZPVPC에서 Private Subnet A, B 사용)
export PrivateSubnetA=$(aws cloudformation describe-stacks --stack-name ${VPC_STACK_NAME} --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnetA`].OutputValue' --output text)
export PrivateSubnetB=$(aws cloudformation describe-stacks --stack-name ${VPC_STACK_NAME} --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnetB`].OutputValue' --output text)

# Public Subnet ID 조회 (필요시 사용)
export PublicSubnetA=$(aws cloudformation describe-stacks --stack-name ${VPC_STACK_NAME} --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnetA`].OutputValue' --output text)
export PublicSubnetB=$(aws cloudformation describe-stacks --stack-name ${VPC_STACK_NAME} --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnetB`].OutputValue' --output text)

# 중복 방지 후 환경 변수 저장
append_to_bash_profile() {
  VAR=$1
  VALUE=$2
  # 기존 변수가 있으면 제거하고 새로 추가
  sed -i "/export $VAR=/d" ~/.bash_profile 2>/dev/null || true
  echo "export $VAR=$VALUE" >> ~/.bash_profile
}

append_to_bash_profile "VPC_STACK_NAME" "$VPC_STACK_NAME"
append_to_bash_profile "VPC_ID" "$VPC_ID"
append_to_bash_profile "PrivateSubnetA" "$PrivateSubnetA"
append_to_bash_profile "PrivateSubnetB" "$PrivateSubnetB"
append_to_bash_profile "PublicSubnetA" "$PublicSubnetA"
append_to_bash_profile "PublicSubnetB" "$PublicSubnetB"

echo "✅ DMZPVPC 및 Subnet ID 환경변수 저장 완료"
echo "   VPC ID: $VPC_ID"
echo "   Private Subnet A: $PrivateSubnetA"
echo "   Private Subnet B: $PrivateSubnetB"

# 사용자로부터 EKS 버전 입력
echo "🧭 [2/4] EKS 버전 입력 받는 중..."
read -rp "Enter the EKS version (default: 1.31): " USER_EKS_VERSION
EKS_VERSION="${USER_EKS_VERSION:-1.31}"
echo "🛠️ 선택된 EKS 버전: ${EKS_VERSION}"

# EKS 관련 변수 정의
export EKSCLUSTER_NAME="dmz-eks-cluster"
export INSTANCE_TYPE="m6i.large"
export PRIVATE_MGMD_NODE="dmz-private-managed-nodes"

append_to_bash_profile "EKSCLUSTER_NAME" "$EKSCLUSTER_NAME"
append_to_bash_profile "EKS_VERSION" "$EKS_VERSION"
append_to_bash_profile "INSTANCE_TYPE" "$INSTANCE_TYPE"
append_to_bash_profile "PRIVATE_MGMD_NODE" "$PRIVATE_MGMD_NODE"

echo "✅ EKS 관련 환경변수 저장 완료"
echo "   클러스터 이름: $EKSCLUSTER_NAME"
echo "   EKS 버전: $EKS_VERSION"
echo "   인스턴스 타입: $INSTANCE_TYPE"

echo "🧭 [3/4] .bash_profile 적용 중..."
source ~/.bash_profile

echo "🎉 [4/4] 완료: 모든 환경변수가 설정되었습니다!"
echo ""
echo "📋 설정된 환경변수:"
echo "   VPC_ID: $VPC_ID"
echo "   PrivateSubnetA: $PrivateSubnetA"
echo "   PrivateSubnetB: $PrivateSubnetB"
echo "   EKSCLUSTER_NAME: $EKSCLUSTER_NAME"
echo "   EKS_VERSION: $EKS_VERSION"
echo "   INSTANCE_TYPE: $INSTANCE_TYPE"
echo ""
echo "💡 다음 단계: ./dmz_eksctl_shell.sh 를 실행하여 EKS 클러스터를 생성하세요."
