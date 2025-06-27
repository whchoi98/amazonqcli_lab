#!/bin/bash

# 최적화된 Amazon Q MCP 설정 스크립트
# 현재 시스템 상태를 고려한 효율적인 설치

set -e

echo "======================================================"
echo "🚀 최적화된 Amazon Q MCP 설정 시작"
echo "======================================================"

# 현재 상태 확인
echo "📋 [1/6] 현재 시스템 상태 확인..."
echo "   Python: $(python3 --version)"
echo "   Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "   AWS: $(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 'Not configured')"

# Python 3.12 설치 (Amazon Linux 2023 최적화)
echo "🐍 [2/6] Python 3.12 설치 중..."
if ! command -v python3.12 &> /dev/null; then
    # Amazon Linux 2023에서 더 빠른 방법: dnf 사용
    sudo dnf install -y python3.12 python3.12-pip python3.12-devel
    
    # 만약 dnf로 설치되지 않으면 소스 컴파일
    if ! command -v python3.12 &> /dev/null; then
        echo "   📦 소스에서 컴파일 중... (시간이 걸릴 수 있습니다)"
        sudo dnf groupinstall "Development Tools" -y
        sudo dnf install -y openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel
        
        cd /tmp
        wget -q https://www.python.org/ftp/python/3.12.7/Python-3.12.7.tgz
        tar xzf Python-3.12.7.tgz
        cd Python-3.12.7
        ./configure --enable-optimizations --prefix=/usr/local
        make -j $(nproc) > /dev/null 2>&1
        sudo make altinstall > /dev/null 2>&1
        cd ~
    fi
else
    echo "   ✅ Python 3.12 이미 설치됨"
fi

# uv 설치
echo "⚡ [3/6] uv 패키지 매니저 설치 중..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "   ✅ uv 이미 설치됨"
fi

# Node.js 버전 확인 및 업그레이드 (필요시)
echo "📦 [4/6] Node.js 상태 확인..."
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "   🔄 Node.js 업그레이드 중..."
    sudo dnf install -y nodejs npm
else
    echo "   ✅ Node.js 버전 적합 (v$(node --version))"
fi

# AWS Bedrock 액세스 확인
echo "🔐 [5/6] AWS Bedrock 액세스 확인..."
if aws bedrock list-foundation-models --region us-east-1 --max-items 1 > /dev/null 2>&1; then
    echo "   ✅ Bedrock 액세스 확인됨"
else
    echo "   ⚠️  Bedrock 액세스 확인 실패 - IAM 권한을 확인하세요"
    echo "      필요한 권한: bedrock:ListFoundationModels, bedrock:InvokeModel"
fi

# MCP 설정 파일은 별도로 생성하세요 (5.setup-mcp-config.sh 사용)
echo "📝 [6/6] MCP 설정 파일 생성은 별도 스크립트로 진행하세요..."
echo "   ./5.setup-mcp-config.sh 를 실행하여 MCP 서버 설정을 완료하세요"

# 환경 변수 설정
echo "🔧 환경 변수 설정..."
if ! grep -q "export PATH=.*\.local/bin" ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# 설치 확인
echo ""
echo "======================================================"
echo "✅ 설치 완료! 버전 확인:"
echo "   Python: $(python3.12 --version 2>/dev/null || echo 'Installation failed')"
echo "   uv: $(~/.local/bin/uv --version 2>/dev/null || echo 'Installation failed')"
echo "   Node.js: $(node --version)"
echo "   npm: $(npm --version)"
echo ""
echo "🎉 기본 패키지 설치가 완료되었습니다!"
echo ""
echo "💡 다음 단계:"
echo "   1. 새 터미널을 열거나 'source ~/.bashrc' 실행"
echo "   2. './5.setup-mcp-config.sh' 실행하여 MCP 서버 설정"
echo "   3. Amazon Q CLI 재시작"
echo "   4. 'q chat' 명령어로 확장된 기능 사용"
echo "======================================================"
