#!/usr/bin/env python3
"""
Enhanced Database Analysis Report Generator
Shell 스크립트의 모든 기능을 Python으로 구현한 고도화된 데이터베이스 분석 보고서 생성기
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

class DatabaseReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 데이터 파일 경로
        self.data_files = {
            'rds_instances': 'database_rds_instances.json',
            'rds_clusters': 'database_rds_clusters.json',
            'rds_subnet_groups': 'database_rds_subnet_groups.json',
            'rds_parameter_groups': 'database_rds_parameter_groups.json',
            'elasticache_clusters': 'database_elasticache_clusters.json',
            'elasticache_replication_groups': 'database_elasticache_replication_groups.json',
            'opensearch_domains': 'database_opensearch_domains.json',
            'athena_workgroups': 'database_athena_workgroups.json',
            'dynamodb_tables': 'database_dynamodb_tables.json'
        }
        
        # 서비스 통계 초기화
        self.service_stats = {
            'rds_instances': 0,
            'rds_clusters': 0,
            'elasticache_clusters': 0,
            'opensearch_domains': 0,
            'athena_workgroups': 0,
            'active_services': 0,
            'total_services': 5
        }

    def load_json_data(self, filename: str) -> Optional[Dict]:
        """JSON 데이터 파일 로드"""
        file_path = self.report_dir / filename
        try:
            if file_path.exists() and file_path.stat().st_size > 16:  # 빈 파일이 아닌 경우
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('rows') and len(data['rows']) > 0:
                        return data
            return None
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.warning(f"데이터 파일 로드 실패: {filename} - {e}")
            return None

    def calculate_percentage(self, part: int, total: int) -> str:
        """백분율 계산"""
        if total == 0:
            return "0.0"
        return f"{(part * 100 / total):.1f}"

    def generate_executive_summary(self) -> str:
        """Executive Summary 생성"""
        # 서비스별 데이터 로드 및 카운트
        rds_instances_data = self.load_json_data(self.data_files['rds_instances'])
        rds_clusters_data = self.load_json_data(self.data_files['rds_clusters'])
        elasticache_clusters_data = self.load_json_data(self.data_files['elasticache_clusters'])
        opensearch_domains_data = self.load_json_data(self.data_files['opensearch_domains'])
        athena_workgroups_data = self.load_json_data(self.data_files['athena_workgroups'])
        
        # 통계 업데이트
        self.service_stats['rds_instances'] = len(rds_instances_data['rows']) if rds_instances_data else 0
        self.service_stats['rds_clusters'] = len(rds_clusters_data['rows']) if rds_clusters_data else 0
        self.service_stats['elasticache_clusters'] = len(elasticache_clusters_data['rows']) if elasticache_clusters_data else 0
        self.service_stats['opensearch_domains'] = len(opensearch_domains_data['rows']) if opensearch_domains_data else 0
        self.service_stats['athena_workgroups'] = len(athena_workgroups_data['rows']) if athena_workgroups_data else 0
        
        # 활성 서비스 카운트
        active_services = sum([
            1 if self.service_stats['rds_instances'] > 0 else 0,
            1 if self.service_stats['rds_clusters'] > 0 else 0,
            1 if self.service_stats['elasticache_clusters'] > 0 else 0,
            1 if self.service_stats['opensearch_domains'] > 0 else 0,
            1 if self.service_stats['athena_workgroups'] > 0 else 0
        ])
        self.service_stats['active_services'] = active_services
        
        summary = f"""# 🗄️ 데이터베이스 리소스 종합 분석

> **분석 일시**: {self.current_time}  
> **분석 대상**: AWS 계정 내 모든 데이터베이스 서비스  
> **분석 리전**: ap-northeast-2 (서울)

## 📊 Executive Summary

### 데이터베이스 서비스 현황 개요

