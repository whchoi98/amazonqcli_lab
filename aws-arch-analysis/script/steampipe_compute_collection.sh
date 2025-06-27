#!/bin/bash
# Steampipe 기반 컴퓨팅 및 서버리스 리소스 데이터 수집 스크립트 (강화 버전)

# 설정 변수
REGION="${AWS_REGION:-ap-northeast-2}"
REPORT_DIR="${REPORT_DIR:-/home/ec2-user/amazonqcli_lab/report}"
LOG_FILE="steampipe_compute_collection.log"
ERROR_LOG="steampipe_compute_errors.log"

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

# Steampipe 쿼리 실행 함수
execute_steampipe_query() {
    local description="$1"
    local query="$2"
    local output_file="$3"
    
    log_info "수집 중: $description"
    
    if steampipe query "$query" --output json > "$output_file" 2>>"$ERROR_LOG"; then
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

# 메인 실행부
main() {
    log_info "🚀 Steampipe 기반 컴퓨팅 및 서버리스 리소스 데이터 수집 시작"
    log_info "Region: $REGION"
    log_info "Report Directory: $REPORT_DIR"
    
    # 보고서 디렉토리 생성 및 이동
    mkdir -p "$REPORT_DIR"
    cd "$REPORT_DIR" || exit 1
    
    # 로그 파일 초기화
    > "$LOG_FILE"
    > "$ERROR_LOG"
    
    # Steampipe 설치 확인
    if ! command -v steampipe &> /dev/null; then
        log_error "Steampipe가 설치되지 않았습니다."
        echo -e "${YELLOW}💡 Steampipe 설치 방법:${NC}"
        echo "sudo /bin/sh -c \"\$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)\""
        echo "steampipe plugin install aws"
        exit 1
    fi
    
    # AWS 플러그인 확인
    log_info "Steampipe AWS 플러그인 확인 중..."
    if ! steampipe plugin list | grep -q "aws"; then
        log_warning "AWS 플러그인이 설치되지 않았습니다. 설치 중..."
        steampipe plugin install aws
    fi
    
    # 수집 카운터
    local success_count=0
    local total_count=0
    
    log_info "💻 컴퓨팅 리소스 수집 시작..."
    
    # 컴퓨팅 리소스 수집 배열
    declare -a compute_queries=(
        "EC2 인스턴스 상세 정보|select instance_id, instance_type, instance_state, vpc_id, subnet_id, private_ip_address, public_ip_address, private_dns_name, public_dns_name, key_name, security_groups, iam_instance_profile_arn, monitoring_state, placement_availability_zone, platform, architecture, virtualization_type, hypervisor, root_device_type, root_device_name, block_device_mappings, ebs_optimized, ena_support, sriov_net_support, source_dest_check, launch_time, state_transition_reason, usage_operation, usage_operation_update_time, tags from aws_ec2_instance where region = '$REGION'|compute_ec2_instances.json"
        "EC2 AMI 이미지|select image_id, name, description, state, public, owner_id, architecture, platform, virtualization_type, hypervisor, root_device_type, root_device_name, block_device_mappings, creation_date, deprecation_time, usage_operation, platform_details, image_type, image_location, kernel_id, ramdisk_id, sriov_net_support, ena_support, boot_mode, tags from aws_ec2_ami where region = '$REGION' and owner_id = (select account_id from aws_caller_identity)|compute_ec2_amis.json"
        "EC2 키 페어|select key_name, key_fingerprint, key_type, key_pair_id, create_time, tags from aws_ec2_key_pair where region = '$REGION'|compute_ec2_key_pairs.json"
        "EC2 예약 인스턴스|select reserved_instance_id, instance_type, availability_zone, instance_count, product_description, instance_state, start_time, end_time, duration, usage_price, fixed_price, currency_code, instance_tenancy, offering_class, offering_type, scope, tags from aws_ec2_reserved_instance where region = '$REGION'|compute_ec2_reserved_instances.json"
        "EC2 스팟 인스턴스 요청|select spot_instance_request_id, spot_price, type, state, status, fault, valid_from, valid_until, launch_group, availability_zone_group, launch_specification, instance_id, create_time, product_description, block_duration_minutes, actual_block_hourly_price, tags from aws_ec2_spot_instance_request where region = '$REGION'|compute_ec2_spot_requests.json"
        "EC2 배치 그룹|select group_name, group_id, strategy, partition_count, state, tags from aws_ec2_placement_group where region = '$REGION'|compute_ec2_placement_groups.json"
        "EC2 시작 템플릿|select launch_template_id, launch_template_name, create_time, created_by, default_version_number, latest_version_number, tags from aws_ec2_launch_template where region = '$REGION'|compute_ec2_launch_templates.json"
        "EC2 시작 템플릿 버전|select launch_template_id, launch_template_name, version_number, version_description, create_time, created_by, default_version, launch_template_data from aws_ec2_launch_template_version where region = '$REGION'|compute_ec2_launch_template_versions.json"
        "Application Load Balancer 상세 정보|select arn, name, type, scheme, vpc_id, availability_zones, security_groups, ip_address_type, state_code, state_reason, dns_name, canonical_hosted_zone_id, created_time, load_balancer_attributes, tags from aws_ec2_application_load_balancer where region = '$REGION'|compute_alb_detailed.json"
        "Network Load Balancer 상세 정보|select arn, name, type, scheme, vpc_id, availability_zones, ip_address_type, state_code, state_reason, dns_name, canonical_hosted_zone_id, created_time, load_balancer_attributes, tags from aws_ec2_network_load_balancer where region = '$REGION'|compute_nlb_detailed.json"
        "Classic Load Balancer|select name, dns_name, canonical_hosted_zone_name, canonical_hosted_zone_name_id, vpc_id, subnets, security_groups, instances, availability_zones, backend_server_descriptions, connection_draining, cross_zone_load_balancing, access_log, connection_settings, created_time, scheme, source_security_group, tags from aws_ec2_classic_load_balancer where region = '$REGION'|compute_clb.json"
        "타겟 그룹|select target_group_arn, target_group_name, protocol, port, vpc_id, health_check_enabled, health_check_interval_seconds, health_check_path, health_check_port, health_check_protocol, health_check_timeout_seconds, healthy_threshold_count, unhealthy_threshold_count, load_balancer_arns, target_type, protocol_version, ip_address_type, tags from aws_ec2_target_group where region = '$REGION'|compute_target_groups.json"
        "Auto Scaling 그룹 상세 정보|select name, autoscaling_group_arn, min_size, max_size, desired_capacity, default_cooldown, availability_zones, load_balancer_names, target_group_arns, health_check_type, health_check_grace_period, placement_group, vpc_zone_identifier, termination_policies, new_instances_protected_from_scale_in, service_linked_role_arn, max_instance_lifetime, capacity_rebalance, warm_pool_configuration, warm_pool_size, status, suspended_processes, enabled_metrics, tags from aws_ec2_autoscaling_group where region = '$REGION'|compute_asg_detailed.json"
        "Auto Scaling 시작 구성|select launch_configuration_name, launch_configuration_arn, image_id, instance_type, key_name, security_groups, classic_link_vpc_id, classic_link_vpc_security_groups, user_data, instance_monitoring, spot_price, iam_instance_profile, created_time, ebs_optimized, associate_public_ip_address, placement_tenancy, block_device_mappings, metadata_options from aws_ec2_autoscaling_launch_configuration where region = '$REGION'|compute_asg_launch_configs.json"
        "Auto Scaling 정책|select policy_name, policy_arn, auto_scaling_group_name, policy_type, adjustment_type, min_adjustment_step, min_adjustment_magnitude, scaling_adjustment, cooldown, step_adjustments, metric_aggregation_type, estimated_instance_warmup, target_tracking_configuration, enabled, alarms from aws_ec2_autoscaling_policy where region = '$REGION'|compute_asg_policies.json"
        "Elastic Beanstalk 애플리케이션|select name, description, date_created, date_updated, versions, configuration_templates, resource_lifecycle_config from aws_elastic_beanstalk_application where region = '$REGION'|compute_beanstalk_applications.json"
        "Elastic Beanstalk 환경|select environment_name, environment_id, application_name, version_label, solution_stack_name, platform_arn, template_name, description, endpoint_url, cname, date_created, date_updated, status, abortable_operation_in_progress, health, health_status, resources, tier, environment_links, environment_arn, operations_role from aws_elastic_beanstalk_environment where region = '$REGION'|compute_beanstalk_environments.json"
    )
    
    # 컴퓨팅 리소스 쿼리 실행
    for query_info in "${compute_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    log_info "🚀 서버리스 컴퓨팅 수집 시작..."
    
    # 서버리스 리소스 수집 배열
    declare -a serverless_queries=(
        "Lambda 함수 상세 정보|select name, arn, runtime, role, handler, code_size, description, timeout, memory_size, last_modified, code_sha_256, version, vpc_id, environment_variables, dead_letter_config_target_arn, kms_key_arn, tracing_config, master_arn, revision_id, layers, state, state_reason, state_reason_code, last_update_status, last_update_status_reason, last_update_status_reason_code, file_system_configs, package_type, architectures, ephemeral_storage, snap_start, logging_config, tags from aws_lambda_function where region = '$REGION'|compute_lambda_functions.json"
        "Lambda 레이어|select layer_name, layer_arn, version, description, created_date, compatible_runtimes, license_info, compatible_architectures from aws_lambda_layer_version where region = '$REGION'|compute_lambda_layers.json"
        "Lambda 별칭|select name, alias_arn, function_name, function_version, description, revision_id from aws_lambda_alias where region = '$REGION'|compute_lambda_aliases.json"
        "Lambda 이벤트 소스 매핑|select uuid, arn, function_arn, function_name, last_modified, last_processing_result, state, state_transition_reason, batch_size, maximum_batching_window_in_seconds, parallelization_factor, starting_position, starting_position_timestamp, maximum_record_age_in_seconds, bisect_batch_on_function_error, maximum_retry_attempts, tumbling_window_in_seconds, topics, queues, source_access_configurations, self_managed_event_source, function_response_types, amazon_managed_kafka_event_source_config, self_managed_kafka_event_source_config, scaling_config from aws_lambda_event_source_mapping where region = '$REGION'|compute_lambda_event_mappings.json"
    )
    
    # 서버리스 리소스 쿼리 실행
    for query_info in "${serverless_queries[@]}"; do
        IFS='|' read -r description query output_file <<< "$query_info"
        ((total_count++))
        if execute_steampipe_query "$description" "$query" "$output_file"; then
            ((success_count++))
        fi
    done
    
    # 결과 요약
    log_success "컴퓨팅 및 서버리스 리소스 데이터 수집 완료!"
    log_info "성공: $success_count/$total_count"
    
    # 파일 목록 및 크기 표시
    echo -e "\n${BLUE}📁 생성된 파일 목록:${NC}"
    for file in compute_*.json; do
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
    echo "1. 수집된 컴퓨팅 데이터를 바탕으로 Phase 1 인프라 분석 진행"
    echo "2. EC2 인스턴스 최적화 및 비용 분석"
    echo "3. Auto Scaling 및 Load Balancer 구성 검토"
    echo "4. Lambda 함수 성능 및 비용 최적화 분석"
    
    log_info "🎉 컴퓨팅 및 서버리스 리소스 데이터 수집이 완료되었습니다!"
}

# 도움말 함수
show_help() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -r, --region REGION    AWS 리전 설정 (기본값: ap-northeast-2)"
    echo "  -d, --dir DIRECTORY    보고서 디렉토리 설정 (기본값: ~/report)"
    echo "  -h, --help            이 도움말 표시"
    echo ""
    echo "환경 변수:"
    echo "  AWS_REGION            AWS 리전 설정"
    echo "  REPORT_DIR            보고서 디렉토리 설정"
    echo ""
    echo "예시:"
    echo "  $0                                    # 기본 설정으로 실행"
    echo "  $0 -r us-east-1                      # 특정 리전으로 실행"
    echo "  $0 -d /custom/path                   # 사용자 정의 디렉토리로 실행"
    echo "  AWS_REGION=eu-west-1 $0              # 환경 변수로 리전 설정"
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
            show_help
            exit 0
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 스크립트 실행
main "$@"
