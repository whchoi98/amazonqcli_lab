#!/usr/bin/env python3
"""
AWS 애플리케이션 서비스 상세 분석 리포트 생성 스크립트
수집된 데이터를 기반으로 포괄적인 애플리케이션 아키텍처 분석 리포트 생성
컴퓨팅 리포트 스타일에 맞춘 상세 테이블 형식
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

class ApplicationReportGenerator:
    def __init__(self, report_dir: str = None):
        # 스크립트의 실제 위치를 기준으로 경로 설정
        if report_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent
            report_dir = str(project_root / "aws-arch-analysis" / "report")
        self.report_dir = Path(report_dir)
        self.output_file = self.report_dir / "08-application-analysis.md"
        
        # 색상 코드
        self.GREEN = '\033[0;32m'
        self.BLUE = '\033[0;34m'
        self.YELLOW = '\033[1;33m'
        self.RED = '\033[0;31m'
        self.NC = '\033[0m'
        
        # 수집된 데이터 저장
        self.collected_data = {}
        
    def log_info(self, message: str):
        print(f"{self.BLUE}[INFO]{self.NC} {message}")
        
    def log_success(self, message: str):
        print(f"{self.GREEN}[SUCCESS]{self.NC} {message}")
        
    def log_warning(self, message: str):
        print(f"{self.YELLOW}[WARNING]{self.NC} {message}")
        
    def log_error(self, message: str):
        print(f"{self.RED}[ERROR]{self.NC} {message}")

    def load_json_file(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """JSON 파일을 로드합니다."""
        file_path = self.report_dir / filename
        try:
            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'rows' in data:
                        return data['rows']
                    elif isinstance(data, list):
                        return data
                    return []
        except (json.JSONDecodeError, IOError) as e:
            self.log_warning(f"파일 로드 실패: {filename} - {str(e)}")
        return None

    def collect_all_data(self):
        """모든 애플리케이션 데이터 수집"""
        self.log_info("📊 애플리케이션 서비스 데이터 로드 중...")
        
        # 성공적으로 수집된 파일들
        data_files = {
            'api_gateway_api_keys': 'application_api_gateway_api_keys.json',
            'api_gateway_domain_names': 'application_api_gateway_domain_names.json',
            'api_gateway_methods': 'application_api_gateway_methods.json',
            'api_gateway_usage_plans': 'application_api_gateway_usage_plans.json',
            'appsync_apis': 'application_appsync_apis.json',
            'cloudfront_distributions': 'application_cloudfront_distributions.json',
            'cloudfront_oai': 'application_cloudfront_oai.json',
            'codebuild_projects': 'application_codebuild_projects.json',
            'codedeploy_deployment_configs': 'application_codedeploy_deployment_configs.json',
            'eventbridge_buses': 'application_eventbridge_buses.json',
            'eventbridge_rules': 'application_eventbridge_rules.json',
            'ssm_documents': 'application_ssm_documents.json',
            'ssm_maintenance_windows': 'application_ssm_maintenance_windows.json',
            'ssm_patch_baselines': 'application_ssm_patch_baselines.json'
        }
        
        loaded_count = 0
        for key, filename in data_files.items():
            data = self.load_json_file(filename)
            if data is not None:
                self.collected_data[key] = data
                loaded_count += 1
                self.log_success(f"✓ {filename} 로드 완료 ({len(data) if isinstance(data, list) else 1}개 항목)")
            else:
                self.log_warning(f"✗ {filename} 로드 실패")
        
        self.log_info(f"📈 총 {loaded_count}/{len(data_files)}개 데이터 파일 로드 완료")
        return loaded_count > 0

    def write_api_gateway_analysis(self, report_file) -> None:
        """API Gateway 분석 섹션을 작성합니다."""
        report_file.write("## 🌐 API Gateway 현황\n\n")
        
        # API 키 분석
        api_keys = self.collected_data.get('api_gateway_api_keys', [])
        domain_names = self.collected_data.get('api_gateway_domain_names', [])
        methods = self.collected_data.get('api_gateway_methods', [])
        usage_plans = self.collected_data.get('api_gateway_usage_plans', [])
        
        report_file.write("### API Gateway 개요\n")
        report_file.write(f"**총 API 키:** {len(api_keys)}개\n")
        report_file.write(f"**총 도메인 이름:** {len(domain_names)}개\n")
        report_file.write(f"**총 메서드:** {len(methods)}개\n")
        report_file.write(f"**총 사용 계획:** {len(usage_plans)}개\n\n")
        
        # API 키 상세 목록
        if api_keys:
            report_file.write("### API 키 상세 목록\n")
            report_file.write("| API 키 ID | 이름 | 상태 | 생성일 | 설명 |\n")
            report_file.write("|-----------|------|------|--------|------|\n")
            
            for key in api_keys[:10]:  # 최대 10개만 표시
                key_id = key.get('id', 'N/A')
                name = key.get('name', 'N/A')
                enabled = '활성' if key.get('enabled', False) else '비활성'
                created_date = key.get('created_date', 'N/A')
                description = key.get('description', 'N/A')[:50] + '...' if len(key.get('description', '')) > 50 else key.get('description', 'N/A')
                
                report_file.write(f"| {key_id} | {name} | {enabled} | {created_date} | {description} |\n")
        else:
            report_file.write("### API 키\nAPI 키 데이터를 찾을 수 없습니다.\n")
        
        report_file.write("\n")
        
        # 도메인 이름 상세 목록
        if domain_names:
            report_file.write("### 커스텀 도메인 상세 목록\n")
            report_file.write("| 도메인 이름 | 인증서 ARN | 리전별 도메인 | 상태 | 보안 정책 |\n")
            report_file.write("|-------------|-------------|---------------|------|----------|\n")
            
            for domain in domain_names[:10]:
                domain_name = domain.get('domain_name', 'N/A')
                cert_arn = domain.get('certificate_arn', 'N/A')[:50] + '...' if len(domain.get('certificate_arn', '')) > 50 else domain.get('certificate_arn', 'N/A')
                regional_domain = domain.get('regional_domain_name', 'N/A')
                status = domain.get('domain_name_status', 'N/A')
                security_policy = domain.get('security_policy', 'N/A')
                
                report_file.write(f"| {domain_name} | {cert_arn} | {regional_domain} | {status} | {security_policy} |\n")
        else:
            report_file.write("### 커스텀 도메인\n커스텀 도메인 데이터를 찾을 수 없습니다.\n")
        
        report_file.write("\n")

    def write_eventbridge_analysis(self, report_file) -> None:
        """EventBridge 분석 섹션을 작성합니다."""
        report_file.write("## ⚡ EventBridge 현황\n\n")
        
        buses = self.collected_data.get('eventbridge_buses', [])
        rules = self.collected_data.get('eventbridge_rules', [])
        
        report_file.write("### EventBridge 개요\n")
        report_file.write(f"**총 이벤트 버스:** {len(buses)}개\n")
        report_file.write(f"**총 이벤트 규칙:** {len(rules)}개\n")
        
        if rules:
            active_rules = len([rule for rule in rules if rule.get('state') == 'ENABLED'])
            report_file.write(f"**활성 규칙:** {active_rules}개\n")
            report_file.write(f"**비활성 규칙:** {len(rules) - active_rules}개\n")
        
        report_file.write("\n")
        
        # 이벤트 규칙 상세 목록
        if rules:
            report_file.write("### 이벤트 규칙 상세 목록\n")
            report_file.write("| 규칙 이름 | 상태 | 스케줄 | 이벤트 패턴 | 대상 수 | 설명 |\n")
            report_file.write("|-----------|------|--------|-------------|---------|------|\n")
            
            for rule in rules[:10]:  # 최대 10개만 표시
                name = rule.get('name', 'N/A')
                state = rule.get('state', 'N/A')
                schedule_expr = rule.get('schedule_expression') or 'N/A'
                schedule = schedule_expr[:20] + '...' if len(schedule_expr) > 20 else schedule_expr
                has_pattern = '있음' if rule.get('event_pattern') else '없음'
                target_count = len(rule.get('targets', [])) if rule.get('targets') else 0
                desc = rule.get('description') or 'N/A'
                description = desc[:30] + '...' if len(desc) > 30 else desc
                
                report_file.write(f"| {name} | {state} | {schedule} | {has_pattern} | {target_count} | {description} |\n")
        else:
            report_file.write("### 이벤트 규칙\n이벤트 규칙 데이터를 찾을 수 없습니다.\n")
        
        report_file.write("\n")

    def write_cicd_analysis(self, report_file) -> None:
        """CI/CD 파이프라인 분석 섹션을 작성합니다."""
        report_file.write("## 🚀 CI/CD 파이프라인 현황\n\n")
        
        codebuild_projects = self.collected_data.get('codebuild_projects', [])
        deployment_configs = self.collected_data.get('codedeploy_deployment_configs', [])
        
        report_file.write("### CI/CD 개요\n")
        report_file.write(f"**총 CodeBuild 프로젝트:** {len(codebuild_projects)}개\n")
        report_file.write(f"**총 배포 구성:** {len(deployment_configs)}개\n\n")
        
        # CodeDeploy 배포 구성 상세 목록
        if deployment_configs:
            report_file.write("### CodeDeploy 배포 구성 상세 목록\n")
            report_file.write("| 구성 이름 | 컴퓨트 플랫폼 | 최소 정상 호스트 | 트래픽 라우팅 | 생성일 |\n")
            report_file.write("|-----------|----------------|------------------|---------------|--------|\n")
            
            for config in deployment_configs[:15]:  # 최대 15개만 표시
                name = config.get('deployment_config_name', 'N/A')
                platform = config.get('compute_platform', 'N/A')
                min_healthy = str(config.get('minimum_healthy_hosts', {})) if config.get('minimum_healthy_hosts') else 'N/A'
                traffic_routing = '있음' if config.get('traffic_routing_config') else '없음'
                created = config.get('create_time', 'N/A')
                
                report_file.write(f"| {name} | {platform} | {min_healthy} | {traffic_routing} | {created} |\n")
            
            # 컴퓨트 플랫폼별 분포
            platforms = Counter(config.get('compute_platform', 'Unknown') for config in deployment_configs)
            report_file.write("\n#### 컴퓨트 플랫폼별 분포\n")
            report_file.write("| 플랫폼 | 개수 | 비율 |\n")
            report_file.write("|--------|------|------|\n")
            
            total_configs = len(deployment_configs)
            for platform, count in platforms.most_common():
                percentage = round((count / total_configs) * 100, 1)
                report_file.write(f"| {platform} | {count} | {percentage}% |\n")
        else:
            report_file.write("### CodeDeploy 배포 구성\n배포 구성 데이터를 찾을 수 없습니다.\n")
        
        report_file.write("\n")

    def write_content_delivery_analysis(self, report_file) -> None:
        """콘텐츠 전송 및 배포 분석 섹션을 작성합니다."""
        report_file.write("## 🌍 콘텐츠 전송 및 배포 현황\n\n")
        
        cloudfront_distributions = self.collected_data.get('cloudfront_distributions', [])
        cloudfront_oai = self.collected_data.get('cloudfront_oai', [])
        appsync_apis = self.collected_data.get('appsync_apis', [])
        
        report_file.write("### 콘텐츠 전송 개요\n")
        report_file.write(f"**총 CloudFront 배포:** {len(cloudfront_distributions)}개\n")
        report_file.write(f"**총 Origin Access Identity:** {len(cloudfront_oai)}개\n")
        report_file.write(f"**총 AppSync API:** {len(appsync_apis)}개\n\n")
        
        # CloudFront 배포 상세 목록
        if cloudfront_distributions:
            report_file.write("### CloudFront 배포 상세 목록\n")
            report_file.write("| 배포 ID | 상태 | 도메인 이름 | 가격 클래스 | HTTP 버전 | IPv6 지원 |\n")
            report_file.write("|---------|------|-------------|-------------|-----------|----------|\n")
            
            for dist in cloudfront_distributions:
                dist_id = dist.get('id', 'N/A')
                status = dist.get('status', 'N/A')
                domain_name = dist.get('domain_name', 'N/A')[:40] + '...' if len(dist.get('domain_name', '')) > 40 else dist.get('domain_name', 'N/A')
                price_class = dist.get('price_class', 'N/A')
                http_version = dist.get('http_version', 'N/A')
                ipv6_enabled = '지원' if dist.get('is_ipv6_enabled', False) else '미지원'
                
                report_file.write(f"| {dist_id} | {status} | {domain_name} | {price_class} | {http_version} | {ipv6_enabled} |\n")
        else:
            report_file.write("### CloudFront 배포\nCloudFront 배포 데이터를 찾을 수 없습니다.\n")
        
        report_file.write("\n")

    def generate_markdown_report(self):
        """마크다운 리포트 생성"""
        self.log_info("📝 마크다운 리포트 생성 중...")
        
        with open(self.output_file, 'w', encoding='utf-8') as report_file:
            # 헤더
            report_file.write("# 🚀 애플리케이션 서비스 종합 분석\n\n")
            report_file.write(f"> **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            report_file.write(f"> **분석 대상**: AWS 계정 내 모든 애플리케이션 서비스  \n")
            report_file.write(f"> **분석 리전**: ap-northeast-2 (서울)\n\n")
            report_file.write("이 보고서는 AWS 계정의 애플리케이션 인프라에 대한 종합적인 분석을 제공하며, API Gateway, Lambda 함수, CloudFront 배포, ELB 로드 밸런서 등의 구성 상태와 성능 최적화 방안을 평가합니다.\n\n")
            
            # 개요
            total_services = len([k for k in self.collected_data.keys() if self.collected_data[k]])
            report_file.write("## 📊 애플리케이션 서비스 개요\n\n")
            report_file.write(f"**분석된 서비스 카테고리:** {total_services}개\n")
            
            # 각 서비스별 개수 요약
            service_summary = []
            if self.collected_data.get('api_gateway_api_keys'):
                service_summary.append(f"- **API Gateway:** {len(self.collected_data['api_gateway_api_keys'])}개 API 키")
            if self.collected_data.get('eventbridge_rules'):
                service_summary.append(f"- **EventBridge:** {len(self.collected_data['eventbridge_rules'])}개 이벤트 규칙")
            if self.collected_data.get('codebuild_projects'):
                service_summary.append(f"- **CodeBuild:** {len(self.collected_data['codebuild_projects'])}개 프로젝트")
            if self.collected_data.get('codedeploy_deployment_configs'):
                service_summary.append(f"- **CodeDeploy:** {len(self.collected_data['codedeploy_deployment_configs'])}개 배포 구성")
            if self.collected_data.get('cloudfront_distributions'):
                service_summary.append(f"- **CloudFront:** {len(self.collected_data['cloudfront_distributions'])}개 배포")
            
            if service_summary:
                report_file.write('\n'.join(service_summary))
            report_file.write("\n\n")
            
            # 각 분석 섹션 작성
            self.write_api_gateway_analysis(report_file)
            self.write_eventbridge_analysis(report_file)
            self.write_cicd_analysis(report_file)
            self.write_content_delivery_analysis(report_file)
            
            # 권장사항 섹션
            report_file.write("## 🎯 종합 권장사항\n\n")
            recommendations = [
                "1. **API Gateway 보안 강화**: API 키 및 인증 메커니즘 구현으로 무단 접근 방지",
                "2. **EventBridge 활용 확대**: 이벤트 기반 아키텍처로 서비스 간 느슨한 결합 구현",
                "3. **CI/CD 파이프라인 최적화**: 자동화된 빌드 및 배포 프로세스 구축",
                "4. **Systems Manager 자동화**: 운영 작업 자동화 및 패치 관리 체계화",
                "5. **콘텐츠 전송 최적화**: CloudFront를 통한 글로벌 성능 향상",
                "6. **모니터링 및 로깅**: 애플리케이션 성능 및 보안 모니터링 강화",
                "7. **비용 최적화**: 리소스 사용량 모니터링 및 최적화",
                "8. **보안 강화**: WAF, SSL/TLS 인증서 등 보안 기능 활용",
                "9. **재해 복구**: 백업 및 복구 전략 수립",
                "10. **거버넌스**: 태그 정책 및 리소스 관리 체계 구축"
            ]
            
            for rec in recommendations:
                report_file.write(f"{rec}\n")
            
            # 마무리 섹션 추가
            self.write_footer_section(report_file)
        
        self.log_success(f"📄 리포트 생성 완료: {self.output_file}")

    def write_footer_section(self, report_file):
        """보고서 마무리 섹션 추가"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_file.write(f"""
