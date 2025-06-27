#!/usr/bin/env python3
"""
스토리지 분석 보고서 생성 스크립트 (Python 버전)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class StorageReportGenerator:
    def __init__(self, report_dir: str = "/home/ec2-user/amazonqcli_lab/report"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_json_file(self, filename: str) -> Optional[List[Dict[str, Any]]]:
        """JSON 파일을 로드합니다."""
        file_path = self.report_dir / filename
        try:
            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Steampipe 형식 처리
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
        report_file.write("### EBS 볼륨 개요\n")
        
        if not ebs_data:
            report_file.write("EBS 볼륨 데이터를 찾을 수 없습니다.\n\n")
            return
        
        # 통계 계산
        total_count = len(ebs_data)
        encrypted_count = len([v for v in ebs_data if v.get('encrypted', False)])
        available_count = len([v for v in ebs_data if v.get('state') == 'available'])
        in_use_count = len([v for v in ebs_data if v.get('state') == 'in-use'])
        total_size = sum([v.get('size', 0) for v in ebs_data])
        
        report_file.write(f"**총 EBS 볼륨:** {total_count}개\n")
        report_file.write(f"- **사용 중:** {in_use_count}개\n")
        report_file.write(f"- **미사용 볼륨:** {available_count}개\n")
        report_file.write(f"- **암호화된 볼륨:** {encrypted_count}개\n")
        report_file.write(f"- **총 스토리지 크기:** {total_size}GB\n\n")
        
        # 상세 목록
        report_file.write("### EBS 볼륨 상세 목록\n")
        report_file.write("| 볼륨 ID | 타입 | 크기 | 상태 | 암호화 | AZ | 연결된 인스턴스 |\n")
        report_file.write("|---------|------|------|------|--------|----|-----------------|\n")
        
        for volume in ebs_data[:10]:  # 최대 10개만 표시
            volume_id = volume.get('volume_id', 'N/A')
            volume_type = volume.get('volume_type', 'N/A')
            size = volume.get('size', 0)
            state = volume.get('state', 'N/A')
            encrypted = '예' if volume.get('encrypted', False) else '아니오'
            az = volume.get('availability_zone', 'N/A')
            
            # 연결된 인스턴스 확인
            attachments = volume.get('attachments', [])
            instance_id = attachments[0].get('instance_id', '없음') if attachments else '없음'
            
            report_file.write(f"| {volume_id} | {volume_type} | {size}GB | {state} | {encrypted} | {az} | {instance_id} |\n")
        
        if total_count > 10:
            report_file.write(f"... 및 {total_count - 10}개 추가 볼륨\n")
        
        # 볼륨 타입별 분포
        report_file.write("\n### 볼륨 타입별 분포\n")
        report_file.write("| 볼륨 타입 | 개수 | 총 크기 |\n")
        report_file.write("|-----------|------|----------|\n")
        
        # 타입별 그룹화
        type_stats = {}
        for volume in ebs_data:
            vol_type = volume.get('volume_type', 'unknown')
            size = volume.get('size', 0)
            if vol_type not in type_stats:
                type_stats[vol_type] = {'count': 0, 'total_size': 0}
            type_stats[vol_type]['count'] += 1
            type_stats[vol_type]['total_size'] += size
        
        for vol_type, stats in type_stats.items():
            report_file.write(f"| {vol_type} | {stats['count']} | {stats['total_size']}GB |\n")
        
        report_file.write("\n")

    def write_s3_analysis(self, report_file, s3_data: Optional[List]) -> None:
        """S3 버킷 분석 섹션을 작성합니다."""
        report_file.write("## 🪣 S3 버킷 현황\n\n")
        report_file.write("### S3 버킷 개요\n")
        
        if not s3_data:
            report_file.write("S3 버킷 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_buckets = len(s3_data)
        public_buckets = len([b for b in s3_data if b.get('bucket_policy_is_public', False)])
        encrypted_buckets = len([b for b in s3_data if b.get('server_side_encryption_configuration')])
        versioned_buckets = len([b for b in s3_data if b.get('versioning', {}).get('Status') == 'Enabled'])
        
        report_file.write(f"**총 S3 버킷:** {total_buckets}개\n")
        report_file.write(f"- **퍼블릭 버킷:** {public_buckets}개\n")
        report_file.write(f"- **암호화된 버킷:** {encrypted_buckets}개\n")
        report_file.write(f"- **버전 관리 활성화:** {versioned_buckets}개\n\n")
        
        # 상세 목록
        report_file.write("### S3 버킷 상세 목록\n")
        report_file.write("| 버킷 이름 | 생성일 | 퍼블릭 | 암호화 | 버전 관리 | 로깅 |\n")
        report_file.write("|-----------|--------|--------|--------|-----------|------|\n")
        
        for bucket in s3_data[:10]:
            name = bucket.get('name', 'N/A')
            creation_date = bucket.get('creation_date', 'N/A')[:10] if bucket.get('creation_date') else 'N/A'
            is_public = '예' if bucket.get('bucket_policy_is_public', False) else '아니오'
            is_encrypted = '예' if bucket.get('server_side_encryption_configuration') else '아니오'
            versioning = bucket.get('versioning', {}).get('Status', '비활성화')
            logging = '예' if bucket.get('logging') else '아니오'
            
            report_file.write(f"| {name} | {creation_date} | {is_public} | {is_encrypted} | {versioning} | {logging} |\n")
        
        if total_buckets > 10:
            report_file.write(f"... 및 {total_buckets - 10}개 추가 버킷\n")
        
        report_file.write("\n")

    def write_efs_analysis(self, report_file, efs_data: Optional[List]) -> None:
        """EFS 파일 시스템 분석 섹션을 작성합니다."""
        report_file.write("## 📁 EFS 파일 시스템 현황\n\n")
        
        if not efs_data:
            report_file.write("EFS 파일 시스템 데이터를 찾을 수 없습니다.\n\n")
            return
        
        total_efs = len(efs_data)
        encrypted_efs = len([e for e in efs_data if e.get('encrypted', False)])
        
        report_file.write(f"**총 EFS 파일 시스템:** {total_efs}개\n")
        report_file.write(f"- **암호화된 파일 시스템:** {encrypted_efs}개\n\n")
        
        if total_efs > 0:
            report_file.write("### EFS 파일 시스템 상세 목록\n")
            report_file.write("| 파일 시스템 ID | 이름 | 상태 | 성능 모드 | 암호화 | 마운트 타겟 수 |\n")
            report_file.write("|----------------|------|------|-----------|--------|----------------|\n")
            
            for efs in efs_data:
                fs_id = efs.get('file_system_id', 'N/A')
                name = efs.get('name', 'N/A')
                state = efs.get('life_cycle_state', 'N/A')
                performance_mode = efs.get('performance_mode', 'N/A')
                encrypted = '예' if efs.get('encrypted', False) else '아니오'
                mount_targets = efs.get('number_of_mount_targets', 0)
                
                report_file.write(f"| {fs_id} | {name} | {state} | {performance_mode} | {encrypted} | {mount_targets} |\n")
        
        report_file.write("\n")

    def write_storage_recommendations(self, report_file, ebs_data: Optional[List], s3_data: Optional[List]) -> None:
        """스토리지 권장사항 섹션을 작성합니다."""
        report_file.write("## 📋 스토리지 최적화 권장사항\n\n")
        
        report_file.write("### 🔴 높은 우선순위\n")
        
        recommendations = []
        
        # EBS 관련 권장사항
        if ebs_data:
            available_volumes = [v for v in ebs_data if v.get('state') == 'available']
            unencrypted_volumes = [v for v in ebs_data if not v.get('encrypted', False)]
            
            if available_volumes:
                recommendations.append(f"**미사용 EBS 볼륨 정리**: {len(available_volumes)}개의 미사용 볼륨이 발견되었습니다. 불필요한 비용을 절약하기 위해 삭제를 검토하세요.")
            
            if unencrypted_volumes:
                recommendations.append(f"**EBS 볼륨 암호화**: {len(unencrypted_volumes)}개의 암호화되지 않은 볼륨이 있습니다. 데이터 보안을 위해 암호화를 활성화하세요.")
        
        # S3 관련 권장사항
        if s3_data:
            public_buckets = [b for b in s3_data if b.get('bucket_policy_is_public', False)]
            unencrypted_buckets = [b for b in s3_data if not b.get('server_side_encryption_configuration')]
            
            if public_buckets:
                recommendations.append(f"**S3 퍼블릭 버킷 검토**: {len(public_buckets)}개의 퍼블릭 버킷이 있습니다. 보안상 필요하지 않다면 접근을 제한하세요.")
            
            if unencrypted_buckets:
                recommendations.append(f"**S3 버킷 암호화**: {len(unencrypted_buckets)}개의 암호화되지 않은 버킷이 있습니다. 서버 측 암호화를 활성화하세요.")
        
        # 기본 권장사항
        if not recommendations:
            recommendations = [
                "**스토리지 클래스 최적화**: S3 Intelligent-Tiering을 활용하여 자동으로 비용을 최적화하세요.",
                "**백업 전략 수립**: 중요한 데이터에 대한 정기적인 백업 정책을 수립하세요."
            ]
        
        for i, rec in enumerate(recommendations, 1):
            report_file.write(f"{i}. {rec}\n")
        
        report_file.write("\n### 🟡 중간 우선순위\n")
        report_file.write("1. **라이프사이클 정책**: S3 버킷에 라이프사이클 정책을 설정하여 오래된 데이터를 자동으로 아카이브하세요.\n")
        report_file.write("2. **EBS 스냅샷 관리**: 정기적인 스냅샷 생성 및 오래된 스냅샷 정리 정책을 수립하세요.\n")
        report_file.write("3. **모니터링 설정**: CloudWatch를 통해 스토리지 사용량과 성능을 모니터링하세요.\n\n")
        
        report_file.write("### 🟢 낮은 우선순위\n")
        report_file.write("1. **성능 최적화**: EBS 볼륨 타입을 워크로드에 맞게 최적화하세요.\n")
        report_file.write("2. **크로스 리전 복제**: 재해 복구를 위한 크로스 리전 복제를 고려하세요.\n")
        report_file.write("3. **스토리지 게이트웨이**: 하이브리드 환경에서 Storage Gateway 활용을 검토하세요.\n\n")

    def generate_report(self):
        """스토리지 분석 보고서를 생성합니다."""
        print("💾 Storage Analysis 보고서 생성 중...")
        
        # 데이터 파일 로드
        ebs_data = self.load_json_file("storage_ebs_volumes.json")
        s3_data = self.load_json_file("storage_s3_buckets.json")
        efs_data = self.load_json_file("storage_efs_filesystems.json")
        
        # 보고서 파일 생성
        report_path = self.report_dir / "05-storage-analysis.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as report_file:
                # 헤더 작성
                report_file.write("# 스토리지 리소스 분석\n\n")
                
                # 각 섹션 작성
                self.write_ebs_analysis(report_file, ebs_data)
                self.write_s3_analysis(report_file, s3_data)
                self.write_efs_analysis(report_file, efs_data)
                self.write_storage_recommendations(report_file, ebs_data, s3_data)
                
                # 마무리
                report_file.write("---\n")
                report_file.write("*스토리지 분석 완료*\n")
            
            print("✅ Storage Analysis 생성 완료: 05-storage-analysis.md")
            
        except IOError as e:
            print(f"❌ 보고서 파일 생성 실패: {e}")
            sys.exit(1)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="스토리지 분석 보고서 생성")
    parser.add_argument("--report-dir", default="/home/ec2-user/amazonqcli_lab/report", help="보고서 디렉토리")
    
    args = parser.parse_args()
    
    generator = StorageReportGenerator(args.report_dir)
    generator.generate_report()

if __name__ == "__main__":
    main()
