#!/bin/bash
echo "🔍 AWS 아키텍처 분석 환경 검증 시작..."
echo ""

# Python 패키지 확인
echo "📦 Python 패키지 확인:"
python3 -c "import markdown; print('  ✅ markdown')" 2>/dev/null || echo "  ❌ markdown"
python3 -c "import bs4; print('  ✅ beautifulsoup4')" 2>/dev/null || echo "  ❌ beautifulsoup4"
python3 -c "import pygments; print('  ✅ pygments')" 2>/dev/null || echo "  ❌ pygments"

echo ""

# Glow 확인
echo "📖 Glow 확인:"
glow --version >/dev/null 2>&1 && echo "  ✅ Glow 설치됨" || echo "  ❌ Glow 미설치"

echo ""

# Steampipe 확인
echo "🔧 Steampipe 확인:"
steampipe --version >/dev/null 2>&1 && echo "  ✅ Steampipe 설치됨" || echo "  ❌ Steampipe 미설치"

# Steampipe 플러그인 확인
if command -v steampipe >/dev/null 2>&1; then
    echo "🔌 Steampipe 플러그인 확인:"
    steampipe plugin list | grep -q aws && echo "  ✅ AWS 플러그인" || echo "  ❌ AWS 플러그인"
    steampipe plugin list | grep -q kubernetes && echo "  ✅ Kubernetes 플러그인" || echo "  ❌ Kubernetes 플러그인"
fi

echo ""

# AWS 자격 증명 확인
echo "🔐 AWS 자격 증명 확인:"
aws sts get-caller-identity >/dev/null 2>&1 && echo "  ✅ AWS CLI 인증됨" || echo "  ❌ AWS CLI 인증 실패"

echo ""

# kubectl 확인 (선택사항)
echo "☸️ Kubernetes 도구 확인:"
kubectl version --client >/dev/null 2>&1 && echo "  ✅ kubectl 설치됨" || echo "  ❌ kubectl 미설치"

echo ""

# 추가 도구 확인
echo "🛠️ 추가 도구 확인:"
jq --version >/dev/null 2>&1 && echo "  ✅ jq" || echo "  ❌ jq"
which curl >/dev/null 2>&1 && echo "  ✅ curl" || echo "  ❌ curl"
which git >/dev/null 2>&1 && echo "  ✅ git" || echo "  ❌ git"

echo ""
echo "🎉 환경 검증 완료!"
echo ""
echo "📋 설치가 필요한 패키지가 있다면 다음 명령어를 실행하세요:"
echo ""
echo "# Python 패키지 설치:"
echo "python3 -m ensurepip --default-pip --user 2>/dev/null || curl https://bootstrap.pypa.io/get-pip.py | python3 - --user"
echo "pip3 install markdown beautifulsoup4 pygments --user"
echo ""
echo "# Steampipe 설치:"
echo "sudo /bin/sh -c \"\$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)\""
echo "steampipe plugin install aws"
echo "steampipe plugin install kubernetes"
echo ""
echo "# Glow 설치 (선택사항):"
echo "sudo yum install -y glow"
