#!/usr/bin/env python3
"""
기존 보고서에 Enhanced 권장사항을 추가하는 모듈
기존 구조를 유지하면서 권장사항 부분만 데이터 기반으로 개선
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class EnhancedRecommendationsMixin:
    """기존 보고서 클래스에 추가할 수 있는 Enhanced 권장사항 Mixin"""
    
    def __init__(self):
        # 권장사항 저장소
        self.recommendations = {
            'high_priority': [],    # 높은 우선순위 (즉시 실행)
            'medium_priority': [],  # 중간 우선순위 (1-3개월)
            'low_priority': []      # 낮은 우선순위 (3-6개월)
        }
        
        # 우선순위 결정 기준
        self.priority_criteria = {
            'security_risk': 'high',      # 보안 위험
            'cost_impact': 'high',        # 높은 비용 영향
            'compliance': 'high',         # 컴플라이언스 위반
            'performance': 'medium',      # 성능 개선
            'monitoring': 'medium',       # 모니터링 강화
            'optimization': 'low',        # 일반적 최적화
            'best_practice': 'low'        # 모범 사례 적용
        }

    def safe_get(self, data: Dict, key: str, default: str = 'N/A') -> str:
        """안전하게 딕셔너리에서 값을 가져옵니다."""
        value = data.get(key, default)
        return str(value) if value is not None else default

    def add_recommendation(self, title: str, description: str, category: str, 
                          impact: str = 'medium', effort: str = 'medium', 
                          quantitative_benefit: str = None):
        """권장사항을 추가합니다."""
        
        # 우선순위 결정
        priority = self.priority_criteria.get(category, 'medium')
        
        # 보안 위험이나 높은 비용 영향은 항상 높은 우선순위
        if 'security' in title.lower() or 'mfa' in title.lower() or '보안' in title:
            priority = 'high'
        elif 'cost' in title.lower() or '비용' in title or quantitative_benefit:
            if quantitative_benefit and any(x in quantitative_benefit for x in ['$', '원', '%']):
                priority = 'high'
        
        recommendation = {
            'title': title,
            'description': description,
            'category': category,
            'priority': priority,
            'impact': impact,
            'effort': effort,
            'quantitative_benefit': quantitative_benefit
        }
        
        # 우선순위별로 분류
        if priority == 'high':
            self.recommendations['high_priority'].append(recommendation)
        elif priority == 'medium':
            self.recommendations['medium_priority'].append(recommendation)
        else:
            self.recommendations['low_priority'].append(recommendation)

    def write_enhanced_recommendations_section(self, report_file, section_title: str = "권장사항") -> None:
        """Enhanced 권장사항 섹션을 작성합니다."""
        
        report_file.write(f"## 📋 {section_title}\n\n")
        
        # 높은 우선순위
        if self.recommendations['high_priority']:
            report_file.write("### 🔴 높은 우선순위 (즉시 실행)\n")
            for i, rec in enumerate(self.recommendations['high_priority'], 1):
                report_file.write(f"{i}. **{rec['title']}**: {rec['description']}\n")
                if rec.get('quantitative_benefit'):
                    report_file.write(f"   - **예상 효과**: {rec['quantitative_benefit']}\n")
                report_file.write(f"   - **영향도**: {rec['impact']}, **구현 난이도**: {rec['effort']}\n")
            report_file.write("\n")
        
        # 중간 우선순위
        if self.recommendations['medium_priority']:
            report_file.write("### 🟡 중간 우선순위 (1-3개월 내)\n")
            for i, rec in enumerate(self.recommendations['medium_priority'], 1):
                report_file.write(f"{i}. **{rec['title']}**: {rec['description']}\n")
                if rec.get('quantitative_benefit'):
                    report_file.write(f"   - **예상 효과**: {rec['quantitative_benefit']}\n")
                report_file.write(f"   - **영향도**: {rec['impact']}, **구현 난이도**: {rec['effort']}\n")
            report_file.write("\n")
        
        # 낮은 우선순위
        if self.recommendations['low_priority']:
            report_file.write("### 🟢 낮은 우선순위 (3-6개월 내)\n")
            for i, rec in enumerate(self.recommendations['low_priority'], 1):
                report_file.write(f"{i}. **{rec['title']}**: {rec['description']}\n")
                if rec.get('quantitative_benefit'):
                    report_file.write(f"   - **예상 효과**: {rec['quantitative_benefit']}\n")
                report_file.write(f"   - **영향도**: {rec['impact']}, **구현 난이도**: {rec['effort']}\n")
            report_file.write("\n")
        
        # 권장사항이 없는 경우
        if not any(self.recommendations.values()):
            report_file.write("현재 분석된 데이터를 기반으로 특별한 권장사항이 없습니다.\n")
            report_file.write("정기적인 검토를 통해 지속적인 최적화를 수행하세요.\n\n")

    def get_recommendations_summary(self) -> Dict[str, int]:
        """권장사항 요약 통계를 반환합니다."""
        return {
            'high_priority': len(self.recommendations['high_priority']),
            'medium_priority': len(self.recommendations['medium_priority']),
            'low_priority': len(self.recommendations['low_priority']),
            'total': sum(len(recs) for recs in self.recommendations.values())
        }

class NetworkingRecommendations(EnhancedRecommendationsMixin):
    """네트워킹 관련 Enhanced 권장사항"""
    
    def analyze_networking_data(self, data_dict: Dict) -> None:
        """네트워킹 데이터를 분석하여 권장사항 생성"""
        
        # 보안 그룹 0.0.0.0/0 규칙 검사
        security_groups = data_dict.get('security_groups') or []
        ingress_rules = data_dict.get('security_groups_ingress') or []
        
        open_sg_count = 0
        ssh_open_count = 0
        rdp_open_count = 0
        
        for rule in ingress_rules:
            if rule.get('cidr_ipv4') == '0.0.0.0/0':
                open_sg_count += 1
                from_port = rule.get('from_port', 0)
                if from_port == 22:
                    ssh_open_count += 1
                elif from_port == 3389:
                    rdp_open_count += 1
        
        if ssh_open_count > 0:
            self.add_recommendation(
                title="SSH 접근 제한",
                description=f"{ssh_open_count}개의 보안 그룹이 전체 인터넷에서 SSH(22번 포트) 접근을 허용합니다. 특정 IP 대역으로 제한하세요.",
                category="security_risk",
                impact="high",
                effort="low"
            )
        
        if rdp_open_count > 0:
            self.add_recommendation(
                title="RDP 접근 제한",
                description=f"{rdp_open_count}개의 보안 그룹이 전체 인터넷에서 RDP(3389번 포트) 접근을 허용합니다. 특정 IP 대역으로 제한하세요.",
                category="security_risk",
                impact="high",
                effort="low"
            )
        
        if open_sg_count > ssh_open_count + rdp_open_count:
            other_open = open_sg_count - ssh_open_count - rdp_open_count
            self.add_recommendation(
                title="보안 그룹 규칙 최소화",
                description=f"{other_open}개의 추가 보안 그룹 규칙이 0.0.0.0/0에서 접근을 허용합니다. 최소 권한 원칙을 적용하세요.",
                category="security_risk",
                impact="medium",
                effort="medium"
            )
        
        # VPC Flow Logs 검사
        flow_logs = data_dict.get('flow_logs') or []
        vpcs = data_dict.get('vpc') or []
        
        if vpcs and not flow_logs:
            self.add_recommendation(
                title="VPC Flow Logs 활성화",
                description=f"{len(vpcs)}개의 VPC에 Flow Logs가 설정되지 않았습니다. 네트워크 트래픽 모니터링을 위해 활성화하세요.",
                category="security_risk",
                impact="medium",
                effort="low"
            )
        
        # 미사용 Elastic IP 검사
        elastic_ips = data_dict.get('elastic_ips') or []
        if elastic_ips:
            unassociated_eips = [eip for eip in elastic_ips if not eip.get('association_id')]
            if unassociated_eips:
                monthly_cost = len(unassociated_eips) * 3.65  # 월 $3.65 per EIP
                self.add_recommendation(
                    title="미사용 Elastic IP 정리",
                    description=f"{len(unassociated_eips)}개의 연결되지 않은 Elastic IP가 있습니다. 불필요한 EIP를 해제하세요.",
                    category="cost_impact",
                    impact="medium",
                    effort="low",
                    quantitative_benefit=f"월 ${monthly_cost:.2f} 절감 가능"
                )
        
        # NAT Gateway 최적화 검사
        nat_gateways = data_dict.get('nat') or []
        if len(nat_gateways) > 2:
            excess_nat = len(nat_gateways) - 2
            monthly_cost = excess_nat * 45.0  # 월 $45 per NAT Gateway
            self.add_recommendation(
                title="NAT Gateway 최적화",
                description=f"{len(nat_gateways)}개의 NAT Gateway가 있습니다. 필요에 따라 통합을 고려하세요.",
                category="cost_impact",
                impact="medium",
                effort="high",
                quantitative_benefit=f"통합 시 월 최대 ${monthly_cost:.2f} 절감 가능"
            )
        
        # VPC 엔드포인트 활용 권장
        vpc_endpoints = data_dict.get('vpc_endpoints') or []
        if not vpc_endpoints:
            self.add_recommendation(
                title="VPC 엔드포인트 구성",
                description="AWS 서비스 접근을 위한 VPC 엔드포인트를 구성하여 데이터 전송 비용을 절감하세요.",
                category="cost_impact",
                impact="medium",
                effort="medium",
                quantitative_benefit="데이터 전송 비용 최대 50% 절감 가능"
            )

class ComputeRecommendations(EnhancedRecommendationsMixin):
    """컴퓨팅 관련 Enhanced 권장사항"""
    
    def analyze_compute_data(self, data_dict: Dict) -> None:
        """컴퓨팅 데이터를 분석하여 권장사항 생성"""
        
        # EC2 인스턴스 분석
        ec2_instances = data_dict.get('compute_ec2_instances') or []
        if ec2_instances:
            running_instances = [i for i in ec2_instances if i.get('state', {}).get('name') == 'running']
            stopped_instances = [i for i in ec2_instances if i.get('state', {}).get('name') == 'stopped']
            
            # 중지된 인스턴스 정리 권장
            if stopped_instances:
                self.add_recommendation(
                    title="중지된 EC2 인스턴스 정리",
                    description=f"{len(stopped_instances)}개의 중지된 EC2 인스턴스가 있습니다. 불필요한 인스턴스를 종료하여 EBS 비용을 절감하세요.",
                    category="cost_impact",
                    impact="medium",
                    effort="low",
                    quantitative_benefit="EBS 스토리지 비용 절감"
                )
            
            # Reserved Instance 활용 권장
            reserved_instances = data_dict.get('ec2_reserved_instances') or []
            if len(running_instances) > 5 and len(reserved_instances) == 0:
                estimated_savings = len(running_instances) * 30 * 0.4  # 대략적인 월 절감액
                self.add_recommendation(
                    title="Reserved Instance 구매 검토",
                    description=f"{len(running_instances)}개의 실행 중인 인스턴스가 있습니다. Reserved Instance로 비용을 절감하세요.",
                    category="cost_impact",
                    impact="high",
                    effort="low",
                    quantitative_benefit=f"월 약 ${estimated_savings:.0f} 절감 가능 (최대 75%)"
                )

class SecurityRecommendations(EnhancedRecommendationsMixin):
    """보안 관련 Enhanced 권장사항"""
    
    def analyze_security_data(self, data_dict: Dict) -> None:
        """보안 데이터를 분석하여 권장사항 생성"""
        
        # IAM MFA 검사
        iam_users = data_dict.get('iam_users') or []
        if iam_users:
            users_without_mfa = [u for u in iam_users if u.get('password_enabled', False) and not u.get('mfa_enabled', False)]
            if users_without_mfa:
                self.add_recommendation(
                    title="MFA 필수 설정",
                    description=f"{len(users_without_mfa)}개의 콘솔 사용자가 MFA를 사용하지 않습니다. 즉시 MFA를 활성화하세요.",
                    category="security_risk",
                    impact="high",
                    effort="low"
                )
        
        # GuardDuty 검사
        if not (data_dict.get('guardduty_detectors') or []):
            self.add_recommendation(
                title="GuardDuty 활성화",
                description="위협 탐지를 위해 Amazon GuardDuty를 활성화하세요.",
                category="security_risk",
                impact="high",
                effort="low"
            )
