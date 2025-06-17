### Phase 4: 애플리케이션 서비스 및 통합 분석

#### 4.1 🌐 API 및 애플리케이션 게이트웨이 (완전 분석)
```
다음 모든 API 및 게이트웨이 리소스를 상세 분석해주세요:

**API Gateway:**
□ API Gateway REST API (aws_api_gateway_rest_api) - REST API 설계, 성능
□ API Gateway 리소스 (aws_api_gateway_resource) - API 리소스 구조
□ API Gateway 메서드 (aws_api_gateway_method) - HTTP 메서드 설정
□ API Gateway 통합 (aws_api_gateway_integration) - 백엔드 통합
□ API Gateway 배포 (aws_api_gateway_deployment) - API 배포 관리
□ API Gateway 스테이지 (aws_api_gateway_stage) - 환경별 스테이지
□ API Gateway 사용 계획 (aws_api_gateway_usage_plan) - API 사용량 제한
□ API Gateway API 키 (aws_api_gateway_api_key) - API 키 관리
□ API Gateway 도메인 이름 (aws_api_gateway_domain_name) - 커스텀 도메인
□ API Gateway 기본 경로 매핑 (aws_api_gateway_base_path_mapping) - 경로 매핑
□ API Gateway 권한 부여자 (aws_api_gateway_authorizer) - 인증/인가
□ API Gateway 게이트웨이 응답 (aws_api_gateway_gateway_response) - 오류 응답
□ API Gateway 모델 (aws_api_gateway_model) - 데이터 모델
□ API Gateway 요청 검증기 (aws_api_gateway_request_validator) - 요청 검증
□ API Gateway VPC 링크 (aws_api_gateway_vpc_link) - VPC 연결

**API Gateway v2 (HTTP API):**
□ API Gateway v2 API (aws_apigatewayv2_api) - HTTP/WebSocket API
□ API Gateway v2 권한 부여자 (aws_apigatewayv2_authorizer) - JWT 인증
□ API Gateway v2 배포 (aws_apigatewayv2_deployment) - API 배포
□ API Gateway v2 도메인 이름 (aws_apigatewayv2_domain_name) - 커스텀 도메인
□ API Gateway v2 통합 (aws_apigatewayv2_integration) - 백엔드 통합
□ API Gateway v2 모델 (aws_apigatewayv2_model) - 데이터 모델
□ API Gateway v2 라우트 (aws_apigatewayv2_route) - API 라우팅
□ API Gateway v2 스테이지 (aws_apigatewayv2_stage) - 환경 관리
□ API Gateway v2 VPC 링크 (aws_apigatewayv2_vpc_link) - VPC 연결

**Application Load Balancer (고급 기능):**
□ ALB 리스너 인증서 (aws_lb_listener_certificate) - SSL 인증서
□ ALB 리스너 규칙 (aws_lb_listener_rule) - 고급 라우팅
□ ALB 타겟 그룹 연결 (aws_lb_target_group_attachment) - 타겟 연결
```

#### 4.2 📨 메시징 및 알림 서비스 (완전 분석)
```
다음 모든 메시징 및 알림 리소스를 상세 분석해주세요:

**Simple Notification Service (SNS):**
□ SNS 주제 (aws_sns_topic) - 메시지 주제 관리
□ SNS 구독 (aws_sns_topic_subscription) - 구독자 관리
□ SNS 플랫폼 애플리케이션 (aws_sns_platform_application) - 모바일 푸시
□ SNS 플랫폼 엔드포인트 (aws_sns_platform_endpoint) - 디바이스 엔드포인트
□ SNS SMS 기본 설정 (aws_sns_sms_preferences) - SMS 설정

**Simple Queue Service (SQS):**
□ SQS 큐 (aws_sqs_queue) - 메시지 큐 설계, 성능
□ SQS 큐 정책 (aws_sqs_queue_policy) - 액세스 정책
□ SQS 큐 재드라이브 정책 (aws_sqs_queue_redrive_policy) - DLQ 설정
□ SQS 큐 재드라이브 허용 정책 (aws_sqs_queue_redrive_allow_policy)

**Amazon MQ:**
□ MQ 브로커 (aws_mq_broker) - 메시지 브로커
□ MQ 구성 (aws_mq_configuration) - 브로커 구성

**EventBridge (CloudWatch Events):**
□ EventBridge 버스 (aws_cloudwatch_event_bus) - 이벤트 버스
□ EventBridge 규칙 (aws_cloudwatch_event_rule) - 이벤트 규칙
□ EventBridge 대상 (aws_cloudwatch_event_target) - 이벤트 대상
□ EventBridge 연결 (aws_cloudwatch_event_connection) - 외부 연결
□ EventBridge 대상 (aws_cloudwatch_event_destination) - 이벤트 대상
□ EventBridge 아카이브 (aws_cloudwatch_event_archive) - 이벤트 아카이브
□ EventBridge 재생 (aws_cloudwatch_event_replay) - 이벤트 재생

**Step Functions:**
□ Step Functions 상태 머신 (aws_sfn_state_machine) - 워크플로우 오케스트레이션
□ Step Functions 활동 (aws_sfn_activity) - 활동 정의
```

