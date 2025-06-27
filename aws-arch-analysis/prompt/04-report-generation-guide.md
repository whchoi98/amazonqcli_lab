# AWS 계정 분석 - 보고서 생성 가이드

## 📋 보고서 생성 상세 가이드

### 보고서 생성 스크립트 매핑

#### 1. 📊 전체 계정 분석 요약 (`01-executive-summary.md`)
**생성 스크립트**: `generate-executive-summary.py`
**목적**: C-Level 임원진을 위한 고수준 요약
**내용**:
- 계정 개요 및 주요 지표
- 비용 현황 및 트렌드 (월간/분기별)
- 주요 발견사항 (Top 5)
- 즉시 조치 필요 항목
- ROI 기반 우선순위 권장사항

**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-executive-summary.py
```

#### 2. 🌐 네트워킹 분석 (`02-networking-analysis.md`)
**생성 스크립트**: `generate-networking-report.py`
**목적**: 네트워크 아키텍처 및 보안 분석
**내용**:
**VPC 관련 리소스:**
□ VPC (aws_vpc) - 모든 VPC의 CIDR, 상태, 태그 분석
□ 서브넷 (aws_vpc_subnet) - 퍼블릭/프라이빗 분류, AZ 분산, CIDR 할당
□ 라우팅 테이블 (aws_vpc_route_table) - 라우팅 규칙, 연결된 서브넷
□ 라우팅 (aws_vpc_route) - 개별 라우팅 규칙 상세 분석
□ 인터넷 게이트웨이 (aws_vpc_internet_gateway) - 연결 상태, 사용 현황
□ NAT 게이트웨이 (aws_vpc_nat_gateway) - 위치, 타입, 비용 효율성
□ VPC 엔드포인트 (aws_vpc_endpoint) - 서비스별 엔드포인트 활용도
□ VPC 피어링 (aws_vpc_peering_connection) - 연결 상태, 라우팅 설정

**보안 관련:**
□ 보안 그룹 (aws_vpc_security_group) - 규칙 분석, 최소 권한 준수
□ 보안 그룹 규칙 (aws_vpc_security_group_rule) - 개별 규칙 상세 검토
□ 네트워크 ACL (aws_vpc_network_acl) - 서브넷 레벨 보안 설정
□ VPC Flow Logs (aws_vpc_flow_log) - 로깅 설정, 분석 활용도

**고급 네트워킹:**
□ Transit Gateway (aws_ec2_transit_gateway) - 연결 허브 구성
□ Transit Gateway 라우팅 테이블 (aws_ec2_transit_gateway_route_table)
□ Transit Gateway VPC 연결 (aws_ec2_transit_gateway_vpc_attachment)
□ VPN 연결 (aws_vpc_vpn_connection) - 온프레미스 연결
□ VPN 게이트웨이 (aws_vpc_vpn_gateway) - VPN 종단점
□ 고객 게이트웨이 (aws_vpc_customer_gateway) - 온프레미스 측 설정
□ Direct Connect (aws_directconnect_*) - 전용선 연결 현황
□ Elastic IP (aws_vpc_eip) - 고정 IP 할당 및 사용 현황


**실행 방법**
```
./generate-networking-report.py
```

#### 3. 💻 컴퓨팅 분석 (`03-compute-analysis.md`)
**생성 스크립트**: `generate-compute-report.py` (Python 버전)
**목적**: 컴퓨팅 리소스 효율성 및 최적화
**내용**:
다음 모든 컴퓨팅 리소스를 상세 분석해주세요:

**EC2 관련:**
□ EC2 인스턴스 (aws_ec2_instance) - 타입, 상태, 사용률, 비용 분석
□ AMI (aws_ec2_ami) - 사용 중인 이미지, 보안 패치 상태
□ 키 페어 (aws_ec2_key_pair) - SSH 키 관리 현황
□ 인스턴스 타입 (aws_ec2_instance_type) - 사용 가능한 타입 분석
□ 스팟 가격 (aws_ec2_spot_price) - 스팟 인스턴스 활용 기회
□ 예약 인스턴스 (aws_ec2_reserved_instance) - RI 활용 현황
□ 배치 그룹 (aws_ec2_placement_group) - 성능 최적화 설정

**Auto Scaling:**
□ Auto Scaling 그룹 (aws_ec2_autoscaling_group) - 스케일링 정책
□ 시작 구성 (aws_ec2_launch_configuration) - 인스턴스 템플릿
□ 시작 템플릿 (aws_ec2_launch_template) - 최신 템플릿 활용
□ 시작 템플릿 버전 (aws_ec2_launch_template_version) - 버전 관리

**로드 밸런싱:**
□ Application Load Balancer (aws_ec2_application_load_balancer)
□ Network Load Balancer (aws_ec2_network_load_balancer)
□ Classic Load Balancer (aws_ec2_classic_load_balancer)
□ 타겟 그룹 (aws_ec2_target_group) - 헬스 체크, 라우팅 규칙
□ 리스너 (aws_ec2_load_balancer_listener) - 포트, 프로토콜 설정
□ 리스너 규칙 (aws_ec2_load_balancer_listener_rule) - 라우팅 로직

**서버리스 컴퓨팅:**
□ Lambda 함수 (aws_lambda_function) - 런타임, 메모리, 성능
□ Lambda 레이어 (aws_lambda_layer) - 공통 라이브러리 관리
□ Lambda 별칭 (aws_lambda_alias) - 버전 관리
□ Lambda 버전 (aws_lambda_version) - 배포 이력
□ 이벤트 소스 매핑 (aws_lambda_event_source_mapping) - 트리거 설정

**컨테이너 서비스:**
□ ECS 클러스터 (aws_ecs_cluster) - 컨테이너 오케스트레이션
□ ECS 서비스 (aws_ecs_service) - 서비스 정의, 스케일링
□ ECS 태스크 (aws_ecs_task) - 실행 중인 태스크
□ ECS 태스크 정의 (aws_ecs_task_definition) - 컨테이너 스펙
□ ECS 컨테이너 인스턴스 (aws_ecs_container_instance) - 호스트 인스턴스
□ EKS 클러스터 (aws_eks_cluster) - Kubernetes 클러스터
□ EKS 노드 그룹 (aws_eks_node_group) - 워커 노드 관리
□ EKS 애드온 (aws_eks_addon) - 클러스터 확장 기능
□ EKS Fargate 프로필 (aws_eks_fargate_profile) - 서버리스 컨테이너

**기타 컴퓨팅:**
□ Elastic Beanstalk 애플리케이션 (aws_elastic_beanstalk_application)
□ Elastic Beanstalk 환경 (aws_elastic_beanstalk_environment)
□ Batch 작업 큐 (aws_batch_queue) - 배치 처리
□ Lightsail 인스턴스 (aws_lightsail_instance) - 간소화된 VPS


**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-compute-report.py
# 또는 기존 bapy 버전
./generate-compute-report.py
```