| 서비스 | 리소스 수 | 상태 |
|--------|-----------|------|
| 🏛️ RDS 인스턴스 | {self.service_stats['rds_instances']}개 | {'✅ 활성' if self.service_stats['rds_instances'] > 0 else '❌ 없음'} |
| 🏛️ RDS 클러스터 (Aurora) | {self.service_stats['rds_clusters']}개 | {'✅ 활성' if self.service_stats['rds_clusters'] > 0 else '❌ 없음'} |
| ⚡ ElastiCache 클러스터 | {self.service_stats['elasticache_clusters']}개 | {'✅ 활성' if self.service_stats['elasticache_clusters'] > 0 else '❌ 없음'} |
| 🔍 OpenSearch 도메인 | {self.service_stats['opensearch_domains']}개 | {'✅ 활성' if self.service_stats['opensearch_domains'] > 0 else '❌ 없음'} |
| 📊 Athena 워크그룹 | {self.service_stats['athena_workgroups']}개 | {'✅ 활성' if self.service_stats['athena_workgroups'] > 0 else '❌ 없음'} |

**활성 데이터베이스 서비스**: {active_services}/{self.service_stats['total_services']}개

---

"""
        return summary

    def analyze_rds_instances(self) -> str:
        """RDS 인스턴스 상세 분석"""
        rds_data = self.load_json_data(self.data_files['rds_instances'])
        
        if not rds_data:
            return """## 🏛️ Amazon RDS 상세 분석

### RDS 인스턴스 현황
❌ RDS 인스턴스 데이터를 찾을 수 없습니다.

"""
        
        instances = rds_data['rows']
        total_count = len(instances)
        available_count = len([i for i in instances if i.get('status') == 'available'])
        encrypted_count = len([i for i in instances if i.get('storage_encrypted') == True])
        multi_az_count = len([i for i in instances if i.get('multi_az') == True])
        public_count = len([i for i in instances if i.get('publicly_accessible') == True])
        
        # 엔진별 분포 계산
        engine_stats = {}
        for instance in instances:
            engine = instance.get('engine', 'Unknown')
            if engine not in engine_stats:
                engine_stats[engine] = {'count': 0, 'version': instance.get('engine_version', 'N/A')}
            engine_stats[engine]['count'] += 1
        
        analysis = f"""## 🏛️ Amazon RDS 상세 분석

### RDS 인스턴스 현황

**📈 RDS 인스턴스 통계**
- **총 인스턴스 수**: {total_count}개
- **사용 가능한 인스턴스**: {available_count}개 ({self.calculate_percentage(available_count, total_count)}%)
- **암호화된 인스턴스**: {encrypted_count}개 ({self.calculate_percentage(encrypted_count, total_count)}%)
- **Multi-AZ 구성**: {multi_az_count}개 ({self.calculate_percentage(multi_az_count, total_count)}%)

#### 📋 RDS 인스턴스 상세 목록

| DB 식별자 | 엔진 | 버전 | 클래스 | 스토리지 | 상태 | Multi-AZ | 암호화 | 공개 접근 |
|-----------|------|------|-------|----------|------|----------|--------|-----------|
"""
        
        # 인스턴스 상세 목록
        for instance in instances:
            db_id = instance.get('db_instance_identifier', 'N/A')
            engine = instance.get('engine', 'N/A')
            version = instance.get('engine_version', 'N/A')
            instance_class = instance.get('class', 'N/A')
            storage = f"{instance.get('allocated_storage', 0)}GB ({instance.get('storage_type', 'N/A')})"
            status = instance.get('status', 'N/A')
            multi_az = "✅" if instance.get('multi_az') else "❌"
            encrypted = "🔒" if instance.get('storage_encrypted') else "🔓"
            public = "🌐" if instance.get('publicly_accessible') else "🔒"
            
            analysis += f"| {db_id} | {engine} | {version} | {instance_class} | {storage} | {status} | {multi_az} | {encrypted} | {public} |\n"
        
        # 엔진별 분포
        analysis += f"""
#### 🔧 엔진별 분포 및 버전 분석

| 엔진 | 개수 | 최신 버전 | 권장사항 |
|------|------|-----------|----------|
"""
        
        for engine, stats in engine_stats.items():
            analysis += f"| {engine} | {stats['count']}개 | {stats['version']} | 버전 업데이트 검토 |\n"
        
        # 보안 설정 분석
        analysis += f"""
#### 🔐 보안 설정 분석

