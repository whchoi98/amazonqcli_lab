# AWS 계정 종합 분석 보고서 - 구현 가이드

## 🎯 다른 계정에서 사용하기 위한 완전 가이드

### 1. 환경 준비

#### 필수 도구 설치
```bash
# 1. Steampipe 설치
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)"
steampipe plugin install aws

# 2. AWS CLI 설치 (Amazon Linux 2)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 3. Glow 설치 (마크다운 뷰어)
sudo wget -O /usr/local/bin/glow https://github.com/charmbracelet/glow/releases/latest/download/glow_Linux_x86_64
sudo chmod +x /usr/local/bin/glow

# 4. jq 설치 (JSON 처리)
sudo yum install -y jq  # Amazon Linux
# sudo apt-get install -y jq  # Ubuntu

# 5. bc 설치 (계산기)
sudo yum install -y bc  # Amazon Linux
# sudo apt-get install -y bc  # Ubuntu
```

#### AWS 자격 증명 구성
```bash
# AWS CLI 구성
aws configure
# AWS Access Key ID: [YOUR_ACCESS_KEY]
# AWS Secret Access Key: [YOUR_SECRET_KEY]
# Default region name: [YOUR_REGION]
# Default output format: json

# 권한 확인
aws sts get-caller-identity
```

### 2. 프로젝트 구조 생성

```bash
# 프로젝트 디렉토리 생성
mkdir -p aws-account-analysis/{scripts,templates,data,report/styles}
cd aws-account-analysis

# 실행 권한 부여
chmod +x scripts/*.sh
```

### 3. 핵심 스크립트 파일들

#### A. 데이터 수집 스크립트 (scripts/collect_data.sh)
```bash
#!/bin/bash
set -e

echo "🔍 AWS 리소스 데이터 수집 시작..."

# 환경 변수
export AWS_REGION=$(aws configure get region)
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

mkdir -p data/

# VPC 데이터 수집
steampipe query "
SELECT 
    vpc_id, cidr_block, state, is_default,
    tags ->> 'Name' as vpc_name,
    tags ->> 'Project' as project
FROM aws_vpc
ORDER BY is_default DESC, vpc_id;
" --output json > data/vpcs.json

# EC2 인스턴스 데이터 수집
steampipe query "
SELECT 
    instance_id, instance_type, instance_state, 
    vpc_id, availability_zone, launch_time,
    tags ->> 'Name' as instance_name,
    tags ->> 'Environment' as environment
FROM aws_ec2_instance
ORDER BY launch_time DESC;
" --output json > data/instances.json

# EBS 볼륨 데이터 수집
steampipe query "
SELECT 
    volume_id, volume_type, size, encrypted, 
    state, availability_zone, create_time
FROM aws_ebs_volume
ORDER BY create_time DESC;
" --output json > data/volumes.json

# 보안 그룹 데이터 수집
steampipe query "
SELECT 
    group_id, group_name, vpc_id, description,
    ip_permissions, ip_permissions_egress
FROM aws_vpc_security_group
ORDER BY vpc_id, group_name;
" --output json > data/security_groups.json

# IAM 역할 데이터 수집
steampipe query "
SELECT 
    role_name, arn, create_date,
    assume_role_policy_document
FROM aws_iam_role
ORDER BY create_date DESC;
" --output json > data/iam_roles.json

echo "✅ 데이터 수집 완료!"
```