#### 4. 💾 스토리지 분석 (`04-storage-analysis.md`)
**생성 스크립트**: `generate-storage-report.py`
**목적**: 스토리지 전략 및 데이터 관리 최적화
**내용**:
다음 모든 스토리지 리소스를 상세 분석해주세요:

**블록 스토리지:**
□ EBS 볼륨 (aws_ebs_volume) - 타입, 크기, 성능, 암호화 상태
□ EBS 스냅샷 (aws_ebs_snapshot) - 백업 정책, 보존 기간
□ EBS 볼륨 메트릭 (aws_ebs_volume_metric_*) - 성능 분석

**객체 스토리지:**
□ S3 버킷 (aws_s3_bucket) - 설정, 보안, 비용 최적화
□ S3 객체 (aws_s3_object) - 스토리지 클래스, 크기 분석
□ S3 액세스 포인트 (aws_s3_access_point) - 액세스 제어
□ S3 멀티 리전 액세스 포인트 (aws_s3_multi_region_access_point)
□ S3 멀티파트 업로드 (aws_s3_multipart_upload) - 미완료 업로드
□ S3 인텔리전트 티어링 (aws_s3_bucket_intelligent_tiering_configuration)

**파일 시스템:**
□ EFS 파일 시스템 (aws_efs_file_system) - 성능 모드, 처리량
□ EFS 액세스 포인트 (aws_efs_access_point) - 액세스 제어
□ EFS 마운트 타겟 (aws_efs_mount_target) - 네트워크 연결
□ FSx 파일 시스템 (aws_fsx_file_system) - 고성능 파일 시스템

