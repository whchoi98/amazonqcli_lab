#!/usr/bin/env python3
"""
Application Analysis 보고서 생성 스크립트
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """JSON 파일을 로드하고 파싱합니다."""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load {file_path}: {e}")
    return None

def write_api_gateway_analysis(report_file, api_gateway_data: Optional[Dict]) -> None:
    """API Gateway 분석 섹션을 작성합니다."""
    report_file.write("## 🌐 API Gateway 현황\n")
    
    if not api_gateway_data:
        report_file.write("API Gateway 데이터를 찾을 수 없습니다.\n\n")
        return
    
    # API Gateway 데이터가 리스트인 경우와 딕셔너리인 경우 모두 처리
    if isinstance(api_gateway_data, list):
        api_count = len(api_gateway_data)
        apis = api_gateway_data
    elif isinstance(api_gateway_data, dict):
        if 'items' in api_gateway_data:
            apis = api_gateway_data['items']
            api_count = len(apis)
        else:
            # 딕셔너리 자체가 API 정보인 경우
            apis = [api_gateway_data]
            api_count = 1
    else:
        report_file.write("API Gateway 데이터 형식을 인식할 수 없습니다.\n\n")
        return
    
    report_file.write(f"**총 API Gateway:** {api_count}개\n\n")
    
    if api_count > 0:
        report_file.write("### API Gateway 상세 정보\n")
        report_file.write("| API 이름 | API ID | 생성일 | 설명 | 엔드포인트 타입 |\n")
        report_file.write("|----------|--------|--------|------|----------------|\n")
        
        for api in apis:
            name = api.get('name', 'N/A')
            api_id = api.get('id', 'N/A')
            created_date = api.get('createdDate', 'N/A')
            description = api.get('description', 'N/A')
            endpoint_config = api.get('endpointConfiguration', {})
            endpoint_types = endpoint_config.get('types', ['N/A']) if endpoint_config else ['N/A']
            endpoint_type = ', '.join(endpoint_types) if endpoint_types else 'N/A'
            
            # 날짜 형식 정리 (ISO 형식인 경우)
            if isinstance(created_date, str) and 'T' in created_date:
                created_date = created_date.split('T')[0]
            
            report_file.write(f"| {name} | {api_id} | {created_date} | {description} | {endpoint_type} |\n")
        
        report_file.write("\n")

def write_messaging_analysis(report_file, sns_data: Optional[Dict], sqs_data: Optional[Dict] = None) -> None:
    """메시징 서비스 분석 섹션을 작성합니다."""
    report_file.write("## 📨 메시징 서비스 현황\n\n")
    
    # SNS 토픽 분석
    report_file.write("### SNS 토픽\n")
    if not sns_data:
        report_file.write("SNS 토픽 데이터를 찾을 수 없습니다.\n\n")
    else:
        # SNS 데이터가 리스트인 경우와 딕셔너리인 경우 모두 처리
        if isinstance(sns_data, list):
            sns_count = len(sns_data)
            topics = sns_data
        elif isinstance(sns_data, dict):
            if 'Topics' in sns_data:
                topics = sns_data['Topics']
                sns_count = len(topics)
            else:
                # 딕셔너리 자체가 토픽 정보인 경우
                topics = [sns_data]
                sns_count = 1
        else:
            report_file.write("SNS 토픽 데이터 형식을 인식할 수 없습니다.\n\n")
            return
        
        report_file.write(f"**총 SNS 토픽:** {sns_count}개\n\n")
        
        if sns_count > 0:
            report_file.write("| 토픽 ARN | 토픽 이름 | 구독자 수 |\n")
            report_file.write("|----------|-----------|----------|\n")
            
            for topic in topics:
                if isinstance(topic, str):
                    # ARN만 있는 경우
                    topic_arn = topic
                    topic_name = topic_arn.split(':')[-1] if ':' in topic_arn else topic_arn
                    subscribers = 'N/A'
                else:
                    # 딕셔너리 형태의 토픽 정보
                    topic_arn = topic.get('TopicArn', topic.get('arn', 'N/A'))
                    topic_name = topic.get('Name', topic_arn.split(':')[-1] if ':' in topic_arn else 'N/A')
                    subscribers = topic.get('SubscriptionsConfirmed', 'N/A')
                
                report_file.write(f"| {topic_arn} | {topic_name} | {subscribers} |\n")
            
            report_file.write("\n")
    
    # SQS 큐 분석 (데이터가 있는 경우)
    if sqs_data:
        report_file.write("### SQS 큐\n")
        if isinstance(sqs_data, list):
            sqs_count = len(sqs_data)
            queues = sqs_data
        elif isinstance(sqs_data, dict):
            if 'QueueUrls' in sqs_data:
                queues = sqs_data['QueueUrls']
                sqs_count = len(queues)
            else:
                queues = [sqs_data]
                sqs_count = 1
        else:
            queues = []
            sqs_count = 0
        
        report_file.write(f"**총 SQS 큐:** {sqs_count}개\n\n")
        
        if sqs_count > 0:
            report_file.write("| 큐 URL | 큐 이름 |\n")
            report_file.write("|--------|--------|\n")
            
            for queue in queues:
                if isinstance(queue, str):
                    queue_url = queue
                    queue_name = queue_url.split('/')[-1] if '/' in queue_url else queue_url
                else:
                    queue_url = queue.get('QueueUrl', queue.get('url', 'N/A'))
                    queue_name = queue.get('QueueName', queue_url.split('/')[-1] if '/' in queue_url else 'N/A')
                
                report_file.write(f"| {queue_url} | {queue_name} |\n")
            
            report_file.write("\n")

def write_eventbridge_analysis(report_file, eventbridge_data: Optional[Dict]) -> None:
    """EventBridge 분석 섹션을 작성합니다."""
    if not eventbridge_data:
        return
    
    report_file.write("### EventBridge 이벤트 버스\n")
    
    if isinstance(eventbridge_data, list):
        bus_count = len(eventbridge_data)
        buses = eventbridge_data
    elif isinstance(eventbridge_data, dict):
        if 'EventBuses' in eventbridge_data:
            buses = eventbridge_data['EventBuses']
            bus_count = len(buses)
        else:
            buses = [eventbridge_data]
            bus_count = 1
    else:
        report_file.write("EventBridge 데이터 형식을 인식할 수 없습니다.\n\n")
        return
    
    report_file.write(f"**총 EventBridge 버스:** {bus_count}개\n\n")
    
    if bus_count > 0:
        report_file.write("| 버스 이름 | ARN | 정책 |\n")
        report_file.write("|-----------|-----|------|\n")
        
        for bus in buses:
            name = bus.get('Name', 'N/A')
            arn = bus.get('Arn', 'N/A')
            policy = 'Yes' if bus.get('Policy') else 'No'
            
            report_file.write(f"| {name} | {arn} | {policy} |\n")
        
        report_file.write("\n")

def write_step_functions_analysis(report_file, step_functions_data: Optional[Dict]) -> None:
    """Step Functions 분석 섹션을 작성합니다."""
    if not step_functions_data:
        return
    
    report_file.write("### Step Functions 상태 머신\n")
    
    if isinstance(step_functions_data, list):
        sm_count = len(step_functions_data)
        state_machines = step_functions_data
    elif isinstance(step_functions_data, dict):
        if 'stateMachines' in step_functions_data:
            state_machines = step_functions_data['stateMachines']
            sm_count = len(state_machines)
        else:
            state_machines = [step_functions_data]
            sm_count = 1
    else:
        report_file.write("Step Functions 데이터 형식을 인식할 수 없습니다.\n\n")
        return
    
    report_file.write(f"**총 Step Functions 상태 머신:** {sm_count}개\n\n")
    
    if sm_count > 0:
        report_file.write("| 상태 머신 이름 | 타입 | 상태 | 생성일 |\n")
        report_file.write("|----------------|------|------|--------|\n")
        
        for sm in state_machines:
            name = sm.get('name', 'N/A')
            sm_type = sm.get('type', 'N/A')
            status = sm.get('status', 'N/A')
            creation_date = sm.get('creationDate', 'N/A')
            
            # 날짜 형식 정리
            if isinstance(creation_date, str) and 'T' in creation_date:
                creation_date = creation_date.split('T')[0]
            
            report_file.write(f"| {name} | {sm_type} | {status} | {creation_date} |\n")
        
        report_file.write("\n")

def write_recommendations(report_file, api_gateway_data: Optional[Dict], sns_data: Optional[Dict]) -> None:
    """권장사항 섹션을 작성합니다."""
    report_file.write("## 📋 애플리케이션 권장사항\n\n")
    
    report_file.write("### 🔴 높은 우선순위\n")
    
    recommendations = []
    
    # API Gateway 관련 권장사항
    if api_gateway_data:
        recommendations.append("**API Gateway 모니터링**: 응답 시간, 오류율 추적")
        recommendations.append("**API Gateway 보안**: API 키, IAM 역할, WAF 설정 검토")
        recommendations.append("**API Gateway 캐싱**: 자주 요청되는 엔드포인트에 캐싱 적용")
    
    # SNS 관련 권장사항
    if sns_data:
        recommendations.append("**메시지 큐 최적화**: DLQ 설정 및 메시지 보존 기간 조정")
        recommendations.append("**SNS 구독 관리**: 불필요한 구독 정리 및 필터링 정책 적용")
    
    # 기본 권장사항
    if not recommendations:
        recommendations = [
            "**API Gateway 모니터링**: 응답 시간, 오류율 추적",
            "**메시지 큐 최적화**: DLQ 설정 및 메시지 보존 기간 조정"
        ]
    
    for i, rec in enumerate(recommendations, 1):
        report_file.write(f"{i}. {rec}\n")
    
    report_file.write("\n### 🟡 중간 우선순위\n")
    report_file.write("1. **비용 최적화**: 사용하지 않는 API 및 메시징 리소스 정리\n")
    report_file.write("2. **로깅 및 모니터링**: CloudWatch 로그 및 메트릭 설정\n")
    report_file.write("3. **백업 및 복구**: 중요한 설정의 백업 전략 수립\n\n")
    
    report_file.write("### 🟢 낮은 우선순위\n")
    report_file.write("1. **성능 최적화**: API 응답 시간 및 처리량 개선\n")
    report_file.write("2. **자동화**: Infrastructure as Code를 통한 배포 자동화\n")
    report_file.write("3. **문서화**: API 문서 및 아키텍처 다이어그램 업데이트\n\n")

def write_cost_optimization(report_file, api_gateway_data: Optional[Dict], sns_data: Optional[Dict]) -> None:
    """비용 최적화 섹션을 작성합니다."""
    report_file.write("## 💰 비용 최적화 기회\n\n")
    
    report_file.write("### 즉시 절감 가능\n")
    
    cost_items = []
    
    # API Gateway 비용 최적화
    if api_gateway_data:
        cost_items.append("**API Gateway 사용량 검토**: 사용하지 않는 API 엔드포인트 제거")
        cost_items.append("**API Gateway 캐싱**: 반복 요청 감소로 비용 절감")
    
    # SNS 비용 최적화
    if sns_data:
        cost_items.append("**SNS 구독 정리**: 불필요한 구독 및 토픽 제거")
        cost_items.append("**메시지 필터링**: 불필요한 메시지 전송 방지")
    
    # 기본 비용 최적화 항목
    if not cost_items:
        cost_items = [
            "**사용하지 않는 리소스 정리**: 미사용 API 및 메시징 서비스 제거",
            "**모니터링 설정**: 비용 알림 및 예산 설정"
        ]
    
    for i, item in enumerate(cost_items, 1):
        report_file.write(f"{i}. {item}\n")
    
    report_file.write("\n### 장기 절감 계획\n")
    report_file.write("1. **예약 용량**: 예측 가능한 워크로드에 대한 예약 용량 구매\n")
    report_file.write("2. **아키텍처 최적화**: 서버리스 아키텍처로 전환 검토\n")
    report_file.write("3. **리소스 태깅**: 비용 추적을 위한 체계적인 태깅 전략\n\n")

def main():
    """메인 함수"""
    print("🌐 Application Analysis 보고서 생성 중...")
    
    # 보고서 디렉토리 설정
    report_dir = Path("/home/ec2-user/amazonqcli_lab/report")
    os.chdir(report_dir)
    
    # JSON 데이터 파일들 로드
    api_gateway_data = load_json_file("application_api_gateway_rest_apis.json")
    sns_data = load_json_file("application_sns_topics.json")
    sqs_data = load_json_file("application_sqs_queues.json")  # 선택적
    eventbridge_data = load_json_file("application_eventbridge_buses.json")  # 선택적
    step_functions_data = load_json_file("application_step_functions.json")  # 선택적
    
    # 보고서 파일 생성
    report_path = report_dir / "07-application-analysis.md"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as report_file:
            # 헤더 작성
            report_file.write("# 애플리케이션 서비스 분석\n\n")
            
            # 각 섹션 작성
            write_api_gateway_analysis(report_file, api_gateway_data)
            write_messaging_analysis(report_file, sns_data, sqs_data)
            write_eventbridge_analysis(report_file, eventbridge_data)
            write_step_functions_analysis(report_file, step_functions_data)
            write_recommendations(report_file, api_gateway_data, sns_data)
            write_cost_optimization(report_file, api_gateway_data, sns_data)
            
            # 마무리
            report_file.write("---\n")
            report_file.write("*애플리케이션 분석 완료*\n")
        
        print("✅ Application Analysis 생성 완료: 07-application-analysis.md")
        
    except IOError as e:
        print(f"❌ 보고서 파일 생성 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
