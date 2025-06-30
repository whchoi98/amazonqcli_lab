#!/bin/bash
# AWS 아키텍처 분석 도구 자동 설치 스크립트 (Linux/macOS 지원)

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 AWS 아키텍처 분석 도구 자동 설치 시작..."
echo ""

# OS 감지 함수
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v yum >/dev/null 2>&1; then
            echo "amazon-linux"
        elif command -v apt >/dev/null 2>&1; then
            echo "ubuntu"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# 진행 상황 표시 함수
show_progress() {
    echo "📦 $1..."
}

# 오류 처리 함수
handle_error() {
    echo "❌ 오류 발생: $1"
    echo "💡 수동 설치를 시도하거나 ./check-environment.sh를 실행하여 가이드를 확인하세요."
    exit 1
}

# OS 감지
OS=$(detect_os)
echo "💻 감지된 운영체제: $OS"
echo ""

# 설치 함수들
install_amazon_linux() {
    show_progress "Amazon Linux 패키지 업데이트"
    sudo yum update -y || handle_error "패키지 업데이트 실패"
    
    show_progress "기본 도구 설치"
    sudo yum install -y python3 python3-pip jq git zip curl unzip || handle_error "기본 도구 설치 실패"
    
    show_progress "Python 패키지 설치"
    pip3 install markdown beautifulsoup4 pygments --user || handle_error "Python 패키지 설치 실패"
    
    show_progress "AWS CLI v2 설치"
    if ! command -v aws >/dev/null 2>&1; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" || handle_error "AWS CLI 다운로드 실패"
        unzip awscliv2.zip || handle_error "AWS CLI 압축 해제 실패"
        sudo ./aws/install || handle_error "AWS CLI 설치 실패"
        rm -rf aws awscliv2.zip
    else
        echo "  ✅ AWS CLI 이미 설치됨"
    fi
    
    show_progress "Steampipe 설치"
    if ! command -v steampipe >/dev/null 2>&1; then
        sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)" || handle_error "Steampipe 설치 실패"
        steampipe plugin install aws || handle_error "AWS 플러그인 설치 실패"
        steampipe plugin install kubernetes || handle_error "Kubernetes 플러그인 설치 실패"
    else
        echo "  ✅ Steampipe 이미 설치됨"
    fi
}

install_ubuntu() {
    show_progress "Ubuntu 패키지 업데이트"
    sudo apt update || handle_error "패키지 업데이트 실패"
    
    show_progress "기본 도구 설치"
    sudo apt install -y python3 python3-pip jq git zip curl unzip || handle_error "기본 도구 설치 실패"
    
    show_progress "Python 패키지 설치"
    pip3 install markdown beautifulsoup4 pygments --user || handle_error "Python 패키지 설치 실패"
    
    show_progress "AWS CLI v2 설치"
    if ! command -v aws >/dev/null 2>&1; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" || handle_error "AWS CLI 다운로드 실패"
        unzip awscliv2.zip || handle_error "AWS CLI 압축 해제 실패"
        sudo ./aws/install || handle_error "AWS CLI 설치 실패"
        rm -rf aws awscliv2.zip
    else
        echo "  ✅ AWS CLI 이미 설치됨"
    fi
    
    show_progress "Steampipe 설치"
    if ! command -v steampipe >/dev/null 2>&1; then
        sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)" || handle_error "Steampipe 설치 실패"
        steampipe plugin install aws || handle_error "AWS 플러그인 설치 실패"
        steampipe plugin install kubernetes || handle_error "Kubernetes 플러그인 설치 실패"
    else
        echo "  ✅ Steampipe 이미 설치됨"
    fi
}

install_macos() {
    # Homebrew 확인 및 설치
    if ! command -v brew >/dev/null 2>&1; then
        show_progress "Homebrew 설치"
        echo "🍺 Homebrew를 설치합니다. 관리자 권한이 필요할 수 있습니다."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || handle_error "Homebrew 설치 실패"
        
        # Homebrew PATH 설정 (Apple Silicon Mac 대응)
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        echo "  ✅ Homebrew 이미 설치됨"
    fi
    
    show_progress "Homebrew 업데이트"
    brew update || handle_error "Homebrew 업데이트 실패"
    
    show_progress "기본 도구 설치"
    brew install python3 jq git curl || handle_error "기본 도구 설치 실패"
    
    show_progress "Python 패키지 설치"
    pip3 install markdown beautifulsoup4 pygments --user || handle_error "Python 패키지 설치 실패"
    
    show_progress "AWS CLI 설치"
    if ! command -v aws >/dev/null 2>&1; then
        brew install awscli || handle_error "AWS CLI 설치 실패"
    else
        echo "  ✅ AWS CLI 이미 설치됨"
    fi
    
    show_progress "Steampipe 설치"
    if ! command -v steampipe >/dev/null 2>&1; then
        brew install turbot/tap/steampipe || handle_error "Steampipe 설치 실패"
        steampipe plugin install aws || handle_error "AWS 플러그인 설치 실패"
        steampipe plugin install kubernetes || handle_error "Kubernetes 플러그인 설치 실패"
    else
        echo "  ✅ Steampipe 이미 설치됨"
    fi
    
    show_progress "선택적 도구 설치"
    brew install kubectl glow 2>/dev/null || echo "  ⚠️ 선택적 도구 설치 중 일부 실패 (무시 가능)"
}

# OS별 설치 실행
case $OS in
    "amazon-linux")
        install_amazon_linux
        ;;
    "ubuntu")
        install_ubuntu
        ;;
    "macos")
        install_macos
        ;;
    *)
        echo "❌ 지원되지 않는 운영체제입니다: $OS"
        echo "💡 ./check-environment.sh를 실행하여 수동 설치 가이드를 확인하세요."
        exit 1
        ;;
esac

echo ""
echo "🎉 설치 완료!"
echo ""
echo "🔧 다음 단계:"
echo "1. AWS 자격 증명 설정:"
echo "   aws configure"
echo ""
echo "2. 환경 검증:"
echo "   ./check-environment.sh"
echo ""
echo "3. 분석 시작:"
echo "   ./convert-md-to-html-simple.sh"
echo ""
echo "💡 문제가 발생하면 ./check-environment.sh를 실행하여 상세한 상태를 확인하세요."
