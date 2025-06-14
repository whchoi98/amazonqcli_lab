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
echo "🧭 [1/3] DMZVPC VPC/Subnet 정보 추출 중..."

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
echo "🔧 [2/3] EKS 환경변수 설정 중..."

EKSCLUSTER_NAME="eksworkshop"
EKS_VERSION="1.31"
INSTANCE_TYPE="m6i.xlarge"
PRIVATE_MGMD_NODE="managed-backend-workloads"

echo "✅ EKS 환경변수 설정 완료"

# bash_profile에 환경변수 저장
echo ""
echo "📝 [3/3] bash_profile에 환경변수 저장 중..."

append_to_bash_profile "VPCID" "$VPCID"
append_to_bash_profile "PRIVATE_SUBNET_A" "$PRIVATE_SUBNET_A"
append_to_bash_profile "PRIVATE_SUBNET_B" "$PRIVATE_SUBNET_B"
append_to_bash_profile "EKSCLUSTER_NAME" "$EKSCLUSTER_NAME"
append_to_bash_profile "EKS_VERSION" "$EKS_VERSION"
append_to_bash_profile "INSTANCE_TYPE" "$INSTANCE_TYPE"
append_to_bash_profile "PUBLIC_MGMD_NODE" "$PUBLIC_MGMD_NODE"
append_to_bash_profile "PRIVATE_MGMD_NODE" "$PRIVATE_MGMD_NODE"

echo "✅ bash_profile에 환경변수 저장 완료"

# bash_profile 다시 로드
source ~/.bash_profile

echo ""
echo "======================================================"
echo "✅ 환경변수 설정 완료!"
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
echo "3. 필요시 이 환경변수들을 사용하여 EKS 클러스터를 구성하세요"
echo "======================================================"
