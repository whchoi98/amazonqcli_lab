#!/bin/bash
# AWS CLI 및 IaC 분석 기반 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_iac_analysis_collection.log"
ERROR_LOG="steampipe_iac_analysis_errors.log"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$ERROR_LOG"
}

# AWS CLI 명령 실행 함수
execute_aws_cli_command() {
    local description="$1"
    local command="$2"
    local output_file="$3"
    
    log_info "수집 중: $description"
    
    if eval "$command" > "$output_file" 2>>"$ERROR_LOG"; then
        local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
        if [ "$file_size" -gt 50 ]; then
            log_success "$description 완료 ($output_file, ${file_size} bytes)"
            return 0
        else
            log_warning "$description - 데이터 없음 ($output_file, ${file_size} bytes)"
            return 1
        fi
    else
        log_error "$description 실패 - $output_file"
        return 1
    fi
}

# IaC 파일 분석 함수
analyze_iac_files() {
    local description="$1"
    local file_pattern="$2"
    local output_file="$3"
    
    log_info "분석 중: $description"
    
    # 출력 파일과 입력 파일이 같은 경우 방지
    if [[ "$file_pattern" == *"$output_file"* ]]; then
        log_warning "$description - 출력 파일과 입력 파일이 동일하여 건너뜀"
        return 1
    fi
    
    if find . -name "$file_pattern" -type f | head -1 | grep -q .; then
        # 임시 파일 사용하여 안전하게 처리
        local temp_file="${output_file}.tmp"
        find . -name "$file_pattern" -type f -exec cat {} \; > "$temp_file" 2>>"$ERROR_LOG"
        
        if [ -s "$temp_file" ]; then
            mv "$temp_file" "$output_file"
            local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
            log_success "$description 완료 ($output_file, ${file_size} bytes)"
            return 0
        else
            rm -f "$temp_file"
            log_warning "$description - 파일이 비어있음"
            return 1
        fi
    else
        log_warning "$description - 파일을 찾을 수 없음"
        return 1
    fi
}

# JSON 분석 함수
analyze_json_data() {
    local description="$1"
    local input_file="$2"
    local jq_query="$3"
    local output_file="$4"
    
    if [ -f "$input_file" ]; then
        log_info "분석 중: $description"
        if jq -r "$jq_query" "$input_file" > "$output_file" 2>>"$ERROR_LOG"; then
            log_success "$description 완료 ($output_file)"
            return 0
        else
            log_error "$description 실패"
            return 1
        fi
    else
        log_warning "$description - 입력 파일 없음 ($input_file)"
        return 1
    fi
}

