#!/usr/bin/env python3
"""
네트워킹 분석 보고서 생성 스크립트 (Python 버전)
Shell 스크립트와 동일한 기능 및 출력 형식 제공
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class NetworkingReportGenerator:
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

    def write_header(self):
        """보고서 헤더 작성"""
        content = """# 네트워킹 리소스 분석

## 📊 네트워킹 개요

### VPC 구성 현황
"""
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def write_vpc_section(self, report_file):
        """VPC 섹션 생성"""
        vpc_data = self.load_json_file("networking_vpc.json")
        
        if vpc_data:
            vpc_count = len(vpc_data)
            default_vpc_count = len([vpc for vpc in vpc_data if vpc.get('is_default', False)])
            
            report_file.write(f"**총 VPC 수:** {vpc_count}개 (기본 VPC: {default_vpc_count}개)\n\n")
            report_file.write("| VPC ID | CIDR Block | 상태 | 기본 VPC | 태그 |\n")
            report_file.write("|--------|------------|------|----------|------|\n")
            
            for vpc in vpc_data:
                vpc_id = vpc.get('vpc_id', 'N/A')
                cidr_block = vpc.get('cidr_block', 'N/A')
                state = vpc.get('state', 'N/A')
                is_default = vpc.get('is_default', False)
                tag_name = vpc.get('tags', {}).get('Name', 'N/A') if vpc.get('tags') else 'N/A'
                
                report_file.write(f"| {vpc_id} | {cidr_block} | {state} | {is_default} | {tag_name} |\n")
        else:
            report_file.write("VPC 데이터를 찾을 수 없습니다.\n")

    def write_security_groups_section(self, report_file):
        """보안 그룹 섹션 생성"""
        report_file.write("\n## 🔒 보안 그룹 분석\n\n### 보안 그룹 현황\n")
        
        sg_data = self.load_json_file("security_groups.json")
        
        if sg_data:
            sg_count = len(sg_data)
            report_file.write(f"**총 보안 그룹 수:** {sg_count}개\n\n")
            report_file.write("| 그룹 ID | 그룹명 | VPC ID | 설명 |\n")
            report_file.write("|---------|--------|--------|------|\n")
            
            # 전체 보안 그룹 표시
            for sg in sg_data:
                group_id = sg.get('group_id', 'N/A')
                group_name = sg.get('group_name', 'N/A')
                vpc_id = sg.get('vpc_id', 'N/A')
                description = sg.get('description', '설명 없음')
                
                report_file.write(f"| {group_id} | {group_name} | {vpc_id} | {description} |\n")
            
            # VPC별 보안 그룹 분포
            report_file.write("\n### VPC별 보안 그룹 분포\n")
            report_file.write("| VPC ID | 보안 그룹 수 |\n")
            report_file.write("|--------|--------------||\n")
            
            # VPC별 그룹화
            vpc_groups = {}
            for sg in sg_data:
                vpc_id = sg.get('vpc_id', 'N/A')
                vpc_groups[vpc_id] = vpc_groups.get(vpc_id, 0) + 1
            
            for vpc_id, count in vpc_groups.items():
                report_file.write(f"| {vpc_id} | {count} |\n")
        else:
            report_file.write("보안 그룹 데이터를 찾을 수 없습니다.\n")

    def write_routing_tables_section(self, report_file):
        """라우팅 테이블 섹션 생성"""
        report_file.write("\n## 🌐 라우팅 테이블 분석\n\n### 라우팅 테이블 현황\n")
        
        rt_data = self.load_json_file("networking_route_tables.json")
        
        if rt_data:
            rt_count = len(rt_data)
            main_rt_count = len([rt for rt in rt_data if any(
                assoc.get('main', False) for assoc in rt.get('associations', [])
            )])
            
            report_file.write(f"**총 라우팅 테이블 수:** {rt_count}개 (메인 테이블: {main_rt_count}개)\n\n")
            report_file.write("| 라우팅 테이블 ID | VPC ID | 메인 테이블 | 연결된 서브넷 수 |\n")
            report_file.write("|------------------|--------|-------------|------------------|\n")
            
            # 전체 라우팅 테이블 표시
            for rt in rt_data:
                route_table_id = rt.get('route_table_id', 'N/A')
                vpc_id = rt.get('vpc_id', 'N/A')
                is_main = any(assoc.get('main', False) for assoc in rt.get('associations', []))
                subnet_count = len(rt.get('associations', []))
                
                report_file.write(f"| {route_table_id} | {vpc_id} | {is_main} | {subnet_count} |\n")
        else:
            report_file.write("라우팅 테이블 데이터를 찾을 수 없습니다.\n")

    def write_gateways_section(self, report_file):
        """네트워크 게이트웨이 섹션 생성"""
        report_file.write("\n## 🔌 네트워크 게이트웨이\n\n### 인터넷 게이트웨이\n")
        
        igw_data = self.load_json_file("networking_igw.json")
        
        if igw_data:
            igw_count = len(igw_data)
            report_file.write(f"**총 인터넷 게이트웨이 수:** {igw_count}개\n\n")
            report_file.write("| IGW ID | 상태 | 연결된 VPC |\n")
            report_file.write("|--------|------|------------|\n")
            
            for igw in igw_data:
                igw_id = igw.get('internet_gateway_id', 'N/A')
                # attachments에서 상태와 VPC ID 추출
                attachments = igw.get('attachments', [])
                if attachments:
                    state = attachments[0].get('state', 'N/A')
                    vpc_id = attachments[0].get('vpc_id', '없음')
                else:
                    state = 'detached'
                    vpc_id = '없음'
                
                report_file.write(f"| {igw_id} | {state} | {vpc_id} |\n")
        else:
            report_file.write("인터넷 게이트웨이 데이터를 찾을 수 없습니다.\n")

    def write_elastic_ip_section(self, report_file):
        """Elastic IP 섹션 생성"""
        report_file.write("\n### Elastic IP 주소\n")
        
        eip_data = self.load_json_file("networking_eip.json")
        
        if eip_data:
            eip_count = len(eip_data)
            associated_eip = len([eip for eip in eip_data if eip.get('association_id')])
            
            report_file.write(f"**총 Elastic IP:** {eip_count}개 (연결됨: {associated_eip}개)\n\n")
            report_file.write("| 할당 ID | 공인 IP | 연결된 인스턴스 | 도메인 |\n")
            report_file.write("|---------|---------|-----------------|--------|\n")
            
            for eip in eip_data:
                allocation_id = eip.get('allocation_id', 'N/A')
                public_ip = eip.get('public_ip', 'N/A')
                instance_id = eip.get('instance_id', '없음')
                domain = eip.get('domain', 'N/A')
                
                report_file.write(f"| {allocation_id} | {public_ip} | {instance_id} | {domain} |\n")
        else:
            report_file.write("Elastic IP 데이터를 찾을 수 없습니다.\n")

    def write_network_acl_section(self, report_file):
        """네트워크 ACL 섹션 생성"""
        report_file.write("\n## 🛡️ 네트워크 ACL 분석\n\n### Network ACL 현황\n")
        
        acl_data = self.load_json_file("networking_acl.json")
        
        if acl_data:
            acl_count = len(acl_data)
            default_acl_count = len([acl for acl in acl_data if acl.get('is_default', False)])
            
            report_file.write(f"**총 Network ACL:** {acl_count}개 (기본 ACL: {default_acl_count}개)\n\n")
            report_file.write("| ACL ID | VPC ID | 기본 ACL | 연결된 서브넷 수 |\n")
            report_file.write("|--------|--------|----------|------------------|\n")
            
            # 전체 Network ACL 표시
            for acl in acl_data:
                network_acl_id = acl.get('network_acl_id', 'N/A')
                vpc_id = acl.get('vpc_id', 'N/A')
                is_default = acl.get('is_default', False)
                subnet_count = len(acl.get('associations', []))
                
                report_file.write(f"| {network_acl_id} | {vpc_id} | {is_default} | {subnet_count} |\n")
        else:
            report_file.write("Network ACL 데이터를 찾을 수 없습니다.\n")

    def write_recommendations_section(self, report_file):
        """권장사항 섹션 생성"""
        content = """
