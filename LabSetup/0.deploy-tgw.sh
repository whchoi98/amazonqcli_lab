#!/bin/bash

# Transit Gateway 배포 스크립트
# VPC들을 연결하는 Transit Gateway를 배포합니다.

set -e

# 환경 설정
source ~/.bash_profile
export AWS_REGION=ap-northeast-2

echo "🚀 Transit Gateway 배포 시작"
echo "======================================================"
echo "📋 배포 정보:"
echo "   - 리전: ${AWS_REGION}"
echo "   - 스택 이름: TGW"
echo "   - 템플릿: ~/amazonqcli_lab/4.TGW.yml"
echo "======================================================"

# 의존성 스택 확인
echo "🔍 [1/3] 의존성 스택 상태 확인 중..."

REQUIRED_STACKS=("DMZVPC" "VPC01" "VPC02")
MISSING_STACKS=()

for stack in "${REQUIRED_STACKS[@]}"; do
    STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $stack --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    
    if [[ "$STACK_STATUS" == "CREATE_COMPLETE" || "$STACK_STATUS" == "UPDATE_COMPLETE" ]]; then
        echo "   ✅ $stack: $STACK_STATUS"
    else
        echo "   ❌ $stack: $STACK_STATUS"
        MISSING_STACKS+=($stack)
    fi
done

if [ ${#MISSING_STACKS[@]} -ne 0 ]; then
    echo ""
    echo "❌ 다음 스택들이 준비되지 않았습니다: ${MISSING_STACKS[*]}"
    echo "   먼저 다음 명령어로 VPC 스택들을 배포하세요:"
    echo "   ./deploy-all-vpcs.sh"
    exit 1
fi

echo "✅ 모든 의존성 스택이 준비되었습니다."

# TGW 스택 존재 여부 확인
echo ""
echo "📋 [2/3] TGW 스택 상태 확인 중..."
TGW_STATUS=$(aws cloudformation describe-stacks --stack-name TGW --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$TGW_STATUS" == "NOT_FOUND" ]]; then
    echo "🆕 새로운 TGW 스택을 생성합니다..."
    OPERATION="create"
elif [[ "$TGW_STATUS" == "CREATE_COMPLETE" || "$TGW_STATUS" == "UPDATE_COMPLETE" ]]; then
    echo "🔄 기존 TGW 스택을 업데이트합니다... (현재 상태: $TGW_STATUS)"
    OPERATION="update"
else
    echo "⚠️ TGW 스택이 비정상 상태입니다: $TGW_STATUS"
    echo "   스택을 확인하고 필요시 삭제 후 다시 실행하세요."
    exit 1
fi

# TGW 스택 배포
echo ""
echo "🚀 [3/3] Transit Gateway 배포 중..."
echo "   작업: $OPERATION"
echo "   예상 소요 시간: 5-10분"

aws cloudformation deploy \
  --region ${AWS_REGION} \
  --stack-name "TGW" \
  --template-file "~/amazonqcli_lab/4.TGW.yml" \
  --capabilities CAPABILITY_NAMED_IAM

echo ""
echo "✅ Transit Gateway 배포가 완료되었습니다!"

echo ""
echo "======================================================"
echo "🎉 Transit Gateway 배포 성공!"
echo ""
echo "📊 배포 결과 확인:"
echo "aws cloudformation describe-stacks --stack-name TGW --query 'Stacks[0].StackStatus'"
echo ""
echo "🔗 TGW 출력값 확인:"
echo "aws cloudformation describe-stacks --stack-name TGW --query 'Stacks[0].Outputs'"
echo ""
echo "🌐 Transit Gateway 정보 확인:"
echo "aws ec2 describe-transit-gateways --query 'TransitGateways[?State==\`available\`].{ID:TransitGatewayId,State:State,Description:Description}' --output table"
echo ""
echo "🔗 TGW 연결 상태 확인:"
echo "aws ec2 describe-transit-gateway-attachments --query 'TransitGatewayAttachments[].{TGW:TransitGatewayId,VPC:ResourceId,State:State,Type:ResourceType}' --output table"
echo ""
echo "💡 다음 단계:"
echo "   - TGW 라우팅 테이블 구성"
echo "   - VPC 간 연결 테스트"
echo "   - 보안 그룹 규칙 확인"
echo "======================================================"