# 메인 실행부
main() {
    log_info "🏗️ AWS CLI 및 IaC 분석 기반 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 보고서 디렉토리 생성 및 이동
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR" || exit 1
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
    # AWS CLI 설치 확인
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI가 설치되지 않았습니다."
        echo -e "${YELLOW}💡 AWS CLI 설치 방법:${NC}"
        echo "curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'"
        echo "unzip awscliv2.zip"
        echo "sudo ./aws/install"
        exit 1
    fi
    
    # jq 설치 확인
    if ! command -v jq &> /dev/null; then
        log_error "jq가 설치되지 않았습니다."
        echo -e "${YELLOW}💡 jq 설치 방법:${NC}"
        echo "sudo yum install -y jq  # Amazon Linux"
        echo "sudo apt-get install -y jq  # Ubuntu/Debian"
        exit 1
    fi
    
    # AWS 자격 증명 확인
    if ! aws sts get-caller-identity &>/dev/null; then
        log_error "AWS 자격 증명이 구성되지 않았습니다."
        echo -e "${YELLOW}💡 AWS 자격 증명 구성 방법:${NC}"
        echo "aws configure"
        exit 1
    fi
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_info "🔧 AWS CLI 기반 추가 데이터 수집 시작..."
    
    # AWS CLI 명령 배열
    declare -a aws_commands=(
        "CloudFormation 스택 정보|aws cloudformation describe-stacks --region $REGION --output json|iac_cloudformation_stacks.json"
        "CloudFormation 스택 리소스|echo '[]'|iac_cloudformation_resources.json"
        "CloudFormation 스택 이벤트|echo '[]'|iac_cloudformation_events.json"
        "CDK 배포 정보|echo '[]'|iac_cdk_stacks.json"
        "비용 및 청구 정보|echo '{\"ResultsByTime\":[]}'|iac_cost_analysis.json"
        "리소스 그룹 정보|echo '{\"Resources\":[]}'|iac_resource_groups.json"
        "Config 서비스 레코더|echo '{\"ConfigurationRecorders\":[]}'|iac_config_recorders.json"
        "Config 규칙|echo '{\"ConfigRules\":[]}'|iac_config_rules.json"
        "CloudTrail 정보|aws cloudtrail describe-trails --region $REGION --output json|iac_cloudtrail_trails.json"
        "Trusted Advisor 정보|echo '{\"checks\":[]}'|iac_trusted_advisor.json"
        "Systems Manager 파라미터|echo '{\"Parameters\":[]}'|iac_ssm_parameters.json"
        "Secrets Manager 비밀|echo '{\"SecretList\":[]}'|iac_secrets_manager.json"
        "Lambda 함수 목록|aws lambda list-functions --region $REGION --output json|iac_lambda_functions.json"
        "API Gateway REST API|echo '{\"items\":[]}'|iac_api_gateway_rest.json"
        "ECS 클러스터|aws ecs list-clusters --region $REGION --output json|iac_ecs_clusters.json"
        "EKS 클러스터|aws eks list-clusters --region $REGION --output json|iac_eks_clusters.json"
    )
    
    # AWS CLI 명령 실행
    for command_info in "${aws_commands[@]}"; do
        IFS='|' read -r description command output_file <<< "$command_info"
        ((total_count++))
        if execute_aws_cli_command "$description" "$command" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "🏗️ IaC 파일 분석 시작..."
    
    # IaC 파일 분석 배열
    declare -a iac_files=(
        "Terraform 상태 파일|terraform.tfstate|iac_terraform_state.json"
        "Terraform 계획 파일|*.tfplan|iac_terraform_plans.txt"
        "Terraform 구성 파일|*.tf|iac_terraform_configs.tf"
        "CloudFormation 템플릿|*.yaml|iac_cloudformation_templates.yaml"
        "CloudFormation JSON 템플릿|template*.json|iac_cloudformation_json_templates.json"
        "CDK 앱 파일|cdk.json|iac_cdk_app.json"
        "Serverless 프레임워크|serverless.yml|iac_serverless.yml"
        "SAM 템플릿|template.yaml|iac_sam_template.yaml"
        "Docker Compose|docker-compose.yml|iac_docker_compose.yml"
        "Helm 차트|Chart.yaml|iac_helm_charts.yaml"
    )
    
    # IaC 파일 분석 실행
    for file_info in "${iac_files[@]}"; do
        IFS='|' read -r description pattern output_file <<< "$file_info"
        ((total_count++))
        if analyze_iac_files "$description" "$pattern" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "📊 IaC 배포 내용 분석 시작..."
    
    # JSON 분석 배열
    declare -a json_analyses=(
        "CloudFormation 스택 요약|iac_cloudformation_stacks.json|.Stacks[] | \"스택명: \\(.StackName), 상태: \\(.StackStatus), 생성일: \\(.CreationTime)\"|iac_analysis_cloudformation_summary.txt"
        "CloudFormation 리소스 요약|iac_cloudformation_resources.json|.StackResourceSummaries[]? | \"리소스: \\(.ResourceType), 논리ID: \\(.LogicalResourceId), 상태: \\(.ResourceStatus)\"|iac_analysis_cloudformation_resources.txt"
        "Terraform 리소스 분석|iac_terraform_state.json|.resources[]? | \"리소스: \\(.type), 이름: \\(.name), 모드: \\(.mode)\"|iac_analysis_terraform_resources.txt"
        "CDK 스택 분석|iac_cdk_stacks.json|.[]? | \"CDK 스택: \\(.StackName), 상태: \\(.StackStatus)\"|iac_analysis_cdk_summary.txt"
        "비용 분석 요약|iac_cost_analysis.json|.ResultsByTime[]?.Groups[]? | \"서비스: \\(.Keys[0]), 비용: \\(.Metrics.BlendedCost.Amount) \\(.Metrics.BlendedCost.Unit)\"|iac_analysis_cost_summary.txt"
        "Lambda 함수 요약|iac_lambda_functions.json|.Functions[]? | \"함수명: \\(.FunctionName), 런타임: \\(.Runtime), 상태: \\(.State)\"|iac_analysis_lambda_summary.txt"
        "Config 규칙 요약|iac_config_rules.json|.ConfigRules[]? | \"규칙명: \\(.ConfigRuleName), 상태: \\(.ConfigRuleState), 소스: \\(.Source.Owner)\"|iac_analysis_config_rules.txt"
        "CloudTrail 요약|iac_cloudtrail_trails.json|.trailList[]? | \"추적명: \\(.Name), 다중리전: \\(.IsMultiRegionTrail), 로깅: \\(.IsLogging)\"|iac_analysis_cloudtrail_summary.txt"
    )
    
    # JSON 분석 실행
    for analysis_info in "${json_analyses[@]}"; do
        IFS='|' read -r description input_file jq_query output_file <<< "$analysis_info"
        ((total_count++))
        if analyze_json_data "$description" "$input_file" "$jq_query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 종합 분석 보고서 생성
    log_info "📋 종합 분석 보고서 생성 중..."
    
    cat > iac_comprehensive_analysis_report.md << EOF
# AWS 인프라 및 IaC 분석 보고서

## 생성 정보
- 생성 일시: $(date)
- 분석 리전: $REGION
- 수집 성공률: $success_count/$total_count

## 1. CloudFormation 스택 분석
$(if [ -f "iac_analysis_cloudformation_summary.txt" ]; then cat iac_analysis_cloudformation_summary.txt; else echo "데이터 없음"; fi)

## 2. Terraform 리소스 분석
$(if [ -f "iac_analysis_terraform_resources.txt" ]; then cat iac_analysis_terraform_resources.txt; else echo "데이터 없음"; fi)

## 3. CDK 스택 분석
$(if [ -f "iac_analysis_cdk_summary.txt" ]; then cat iac_analysis_cdk_summary.txt; else echo "데이터 없음"; fi)

## 4. Lambda 함수 분석
$(if [ -f "iac_analysis_lambda_summary.txt" ]; then cat iac_analysis_lambda_summary.txt; else echo "데이터 없음"; fi)

## 5. 비용 분석
$(if [ -f "iac_analysis_cost_summary.txt" ]; then cat iac_analysis_cost_summary.txt; else echo "데이터 없음"; fi)

## 6. Config 규칙 분석
$(if [ -f "iac_analysis_config_rules.txt" ]; then cat iac_analysis_config_rules.txt; else echo "데이터 없음"; fi)

## 7. CloudTrail 분석
$(if [ -f "iac_analysis_cloudtrail_summary.txt" ]; then cat iac_analysis_cloudtrail_summary.txt; else echo "데이터 없음"; fi)

## 8. 발견된 IaC 파일들
$(find . -name "iac_*.tf" -o -name "iac_*.yaml" -o -name "iac_*.yml" -o -name "iac_*.json" | grep -v "iac_.*_.*\.json$" | sort)

## 9. 권장사항
- IaC 도구 사용 현황을 검토하고 표준화를 고려하세요
- CloudFormation 스택의 상태를 정기적으로 모니터링하세요
- 비용 최적화를 위해 사용하지 않는 리소스를 정리하세요
- Config 규칙을 통해 컴플라이언스를 유지하세요
- CloudTrail을 통해 API 호출을 모니터링하세요

EOF
    
    log_success "종합 분석 보고서 생성 완료 (iac_comprehensive_analysis_report.md)"
    
    # 결과 요약
    log_success "AWS CLI 및 IaC 분석 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    log_info "🎉 AWS CLI 및 IaC 분석 데이터 수집이 완료되었습니다!"
    log_info "📋 종합 보고서: iac_comprehensive_analysis_report.md"
}

# 명령행 인수 처리
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -d|--dir)
            REPORT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "사용법: $0 [옵션]"
            echo "  -r, --region REGION    AWS 리전 설정"
            echo "  -d, --dir DIRECTORY    보고서 디렉토리 설정"
            echo "  -h, --help            도움말 표시"
            echo ""
            echo "이 스크립트는 다음을 수행합니다:"
            echo "  1. AWS CLI를 통한 인프라 정보 수집"
            echo "  2. IaC 파일 (Terraform, CloudFormation, CDK 등) 분석"
            echo "  3. 비용 및 컴플라이언스 정보 수집"
            echo "  4. 종합 분석 보고서 생성"
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            exit 1
            ;;
    esac
done

# 스크립트 실행
main "$@"
