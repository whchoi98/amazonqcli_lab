### Phase 2: 데이터베이스 및 데이터 서비스 분석

#### 2.1 🗄️ 관계형 데이터베이스 (완전 분석)
```
다음 모든 RDS 관련 리소스를 상세 분석해주세요:

**RDS 인스턴스:**
□ RDS DB 인스턴스 (aws_rds_db_instance) - 타입, 엔진, 성능, 비용
□ RDS DB 클러스터 (aws_rds_db_cluster) - Aurora 클러스터 구성
□ RDS 엔진 버전 (aws_rds_db_engine_version) - 지원 버전, 업그레이드 계획
□ RDS 파라미터 그룹 (aws_rds_db_parameter_group) - 설정 최적화
□ RDS 클러스터 파라미터 그룹 (aws_rds_db_cluster_parameter_group)
□ RDS 옵션 그룹 (aws_rds_db_option_group) - 추가 기능 설정
□ RDS 서브넷 그룹 (aws_rds_db_subnet_group) - 네트워크 배치

**백업 및 스냅샷:**
□ RDS DB 스냅샷 (aws_rds_db_snapshot) - 백업 정책, 보존
□ RDS 클러스터 스냅샷 (aws_rds_db_cluster_snapshot) - Aurora 백업
□ RDS 자동 백업 (aws_rds_db_instance_automated_backup) - 자동화 설정

**성능 및 모니터링:**
□ RDS 성능 인사이트 - CPU, 메모리, I/O 분석
□ RDS 메트릭 (aws_rds_db_instance_metric_*) - 연결, CPU, IOPS
□ RDS 이벤트 구독 (aws_rds_db_event_subscription) - 알림 설정
□ RDS 권장사항 (aws_rds_db_recommendation) - 최적화 제안

**고급 기능:**
□ RDS Proxy (aws_rds_db_proxy) - 연결 풀링, 보안
□ RDS 예약 인스턴스 (aws_rds_reserved_db_instance) - 비용 최적화
□ RDS 유지보수 작업 (aws_rds_pending_maintenance_action) - 예정된 작업
```

#### 2.2 🔄 NoSQL 및 캐시 데이터베이스 (완전 분석)
```
다음 모든 NoSQL 및 캐시 리소스를 상세 분석해주세요:

**DynamoDB:**
□ DynamoDB 테이블 (aws_dynamodb_table) - 설계, 성능, 비용
□ DynamoDB 백업 (aws_dynamodb_backup) - 백업 정책
□ DynamoDB 글로벌 테이블 (aws_dynamodb_global_table) - 다중 리전
□ DynamoDB 테이블 내보내기 (aws_dynamodb_table_export) - 데이터 내보내기
□ DynamoDB 메트릭 (aws_dynamodb_metric_*) - 용량, 성능 분석

**ElastiCache:**
□ ElastiCache 클러스터 (aws_elasticache_cluster) - Redis/Memcached
□ ElastiCache 복제 그룹 (aws_elasticache_replication_group) - HA 구성
□ ElastiCache 파라미터 그룹 (aws_elasticache_parameter_group) - 설정
□ ElastiCache 서브넷 그룹 (aws_elasticache_subnet_group) - 네트워크
□ ElastiCache 예약 노드 (aws_elasticache_reserved_cache_node) - 비용 최적화
□ ElastiCache 업데이트 작업 (aws_elasticache_update_action) - 유지보수

**기타 NoSQL:**
□ DocumentDB 클러스터 (aws_docdb_cluster) - MongoDB 호환
□ DocumentDB 인스턴스 (aws_docdb_cluster_instance) - 클러스터 노드
□ DocumentDB 스냅샷 (aws_docdb_cluster_snapshot) - 백업
□ Neptune 클러스터 (aws_neptune_db_cluster) - 그래프 데이터베이스
□ Neptune 스냅샷 (aws_neptune_db_cluster_snapshot) - 그래프 DB 백업
□ Keyspaces 키스페이스 (aws_keyspaces_keyspace) - Cassandra 호환
□ Keyspaces 테이블 (aws_keyspaces_table) - Cassandra 테이블
□ MemoryDB 클러스터 (aws_memorydb_cluster) - Redis 호환 인메모리
```

