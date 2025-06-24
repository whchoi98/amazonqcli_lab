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

# 분석 보고서 생성 함수
generate_analysis_report() {
    local description="$1"
    local input_file="$2"
    local jq_filter="$3"
    local output_file="$4"
    
    log_info "분석 중: $description"
    
    if [ -f "$input_file" ] && [ -s "$input_file" ]; then
        if jq -r "$jq_filter" "$input_file" > "$output_file" 2>>"$ERROR_LOG"; then
            local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
            log_success "$description 완료 ($output_file, ${file_size} bytes)"
            return 0
        else
            log_error "$description 실패 - $output_file"
            return 1
        fi
    else
        log_warning "$description - 입력 파일 없음 ($input_file)"
        return 1
    fi
}

# 메인 함수
main() {
    log_info "🚀 AWS CLI 및 IaC 분석 기반 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 디렉토리 생성
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR"
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_info "🏗️ Infrastructure as Code 분석 시작..."
    
    # AWS CLI 기반 데이터 수집 배열
    declare -a aws_commands=(
        # CloudFormation
        "CloudFormation 스택 정보|aws cloudformation describe-stacks --region $REGION --output json|iac_cloudformation_stacks.json"
        "CloudFormation 스택 리소스|aws cloudformation list-stack-resources --region $REGION --stack-name \$(aws cloudformation describe-stacks --region $REGION --query 'Stacks[0].StackName' --output text 2>/dev/null || echo 'dummy') --output json 2>/dev/null || echo '[]'|iac_cloudformation_resources.json"
        "CloudFormation 스택 이벤트|aws cloudformation describe-stack-events --region $REGION --stack-name \$(aws cloudformation describe-stacks --region $REGION --query 'Stacks[0].StackName' --output text 2>/dev/null || echo 'dummy') --output json 2>/dev/null || echo '[]'|iac_cloudformation_events.json"
        
        # AWS Config
        "Config 구성 레코더|aws configservice describe-configuration-recorders --region $REGION --output json|iac_config_recorders.json"
        "Config 규칙|aws configservice describe-config-rules --region $REGION --output json|iac_config_rules.json"
        "Config 규정 준수|aws configservice describe-compliance-by-config-rule --region $REGION --output json|iac_config_compliance.json"
        
        # CloudTrail
        "CloudTrail 정보|aws cloudtrail describe-trails --region $REGION --output json|iac_cloudtrail_trails.json"
        "CloudTrail 이벤트 선택기|aws cloudtrail get-event-selectors --region $REGION --trail-name \$(aws cloudtrail describe-trails --region $REGION --query 'trailList[0].Name' --output text 2>/dev/null || echo 'dummy') --output json 2>/dev/null || echo '{}'|iac_cloudtrail_selectors.json"
        
        # Systems Manager
        "SSM 파라미터|aws ssm describe-parameters --region $REGION --output json|iac_ssm_parameters.json"
        "SSM 문서|aws ssm list-documents --region $REGION --output json|iac_ssm_documents.json"
        
        # Lambda (IaC 관련)
        "Lambda 함수 목록|aws lambda list-functions --region $REGION --output json|iac_lambda_functions.json"
        
        # Cost Explorer (지난 30일)
        "비용 분석|aws ce get-cost-and-usage --region us-east-1 --time-period Start=\$(date -d '30 days ago' +%Y-%m-%d),End=\$(date +%Y-%m-%d) --granularity MONTHLY --metrics BlendedCost --group-by Type=DIMENSION,Key=SERVICE --output json|iac_cost_analysis.json"
        
        # Organizations (조직 정보)
        "조직 정보|aws organizations describe-organization --region us-east-1 --output json 2>/dev/null || echo '{}'|iac_organization_info.json"
        "조직 계정|aws organizations list-accounts --region us-east-1 --output json 2>/dev/null || echo '{}'|iac_organization_accounts.json"
        
        # Service Catalog
        "Service Catalog 포트폴리오|aws servicecatalog list-portfolios --region $REGION --output json|iac_servicecatalog_portfolios.json"
        "Service Catalog 제품|aws servicecatalog search-products --region $REGION --output json|iac_servicecatalog_products.json"
        
        # Resource Groups
        "리소스 그룹|aws resource-groups list-groups --region $REGION --output json|iac_resource_groups.json"
        
        # Tags
        "태그 리소스|aws resourcegroupstaggingapi get-resources --region $REGION --output json|iac_tagged_resources.json"
    )
    
    # AWS CLI 명령 실행
    for command_info in "${aws_commands[@]}"; do
        IFS='|' read -r description command output_file <<< "$command_info"
        ((total_count++))
        
        if execute_aws_cli_command "$description" "$command" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "📊 데이터 분석 및 요약 생성 시작..."
    
    # 분석 보고서 생성 배열
    declare -a analysis_reports=(
        "CloudFormation 스택 요약|iac_cloudformation_stacks.json|.Stacks[]? | \"스택명: \\(.StackName), 상태: \\(.StackStatus), 생성일: \\(.CreationTime)\"|iac_analysis_cloudformation_summary.txt"
        "CDK 스택 분석|iac_cloudformation_stacks.json|.Stacks[]? | select(.Tags[]?.Key == \"aws:cdk:path\") | \"CDK 스택: \\(.StackName), 상태: \\(.StackStatus)\"|iac_analysis_cdk_summary.txt"
        "비용 분석 요약|iac_cost_analysis.json|.ResultsByTime[]?.Groups[]? | \"서비스: \\(.Keys[0]), 비용: \\(.Metrics.BlendedCost.Amount) \\(.Metrics.BlendedCost.Unit)\"|iac_analysis_cost_summary.txt"
        "Lambda 함수 요약|iac_lambda_functions.json|.Functions[]? | \"함수명: \\(.FunctionName), 런타임: \\(.Runtime), 상태: \\(.State)\"|iac_analysis_lambda_summary.txt"
        "Config 규칙 요약|iac_config_rules.json|.ConfigRules[]? | \"규칙명: \\(.ConfigRuleName), 상태: \\(.ConfigRuleState), 소스: \\(.Source.Owner)\"|iac_analysis_config_rules.txt"
        "CloudTrail 요약|iac_cloudtrail_trails.json|.trailList[]? | \"추적명: \\(.Name), 다중리전: \\(.IsMultiRegionTrail), 로깅: \\(.IsLogging)\"|iac_analysis_cloudtrail_summary.txt"
        "태그 분석|iac_tagged_resources.json|.ResourceTagMappingList[]? | \"리소스: \\(.ResourceARN), 태그수: \\(.Tags | length)\"|iac_analysis_tags_summary.txt"
        "조직 분석|iac_organization_info.json|\"조직 ID: \\(.Organization.Id // \"N/A\"), 마스터 계정: \\(.Organization.MasterAccountId // \"N/A\")\"|iac_analysis_organization_summary.txt"
    )
    
    # 분석 보고서 생성
    for report_info in "${analysis_reports[@]}"; do
        IFS='|' read -r description input_file jq_filter output_file <<< "$report_info"
        ((total_count++))
        
        if generate_analysis_report "$description" "$input_file" "$jq_filter" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 종합 분석 보고서 생성
    log_info "📋 종합 분석 보고서 생성 중..."
    ((total_count++))
    
    cat > iac_comprehensive_analysis_report.md << 'EOF'
# AWS Infrastructure as Code 종합 분석 보고서

## 📊 개요
이 보고서는 AWS CLI 및 IaC 도구를 통해 수집된 데이터를 기반으로 생성되었습니다.

## 🏗️ CloudFormation 분석
### 스택 현황
EOF
    
    if [ -f "iac_analysis_cloudformation_summary.txt" ]; then
        echo "```" >> iac_comprehensive_analysis_report.md
        cat iac_analysis_cloudformation_summary.txt >> iac_comprehensive_analysis_report.md
        echo "```" >> iac_comprehensive_analysis_report.md
    fi
    
    cat >> iac_comprehensive_analysis_report.md << 'EOF'

## 💰 비용 분석
### 서비스별 비용 (지난 30일)
EOF
    
    if [ -f "iac_analysis_cost_summary.txt" ]; then
        echo "```" >> iac_comprehensive_analysis_report.md
        cat iac_analysis_cost_summary.txt >> iac_comprehensive_analysis_report.md
        echo "```" >> iac_comprehensive_analysis_report.md
    fi
    
    cat >> iac_comprehensive_analysis_report.md << 'EOF'

## 🔧 Lambda 함수 분석
### 함수 현황
EOF
    
    if [ -f "iac_analysis_lambda_summary.txt" ]; then
        echo "```" >> iac_comprehensive_analysis_report.md
        cat iac_analysis_lambda_summary.txt >> iac_comprehensive_analysis_report.md
        echo "```" >> iac_comprehensive_analysis_report.md
    fi
    
    cat >> iac_comprehensive_analysis_report.md << 'EOF'

## 📋 Config 규칙 분석
### 규정 준수 현황
EOF
    
    if [ -f "iac_analysis_config_rules.txt" ]; then
        echo "```" >> iac_comprehensive_analysis_report.md
        cat iac_analysis_config_rules.txt >> iac_comprehensive_analysis_report.md
        echo "```" >> iac_comprehensive_analysis_report.md
    fi
    
    echo "" >> iac_comprehensive_analysis_report.md
    echo "---" >> iac_comprehensive_analysis_report.md
    echo "**생성 일시:** $(date)" >> iac_comprehensive_analysis_report.md
    echo "**분석 리전:** $REGION" >> iac_comprehensive_analysis_report.md
    
    if [ -f "iac_comprehensive_analysis_report.md" ]; then
        local file_size=$(stat -f%z "iac_comprehensive_analysis_report.md" 2>/dev/null || stat -c%s "iac_comprehensive_analysis_report.md" 2>/dev/null)
        log_success "종합 분석 보고서 생성 완료 (iac_comprehensive_analysis_report.md, ${file_size} bytes)"
        ((success_count++))
    else
        log_error "종합 분석 보고서 생성 실패"
    fi
    
    # 결과 요약
    log_success "AWS CLI 및 IaC 분석 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in iac_*.json iac_*.txt iac_*.md; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            if [ "$size" -gt 100 ]; then
                echo -e "${GREEN}✓ $file (${size} bytes)${NC}"
            else
                echo -e "${YELLOW}⚠ $file (${size} bytes) - 데이터 없음${NC}"
            fi
        fi
    done
    
    # 수집 통계
    echo -e "\n${BLUE}📊 수집 통계:${NC}"
    echo "총 쿼리 수: $total_count"
    echo "성공한 쿼리: $success_count"
    echo "실패한 쿼리: $((total_count - success_count))"
    
    # 오류 로그 확인
    if [ -s "$ERROR_LOG" ]; then
        log_warning "오류가 발생했습니다. $ERROR_LOG 파일을 확인하세요."
        echo -e "\n${YELLOW}최근 오류 (마지막 5줄):${NC}"
        tail -5 "$ERROR_LOG"
    fi
    
    # 다음 단계 안내
    echo -e "\n${YELLOW}💡 다음 단계:${NC}"
    echo "1. 수집된 IaC 데이터를 바탕으로 인프라 거버넌스 분석 진행"
    echo "2. CloudFormation 스택 최적화 및 표준화 검토"
    echo "3. AWS Config 규칙 및 규정 준수 상태 분석"
    echo "4. 비용 최적화 및 리소스 태깅 전략 수립"
    echo "5. 조직 수준 정책 및 거버넌스 강화 방안 검토"
    
    log_info "🎉 AWS CLI 및 IaC 분석 데이터 수집이 완료되었습니다!"
    log_info "📋 종합 보고서: iac_comprehensive_analysis_report.md"
}

# 스크립트 실행
main "$@"
