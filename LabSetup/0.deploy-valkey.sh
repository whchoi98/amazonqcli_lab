#!/bin/bash

# Valkey Cluster 배포 스크립트
# DMZVPC Private Subnet에 Valkey 8.2 클러스터 모드를 배포합니다.

set -e

# 환경 설정
export AWS_REGION=ap-northeast-2

STACK_NAME="DMZVPC-Redis"

echo "🚀 Valkey Cluster 배포 시작"
echo "======================================================"
echo "📋 배포 정보:"
echo "   - 리전: ${AWS_REGION}"
echo "   - 스택 이름: ${STACK_NAME}"
echo "   - 템플릿: ~/amazonqcli_lab/LabSetup/valkey-cluster-stack.yml"
echo "   - 노드 타입: cache.t3.medium"
echo "   - 구성: 클러스터 모드 (2 샤드 x 2 노드)"
echo "   - 엔진: Valkey 8.2"
echo "   - 위치: DMZVPC Private Subnets"
echo "======================================================"

# DMZVPC 스택 상태 확인
echo "🔍 [1/3] DMZVPC 스택 상태 확인 중..."
DMZVPC_STATUS=$(aws cloudformation describe-stacks --stack-name DMZVPC --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$DMZVPC_STATUS" != "CREATE_COMPLETE" && "$DMZVPC_STATUS" != "UPDATE_COMPLETE" ]]; then
    echo "❌ DMZVPC 스택이 준비되지 않았습니다. 상태: $DMZVPC_STATUS"
    echo "   먼저 DMZVPC 스택을 배포하세요:"
    echo "   ./0.deploy-all-vpcs.sh"
    exit 1
fi

echo "✅ DMZVPC 스택 상태: $DMZVPC_STATUS"

# Valkey 스택 존재 여부 확인
echo ""
echo "📋 [2/3] Valkey 스택 상태 확인 중..."
VALKEY_STATUS=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$VALKEY_STATUS" == "NOT_FOUND" ]]; then
    echo "🆕 새로운 Valkey 스택을 생성합니다..."
    OPERATION="create"
elif [[ "$VALKEY_STATUS" == "CREATE_COMPLETE" || "$VALKEY_STATUS" == "UPDATE_COMPLETE" ]]; then
    echo "🔄 기존 Valkey 스택을 업데이트합니다... (현재 상태: $VALKEY_STATUS)"
    OPERATION="update"
else
    echo "⚠️ Valkey 스택이 비정상 상태입니다: $VALKEY_STATUS"
    echo "   스택을 확인하고 필요시 삭제 후 다시 실행하세요."
    exit 1
fi

# Valkey 클러스터 배포
echo ""
echo "🚀 [3/3] Valkey 클러스터 배포 중..."
echo "   작업: $OPERATION"
echo "   예상 소요 시간: 15-20분"

aws cloudformation deploy \
  --stack-name ${STACK_NAME} \
  --template-file "$HOME/amazonqcli_lab/LabSetup/valkey-cluster-stack.yml" \
  --parameter-overrides \
    DMZVPCStackName=DMZVPC \
    NodeType=cache.t3.medium \
  --capabilities CAPABILITY_IAM

echo ""
echo "✅ Valkey 클러스터 배포가 완료되었습니다!"

echo ""
echo "======================================================"
echo "🎉 Valkey 클러스터 배포 성공!"
echo ""
echo "📊 배포 결과 확인:"
echo "aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].StackStatus'"
echo ""
echo "🔗 Valkey 클러스터 정보 확인:"
echo "aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].Outputs'"
echo ""
echo "📋 Valkey Configuration 엔드포인트 확인:"
echo "aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].Outputs[?OutputKey==\`ValkeyConfigurationEndpoint\`].OutputValue' --output text"
echo ""
echo "🔧 Valkey 클러스터 상세 정보:"
echo "aws elasticache describe-replication-groups --query 'ReplicationGroups[?contains(ReplicationGroupId,\`dmz\`)].{Id:ReplicationGroupId,Status:Status,Engine:Engine,EngineVersion:EngineVersion,NodeType:CacheNodeType,ClusterEnabled:ClusterEnabled}' --output table"
echo ""
echo "💡 연결 테스트 (Private Subnet의 EC2에서):"
echo "valkey-cli -c -h <Configuration-Endpoint> -p 6379 --tls"
echo ""
echo "🔒 보안 정보:"
echo "   - Valkey 클러스터는 DMZVPC Private Subnet에 배포됨"
echo "   - DMZ VPC, VPC01, VPC02에서 접근 가능"
echo "   - 포트 6379로 통신"
echo "   - 저장 데이터 암호화 활성화 (at-rest)"
echo "   - 전송 암호화 활성화 (in-transit TLS)"
echo "   - 클러스터 모드: 2 샤드 x 2 노드 (Primary + Replica)"
echo ""
echo "📈 모니터링:"
echo "   - CloudWatch에서 Valkey 메트릭 확인 가능"
echo "   - ElastiCache 콘솔에서 클러스터 상태 모니터링"
echo "======================================================"