#### 4.3 🔄 워크플로우 및 자동화 서비스 (완전 분석)
```
다음 모든 워크플로우 및 자동화 리소스를 상세 분석해주세요:

**Systems Manager:**
□ SSM 문서 (aws_ssm_document) - 자동화 문서
□ SSM 연결 (aws_ssm_association) - 문서 연결
□ SSM 유지보수 창 (aws_ssm_maintenance_window) - 유지보수 스케줄
□ SSM 유지보수 창 작업 (aws_ssm_maintenance_window_task) - 유지보수 작업
□ SSM 유지보수 창 대상 (aws_ssm_maintenance_window_target) - 대상 지정
□ SSM 패치 기준선 (aws_ssm_patch_baseline) - 패치 관리
□ SSM 패치 그룹 (aws_ssm_patch_group) - 패치 그룹
□ SSM 리소스 데이터 동기화 (aws_ssm_resource_data_sync) - 데이터 동기화
□ SSM 활성화 (aws_ssm_activation) - 하이브리드 활성화
□ SSM 기본 패치 기준선 (aws_ssm_default_patch_baseline) - 기본 패치
□ SSM 서비스 설정 (aws_ssm_service_setting) - 서비스 설정

**CloudFormation:**
□ CloudFormation 스택 (aws_cloudformation_stack) - 인프라 스택
□ CloudFormation 스택 세트 (aws_cloudformation_stack_set) - 다중 계정 배포
□ CloudFormation 스택 세트 인스턴스 (aws_cloudformation_stack_set_instance)
□ CloudFormation 타입 (aws_cloudformation_type) - 커스텀 리소스 타입

**CodePipeline (CI/CD):**
□ CodePipeline 파이프라인 (aws_codepipeline_pipeline) - CI/CD 파이프라인
□ CodePipeline 웹훅 (aws_codepipeline_webhook) - 트리거 설정

**CodeBuild:**
□ CodeBuild 프로젝트 (aws_codebuild_project) - 빌드 프로젝트
□ CodeBuild 보고서 그룹 (aws_codebuild_report_group) - 테스트 보고서
□ CodeBuild 소스 자격 증명 (aws_codebuild_source_credential) - 소스 인증

**CodeCommit:**
□ CodeCommit 저장소 (aws_codecommit_repository) - Git 저장소
□ CodeCommit 트리거 (aws_codecommit_trigger) - 저장소 트리거

**CodeDeploy:**
□ CodeDeploy 애플리케이션 (aws_codedeploy_application) - 배포 애플리케이션
□ CodeDeploy 배포 구성 (aws_codedeploy_deployment_config) - 배포 설정
□ CodeDeploy 배포 그룹 (aws_codedeploy_deployment_group) - 배포 대상

**OpsWorks:**
□ OpsWorks 스택 (aws_opsworks_stack) - 애플리케이션 스택
□ OpsWorks 레이어 (aws_opsworks_layer) - 애플리케이션 레이어
□ OpsWorks 인스턴스 (aws_opsworks_instance) - 관리형 인스턴스
□ OpsWorks 애플리케이션 (aws_opsworks_application) - 애플리케이션 정의
□ OpsWorks 사용자 프로필 (aws_opsworks_user_profile) - 사용자 관리
□ OpsWorks 권한 (aws_opsworks_permission) - 액세스 권한
□ OpsWorks RDS DB 인스턴스 (aws_opsworks_rds_db_instance) - DB 연결
□ OpsWorks 커스텀 레이어 (aws_opsworks_custom_layer) - 커스텀 레이어
□ OpsWorks Java 앱 레이어 (aws_opsworks_java_app_layer) - Java 레이어
□ OpsWorks HAProxy 레이어 (aws_opsworks_haproxy_layer) - 로드 밸런서
□ OpsWorks MySQL 레이어 (aws_opsworks_mysql_layer) - MySQL 레이어
□ OpsWorks PHP 앱 레이어 (aws_opsworks_php_app_layer) - PHP 레이어
□ OpsWorks Rails 앱 레이어 (aws_opsworks_rails_app_layer) - Rails 레이어
□ OpsWorks 정적 웹 레이어 (aws_opsworks_static_web_layer) - 정적 웹
```

### Phase 5: 모니터링, 로깅 및 관리 서비스 분석

