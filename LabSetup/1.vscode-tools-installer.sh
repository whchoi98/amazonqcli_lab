#!/bin/bash

# 🛠️ AWS 및 EKS 개발 도구 통합 설치 스크립트
# 포함 도구: AWS CLI, Session Manager, kubectl, eksctl, helm, k9s, fzf, kns, ktx, jq, gettext, bash-completion, sponge

set -e

KUBECTL_VERSION="1.33.0"
HELM_VERSION="4.1.1"
K9S_VERSION="0.50.18"
CURRENT_USER=$(whoami)
export HOME="/home/${CURRENT_USER}"

echo "======================================================"
echo "🚀 AWS 및 EKS 개발 도구 통합 설치 시작"
echo "👤 사용자: $CURRENT_USER"
echo "🏠 HOME 디렉토리: $HOME"
echo "======================================================"

# AWS CLI 설치
echo "------------------------------------------------------"
echo "☁️  [1/9] AWS CLI 설치 중..."
echo "------------------------------------------------------"

# AWS CLI 다운로드 및 설치
curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && echo "✅ AWS CLI zip 파일 다운로드 완료"
unzip -q awscliv2.zip && echo "✅ 압축 해제 완료"
sudo ./aws/install && echo "✅ AWS CLI 설치 완료"

# PATH 및 자동완성 설정
export PATH=/usr/local/bin:$PATH
source ~/.bashrc 2>/dev/null || true
source ~/.bash_profile 2>/dev/null || true

# 자동완성 등록
if command -v aws_completer &> /dev/null; then
  complete -C "$(which aws_completer)" aws && echo "✅ AWS CLI 자동완성 활성화 완료"
fi

# 버전 확인
aws --version && echo "✅ AWS CLI 버전 확인 완료"

# Session Manager 플러그인 설치
echo "------------------------------------------------------"
echo "🔐 [2/9] Session Manager 플러그인 설치 중..."
echo "------------------------------------------------------"

curl -s "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm" -o "session-manager-plugin.rpm" && echo "✅ 플러그인 RPM 다운로드 완료"
sudo yum install -y session-manager-plugin.rpm && echo "✅ 플러그인 설치 완료"
session-manager-plugin --version && echo "✅ Session Manager 버전 확인 완료"

# 기본 유틸리티 설치
echo "------------------------------------------------------"
echo "🔧 [3/9] 기본 유틸리티 설치 중..."
echo "------------------------------------------------------"

sudo yum -y install jq gettext bash-completion && echo "✅ 기본 유틸리티 설치 완료"

# sponge 설치 (moreutils 패키지)
if ! command -v sponge &>/dev/null; then
  echo "📦 sponge 설치 중..."
  sudo yum -y install moreutils 2>/dev/null || {
    echo "   moreutils 패키지 없음, 소스에서 컴파일 중..."
    curl -sLO https://raw.githubusercontent.com/joeyh/moreutils/master/sponge.c
    gcc -o sponge sponge.c
    sudo mv sponge /usr/local/bin/
    rm -f sponge.c
  }
  echo "✅ sponge 설치 완료"
fi

# kubectl 설치
echo "------------------------------------------------------"
echo "📦 [4/9] kubectl ${KUBECTL_VERSION} 설치 중..."
echo "------------------------------------------------------"

curl -sLO "https://s3.us-west-2.amazonaws.com/amazon-eks/${KUBECTL_VERSION}/2025-05-01/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client --output=yaml
kubectl completion bash > "${HOME}/.kubectl_completion"
grep -q 'source.*\.kubectl_completion' "${HOME}/.bashrc" 2>/dev/null || echo "source ${HOME}/.kubectl_completion" >> "${HOME}/.bashrc"
source "${HOME}/.kubectl_completion" 2>/dev/null || true
echo "✅ kubectl 설치 완료"

# fzf, kns, ktx 설치
echo "------------------------------------------------------"
echo "🔍 [5/9] fzf, kns, ktx 설치 중..."
echo "------------------------------------------------------"

if [ -d ~/.fzf ]; then
  cd ~/.fzf && git pull
else
  git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
fi
~/.fzf/install --all --no-zsh --no-fish

wget -q https://raw.githubusercontent.com/blendle/kns/master/bin/kns
wget -q https://raw.githubusercontent.com/blendle/kns/master/bin/ktx
chmod +x kns ktx
sudo mv kns ktx /usr/local/bin/

