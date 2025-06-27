#!/usr/bin/env python3
"""
확장된 스토리지 분석 보고서 생성 스크립트 (Python 버전)
모든 스토리지 리소스와 성능 메트릭 포함
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

class StorageReportGenerator:
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

    def write_ebs_analysis(self, report_file, ebs_data: Optional[List]) -> None:
        """EBS 볼륨 분석 섹션을 작성합니다."""
        report_file.write("## 💾 EBS 볼륨 현황\n\n")
        
        if not ebs_data:
            report_file.write("EBS 볼륨 데이터를 찾을 수 없습니다.\n\n")
            return
        
        # 기본 통계
        total_count = len(ebs_data)
        encrypted_count = len([v for v in ebs_data if v.get('encrypted', False)])
        available_count = len([v for v in ebs_data if v.get('state') == 'available'])
        in_use_count = len([v for v in ebs_data if v.get('state') == 'in-use'])
        total_size = sum([v.get('size', 0) for v in ebs_data])
        
        report_file.write("### EBS 볼륨 개요\n")
        report_file.write(f"**총 EBS 볼륨:** {total_count}개\n")
        report_file.write(f"- **사용 중:** {in_use_count}개\n")
        report_file.write(f"- **사용 가능:** {available_count}개\n")
        report_file.write(f"- **암호화됨:** {encrypted_count}개 ({round(encrypted_count/total_count*100, 1)}%)\n")
        report_file.write(f"- **총 용량:** {total_size} GB\n\n")
        
        # 전체 EBS 볼륨 상세 목록
        report_file.write(f"### EBS 볼륨 상세 목록 (전체 {total_count}개)\n")
        report_file.write("| 볼륨 ID | 타입 | 크기(GB) | 상태 | 암호화 | 가용영역 | 연결된 인스턴스 |\n")
        report_file.write("|---------|------|----------|------|--------|----------|------------------|\n")
        
        for volume in ebs_data:
            volume_id = volume.get('volume_id', 'N/A')
            volume_type = volume.get('volume_type', 'N/A')
            size = volume.get('size', 0)
            state = volume.get('state', 'N/A')
            encrypted = '예' if volume.get('encrypted', False) else '아니오'
            az = volume.get('availability_zone', 'N/A')
            
            # 연결된 인스턴스 정보
            attachments = volume.get('attachments', [])
            instance_id = attachments[0].get('instance_id', 'N/A') if attachments else '연결 안됨'
            
            report_file.write(f"| {volume_id} | {volume_type} | {size} | {state} | {encrypted} | {az} | {instance_id} |\n")
        
        # 볼륨 타입별 분포
        report_file.write("\n### 볼륨 타입별 분포\n")
        report_file.write("| 볼륨 타입 | 개수 | 총 용량(GB) | 비율 |\n")
        report_file.write("|-----------|------|-------------|------|\n")
        
        type_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        for volume in ebs_data:
            vol_type = volume.get('volume_type', 'Unknown')
            type_stats[vol_type]['count'] += 1
            type_stats[vol_type]['size'] += volume.get('size', 0)
        
        for vol_type, stats in sorted(type_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            count = stats['count']
            size = stats['size']
            percentage = round((count / total_count) * 100, 1)
            report_file.write(f"| {vol_type} | {count} | {size} | {percentage}% |\n")
        
        # 가용영역별 분포
        report_file.write("\n### 가용영역별 분포\n")
        report_file.write("| 가용영역 | 개수 | 총 용량(GB) |\n")
        report_file.write("|----------|------|-------------|\n")
        
        az_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        for volume in ebs_data:
            az = volume.get('availability_zone', 'Unknown')
            az_stats[az]['count'] += 1
            az_stats[az]['size'] += volume.get('size', 0)
        
        for az, stats in sorted(az_stats.items()):
            report_file.write(f"| {az} | {stats['count']} | {stats['size']} |\n")

    def write_ebs_performance_analysis(self, report_file) -> None:
        """EBS 성능 메트릭 분석 섹션을 작성합니다."""
        report_file.write("## 📊 EBS 성능 분석\n\n")
        
        # 읽기 IOPS 메트릭
        read_ops_data = self.load_json_file("storage_ebs_volume_metric_read_ops.json")
        write_ops_data = self.load_json_file("storage_ebs_volume_metric_write_ops.json")
        
        if read_ops_data or write_ops_data:
            report_file.write("### IOPS 성능 메트릭 (최근 1시간)\n")
            
            if read_ops_data:
                report_file.write(f"**읽기 IOPS 데이터 포인트:** {len(read_ops_data)}개\n")
                # 볼륨별 평균 읽기 IOPS 계산
                volume_read_iops = defaultdict(list)
                for metric in read_ops_data:
                    volume_id = metric.get('volume_id', 'Unknown')
                    average = metric.get('average', 0)
                    if average > 0:
                        volume_read_iops[volume_id].append(average)
                
                if volume_read_iops:
                    report_file.write("\n#### 볼륨별 평균 읽기 IOPS (상위 10개)\n")
                    report_file.write("| 볼륨 ID | 평균 읽기 IOPS | 최대 읽기 IOPS |\n")
                    report_file.write("|---------|----------------|----------------|\n")
                    
                    # 평균 IOPS 기준으로 정렬
                    sorted_volumes = sorted(volume_read_iops.items(), 
                                          key=lambda x: sum(x[1])/len(x[1]), reverse=True)[:10]
                    
                    for volume_id, iops_list in sorted_volumes:
                        avg_iops = round(sum(iops_list) / len(iops_list), 2)
                        max_iops = round(max(iops_list), 2)
                        report_file.write(f"| {volume_id} | {avg_iops} | {max_iops} |\n")
            
            if write_ops_data:
                report_file.write(f"\n**쓰기 IOPS 데이터 포인트:** {len(write_ops_data)}개\n")
                # 볼륨별 평균 쓰기 IOPS 계산
                volume_write_iops = defaultdict(list)
                for metric in write_ops_data:
                    volume_id = metric.get('volume_id', 'Unknown')
                    average = metric.get('average', 0)
                    if average > 0:
                        volume_write_iops[volume_id].append(average)
                
                if volume_write_iops:
                    report_file.write("\n#### 볼륨별 평균 쓰기 IOPS (상위 10개)\n")
                    report_file.write("| 볼륨 ID | 평균 쓰기 IOPS | 최대 쓰기 IOPS |\n")
                    report_file.write("|---------|----------------|----------------|\n")
                    
                    # 평균 IOPS 기준으로 정렬
                    sorted_volumes = sorted(volume_write_iops.items(), 
                                          key=lambda x: sum(x[1])/len(x[1]), reverse=True)[:10]
                    
                    for volume_id, iops_list in sorted_volumes:
                        avg_iops = round(sum(iops_list) / len(iops_list), 2)
                        max_iops = round(max(iops_list), 2)
                        report_file.write(f"| {volume_id} | {avg_iops} | {max_iops} |\n")
        else:
            report_file.write("EBS 성능 메트릭 데이터를 찾을 수 없습니다.\n")

    def write_s3_analysis(self, report_file) -> None:
        """S3 분석 섹션을 작성합니다."""
        report_file.write("\n## 🪣 S3 스토리지 분석\n\n")
        
        s3_data = self.load_json_file("storage_s3_buckets.json")
        
        if s3_data:
            bucket_count = len(s3_data)
            encrypted_buckets = len([b for b in s3_data if b.get('server_side_encryption_configuration')])
            versioning_enabled = len([b for b in s3_data if b.get('versioning_enabled', False)])
            public_buckets = len([b for b in s3_data if b.get('bucket_policy_is_public', False)])
            
            report_file.write("### S3 버킷 개요\n")
            report_file.write(f"**총 S3 버킷:** {bucket_count}개\n")
            report_file.write(f"- **암호화 설정:** {encrypted_buckets}개\n")
            report_file.write(f"- **버전 관리 활성화:** {versioning_enabled}개\n")
            report_file.write(f"- **퍼블릭 버킷:** {public_buckets}개\n\n")
            
            # 전체 S3 버킷 상세 목록
            report_file.write("### S3 버킷 상세 목록\n")
            report_file.write("| 버킷 이름 | 리전 | 생성일 | 버전 관리 | 암호화 | 퍼블릭 액세스 |\n")
            report_file.write("|-----------|------|--------|-----------|--------|---------------|\n")
            
            for bucket in s3_data:
                name = bucket.get('name', 'N/A')
                region = bucket.get('region', 'N/A')
                created = bucket.get('creation_date', 'N/A')[:10] if bucket.get('creation_date') else 'N/A'
                versioning = '활성화' if bucket.get('versioning_enabled', False) else '비활성화'
                encryption = '설정됨' if bucket.get('server_side_encryption_configuration') else '미설정'
                public = '예' if bucket.get('bucket_policy_is_public', False) else '아니오'
                
                report_file.write(f"| {name} | {region} | {created} | {versioning} | {encryption} | {public} |\n")
        else:
            report_file.write("S3 버킷 데이터를 찾을 수 없습니다.\n")

    def write_file_system_analysis(self, report_file) -> None:
        """파일 시스템 분석 섹션을 작성합니다."""
        report_file.write("\n## 📁 파일 시스템 분석\n\n")
        
        efs_data = self.load_json_file("storage_efs_file_systems.json")
        fsx_data = self.load_json_file("storage_fsx_file_systems.json")
        
        efs_count = len(efs_data) if efs_data else 0
        fsx_count = len(fsx_data) if fsx_data else 0
        
        report_file.write("### 파일 시스템 개요\n")
        report_file.write(f"**EFS 파일 시스템:** {efs_count}개\n")
        report_file.write(f"**FSx 파일 시스템:** {fsx_count}개\n\n")
        
        # EFS 상세 정보
        if efs_data:
            report_file.write("### EFS 파일 시스템 상세\n")
            report_file.write("| 파일 시스템 ID | 이름 | 성능 모드 | 처리량 모드 | 암호화 | 상태 |\n")
            report_file.write("|----------------|------|-----------|-------------|--------|------|\n")
            
            for efs in efs_data:
                fs_id = efs.get('file_system_id', 'N/A')
                name = efs.get('name', 'N/A')
                perf_mode = efs.get('performance_mode', 'N/A')
                throughput_mode = efs.get('throughput_mode', 'N/A')
                encrypted = '예' if efs.get('encrypted', False) else '아니오'
                state = efs.get('life_cycle_state', 'N/A')
                
                report_file.write(f"| {fs_id} | {name} | {perf_mode} | {throughput_mode} | {encrypted} | {state} |\n")
        
        # FSx 상세 정보
        if fsx_data:
            report_file.write("\n### FSx 파일 시스템 상세\n")
            report_file.write("| 파일 시스템 ID | 타입 | 스토리지 용량(GB) | 상태 | VPC ID |\n")
            report_file.write("|----------------|------|-------------------|------|--------|\n")
            
            for fsx in fsx_data:
                fs_id = fsx.get('file_system_id', 'N/A')
                fs_type = fsx.get('file_system_type', 'N/A')
                capacity = fsx.get('storage_capacity', 'N/A')
                state = fsx.get('lifecycle_state', 'N/A')
                vpc_id = fsx.get('vpc_id', 'N/A')
                
                report_file.write(f"| {fs_id} | {fs_type} | {capacity} | {state} | {vpc_id} |\n")
        
        if not efs_data and not fsx_data:
            report_file.write("파일 시스템 데이터를 찾을 수 없습니다.\n")

    def write_backup_analysis(self, report_file) -> None:
        """백업 분석 섹션을 작성합니다."""
        report_file.write("\n## 💾 백업 및 복구 분석\n\n")
        
        backup_vaults = self.load_json_file("storage_backup_vaults.json")
        backup_plans = self.load_json_file("storage_backup_plans.json")
        backup_jobs = self.load_json_file("storage_backup_jobs.json")
        
        vault_count = len(backup_vaults) if backup_vaults else 0
        plan_count = len(backup_plans) if backup_plans else 0
        job_count = len(backup_jobs) if backup_jobs else 0
        
        report_file.write("### 백업 서비스 개요\n")
        report_file.write(f"**AWS Backup 볼트:** {vault_count}개\n")
        report_file.write(f"**백업 계획:** {plan_count}개\n")
        report_file.write(f"**백업 작업:** {job_count}개\n\n")
        
        if backup_vaults:
            report_file.write("### AWS Backup 볼트 상세\n")
            report_file.write("| 볼트 이름 | 복구 포인트 수 | 생성일 | 암호화 키 |\n")
            report_file.write("|-----------|----------------|--------|----------|\n")
            
            for vault in backup_vaults:
                name = vault.get('name', 'N/A')
                recovery_points = vault.get('number_of_recovery_points', 0)
                created = vault.get('creation_date', 'N/A')[:10] if vault.get('creation_date') else 'N/A'
                kms_key = vault.get('encryption_key_arn', 'N/A')[-20:] if vault.get('encryption_key_arn') else 'N/A'
                
                report_file.write(f"| {name} | {recovery_points} | {created} | {kms_key} |\n")
        
        if not backup_vaults and not backup_plans and not backup_jobs:
            report_file.write("백업 서비스 데이터를 찾을 수 없습니다.\n")

    def write_recommendations(self, report_file) -> None:
        """스토리지 최적화 권장사항을 작성합니다."""
        report_file.write("\n## 📋 스토리지 최적화 권장사항\n\n")
        
        report_file.write("### 🔴 높은 우선순위\n")
        report_file.write("1. **EBS 볼륨 암호화**: 암호화되지 않은 볼륨에 대한 암호화 활성화\n")
        report_file.write("2. **미사용 EBS 볼륨 정리**: 'available' 상태의 볼륨 검토 및 정리\n")
        report_file.write("3. **S3 버킷 보안**: 퍼블릭 액세스 설정 검토 및 제한\n\n")
        
        report_file.write("### 🟡 중간 우선순위\n")
        report_file.write("1. **EBS 볼륨 타입 최적화**: 워크로드에 맞는 적절한 볼륨 타입 선택\n")
        report_file.write("2. **S3 라이프사이클 정책**: 데이터 사용 패턴에 따른 스토리지 클래스 최적화\n")
        report_file.write("3. **백업 정책 수립**: 중요 데이터에 대한 자동 백업 설정\n\n")
        
        report_file.write("### 🟢 낮은 우선순위\n")
        report_file.write("1. **EBS 성능 모니터링**: IOPS 사용률 기반 볼륨 타입 조정\n")
        report_file.write("2. **S3 버전 관리**: 중요 데이터에 대한 버전 관리 활성화\n")
        report_file.write("3. **파일 시스템 최적화**: EFS/FSx 성능 모드 및 처리량 설정 검토\n\n")

    def generate_report(self):
        """확장된 스토리지 분석 보고서를 생성합니다."""
        print("💾 확장된 Storage Analysis 보고서 생성 중...")
        
        # 데이터 파일 로드
        ebs_data = self.load_json_file("storage_ebs_volumes.json")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "04-storage-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 스토리지 리소스 분석\n\n")
                
                # 각 섹션 작성
                self.write_ebs_analysis(report_file, ebs_data)
                self.write_ebs_performance_analysis(report_file)
                self.write_s3_analysis(report_file)
                self.write_file_system_analysis(report_file)
                self.write_backup_analysis(report_file)
                self.write_recommendations(report_file)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*스토리지 리소스 분석 완료*\n")
            
            print("✅ 확장된 Storage Analysis 생성 완료: 04-storage-analysis.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="확장된 스토리지 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = StorageReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
