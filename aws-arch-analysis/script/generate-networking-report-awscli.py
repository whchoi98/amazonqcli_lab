#!/usr/bin/env python3
"""
AWS CLI 데이터 기반 네트워킹 분석 보고서 생성 스크립트
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def load_json_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """JSON 파일을 로드하고 파싱합니다."""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # AWS CLI는 직접 배열을 반환하므로 그대로 사용
                return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load {file_path}: {e}")
    return []

def write_vpc_analysis(report_file, vpc_data: Optional[List]) -> None:
    """VPC 분석 섹션을 작성합니다."""
    report_file.write("## 🌐 VPC (Virtual Private Cloud) 현황\n\n")
    
    if not vpc_data:
        report_file.write("VPC 데이터를 찾을 수 없습니다.\n\n")
        return
    
    vpc_count = len(vpc_data)
    report_file.write(f"**총 VPC 수**: {vpc_count}개\n\n")
    
    if vpc_count > 0:
        report_file.write("### VPC 상세 정보\n")
        report_file.write("| VPC ID | CIDR Block | 상태 | 기본 VPC | 이름 |\n")
        report_file.write("|--------|------------|------|----------|------|\n")
        
        for vpc in vpc_data:
            vpc_id = vpc.get('vpc_id', 'N/A')
            cidr_block = vpc.get('cidr_block', 'N/A')
            state = vpc.get('state', 'N/A')
            is_default = '예' if vpc.get('is_default', False) else '아니오'
            
            # 태그에서 이름 추출
            name = 'N/A'
            if vpc.get('tags'):
                for tag in vpc['tags']:
                    if tag.get('Key') == 'Name':
                        name = tag.get('Value', 'N/A')
                        break
            
            report_file.write(f"| {vpc_id} | {cidr_block} | {state} | {is_default} | {name} |\n")
    
    report_file.write("\n")

def write_subnet_analysis(report_file, subnet_data: Optional[List]) -> None:
    """서브넷 분석 섹션을 작성합니다."""
    report_file.write("## 🏗️ 서브넷 현황\n\n")
    
    if not subnet_data:
        report_file.write("서브넷 데이터를 찾을 수 없습니다.\n\n")
        return
    
    subnet_count = len(subnet_data)
    public_subnets = [s for s in subnet_data if s.get('map_public_ip_on_launch', False)]
    private_subnets = [s for s in subnet_data if not s.get('map_public_ip_on_launch', False)]
    
    report_file.write(f"**총 서브넷 수**: {subnet_count}개\n")
    report_file.write(f"- **퍼블릭 서브넷**: {len(public_subnets)}개\n")
    report_file.write(f"- **프라이빗 서브넷**: {len(private_subnets)}개\n\n")
    
    if subnet_count > 0:
        report_file.write("### 서브넷 상세 정보\n")
        report_file.write("| 서브넷 ID | VPC ID | CIDR Block | AZ | 타입 | 상태 |\n")
        report_file.write("|-----------|--------|------------|----|----- |------|\n")
        
        for subnet in subnet_data[:10]:  # 최대 10개만 표시
            subnet_id = subnet.get('subnet_id', 'N/A')
            vpc_id = subnet.get('vpc_id', 'N/A')
            cidr_block = subnet.get('cidr_block', 'N/A')
            az = subnet.get('availability_zone', 'N/A')
            subnet_type = '퍼블릭' if subnet.get('map_public_ip_on_launch', False) else '프라이빗'
            state = subnet.get('state', 'N/A')
            
            report_file.write(f"| {subnet_id} | {vpc_id} | {cidr_block} | {az} | {subnet_type} | {state} |\n")
        
        if subnet_count > 10:
            report_file.write(f"... 및 {subnet_count - 10}개 추가 서브넷\n")
    
    report_file.write("\n")

def write_security_group_analysis(report_file, sg_data: Optional[List]) -> None:
    """보안 그룹 분석 섹션을 작성합니다."""
    report_file.write("## 🔒 보안 그룹 현황\n\n")
    
    if not sg_data:
        report_file.write("보안 그룹 데이터를 찾을 수 없습니다.\n\n")
        return
    
    sg_count = len(sg_data)
    report_file.write(f"**총 보안 그룹 수**: {sg_count}개\n\n")
    
    if sg_count > 0:
        report_file.write("### 보안 그룹 상세 정보\n")
        report_file.write("| 그룹 ID | 그룹 이름 | VPC ID | 설명 | 인바운드 규칙 | 아웃바운드 규칙 |\n")
        report_file.write("|---------|-----------|--------|------|---------------|------------------|\n")
        
        for sg in sg_data[:10]:  # 최대 10개만 표시
            group_id = sg.get('group_id', 'N/A')
            group_name = sg.get('group_name', 'N/A')
            vpc_id = sg.get('vpc_id', 'N/A')
            description = sg.get('description', 'N/A')[:30] + '...' if len(sg.get('description', '')) > 30 else sg.get('description', 'N/A')
            inbound_rules = len(sg.get('ip_permissions', []))
            outbound_rules = len(sg.get('ip_permissions_egress', []))
            
            report_file.write(f"| {group_id} | {group_name} | {vpc_id} | {description} | {inbound_rules} | {outbound_rules} |\n")
        
        if sg_count > 10:
            report_file.write(f"... 및 {sg_count - 10}개 추가 보안 그룹\n")
    
    report_file.write("\n")

def write_route_table_analysis(report_file, rt_data: Optional[List]) -> None:
    """라우팅 테이블 분석 섹션을 작성합니다."""
    report_file.write("## 🛣️ 라우팅 테이블 현황\n\n")
    
    if not rt_data:
        report_file.write("라우팅 테이블 데이터를 찾을 수 없습니다.\n\n")
        return
    
    rt_count = len(rt_data)
    report_file.write(f"**총 라우팅 테이블 수**: {rt_count}개\n\n")
    
    if rt_count > 0:
        report_file.write("### 라우팅 테이블 상세 정보\n")
        report_file.write("| 라우팅 테이블 ID | VPC ID | 라우트 수 | 연결된 서브넷 수 |\n")
        report_file.write("|------------------|--------|-----------|------------------|\n")
        
        for rt in rt_data:
            rt_id = rt.get('route_table_id', 'N/A')
            vpc_id = rt.get('vpc_id', 'N/A')
            routes_count = len(rt.get('routes', []))
            associations_count = len(rt.get('associations', []))
            
            report_file.write(f"| {rt_id} | {vpc_id} | {routes_count} | {associations_count} |\n")
    
    report_file.write("\n")

def write_gateway_analysis(report_file, igw_data: Optional[List], nat_data: Optional[List]) -> None:
    """게이트웨이 분석 섹션을 작성합니다."""
    report_file.write("## 🌉 게이트웨이 현황\n\n")
    
    # 인터넷 게이트웨이
    report_file.write("### 인터넷 게이트웨이\n")
    if not igw_data:
        report_file.write("인터넷 게이트웨이 데이터를 찾을 수 없습니다.\n\n")
    else:
        igw_count = len(igw_data)
        report_file.write(f"**총 인터넷 게이트웨이 수**: {igw_count}개\n\n")
        
        if igw_count > 0:
            report_file.write("| IGW ID | 상태 | 연결된 VPC |\n")
            report_file.write("|--------|------|------------|\n")
            
            for igw in igw_data:
                igw_id = igw.get('internet_gateway_id', 'N/A')
                state = igw.get('state', 'N/A')
                attachments = igw.get('attachments', [])
                vpc_ids = [att.get('VpcId', 'N/A') for att in attachments]
                vpc_list = ', '.join(vpc_ids) if vpc_ids else 'N/A'
                
                report_file.write(f"| {igw_id} | {state} | {vpc_list} |\n")
    
    # NAT 게이트웨이
    report_file.write("\n### NAT 게이트웨이\n")
    if not nat_data:
        report_file.write("NAT 게이트웨이 데이터를 찾을 수 없습니다.\n\n")
    else:
        nat_count = len(nat_data)
        report_file.write(f"**총 NAT 게이트웨이 수**: {nat_count}개\n\n")
        
        if nat_count > 0:
            report_file.write("| NAT GW ID | VPC ID | 서브넷 ID | 상태 |\n")
            report_file.write("|-----------|--------|-----------|------|\n")
            
            for nat in nat_data:
                nat_id = nat.get('nat_gateway_id', 'N/A')
                vpc_id = nat.get('vpc_id', 'N/A')
                subnet_id = nat.get('subnet_id', 'N/A')
                state = nat.get('state', 'N/A')
                
                report_file.write(f"| {nat_id} | {vpc_id} | {subnet_id} | {state} |\n")
    
    report_file.write("\n")

def write_network_recommendations(report_file, vpc_data: Optional[List], subnet_data: Optional[List], sg_data: Optional[List]) -> None:
    """네트워킹 권장사항 섹션을 작성합니다."""
    report_file.write("## 📋 네트워킹 권장사항\n\n")
    
    report_file.write("### 🔴 높은 우선순위\n")
    
    recommendations = []
    
    # VPC 관련 권장사항
    if vpc_data:
        default_vpcs = [v for v in vpc_data if v.get('is_default', False)]
        if default_vpcs:
            recommendations.append(f"**기본 VPC 검토**: {len(default_vpcs)}개의 기본 VPC가 발견되었습니다. 보안상 사용하지 않는 기본 VPC는 삭제를 고려하세요.")
    
    # 보안 그룹 관련 권장사항
    if sg_data:
        open_sgs = []
        for sg in sg_data:
            for rule in sg.get('ip_permissions', []):
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        open_sgs.append(sg.get('group_id'))
                        break
        
        if open_sgs:
            recommendations.append(f"**보안 그룹 검토**: {len(set(open_sgs))}개의 보안 그룹이 0.0.0.0/0에서 접근을 허용합니다. 필요한 IP 범위로 제한하세요.")
    
    # 서브넷 관련 권장사항
    if subnet_data:
        public_subnets = [s for s in subnet_data if s.get('map_public_ip_on_launch', False)]
        if public_subnets:
            recommendations.append(f"**퍼블릭 서브넷 검토**: {len(public_subnets)}개의 퍼블릭 서브넷이 있습니다. 불필요한 퍼블릭 IP 할당을 방지하세요.")
    
    # 기본 권장사항
    if not recommendations:
        recommendations = [
            "**네트워크 세분화**: 워크로드별로 서브넷을 분리하여 보안을 강화하세요.",
            "**보안 그룹 최소 권한**: 필요한 포트와 IP 범위만 허용하도록 설정하세요."
        ]
    
    for i, rec in enumerate(recommendations, 1):
        report_file.write(f"{i}. {rec}\n")
    
    report_file.write("\n### 🟡 중간 우선순위\n")
    report_file.write("1. **네트워크 모니터링**: VPC Flow Logs를 활성화하여 네트워크 트래픽을 모니터링하세요.\n")
    report_file.write("2. **네트워크 ACL 활용**: 서브넷 레벨에서 추가 보안 계층을 구성하세요.\n")
    report_file.write("3. **VPC 엔드포인트**: AWS 서비스 접근을 위한 VPC 엔드포인트를 구성하여 비용을 절감하세요.\n\n")
    
    report_file.write("### 🟢 낮은 우선순위\n")
    report_file.write("1. **네트워크 성능 최적화**: Enhanced Networking 및 SR-IOV를 활용하세요.\n")
    report_file.write("2. **DNS 해상도**: Route 53 Resolver를 활용한 하이브리드 DNS 구성을 고려하세요.\n")
    report_file.write("3. **네트워크 자동화**: Infrastructure as Code를 통한 네트워크 구성 자동화를 구현하세요.\n\n")

def main():
    """메인 함수"""
    print("🌐 Networking Analysis 보고서 생성 중...")
    
    # 보고서 디렉토리 설정
    report_dir = Path("/home/ec2-user/amazonqcli_lab/report")
    os.chdir(report_dir)
    
    # JSON 데이터 파일들 로드
    vpc_data = load_json_file("networking_vpc.json")
    subnet_data = load_json_file("networking_subnets.json")
    sg_data = load_json_file("security_groups.json")
    rt_data = load_json_file("networking_route_tables.json")
    igw_data = load_json_file("networking_igw.json")
    nat_data = load_json_file("networking_nat.json")
    
    # 보고서 파일 생성
    report_path = report_dir / "02-networking-analysis.md"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as report_file:
            # 헤더 작성
            report_file.write("# 네트워킹 분석\n\n")
            
            # 각 섹션 작성
            write_vpc_analysis(report_file, vpc_data)
            write_subnet_analysis(report_file, subnet_data)
            write_security_group_analysis(report_file, sg_data)
            write_route_table_analysis(report_file, rt_data)
            write_gateway_analysis(report_file, igw_data, nat_data)
            write_network_recommendations(report_file, vpc_data, subnet_data, sg_data)
            
            # 마무리
            report_file.write("---\n")
            report_file.write("*네트워킹 분석 완료*\n")
        
        print("✅ Networking Analysis 생성 완료: 02-networking-analysis.md")
        
    except IOError as e:
        print(f"❌ 보고서 파일 생성 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