## 📞 추가 지원

이 보고서에 대한 질문이나 추가 분석이 필요한 경우:
- AWS Support 케이스 생성
- AWS Well-Architected Review 수행
- AWS Professional Services 문의

📅 분석 완료 시간: {current_time} 🔄 다음 애플리케이션 검토 권장 주기: 월 1회
""")
        return str(self.output_file)

def main():
    """메인 실행 함수"""
    generator = ApplicationReportGenerator()
    
    generator.log_info("🚀 AWS 애플리케이션 서비스 상세 분석 리포트 생성 시작")
    
    # 데이터 수집
    if not generator.collect_all_data():
        generator.log_error("데이터 로드 실패. 먼저 steampipe_application_collection.py를 실행하세요.")
        sys.exit(1)
    
    # 리포트 생성
    report_file = generator.generate_markdown_report()
    
    # 결과 요약
    generator.log_info("📋 분석 결과 요약:")
    total_services = len([k for k in generator.collected_data.keys() if generator.collected_data[k]])
    generator.log_info(f"   - 분석된 서비스: {total_services}개")
    generator.log_info(f"   - 리포트 파일: {report_file}")
    
    generator.log_success("🎉 애플리케이션 분석 리포트 생성이 완료되었습니다!")
    generator.log_info("💡 생성된 마크다운 파일을 확인하여 상세 분석 결과를 검토하세요.")
    
    # Enhanced 권장사항 통계 출력
    if hasattr(generator, 'get_recommendations_summary'):
        stats = generator.get_recommendations_summary()
        if stats['total'] > 0:
            generator.log_info(f"📋 Enhanced 권장사항 통계:")
            generator.log_info(f"   - 높은 우선순위: {stats['high_priority']}개")
            generator.log_info(f"   - 중간 우선순위: {stats['medium_priority']}개")
            generator.log_info(f"   - 낮은 우선순위: {stats['low_priority']}개")
            generator.log_info(f"   - 총 권장사항: {stats['total']}개")

if __name__ == "__main__":
    main()