## 📋 네트워킹 권장사항

### 🔴 높은 우선순위
1. **보안 그룹 규칙 검토**: 0.0.0.0/0 허용 규칙 최소화
2. **VPC Flow Logs 활성화**: 네트워크 트래픽 모니터링 강화
3. **미사용 Elastic IP 정리**: 연결되지 않은 EIP 해제

### 🟡 중간 우선순위
1. **VPC 엔드포인트 구성**: AWS 서비스 접근 최적화
2. **서브넷 구성 최적화**: 퍼블릭/프라이빗 서브넷 적절한 분리
3. **라우팅 테이블 정리**: 불필요한 라우팅 규칙 제거

### 🟢 낮은 우선순위
1. **Transit Gateway 검토**: 복잡한 네트워크 연결 시 고려
2. **VPC 피어링 최적화**: 불필요한 피어링 연결 정리
3. **DNS 설정 최적화**: Route 53 Private Hosted Zone 활용

## 📊 네트워킹 보안 점검

### 보안 그룹 분석 결과
"""
        report_file.write(content)

    def write_security_analysis(self, report_file):
        """보안 분석 섹션 생성"""
        sg_data = self.load_json_file("security_groups.json")
        
        if sg_data:
            # 0.0.0.0/0 허용 규칙 확인
            open_rules_count = 0
            ssh_open_count = 0
            rdp_open_count = 0
            
            for sg in sg_data:
                ip_permissions = sg.get('ip_permissions', [])
                for perm in ip_permissions:
                    ip_ranges = perm.get('ip_ranges', [])
                    for ip_range in ip_ranges:
                        if ip_range.get('cidr_ip') == '0.0.0.0/0':
                            open_rules_count += 1
                            from_port = perm.get('from_port')
                            if from_port == 22:
                                ssh_open_count += 1
                            elif from_port == 3389:
                                rdp_open_count += 1
            
            report_file.write(f"- **전체 오픈 규칙 (0.0.0.0/0)**: {open_rules_count}개 규칙에서 발견\n")
            report_file.write(f"- **SSH 포트 22 전체 오픈**: {ssh_open_count}개 보안 그룹\n")
            report_file.write(f"- **RDP 포트 3389 전체 오픈**: {rdp_open_count}개 보안 그룹\n")
        else:
            report_file.write("- 보안 그룹 데이터 분석 불가\n")

    def write_cost_optimization_section(self, report_file):
        """비용 최적화 섹션 생성"""
        report_file.write("\n## 💰 네트워킹 비용 최적화\n\n### 비용 절감 기회\n")
        
        eip_data = self.load_json_file("networking_eip.json")
        
        if eip_data:
            unassociated_eip = len([eip for eip in eip_data if not eip.get('association_id')])
            if unassociated_eip > 0:
                estimated_cost = unassociated_eip * 3.6  # 월 $3.6 per EIP
                report_file.write(f"1. **미사용 Elastic IP**: {unassociated_eip}개 (월 ${estimated_cost:.1f} 절감 가능)\n")
        
        report_file.write("2. **NAT Gateway 최적화**: 불필요한 NAT Gateway 제거 검토\n")
        report_file.write("3. **데이터 전송 비용**: 같은 AZ 내 통신 최대화\n")

    def generate_report(self):
        """전체 보고서 생성"""
        print("🌐 Networking Analysis 보고서 생성 중...")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "02-networking-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 네트워킹 리소스 분석\n\n")
                report_file.write("## 📊 네트워킹 개요\n\n### VPC 구성 현황\n")
                
                # 각 섹션 순차적으로 생성
                self.write_vpc_section(report_file)
                self.write_security_groups_section(report_file)
                self.write_routing_tables_section(report_file)
                self.write_gateways_section(report_file)
                self.write_elastic_ip_section(report_file)
                self.write_network_acl_section(report_file)
                self.write_recommendations_section(report_file)
                self.write_security_analysis(report_file)
                self.write_cost_optimization_section(report_file)
                
                # 마무리
                report_file.write("\n---\n*네트워킹 분석 완료*\n")
            
            print("✅ Networking Analysis 생성 완료: 02-networking-analysis.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="네트워킹 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = NetworkingReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