**아카이브 스토리지:**
□ Glacier 볼트 (aws_glacier_vault) - 장기 보관 스토리지

**스토리지 게이트웨이:**
□ Storage Gateway (aws_storagegateway_*) - 하이브리드 스토리지

**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-storage-report.py
```

#### 5. 🗄️ 데이터베이스 분석 (`05-database-analysis.md`)
**생성 스크립트**: `generate-database-report.py`
**목적**: 데이터베이스 성능 및 가용성 분석
**내용**:
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

**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-database-report.py
```

#### 6. 🔒 보안 분석 (`06-security-analysis.md`)
**생성 스크립트**: `generate-security-report.py`
**목적**: 보안 태세 및 컴플라이언스 평가
**내용**:
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
**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-security-report.py
```

#### 7. 💰 비용 최적화 (`07-cost-optimization.md`)
**생성 스크립트**: `generate-cost-report.py` (Python 버전)
**목적**: 비용 효율성 및 최적화 기회 식별
**내용**:
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

**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-cost-report.py
```

#### 8. 🌐 애플리케이션 서비스 분석 (`08-application-analysis.md`)
**생성 스크립트**: `generate-application-report.py` (Python 버전)
**목적**: 애플리케이션 아키텍처 및 운영 효율성
**내용**:

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

**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-application-report.py
```

#### 9. 📈 모니터링 분석 (`09-monitoring-analysis.md`)
**생성 스크립트**: `generate-monitoring-report.py`
**목적**: 모니터링 및 운영 효율성 분석
**내용**:
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

**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-monitoring-report.py
```

#### 10. 🛠️ 종합 권장사항 (`10-comprehensive-recommendations.md`)
**생성 스크립트**: `generate-recommendations.py`
**목적**: 통합적 관점의 전략적 권장사항
**내용**:

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


#### 6.2 📋 실행 계획 수립

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

**실행 방법**:
```
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-recommendations.py
```

### 보고서 일괄 생성
```
# 모든 보고서를 한 번에 생성
cd ~/amazonqcli_lab/aws-arch-analysis/script
./generate-all-reports.py
# 생성된 보고서 확인
ls -la ~/amazonqcli_lab/report/*.md
```

### 보고서 생성 순서 (의존성 고려)
1. **데이터 수집 완료 확인** (모든 JSON 파일 존재)
2. **개별 분석 보고서 생성** (02-09번)
3. **경영진 요약 보고서 생성** (01번) - 다른 보고서 참조
4. **종합 권장사항 생성** (10번) - 모든 분석 결과 통합

### 보고서 품질 검증
```
# Markdown 문법 검증
markdownlint ~/amazonqcli_lab/report/*.md

# 보고서 완성도 확인
for file in ~/amazonqcli_lab/report/*.md; do
    echo "=== $file ==="
    wc -l "$file"
    grep -c "^#" "$file"
    echo ""
done
```

### 보고서 작성 품질 기준

#### 📝 내용 품질
- **정확성**: 수집된 데이터 기반 정확한 분석
- **완전성**: 모든 주요 영역 포괄적 검토
- **실용성**: 실행 가능한 구체적 권장사항
- **우선순위**: 비즈니스 영향도 기반 우선순위 제시

#### 📊 시각화 요구사항
- 표와 차트를 활용한 데이터 시각화
- 비교 분석 및 트렌드 표시
- 색상 코딩을 통한 우선순위 표시
- 아키텍처 다이어그램 포함 (필요시)

#### 🎯 권장사항 형식
```markdown
### 🔴 높은 우선순위 (즉시 실행)
1. **권장사항 제목**: 구체적 설명
   - **예상 효과**: 정량적 지표
   - **구현 난이도**: 쉬움/보통/어려움
   - **예상 기간**: X주/X개월
   - **필요 리소스**: 인력/예산

### 🟡 중간 우선순위 (1-3개월)
### 🟢 낮은 우선순위 (3-6개월)
```
