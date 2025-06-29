#!/usr/bin/env python3
"""
권장사항 생성 기준 통일을 위한 베이스 클래스
모든 보고서에서 일관된 권장사항 생성 방식 적용
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class RecommendationBase:
    """권장사항 생성을 위한 베이스 클래스"""
    
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
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

    def analyze_security_risks(self, data_dict: Dict) -> None:
        """보안 위험 분석 및 권장사항 생성"""
        
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
        
        # 보안 그룹 검사
        security_groups = data_dict.get('security_groups') or []
        if security_groups:
            open_sg_count = 0
            for sg in security_groups:
                for rule in sg.get('ip_permissions', []):
                    for ip_range in rule.get('ip_ranges', []):
                        if ip_range.get('cidr_ip') == '0.0.0.0/0':
                            open_sg_count += 1
                            break
            
            if open_sg_count > 0:
                self.add_recommendation(
                    title="보안 그룹 규칙 검토",
                    description=f"{open_sg_count}개의 보안 그룹이 0.0.0.0/0에서 접근을 허용합니다. 최소 권한 원칙을 적용하세요.",
                    category="security_risk",
                    impact="high",
                    effort="medium"
                )

    def analyze_cost_optimization(self, data_dict: Dict) -> None:
        """비용 최적화 분석 및 권장사항 생성"""
        
        # EC2 인스턴스 분석
        ec2_instances = data_dict.get('compute_ec2_instances') or []
        if ec2_instances:
            running_instances = [i for i in ec2_instances if i.get('state', {}).get('name') == 'running']
            if len(running_instances) > 10:
                self.add_recommendation(
                    title="EC2 인스턴스 최적화",
                    description=f"{len(running_instances)}개의 실행 중인 EC2 인스턴스가 있습니다. Reserved Instance 또는 Savings Plans 활용을 검토하세요.",
                    category="cost_impact",
                    impact="high",
                    effort="medium",
                    quantitative_benefit="최대 75% 비용 절감 가능"
                )
        
        # 미사용 EBS 볼륨 검사
        ebs_volumes = data_dict.get('storage_ebs_volumes') or []
        if ebs_volumes:
            unattached_volumes = [v for v in ebs_volumes if v.get('state') == 'available']
            if unattached_volumes:
                total_size = sum(v.get('size', 0) for v in unattached_volumes)
                estimated_cost = total_size * 0.1  # 대략적인 월 비용 계산
                self.add_recommendation(
                    title="미사용 EBS 볼륨 정리",
                    description=f"{len(unattached_volumes)}개의 연결되지 않은 EBS 볼륨이 있습니다. 불필요한 볼륨을 삭제하세요.",
                    category="cost_impact",
                    impact="medium",
                    effort="low",
                    quantitative_benefit=f"월 약 ${estimated_cost:.2f} 절감 가능"
                )

    def analyze_performance_monitoring(self, data_dict: Dict) -> None:
        """성능 및 모니터링 분석"""
        
        # CloudWatch 알람 검사
        cloudwatch_alarms = data_dict.get('monitoring_cloudwatch_alarms') or []
        if not cloudwatch_alarms:
            self.add_recommendation(
                title="CloudWatch 알람 설정",
                description="핵심 메트릭에 대한 모니터링 알람을 구성하세요.",
                category="monitoring",
                impact="medium",
                effort="medium"
            )
        
        # VPC Flow Logs 검사
        flow_logs = data_dict.get('networking_flow_logs') or []
        if not flow_logs:
            self.add_recommendation(
                title="VPC Flow Logs 활성화",
                description="네트워크 트래픽 모니터링을 위해 VPC Flow Logs를 활성화하세요.",
                category="monitoring",
                impact="medium",
                effort="low"
            )

    def analyze_compliance_best_practices(self, data_dict: Dict) -> None:
        """컴플라이언스 및 모범 사례 분석"""
        
        # RDS 암호화 검사
        rds_instances = data_dict.get('database_rds_instances') or []
        if rds_instances:
            unencrypted_rds = [r for r in rds_instances if not r.get('storage_encrypted', False)]
            if unencrypted_rds:
                self.add_recommendation(
                    title="RDS 암호화 활성화",
                    description=f"{len(unencrypted_rds)}개의 RDS 인스턴스가 암호화되지 않았습니다. 데이터 보안을 위해 암호화를 활성화하세요.",
                    category="compliance",
                    impact="high",
                    effort="high"
                )
        
        # S3 버킷 퍼블릭 액세스 검사
        s3_buckets = data_dict.get('storage_s3_buckets') or []
        s3_public_access = data_dict.get('storage_s3_public_access_block') or []
        if s3_buckets and not s3_public_access:
            self.add_recommendation(
                title="S3 퍼블릭 액세스 차단",
                description="S3 버킷의 퍼블릭 액세스 차단 설정을 활성화하세요.",
                category="compliance",
                impact="high",
                effort="low"
            )

    def generate_all_recommendations(self, data_dict: Dict) -> None:
        """모든 영역의 권장사항을 생성합니다."""
        
        # 각 영역별 분석 수행
        self.analyze_security_risks(data_dict)
        self.analyze_cost_optimization(data_dict)
        self.analyze_performance_monitoring(data_dict)
        self.analyze_compliance_best_practices(data_dict)

    def write_recommendations_section(self, report_file, section_title: str = "권장사항") -> None:
        """권장사항 섹션을 작성합니다."""
        
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