**암호화 현황**:
- 저장 시 암호화: {encrypted_count}/{total_count}개 인스턴스
- 권장사항: {'✅ 모든 인스턴스가 암호화됨' if encrypted_count == total_count else '⚠️ 암호화되지 않은 인스턴스 존재'}

**네트워크 보안**:
- 공개 접근 가능: {public_count}/{total_count}개 인스턴스
- 권장사항: {'✅ 모든 인스턴스가 비공개' if public_count == 0 else '⚠️ 공개 접근 가능한 인스턴스 검토 필요'}

"""
        return analysis

    def analyze_rds_clusters(self) -> str:
        """RDS 클러스터 (Aurora) 상세 분석"""
        clusters_data = self.load_json_data(self.data_files['rds_clusters'])
        
        if not clusters_data:
            return """### RDS 클러스터 (Aurora) 분석
❌ RDS 클러스터 데이터를 찾을 수 없습니다.

"""
        
        clusters = clusters_data['rows']
        total_count = len(clusters)
        available_count = len([c for c in clusters if c.get('status') == 'available'])
        encrypted_count = len([c for c in clusters if c.get('storage_encrypted') == True])
        
        analysis = f"""### RDS 클러스터 (Aurora) 분석

**📈 Aurora 클러스터 통계**
- **총 클러스터 수**: {total_count}개
- **사용 가능한 클러스터**: {available_count}개
- **암호화된 클러스터**: {encrypted_count}개 ({self.calculate_percentage(encrypted_count, total_count)}%)

#### 📋 Aurora 클러스터 상세 목록

| 클러스터 식별자 | 엔진 | 버전 | 상태 | 멤버 수 | 백업 보존 | 암호화 | 엔드포인트 |
|-----------------|------|------|------|---------|-----------|--------|------------|
"""
        
        # 클러스터 상세 목록
        for cluster in clusters:
            cluster_id = cluster.get('db_cluster_identifier', 'N/A')
            engine = cluster.get('engine', 'N/A')
            version = cluster.get('engine_version', 'N/A')
            status = cluster.get('status', 'N/A')
            members_count = len(cluster.get('members', []))
            backup_retention = f"{cluster.get('backup_retention_period', 0)}일"
            encrypted = "🔒" if cluster.get('storage_encrypted') else "🔓"
            endpoint = cluster.get('endpoint', 'N/A')
            
            analysis += f"| {cluster_id} | {engine} | {version} | {status} | {members_count} | {backup_retention} | {encrypted} | {endpoint} |\n"
        
        # 백업 설정 분석
        backup_periods = {}
        for cluster in clusters:
            period = cluster.get('backup_retention_period', 0)
            backup_periods[period] = backup_periods.get(period, 0) + 1
        
        analysis += f"""
#### 🔄 백업 및 복구 설정

**백업 보존 기간 분석**:
"""
        
        for period, count in backup_periods.items():
            analysis += f"- {period}일: {count}개 클러스터\n"
        
        analysis += "\n**백업 윈도우**:\n"
        for cluster in clusters:
            cluster_id = cluster.get('db_cluster_identifier', 'N/A')
            backup_window = cluster.get('preferred_backup_window', 'N/A')
            maintenance_window = cluster.get('preferred_maintenance_window', 'N/A')
            analysis += f"- {cluster_id}: {backup_window} (유지보수: {maintenance_window})\n"
        
        analysis += "\n"
        return analysis

    def analyze_elasticache(self) -> str:
        """ElastiCache 상세 분석"""
        clusters_data = self.load_json_data(self.data_files['elasticache_clusters'])
        replication_data = self.load_json_data(self.data_files['elasticache_replication_groups'])
        
        analysis = """---

## ⚡ Amazon ElastiCache 상세 분석

