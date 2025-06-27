#!/usr/bin/env python3
"""
확장된 컴퓨팅 분석 보고서 생성 스크립트 (Python 버전)
모든 컴퓨팅 리소스와 Kubernetes 워크로드 포함
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

class ExtendedComputeReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

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

    def write_ec2_analysis(self, report_file, ec2_data: Optional[List]) -> None:
        """EC2 인스턴스 분석 섹션을 작성합니다."""
        report_file.write("## 💻 EC2 인스턴스 현황\n\n")
        
        if not ec2_data:
            report_file.write("EC2 인스턴스 데이터를 찾을 수 없습니다.\n\n")
            return
        
        # 기본 통계
        total_instances = len(ec2_data)
        running_instances = len([i for i in ec2_data if i.get('instance_state') == 'running'])
        stopped_instances = len([i for i in ec2_data if i.get('instance_state') == 'stopped'])
        
        report_file.write("### 인스턴스 개요\n")
        report_file.write(f"**총 EC2 인스턴스:** {total_instances}개\n")
        report_file.write(f"- **실행 중:** {running_instances}개\n")
        report_file.write(f"- **중지됨:** {stopped_instances}개\n")
        report_file.write(f"- **기타:** {total_instances - running_instances - stopped_instances}개\n\n")
        
        # 전체 인스턴스 상세 목록
        report_file.write(f"### 인스턴스 상세 목록 (전체 {total_instances}개)\n")
        report_file.write("| 인스턴스 ID | 타입 | 상태 | VPC ID | 프라이빗 IP | 퍼블릭 IP | 태그 |\n")
        report_file.write("|-------------|------|------|--------|-------------|-----------|------|\n")
        
        for instance in ec2_data:
            instance_id = instance.get('instance_id', 'N/A')
            instance_type = instance.get('instance_type', 'N/A')
            state = instance.get('instance_state', 'N/A')
            vpc_id = instance.get('vpc_id', 'N/A')
            private_ip = instance.get('private_ip_address', 'N/A')
            public_ip = instance.get('public_ip_address', 'N/A')
            tag_name = instance.get('tags', {}).get('Name', 'N/A') if instance.get('tags') else 'N/A'
            
            report_file.write(f"| {instance_id} | {instance_type} | {state} | {vpc_id} | {private_ip} | {public_ip} | {tag_name} |\n")
        
        # 인스턴스 타입별 분포
        report_file.write("\n### 인스턴스 타입별 분포\n")
        report_file.write("| 인스턴스 타입 | 개수 | 비율 |\n")
        report_file.write("|---------------|------|------|\n")
        
        type_counter = Counter(i.get('instance_type', 'Unknown') for i in ec2_data)
        for instance_type, count in type_counter.most_common():
            percentage = round((count / total_instances) * 100, 1)
            report_file.write(f"| {instance_type} | {count} | {percentage}% |\n")
        
        # VPC별 분포
        report_file.write("\n### VPC별 인스턴스 분포\n")
        report_file.write("| VPC ID | 개수 | 비율 |\n")
        report_file.write("|--------|------|------|\n")
        
        vpc_counter = Counter(i.get('vpc_id', 'Unknown') for i in ec2_data)
        for vpc_id, count in vpc_counter.most_common():
            percentage = round((count / total_instances) * 100, 1)
            report_file.write(f"| {vpc_id} | {count} | {percentage}% |\n")

    def write_autoscaling_analysis(self, report_file, asg_data: Optional[List]) -> None:
        """Auto Scaling 분석 섹션을 작성합니다."""
        report_file.write("## ⚖️ Auto Scaling 그룹 분석\n\n")
        
        if not asg_data:
            report_file.write("Auto Scaling 그룹 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_asgs = len(asg_data)
        total_desired = sum(asg.get('desired_capacity', 0) for asg in asg_data)
        total_min = sum(asg.get('min_size', 0) for asg in asg_data)
        total_max = sum(asg.get('max_size', 0) for asg in asg_data)
        
        report_file.write("### Auto Scaling 개요\n")
        report_file.write(f"**총 Auto Scaling 그룹:** {total_asgs}개\n")
        report_file.write(f"- **총 희망 용량:** {total_desired}개\n")
        report_file.write(f"- **총 최소 용량:** {total_min}개\n")
        report_file.write(f"- **총 최대 용량:** {total_max}개\n\n")
        
        # Auto Scaling 그룹 상세 목록
        report_file.write("### Auto Scaling 그룹 상세\n")
        report_file.write("| ASG 이름 | 최소 | 희망 | 최대 | 헬스체크 | 가용영역 |\n")
        report_file.write("|----------|------|------|------|----------|----------|\n")
        
        for asg in asg_data:
            name = asg.get('name', 'N/A')
            min_size = asg.get('min_size', 0)
            desired = asg.get('desired_capacity', 0)
            max_size = asg.get('max_size', 0)
            health_check = asg.get('health_check_type', 'N/A')
            azs = ', '.join(asg.get('availability_zones', [])[:2])  # 처음 2개만 표시
            if len(asg.get('availability_zones', [])) > 2:
                azs += '...'
            
            report_file.write(f"| {name} | {min_size} | {desired} | {max_size} | {health_check} | {azs} |\n")

    def write_loadbalancer_analysis(self, report_file, alb_data: Optional[List], nlb_data: Optional[List], target_groups: Optional[List]) -> None:
        """로드 밸런서 분석 섹션을 작성합니다."""
        report_file.write("## 🔄 로드 밸런서 분석\n\n")
        
        alb_count = len(alb_data) if alb_data else 0
        nlb_count = len(nlb_data) if nlb_data else 0
        tg_count = len(target_groups) if target_groups else 0
        
        report_file.write("### 로드 밸런서 개요\n")
        report_file.write(f"**Application Load Balancer:** {alb_count}개\n")
        report_file.write(f"**Network Load Balancer:** {nlb_count}개\n")
        report_file.write(f"**타겟 그룹:** {tg_count}개\n\n")
        
        # ALB 상세 정보
        if alb_data:
            report_file.write("### Application Load Balancer 상세\n")
            report_file.write("| ALB 이름 | 스킴 | VPC ID | 상태 | DNS 이름 |\n")
            report_file.write("|----------|------|--------|------|----------|\n")
            
            for alb in alb_data:
                name = alb.get('name', 'N/A')
                scheme = alb.get('scheme', 'N/A')
                vpc_id = alb.get('vpc_id', 'N/A')
                state = alb.get('state_code', 'N/A')
                dns_name = alb.get('dns_name', 'N/A')[:50] + '...' if len(alb.get('dns_name', '')) > 50 else alb.get('dns_name', 'N/A')
                
                report_file.write(f"| {name} | {scheme} | {vpc_id} | {state} | {dns_name} |\n")
        
        # 타겟 그룹 상세 정보
        if target_groups:
            report_file.write("\n### 타겟 그룹 상세\n")
            report_file.write("| 타겟 그룹 이름 | 프로토콜 | 포트 | VPC ID | 헬스체크 경로 |\n")
            report_file.write("|----------------|----------|------|--------|---------------|\n")
            
            for tg in target_groups:
                name = tg.get('target_group_name', 'N/A')
                protocol = tg.get('protocol', 'N/A')
                port = tg.get('port', 'N/A')
                vpc_id = tg.get('vpc_id', 'N/A')
                health_path = tg.get('health_check_path', 'N/A')
                
                report_file.write(f"| {name} | {protocol} | {port} | {vpc_id} | {health_path} |\n")

    def write_container_analysis(self, report_file, eks_clusters: Optional[List], eks_nodes: Optional[List]) -> None:
        """컨테이너 서비스 분석 섹션을 작성합니다."""
        report_file.write("## 📦 컨테이너 서비스 분석\n\n")
        
        eks_cluster_count = len(eks_clusters) if eks_clusters else 0
        eks_node_count = len(eks_nodes) if eks_nodes else 0
        
        report_file.write("### 컨테이너 서비스 개요\n")
        report_file.write(f"**EKS 클러스터:** {eks_cluster_count}개\n")
        report_file.write(f"**EKS 노드 그룹:** {eks_node_count}개\n\n")
        
        # EKS 클러스터 상세 정보 (기존 데이터 사용)
        if eks_cluster_count > 0:
            # 기존에 수집된 데이터 파일에서 정보 추출
            eks_data = self.load_json_file("compute_eks_clusters.json")
            if not eks_data:
                # 대체 데이터 소스 시도
                eks_data = self.load_json_file("compute_eks_clusters.json") or []
            
            if eks_data:
                report_file.write("### EKS 클러스터 상세\n")
                report_file.write("| 클러스터 이름 | 버전 | 상태 | 엔드포인트 | 생성일 |\n")
                report_file.write("|---------------|------|------|------------|--------|\n")
                
                for cluster in eks_data:
                    name = cluster.get('name', 'N/A')
                    version = cluster.get('version', 'N/A')
                    status = cluster.get('status', 'N/A')
                    endpoint = cluster.get('endpoint', 'N/A')[:30] + '...' if len(cluster.get('endpoint', '')) > 30 else cluster.get('endpoint', 'N/A')
                    created_at = cluster.get('created_at', 'N/A')[:10] if cluster.get('created_at') else 'N/A'
                    
                    report_file.write(f"| {name} | {version} | {status} | {endpoint} | {created_at} |\n")
            else:
                report_file.write("EKS 클러스터가 감지되었지만 상세 정보를 가져올 수 없습니다.\n")

    def write_kubernetes_analysis(self, report_file) -> None:
        """Kubernetes 리소스 분석 섹션을 작성합니다."""
        report_file.write("## ☸️ Kubernetes 워크로드 분석\n\n")
        
        # K8s 리소스 데이터 로드
        namespaces = self.load_json_file("k8s_namespaces.json")
        deployments = self.load_json_file("k8s_deployments.json")
        nodes = self.load_json_file("k8s_nodes.json")
        configmaps = self.load_json_file("k8s_configmaps.json")
        daemonsets = self.load_json_file("k8s_daemonsets.json")
        
        # 기본 통계
        ns_count = len(namespaces) if namespaces else 0
        deploy_count = len(deployments) if deployments else 0
        node_count = len(nodes) if nodes else 0
        cm_count = len(configmaps) if configmaps else 0
        ds_count = len(daemonsets) if daemonsets else 0
        
        report_file.write("### Kubernetes 리소스 개요\n")
        report_file.write(f"**네임스페이스:** {ns_count}개\n")
        report_file.write(f"**디플로이먼트:** {deploy_count}개\n")
        report_file.write(f"**노드:** {node_count}개\n")
        report_file.write(f"**컨피그맵:** {cm_count}개\n")
        report_file.write(f"**데몬셋:** {ds_count}개\n\n")
        
        # 네임스페이스 상세
        if namespaces:
            report_file.write("### 네임스페이스 목록\n")
            report_file.write("| 네임스페이스 | 생성일 | 레이블 |\n")
            report_file.write("|--------------|--------|--------|\n")
            
            for ns in namespaces:
                name = ns.get('name', 'N/A')
                created = ns.get('creation_timestamp', 'N/A')[:10] if ns.get('creation_timestamp') else 'N/A'
                labels = ', '.join([f"{k}={v}" for k, v in (ns.get('labels', {}) or {}).items()][:2])
                if len(ns.get('labels', {}) or {}) > 2:
                    labels += '...'
                
                report_file.write(f"| {name} | {created} | {labels} |\n")
        
        # 디플로이먼트 상세
        if deployments:
            report_file.write("\n### 디플로이먼트 상세\n")
            report_file.write("| 디플로이먼트 | 네임스페이스 | 복제본 | 준비된 복제본 | 사용 가능한 복제본 |\n")
            report_file.write("|--------------|--------------|--------|----------------|--------------------|\n")
            
            for deploy in deployments:
                name = deploy.get('name', 'N/A')
                namespace = deploy.get('namespace', 'N/A')
                replicas = deploy.get('replicas', 'N/A')
                ready_replicas = deploy.get('ready_replicas', 'N/A')
                available_replicas = deploy.get('available_replicas', 'N/A')
                
                report_file.write(f"| {name} | {namespace} | {replicas} | {ready_replicas} | {available_replicas} |\n")
        
        # 노드 상세
        if nodes:
            report_file.write("\n### 노드 상세\n")
            report_file.write("| 노드 이름 | 생성일 | 레이블 (일부) |\n")
            report_file.write("|-----------|--------|---------------|\n")
            
            for node in nodes:
                name = node.get('name', 'N/A')
                created = node.get('creation_timestamp', 'N/A')[:10] if node.get('creation_timestamp') else 'N/A'
                labels = ', '.join([f"{k}={v}" for k, v in (node.get('labels', {}) or {}).items() if not k.startswith('kubernetes.io')][:2])
                if not labels:
                    labels = 'N/A'
                
                report_file.write(f"| {name} | {created} | {labels} |\n")

    def write_serverless_analysis(self, report_file) -> None:
        """서버리스 컴퓨팅 분석 섹션을 작성합니다."""
        report_file.write("## 🚀 서버리스 컴퓨팅 분석\n\n")
        
        # Lambda 함수 데이터 로드 시도
        lambda_functions = self.load_json_file("compute_lambda_functions.json")
        
        if lambda_functions:
            lambda_count = len(lambda_functions)
            report_file.write("### Lambda 함수 개요\n")
            report_file.write(f"**총 Lambda 함수:** {lambda_count}개\n\n")
            
            # 런타임별 분포
            runtime_counter = Counter(func.get('runtime', 'Unknown') for func in lambda_functions)
            report_file.write("### 런타임별 분포\n")
            report_file.write("| 런타임 | 개수 | 비율 |\n")
            report_file.write("|--------|------|------|\n")
            
            for runtime, count in runtime_counter.most_common():
                percentage = round((count / lambda_count) * 100, 1)
                report_file.write(f"| {runtime} | {count} | {percentage}% |\n")
            
            # Lambda 함수 상세 목록
            report_file.write("\n### Lambda 함수 상세\n")
            report_file.write("| 함수 이름 | 런타임 | 메모리 | 타임아웃 | 마지막 수정일 |\n")
            report_file.write("|-----------|---------|--------|----------|---------------|\n")
            
            for func in lambda_functions:
                name = func.get('name', 'N/A')
                runtime = func.get('runtime', 'N/A')
                memory = func.get('memory_size', 'N/A')
                timeout = func.get('timeout', 'N/A')
                last_modified = func.get('last_modified', 'N/A')[:10] if func.get('last_modified') else 'N/A'
                
                report_file.write(f"| {name} | {runtime} | {memory}MB | {timeout}s | {last_modified} |\n")
        else:
            report_file.write("Lambda 함수 데이터를 찾을 수 없습니다.\n\n")

    def write_recommendations(self, report_file) -> None:
        """컴퓨팅 최적화 권장사항을 작성합니다."""
        report_file.write("## 📋 컴퓨팅 최적화 권장사항\n\n")
        
        report_file.write("### 🔴 높은 우선순위\n")
        report_file.write("1. **인스턴스 타입 최적화**: 워크로드에 맞는 적절한 인스턴스 타입 선택\n")
        report_file.write("2. **Auto Scaling 정책 검토**: 트래픽 패턴에 맞는 스케일링 정책 설정\n")
        report_file.write("3. **미사용 리소스 정리**: 중지된 인스턴스 및 미사용 로드 밸런서 제거\n\n")
        
        report_file.write("### 🟡 중간 우선순위\n")
        report_file.write("1. **스팟 인스턴스 활용**: 적절한 워크로드에 스팟 인스턴스 도입\n")
        report_file.write("2. **컨테이너화 검토**: 마이크로서비스 아키텍처로 전환 고려\n")
        report_file.write("3. **서버리스 전환**: 이벤트 기반 워크로드의 Lambda 전환\n\n")
        
        report_file.write("### 🟢 낮은 우선순위\n")
        report_file.write("1. **예약 인스턴스 구매**: 장기 실행 워크로드에 대한 RI 구매\n")
        report_file.write("2. **Kubernetes 최적화**: 리소스 요청/제한 설정 최적화\n")
        report_file.write("3. **모니터링 강화**: CloudWatch 메트릭 및 알람 설정\n\n")

    def generate_report(self):
        """확장된 컴퓨팅 분석 보고서를 생성합니다."""
        print("💻 확장된 Compute Analysis 보고서 생성 중...")
        
        # 데이터 파일 로드
        ec2_data = self.load_json_file("compute_ec2_instances.json")
        asg_data = self.load_json_file("compute_asg_detailed.json")
        alb_data = self.load_json_file("compute_alb_detailed.json")
        nlb_data = self.load_json_file("compute_nlb_detailed.json")
        target_groups = self.load_json_file("compute_target_groups.json")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "03-compute-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 컴퓨팅 리소스 분석\n\n")
                
                # 각 섹션 작성
                self.write_ec2_analysis(report_file, ec2_data)
                self.write_autoscaling_analysis(report_file, asg_data)
                self.write_loadbalancer_analysis(report_file, alb_data, nlb_data, target_groups)
                self.write_container_analysis(report_file, None, None)  # EKS 데이터는 별도 처리
                self.write_kubernetes_analysis(report_file)
                self.write_serverless_analysis(report_file)
                self.write_recommendations(report_file)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*컴퓨팅 리소스 분석 완료*\n")
            
            print("✅ 확장된 Compute Analysis 생성 완료: 03-compute-analysis.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="확장된 컴퓨팅 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = ExtendedComputeReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