#### 2.3 📊 분석 및 데이터 웨어하우스 (완전 분석)
```
다음 모든 분석 서비스를 상세 분석해주세요:

**데이터 웨어하우스:**
□ Redshift 클러스터 (aws_redshift_cluster) - 데이터 웨어하우스
□ Redshift 스냅샷 (aws_redshift_snapshot) - 백업 정책
□ Redshift 파라미터 그룹 (aws_redshift_parameter_group) - 설정
□ Redshift 서브넷 그룹 (aws_redshift_subnet_group) - 네트워크
□ Redshift 이벤트 구독 (aws_redshift_event_subscription) - 알림
□ Redshift Serverless 네임스페이스 (aws_redshiftserverless_namespace)
□ Redshift Serverless 워크그룹 (aws_redshiftserverless_workgroup)

**검색 및 분석:**
□ OpenSearch 도메인 (aws_opensearch_domain) - 검색 엔진
□ Elasticsearch 도메인 (aws_elasticsearch_domain) - 레거시 검색

**빅데이터 처리:**
□ EMR 클러스터 (aws_emr_cluster) - 빅데이터 처리
□ EMR 인스턴스 (aws_emr_instance) - 클러스터 노드
□ EMR 인스턴스 그룹 (aws_emr_instance_group) - 노드 그룹
□ EMR 인스턴스 플릿 (aws_emr_instance_fleet) - 플릿 관리
□ EMR 보안 구성 (aws_emr_security_configuration) - 보안 설정
□ EMR 스튜디오 (aws_emr_studio) - 개발 환경
□ EMR 퍼블릭 액세스 차단 (aws_emr_block_public_access_configuration)

**스트리밍 데이터:**
□ Kinesis 스트림 (aws_kinesis_stream) - 실시간 데이터 스트리밍
□ Kinesis Firehose (aws_kinesis_firehose_delivery_stream) - 데이터 전송
□ Kinesis Video 스트림 (aws_kinesis_video_stream) - 비디오 스트리밍
□ Kinesis 소비자 (aws_kinesis_consumer) - 스트림 소비자
□ Kinesis Analytics v2 (aws_kinesisanalyticsv2_application) - 실시간 분석
□ MSK 클러스터 (aws_msk_cluster) - 관리형 Kafka
□ MSK Serverless 클러스터 (aws_msk_serverless_cluster) - 서버리스 Kafka

**데이터 카탈로그 및 ETL:**
□ Glue 데이터베이스 (aws_glue_catalog_database) - 데이터 카탈로그
□ Glue 테이블 (aws_glue_catalog_table) - 메타데이터
□ Glue 작업 (aws_glue_job) - ETL 작업
□ Glue 크롤러 (aws_glue_crawler) - 스키마 발견
□ Glue 연결 (aws_glue_connection) - 데이터 소스 연결
□ Glue 개발 엔드포인트 (aws_glue_dev_endpoint) - 개발 환경
□ Glue 보안 구성 (aws_glue_security_configuration) - 보안 설정
□ Glue 데이터 품질 규칙셋 (aws_glue_data_quality_ruleset) - 품질 관리
□ Glue 암호화 설정 (aws_glue_data_catalog_encryption_settings)

**쿼리 서비스:**
□ Athena 워크그룹 (aws_athena_workgroup) - 쿼리 그룹
□ Athena 쿼리 실행 (aws_athena_query_execution) - 쿼리 이력
```

### Phase 3: 보안 및 자격 증명 서비스 분석