### ElastiCache 클러스터 현황
"""
        
        if not clusters_data:
            analysis += "❌ ElastiCache 클러스터 데이터를 찾을 수 없습니다.\n\n"
        else:
            clusters = clusters_data['rows']
            total_count = len(clusters)
            available_count = len([c for c in clusters if c.get('cache_cluster_status') == 'available'])
            auto_upgrade_count = len([c for c in clusters if c.get('auto_minor_version_upgrade') == True])
            
            # 엔진별 통계
            engine_stats = {}
            for cluster in clusters:
                engine = cluster.get('engine', 'Unknown')
                if engine not in engine_stats:
                    engine_stats[engine] = {
                        'count': 0,
                        'total_nodes': 0,
                        'node_types': set()
                    }
                engine_stats[engine]['count'] += 1
                engine_stats[engine]['total_nodes'] += cluster.get('num_cache_nodes', 0)
                engine_stats[engine]['node_types'].add(cluster.get('cache_node_type', 'N/A'))
            
            analysis += f"""
**📈 ElastiCache 클러스터 통계**
- **총 클러스터 수**: {total_count}개
- **사용 가능한 클러스터**: {available_count}개
- **가용성**: {self.calculate_percentage(available_count, total_count)}%

#### 📋 ElastiCache 클러스터 상세 목록

| 클러스터 ID | 엔진 | 버전 | 노드 타입 | 상태 | 노드 수 | AZ | 복제 그룹 |
|-------------|------|------|-----------|------|---------|----|-----------| 
"""
            
            # 클러스터 상세 목록
            for cluster in clusters:
                cluster_id = cluster.get('cache_cluster_id', 'N/A')
                engine = cluster.get('engine', 'N/A')
                version = cluster.get('engine_version', 'N/A')
                node_type = cluster.get('cache_node_type', 'N/A')
                status = cluster.get('cache_cluster_status', 'N/A')
                num_nodes = cluster.get('num_cache_nodes', 0)
                az = cluster.get('preferred_availability_zone', 'N/A')
                repl_group = cluster.get('replication_group_id', '없음')
                
                analysis += f"| {cluster_id} | {engine} | {version} | {node_type} | {status} | {num_nodes} | {az} | {repl_group} |\n"
            
            # 엔진별 분포
            analysis += f"""
#### 🔧 엔진별 분포

| 엔진 | 클러스터 수 | 평균 노드 수 | 주요 노드 타입 |
|------|-------------|--------------|----------------|
"""
            
            for engine, stats in engine_stats.items():
                avg_nodes = stats['total_nodes'] / stats['count'] if stats['count'] > 0 else 0
                main_node_type = list(stats['node_types'])[0] if stats['node_types'] else 'N/A'
                analysis += f"| {engine} | {stats['count']}개 | {avg_nodes:.1f}개 | {main_node_type} |\n"
            
            # 유지보수 설정
            analysis += f"""
#### ⚙️ 유지보수 및 업그레이드 설정

**자동 마이너 버전 업그레이드**:
- 활성화된 클러스터: {auto_upgrade_count}/{total_count}개
- 권장사항: {'✅ 모든 클러스터에서 활성화됨' if auto_upgrade_count == total_count else '⚠️ 일부 클러스터에서 비활성화됨'}

**유지보수 윈도우**:
"""
            
            for cluster in clusters:
                cluster_id = cluster.get('cache_cluster_id', 'N/A')
                maintenance_window = cluster.get('preferred_maintenance_window', 'N/A')
                analysis += f"- {cluster_id}: {maintenance_window}\n"
        
        # 복제 그룹 분석
        analysis += "\n### ElastiCache 복제 그룹 분석\n"
        
        if not replication_data:
            analysis += "❌ ElastiCache 복제 그룹 데이터를 찾을 수 없습니다.\n\n"
        else:
            repl_groups = replication_data['rows']
            total_repl = len(repl_groups)
            available_repl = len([r for r in repl_groups if r.get('status') == 'available'])
            transit_encrypted = len([r for r in repl_groups if r.get('transit_encryption_enabled') == True])
            rest_encrypted = len([r for r in repl_groups if r.get('at_rest_encryption_enabled') == True])
            
            analysis += f"""
**📈 복제 그룹 통계**
- **총 복제 그룹**: {total_repl}개
- **사용 가능한 그룹**: {available_repl}개

#### 📋 복제 그룹 상세 목록

