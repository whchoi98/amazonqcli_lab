#!/bin/bash

# 모든 VPC 스택을 동시에 배포하는 스크립트
# DMZVPC, VPC01, VPC02를 병렬로 배포합니다.

set -e

export AWS_REGION=ap-northeast-2

echo "🚀 모든 VPC 스택 배포 시작"
echo "======================================================"
echo "📋 배포 정보:"
echo "   - 리전: ${AWS_REGION}"
echo "   - 스택: DMZVPC, VPC01, VPC02"
echo "   - 배포 방식: 병렬 배포"
echo "======================================================"

# S3 버킷 이름 생성
ACCOUNT_ALIAS=$(aws iam list-account-aliases --query 'AccountAliases[0]' --output text 2>/dev/null)
if [ -z "$ACCOUNT_ALIAS" ] || [ "$ACCOUNT_ALIAS" = "None" ]; then
    ACCOUNT_ALIAS=$(aws sts get-caller-identity --query Account --output text)
fi
BUCKET_NAME=${ACCOUNT_ALIAS}-$(date +%Y%m%d)-cf-template

echo "🔄 [1/3] DMZVPC 배포 시작..."
# DMZVPC 배포 (백그라운드에서 실행)
{
    echo "📦 S3 버킷 확인/생성: ${BUCKET_NAME}"
    aws s3 mb s3://${BUCKET_NAME} --region ${AWS_REGION} 2>/dev/null || echo "   (버킷이 이미 존재합니다)"
    
    echo "🚀 DMZVPC CloudFormation 배포 중..."
    aws cloudformation deploy \
      --region ${AWS_REGION} \
      --stack-name DMZVPC \
      --template-file $HOME/amazonqcli_lab/LabSetup/1.DMZVPC.yml \
      --s3-bucket ${BUCKET_NAME} \
      --capabilities CAPABILITY_NAMED_IAM
    
    echo "🗑️ S3 버킷 정리: ${BUCKET_NAME}"
    aws s3 rb s3://${BUCKET_NAME} --force
    
    echo "✅ DMZVPC 배포 완료"
} &

DMZVPC_PID=$!

echo "🔄 [2/3] VPC01 배포 시작..."
# VPC01 배포 (백그라운드에서 실행)
{
    aws cloudformation deploy --region ${AWS_REGION} \
      --stack-name "VPC01" \
      --template-file "$HOME/amazonqcli_lab/LabSetup/2.VPC01.yml" \
      --capabilities CAPABILITY_NAMED_IAM
    
    echo "✅ VPC01 배포 완료"
} &

VPC01_PID=$!

echo "🔄 [3/3] VPC02 배포 시작..."
# VPC02 배포 (백그라운드에서 실행)
{
    aws cloudformation deploy --region ${AWS_REGION} \
      --stack-name "VPC02" \
      --template-file "$HOME/amazonqcli_lab/LabSetup/3.VPC02.yml" \
      --capabilities CAPABILITY_NAMED_IAM
    
    echo "✅ VPC02 배포 완료"
} &

VPC02_PID=$!

echo ""
echo "⏰ 모든 스택이 병렬로 배포 중입니다..."
echo "   - DMZVPC PID: ${DMZVPC_PID}"
echo "   - VPC01 PID: ${VPC01_PID}"
echo "   - VPC02 PID: ${VPC02_PID}"
echo ""

# 모든 백그라운드 작업이 완료될 때까지 대기
wait ${DMZVPC_PID}
DMZVPC_STATUS=$?

wait ${VPC01_PID}
VPC01_STATUS=$?

wait ${VPC02_PID}
VPC02_STATUS=$?

echo ""
echo "======================================================"
echo "🎉 모든 VPC 스택 배포 완료!"
echo ""
echo "📊 배포 결과:"
if [ ${DMZVPC_STATUS} -eq 0 ]; then
    echo "   ✅ DMZVPC: 성공"
else
    echo "   ❌ DMZVPC: 실패 (종료 코드: ${DMZVPC_STATUS})"
fi

if [ ${VPC01_STATUS} -eq 0 ]; then
    echo "   ✅ VPC01: 성공"
else
    echo "   ❌ VPC01: 실패 (종료 코드: ${VPC01_STATUS})"
fi

if [ ${VPC02_STATUS} -eq 0 ]; then
    echo "   ✅ VPC02: 성공"
else
    echo "   ❌ VPC02: 실패 (종료 코드: ${VPC02_STATUS})"
fi

echo ""
echo "📋 배포된 스택 확인:"
echo "aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query 'StackSummaries[?contains(StackName, \`VPC\`)].{Name:StackName,Status:StackStatus}' --output table"
echo ""
echo "🔗 스택 상세 정보:"
echo "aws cloudformation describe-stacks --stack-name DMZVPC --query 'Stacks[0].Outputs'"
echo "aws cloudformation describe-stacks --stack-name VPC01 --query 'Stacks[0].Outputs'"
echo "aws cloudformation describe-stacks --stack-name VPC02 --query 'Stacks[0].Outputs'"

# 전체 결과 반환
if [ ${DMZVPC_STATUS} -eq 0 ] && [ ${VPC01_STATUS} -eq 0 ] && [ ${VPC02_STATUS} -eq 0 ]; then
    echo ""
    echo "🎊 모든 스택이 성공적으로 배포되었습니다!"
    exit 0
else
    echo ""
    echo "⚠️ 일부 스택 배포에 실패했습니다. 로그를 확인해주세요."
    exit 1
fi
