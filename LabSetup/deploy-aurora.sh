#!/bin/bash

# Aurora MySQL 클러스터 배포 스크립트
# VPC01 Private Subnet에 Aurora MySQL 클러스터를 배포합니다.

set -e

# 환경 설정
export AWS_REGION=ap-northeast-2

echo "🚀 Aurora MySQL 클러스터 배포 시작"
echo "======================================================"
echo "📋 배포 정보:"
echo "   - 리전: ${AWS_REGION}"
echo "   - 스택 이름: VPC01-Aurora-MySQL"
echo "   - 템플릿: ~/amazonqcli_lab/LabSetup/aurora-mysql-stack.yml"
echo "   - 데이터베이스: ${DB_NAME:-mydb}"
echo "   - 사용자명: ${DB_USERNAME:-admin}"
echo "   - 인스턴스 클래스: db.t4g.medium"
echo "   - 엔진 버전: Aurora MySQL 8.0.mysql_aurora.3.04.0"
echo "   - 위치: VPC01 Private Subnets"
echo "   - 고가용성: Primary + Replica"
echo "======================================================"

# VPC01 스택 상태 확인
echo "🔍 [1/3] VPC01 스택 상태 확인 중..."
VPC01_STATUS=$(aws cloudformation describe-stacks --stack-name VPC01 --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$VPC01_STATUS" != "CREATE_COMPLETE" && "$VPC01_STATUS" != "UPDATE_COMPLETE" ]]; then
    echo "❌ VPC01 스택이 준비되지 않았습니다. 상태: $VPC01_STATUS"
    echo "   먼저 VPC01 스택을 배포하세요:"
    echo "   ./deploy-all-vpcs.sh"
    exit 1
fi

echo "✅ VPC01 스택 상태: $VPC01_STATUS"

# Aurora 스택 존재 여부 확인
echo ""
echo "📋 [2/3] Aurora MySQL 스택 상태 확인 중..."
AURORA_STATUS=$(aws cloudformation describe-stacks --stack-name VPC01-Aurora-MySQL --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "$AURORA_STATUS" == "NOT_FOUND" ]]; then
    echo "🆕 새로운 Aurora MySQL 스택을 생성합니다..."
    OPERATION="create"
elif [[ "$AURORA_STATUS" == "CREATE_COMPLETE" || "$AURORA_STATUS" == "UPDATE_COMPLETE" ]]; then
    echo "🔄 기존 Aurora MySQL 스택을 업데이트합니다... (현재 상태: $AURORA_STATUS)"
    OPERATION="update"
else
    echo "⚠️ Aurora MySQL 스택이 비정상 상태입니다: $AURORA_STATUS"
    echo "   스택을 확인하고 필요시 삭제 후 다시 실행하세요."
    exit 1
fi

# 패스워드 보안 확인
echo ""
echo "🔐 데이터베이스 마스터 계정 설정..."
read -p "데이터베이스 이름 (기본값: mydb): " DB_NAME
DB_NAME=${DB_NAME:-mydb}

read -p "마스터 사용자명 (기본값: admin): " DB_USERNAME
DB_USERNAME=${DB_USERNAME:-admin}

read -s -p "마스터 패스워드 (8자 이상): " DB_PASSWORD
echo ""