#### B. HTML 생성 스크립트 (scripts/generate_html.sh)
```bash
#!/bin/bash
set -e

echo "🚀 HTML 보고서 생성 시작..."

# 환경 변수 설정
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=$(aws configure get region)
export ANALYSIS_DATE=$(date +"%Y년 %m월 %d일")

# 데이터 로드
VPC_DATA=$(cat data/vpcs.json)
INSTANCE_DATA=$(cat data/instances.json)
VOLUME_DATA=$(cat data/volumes.json)
SG_DATA=$(cat data/security_groups.json)
IAM_DATA=$(cat data/iam_roles.json)

# 통계 계산
VPC_COUNT=$(echo "$VPC_DATA" | jq length)
INSTANCE_COUNT=$(echo "$INSTANCE_DATA" | jq length)
VOLUME_COUNT=$(echo "$VOLUME_DATA" | jq length)
ENCRYPTED_VOLUMES=$(echo "$VOLUME_DATA" | jq '[.[] | select(.encrypted == true)] | length')
ENCRYPTION_RATIO=$(echo "scale=0; $ENCRYPTED_VOLUMES * 100 / $VOLUME_COUNT" | bc)

# CSS 파일 생성
generate_css

# 각 HTML 페이지 생성
generate_index_page
generate_networking_page
generate_computing_page
generate_storage_page
generate_security_page
generate_cost_optimization_page

echo "✅ HTML 보고서 생성 완료!"
```

#### C. CSS 생성 함수 (scripts/generate_css.sh)
```bash
generate_css() {
cat > report/styles/main.css << 'EOF'
/* AWS 계정 종합 분석 보고서 - 메인 스타일시트 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.detail-page {
    background: white;
    border-radius: 15px;
    padding: 40px;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
    background: #f8f9fa;
    padding: 15px 20px;
    border-radius: 8px;
    margin-bottom: 30px;
}

.breadcrumb a {
    color: #3498db;
    text-decoration: none;
}

.analysis-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    overflow: hidden;
}

.analysis-table th {
    background: #3498db;
    color: white;
    padding: 15px;
    text-align: left;
    font-weight: 600;
}

.analysis-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #e9ecef;
}

.analysis-table tr:hover {
    background: #f8f9fa;
}

.summary-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-bottom: 40px;
}

.summary-card {
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.summary-card.success {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    border-left: 5px solid #28a745;
}

.summary-card.warning {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border-left: 5px solid #ffc107;
}

.nav-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #e9ecef;
}

.nav-btn {
    background: #3498db;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
}

.nav-btn:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
    .summary-grid { grid-template-columns: 1fr; }
    .container { padding: 10px; }
    .detail-page { padding: 20px; }
}
EOF
}
```

### 4. HTML 페이지 생성 함수들

#### A. 인덱스 페이지 생성
```bash
generate_index_page() {
cat > report/index.html << EOF
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS 계정 종합 분석 보고서</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="detail-page">
            <header>
                <h1>🎯 AWS 계정 종합 분석 보고서</h1>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div><strong>분석 대상:</strong> AWS 계정 $ACCOUNT_ID</div>
                    <div><strong>분석 리전:</strong> $AWS_REGION</div>
                    <div><strong>분석 일시:</strong> $ANALYSIS_DATE</div>
                    <div><strong>총 리소스:</strong> VPC $VPC_COUNT개, EC2 $INSTANCE_COUNT개</div>
                </div>
            </header>

            <section>
                <h2>📋 Executive Summary</h2>
                <div class="summary-grid">
                    <div class="summary-card success">
                        <h3>✅ 강점</h3>
                        <ul>
                            <li>잘 구조화된 네트워킹 ($VPC_COUNT개 VPC)</li>
                            <li>적절한 인스턴스 분산 ($INSTANCE_COUNT개)</li>
                            <li>부분적 암호화 적용 ($ENCRYPTION_RATIO%)</li>
                        </ul>
                    </div>
                    <div class="summary-card warning">
                        <h3>⚠️ 개선 기회</h3>
                        <ul>
                            <li>비용 최적화: Reserved Instance 검토</li>
                            <li>보안 강화: 전체 볼륨 암호화</li>
                            <li>모니터링: CloudWatch 구성</li>
                        </ul>
                    </div>
                </div>
            </section>

            <section>
                <h2>📚 상세 분석 보고서</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    <a href="networking.html" style="text-decoration: none; color: inherit;">
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #3498db;">
                            <h3>🌐 Phase 1: 네트워킹 분석</h3>
                            <p>VPC, 서브넷, 보안 그룹 분석</p>
                            <div style="margin-top: 10px;">
                                <span style="background: #3498db; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">$VPC_COUNT개 VPC</span>
                            </div>
                        </div>
                    </a>
                    
                    <a href="computing.html" style="text-decoration: none; color: inherit;">
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #28a745;">
                            <h3>💻 Phase 2: 컴퓨팅 분석</h3>
                            <p>EC2 인스턴스, EKS 클러스터 분석</p>
                            <div style="margin-top: 10px;">
                                <span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">$INSTANCE_COUNT개 인스턴스</span>
                            </div>
                        </div>
                    </a>
                    
                    <a href="storage.html" style="text-decoration: none; color: inherit;">
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107;">
                            <h3>💾 Phase 3: 스토리지 분석</h3>
                            <p>EBS 볼륨, 스냅샷 분석</p>
                            <div style="margin-top: 10px;">
                                <span style="background: #ffc107; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">$VOLUME_COUNT개 볼륨</span>
                            </div>
                        </div>
                    </a>
                </div>
            </section>
        </div>
    </div>
</body>
</html>
EOF
}
```

