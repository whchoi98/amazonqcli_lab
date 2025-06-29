#!/bin/bash
# AWS 애플리케이션 서비스 상세 분석 리포트 생성 스크립트 (Shell 버전)
# 컴퓨팅 리포트 스타일에 맞춘 상세 테이블 형식

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report}"
OUTPUT_FILE="$REPORT_DIR/08-application-analysis.md"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# JSON 파일에서 데이터 개수 추출
count_json_items() {
    local file="$1"
    if [ -f "$file" ]; then
        # jq를 사용하여 rows 배열의 길이 계산
        local count=$(jq -r '.rows | length' "$file" 2>/dev/null || echo "0")
        echo "$count"
    else
        echo "0"
    fi
}

# 파일 존재 여부 확인
check_file_exists() {
    local file="$1"
    [ -f "$REPORT_DIR/$file" ] && echo "1" || echo "0"
}

# 리포트 헤더 생성
generate_header() {
    cat << EOF
# 🚀 애플리케이션 서비스 종합 분석

> **분석 일시**: $(date +"%Y-%m-%d %H:%M:%S")  
> **분석 대상**: AWS 계정 내 모든 애플리케이션 서비스  
> **분석 리전**: $REGION (서울)

이 보고서는 AWS 계정의 애플리케이션 서비스에 대한 종합적인 분석을 제공하며, Lambda 함수, API Gateway, ECS/EKS 서비스, 애플리케이션 로드 밸런서 등의 구성 상태와 성능 최적화 방안을 평가합니다.
**분석 대상:** AWS 계정의 애플리케이션 서비스

EOF
}

# 서비스 개요 생성
generate_service_overview() {
    local total_services=0
    local service_summary=""
    
    # 서비스 개수 계산
    for file in application_*.json; do
        if [ -f "$REPORT_DIR/$file" ]; then
            ((total_services++))
        fi
    done
    
    # 주요 서비스별 개수
    local api_keys_count=$(count_json_items "$REPORT_DIR/application_api_gateway_api_keys.json")
    local rules_count=$(count_json_items "$REPORT_DIR/application_eventbridge_rules.json")
    local codebuild_count=$(count_json_items "$REPORT_DIR/application_codebuild_projects.json")
    local deployment_configs_count=$(count_json_items "$REPORT_DIR/application_codedeploy_deployment_configs.json")
    local cloudfront_count=$(count_json_items "$REPORT_DIR/application_cloudfront_distributions.json")
    
    cat << EOF
## 📊 애플리케이션 서비스 개요

**분석된 서비스 카테고리:** ${total_services}개
EOF

    # 서비스별 요약 추가
    if [ "$api_keys_count" -gt 0 ]; then
        echo "- **API Gateway:** ${api_keys_count}개 API 키"
    fi
    if [ "$rules_count" -gt 0 ]; then
        echo "- **EventBridge:** ${rules_count}개 이벤트 규칙"
    fi
    if [ "$codebuild_count" -gt 0 ]; then
        echo "- **CodeBuild:** ${codebuild_count}개 프로젝트"
    fi
    if [ "$deployment_configs_count" -gt 0 ]; then
        echo "- **CodeDeploy:** ${deployment_configs_count}개 배포 구성"
    fi
    if [ "$cloudfront_count" -gt 0 ]; then
        echo "- **CloudFront:** ${cloudfront_count}개 배포"
    fi
    
    echo ""
}

# API Gateway 분석
analyze_api_gateway() {
    local api_keys_count=$(count_json_items "$REPORT_DIR/application_api_gateway_api_keys.json")
    local domain_names_count=$(count_json_items "$REPORT_DIR/application_api_gateway_domain_names.json")
    local methods_count=$(count_json_items "$REPORT_DIR/application_api_gateway_methods.json")
    local usage_plans_count=$(count_json_items "$REPORT_DIR/application_api_gateway_usage_plans.json")
    
    cat << EOF
## 🌐 API Gateway 현황

### API Gateway 개요
**총 API 키:** ${api_keys_count}개
**총 도메인 이름:** ${domain_names_count}개
**총 메서드:** ${methods_count}개
**총 사용 계획:** ${usage_plans_count}개

EOF

    # API 키 상세 목록
    if [ -f "$REPORT_DIR/application_api_gateway_api_keys.json" ] && [ "$api_keys_count" -gt 0 ]; then
        echo "### API 키 상세 목록"
        echo "| API 키 ID | 이름 | 상태 | 생성일 | 설명 |"
        echo "|-----------|------|------|--------|------|"
        jq -r '.rows[] | "| \(.id // "N/A") | \(.name // "N/A") | \(if .enabled then "활성" else "비활성" end) | \(.created_date // "N/A") | \(.description // "N/A") |"' "$REPORT_DIR/application_api_gateway_api_keys.json" | head -10
    else
        echo "### API 키"
        echo "API 키 데이터를 찾을 수 없습니다."
    fi
    
    echo ""
    
    # 도메인 이름 상세 목록
    if [ -f "$REPORT_DIR/application_api_gateway_domain_names.json" ] && [ "$domain_names_count" -gt 0 ]; then
        echo "### 커스텀 도메인 상세 목록"
        echo "| 도메인 이름 | 인증서 ARN | 리전별 도메인 | 상태 | 보안 정책 |"
        echo "|-------------|-------------|---------------|------|----------|"
        jq -r '.rows[] | "| \(.domain_name // "N/A") | \(.certificate_arn // "N/A") | \(.regional_domain_name // "N/A") | \(.domain_name_status // "N/A") | \(.security_policy // "N/A") |"' "$REPORT_DIR/application_api_gateway_domain_names.json" | head -10
    else
        echo "### 커스텀 도메인"
        echo "커스텀 도메인 데이터를 찾을 수 없습니다."
    fi
    
    echo ""
}

