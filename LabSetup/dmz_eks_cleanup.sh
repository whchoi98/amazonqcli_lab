#!/bin/bash
# dmz_eks_cleanup.sh: DMZPVPC EKS 클러스터 삭제 스크립트

set -e

source ~/.bash_profile

echo "🗑️  DMZPVPC EKS 클러스터 삭제 시작"
echo ""
echo "⚠️  주의: 이 작업은 다음을 삭제합니다:"
echo "   - EKS 클러스터: ${EKSCLUSTER_NAME}"
echo "   - 관리형 노드 그룹: ${PRIVATE_MGMD_NODE}"
echo "   - 관련된 모든 AWS 리소스"
echo ""

read -p "정말로 클러스터를 삭제하시겠습니까? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
    echo "❌ 클러스터 삭제가 취소되었습니다."
    exit 1
fi

echo "🚀 EKS 클러스터 삭제를 시작합니다..."
echo "⏰ 예상 소요 시간: 10-15분"

# EKS 클러스터 삭제 실행
if [[ -f ~/amazonqcli_lab/LabSetup/ekscluster.yaml ]]; then
    eksctl delete cluster -f ~/amazonqcli_lab/LabSetup/ekscluster.yaml 
else
    eksctl delete cluster --name ${EKSCLUSTER_NAME} --region ${AWS_REGION}
fi

echo ""
echo "🎉 EKS 클러스터 삭제가 완료되었습니다!"
echo ""
echo "💡 정리 작업:"
echo "   - kubectl 컨텍스트가 자동으로 제거되었습니다"
echo "   - 생성된 YAML 파일은 그대로 유지됩니다"
echo "   - 환경 변수는 .bash_profile에 그대로 유지됩니다"