#### 3.1 🔐 자격 증명 및 액세스 관리 (완전 분석)
```
다음 모든 IAM 및 보안 리소스를 상세 분석해주세요:

**IAM 핵심 구성 요소:**
□ IAM 사용자 (aws_iam_user) - 사용자 계정, MFA, 액세스 키
□ IAM 그룹 (aws_iam_group) - 사용자 그룹화
□ IAM 역할 (aws_iam_role) - 서비스 역할, 크로스 계정 액세스
□ IAM 정책 (aws_iam_policy) - 권한 정책 분석
□ IAM 정책 연결 (aws_iam_policy_attachment) - 정책 할당 현황
□ IAM 액세스 키 (aws_iam_access_key) - 프로그래밍 액세스
□ IAM 서버 인증서 (aws_iam_server_certificate) - SSL/TLS 인증서
□ IAM 가상 MFA 디바이스 (aws_iam_virtual_mfa_device) - MFA 설정

**IAM 고급 기능:**
□ IAM 액세스 어드바이저 (aws_iam_access_advisor) - 권한 사용 분석
□ IAM 자격 증명 보고서 (aws_iam_credential_report) - 보안 감사
□ IAM 계정 요약 (aws_iam_account_summary) - 계정 한도 및 사용량
□ IAM 계정 암호 정책 (aws_iam_account_password_policy) - 암호 정책
□ IAM 정책 시뮬레이터 (aws_iam_policy_simulator) - 권한 테스트
□ IAM 액션 (aws_iam_action) - 사용 가능한 액션 목록
□ IAM 서비스별 자격 증명 (aws_iam_service_specific_credential)

**외부 자격 증명 제공자:**
□ IAM OIDC 제공자 (aws_iam_open_id_connect_provider) - OpenID Connect
□ IAM SAML 제공자 (aws_iam_saml_provider) - SAML 연동

**AWS SSO/Identity Center:**
□ SSO 인스턴스 (aws_ssoadmin_instance) - Identity Center 인스턴스
□ SSO 권한 세트 (aws_ssoadmin_permission_set) - 권한 템플릿
□ SSO 계정 할당 (aws_ssoadmin_account_assignment) - 계정 액세스
□ SSO 관리형 정책 연결 (aws_ssoadmin_managed_policy_attachment)

**Identity Store:**
□ Identity Store 사용자 (aws_identitystore_user) - 사용자 관리
□ Identity Store 그룹 (aws_identitystore_group) - 그룹 관리
□ Identity Store 그룹 멤버십 (aws_identitystore_group_membership)
```

#### 3.2 🔒 암호화 및 키 관리 (완전 분석)
```
다음 모든 암호화 관련 리소스를 상세 분석해주세요:

**KMS (Key Management Service):**
□ KMS 키 (aws_kms_key) - 암호화 키 관리
□ KMS 별칭 (aws_kms_alias) - 키 별칭 관리
□ KMS 키 순환 (aws_kms_key_rotation) - 키 순환 정책

**인증서 관리:**
□ ACM 인증서 (aws_acm_certificate) - SSL/TLS 인증서
□ ACM PCA 인증 기관 (aws_acmpca_certificate_authority) - 프라이빗 CA

**시크릿 관리:**
□ Secrets Manager 시크릿 (aws_secretsmanager_secret) - 시크릿 관리

**Parameter Store:**
□ SSM 파라미터 (aws_ssm_parameter) - 구성 매개변수 관리
```

