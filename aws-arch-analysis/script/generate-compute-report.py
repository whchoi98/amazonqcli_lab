#!/usr/bin/env python3
"""
Compute Analysis 보고서 생성 스크립트
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

def write_ec2_analysis(report_file, ec2_data: Optional[Dict]) -> None:
    """EC2 인스턴스 분석 섹션을 작성합니다."""
    report_file.write("## 💻 EC2 인스턴스 현황\n\n")
    report_file.write("### 인스턴스 개요\n")
    
    if not ec2_data or 'rows' not in ec2_data:
        report_file.write("EC2 인스턴스 데이터를 찾을 수 없습니다.\n\n")
        return
    
    instances = ec2_data['rows']
    total_count = len(instances)
    running_count = len([i for i in instances if i.get('instance_state') == 'running'])
    stopped_count = len([i for i in instances if i.get('instance_state') == 'stopped'])
    
    report_file.write(f"**총 EC2 인스턴스:** {total_count}개\n")
    report_file.write(f"- **실행 중:** {running_count}개\n")
    report_file.write(f"- **중지됨:** {stopped_count}개\n\n")
    
    # 인스턴스 상세 목록
    report_file.write("### 인스턴스 상세 목록\n")
    report_file.write("| 인스턴스 ID | 타입 | 상태 | VPC ID | 프라이빗 IP | 태그 |\n")
    report_file.write("|-------------|------|------|--------|-------------|------|\n")
    
    for i, instance in enumerate(instances[:10]):  # 최대 10개만 표시
        instance_id = instance.get('instance_id', 'N/A')
        instance_type = instance.get('instance_type', 'N/A')
        state = instance.get('instance_state', 'N/A')
        vpc_id = instance.get('vpc_id', 'N/A')
        private_ip = instance.get('private_ip_address', 'N/A')
        tag_name = instance.get('tags', {}).get('Name', 'N/A') if instance.get('tags') else 'N/A'
        
        report_file.write(f"| {instance_id} | {instance_type} | {state} | {vpc_id} | {private_ip} | {tag_name} |\n")
    
    # 인스턴스 타입별 분포
    report_file.write("\n### 인스턴스 타입별 분포\n")
    report_file.write("| 인스턴스 타입 | 개수 | 비율 |\n")
    report_file.write("|---------------|------|------|\n")
    
    type_counts = {}
    for instance in instances:
        instance_type = instance.get('instance_type', 'Unknown')
        type_counts[instance_type] = type_counts.get(instance_type, 0) + 1
    
    for instance_type, count in type_counts.items():
        percentage = int((count * 100) / total_count) if total_count > 0 else 0
        report_file.write(f"| {instance_type} | {count} | {percentage}% |\n")
    
    report_file.write("\n")

def write_alb_analysis(report_file, alb_data: Optional[Dict]) -> None:
    """ALB 분석 섹션을 작성합니다."""
    report_file.write("## ⚖️ 로드 밸런서 현황\n\n")
    report_file.write("### Application Load Balancer\n")
    
    if not alb_data or 'rows' not in alb_data:
        report_file.write("ALB 데이터를 찾을 수 없습니다.\n\n")
        return
    
    albs = alb_data['rows']
    alb_count = len(albs)
    
    report_file.write(f"**총 ALB 수:** {alb_count}개\n\n")
    report_file.write("| 이름 | 타입 | 스킴 | VPC ID | 상태 | DNS 이름 |\n")
    report_file.write("|------|------|------|--------|------|----------|\n")
    
    for alb in albs:
        name = alb.get('load_balancer_name') or alb.get('name', 'N/A')
        alb_type = alb.get('type', 'N/A')
        scheme = alb.get('scheme', 'N/A')
        vpc_id = alb.get('vpc_id', 'N/A')
        state = alb.get('state', {}).get('code', 'available') if alb.get('state') else 'available'
        dns_name = alb.get('dns_name', 'N/A')
        
        report_file.write(f"| {name} | {alb_type} | {scheme} | {vpc_id} | {state} | {dns_name} |\n")
    
    report_file.write("\n")

def write_target_groups_analysis(report_file, tg_data: Optional[Dict]) -> None:
    """Target Groups 분석 섹션을 작성합니다."""
    report_file.write("### Target Groups\n")
    
    if not tg_data or 'rows' not in tg_data:
        report_file.write("Target Group 데이터를 찾을 수 없습니다.\n\n")
        return
    
    target_groups = tg_data['rows']
    tg_count = len(target_groups)
    
    report_file.write(f"**총 Target Group 수:** {tg_count}개\n\n")
    report_file.write("| Target Group 이름 | 프로토콜 | 포트 | VPC ID | 헬스체크 경로 |\n")
    report_file.write("|-------------------|----------|------|--------|---------------|\n")
    
    for tg in target_groups[:5]:  # 최대 5개만 표시
        name = tg.get('target_group_name', 'N/A')
        protocol = tg.get('protocol', 'N/A')
        port = tg.get('port', 'N/A')
        vpc_id = tg.get('vpc_id', 'N/A')
        health_check_path = tg.get('health_check_path', 'N/A')
        
        report_file.write(f"| {name} | {protocol} | {port} | {vpc_id} | {health_check_path} |\n")
    
    report_file.write("\n")

def write_asg_analysis(report_file, asg_data: Optional[Dict]) -> None:
    """Auto Scaling 그룹 분석 섹션을 작성합니다."""
    report_file.write("### Auto Scaling 그룹\n")
    
    if not asg_data or 'rows' not in asg_data:
        report_file.write("Auto Scaling 그룹 데이터를 찾을 수 없습니다.\n\n")
        return
    
    asgs = asg_data['rows']
    asg_count = len(asgs)
    
    report_file.write(f"**총 ASG 수:** {asg_count}개\n\n")
    report_file.write("| ASG 이름 | 최소 | 원하는 | 최대 | 현재 인스턴스 | 헬스체크 타입 |\n")
    report_file.write("|----------|------|---------|------|---------------|---------------|\n")
    
    for asg in asgs:
        name = asg.get('auto_scaling_group_name', 'N/A')
        min_size = asg.get('min_size', 'N/A')
        desired = asg.get('desired_capacity', 'N/A')
        max_size = asg.get('max_size', 'N/A')
        current_instances = len(asg.get('instances', [])) if asg.get('instances') else 0
        health_check_type = asg.get('health_check_type', 'N/A')
        
        report_file.write(f"| {name} | {min_size} | {desired} | {max_size} | {current_instances} | {health_check_type} |\n")
    
    report_file.write("\n")

def write_lambda_analysis(report_file, lambda_data: Optional[Dict]) -> None:
    """Lambda 함수 분석 섹션을 작성합니다."""
    report_file.write("## 🚀 서버리스 컴퓨팅\n\n")
    report_file.write("### Lambda 함수 현황\n")
    
    if not lambda_data or 'Functions' not in lambda_data:
        report_file.write("Lambda 함수 데이터를 찾을 수 없습니다.\n\n")
        return
    
    functions = lambda_data['Functions']
    lambda_count = len(functions)
    
    report_file.write(f"**총 Lambda 함수:** {lambda_count}개\n\n")
    report_file.write("| 함수명 | 런타임 | 메모리 | 타임아웃 | 마지막 수정 | 코드 크기 |\n")
    report_file.write("|--------|---------|--------|----------|-------------|-----------|")
    
    for func in functions:
        name = func.get('FunctionName', 'N/A')
        runtime = func.get('Runtime', 'N/A')
        memory = func.get('MemorySize', 'N/A')
        timeout = func.get('Timeout', 'N/A')
        last_modified = func.get('LastModified', 'N/A')
        code_size = func.get('CodeSize', 'N/A')
        
        report_file.write(f"| {name} | {runtime} | {memory}MB | {timeout}s | {last_modified} | {code_size}B |\n")
    
    report_file.write("\n")

def write_eks_analysis(report_file, eks_data: Optional[Dict], node_group_data: Optional[Dict]) -> None:
    """EKS 클러스터 분석 섹션을 작성합니다."""
    report_file.write("## 🐳 컨테이너 서비스\n\n")
    report_file.write("### EKS 클러스터\n")
    
    if not eks_data or 'rows' not in eks_data:
        report_file.write("EKS 클러스터 데이터를 찾을 수 없습니다.\n\n")
        return
    
    clusters = eks_data['rows']
    eks_count = len(clusters)
    
    report_file.write(f"**총 EKS 클러스터:** {eks_count}개\n\n")
    report_file.write("| 클러스터명 | 버전 | 상태 | 엔드포인트 | 플랫폼 버전 |\n")
    report_file.write("|------------|------|------|------------|-------------|\n")
    
    for cluster in clusters:
        name = cluster.get('name', 'N/A')
        version = cluster.get('version', 'N/A')
        status = cluster.get('status', 'N/A')
        endpoint = cluster.get('endpoint', 'N/A')[:50] + '...' if cluster.get('endpoint') else 'N/A'
        platform_version = cluster.get('platform_version', 'N/A')
        
        report_file.write(f"| {name} | {version} | {status} | {endpoint} | {platform_version} |\n")
    
    # EKS 노드 그룹 정보
    if node_group_data and 'rows' in node_group_data:
        node_groups = node_group_data['rows']
        node_group_count = len(node_groups)
        
        report_file.write(f"\n### EKS 노드 그룹\n")
        report_file.write(f"**총 노드 그룹:** {node_group_count}개\n\n")
        report_file.write("| 노드 그룹명 | 클러스터 | 인스턴스 타입 | 원하는 크기 | 상태 |\n")
        report_file.write("|-------------|----------|---------------|-------------|------|\n")
        
        for ng in node_groups:
            ng_name = ng.get('nodegroup_name', 'N/A')
            cluster_name = ng.get('cluster_name', 'N/A')
            instance_types = ng.get('instance_types', ['N/A'])
            instance_type = instance_types[0] if instance_types else 'N/A'
            desired_size = ng.get('scaling_config', {}).get('desired_size', 'N/A') if ng.get('scaling_config') else 'N/A'
            status = ng.get('status', 'N/A')
            
            report_file.write(f"| {ng_name} | {cluster_name} | {instance_type} | {desired_size} | {status} |\n")
    
    report_file.write("\n")

def write_ecs_analysis(report_file, ecs_data: Optional[Dict]) -> None:
    """ECS 클러스터 분석 섹션을 작성합니다."""
    report_file.write("### ECS 클러스터\n")
    
    if not ecs_data or 'rows' not in ecs_data:
        report_file.write("ECS 클러스터 데이터를 찾을 수 없습니다.\n\n")
        return
    
    clusters = ecs_data['rows']
    ecs_count = len(clusters)
    
    report_file.write(f"**총 ECS 클러스터:** {ecs_count}개\n\n")
    
    if ecs_count > 0:
        report_file.write("| 클러스터명 | 상태 | 활성 서비스 | 실행 중 태스크 | 등록된 인스턴스 |\n")
        report_file.write("|------------|------|-------------|---------------|------------------|\n")
        
        for cluster in clusters:
            name = cluster.get('cluster_name', 'N/A')
            status = cluster.get('status', 'N/A')
            active_services = cluster.get('active_services_count', 0)
            running_tasks = cluster.get('running_tasks_count', 0)
            registered_instances = cluster.get('registered_container_instances_count', 0)
            
            report_file.write(f"| {name} | {status} | {active_services} | {running_tasks} | {registered_instances} |\n")
    
    report_file.write("\n")

def write_recommendations_and_cost_optimization(report_file, ec2_data: Optional[Dict]) -> None:
    """권장사항 및 비용 최적화 섹션을 작성합니다."""
    report_file.write("## 📋 컴퓨팅 권장사항\n\n")
    
    report_file.write("### 🔴 높은 우선순위\n")
    report_file.write("1. **인스턴스 타입 최적화**: 사용률 기반 적절한 타입 선택\n")
    report_file.write("2. **미사용 인스턴스 정리**: 중지된 인스턴스 검토 및 정리\n")
    report_file.write("3. **Auto Scaling 정책**: 트래픽 패턴에 맞는 스케일링 정책 설정\n\n")
    
    report_file.write("### 🟡 중간 우선순위\n")
    report_file.write("1. **예약 인스턴스 활용**: 비용 최적화를 위한 RI 구매 검토\n")
    report_file.write("2. **Lambda 성능 최적화**: 메모리 및 타임아웃 설정 조정\n")
    report_file.write("3. **로드 밸런서 최적화**: Target Group 헬스체크 설정 검토\n\n")
    
    report_file.write("### 🟢 낮은 우선순위\n")
    report_file.write("1. **스팟 인스턴스 활용**: 배치 작업용 비용 절감\n")
    report_file.write("2. **컨테이너화 검토**: ECS/EKS 마이그레이션 고려\n")
    report_file.write("3. **Graviton 인스턴스**: ARM 기반 인스턴스 성능/비용 검토\n\n")
    
    report_file.write("## 💰 비용 최적화 기회\n\n")
    report_file.write("### 즉시 절감 가능\n")
    
    # 비용 최적화 분석
    if ec2_data and 'rows' in ec2_data:
        stopped_instances = len([i for i in ec2_data['rows'] if i.get('instance_state') == 'stopped'])
        if stopped_instances > 0:
            report_file.write(f"1. **중지된 인스턴스**: {stopped_instances}개 (EBS 비용 발생 중)\n")
    
    report_file.write("2. **오버프로비저닝**: 사용률 낮은 인스턴스 타입 다운사이징\n")
    report_file.write("3. **예약 인스턴스**: 장기 실행 워크로드 비용 절감\n\n")
    
    report_file.write("---\n")
    report_file.write("*컴퓨팅 분석 완료*\n")

def main():
    """메인 함수"""
    print("💻 Compute Analysis 보고서 생성 중...")
    
    # 보고서 디렉토리 설정
    report_dir = Path("/home/ec2-user/amazonqcli_lab/report")
    os.chdir(report_dir)
    
    # JSON 데이터 파일들 로드
    ec2_data = load_json_file("compute_ec2_instances.json")
    alb_data = load_json_file("compute_alb_detailed.json")
    tg_data = load_json_file("compute_target_groups.json")
    asg_data = load_json_file("compute_asg_detailed.json")
    lambda_data = load_json_file("iac_lambda_functions.json")
    eks_data = load_json_file("compute_eks_clusters.json")
    node_group_data = load_json_file("compute_eks_node_groups.json")
    ecs_data = load_json_file("compute_ecs_clusters.json")
    
    # 보고서 파일 생성
    report_path = report_dir / "03-compute-analysis.md"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as report_file:
            # 헤더 작성
            report_file.write("# 컴퓨팅 리소스 분석\n\n")
            
            # 각 섹션 작성
            write_ec2_analysis(report_file, ec2_data)
            write_alb_analysis(report_file, alb_data)
            write_target_groups_analysis(report_file, tg_data)
            write_asg_analysis(report_file, asg_data)
            write_lambda_analysis(report_file, lambda_data)
            write_eks_analysis(report_file, eks_data, node_group_data)
            write_ecs_analysis(report_file, ecs_data)
            write_recommendations_and_cost_optimization(report_file, ec2_data)
        
        print("✅ Compute Analysis 생성 완료: 03-compute-analysis.md")
        
    except IOError as e:
        print(f"❌ 보고서 파일 생성 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