| 복제 그룹 ID | 설명 | 상태 | 노드 타입 | 멤버 수 | 자동 장애조치 | Multi-AZ |
|--------------|------|------|-----------|---------|---------------|----------|
"""
            
            for group in repl_groups:
                group_id = group.get('replication_group_id', 'N/A')
                description = group.get('description', 'N/A')
                status = group.get('status', 'N/A')
                node_type = group.get('cache_node_type', 'N/A')
                member_count = len(group.get('member_clusters', []))
                auto_failover = "✅" if group.get('automatic_failover') == 'enabled' else "❌"
                multi_az = "✅" if group.get('multi_az') == 'enabled' else "❌"
                
                analysis += f"| {group_id} | {description} | {status} | {node_type} | {member_count} | {auto_failover} | {multi_az} |\n"
            
            # 보안 및 암호화 설정
            analysis += f"""
#### 🔐 보안 및 암호화 설정

**전송 중 암호화**:
- 활성화된 그룹: {transit_encrypted}/{total_repl}개

**저장 시 암호화**:
- 활성화된 그룹: {rest_encrypted}/{total_repl}개

"""
        
        return analysis

    def analyze_opensearch(self) -> str:
        """OpenSearch 상세 분석"""
        opensearch_data = self.load_json_data(self.data_files['opensearch_domains'])
        
        analysis = """---

## 🔍 Amazon OpenSearch 상세 분석

### OpenSearch 도메인 현황
"""
        
        if not opensearch_data:
            analysis += "❌ OpenSearch 도메인 데이터를 찾을 수 없습니다.\n\n"
            return analysis
        
        domains = opensearch_data['rows']
        total_count = len(domains)
        processing_count = len([d for d in domains if d.get('processing') == True])
        
        analysis += f"""
**📈 OpenSearch 도메인 통계**
- **총 도메인 수**: {total_count}개
- **처리 중인 도메인**: {processing_count}개

#### 📋 OpenSearch 도메인 상세 목록

| 도메인명 | 엔진 버전 | 엔드포인트 | 처리 상태 | 생성일 | 삭제일 |
|----------|-----------|------------|-----------|--------|--------|
"""
        
        # 도메인 상세 목록
        for domain in domains:
            domain_name = domain.get('domain_name', 'N/A')
            engine_version = domain.get('engine_version', 'N/A')
            endpoint = domain.get('endpoint', 'N/A')
            processing_status = "🔄 처리중" if domain.get('processing') else "✅ 완료"
            created = str(domain.get('created', 'N/A'))
            deleted = str(domain.get('deleted', 'N/A'))
            
            analysis += f"| {domain_name} | {engine_version} | {endpoint} | {processing_status} | {created} | {deleted} |\n"
        
        # 클러스터 구성 분석
        analysis += f"""
#### ⚙️ 클러스터 구성 분석

**인스턴스 구성**:
"""
        
        for domain in domains:
            domain_name = domain.get('domain_name', 'N/A')
            cluster_config = domain.get('cluster_config', {})
            instance_type = cluster_config.get('instance_type', 'N/A')
            instance_count = cluster_config.get('instance_count', 0)
            analysis += f"- **{domain_name}**: {instance_type} ({instance_count}개 인스턴스)\n"
        
        # 보안 및 네트워크 설정
        analysis += f"""
#### 🔐 보안 및 네트워크 설정

**VPC 구성**:
"""
        
        for domain in domains:
            domain_name = domain.get('domain_name', 'N/A')
            vpc_options = domain.get('vpc_options')
            if vpc_options and vpc_options.get('subnet_ids'):
                subnet_count = len(vpc_options.get('subnet_ids', []))
                analysis += f"- **{domain_name}**: VPC 내부 배치 (서브넷: {subnet_count}개)\n"
            else:
                analysis += f"- **{domain_name}**: 퍼블릭 액세스\n"
        
        analysis += f"""
**저장 시 암호화**:
"""
        
        for domain in domains:
            domain_name = domain.get('domain_name', 'N/A')
            encryption_options = domain.get('encryption_at_rest_options', {})
            encrypted = "🔒 활성화" if encryption_options.get('enabled') else "🔓 비활성화"
            analysis += f"- **{domain_name}**: {encrypted}\n"
        
        analysis += "\n"
        return analysis

    def analyze_athena(self) -> str:
        """Athena 상세 분석"""
        athena_data = self.load_json_data(self.data_files['athena_workgroups'])
        
        analysis = """---