# kubectl 유용한 alias 추가
grep -q 'alias kgn=' "${HOME}/.bashrc" 2>/dev/null || echo "alias kgn='kubectl get nodes -L beta.kubernetes.io/arch -L eks.amazonaws.com/capacityType -L beta.kubernetes.io/instance-type -L eks.amazonaws.com/nodegroup -L topology.kubernetes.io/zone -L karpenter.sh/provisioner-name -L karpenter.sh/capacity-type'" >> "${HOME}/.bashrc"

echo "✅ fzf, kns, ktx 설치 완료"

# eksctl 설치
echo "------------------------------------------------------"
echo "🚀 [6/9] eksctl 설치 중..."
echo "------------------------------------------------------"

curl -sSL "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
. <(eksctl completion bash) 2>/dev/null || true
eksctl version
echo "✅ eksctl 설치 완료"

# Helm 설치
echo "------------------------------------------------------"
echo "⚓ [7/9] Helm ${HELM_VERSION} 설치 중..."
echo "------------------------------------------------------"

cd ~
wget -q "https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz"
tar -zxf helm-v${HELM_VERSION}-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
helm version --short

# Helm 저장소 추가
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Helm 자동완성 설정
helm completion bash > ~/.helm_completion
grep -q 'source.*\.helm_completion' "${HOME}/.bashrc" 2>/dev/null || echo "source ~/.helm_completion" >> "${HOME}/.bashrc"
. ~/.helm_completion 2>/dev/null || true

echo "✅ Helm 설치 완료"

# K9s 설치
echo "------------------------------------------------------"
echo "🎮 [8/9] K9s ${K9S_VERSION} 설치 중..."
echo "------------------------------------------------------"

cd ~
wget -q "https://github.com/derailed/k9s/releases/download/v${K9S_VERSION}/k9s_Linux_amd64.tar.gz"
tar -zxf k9s_Linux_amd64.tar.gz
sudo mv k9s /usr/local/bin/
k9s version
echo "✅ K9s 설치 완료"

# Bash 자동완성 최종 설정
echo "------------------------------------------------------"
echo "🧠 [9/9] Bash 자동완성 최종 구성 중..."
echo "------------------------------------------------------"

# /etc/profile.d/bash_completion.sh가 존재하면 로드
if [ -f /etc/profile.d/bash_completion.sh ]; then
  grep -q 'bash_completion.sh' "${HOME}/.bash_profile" 2>/dev/null || \
    echo "[ -f /etc/profile.d/bash_completion.sh ] && . /etc/profile.d/bash_completion.sh" >> "${HOME}/.bash_profile"
fi

# 설치된 도구 확인
echo "------------------------------------------------------"
echo "🔍 설치된 도구 확인 중..."
echo "------------------------------------------------------"

for cmd in aws session-manager-plugin kubectl eksctl helm k9s jq envsubst sponge kns ktx; do
  if command -v $cmd &>/dev/null; then
    echo "✅ $cmd: 설치됨"
  else
    echo "❌ $cmd: 설치 실패"
  fi
done

# 정리 작업
echo "------------------------------------------------------"
echo "🧹 임시 파일 정리 중..."
echo "------------------------------------------------------"

cd ~
rm -rf awscliv2.zip aws/ session-manager-plugin.rpm helm-v${HELM_VERSION}-linux-amd64.tar.gz linux-amd64/ k9s_Linux_amd64.tar.gz
echo "✅ 정리 완료"

echo "======================================================"
echo "🎉 모든 도구 설치가 성공적으로 완료되었습니다!"
echo ""
echo "📦 설치된 도구 목록:"
echo "   ☁️  AWS CLI + Session Manager Plugin"
echo "   🎯 kubectl ${KUBECTL_VERSION}"
echo "   🚀 eksctl (최신 버전)"
echo "   ⚓ Helm ${HELM_VERSION}"
echo "   🎮 K9s ${K9S_VERSION}"
echo "   🔍 fzf (퍼지 파인더)"
echo "   🎛️  kns, ktx (네임스페이스/컨텍스트 스위처)"
echo "   🔧 jq, gettext, bash-completion, sponge"
echo ""
echo "💡 사용 팁:"
echo "   - 새 터미널을 열거나 'source ~/.bashrc'를 실행하세요"
echo "   - kubectl 자동완성이 활성화되었습니다"
echo "   - kns로 네임스페이스, ktx로 컨텍스트를 쉽게 변경할 수 있습니다"
echo "   - kgn 명령으로 노드 상세 정보를 확인할 수 있습니다"
echo "   - k9s를 실행하여 대화형 Kubernetes 관리 도구를 사용할 수 있습니다"
echo ""
echo "📘 Welcome to the exciting world of AWS and EKS!"
echo "======================================================"