#### 3.3 🛡️ 보안 서비스 (완전 분석)
```
다음 모든 보안 서비스를 상세 분석해주세요:

**웹 애플리케이션 방화벽:**
□ WAF v2 Web ACL (aws_wafv2_web_acl) - 웹 애플리케이션 보호
□ WAF v2 규칙 그룹 (aws_wafv2_rule_group) - 보안 규칙
□ WAF v2 IP 세트 (aws_wafv2_ip_set) - IP 화이트/블랙리스트
□ WAF v2 정규식 패턴 (aws_wafv2_regex_pattern_set) - 패턴 매칭
□ WAF 레이트 기반 규칙 (aws_waf_rate_based_rule) - 속도 제한
□ WAF 규칙 (aws_waf_rule) - 보안 규칙
□ WAF 규칙 그룹 (aws_waf_rule_group) - 규칙 그룹화
□ WAF Web ACL (aws_waf_web_acl) - 웹 ACL
□ WAF Regional 규칙 (aws_wafregional_rule) - 리전별 규칙
□ WAF Regional Web ACL (aws_wafregional_web_acl) - 리전별 Web ACL

**DDoS 보호:**
□ Shield 공격 (aws_shield_attack) - DDoS 공격 정보
□ Shield 공격 통계 (aws_shield_attack_statistic) - 공격 통계
□ Shield DRT 액세스 (aws_shield_drt_access) - 대응팀 액세스
□ Shield 긴급 연락처 (aws_shield_emergency_contact) - 긴급 연락처
□ Shield 보호 (aws_shield_protection) - 리소스 보호
□ Shield 보호 그룹 (aws_shield_protection_group) - 보호 그룹
□ Shield 구독 (aws_shield_subscription) - Shield Advanced 구독

**위협 탐지:**
□ GuardDuty 탐지기 (aws_guardduty_detector) - 위협 탐지
□ GuardDuty 필터 (aws_guardduty_filter) - 탐지 필터
□ GuardDuty 발견사항 (aws_guardduty_finding) - 보안 위협
□ GuardDuty IP 세트 (aws_guardduty_ipset) - IP 목록
□ GuardDuty 멤버 (aws_guardduty_member) - 멤버 계정
□ GuardDuty 게시 대상 (aws_guardduty_publishing_destination) - 결과 게시
□ GuardDuty 위협 인텔 세트 (aws_guardduty_threat_intel_set) - 위협 정보

**보안 허브:**
□ Security Hub 허브 (aws_securityhub_hub) - 보안 허브
□ Security Hub 발견사항 (aws_securityhub_finding) - 보안 발견사항
□ Security Hub 인사이트 (aws_securityhub_insight) - 보안 인사이트
□ Security Hub 멤버 (aws_securityhub_member) - 멤버 계정
□ Security Hub 제품 (aws_securityhub_product) - 보안 제품
□ Security Hub 액션 대상 (aws_securityhub_action_target) - 액션 대상
□ Security Hub 표준 제어 (aws_securityhub_standards_control) - 표준 제어
□ Security Hub 표준 구독 (aws_securityhub_standards_subscription) - 표준 구독
□ Security Hub 제품 구독 (aws_securityhub_enabled_product_subscription)
□ Security Hub 발견사항 집계기 (aws_securityhub_finding_aggregator)

**취약점 관리:**
□ Inspector 2 커버리지 (aws_inspector2_coverage) - 취약점 스캔 범위
□ Inspector 2 발견사항 (aws_inspector2_finding) - 취약점 발견사항
□ Inspector 2 멤버 (aws_inspector2_member) - 멤버 계정
□ Inspector 2 커버리지 통계 (aws_inspector2_coverage_statistics) - 통계
□ Inspector 평가 실행 (aws_inspector_assessment_run) - 평가 실행
□ Inspector 평가 대상 (aws_inspector_assessment_target) - 평가 대상
□ Inspector 평가 템플릿 (aws_inspector_assessment_template) - 평가 템플릿
□ Inspector 제외 (aws_inspector_exclusion) - 제외 항목
□ Inspector 발견사항 (aws_inspector_finding) - 취약점 발견사항

**데이터 보안:**
□ Macie 2 분류 작업 (aws_macie2_classification_job) - 데이터 분류
□ Macie 2 발견사항 (aws_macie2_finding) - 민감 데이터 발견

**네트워크 방화벽:**
□ Network Firewall 방화벽 (aws_networkfirewall_firewall) - 네트워크 방화벽
□ Network Firewall 정책 (aws_networkfirewall_firewall_policy) - 방화벽 정책
□ Network Firewall 규칙 그룹 (aws_networkfirewall_rule_group) - 규칙 그룹
```
