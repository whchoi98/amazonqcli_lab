# 포괄적 AWS 계정 아키텍처 진단 프롬프트

## 🎯 진단 목표
AWS 계정의 **모든 리소스**를 체계적으로 분석하여 완전한 아키텍처 현황을 파악하고, 보안, 성능, 비용, 운영 효율성 관점에서 종합적인 개선 방안을 제시합니다.

## 📋 전체 리소스 분석 체크리스트

### Phase 1: 기본 인프라 리소스 분석

#### 1.1 🌐 네트워킹 리소스 (완전 분석)
```
다음 모든 네트워킹 구성 요소를 빠짐없이 분석해주세요:

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
```

#### 1.2 💻 컴퓨팅 리소스 (완전 분석)
```
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
```

#### 1.3 💾 스토리지 리소스 (완전 분석)
```
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
```
