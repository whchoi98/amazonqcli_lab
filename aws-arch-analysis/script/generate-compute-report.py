#!/usr/bin/env python3
"""
확장된 컴퓨팅 분석 보고서 생성 스크립트 (Python 버전)
모든 컴퓨팅 리소스와 Kubernetes 워크로드 포함
Enhanced 권장사항 기능 추가
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime

# Enhanced 권장사항 모듈 import
sys.path.append(str(Path(__file__).parent))
from enhanced_recommendations import ComputeRecommendations

class ExtendedComputeReportGenerator(ComputeRecommendations):
    def __init__(self, report_dir: str = None):
        # 스크립트의 실제 위치를 기준으로 경로 설정
        if report_dir is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent
            report_dir = str(project_root / "aws-arch-analysis" / "report")
        super().__init__()  # Enhanced 권장사항 초기화
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
        """Enhanced 컴퓨팅 최적화 권장사항을 작성합니다."""
        
        # 컴퓨팅 데이터 로드 및 분석
        data_dict = {
            'compute_ec2_instances': self.load_json_file("compute_ec2_instances.json"),
            'ec2_reserved_instances': self.load_json_file("compute_ec2_reserved_instances.json"),
            'compute_asg_detailed': self.load_json_file("compute_asg_detailed.json"),
            'lambda_functions': self.load_json_file("iac_lambda_functions.json"),
            'eks_clusters': self.load_json_file("compute_eks_clusters.json")
        }
        
        # Enhanced 권장사항 생성
        self.analyze_compute_data(data_dict)
        
        # Enhanced 권장사항 섹션 작성
        self.write_enhanced_recommendations_section(report_file, "컴퓨팅 최적화 권장사항")

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
                report_file.write("# 💻 컴퓨팅 리소스 종합 분석\n\n")
                report_file.write(f"> **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
                report_file.write(f"> **분석 대상**: AWS 계정 내 모든 컴퓨팅 리소스  \n")
                report_file.write(f"> **분석 리전**: ap-northeast-2 (서울)\n\n")
                report_file.write("이 보고서는 AWS 계정의 컴퓨팅 인프라에 대한 종합적인 분석을 제공하며, EC2 인스턴스, Lambda 함수, ECS/EKS 클러스터, Auto Scaling 그룹 등의 구성 상태와 성능 최적화 방안을 평가합니다.\n\n")
                
                # 각 섹션 작성
                self.write_ec2_analysis(report_file, ec2_data)
                self.write_autoscaling_analysis(report_file, asg_data)
                self.write_loadbalancer_analysis(report_file, alb_data, nlb_data, target_groups)
                self.write_container_analysis(report_file, None, None)  # EKS 데이터는 별도 처리
                self.write_kubernetes_analysis(report_file)
                self.write_serverless_analysis(report_file)
                self.write_recommendations(report_file)
                
                # 마무리 섹션 추가
                self.write_footer_section(report_file)
            
            print("✅ 확장된 Compute Analysis 생성 완료: 03-compute-analysis.md")
            
            # Enhanced 권장사항 통계 출력
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

📅 분석 완료 시간: {current_time} 🔄 다음 컴퓨팅 검토 권장 주기: 월 1회
""")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="확장된 컴퓨팅 분석 보고서 생성")
    # 스크립트의 실제 위치를 기준으로 기본 경로 설정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    default_report_dir = str(project_root / "aws-arch-analysis" / "report")
    
    parser.add_argument("--report-dir", default=default_report_dir, help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = ExtendedComputeReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