# EventBridge 분석
analyze_eventbridge() {
    local buses_count=$(count_json_items "$REPORT_DIR/application_eventbridge_buses.json")
    local rules_count=$(count_json_items "$REPORT_DIR/application_eventbridge_rules.json")
    
    cat << EOF
## ⚡ EventBridge 현황

### EventBridge 개요
**총 이벤트 버스:** ${buses_count}개
**총 이벤트 규칙:** ${rules_count}개
EOF

    # 활성/비활성 규칙 계산
    if [ -f "$REPORT_DIR/application_eventbridge_rules.json" ] && [ "$rules_count" -gt 0 ]; then
        local active_rules=$(jq '[.rows[] | select(.state == "ENABLED")] | length' "$REPORT_DIR/application_eventbridge_rules.json")
        local inactive_rules=$((rules_count - active_rules))
        echo "**활성 규칙:** ${active_rules}개"
        echo "**비활성 규칙:** ${inactive_rules}개"
    fi
    
    echo ""
    
    # 이벤트 규칙 상세 목록
    if [ -f "$REPORT_DIR/application_eventbridge_rules.json" ] && [ "$rules_count" -gt 0 ]; then
        echo "### 이벤트 규칙 상세 목록"
        echo "| 규칙 이름 | 상태 | 스케줄 | 이벤트 패턴 | 대상 수 | 설명 |"
        echo "|-----------|------|--------|-------------|---------|------|"
        jq -r '.rows[] | "| \(.name // "N/A") | \(.state // "N/A") | \(.schedule_expression // "N/A") | \(if .event_pattern then "있음" else "없음" end) | \(.targets | length) | \(.description // "N/A") |"' "$REPORT_DIR/application_eventbridge_rules.json" | head -10
    else
        echo "### 이벤트 규칙"
        echo "이벤트 규칙 데이터를 찾을 수 없습니다."
    fi
    
    echo ""
}

# CI/CD 분석
analyze_cicd() {
    local codebuild_count=$(count_json_items "$REPORT_DIR/application_codebuild_projects.json")
    local deployment_configs_count=$(count_json_items "$REPORT_DIR/application_codedeploy_deployment_configs.json")
    
    cat << EOF
## 🚀 CI/CD 파이프라인 현황

### CI/CD 개요
**총 CodeBuild 프로젝트:** ${codebuild_count}개
**총 배포 구성:** ${deployment_configs_count}개

EOF

    # CodeDeploy 배포 구성 상세 목록
    if [ -f "$REPORT_DIR/application_codedeploy_deployment_configs.json" ] && [ "$deployment_configs_count" -gt 0 ]; then
        echo "### CodeDeploy 배포 구성 상세 목록"
        echo "| 구성 이름 | 컴퓨트 플랫폼 | 최소 정상 호스트 | 트래픽 라우팅 | 생성일 |"
        echo "|-----------|----------------|------------------|---------------|--------|"
        jq -r '.rows[] | "| \(.deployment_config_name // "N/A") | \(.compute_platform // "N/A") | \(.minimum_healthy_hosts // "N/A") | \(if .traffic_routing_config then "있음" else "없음" end) | \(.create_time // "N/A") |"' "$REPORT_DIR/application_codedeploy_deployment_configs.json" | head -15
        
        echo ""
        echo "#### 컴퓨트 플랫폼별 분포"
        echo "| 플랫폼 | 개수 | 비율 |"
        echo "|--------|------|------|"
        jq -r '.rows | group_by(.compute_platform) | .[] | "\(.[0].compute_platform // "Unknown") | \(length) | \((length * 100 / ('$deployment_configs_count')) | floor)%"' "$REPORT_DIR/application_codedeploy_deployment_configs.json"
    else
        echo "### CodeDeploy 배포 구성"
        echo "배포 구성 데이터를 찾을 수 없습니다."
    fi
    
    echo ""
}