#### 5.1 📊 모니터링 및 관찰성 (완전 분석)
```
다음 모든 모니터링 및 관찰성 리소스를 상세 분석해주세요:

**CloudWatch 메트릭 및 알람:**
□ CloudWatch 메트릭 (aws_cloudwatch_metric_*) - 모든 서비스 메트릭
□ CloudWatch 알람 (aws_cloudwatch_metric_alarm) - 알람 설정, 임계값
□ CloudWatch 복합 알람 (aws_cloudwatch_composite_alarm) - 복합 조건
□ CloudWatch 대시보드 (aws_cloudwatch_dashboard) - 모니터링 대시보드
□ CloudWatch 메트릭 스트림 (aws_cloudwatch_metric_stream) - 실시간 스트리밍

**CloudWatch Logs:**
□ CloudWatch 로그 그룹 (aws_cloudwatch_log_group) - 로그 그룹 관리
□ CloudWatch 로그 스트림 (aws_cloudwatch_log_stream) - 로그 스트림
□ CloudWatch 로그 대상 (aws_cloudwatch_log_destination) - 로그 전송
□ CloudWatch 로그 대상 정책 (aws_cloudwatch_log_destination_policy)
□ CloudWatch 로그 메트릭 필터 (aws_cloudwatch_log_metric_filter) - 메트릭 추출
□ CloudWatch 로그 구독 필터 (aws_cloudwatch_log_subscription_filter) - 실시간 처리
□ CloudWatch 로그 리소스 정책 (aws_cloudwatch_log_resource_policy) - 액세스 정책
□ CloudWatch 로그 보존 정책 (aws_cloudwatch_log_retention_policy) - 보존 기간
□ CloudWatch 로그 쿼리 정의 (aws_cloudwatch_query_definition) - 저장된 쿼리

**X-Ray (분산 추적):**
□ X-Ray 암호화 구성 (aws_xray_encryption_config) - 추적 데이터 암호화
□ X-Ray 샘플링 규칙 (aws_xray_sampling_rule) - 샘플링 정책

**Application Insights:**
□ Application Insights 애플리케이션 (aws_applicationinsights_application) - 애플리케이션 모니터링

**CloudTrail (감사 로깅):**
□ CloudTrail 트레일 (aws_cloudtrail_trail) - API 호출 로깅
□ CloudTrail 이벤트 데이터 스토어 (aws_cloudtrail_event_data_store) - 이벤트 저장소

**Config (구성 관리):**
□ Config 구성 레코더 (aws_config_configuration_recorder) - 리소스 구성 기록
□ Config 전송 채널 (aws_config_delivery_channel) - 구성 전송
□ Config 규칙 (aws_config_config_rule) - 규정 준수 규칙
□ Config 수정 구성 (aws_config_remediation_configuration) - 자동 수정
□ Config 집계기 (aws_config_configuration_aggregator) - 다중 계정 집계
□ Config 권한 부여 집계기 (aws_config_aggregate_authorization) - 집계 권한
□ Config 조직 관리형 규칙 (aws_config_organization_managed_rule) - 조직 규칙
□ Config 조직 커스텀 규칙 (aws_config_organization_custom_rule) - 커스텀 규칙
□ Config 조직 적합성 팩 (aws_config_organization_conformance_pack) - 적합성 팩
□ Config 적합성 팩 (aws_config_conformance_pack) - 규정 준수 팩

**Personal Health Dashboard:**
□ Health 이벤트 (aws_health_event) - AWS 서비스 상태 이벤트
```

#### 5.2 🏷️ 리소스 관리 및 태깅 (완전 분석)
```
다음 모든 리소스 관리 도구를 상세 분석해주세요:

**Resource Groups:**
□ Resource Groups 그룹 (aws_resourcegroups_group) - 리소스 그룹화
□ Resource Groups 리소스 (aws_resourcegroups_resource) - 그룹 리소스

**Resource Explorer:**
□ Resource Explorer 인덱스 (aws_resourceexplorer2_index) - 리소스 인덱싱
□ Resource Explorer 뷰 (aws_resourceexplorer2_view) - 리소스 뷰

**Service Catalog:**
□ Service Catalog 포트폴리오 (aws_servicecatalog_portfolio) - 제품 포트폴리오
□ Service Catalog 제품 (aws_servicecatalog_product) - 승인된 제품
□ Service Catalog 제약 조건 (aws_servicecatalog_constraint) - 제약 조건
□ Service Catalog 주체 포트폴리오 연결 (aws_servicecatalog_principal_portfolio_association)
□ Service Catalog 제품 포트폴리오 연결 (aws_servicecatalog_product_portfolio_association)
□ Service Catalog 프로비저닝된 제품 (aws_servicecatalog_provisioned_product) - 배포된 제품
□ Service Catalog 태그 옵션 (aws_servicecatalog_tag_option) - 태그 옵션
□ Service Catalog 태그 옵션 리소스 연결 (aws_servicecatalog_tag_option_resource_association)

**AWS Organizations:**
□ Organizations 조직 (aws_organizations_organization) - 조직 구조
□ Organizations 계정 (aws_organizations_account) - 멤버 계정
□ Organizations 조직 단위 (aws_organizations_organizational_unit) - OU 구조
□ Organizations 정책 (aws_organizations_policy) - 조직 정책
□ Organizations 정책 연결 (aws_organizations_policy_attachment) - 정책 적용
□ Organizations 위임된 관리자 (aws_organizations_delegated_administrator) - 위임 관리

**Control Tower:**
□ Control Tower 컨트롤 (aws_controltower_control) - 거버넌스 컨트롤
□ Control Tower 랜딩 존 (aws_controltower_landing_zone) - 랜딩 존 설정

**License Manager:**
□ License Manager 라이선스 구성 (aws_licensemanager_license_configuration) - 라이선스 관리
□ License Manager 연결 (aws_licensemanager_association) - 리소스 연결

**Systems Manager (추가 관리 기능):**
□ SSM 인벤토리 (aws_ssm_inventory) - 리소스 인벤토리
□ SSM 규정 준수 항목 (aws_ssm_compliance_item) - 규정 준수 상태
```

