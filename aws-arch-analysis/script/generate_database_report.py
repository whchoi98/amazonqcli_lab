#!/usr/bin/env python3
"""
데이터베이스 분석 보고서 생성 스크립트 (Python 버전)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class DatabaseReportGenerator:
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

    def write_rds_analysis(self, report_file, rds_data: Optional[List]) -> None:
        """RDS 분석 섹션을 작성합니다."""
        report_file.write("## 🗄️ RDS 데이터베이스 현황\n\n")
        
        if not rds_data:
            report_file.write("RDS 인스턴스 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_instances = len(rds_data)
        multi_az_count = len([r for r in rds_data if r.get('multi_az', False)])
        encrypted_count = len([r for r in rds_data if r.get('storage_encrypted', False)])
        
        report_file.write(f"**총 RDS 인스턴스:** {total_instances}개\n")
        report_file.write(f"- **Multi-AZ 배포:** {multi_az_count}개\n")
        report_file.write(f"- **암호화된 인스턴스:** {encrypted_count}개\n\n")
        
        # 엔진별 분포
        engine_stats = {}
        for instance in rds_data:
            engine = instance.get('engine', 'unknown')
            if engine not in engine_stats:
                engine_stats[engine] = 0
            engine_stats[engine] += 1
        
        report_file.write("### 데이터베이스 엔진별 분포\n")
        report_file.write("| 엔진 | 인스턴스 수 |\n")
        report_file.write("|------|-------------|\n")
        for engine, count in engine_stats.items():
            report_file.write(f"| {engine} | {count} |\n")
        
        # 상세 목록
        report_file.write("\n### RDS 인스턴스 상세 목록\n")
        report_file.write("| 인스턴스 ID | 엔진 | 클래스 | 상태 | Multi-AZ | 암호화 | 백업 보존 |\n")
        report_file.write("|-------------|------|--------|------|----------|--------|------------|\n")
        
        for instance in rds_data:
            db_id = instance.get('db_instance_identifier', 'N/A')
            engine = instance.get('engine', 'N/A')
            db_class = instance.get('db_instance_class', 'N/A')
            status = instance.get('db_instance_status', 'N/A')
            multi_az = '예' if instance.get('multi_az', False) else '아니오'
            encrypted = '예' if instance.get('storage_encrypted', False) else '아니오'
            backup_retention = f"{instance.get('backup_retention_period', 0)}일"
            
            report_file.write(f"| {db_id} | {engine} | {db_class} | {status} | {multi_az} | {encrypted} | {backup_retention} |\n")
        
        if total_instances > 10:
            report_file.write(f"... 및 {total_instances - 10}개 추가 인스턴스\n")
        
        report_file.write("\n")

    def write_dynamodb_analysis(self, report_file, dynamodb_data: Optional[List]) -> None:
        """DynamoDB 분석 섹션을 작성합니다."""
        report_file.write("## ⚡ DynamoDB 테이블 현황\n\n")
        
        if not dynamodb_data:
            report_file.write("DynamoDB 테이블 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_tables = len(dynamodb_data)
        on_demand_count = len([t for t in dynamodb_data if t.get('billing_mode_summary', {}).get('billing_mode') == 'PAY_PER_REQUEST'])
        provisioned_count = total_tables - on_demand_count
        
        report_file.write(f"**총 DynamoDB 테이블:** {total_tables}개\n")
        report_file.write(f"- **온디맨드 모드:** {on_demand_count}개\n")
        report_file.write(f"- **프로비저닝 모드:** {provisioned_count}개\n\n")
        
        # 상세 목록
        report_file.write("### DynamoDB 테이블 상세 목록\n")
        report_file.write("| 테이블 이름 | 상태 | 빌링 모드 | 생성일 | GSI 수 |\n")
        report_file.write("|-------------|------|-----------|--------|--------|\n")
        
        for table in dynamodb_data:
            table_name = table.get('table_name', 'N/A')
            status = table.get('table_status', 'N/A')
            billing_mode = table.get('billing_mode_summary', {}).get('billing_mode', 'N/A')
            creation_date = table.get('creation_date_time', 'N/A')[:10] if table.get('creation_date_time') else 'N/A'
            gsi_count = len(table.get('global_secondary_indexes', []))
            
            report_file.write(f"| {table_name} | {status} | {billing_mode} | {creation_date} | {gsi_count} |\n")
        
        if total_tables > 10:
            report_file.write(f"... 및 {total_tables - 10}개 추가 테이블\n")
        
        report_file.write("\n")

    def write_elasticache_analysis(self, report_file, elasticache_data: Optional[List]) -> None:
        """ElastiCache 분석 섹션을 작성합니다."""
        report_file.write("## 🚀 ElastiCache 클러스터 현황\n\n")
        
        if not elasticache_data:
            report_file.write("ElastiCache 클러스터 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_clusters = len(elasticache_data)
        redis_count = len([c for c in elasticache_data if c.get('engine') == 'redis'])
        memcached_count = len([c for c in elasticache_data if c.get('engine') == 'memcached'])
        
        report_file.write(f"**총 ElastiCache 클러스터:** {total_clusters}개\n")
        report_file.write(f"- **Redis:** {redis_count}개\n")
        report_file.write(f"- **Memcached:** {memcached_count}개\n\n")
        
        # 상세 목록
        report_file.write("### ElastiCache 클러스터 상세 목록\n")
        report_file.write("| 클러스터 ID | 엔진 | 노드 타입 | 상태 | 노드 수 | 암호화 |\n")
        report_file.write("|-------------|------|-----------|------|---------|--------|\n")
        
        for cluster in elasticache_data:
            cluster_id = cluster.get('cache_cluster_id', 'N/A')
            engine = cluster.get('engine', 'N/A')
            node_type = cluster.get('cache_node_type', 'N/A')
            status = cluster.get('cache_cluster_status', 'N/A')
            num_nodes = cluster.get('num_cache_nodes', 0)
            encrypted = '예' if cluster.get('at_rest_encryption_enabled', False) else '아니오'
            
            report_file.write(f"| {cluster_id} | {engine} | {node_type} | {status} | {num_nodes} | {encrypted} |\n")
        
        if total_clusters > 10:
            report_file.write(f"... 및 {total_clusters - 10}개 추가 클러스터\n")
        
        report_file.write("\n")

    def write_database_recommendations(self, report_file, rds_data: Optional[List], dynamodb_data: Optional[List]) -> None:
        """데이터베이스 권장사항 섹션을 작성합니다."""
        report_file.write("## 📋 데이터베이스 최적화 권장사항\n\n")
        
        report_file.write("### 🔴 높은 우선순위\n")
        
        recommendations = []
        
        # RDS 관련 권장사항
        if rds_data:
            unencrypted_rds = [r for r in rds_data if not r.get('storage_encrypted', False)]
            single_az_rds = [r for r in rds_data if not r.get('multi_az', False)]
            
            if unencrypted_rds:
                recommendations.append(f"**RDS 암호화**: {len(unencrypted_rds)}개의 암호화되지 않은 RDS 인스턴스가 있습니다. 데이터 보안을 위해 암호화를 활성화하세요.")
            
            if single_az_rds:
                recommendations.append(f"**RDS 고가용성**: {len(single_az_rds)}개의 Single-AZ RDS 인스턴스가 있습니다. 프로덕션 환경에서는 Multi-AZ 배포를 고려하세요.")
        
        # 기본 권장사항
        if not recommendations:
            recommendations = [
                "**백업 정책 검토**: 모든 데이터베이스의 백업 보존 기간과 백업 윈도우를 검토하세요.",
                "**성능 모니터링**: CloudWatch를 통해 데이터베이스 성능 지표를 모니터링하세요."
            ]
        
        for i, rec in enumerate(recommendations, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n### 🟡 중간 우선순위\n")
        report_file.write("1. **읽기 전용 복제본**: 읽기 워크로드 분산을 위한 읽기 전용 복제본 구성을 고려하세요.\n")
        report_file.write("2. **파라미터 그룹 최적화**: 워크로드에 맞는 데이터베이스 파라미터 튜닝을 수행하세요.\n")
        report_file.write("3. **자동 백업 설정**: 자동 백업과 포인트 인 타임 복구 설정을 확인하세요.\n\n")
        
        report_file.write("### 🟢 낮은 우선순위\n")
        report_file.write("1. **성능 인사이트**: RDS Performance Insights를 활성화하여 성능 분석을 개선하세요.\n")
        report_file.write("2. **데이터베이스 프록시**: 연결 풀링을 위한 RDS Proxy 사용을 고려하세요.\n")
        report_file.write("3. **크로스 리전 복제**: 재해 복구를 위한 크로스 리전 복제를 검토하세요.\n\n")

    def generate_report(self):
        """데이터베이스 분석 보고서를 생성합니다."""
        print("🗄️ Database Analysis 보고서 생성 중...")
        
        # 데이터 파일 로드
        rds_data = self.load_json_file("database_rds_instances.json")
        dynamodb_data = self.load_json_file("database_dynamodb_tables.json")
        elasticache_data = self.load_json_file("database_elasticache_clusters.json")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "05-database-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 데이터베이스 분석\n\n")
                
                # 각 섹션 작성
                self.write_rds_analysis(report_file, rds_data)
                self.write_dynamodb_analysis(report_file, dynamodb_data)
                self.write_elasticache_analysis(report_file, elasticache_data)
                self.write_database_recommendations(report_file, rds_data, dynamodb_data)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*데이터베이스 분석 완료*\n")
            
            print("✅ Database Analysis 생성 완료: 05-database-analysis.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="데이터베이스 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = DatabaseReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