## 📊 Amazon Athena 분석

### Athena 워크그룹 현황
"""
        
        if not athena_data:
            analysis += "❌ Athena 워크그룹 데이터를 찾을 수 없습니다.\n\n"
            return analysis
        
        workgroups = athena_data['rows']
        total_count = len(workgroups)
        enabled_count = len([w for w in workgroups if w.get('state') == 'ENABLED'])
        
        analysis += f"""
**📈 Athena 워크그룹 통계**
- **총 워크그룹 수**: {total_count}개
- **활성화된 워크그룹**: {enabled_count}개

#### 📋 Athena 워크그룹 상세 목록

| 워크그룹명 | 설명 | 상태 | 생성일 | 출력 위치 | 암호화 |
|------------|------|------|--------|-----------|--------|
"""
        
        # 워크그룹 상세 목록
        for workgroup in workgroups:
            name = workgroup.get('name', 'N/A')
            description = workgroup.get('description', 'N/A')
            state = workgroup.get('state', 'N/A')
            creation_time = workgroup.get('creation_time', 'N/A')
            output_location = workgroup.get('output_location', 'N/A')
            encryption_option = workgroup.get('encryption_option', '없음')
            
            analysis += f"| {name} | {description} | {state} | {creation_time} | {output_location} | {encryption_option} |\n"
        
        analysis += "\n"
        return analysis
    def generate_recommendations(self) -> str:
        """종합 권장사항 생성"""
        rds_data = self.load_json_data(self.data_files['rds_instances'])
        replication_data = self.load_json_data(self.data_files['elasticache_replication_groups'])
        
        recommendations = """---

## 📋 종합 권장사항 및 개선 계획

### 🔴 높은 우선순위 (즉시 조치 필요)

#### 보안 강화
"""
        
        # RDS 보안 권장사항
        if rds_data:
            instances = rds_data['rows']
            unencrypted_rds = len([i for i in instances if not i.get('storage_encrypted')])
            public_rds = len([i for i in instances if i.get('publicly_accessible')])
            
            if unencrypted_rds > 0:
                recommendations += f"1. **RDS 암호화 미적용**: {unencrypted_rds}개 인스턴스에 저장 시 암호화 적용 필요\n"
            
            if public_rds > 0:
                recommendations += f"2. **RDS 공개 접근**: {public_rds}개 인스턴스의 공개 접근 설정 검토 및 제한 필요\n"
        
        # ElastiCache 보안 권장사항
        if replication_data:
            groups = replication_data['rows']
            unencrypted_cache = len([g for g in groups if not g.get('at_rest_encryption_enabled') or not g.get('transit_encryption_enabled')])
            
            if unencrypted_cache > 0:
                recommendations += f"3. **ElastiCache 암호화**: {unencrypted_cache}개 복제 그룹에 전송/저장 암호화 적용 필요\n"
        
        recommendations += """
#### 고가용성 구성
"""
        
        # RDS Multi-AZ 권장사항
        if rds_data:
            instances = rds_data['rows']
            non_multi_az = len([i for i in instances if not i.get('multi_az')])
            
            if non_multi_az > 0:
                recommendations += f"1. **Multi-AZ 미구성**: {non_multi_az}개 RDS 인스턴스에 Multi-AZ 구성 검토\n"
        
        # ElastiCache 자동 장애조치 권장사항
        if replication_data:
            groups = replication_data['rows']
            non_failover_cache = len([g for g in groups if g.get('automatic_failover') != 'enabled'])
            
            if non_failover_cache > 0:
                recommendations += f"2. **ElastiCache 자동 장애조치**: {non_failover_cache}개 복제 그룹에 자동 장애조치 활성화 필요\n"
        
        recommendations += """
### 🟡 중간 우선순위 (1-3개월 내 조치)

#### 성능 최적화
1. **Performance Insights 활성화**: RDS 인스턴스 성능 모니터링 강화
2. **ElastiCache 노드 타입 최적화**: 워크로드에 맞는 인스턴스 타입 검토
3. **OpenSearch 클러스터 크기 조정**: 사용 패턴 기반 최적화

