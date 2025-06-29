#!/usr/bin/env python3
"""
모니터링 분석 보고서 생성 스크립트 (Python 버전)
수집된 모든 모니터링 데이터를 포함하여 종합적인 분석 보고서를 생성합니다.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class MonitoringReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 수집된 모든 모니터링 데이터 파일 목록
        self.monitoring_files = {
            'cloudwatch_alarms': 'monitoring_cloudwatch_alarms.json',
            'cloudwatch_event_rules': 'monitoring_cloudwatch_event_rules.json',
            'cloudwatch_log_groups': 'monitoring_cloudwatch_log_groups.json',
            'cloudwatch_log_subscription_filters': 'monitoring_cloudwatch_log_subscription_filters.json',
            'cloudwatch_metrics': 'monitoring_cloudwatch_metrics.json',
            'cloudtrail_channels': 'monitoring_cloudtrail_channels.json',
            'cloudtrail_event_data_stores': 'monitoring_cloudtrail_event_data_stores.json',
            'config_configuration_recorders': 'monitoring_config_configuration_recorders.json',
            'config_delivery_channels': 'monitoring_config_delivery_channels.json',
            'config_aggregate_authorizations': 'monitoring_config_aggregate_authorizations.json',
            'config_retention_configurations': 'monitoring_config_retention_configurations.json',
            'service_catalog_portfolios': 'monitoring_service_catalog_portfolios.json'
        }

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
            print(f"Warning: Failed to load {filename}: {e}")
        return None

    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """파일 정보를 반환합니다."""
        file_path = self.report_dir / filename
        if file_path.exists():
            stat = file_path.stat()
            return {
                'exists': True,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
        return {'exists': False}

    def write_data_collection_summary(self, report_file) -> None:
        """데이터 수집 요약 섹션을 작성합니다."""
        report_file.write("## 📋 데이터 수집 요약\n\n")
        
        total_files = 0
        total_size = 0
        successful_collections = 0
        
        report_file.write("| 서비스 | 파일명 | 상태 | 크기 | 수정일시 |\n")
        report_file.write("|--------|--------|------|------|----------|\n")
        
        for service_name, filename in self.monitoring_files.items():
            file_info = self.get_file_info(filename)
            total_files += 1
            
            if file_info['exists']:
                successful_collections += 1
                total_size += file_info['size']
                status = "✅ 성공"
                size_str = f"{file_info['size_mb']} MB" if file_info['size_mb'] >= 0.01 else f"{file_info['size']} bytes"
                modified = file_info['modified']
            else:
                status = "❌ 실패"
                size_str = "-"
                modified = "-"
            
            display_name = service_name.replace('_', ' ').title()
            report_file.write(f"| {display_name} | {filename} | {status} | {size_str} | {modified} |\n")
        
        report_file.write(f"\n**수집 통계:**\n")
        report_file.write(f"- **총 파일 수:** {total_files}개\n")
        report_file.write(f"- **성공한 수집:** {successful_collections}개 ({successful_collections/total_files*100:.1f}%)\n")
        report_file.write(f"- **총 데이터 크기:** {total_size/1024/1024:.2f} MB\n\n")

    def write_cloudwatch_analysis(self, report_file) -> None:
        """CloudWatch 분석 섹션을 작성합니다."""
        report_file.write("## 📊 CloudWatch 모니터링 현황\n\n")
        
        # 로그 그룹 분석
        log_groups = self.load_json_file(self.monitoring_files['cloudwatch_log_groups'])
        report_file.write("### CloudWatch 로그 그룹\n")
        if not log_groups:
            report_file.write("CloudWatch 로그 그룹 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_log_groups = len(log_groups)
            with_retention = len([lg for lg in log_groups if lg.get('retention_in_days')])
            encrypted_groups = len([lg for lg in log_groups if lg.get('kms_key_id')])
            
            report_file.write(f"**총 로그 그룹:** {total_log_groups}개\n")
            report_file.write(f"- **보존 기간 설정:** {with_retention}개\n")
            report_file.write(f"- **암호화된 그룹:** {encrypted_groups}개\n\n")
            
            if log_groups:
                report_file.write("**로그 그룹 상세:**\n")
                report_file.write("| 이름 | 보존기간 | 저장용량 | 메트릭필터 | 암호화 |\n")
                report_file.write("|------|----------|----------|------------|--------|\n")
                for lg in log_groups[:10]:  # 상위 10개만 표시
                    name = lg.get('name', 'N/A')
                    retention = f"{lg.get('retention_in_days', 'N/A')}일" if lg.get('retention_in_days') else "무제한"
                    stored_bytes = f"{lg.get('stored_bytes', 0)/1024/1024:.1f} MB" if lg.get('stored_bytes') else "0 MB"
                    metric_filters = lg.get('metric_filter_count', 0)
                    encrypted = "✅" if lg.get('kms_key_id') else "❌"
                    report_file.write(f"| {name} | {retention} | {stored_bytes} | {metric_filters} | {encrypted} |\n")
                if len(log_groups) > 10:
                    report_file.write(f"| ... | ... | ... | ... | ... |\n")
                    report_file.write(f"*({len(log_groups) - 10}개 추가 로그 그룹 생략)*\n")
                report_file.write("\n")
        
        # 알람 분석
        alarms = self.load_json_file(self.monitoring_files['cloudwatch_alarms'])
        report_file.write("### CloudWatch 알람\n")
        if not alarms:
            report_file.write("CloudWatch 알람 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_alarms = len(alarms)
            ok_alarms = len([a for a in alarms if a.get('state_value') == 'OK'])
            alarm_alarms = len([a for a in alarms if a.get('state_value') == 'ALARM'])
            insufficient_data = len([a for a in alarms if a.get('state_value') == 'INSUFFICIENT_DATA'])
            
            report_file.write(f"**총 CloudWatch 알람:** {total_alarms}개\n")
            report_file.write(f"- **정상 상태 (OK):** {ok_alarms}개\n")
            report_file.write(f"- **알람 상태 (ALARM):** {alarm_alarms}개\n")
            report_file.write(f"- **데이터 부족:** {insufficient_data}개\n\n")
            
            if alarms:
                report_file.write("**알람 상세:**\n")
                report_file.write("| 이름 | 상태 | 메트릭 | 설명 |\n")
                report_file.write("|------|------|--------|------|\n")
                for alarm in alarms[:10]:  # 상위 10개만 표시
                    name = alarm.get('name', 'N/A')
                    state = alarm.get('state_value', 'N/A')
                    metric = alarm.get('metric_name', 'N/A')
                    description = alarm.get('alarm_description', 'N/A')[:50] + "..." if len(alarm.get('alarm_description', '')) > 50 else alarm.get('alarm_description', 'N/A')
                    report_file.write(f"| {name} | {state} | {metric} | {description} |\n")
                if len(alarms) > 10:
                    report_file.write(f"*({len(alarms) - 10}개 추가 알람 생략)*\n")
                report_file.write("\n")
        
        # 이벤트 규칙 분석
        event_rules = self.load_json_file(self.monitoring_files['cloudwatch_event_rules'])
        report_file.write("### CloudWatch 이벤트 규칙\n")
        if not event_rules:
            report_file.write("CloudWatch 이벤트 규칙 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_rules = len(event_rules)
            enabled_rules = len([r for r in event_rules if r.get('state') == 'ENABLED'])
            
            report_file.write(f"**총 이벤트 규칙:** {total_rules}개\n")
            report_file.write(f"- **활성화된 규칙:** {enabled_rules}개\n\n")
        
        # 로그 구독 필터 분석
        subscription_filters = self.load_json_file(self.monitoring_files['cloudwatch_log_subscription_filters'])
        report_file.write("### CloudWatch 로그 구독 필터\n")
        if not subscription_filters:
            report_file.write("CloudWatch 로그 구독 필터 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_filters = len(subscription_filters)
            report_file.write(f"**총 로그 구독 필터:** {total_filters}개\n\n")
        
        # 메트릭 분석 (큰 파일이므로 요약만)
        metrics_info = self.get_file_info(self.monitoring_files['cloudwatch_metrics'])
        report_file.write("### CloudWatch 메트릭\n")
        if metrics_info['exists']:
            report_file.write(f"**메트릭 데이터 파일 크기:** {metrics_info['size_mb']} MB\n")
            report_file.write("*메트릭 데이터가 수집되었습니다. 상세 분석은 별도 도구를 사용하세요.*\n\n")
        else:
            report_file.write("CloudWatch 메트릭 데이터를 찾을 수 없습니다.\n\n")

    def write_cloudtrail_analysis(self, report_file) -> None:
        """CloudTrail 분석 섹션을 작성합니다."""
        report_file.write("## 🔍 CloudTrail 감사 현황\n\n")
        
        # CloudTrail 채널 분석
        channels = self.load_json_file(self.monitoring_files['cloudtrail_channels'])
        report_file.write("### CloudTrail 채널\n")
        if not channels:
            report_file.write("CloudTrail 채널 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_channels = len(channels)
            report_file.write(f"**총 CloudTrail 채널:** {total_channels}개\n\n")
        
        # CloudTrail 이벤트 데이터 스토어 분석
        event_data_stores = self.load_json_file(self.monitoring_files['cloudtrail_event_data_stores'])
        report_file.write("### CloudTrail 이벤트 데이터 스토어\n")
        if not event_data_stores:
            report_file.write("CloudTrail 이벤트 데이터 스토어 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_stores = len(event_data_stores)
            report_file.write(f"**총 이벤트 데이터 스토어:** {total_stores}개\n\n")
            
            if event_data_stores:
                report_file.write("**이벤트 데이터 스토어 상세:**\n")
                report_file.write("| 이름 | 상태 | 다중 리전 | 조직 활성화 |\n")
                report_file.write("|------|------|-----------|-------------|\n")
                for store in event_data_stores:
                    name = store.get('name', 'N/A')
                    status = store.get('status', 'N/A')
                    multi_region = "✅" if store.get('multi_region_enabled') else "❌"
                    organization = "✅" if store.get('organization_enabled') else "❌"
                    report_file.write(f"| {name} | {status} | {multi_region} | {organization} |\n")
                report_file.write("\n")

    def write_config_analysis(self, report_file) -> None:
        """AWS Config 분석 섹션을 작성합니다."""
        report_file.write("## ⚙️ AWS Config 구성 현황\n\n")
        
        # Configuration Recorders 분석
        recorders = self.load_json_file(self.monitoring_files['config_configuration_recorders'])
        report_file.write("### Config 구성 레코더\n")
        if not recorders:
            report_file.write("Config 구성 레코더 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_recorders = len(recorders)
            report_file.write(f"**총 구성 레코더:** {total_recorders}개\n\n")
        
        # Delivery Channels 분석
        delivery_channels = self.load_json_file(self.monitoring_files['config_delivery_channels'])
        report_file.write("### Config 전송 채널\n")
        if not delivery_channels:
            report_file.write("Config 전송 채널 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_channels = len(delivery_channels)
            report_file.write(f"**총 전송 채널:** {total_channels}개\n\n")
        
        # Aggregate Authorizations 분석
        aggregate_auth = self.load_json_file(self.monitoring_files['config_aggregate_authorizations'])
        report_file.write("### Config 집계 권한\n")
        if not aggregate_auth:
            report_file.write("Config 집계 권한 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_auth = len(aggregate_auth)
            report_file.write(f"**총 집계 권한:** {total_auth}개\n\n")
        
        # Retention Configurations 분석
        retention_configs = self.load_json_file(self.monitoring_files['config_retention_configurations'])
        report_file.write("### Config 보존 구성\n")
        if not retention_configs:
            report_file.write("Config 보존 구성 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_configs = len(retention_configs)
            report_file.write(f"**총 보존 구성:** {total_configs}개\n\n")

    def write_service_catalog_analysis(self, report_file) -> None:
        """Service Catalog 분석 섹션을 작성합니다."""
        report_file.write("## 📦 Service Catalog 현황\n\n")
        
        portfolios = self.load_json_file(self.monitoring_files['service_catalog_portfolios'])
        report_file.write("### Service Catalog 포트폴리오\n")
        if not portfolios:
            report_file.write("Service Catalog 포트폴리오 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_portfolios = len(portfolios)
            report_file.write(f"**총 포트폴리오:** {total_portfolios}개\n\n")
            
            if portfolios:
                report_file.write("**포트폴리오 상세:**\n")
                report_file.write("| 이름 | ID | 설명 |\n")
                report_file.write("|------|----|----- |\n")
                for portfolio in portfolios:
                    name = portfolio.get('display_name', 'N/A')
                    portfolio_id = portfolio.get('id', 'N/A')
                    description = portfolio.get('description', 'N/A')[:50] + "..." if len(portfolio.get('description', '')) > 50 else portfolio.get('description', 'N/A')
                    report_file.write(f"| {name} | {portfolio_id} | {description} |\n")
                report_file.write("\n")

    def write_monitoring_recommendations(self, report_file) -> None:
        """모니터링 권장사항 섹션을 작성합니다."""
        report_file.write("## 📋 모니터링 개선 권장사항\n\n")
        
        # 수집된 데이터를 기반으로 권장사항 생성
        log_groups = self.load_json_file(self.monitoring_files['cloudwatch_log_groups'])
        alarms = self.load_json_file(self.monitoring_files['cloudwatch_alarms'])
        
        report_file.write("### 🔴 높은 우선순위\n")
        
        recommendations = []
        
        if log_groups:
            no_retention = [lg for lg in log_groups if not lg.get('retention_in_days')]
            if no_retention:
                recommendations.append(f"**로그 보존 정책**: {len(no_retention)}개의 로그 그룹에 보존 기간이 설정되지 않았습니다. 비용 절약을 위해 적절한 보존 기간을 설정하세요.")
            
            no_encryption = [lg for lg in log_groups if not lg.get('kms_key_id')]
            if no_encryption:
                recommendations.append(f"**로그 암호화**: {len(no_encryption)}개의 로그 그룹이 암호화되지 않았습니다. 보안 강화를 위해 KMS 암호화를 활성화하세요.")
        
        if alarms:
            alarm_state_alarms = [a for a in alarms if a.get('state_value') == 'ALARM']
            if alarm_state_alarms:
                recommendations.append(f"**알람 상태 확인**: {len(alarm_state_alarms)}개의 알람이 ALARM 상태입니다. 즉시 확인이 필요합니다.")
        
        if not recommendations:
            recommendations = [
                "**핵심 메트릭 모니터링**: CPU, 메모리, 디스크 사용률에 대한 알람을 설정하세요.",
                "**로그 중앙화**: 모든 애플리케이션 로그를 CloudWatch Logs로 중앙화하세요."
            ]
        
        for i, rec in enumerate(recommendations, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n### 🟡 중간 우선순위\n")
        report_file.write("1. **대시보드 구성**: 주요 메트릭을 한눈에 볼 수 있는 대시보드를 구성하세요.\n")
        report_file.write("2. **알림 채널**: SNS를 통한 알람 알림 채널을 설정하세요.\n")
        report_file.write("3. **X-Ray 추적**: 애플리케이션 성능 분석을 위한 X-Ray를 활성화하세요.\n")
        report_file.write("4. **Config 규칙**: 리소스 구성 준수를 위한 Config 규칙을 설정하세요.\n\n")
        
        report_file.write("### 🟢 낮은 우선순위\n")
        report_file.write("1. **사용자 정의 메트릭**: 비즈니스 메트릭을 CloudWatch로 전송하세요.\n")
        report_file.write("2. **로그 인사이트**: CloudWatch Logs Insights를 활용한 로그 분석을 수행하세요.\n")
        report_file.write("3. **컨테이너 인사이트**: ECS/EKS 환경에서 Container Insights를 활성화하세요.\n")
        report_file.write("4. **Service Catalog**: 표준화된 리소스 배포를 위한 Service Catalog를 활용하세요.\n\n")

    def write_cost_optimization_recommendations(self, report_file) -> None:
        """비용 최적화 권장사항 섹션을 작성합니다."""
        report_file.write("## 💰 비용 최적화 권장사항\n\n")
        
        log_groups = self.load_json_file(self.monitoring_files['cloudwatch_log_groups'])
        
        if log_groups:
            # 로그 보존 기간 분석
            no_retention = [lg for lg in log_groups if not lg.get('retention_in_days')]
            long_retention = [lg for lg in log_groups if lg.get('retention_in_days') and lg.get('retention_in_days') > 365]
            
            if no_retention:
                report_file.write(f"1. **로그 보존 기간 설정**: {len(no_retention)}개의 로그 그룹에 보존 기간이 설정되지 않아 무제한 저장되고 있습니다.\n")
            
            if long_retention:
                report_file.write(f"2. **장기 보존 검토**: {len(long_retention)}개의 로그 그룹이 1년 이상 보존되도록 설정되어 있습니다.\n")
            
            # 저장 용량 분석
            large_log_groups = [lg for lg in log_groups if lg.get('stored_bytes', 0) > 1024*1024*1024]  # 1GB 이상
            if large_log_groups:
                total_size = sum(lg.get('stored_bytes', 0) for lg in large_log_groups) / (1024*1024*1024)
                report_file.write(f"3. **대용량 로그 그룹**: {len(large_log_groups)}개의 로그 그룹이 총 {total_size:.2f}GB를 사용하고 있습니다.\n")
        
        report_file.write("\n**권장 조치:**\n")
        report_file.write("- 불필요한 로그는 30-90일 보존 기간 설정\n")
        report_file.write("- 중요한 로그는 S3로 아카이브 후 CloudWatch에서 삭제\n")
        report_file.write("- 로그 필터링을 통한 불필요한 로그 제거\n")
        report_file.write("- 메트릭 필터 최적화로 중복 메트릭 제거\n\n")

    def generate_report(self):
        """모니터링 분석 보고서를 생성합니다."""
        print("📊 Monitoring Analysis 보고서 생성 중...")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "09-monitoring-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 📊 모니터링 및 감사 종합 분석\n\n")
                report_file.write(f"> **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
                report_file.write(f"> **분석 대상**: AWS 계정 내 모든 모니터링 및 감사 서비스  \n")
                report_file.write(f"> **분석 리전**: ap-northeast-2 (서울)\n\n")
                report_file.write("이 보고서는 AWS 환경의 모니터링, 로깅, 감사 서비스에 대한 종합적인 분석을 제공하며, CloudWatch, CloudTrail, Config 등의 구성 상태와 운영 효율성을 평가합니다.\n\n")
                
                # 각 섹션 작성
                self.write_data_collection_summary(report_file)
                self.write_cloudwatch_analysis(report_file)
                self.write_cloudtrail_analysis(report_file)
                self.write_config_analysis(report_file)
                self.write_service_catalog_analysis(report_file)
                self.write_monitoring_recommendations(report_file)
                self.write_cost_optimization_recommendations(report_file)
                
                # 마무리 섹션 추가
                self.write_footer_section(report_file)
            
            print("✅ Monitoring Analysis 생성 완료: 09-monitoring-analysis.md")
            print(f"📁 보고서 위치: {report_path}")
            
            # 파일 크기 정보 출력
            file_size = report_path.stat().st_size
            print(f"📊 보고서 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Enhanced 권장사항 통계 출력
            if hasattr(self, 'get_recommendations_summary'):
                stats = self.get_recommendations_summary()
                if stats['total'] > 0:
                    print(f"📋 Enhanced 권장사항 통계:")
                    print(f"   - 높은 우선순위: {stats['high_priority']}개")
                    print(f"   - 중간 우선순위: {stats['medium_priority']}개")
                    print(f"   - 낮은 우선순위: {stats['low_priority']}개")
                    print(f"   - 총 권장사항: {stats['total']}개")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

    def write_footer_section(self, report_file):
        """보고서 마무리 섹션 추가"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_file.write(f"""
## 📞 추가 지원

이 보고서에 대한 질문이나 추가 분석이 필요한 경우:
- AWS Support 케이스 생성
- AWS Well-Architected Review 수행
- AWS Professional Services 문의

📅 분석 완료 시간: {current_time} 🔄 다음 모니터링 검토 권장 주기: 월 1회
""")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="모니터링 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    print("🔍 AWS 모니터링 분석 보고서 생성기")
    print("=" * 50)
    
    generator = MonitoringReportGenerator(args.report_dir)
    generator.generate_report()
    
    print("\n🎉 모니터링 분석 보고서 생성이 완료되었습니다!")
    
    # Enhanced 권장사항 통계 출력
    stats = generator.get_recommendations_summary()
    if stats['total'] > 0:
        print(f"📋 Enhanced 권장사항 통계:")
        print(f"   - 높은 우선순위: {stats['high_priority']}개")
        print(f"   - 중간 우선순위: {stats['medium_priority']}개")
        print(f"   - 낮은 우선순위: {stats['low_priority']}개")
        print(f"   - 총 권장사항: {stats['total']}개")

if __name__ == "__main__":
    main()
