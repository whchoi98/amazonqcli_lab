#!/bin/bash

# 🛠️ AWS Account ID 및 Region 설정 스크립트 (Amazon Linux 2023 기준)

set -e

echo "------------------------------------------------------"
echo "🔐 AWS Account ID 및 Region 추출 중..."
echo "------------------------------------------------------"

# Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --region ap-northeast-2 --output text --query Account)

# Region (IMDSv2 방식 사용)
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 60" || true)

if [ -n "$TOKEN" ]; then
    AWS_REGION=$(curl -sH "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region)
fi

# IMDSv2 실패 시 기본 리전 사용
if [ -z "$AWS_REGION" ]; then
    echo "⚠️  IMDSv2에서 리전을 가져올 수 없습니다. 기본 리전(ap-northeast-2)을 사용합니다."
    AWS_REGION="ap-northeast-2"
fi

# 결과 출력
echo "✅ ACCOUNT_ID: $ACCOUNT_ID"
echo "✅ AWS_REGION: $AWS_REGION"

# 환경 변수 등록 (중복 방지)
echo "------------------------------------------------------"
echo "🧠 ~/.bash_profile에 환경 변수 등록"
echo "------------------------------------------------------"

sed -i '/^export ACCOUNT_ID=/d' ~/.bash_profile 2>/dev/null || true
sed -i '/^export AWS_REGION=/d' ~/.bash_profile 2>/dev/null || true
echo "export ACCOUNT_ID=${ACCOUNT_ID}" | tee -a ~/.bash_profile
echo "export AWS_REGION=${AWS_REGION}" | tee -a ~/.bash_profile

# 현재 셸에도 적용
export ACCOUNT_ID="${ACCOUNT_ID}"
export AWS_REGION="${AWS_REGION}"

# AWS CLI 기본 리전 설정
aws configure set default.region "${AWS_REGION}"

# 설정 확인
echo "------------------------------------------------------"
echo "📋 현재 AWS CLI 프로파일 설정 확인"
aws configure --profile default list
echo "------------------------------------------------------"

echo "🎉 완료되었습니다. 새 셸을 열거나 'source ~/.bash_profile'을 실행하세요."
