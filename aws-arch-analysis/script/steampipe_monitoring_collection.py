#!/usr/bin/env python3
"""
AWS 모니터링 및 리소스 관리 서비스 데이터 수집 스크립트
CloudWatch, X-Ray, Config, Organizations, Service Catalog 등 포괄적 수집

작성자: Amazon Q CLI Lab
버전: 1.0
생성일: 2025-06-27
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

class MonitoringDataCollector:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 스크립트의 실제 위치를 기준으로 경로 설정
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self.report_dir = project_root / "aws-arch-analysis" / "report"
        self.create_output_directory()
        
    def create_output_directory(self):
        """출력 디렉토리 생성"""
        try:
            self.report_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 출력 디렉토리 생성: {self.report_dir}")
        except Exception as e:
            print(f"❌ 디렉토리 생성 실패: {e}")
            sys.exit(1)

    def run_steampipe_query(self, service_name, query):
        """Steampipe 쿼리 실행 및 결과 저장"""
        try:
            print(f"🔍 {service_name} 데이터 수집 중...")
            
            # Steampipe 쿼리 실행
            result = subprocess.run(
                ['steampipe', 'query', query, '--output', 'json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # JSON 파싱 시도
                try:
                    data = json.loads(result.stdout)
                    if data and len(data) > 0:
                        # 파일에 저장
                        filename = self.report_dir / f"monitoring_{service_name.lower().replace(' ', '_')}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                        
                        print(f"✅ {service_name}: {len(data)}개 항목 수집 완료")
                        return True, len(data)
                    else:
                        print(f"⚠️  {service_name}: 데이터 없음")
                        return False, 0
                except json.JSONDecodeError as e:
                    print(f"❌ {service_name}: JSON 파싱 오류 - {e}")
                    return False, 0
            else:
                error_msg = result.stderr.strip() if result.stderr else "알 수 없는 오류"
                print(f"❌ {service_name}: 쿼리 실행 실패 - {error_msg}")
                return False, 0
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {service_name}: 쿼리 타임아웃 (60초)")
            return False, 0
        except Exception as e:
            print(f"❌ {service_name}: 예외 발생 - {e}")
            return False, 0

    def get_monitoring_queries(self):
        """모니터링 및 리소스 관리 서비스 쿼리 정의 (실제 사용 가능한 테이블 기반)"""
        return {
            # CloudWatch 알람 (실제 테이블명: aws_cloudwatch_alarm)
            "CloudWatch Alarms": "select name, arn, alarm_description, state_value, metric_name, namespace, statistic, threshold, comparison_operator, evaluation_periods, datapoints_to_alarm, treat_missing_data, alarm_actions, ok_actions, insufficient_data_actions, region, account_id from aws_cloudwatch_alarm;",
            
            # CloudWatch 이벤트 규칙 (EventBridge)
            "CloudWatch Event Rules": "select name, arn, description, event_pattern, schedule_expression, state, role_arn, managed_by, event_bus_name, targets, tags, region, account_id from aws_cloudwatch_event_rule;",
            
            # CloudWatch Logs
            "CloudWatch Log Groups": "select name, arn, creation_time, retention_in_days, stored_bytes, metric_filter_count, kms_key_id, tags, region, account_id from aws_cloudwatch_log_group;",
            
            "CloudWatch Log Streams": "select log_group_name, name, arn, creation_time, first_event_time, last_event_time, last_ingestion_time, upload_sequence_token, stored_bytes, region, account_id from aws_cloudwatch_log_stream;",
            
            "CloudWatch Log Metric Filters": "select name, log_group_name, filter_pattern, metric_transformations, creation_time, region, account_id from aws_cloudwatch_log_metric_filter;",
            
            "CloudWatch Log Subscription Filters": "select name, log_group_name, filter_pattern, destination_arn, role_arn, distribution, creation_time, region, account_id from aws_cloudwatch_log_subscription_filter;",
            
            "CloudWatch Log Destinations": "select destination_name, arn, role_arn, target_arn, access_policy, creation_time, region, account_id from aws_cloudwatch_log_destination;",
            
            "CloudWatch Log Resource Policies": "select policy_name, policy_document, last_updated_time, region, account_id from aws_cloudwatch_log_resource_policy;",
            
            # CloudWatch 메트릭
            "CloudWatch Metrics": "select metric_name, namespace, dimensions, region, account_id from aws_cloudwatch_metric;",
            
            # CloudTrail
            "CloudTrail Trails": "select name, arn, s3_bucket_name, s3_key_prefix, include_global_service_events, is_multi_region_trail, home_region, trail_arn, log_file_validation_enabled, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn, kms_key_id, has_custom_event_selectors, has_insight_selectors, is_organization_trail, is_logging, latest_delivery_time, latest_notification_time, start_logging_time, stop_logging_time, tags, region, account_id from aws_cloudtrail_trail;",
            
            "CloudTrail Event Data Stores": "select arn, name, status, advanced_event_selectors, multi_region_enabled, organization_enabled, retention_period, termination_protection_enabled, kms_key_id, created_timestamp, updated_timestamp, region, account_id from aws_cloudtrail_event_data_store;",
            
            "CloudTrail Channels": "select arn, name, source, destinations, region, account_id from aws_cloudtrail_channel;",
            
            # Config
            "Config Configuration Recorders": "select name, role_arn, recording_group, status, region, account_id from aws_config_configuration_recorder;",
            
            "Config Delivery Channels": "select name, s3_bucket_name, s3_key_prefix, sns_topic_arn, region, account_id from aws_config_delivery_channel;",
            
            "Config Rules": "select name, arn, rule_id, description, source, input_parameters, maximum_execution_frequency, state, created_by, region, account_id from aws_config_rule;",
            
            "Config Conformance Packs": "select name, arn, conformance_pack_id, delivery_s3_bucket, delivery_s3_key_prefix, conformance_pack_input_parameters, last_update_requested_time, created_by, region, account_id from aws_config_conformance_pack;",
            
            "Config Aggregate Authorizations": "select authorized_account_id, authorized_aws_region, creation_time, region, account_id from aws_config_aggregate_authorization;",
            
            "Config Retention Configurations": "select name, retention_period_in_days, region, account_id from aws_config_retention_configuration;",
            
            # Service Catalog
            "Service Catalog Portfolios": "select id, arn, display_name, description, provider_name, created_time, tags, region, account_id from aws_servicecatalog_portfolio;",
            
            "Service Catalog Products": "select product_id, name, owner, short_description, type, distributor, has_default_path, support_description, support_email, support_url, created_time, tags, region, account_id from aws_servicecatalog_product;",
            
            "Service Catalog Provisioned Products": "select name, arn, id, type, provisioning_artifact_id, product_id, user_arn, user_arn_session, status, status_message, created_time, last_updated_time, last_record_id, last_provisioning_record_id, last_successful_provisioning_record_id, tags, region, account_id from aws_servicecatalog_provisioned_product;",
            
            # Organizations (권한 필요)
            "Organizations Accounts": "select id, arn, email, name, status, joined_method, joined_timestamp, region, account_id from aws_organizations_account;",
            
            "Organizations Organizational Units": "select id, arn, name, parent_id, region, account_id from aws_organizations_organizational_unit;",
            
            "Organizations Policies": "select id, arn, name, description, type, aws_managed, content, region, account_id from aws_organizations_policy;",
            
            "Organizations Policy Targets": "select policy_id, target_id, target_type, region, account_id from aws_organizations_policy_target;",
            
            "Organizations Delegated Administrators": "select account_id, service_principal, delegation_enabled_date, region from aws_organizations_delegated_administrator;",
            
            "Organizations Root": "select id, arn, name, policy_types, region, account_id from aws_organizations_root;"
        }

    def collect_all_data(self):
        """모든 모니터링 데이터 병렬 수집"""
        queries = self.get_monitoring_queries()
        successful_collections = 0
        total_items = 0
        
        print(f"🚀 모니터링 및 리소스 관리 데이터 수집 시작 ({len(queries)}개 서비스)")
        print("=" * 80)
        
        start_time = time.time()
        
        # 병렬 처리로 성능 향상
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_service = {
                executor.submit(self.run_steampipe_query, service, query): service 
                for service, query in queries.items()
            }
            
            for future in as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    success, count = future.result()
                    if success:
                        successful_collections += 1
                        total_items += count
                except Exception as e:
                    print(f"❌ {service}: 처리 중 오류 - {e}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 수집 결과 요약
        print("\n" + "=" * 80)
        print("📊 모니터링 데이터 수집 완료!")
        print(f"✅ 성공한 수집: {successful_collections}/{len(queries)} ({successful_collections/len(queries)*100:.1f}%)")
        print(f"📦 총 수집 항목: {total_items:,}개")
        print(f"⏱️  실행 시간: {execution_time:.1f}초")
        print(f"📁 출력 디렉토리: {self.report_dir}")
        
        # 수집된 파일 목록
        if successful_collections > 0:
            print(f"\n📋 수집된 데이터 파일:")
            try:
                files = sorted([f for f in self.report_dir.glob("monitoring_*.json")])
                for file_path in files:
                    file_size = file_path.stat().st_size
                    print(f"   • {file_path.name} ({file_size:,} bytes)")
            except Exception as e:
                print(f"   파일 목록 조회 실패: {e}")
        
        return successful_collections, total_items

def main():
    """메인 실행 함수"""
    print("🔍 AWS 모니터링 및 리소스 관리 서비스 데이터 수집기")
    print("=" * 80)
    
    # Steampipe 설치 확인
    try:
        result = subprocess.run(['steampipe', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Steampipe가 설치되지 않았거나 실행할 수 없습니다.")
            print("   설치 방법: https://steampipe.io/downloads")
            sys.exit(1)
        print(f"✅ Steampipe 버전: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Steampipe를 찾을 수 없습니다. PATH에 추가되었는지 확인하세요.")
        sys.exit(1)
    
    # 데이터 수집 실행
    collector = MonitoringDataCollector()
    successful_collections, total_items = collector.collect_all_data()
    
    if successful_collections == 0:
        print("\n⚠️  수집된 데이터가 없습니다. AWS 자격 증명과 권한을 확인하세요.")
        sys.exit(1)
    
    print(f"\n🎉 모니터링 데이터 수집이 완료되었습니다!")
    print(f"   다음 명령어로 리포트를 생성할 수 있습니다:")
    print(f"   python3 generate-monitoring-report.py")

if __name__ == "__main__":
    main()
