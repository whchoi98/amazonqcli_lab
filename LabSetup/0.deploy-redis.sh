#!/bin/bash

# Redis Cluster 배포 스크립트
# DMZVPC Private Subnet에 Redis 7.x 클러스터를 배포합니다.

set -e

# 환경 설정
export AWS_REGION=ap-northeast-2

echo "🚀 Redis Cluster 배포 시작"
echo "======================================================"
echo "📋 배포 정보:"
echo "   - 리전: ${AWS_REGION}"
echo "   - 스택 이름: DMZVPC-Redis"
echo "   - 템플릿: ~/amazonqcli_lab/LabSetup/redis-cluster-stack.yml"
echo "   - 노드 타입: cache.t4g.small"
echo "   - 노드 수: 2개"
echo "   - 엔진 버전: Redis 7.0"
echo "   - 위치: DMZVPC Private Subnets"
echo "======================================================"

# DMZVPC 스택 상태 확인
echo "🔍 [1/3] DMZVPC 스택 상태 확인 중..."
DMZVPC_STATUS=$(aws cloudformation describe-stacks --stack-name DMZVPC --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$DMZVPC_STATUS" != "CREATE_COMPLETE" && "$DMZVPC_STATUS" != "UPDATE_COMPLETE" ]]; then
    echo "❌ DMZVPC 스택이 준비되지 않았습니다. 상태: $DMZVPC_STATUS"
    echo "   먼저 DMZVPC 스택을 배포하세요:"
    echo "   ./deploy-all-vpcs.sh"
    exit 1
fi

echo "✅ DMZVPC 스택 상태: $DMZVPC_STATUS"

# Redis 스택 존재 여부 확인
echo ""
echo "📋 [2/3] Redis 스택 상태 확인 중..."
REDIS_STATUS=$(aws cloudformation describe-stacks --stack-name DMZVPC-Redis --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$REDIS_STATUS" == "NOT_FOUND" ]]; then
    echo "🆕 새로운 Redis 스택을 생성합니다..."
    OPERATION="create"
elif [[ "$REDIS_STATUS" == "CREATE_COMPLETE" || "$REDIS_STATUS" == "UPDATE_COMPLETE" ]]; then
    echo "🔄 기존 Redis 스택을 업데이트합니다... (현재 상태: $REDIS_STATUS)"
    OPERATION="update"
else
    echo "⚠️ Redis 스택이 비정상 상태입니다: $REDIS_STATUS"
    echo "   스택을 확인하고 필요시 삭제 후 다시 실행하세요."
    exit 1
fi

# Redis 클러스터 배포
echo ""
echo "🚀 [3/3] Redis 클러스터 배포 중..."
echo "   작업: $OPERATION"
echo "   예상 소요 시간: 15-20분"

# Option1: DMZVPC에 Redis Stack 배포
aws cloudformation deploy \
  --stack-name DMZVPC-Redis \
  --template-file "~/amazonqcli_lab/LabSetup/redis-cluster-stack.yml" \
  --parameter-overrides \
    DMZVPCStackName=DMZVPC \
    RedisNodeType=cache.t4g.small \
    RedisNumCacheNodes=2 \
    RedisEngineVersion=7.0 \
  --capabilities CAPABILITY_IAM

echo ""
echo "✅ Redis 클러스터 배포가 완료되었습니다!"

echo ""
echo "======================================================"
echo "🎉 Redis 클러스터 배포 성공!"
echo ""
echo "📊 배포 결과 확인:"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-Redis --query 'Stacks[0].StackStatus'"
echo ""
echo "🔗 Redis 클러스터 정보 확인:"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-Redis --query 'Stacks[0].Outputs'"
echo ""
echo "📋 Redis 엔드포인트 확인:"
echo "# Primary 엔드포인트 (쓰기용)"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-Redis --query 'Stacks[0].Outputs[?OutputKey==\`RedisClusterEndpoint\`].OutputValue' --output text"
echo ""
echo "# Reader 엔드포인트 (읽기용)"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-Redis --query 'Stacks[0].Outputs[?OutputKey==\`RedisClusterReaderEndpoint\`].OutputValue' --output text"
echo ""
echo "🔧 Redis 클러스터 상세 정보:"
echo "aws elasticache describe-replication-groups --replication-group-id DMZVPC-Redis-redis --query 'ReplicationGroups[0].{Status:Status,Engine:Engine,EngineVersion:EngineVersion,NodeType:CacheNodeType,NumNodes:NumCacheClusters}'"
echo ""
echo "💡 연결 테스트 (Private Subnet의 EC2에서):"
echo "redis-cli -h <Primary-Endpoint> -p 6379"
echo "redis-cli -h <Reader-Endpoint> -p 6379"
echo ""
echo "🔒 보안 정보:"
echo "   - Redis 클러스터는 DMZVPC Private Subnet에 배포됨"
echo "   - VPC 내부에서만 접근 가능"
echo "   - 포트 6379로 통신"
echo "   - 저장 데이터 암호화 활성화"
echo ""
echo "📈 모니터링:"
echo "   - CloudWatch에서 Redis 메트릭 확인 가능"
echo "   - ElastiCache 콘솔에서 클러스터 상태 모니터링"
echo "======================================================"