#### 백업 및 복구
1. **백업 보존 기간 표준화**: 비즈니스 요구사항에 맞는 백업 정책 수립
2. **Point-in-Time Recovery 테스트**: 정기적인 복구 테스트 수행
3. **Cross-Region 백업**: 재해 복구를 위한 다중 리전 백업 고려

### 🟢 낮은 우선순위 (장기 계획)

#### 비용 최적화
1. **Reserved Instance 활용**: 장기 실행 데이터베이스 비용 절감
2. **Aurora Serverless 검토**: 가변 워크로드에 대한 서버리스 옵션 평가
3. **스토리지 타입 최적화**: gp3 스토리지 활용 검토

#### 현대화 및 마이그레이션
1. **Aurora 마이그레이션**: 기존 RDS를 Aurora로 마이그레이션 검토
2. **DynamoDB 활용**: NoSQL 요구사항에 대한 DynamoDB 도입 검토
3. **OpenSearch 최신 버전**: 엔진 버전 업그레이드 계획

---

## 📊 모니터링 및 알림 설정

### 권장 CloudWatch 메트릭
1. **RDS**: CPU 사용률, 연결 수, 읽기/쓰기 지연시간
2. **ElastiCache**: CPU 사용률, 메모리 사용률, 캐시 히트율
3. **OpenSearch**: 클러스터 상태, 검색 지연시간, 인덱싱 속도

### 알림 임계값 권장사항
- **RDS CPU**: 80% 이상 지속 시 알림
- **ElastiCache 메모리**: 90% 이상 사용 시 알림
- **OpenSearch 클러스터**: Yellow/Red 상태 시 즉시 알림

---

## 💰 예상 비용 분석

### 월간 예상 비용 (추정)
- **RDS 인스턴스**: 인스턴스 타입 및 스토리지 기반 비용 계산 필요
- **ElastiCache**: 노드 타입 및 개수 기반 비용 계산 필요
- **OpenSearch**: 인스턴스 타입 및 스토리지 기반 비용 계산 필요

### 비용 최적화 기회
1. **인스턴스 크기 조정**: 사용률 모니터링 후 적절한 크기로 조정
2. **예약 인스턴스**: 1년 또는 3년 약정으로 최대 75% 비용 절감
3. **스토리지 최적화**: 사용하지 않는 스냅샷 정리 및 스토리지 타입 최적화

---

*📅 분석 완료 시간: {self.current_time}*  
*🔄 다음 분석 권장 주기: 월 1회*

---
"""
        return recommendations

    def generate_report(self) -> str:
        """전체 보고서 생성"""
        self.logger.info("🗄️ Enhanced Database Analysis 보고서 생성 시작...")
        
        # 각 섹션 생성
        executive_summary = self.generate_executive_summary()
        rds_analysis = self.analyze_rds_instances()
        rds_clusters = self.analyze_rds_clusters()
        elasticache_analysis = self.analyze_elasticache()
        opensearch_analysis = self.analyze_opensearch()
        athena_analysis = self.analyze_athena()
        recommendations = self.generate_recommendations()
        
        # 전체 보고서 조합
        full_report = (
            executive_summary +
            rds_analysis +
            rds_clusters +
            elasticache_analysis +
            opensearch_analysis +
            athena_analysis +
            recommendations
        )
        
        return full_report

    def save_report(self, content: str, filename: str = "05-database-analysis.md") -> None:
        """보고서를 파일로 저장"""
        output_path = self.report_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"✅ Enhanced Database Analysis 생성 완료: {filename}")
            
            # 파일 크기 정보
            file_size = output_path.stat().st_size
            self.logger.info(f"📄 보고서 크기: {file_size:,} bytes")
            
        except Exception as e:
            self.logger.error(f"❌ 보고서 저장 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    try:
        # 보고서 생성기 초기화
        generator = DatabaseReportGenerator()
        
        # 보고서 생성
        report_content = generator.generate_report()
        
        # 보고서 저장
        generator.save_report(report_content)
        
        print("🎉 Enhanced Database Analysis 보고서 생성이 완료되었습니다!")
        
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
