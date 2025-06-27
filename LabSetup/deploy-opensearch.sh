#!/bin/bash

# OpenSearch 클러스터 배포 스크립트
# DMZVPC Private Subnet에 OpenSearch 클러스터를 배포합니다.

set -e

# 환경 설정
export AWS_REGION=ap-northeast-2

echo "🚀 OpenSearch 클러스터 배포 시작"
echo "======================================================"
echo "📋 배포 정보:"
echo "   - 리전: ${AWS_REGION}"
echo "   - 스택 이름: DMZVPC-OpenSearch"
echo "   - 템플릿: ~/amazonqcli_lab/LabSetup/opensearch-stack.yml"
echo "   - 도메인 이름: dmzvpc-opensearch"
echo "   - 버전: OpenSearch 2.11"
echo "   - 인스턴스 타입: r5.large.elasticsearch"
echo "   - 인스턴스 수: 2개"
echo "   - 볼륨 크기: 20GB"
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

# OpenSearch 스택 존재 여부 확인
echo ""
echo "📋 [2/3] OpenSearch 스택 상태 확인 중..."
OPENSEARCH_STATUS=$(aws cloudformation describe-stacks --stack-name DMZVPC-OpenSearch --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$OPENSEARCH_STATUS" == "NOT_FOUND" ]]; then
    echo "🆕 새로운 OpenSearch 스택을 생성합니다..."
    OPERATION="create"
elif [[ "$OPENSEARCH_STATUS" == "CREATE_COMPLETE" || "$OPENSEARCH_STATUS" == "UPDATE_COMPLETE" ]]; then
    echo "🔄 기존 OpenSearch 스택을 업데이트합니다... (현재 상태: $OPENSEARCH_STATUS)"
    OPERATION="update"
else
    echo "⚠️ OpenSearch 스택이 비정상 상태입니다: $OPENSEARCH_STATUS"
    echo "   스택을 확인하고 필요시 삭제 후 다시 실행하세요."
    exit 1
fi

# 마스터 패스워드 입력
echo ""
echo "🔐 OpenSearch 마스터 계정 설정..."
read -p "마스터 사용자명 (기본값: admin): " MASTER_USERNAME
MASTER_USERNAME=${MASTER_USERNAME:-admin}

read -s -p "마스터 패스워드 (8자 이상): " MASTER_PASSWORD
echo ""

if [ ${#MASTER_PASSWORD} -lt 8 ]; then
    echo "❌ 패스워드는 8자 이상이어야 합니다."
    exit 1
fi

# OpenSearch 클러스터 배포
echo ""
echo "🚀 [3/3] OpenSearch 클러스터 배포 중..."
echo "   작업: $OPERATION"
echo "   예상 소요 시간: 20-30분"
echo "   ⚠️  배포 중에는 중단하지 마세요!"

aws cloudformation deploy \
  --stack-name DMZVPC-OpenSearch \
  --template-file "~/amazonqcli_lab/LabSetup/opensearch-stack.yml" \
  --parameter-overrides \
    DMZVPCStackName=DMZVPC \
    OpenSearchDomainName=dmzvpc-opensearch \
    OpenSearchVersion=OpenSearch_2.11 \
    InstanceType=r5.large.elasticsearch \
    InstanceCount=2 \
    VolumeSize=20 \
    MasterUsername=$MASTER_USERNAME \
    MasterPassword=$MASTER_PASSWORD \
  --capabilities CAPABILITY_IAM

echo ""
echo "✅ OpenSearch 클러스터 배포가 완료되었습니다!"

echo ""
echo "======================================================"
echo "🎉 OpenSearch 클러스터 배포 성공!"
echo ""
echo "📊 배포 결과 확인:"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-OpenSearch --query 'Stacks[0].StackStatus'"
echo ""
echo "🔗 OpenSearch 클러스터 정보 확인:"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-OpenSearch --query 'Stacks[0].Outputs'"
echo ""
echo "📋 OpenSearch 엔드포인트 확인:"
echo "# 도메인 엔드포인트"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-OpenSearch --query 'Stacks[0].Outputs[?OutputKey==\`OpenSearchDomainEndpoint\`].OutputValue' --output text"
echo ""
echo "# Dashboards URL"
echo "aws cloudformation describe-stacks --stack-name DMZVPC-OpenSearch --query 'Stacks[0].Outputs[?OutputKey==\`OpenSearchDashboardsURL\`].OutputValue' --output text"
echo ""
echo "🔧 OpenSearch 도메인 상세 정보:"
echo "aws es describe-elasticsearch-domain --domain-name dmzvpc-opensearch --query 'DomainStatus.{Status:Processing,Endpoint:Endpoint,Version:ElasticsearchVersion,InstanceType:ElasticsearchClusterConfig.InstanceType,InstanceCount:ElasticsearchClusterConfig.InstanceCount}'"
echo ""
echo "💡 접속 방법 (DMZVPC Private Subnet의 EC2에서):"
echo "# API 접속"
echo "curl -u $MASTER_USERNAME:<password> https://<domain-endpoint>/"
echo ""
echo "# Dashboards 접속 (포트 포워딩 필요)"
echo "# 1. EC2에서 포트 포워딩: ssh -L 8443:<domain-endpoint>:443 ec2-user@<ec2-ip>"
echo "# 2. 브라우저에서: https://localhost:8443/_dashboards/"
echo ""
echo "🔒 보안 정보:"
echo "   - OpenSearch 클러스터는 DMZVPC Private Subnet에 배포됨"
echo "   - VPC 내부에서만 접근 가능"
echo "   - HTTPS 강제 사용 (포트 443)"
echo "   - 저장 데이터 암호화 활성화"
echo "   - 노드 간 암호화 활성화"
echo "   - Fine-grained access control 활성화"
echo ""
echo "📈 모니터링:"
echo "   - CloudWatch에서 OpenSearch 메트릭 확인 가능"
echo "   - OpenSearch 콘솔에서 클러스터 상태 모니터링"
echo "   - 로그는 CloudWatch Logs에 저장됨"
echo ""
echo "⚠️  중요 사항:"
echo "   - 마스터 사용자명: $MASTER_USERNAME"
echo "   - 마스터 패스워드: [입력한 패스워드] (안전하게 보관하세요)"
echo "   - Private Subnet에 배포되어 직접 접근 불가"
echo "   - 포트 포워딩 또는 VPN을 통해 접근 필요"
echo "======================================================"