### 5. 실행 방법

#### 단계별 실행
```bash
# 1. 프로젝트 클론 또는 생성
git clone [YOUR_REPO] aws-account-analysis
cd aws-account-analysis

# 2. 환경 설정
./scripts/setup_environment.sh

# 3. AWS 자격 증명 구성
aws configure

# 4. 데이터 수집
./scripts/collect_data.sh

# 5. HTML 보고서 생성
./scripts/generate_html.sh

# 6. 결과 확인
open report/index.html  # macOS
# 또는 브라우저에서 file:///path/to/report/index.html 열기
```

#### 원클릭 실행 스크립트
```bash
#!/bin/bash
# run_analysis.sh - 전체 분석 실행

set -e

echo "🚀 AWS 계정 종합 분석 시작..."

# 환경 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되지 않았습니다."
    exit 1
fi

if ! command -v steampipe &> /dev/null; then
    echo "❌ Steampipe가 설치되지 않았습니다."
    exit 1
fi

# AWS 자격 증명 확인
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS 자격 증명을 확인할 수 없습니다."
    exit 1
fi

# 데이터 수집
echo "📊 데이터 수집 중..."
./scripts/collect_data.sh

# HTML 생성
echo "📄 HTML 보고서 생성 중..."
./scripts/generate_html.sh

echo "✅ 분석 완료!"
echo "📂 결과: $(pwd)/report/index.html"

# 자동으로 브라우저 열기 (선택적)
if command -v open &> /dev/null; then
    open report/index.html
elif command -v xdg-open &> /dev/null; then
    xdg-open report/index.html
fi
```

### 6. 커스터마이징 가이드

#### 리전별 가격 설정
```bash
# scripts/pricing.sh
get_instance_pricing() {
    local instance_type="$1"
    local region="$2"
    
    case "$region" in
        "us-east-1")
            case "$instance_type" in
                "t3.small") echo "0.0208" ;;
                "t3.medium") echo "0.0416" ;;
                "m6i.xlarge") echo "0.1920" ;;
            esac
            ;;
        "ap-northeast-2")
            case "$instance_type" in
                "t3.small") echo "0.0251" ;;
                "t3.medium") echo "0.0502" ;;
                "m6i.xlarge") echo "0.2304" ;;
            esac
            ;;
        # 다른 리전 추가...
    esac
}
```

#### 회사별 커스터마이징
```bash
# config/company_config.sh
export COMPANY_NAME="Your Company"
export COMPANY_LOGO_URL="https://your-company.com/logo.png"
export REPORT_TITLE="$COMPANY_NAME AWS 계정 분석 보고서"
export PRIMARY_COLOR="#your-brand-color"
```

이 가이드를 따라하면 어떤 AWS 계정에서도 동일한 품질의 종합 분석 보고서를 생성할 수 있습니다.
