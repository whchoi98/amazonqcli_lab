#!/usr/bin/env python3
"""
네트워킹 분석 보고서 생성 스크립트 (Python 버전)
Shell 스크립트와 동일한 기능 및 출력 형식 제공
Enhanced 권장사항 기능 추가
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Enhanced 권장사항 모듈 import
sys.path.append(str(Path(__file__).parent))
from enhanced_recommendations import NetworkingRecommendations

class NetworkingReportGenerator(NetworkingRecommendations):
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

    def write_tgw_section(self, report_file):
        """Transit Gateway 섹션 생성"""
        report_file.write("\n## 🌐 Transit Gateway 분석\n\n")
        
        # Transit Gateway 기본 정보
        tgw_data = self.load_json_file("networking_transit_gateway.json")
        
        if tgw_data:
            tgw_count = len(tgw_data)
            report_file.write(f"### Transit Gateway 현황\n")
            report_file.write(f"**총 Transit Gateway 수:** {tgw_count}개\n\n")
            
            report_file.write("| TGW ID | 상태 | 설명 | 기본 라우팅 테이블 연결 | 기본 라우팅 테이블 전파 | 태그 |\n")
            report_file.write("|--------|------|------|------------------------|------------------------|------|\n")
            
            for tgw in tgw_data:
                tgw_id = tgw.get('transit_gateway_id', 'N/A')
                state = tgw.get('state', 'N/A')
                description = tgw.get('description', '설명 없음')
                default_route_table_association = tgw.get('default_route_table_association', 'N/A')
                default_route_table_propagation = tgw.get('default_route_table_propagation', 'N/A')
                tag_name = tgw.get('tags', {}).get('Name', 'N/A') if tgw.get('tags') else 'N/A'
                
                report_file.write(f"| {tgw_id} | {state} | {description} | {default_route_table_association} | {default_route_table_propagation} | {tag_name} |\n")
        else:
            report_file.write("### Transit Gateway 현황\n")
            report_file.write("Transit Gateway가 구성되지 않았습니다.\n\n")
        
        # TGW VPC Attachments
        tgw_attachments = self.load_json_file("networking_tgw_vpc_attachments.json")
        
        if tgw_attachments:
            attachment_count = len(tgw_attachments)
            report_file.write(f"### Transit Gateway VPC 연결\n")
            report_file.write(f"**총 VPC 연결 수:** {attachment_count}개\n\n")
            
            report_file.write("| 연결 ID | TGW ID | VPC ID | 상태 | 서브넷 ID | 태그 |\n")
            report_file.write("|---------|--------|--------|------|-----------|------|\n")
            
            for attachment in tgw_attachments:
                attachment_id = attachment.get('transit_gateway_attachment_id', 'N/A')
                tgw_id = attachment.get('transit_gateway_id', 'N/A')
                vpc_id = attachment.get('vpc_id', 'N/A')
                state = attachment.get('state', 'N/A')
                subnet_ids = ', '.join(attachment.get('subnet_ids', [])) if attachment.get('subnet_ids') else 'N/A'
                tag_name = attachment.get('tags', {}).get('Name', 'N/A') if attachment.get('tags') else 'N/A'
                
                report_file.write(f"| {attachment_id} | {tgw_id} | {vpc_id} | {state} | {subnet_ids} | {tag_name} |\n")
        else:
            report_file.write("### Transit Gateway VPC 연결\n")
            report_file.write("VPC 연결이 구성되지 않았습니다.\n\n")
        
        # TGW Route Tables
        tgw_route_tables = self.load_json_file("networking_tgw_route_tables.json")
        
        if tgw_route_tables:
            route_table_count = len(tgw_route_tables)
            report_file.write(f"### Transit Gateway 라우팅 테이블\n")
            report_file.write(f"**총 라우팅 테이블 수:** {route_table_count}개\n\n")
            
            report_file.write("| 라우팅 테이블 ID | TGW ID | 기본 연결 테이블 | 기본 전파 테이블 | 상태 | 태그 |\n")
            report_file.write("|------------------|--------|------------------|------------------|------|------|\n")
            
            for rt in tgw_route_tables:
                rt_id = rt.get('transit_gateway_route_table_id', 'N/A')
                tgw_id = rt.get('transit_gateway_id', 'N/A')
                default_association_route_table = rt.get('default_association_route_table', False)
                default_propagation_route_table = rt.get('default_propagation_route_table', False)
                state = rt.get('state', 'N/A')
                tag_name = rt.get('tags', {}).get('Name', 'N/A') if rt.get('tags') else 'N/A'
                
                report_file.write(f"| {rt_id} | {tgw_id} | {default_association_route_table} | {default_propagation_route_table} | {state} | {tag_name} |\n")
        else:
            report_file.write("### Transit Gateway 라우팅 테이블\n")
            report_file.write("라우팅 테이블이 구성되지 않았습니다.\n\n")

    def write_vpc_peering_section(self, report_file):
        """VPC Peering 섹션 생성"""
        report_file.write("\n## 🔗 VPC Peering 분석\n\n")
        
        peering_data = self.load_json_file("networking_vpc_peering.json")
        
        if peering_data:
            peering_count = len(peering_data)
            active_count = len([p for p in peering_data if p.get('status_code') == 'active'])
            
            report_file.write(f"### VPC Peering 현황\n")
            report_file.write(f"**총 VPC Peering 연결 수:** {peering_count}개 (활성: {active_count}개)\n\n")
            
            report_file.write("| Peering ID | 상태 | 요청자 VPC | 수락자 VPC | 요청자 리전 | 수락자 리전 | 태그 |\n")
            report_file.write("|------------|------|------------|------------|-------------|-------------|------|\n")
            
            for peering in peering_data:
                peering_id = peering.get('id', 'N/A')
                status = peering.get('status_code', 'N/A')
                requester_vpc = peering.get('requester_vpc_id', 'N/A')
                accepter_vpc = peering.get('accepter_vpc_id', 'N/A')
                requester_region = peering.get('requester_region', 'N/A')
                accepter_region = peering.get('accepter_region', 'N/A')
                tag_name = peering.get('tags', {}).get('Name', 'N/A') if peering.get('tags') else 'N/A'
                
                report_file.write(f"| {peering_id} | {status} | {requester_vpc} | {accepter_vpc} | {requester_region} | {accepter_region} | {tag_name} |\n")
            
            # 상태별 분석
            report_file.write("\n### VPC Peering 상태 분석\n")
            status_counts = {}
            for peering in peering_data:
                status = peering.get('status_code', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            report_file.write("| 상태 | 개수 | 설명 |\n")
            report_file.write("|------|------|------|\n")
            
            status_descriptions = {
                'active': '활성 상태 - 정상적으로 트래픽 전송 가능',
                'pending-acceptance': '수락 대기 중 - 상대방의 수락 필요',
                'rejected': '거부됨 - 연결 요청이 거부됨',
                'expired': '만료됨 - 수락 기한이 지남',
                'failed': '실패 - 연결 생성 실패',
                'deleted': '삭제됨 - 연결이 삭제됨'
            }
            
            for status, count in status_counts.items():
                description = status_descriptions.get(status, '알 수 없는 상태')
                report_file.write(f"| {status} | {count} | {description} |\n")
                
        else:
            report_file.write("### VPC Peering 현황\n")
            report_file.write("VPC Peering 연결이 구성되지 않았습니다.\n\n")

    def write_recommendations_section(self, report_file):
        """Enhanced 권장사항 섹션 생성"""
        
        # 네트워킹 데이터 로드 및 분석
        data_dict = {
            'security_groups': self.load_json_file("security_groups.json"),
            'security_groups_ingress': self.load_json_file("security_groups_ingress_rules.json"),
            'flow_logs': self.load_json_file("networking_flow_logs.json"),
            'vpc': self.load_json_file("networking_vpc.json"),
            'elastic_ips': self.load_json_file("networking_eip.json"),
            'nat': self.load_json_file("networking_nat.json"),
            'vpc_endpoints': self.load_json_file("networking_vpc_endpoints.json"),
            'transit_gateway': self.load_json_file("networking_transit_gateway.json"),
            'tgw_vpc_attachments': self.load_json_file("networking_tgw_vpc_attachments.json"),
            'vpc_peering': self.load_json_file("networking_vpc_peering.json")
        }
        
        # Enhanced 권장사항 생성
        self.analyze_networking_data(data_dict)
        
        # Enhanced 권장사항 섹션 작성
        self.write_enhanced_recommendations_section(report_file, "네트워킹 권장사항")
        
        # 기존 보안 분석 결과도 유지
        report_file.write("## 📊 네트워킹 보안 점검\n\n")
        report_file.write("### 보안 그룹 분석 결과\n")
        
        # 보안 그룹 상세 분석 (기존 로직 유지)
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
                            from_port = perm.get('from_port', 0)
                            if from_port == 22:
                                ssh_open_count += 1
                            elif from_port == 3389:
                                rdp_open_count += 1
            
            report_file.write(f"- **전체 개방 규칙**: {open_rules_count}개\n")
            report_file.write(f"- **SSH 전체 개방**: {ssh_open_count}개\n")
            report_file.write(f"- **RDP 전체 개방**: {rdp_open_count}개\n\n")
            
            if open_rules_count > 0:
                report_file.write("⚠️ **보안 주의**: 전체 인터넷에서 접근 가능한 규칙이 발견되었습니다.\n\n")
        else:
            report_file.write("보안 그룹 데이터를 분석할 수 없습니다.\n\n")

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
                report_file.write(f"> **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
                report_file.write(f"> **분석 대상**: AWS 계정 내 모든 네트워킹 리소스  \n")
                report_file.write(f"> **분석 리전**: ap-northeast-2 (서울)\n\n")
                report_file.write("이 보고서는 AWS 계정의 네트워킹 인프라에 대한 종합적인 분석을 제공하며, VPC, 서브넷, 보안 그룹, 라우팅 테이블, NAT Gateway 등의 구성 상태와 보안 최적화 방안을 평가합니다.\n\n")
                report_file.write("## 📊 네트워킹 개요\n\n### VPC 구성 현황\n")
                
                # 각 섹션 순차적으로 생성
                self.write_vpc_section(report_file)
                self.write_security_groups_section(report_file)
                self.write_routing_tables_section(report_file)
                self.write_gateways_section(report_file)
                self.write_elastic_ip_section(report_file)
                self.write_network_acl_section(report_file)
                self.write_tgw_section(report_file)
                self.write_vpc_peering_section(report_file)
                self.write_recommendations_section(report_file)
                self.write_security_analysis(report_file)
                self.write_footer_section(report_file)
        
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False
        
        return True

    def write_footer_section(self, report_file):
        """보고서 마무리 섹션 추가"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_file.write(f"""
## 📞 추가 지원

이 보고서에 대한 질문이나 추가 분석이 필요한 경우:
- AWS Support 케이스 생성
- AWS Well-Architected Review 수행
- AWS Professional Services 문의

📅 분석 완료 시간: {current_time} 🔄 다음 네트워킹 검토 권장 주기: 월 1회
""")
        
        print("✅ Networking Analysis 생성 완료: 02-networking-analysis.md")
        
        # Enhanced 권장사항 통계 출력
        stats = self.get_recommendations_summary()
        if stats['total'] > 0:
            print(f"📋 Enhanced 권장사항 통계:")
            print(f"   - 높은 우선순위: {stats['high_priority']}개")
            print(f"   - 중간 우선순위: {stats['medium_priority']}개")
            print(f"   - 낮은 우선순위: {stats['low_priority']}개")
            print(f"   - 총 권장사항: {stats['total']}개")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="네트워킹 분석 보고서 생성")
    # 스크립트의 실제 위치를 기준으로 기본 경로 설정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    default_report_dir = str(project_root / "aws-arch-analysis" / "report")
    
    parser.add_argument("--report-dir", default=default_report_dir, help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = NetworkingReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
