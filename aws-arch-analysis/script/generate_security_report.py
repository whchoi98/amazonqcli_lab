#!/usr/bin/env python3
"""
확장된 보안 분석 보고서 생성 스크립트
IAM, 보안 서비스, 암호화, WAF, Shield 등 모든 보안 서비스 포함
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class EnhancedSecurityReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 보안 서비스별 파일 매핑
        self.security_files = {
            # IAM 관련
            'iam_users': 'security_iam_users.json',
            'iam_roles': 'security_iam_roles.json',
            'iam_groups': 'security_iam_groups.json',
            'iam_policies': 'security_iam_policies.json',
            'iam_account_summary': 'security_iam_account_summary.json',
            
            # KMS 관련
            'kms_keys': 'security_kms_keys.json',
            'kms_aliases': 'security_kms_aliases.json',
            
            # 보안 서비스
            'guardduty_detectors': 'security_guardduty_detectors.json',
            'securityhub': 'security_securityhub.json',
            'inspector2': 'security_inspector2.json',
            'macie2': 'security_macie2.json',
            
            # WAF 관련
            'wafv2_web_acls': 'security_wafv2_web_acls.json',
            
            # 네트워크 보안
            'network_firewall': 'security_network_firewall.json',
            'secrets_manager': 'security_secrets_manager.json',
            'config_recorders': 'security_config_recorders.json'
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

    def write_iam_comprehensive_analysis(self, report_file, data_dict: Dict) -> None:
        """포괄적인 IAM 분석 섹션을 작성합니다."""
        report_file.write("## 👤 IAM (Identity and Access Management) 종합 분석\n\n")
        
        # IAM 계정 요약
        account_summary = data_dict.get('iam_account_summary')
        if account_summary and len(account_summary) > 0:
            summary = account_summary[0]
            report_file.write("### 📊 IAM 계정 요약\n")
            report_file.write("| 항목 | 수량 | 한도 |\n")
            report_file.write("|------|------|------|\n")
            report_file.write(f"| 사용자 | {self.safe_get(summary, 'users')} | {self.safe_get(summary, 'users_quota', '5000')} |\n")
            report_file.write(f"| 그룹 | {self.safe_get(summary, 'groups')} | {self.safe_get(summary, 'groups_quota', '300')} |\n")
            report_file.write(f"| 역할 | {self.safe_get(summary, 'roles')} | {self.safe_get(summary, 'roles_quota', '1000')} |\n")
            report_file.write(f"| 정책 | {self.safe_get(summary, 'policies')} | {self.safe_get(summary, 'policies_quota', '1500')} |\n\n")
        
        # IAM 사용자 분석
        iam_users = data_dict.get('iam_users') or []
        report_file.write("### 👥 IAM 사용자 분석\n")
        if not iam_users:
            report_file.write("IAM 사용자 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_users = len(iam_users)
            console_users = len([u for u in iam_users if u.get('password_enabled', False)])
            mfa_users = len([u for u in iam_users if u.get('mfa_enabled', False)])
            access_key_users = len([u for u in iam_users if u.get('access_key_1_active', False) or u.get('access_key_2_active', False)])
            
            report_file.write(f"**총 IAM 사용자:** {total_users}개\n")
            report_file.write(f"- **콘솔 액세스 가능:** {console_users}개\n")
            report_file.write(f"- **MFA 활성화:** {mfa_users}개 ({(mfa_users/total_users*100):.1f}%)\n")
            report_file.write(f"- **액세스 키 보유:** {access_key_users}개\n\n")
            
            # 보안 위험 사용자
            risky_users = [u for u in iam_users if u.get('password_enabled', False) and not u.get('mfa_enabled', False)]
            if risky_users:
                report_file.write(f"⚠️ **보안 위험 사용자:** {len(risky_users)}개 (콘솔 액세스 가능하지만 MFA 미설정)\n\n")
        
        # IAM 역할 분석
        iam_roles = data_dict.get('iam_roles') or []
        report_file.write("### 🎭 IAM 역할 분석\n")
        if not iam_roles:
            report_file.write("IAM 역할 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_roles = len(iam_roles)
            service_roles = len([r for r in iam_roles if 'service-role' in r.get('path', '')])
            aws_service_roles = len([r for r in iam_roles if r.get('assume_role_policy_document', '').find('amazonaws.com') != -1])
            
            report_file.write(f"**총 IAM 역할:** {total_roles}개\n")
            report_file.write(f"- **서비스 역할:** {service_roles}개\n")
            report_file.write(f"- **AWS 서비스 역할:** {aws_service_roles}개\n\n")
            
            # 역할별 분포 (상위 10개)
            role_types = {}
            for role in iam_roles[:10]:  # 상위 10개만 표시
                role_name = role.get('role_name', 'Unknown')
                if 'service-role' in role.get('path', ''):
                    role_type = 'Service Role'
                elif role_name.startswith('AWS'):
                    role_type = 'AWS Managed'
                else:
                    role_type = 'Custom Role'
                role_types[role_type] = role_types.get(role_type, 0) + 1
            
            if role_types:
                report_file.write("**역할 유형별 분포:**\n")
                for role_type, count in role_types.items():
                    report_file.write(f"- {role_type}: {count}개\n")
                report_file.write("\n")
        
        # IAM 그룹 분석
        iam_groups = data_dict.get('iam_groups') or []
        report_file.write("### 👥 IAM 그룹 분석\n")
        if not iam_groups:
            report_file.write("IAM 그룹 데이터를 찾을 수 없습니다.\n\n")
        else:
            total_groups = len(iam_groups)
            report_file.write(f"**총 IAM 그룹:** {total_groups}개\n\n")
            
            if total_groups > 0:
                report_file.write("**그룹 목록:**\n")
                for group in iam_groups[:5]:  # 상위 5개만 표시
                    group_name = group.get('group_name', 'N/A')
                    create_date = group.get('create_date', 'N/A')[:10] if group.get('create_date') else 'N/A'
                    report_file.write(f"- {group_name} (생성일: {create_date})\n")
                if total_groups > 5:
                    report_file.write(f"... 및 {total_groups - 5}개 추가 그룹\n")
                report_file.write("\n")

    def write_kms_encryption_analysis(self, report_file, data_dict: Dict) -> None:
        """KMS 및 암호화 분석 섹션을 작성합니다."""
        report_file.write("## 🔐 KMS 및 암호화 관리\n\n")
        
        # KMS 키 분석
        kms_keys = data_dict.get('kms_keys', [])
        kms_aliases = data_dict.get('kms_aliases', [])
        
        if not kms_keys:
            report_file.write("KMS 키 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_keys = len(kms_keys)
        customer_keys = len([k for k in kms_keys if k.get('key_manager') == 'CUSTOMER'])
        aws_keys = len([k for k in kms_keys if k.get('key_manager') == 'AWS'])
        enabled_keys = len([k for k in kms_keys if k.get('enabled', False)])
        
        report_file.write("### 🔑 KMS 키 현황\n")
        report_file.write(f"**총 KMS 키:** {total_keys}개\n")
        report_file.write(f"- **고객 관리형 키:** {customer_keys}개\n")
        report_file.write(f"- **AWS 관리형 키:** {aws_keys}개\n")
        report_file.write(f"- **활성화된 키:** {enabled_keys}개\n\n")
        
        # 키 사용 목적별 분석
        key_usage = {}
        for key in kms_keys:
            usage = key.get('key_usage', 'ENCRYPT_DECRYPT')
            key_usage[usage] = key_usage.get(usage, 0) + 1
        
        if key_usage:
            report_file.write("**키 사용 목적별 분포:**\n")
            for usage, count in key_usage.items():
                report_file.write(f"- {usage}: {count}개\n")
            report_file.write("\n")
        
        # KMS 별칭 분석
        if kms_aliases:
            total_aliases = len(kms_aliases)
            aws_aliases = len([a for a in kms_aliases if a.get('alias_name', '').startswith('alias/aws/')])
            custom_aliases = total_aliases - aws_aliases
            
            report_file.write("### 🏷️ KMS 별칭 현황\n")
            report_file.write(f"**총 KMS 별칭:** {total_aliases}개\n")
            report_file.write(f"- **AWS 관리형 별칭:** {aws_aliases}개\n")
            report_file.write(f"- **사용자 정의 별칭:** {custom_aliases}개\n\n")

    def write_security_services_analysis(self, report_file, data_dict: Dict) -> None:
        """보안 서비스 분석 섹션을 작성합니다."""
        report_file.write("## 🛡️ AWS 보안 서비스 현황\n\n")
        
        # GuardDuty 분석
        guardduty_data = data_dict.get('guardduty_detectors', [])
        report_file.write("### 🔍 Amazon GuardDuty\n")
        if not guardduty_data:
            report_file.write("GuardDuty 탐지기가 설정되지 않았습니다.\n\n")
        else:
            total_detectors = len(guardduty_data)
            enabled_detectors = len([d for d in guardduty_data if d.get('status') == 'ENABLED'])
            
            report_file.write(f"**GuardDuty 탐지기:** {total_detectors}개\n")
            report_file.write(f"- **활성화된 탐지기:** {enabled_detectors}개\n")
            
            if enabled_detectors > 0:
                report_file.write("✅ GuardDuty가 활성화되어 위협 탐지가 진행 중입니다.\n")
            else:
                report_file.write("⚠️ GuardDuty가 비활성화되어 있습니다. 위협 탐지를 위해 활성화를 권장합니다.\n")
            report_file.write("\n")
        
        # Security Hub 분석
        securityhub_data = data_dict.get('securityhub', [])
        report_file.write("### 🏢 AWS Security Hub\n")
        if not securityhub_data:
            report_file.write("Security Hub가 설정되지 않았습니다.\n")
            report_file.write("⚠️ 중앙 집중식 보안 관리를 위해 Security Hub 활성화를 권장합니다.\n\n")
        else:
            report_file.write("✅ Security Hub가 활성화되어 있습니다.\n\n")
        
        # AWS Config 분석
        config_data = data_dict.get('config_recorders', [])
        report_file.write("### ⚙️ AWS Config\n")
        if not config_data:
            report_file.write("Config 구성 레코더가 설정되지 않았습니다.\n")
            report_file.write("⚠️ 리소스 구성 추적을 위해 Config 활성화를 권장합니다.\n\n")
        else:
            active_recorders = len([c for c in config_data if c.get('recording', False)])
            report_file.write(f"**Config 레코더:** {len(config_data)}개\n")
            report_file.write(f"- **활성 레코더:** {active_recorders}개\n")
            if active_recorders > 0:
                report_file.write("✅ Config가 활성화되어 리소스 구성이 추적되고 있습니다.\n")
            report_file.write("\n")

    def write_waf_network_security_analysis(self, report_file, data_dict: Dict) -> None:
        """WAF 및 네트워크 보안 분석 섹션을 작성합니다."""
        report_file.write("## 🌐 웹 애플리케이션 및 네트워크 보안\n\n")
        
        # WAF v2 분석
        waf_data = data_dict.get('wafv2_web_acls', [])
        report_file.write("### 🛡️ AWS WAF v2\n")
        if not waf_data:
            report_file.write("WAF v2 Web ACL이 설정되지 않았습니다.\n")
            report_file.write("⚠️ 웹 애플리케이션 보호를 위해 WAF 설정을 권장합니다.\n\n")
        else:
            total_acls = len(waf_data)
            cloudfront_acls = len([w for w in waf_data if w.get('scope') == 'CLOUDFRONT'])
            regional_acls = len([w for w in waf_data if w.get('scope') == 'REGIONAL'])
            
            report_file.write(f"**WAF v2 Web ACL:** {total_acls}개\n")
            report_file.write(f"- **CloudFront용:** {cloudfront_acls}개\n")
            report_file.write(f"- **Regional용:** {regional_acls}개\n")
            report_file.write("✅ WAF가 설정되어 웹 애플리케이션이 보호되고 있습니다.\n\n")
        
        # Network Firewall 분석
        network_firewall_data = data_dict.get('network_firewall', [])
        report_file.write("### 🔥 AWS Network Firewall\n")
        if not network_firewall_data:
            report_file.write("Network Firewall이 설정되지 않았습니다.\n")
            report_file.write("💡 고급 네트워크 보안이 필요한 경우 Network Firewall 사용을 고려하세요.\n\n")
        else:
            report_file.write(f"**Network Firewall:** {len(network_firewall_data)}개\n")
            report_file.write("✅ Network Firewall이 설정되어 네트워크 레벨 보안이 강화되었습니다.\n\n")

    def write_secrets_management_analysis(self, report_file, data_dict: Dict) -> None:
        """시크릿 관리 분석 섹션을 작성합니다."""
        report_file.write("## 🔒 시크릿 및 자격 증명 관리\n\n")
        
        # Secrets Manager 분석
        secrets_data = data_dict.get('secrets_manager', [])
        report_file.write("### 🗝️ AWS Secrets Manager\n")
        if not secrets_data:
            report_file.write("Secrets Manager에 저장된 시크릿이 없습니다.\n")
            report_file.write("💡 데이터베이스 자격 증명 등 민감한 정보는 Secrets Manager에 저장하는 것을 권장합니다.\n\n")
        else:
            total_secrets = len(secrets_data)
            auto_rotation_secrets = len([s for s in secrets_data if s.get('rotation_enabled', False)])
            
            report_file.write(f"**총 시크릿:** {total_secrets}개\n")
            report_file.write(f"- **자동 순환 활성화:** {auto_rotation_secrets}개\n")
            
            if auto_rotation_secrets > 0:
                report_file.write("✅ 자동 순환이 설정된 시크릿이 있어 보안이 강화되었습니다.\n")
            else:
                report_file.write("⚠️ 자동 순환이 설정된 시크릿이 없습니다. 보안 강화를 위해 자동 순환 설정을 권장합니다.\n")
            report_file.write("\n")

    def write_comprehensive_security_recommendations(self, report_file, data_dict: Dict) -> None:
        """포괄적인 보안 권장사항 섹션을 작성합니다."""
        report_file.write("## 📋 보안 강화 종합 권장사항\n\n")
        
        # 데이터 기반 권장사항 생성
        high_priority = []
        medium_priority = []
        low_priority = []
        
        # IAM 관련 권장사항
        iam_users = data_dict.get('iam_users') or []
        if iam_users:
            users_without_mfa = [u for u in iam_users if u.get('password_enabled', False) and not u.get('mfa_enabled', False)]
            if users_without_mfa:
                high_priority.append(f"**MFA 필수 설정**: {len(users_without_mfa)}개의 콘솔 사용자가 MFA를 사용하지 않습니다. 즉시 MFA를 활성화하세요.")
            
            old_access_keys = [u for u in iam_users if u.get('access_key_1_last_used_date') and 
                             (datetime.now() - datetime.fromisoformat(u.get('access_key_1_last_used_date', '').replace('Z', '+00:00'))).days > 90]
            if old_access_keys:
                medium_priority.append(f"**액세스 키 순환**: {len(old_access_keys)}개의 사용자가 90일 이상 사용하지 않은 액세스 키를 보유하고 있습니다.")
        
        # 보안 서비스 관련 권장사항
        if not (data_dict.get('guardduty_detectors') or []):
            high_priority.append("**GuardDuty 활성화**: 위협 탐지를 위해 Amazon GuardDuty를 활성화하세요.")
        
        if not (data_dict.get('securityhub') or []):
            medium_priority.append("**Security Hub 활성화**: 중앙 집중식 보안 관리를 위해 AWS Security Hub를 활성화하세요.")
        
        if not (data_dict.get('config_recorders') or []):
            medium_priority.append("**Config 활성화**: 리소스 구성 추적 및 컴플라이언스 모니터링을 위해 AWS Config를 활성화하세요.")
        
        # WAF 관련 권장사항
        if not (data_dict.get('wafv2_web_acls') or []):
            medium_priority.append("**WAF 구성**: 웹 애플리케이션 보호를 위해 AWS WAF를 구성하세요.")
        
        # 암호화 관련 권장사항
        kms_keys = data_dict.get('kms_keys') or []
        if kms_keys:
            customer_keys = [k for k in kms_keys if k.get('key_manager') == 'CUSTOMER']
            if len(customer_keys) < 3:
                low_priority.append("**KMS 키 관리**: 중요한 데이터 암호화를 위해 고객 관리형 KMS 키 사용을 확대하세요.")
        
        # 기본 권장사항 추가
        if not high_priority:
            high_priority.append("**정기적인 보안 검토**: IAM 권한과 보안 그룹 규칙을 정기적으로 검토하세요.")
        
        if not medium_priority:
            medium_priority.extend([
                "**암호화 정책 수립**: 저장 중 및 전송 중 데이터 암호화 정책을 수립하고 적용하세요.",
                "**로그 모니터링 강화**: CloudTrail과 VPC Flow Logs를 통한 감사 로깅을 강화하세요."
            ])
        
        if not low_priority:
            low_priority.extend([
                "**보안 자동화**: AWS Systems Manager를 통한 패치 관리 자동화를 구현하세요.",
                "**네트워크 분할**: VPC와 서브넷을 통한 네트워크 분할 전략을 수립하세요."
            ])
        
        # 권장사항 출력
        report_file.write("### 🔴 높은 우선순위 (즉시 실행)\n")
        for i, rec in enumerate(high_priority, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n### 🟡 중간 우선순위 (1-3개월 내)\n")
        for i, rec in enumerate(medium_priority, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n### 🟢 낮은 우선순위 (3-6개월 내)\n")
        for i, rec in enumerate(low_priority, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n")
        
        # 보안 체크리스트
        report_file.write("### ✅ 보안 체크리스트\n")
        report_file.write("다음 항목들을 정기적으로 점검하세요:\n\n")
        report_file.write("- [ ] 모든 IAM 사용자에 MFA 설정\n")
        report_file.write("- [ ] 불필요한 IAM 권한 제거 (최소 권한 원칙)\n")
        report_file.write("- [ ] 90일 이상 미사용 액세스 키 삭제\n")
        report_file.write("- [ ] 보안 그룹에서 불필요한 인바운드 규칙 제거\n")
        report_file.write("- [ ] 모든 S3 버킷에 적절한 액세스 정책 설정\n")
        report_file.write("- [ ] RDS 인스턴스 암호화 활성화\n")
        report_file.write("- [ ] CloudTrail 로깅 활성화 및 모니터링\n")
        report_file.write("- [ ] GuardDuty 위협 탐지 활성화\n")
        report_file.write("- [ ] 정기적인 보안 패치 적용\n")
        report_file.write("- [ ] 백업 및 재해 복구 계획 수립\n\n")

    def generate_report(self):
        """확장된 보안 분석 보고서를 생성합니다."""
        print("🔒 Enhanced Security Analysis 보고서 생성 중...")
        
        # 모든 보안 관련 데이터 파일 로드
        data_dict = {}
        for key, filename in self.security_files.items():
            data_dict[key] = self.load_json_file(filename)
        
        # 보고서 파일 생성
        report_path = self.report_dir / "06-security-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 🛡️ AWS 보안 리소스 종합 분석\n\n")
                report_file.write(f"> **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
                report_file.write(f"> **분석 대상**: AWS 계정 내 모든 보안 서비스 및 구성  \n")
                report_file.write(f"> **분석 리전**: ap-northeast-2 (서울)\n\n")
                report_file.write("이 보고서는 AWS 계정의 보안 인프라에 대한 종합적인 분석을 제공하며, IAM, 보안 서비스, 암호화, WAF, 네트워크 보안 등의 구성 상태와 보안 강화 방안을 평가합니다.\n\n")
                
                # 보안 현황 요약
                report_file.write("## 📊 보안 현황 요약\n\n")
                
                # 주요 지표 계산 (None 처리)
                iam_users_count = len(data_dict.get('iam_users') or [])
                iam_roles_count = len(data_dict.get('iam_roles') or [])
                kms_keys_count = len(data_dict.get('kms_keys') or [])
                guardduty_enabled = len(data_dict.get('guardduty_detectors') or []) > 0
                waf_enabled = len(data_dict.get('wafv2_web_acls') or []) > 0
                
                report_file.write("| 보안 영역 | 현황 | 상태 |\n")
                report_file.write("|-----------|------|------|\n")
                report_file.write(f"| IAM 사용자 | {iam_users_count}개 | {'✅ 관리됨' if iam_users_count > 0 else '⚠️ 없음'} |\n")
                report_file.write(f"| IAM 역할 | {iam_roles_count}개 | {'✅ 관리됨' if iam_roles_count > 0 else '⚠️ 없음'} |\n")
                report_file.write(f"| KMS 키 | {kms_keys_count}개 | {'✅ 암호화 활성' if kms_keys_count > 0 else '⚠️ 미설정'} |\n")
                report_file.write(f"| GuardDuty | {'활성화' if guardduty_enabled else '비활성화'} | {'✅ 위협 탐지 중' if guardduty_enabled else '❌ 미설정'} |\n")
                report_file.write(f"| WAF | {'설정됨' if waf_enabled else '미설정'} | {'✅ 웹 보안 활성' if waf_enabled else '⚠️ 미설정'} |\n\n")
                
                # 각 섹션 작성
                self.write_iam_comprehensive_analysis(report_file, data_dict)
                self.write_kms_encryption_analysis(report_file, data_dict)
                self.write_security_services_analysis(report_file, data_dict)
                self.write_waf_network_security_analysis(report_file, data_dict)
                self.write_secrets_management_analysis(report_file, data_dict)
                self.write_comprehensive_security_recommendations(report_file, data_dict)
                
                # 마무리 섹션 추가
                self.write_footer_section(report_file)
            
            print("✅ Enhanced Security Analysis 생성 완료: 06-security-analysis.md")
            print(f"📁 보고서 위치: {report_path}")
            print(f"📊 보고서 크기: {report_path.stat().st_size:,} bytes")
            
            # Enhanced 권장사항 통계 출력
            if hasattr(self, 'get_recommendations_summary'):
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

📅 분석 완료 시간: {current_time} 🔄 다음 보안 검토 권장 주기: 주 1회
""")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="확장된 보안 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = EnhancedSecurityReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