#### 5.3 💰 비용 관리 및 청구 (완전 분석)
```
다음 모든 비용 관리 리소스를 상세 분석해주세요:

**Cost and Billing:**
□ 청구 계정 (aws_billing_account) - 청구 계정 정보
□ 청구 서비스 계정 (aws_billing_service_account) - 서비스별 청구

**Cost Explorer:**
□ Cost Explorer 비용 카테고리 (aws_ce_cost_category) - 비용 분류
□ Cost Explorer 이상 탐지기 (aws_ce_anomaly_detector) - 비용 이상 탐지
□ Cost Explorer 이상 구독 (aws_ce_anomaly_subscription) - 이상 알림

**Budgets:**
□ Budgets 예산 (aws_budgets_budget) - 예산 설정
□ Budgets 예산 작업 (aws_budgets_budget_action) - 예산 초과 시 작업

**Cost and Usage Report:**
□ CUR 보고서 정의 (aws_cur_report_definition) - 상세 사용량 보고서

**Savings Plans:**
□ Savings Plans (aws_savingsplans_plan) - 절약 플랜
```

### Phase 6: 종합 분석 및 권장사항

#### 6.1 🔍 아키텍처 종합 평가
```
위의 모든 리소스 분석을 바탕으로 다음 관점에서 종합 평가를 수행해주세요:

**아키텍처 성숙도 평가:**
□ Well-Architected Framework 5개 기둥별 점수 (1-5점)
  - 운영 우수성 (Operational Excellence)
  - 보안 (Security)
  - 안정성 (Reliability)
  - 성능 효율성 (Performance Efficiency)
  - 비용 최적화 (Cost Optimization)

**리소스 활용도 분석:**
□ 미사용 리소스 식별 및 정리 방안
□ 과도하게 프로비저닝된 리소스 최적화
□ 리소스 간 의존성 및 연결 상태 분석

**보안 태세 평가:**
□ 보안 그룹 및 네트워크 ACL 최적화
□ IAM 권한 최소화 원칙 준수 여부
□ 암호화 적용 현황 및 개선 방안
□ 로깅 및 모니터링 완성도

**비용 최적화 기회:**
□ 예약 인스턴스 및 Savings Plans 활용 기회
□ 스토리지 클래스 최적화
□ 자동 스케일링 및 스케줄링 개선
□ 불필요한 데이터 전송 비용 절감

**운영 효율성 개선:**
□ 자동화 기회 식별
□ 모니터링 및 알람 체계 개선
□ 백업 및 재해 복구 전략 강화
□ 태깅 전략 및 리소스 관리 개선
```

#### 6.2 📋 실행 계획 수립
```
분석 결과를 바탕으로 우선순위별 실행 계획을 제시해주세요:

**즉시 실행 (High Priority):**
□ 보안 위험 요소 즉시 해결
□ 비용 절감 효과가 큰 항목 우선 적용
□ 운영 중단 위험이 있는 항목 해결

**단기 실행 (Medium Priority - 1-3개월):**
□ 성능 최적화 및 모니터링 강화
□ 자동화 도입 및 운영 효율성 개선
□ 백업 및 재해 복구 체계 구축

**장기 실행 (Low Priority - 3-12개월):**
□ 아키텍처 현대화 및 마이그레이션
□ 고급 서비스 도입 및 혁신
□ 조직 차원의 클라우드 거버넌스 강화

**각 항목별 상세 정보:**
□ 예상 소요 시간 및 리소스
□ 예상 비용 절감 효과
□ 위험도 및 영향도 평가
□ 필요한 기술 역량 및 교육
```