if [ ${#DB_PASSWORD} -lt 8 ]; then
    echo "❌ 패스워드는 8자 이상이어야 합니다."
    exit 1
fi
echo "✅ 데이터베이스 계정 설정 완료"

# Aurora MySQL 클러스터 배포
echo ""
echo "🚀 [3/3] Aurora MySQL 클러스터 배포 중..."
echo "   작업: $OPERATION"
echo "   예상 소요 시간: 15-25분"
echo "   ⚠️  배포 중에는 중단하지 마세요!"

aws cloudformation deploy \
  --stack-name VPC01-Aurora-MySQL \
  --template-file "$HOME/amazonqcli_lab/LabSetup/aurora-mysql-stack.yml" \
  --parameter-overrides \
    VPC01StackName=VPC01 \
    DBName=$DB_NAME \
    DBMasterUsername=$DB_USERNAME \
    DBMasterPassword=$DB_PASSWORD \
    DBInstanceClass=db.t4g.medium \
    DBEngineVersion=8.0.mysql_aurora.3.04.0 \
  --capabilities CAPABILITY_IAM

echo ""
echo "✅ Aurora MySQL 클러스터 배포가 완료되었습니다!"

echo ""
echo "======================================================"
echo "🎉 Aurora MySQL 클러스터 배포 성공!"
echo ""
echo "📊 배포 결과 확인:"
echo "aws cloudformation describe-stacks --stack-name VPC01-Aurora-MySQL --query 'Stacks[0].StackStatus'"
echo ""
echo "🔗 Aurora 클러스터 정보 확인:"
echo "aws cloudformation describe-stacks --stack-name VPC01-Aurora-MySQL --query 'Stacks[0].Outputs'"
echo ""
echo "📋 Aurora 엔드포인트 확인:"
echo "# Writer 엔드포인트 (읽기/쓰기용)"
echo "aws cloudformation describe-stacks --stack-name VPC01-Aurora-MySQL --query 'Stacks[0].Outputs[?OutputKey==\`ClusterEndpoint\`].OutputValue' --output text"
echo ""
echo "# Reader 엔드포인트 (읽기 전용)"
echo "aws cloudformation describe-stacks --stack-name VPC01-Aurora-MySQL --query 'Stacks[0].Outputs[?OutputKey==\`ReaderEndpoint\`].OutputValue' --output text"
echo ""
echo "🔧 Aurora 클러스터 상세 정보:"
echo "aws rds describe-db-clusters --db-cluster-identifier VPC01-Aurora-MySQL-dbcluster --query 'DBClusters[0].{Status:Status,Engine:Engine,EngineVersion:EngineVersion,DatabaseName:DatabaseName,MasterUsername:MasterUsername}'"
echo ""
echo "💡 연결 테스트 (VPC01 Private Subnet의 EC2에서):"
echo "# Writer 엔드포인트 연결"
echo "mysql -h <Writer-Endpoint> -u $DB_USERNAME -p $DB_NAME"
echo ""
echo "# Reader 엔드포인트 연결"
echo "mysql -h <Reader-Endpoint> -u $DB_USERNAME -p $DB_NAME"
echo ""
echo "🔒 보안 정보:"
echo "   - Aurora 클러스터는 VPC01 Private Subnet에 배포됨"
echo "   - VPC 내부에서만 접근 가능"
echo "   - 포트 3306으로 통신"
echo "   - 저장 데이터 암호화 활성화"
echo "   - 삭제 방지 활성화"
echo "   - IAM 데이터베이스 인증 활성화"
echo ""
echo "📈 백업 및 유지보수:"
echo "   - 자동 백업: 7일 보관"
echo "   - 백업 시간: 03:00-04:00 (UTC)"
echo "   - 유지보수 시간: 일요일 05:00-06:00 (UTC)"
echo ""
echo "📊 모니터링:"
echo "   - CloudWatch에서 Aurora 메트릭 확인 가능"
echo "   - RDS 콘솔에서 클러스터 상태 모니터링"
echo "   - Performance Insights 활용 가능"
echo ""
echo "⚠️  중요 사항:"
echo "   - 데이터베이스: $DB_NAME"
echo "   - 마스터 사용자명: $DB_USERNAME"
echo "   - 마스터 패스워드: [입력한 패스워드] (안전하게 보관하세요)"
echo "   - 삭제 방지가 활성화되어 있어 실수로 삭제되지 않음"
echo "   - 프로덕션 사용 시 패스워드 정책 강화 필요"
echo "======================================================"