# 콘텐츠 전송 분석
analyze_content_delivery() {
    local cloudfront_count=$(count_json_items "$REPORT_DIR/application_cloudfront_distributions.json")
    local oai_count=$(count_json_items "$REPORT_DIR/application_cloudfront_oai.json")
    local appsync_count=$(count_json_items "$REPORT_DIR/application_appsync_apis.json")
    
    cat << EOF
## 🌍 콘텐츠 전송 및 배포 현황

### 콘텐츠 전송 개요
**총 CloudFront 배포:** ${cloudfront_count}개
**총 Origin Access Identity:** ${oai_count}개
**총 AppSync API:** ${appsync_count}개

EOF

    # CloudFront 배포 상세 목록
    if [ -f "$REPORT_DIR/application_cloudfront_distributions.json" ] && [ "$cloudfront_count" -gt 0 ]; then
        echo "### CloudFront 배포 상세 목록"
        echo "| 배포 ID | 상태 | 도메인 이름 | 가격 클래스 | HTTP 버전 | IPv6 지원 |"
        echo "|---------|------|-------------|-------------|-----------|----------|"
        jq -r '.rows[] | "| \(.id // "N/A") | \(.status // "N/A") | \(.domain_name // "N/A") | \(.price_class // "N/A") | \(.http_version // "N/A") | \(if .is_ipv6_enabled then "지원" else "미지원" end) |"' "$REPORT_DIR/application_cloudfront_distributions.json"
    else
        echo "### CloudFront 배포"
        echo "CloudFront 배포 데이터를 찾을 수 없습니다."
    fi
    
    echo ""
}

# 종합 권장사항 생성
generate_recommendations() {
    cat << EOF
## 🎯 종합 권장사항

1. **API Gateway 보안 강화**: API 키 및 인증 메커니즘 구현으로 무단 접근 방지
2. **EventBridge 활용 확대**: 이벤트 기반 아키텍처로 서비스 간 느슨한 결합 구현
3. **CI/CD 파이프라인 최적화**: 자동화된 빌드 및 배포 프로세스 구축
4. **Systems Manager 자동화**: 운영 작업 자동화 및 패치 관리 체계화
5. **콘텐츠 전송 최적화**: CloudFront를 통한 글로벌 성능 향상
6. **모니터링 및 로깅**: 애플리케이션 성능 및 보안 모니터링 강화
7. **비용 최적화**: 리소스 사용량 모니터링 및 최적화
8. **보안 강화**: WAF, SSL/TLS 인증서 등 보안 기능 활용
9. **재해 복구**: 백업 및 복구 전략 수립
10. **거버넌스**: 태그 정책 및 리소스 관리 체계 구축

---
*리포트 생성 완료: $(date '+%Y-%m-%d %H:%M:%S')*

EOF
}

# 메인 함수
main() {
    log_info "🚀 AWS 애플리케이션 서비스 상세 분석 리포트 생성 시작"
    
    # 디렉토리 확인
    if [ ! -d "$REPORT_DIR" ]; then
        log_error "리포트 디렉토리가 존재하지 않습니다: $REPORT_DIR"
        exit 1
    fi
    
    cd "$REPORT_DIR"
    
    # 필수 파일 확인
    local required_files=0
    local existing_files=0
    
    for file in application_*.json; do
        if [ -f "$file" ]; then
            ((existing_files++))
        fi
        ((required_files++))
    done
    
    if [ "$existing_files" -eq 0 ]; then
        log_error "애플리케이션 데이터 파일이 없습니다. 먼저 steampipe_application_collection.py를 실행하세요."
        exit 1
    fi
    
    log_info "📊 $existing_files개 데이터 파일 발견"
    
    # 리포트 생성
    log_info "📝 마크다운 리포트 생성 중..."
    
    {
        generate_header
        generate_service_overview
        analyze_api_gateway
        analyze_eventbridge
        analyze_cicd
        analyze_content_delivery
        generate_recommendations
    } > "$OUTPUT_FILE"
    
    # 결과 요약
    log_success "📄 리포트 생성 완료: $OUTPUT_FILE"
    log_info "📋 분석 결과 요약:"
    log_info "   - 분석된 서비스: $existing_files개"
    log_info "   - 리포트 파일: $OUTPUT_FILE"
    
    log_success "🎉 애플리케이션 분석 리포트 생성이 완료되었습니다!"
    log_info "💡 생성된 마크다운 파일을 확인하여 상세 분석 결과를 검토하세요."
}

# 스크립트 실행
main "$@"
