#!/usr/bin/env python3
"""
Cost Optimization 보고서 생성 스크립트
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """JSON 파일을 로드하고 파싱합니다."""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load {file_path}: {e}")
    return None

def calculate_ec2_costs(ec2_data: Optional[Dict]) -> Dict[str, Any]:
    """EC2 인스턴스 비용을 계산합니다."""
    if not ec2_data or 'rows' not in ec2_data:
        return {"total_instances": 0, "running_instances": 0, "stopped_instances": 0, "estimated_monthly_cost": 0}
    
    instances = ec2_data['rows']
    
    # 인스턴스 타입별 대략적인 시간당 비용 (USD, ap-northeast-2 기준)
    instance_costs = {
        't2.nano': 0.0058, 't2.micro': 0.0116, 't2.small': 0.023, 't2.medium': 0.046,
        't3.nano': 0.0052, 't3.micro': 0.0104, 't3.small': 0.0208, 't3.medium': 0.0416,
        't3.large': 0.0832, 't3.xlarge': 0.1664, 't3.2xlarge': 0.3328,
        'm5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384, 'm5.4xlarge': 0.768,
        'c5.large': 0.085, 'c5.xlarge': 0.17, 'c5.2xlarge': 0.34, 'c5.4xlarge': 0.68,
        'r5.large': 0.126, 'r5.xlarge': 0.252, 'r5.2xlarge': 0.504, 'r5.4xlarge': 1.008
    }
    
    total_instances = len(instances)
    running_instances = [i for i in instances if i.get('instance_state') == 'running']
    stopped_instances = [i for i in instances if i.get('instance_state') == 'stopped']
    
    # 실행 중인 인스턴스 비용 계산
    monthly_cost = 0
    for instance in running_instances:
        instance_type = instance.get('instance_type', 't3.micro')
        hourly_cost = instance_costs.get(instance_type, 0.05)  # 기본값
        monthly_cost += hourly_cost * 24 * 30  # 월간 비용
    
    return {
        "total_instances": total_instances,
        "running_instances": len(running_instances),
        "stopped_instances": len(stopped_instances),
        "estimated_monthly_cost": round(monthly_cost, 2),
        "instance_breakdown": running_instances
    }

def calculate_rds_costs(rds_data: Optional[Dict]) -> Dict[str, Any]:
    """RDS 인스턴스 비용을 계산합니다."""
    if not rds_data or 'rows' not in rds_data:
        return {"total_instances": 0, "estimated_monthly_cost": 0}
    
    instances = rds_data['rows']
    
    # RDS 인스턴스 타입별 대략적인 시간당 비용 (USD, ap-northeast-2 기준)
    rds_costs = {
        'db.t3.micro': 0.017, 'db.t3.small': 0.034, 'db.t3.medium': 0.068,
        'db.t3.large': 0.136, 'db.t3.xlarge': 0.272, 'db.t3.2xlarge': 0.544,
        'db.r5.large': 0.24, 'db.r5.xlarge': 0.48, 'db.r5.2xlarge': 0.96,
        'db.m5.large': 0.192, 'db.m5.xlarge': 0.384, 'db.m5.2xlarge': 0.768
    }
    
    total_instances = len(instances)
    monthly_cost = 0
    
    for instance in instances:
        instance_class = instance.get('db_instance_class', 'db.t3.micro')
        hourly_cost = rds_costs.get(instance_class, 0.1)  # 기본값
        monthly_cost += hourly_cost * 24 * 30
    
    return {
        "total_instances": total_instances,
        "estimated_monthly_cost": round(monthly_cost, 2),
        "instance_breakdown": instances
    }

def calculate_storage_costs(ebs_data: Optional[Dict], s3_data: Optional[Dict]) -> Dict[str, Any]:
    """스토리지 비용을 계산합니다."""
    storage_costs = {"ebs_cost": 0, "s3_cost": 0, "total_ebs_volumes": 0, "total_s3_buckets": 0}
    
    # EBS 볼륨 비용 계산
    if ebs_data and 'rows' in ebs_data:
        volumes = ebs_data['rows']
        storage_costs["total_ebs_volumes"] = len(volumes)
        
        # EBS 타입별 GB당 월간 비용 (USD, ap-northeast-2 기준)
        ebs_pricing = {
            'gp2': 0.10, 'gp3': 0.08, 'io1': 0.125, 'io2': 0.125,
            'st1': 0.045, 'sc1': 0.025, 'standard': 0.05
        }
        
        for volume in volumes:
            volume_type = volume.get('volume_type', 'gp2')
            size = volume.get('size', 0)
            price_per_gb = ebs_pricing.get(volume_type, 0.10)
            storage_costs["ebs_cost"] += size * price_per_gb
    
    # S3 버킷 비용 추정 (실제 사용량 데이터 없이 추정)
    if s3_data and 'rows' in s3_data:
        buckets = s3_data['rows']
        storage_costs["total_s3_buckets"] = len(buckets)
        # 버킷당 평균 10GB 추정 (실제로는 CloudWatch 메트릭 필요)
        estimated_s3_storage = len(buckets) * 10  # GB
        storage_costs["s3_cost"] = estimated_s3_storage * 0.023  # Standard 스토리지 가격
    
    storage_costs["ebs_cost"] = round(storage_costs["ebs_cost"], 2)
    storage_costs["s3_cost"] = round(storage_costs["s3_cost"], 2)
    
    return storage_costs

def write_current_cost_overview(report_file, ec2_costs: Dict, rds_costs: Dict, storage_costs: Dict) -> None:
    """현재 비용 현황 섹션을 작성합니다."""
    report_file.write("## 💰 현재 비용 현황\n\n")
    
    total_estimated_cost = ec2_costs["estimated_monthly_cost"] + rds_costs["estimated_monthly_cost"] + storage_costs["ebs_cost"] + storage_costs["s3_cost"]
    
    report_file.write("### 월간 예상 비용 (추정)\n")
    report_file.write(f"- **EC2 인스턴스**: ${ec2_costs['estimated_monthly_cost']:.2f}/월 ({ec2_costs['running_instances']}개 실행 중)\n")
    report_file.write(f"- **RDS 데이터베이스**: ${rds_costs['estimated_monthly_cost']:.2f}/월 ({rds_costs['total_instances']}개)\n")
    report_file.write(f"- **EBS 스토리지**: ${storage_costs['ebs_cost']:.2f}/월 ({storage_costs['total_ebs_volumes']}개 볼륨)\n")
    report_file.write(f"- **S3 스토리지**: ${storage_costs['s3_cost']:.2f}/월 ({storage_costs['total_s3_buckets']}개 버킷)\n")
    report_file.write(f"- **총 예상 비용**: ${total_estimated_cost:.2f}/월\n\n")
    
    report_file.write("### 비용 분포\n")
    if total_estimated_cost > 0:
        ec2_percentage = (ec2_costs["estimated_monthly_cost"] / total_estimated_cost) * 100
        rds_percentage = (rds_costs["estimated_monthly_cost"] / total_estimated_cost) * 100
        ebs_percentage = (storage_costs["ebs_cost"] / total_estimated_cost) * 100
        s3_percentage = (storage_costs["s3_cost"] / total_estimated_cost) * 100
        
        report_file.write("| 서비스 | 월간 비용 | 비율 |\n")
        report_file.write("|--------|-----------|------|\n")
        report_file.write(f"| EC2 | ${ec2_costs['estimated_monthly_cost']:.2f} | {ec2_percentage:.1f}% |\n")
        report_file.write(f"| RDS | ${rds_costs['estimated_monthly_cost']:.2f} | {rds_percentage:.1f}% |\n")
        report_file.write(f"| EBS | ${storage_costs['ebs_cost']:.2f} | {ebs_percentage:.1f}% |\n")
        report_file.write(f"| S3 | ${storage_costs['s3_cost']:.2f} | {s3_percentage:.1f}% |\n")
    else:
        report_file.write("비용 데이터를 계산할 수 없습니다.\n")
    
    report_file.write("\n")

def write_cost_optimization_opportunities(report_file, ec2_costs: Dict, rds_costs: Dict, storage_costs: Dict, ebs_data: Optional[Dict]) -> None:
    """비용 최적화 기회 섹션을 작성합니다."""
    report_file.write("## 📊 비용 최적화 기회\n\n")
    
    report_file.write("### 🔴 즉시 절감 가능\n")
    
    immediate_savings = []
    total_immediate_savings = 0
    
    # 중지된 인스턴스로 인한 EBS 비용
    if ec2_costs["stopped_instances"] > 0:
        # 중지된 인스턴스의 EBS 비용 추정 (인스턴스당 평균 20GB 가정)
        stopped_ebs_cost = ec2_costs["stopped_instances"] * 20 * 0.10  # gp2 기준
        immediate_savings.append(f"**중지된 인스턴스 정리**: {ec2_costs['stopped_instances']}개 인스턴스의 EBS 비용 ${stopped_ebs_cost:.2f}/월 절감")
        total_immediate_savings += stopped_ebs_cost
    
    # 미사용 EBS 볼륨 (available 상태)
    if ebs_data and 'rows' in ebs_data:
        available_volumes = [v for v in ebs_data['rows'] if v.get('state') == 'available']
        if available_volumes:
            available_cost = sum(v.get('size', 0) * 0.10 for v in available_volumes)  # gp2 기준
            immediate_savings.append(f"**미사용 EBS 볼륨 삭제**: {len(available_volumes)}개 볼륨, ${available_cost:.2f}/월 절감")
            total_immediate_savings += available_cost
    
    # 기본 권장사항
    if not immediate_savings:
        immediate_savings = [
            "**리소스 사용량 검토**: 실제 사용률 기반 인스턴스 타입 최적화",
            "**스토리지 정리**: 미사용 스냅샷 및 볼륨 정리"
        ]
    
    for i, saving in enumerate(immediate_savings, 1):
        report_file.write(f"{i}. {saving}\n")
    
    if total_immediate_savings > 0:
        report_file.write(f"\n**즉시 절감 가능 총액**: ${total_immediate_savings:.2f}/월\n")
    
    report_file.write("\n### 🟡 중기 최적화 (1-3개월)\n")
    report_file.write("1. **예약 인스턴스**: 장기 실행 워크로드에 대해 1년 예약으로 최대 40% 절감\n")
    report_file.write("2. **스팟 인스턴스**: 배치 작업 및 개발 환경에 활용하여 최대 70% 절감\n")
    report_file.write("3. **인스턴스 타입 최적화**: CPU/메모리 사용률 기반 적절한 타입 선택\n")
    report_file.write("4. **스토리지 타입 최적화**: gp3로 마이그레이션하여 20% 비용 절감\n\n")
    
    report_file.write("### 🟢 장기 최적화 (3-6개월)\n")
    report_file.write("1. **서버리스 아키텍처**: Lambda, Fargate 활용으로 유휴 시간 비용 제거\n")
    report_file.write("2. **컨테이너화**: ECS/EKS로 리소스 효율성 향상\n")
    report_file.write("3. **데이터 라이프사이클**: S3 Intelligent Tiering, Glacier 활용\n")
    report_file.write("4. **네트워크 최적화**: CloudFront, VPC 엔드포인트 활용\n\n")

def write_detailed_recommendations(report_file, ec2_costs: Dict, rds_costs: Dict) -> None:
    """상세 권장사항 섹션을 작성합니다."""
    report_file.write("## 🎯 상세 권장사항\n\n")
    
    # EC2 최적화 권장사항
    if ec2_costs["running_instances"] > 0:
        report_file.write("### EC2 최적화\n")
        report_file.write("| 권장사항 | 예상 절감 | 구현 난이도 | 우선순위 |\n")
        report_file.write("|----------|-----------|-------------|----------|\n")
        report_file.write("| 예약 인스턴스 구매 | 30-40% | 쉬움 | 높음 |\n")
        report_file.write("| 인스턴스 타입 최적화 | 20-30% | 중간 | 높음 |\n")
        report_file.write("| 스팟 인스턴스 활용 | 50-70% | 어려움 | 중간 |\n")
        report_file.write("| Auto Scaling 설정 | 15-25% | 중간 | 중간 |\n\n")
    
    # RDS 최적화 권장사항
    if rds_costs["total_instances"] > 0:
        report_file.write("### RDS 최적화\n")
        report_file.write("| 권장사항 | 예상 절감 | 구현 난이도 | 우선순위 |\n")
        report_file.write("|----------|-----------|-------------|----------|\n")
        report_file.write("| 예약 인스턴스 구매 | 30-40% | 쉬움 | 높음 |\n")
        report_file.write("| 인스턴스 크기 최적화 | 20-30% | 중간 | 높음 |\n")
        report_file.write("| Aurora Serverless 검토 | 40-60% | 어려움 | 중간 |\n")
        report_file.write("| 백업 보존 기간 최적화 | 10-20% | 쉬움 | 낮음 |\n\n")
    
    # 스토리지 최적화 권장사항
    report_file.write("### 스토리지 최적화\n")
    report_file.write("| 권장사항 | 예상 절감 | 구현 난이도 | 우선순위 |\n")
    report_file.write("|----------|-----------|-------------|----------|\n")
    report_file.write("| gp2 → gp3 마이그레이션 | 20% | 쉬움 | 높음 |\n")
    report_file.write("| 미사용 볼륨 정리 | 100% | 쉬움 | 높음 |\n")
    report_file.write("| 스냅샷 라이프사이클 관리 | 30-50% | 중간 | 중간 |\n")
    report_file.write("| S3 Intelligent Tiering | 20-40% | 쉬움 | 중간 |\n\n")

def write_monitoring_and_alerts(report_file) -> None:
    """모니터링 및 알림 섹션을 작성합니다."""
    report_file.write("## 📈 비용 모니터링 및 알림\n\n")
    
    report_file.write("### 권장 모니터링 설정\n")
    report_file.write("1. **AWS Budgets**: 월간 예산 설정 및 80%, 100% 임계값 알림\n")
    report_file.write("2. **Cost Anomaly Detection**: 비정상적인 비용 증가 자동 감지\n")
    report_file.write("3. **CloudWatch 대시보드**: 주요 비용 메트릭 시각화\n")
    report_file.write("4. **태그 기반 비용 추적**: 프로젝트/환경별 비용 분석\n\n")
    
    report_file.write("### 정기 검토 프로세스\n")
    report_file.write("- **주간**: 비용 트렌드 및 이상 징후 확인\n")
    report_file.write("- **월간**: 예산 대비 실제 비용 분석 및 최적화 기회 검토\n")
    report_file.write("- **분기**: 아키텍처 최적화 및 예약 인스턴스 구매 계획 수립\n")
    report_file.write("- **연간**: 전체 비용 전략 및 목표 재설정\n\n")

def write_action_plan(report_file, total_estimated_cost: float) -> None:
    """실행 계획 섹션을 작성합니다."""
    report_file.write("## 🚀 실행 계획\n\n")
    
    report_file.write("### 1주차: 즉시 실행\n")
    report_file.write("- [ ] 중지된 인스턴스 및 미사용 EBS 볼륨 정리\n")
    report_file.write("- [ ] AWS Budgets 설정 (현재 예상 비용 기준)\n")
    report_file.write("- [ ] Cost Explorer에서 비용 트렌드 분석\n")
    report_file.write("- [ ] 리소스 태깅 전략 수립 및 적용 시작\n\n")
    
    report_file.write("### 2-4주차: 단기 최적화\n")
    report_file.write("- [ ] 인스턴스 사용률 모니터링 (CloudWatch 메트릭)\n")
    report_file.write("- [ ] 예약 인스턴스 구매 계획 수립\n")
    report_file.write("- [ ] gp2 → gp3 마이그레이션 계획\n")
    report_file.write("- [ ] 스냅샷 라이프사이클 정책 구현\n\n")
    
    report_file.write("### 2-3개월: 중기 최적화\n")
    report_file.write("- [ ] 예약 인스턴스 구매 실행\n")
    report_file.write("- [ ] 인스턴스 타입 최적화 실행\n")
    report_file.write("- [ ] Auto Scaling 정책 구현\n")
    report_file.write("- [ ] 스팟 인스턴스 활용 검토\n\n")
    
    target_savings = total_estimated_cost * 0.3  # 30% 절감 목표
    report_file.write(f"### 목표\n")
    report_file.write(f"- **3개월 내 목표 절감액**: ${target_savings:.2f}/월 (30% 절감)\n")
    report_file.write(f"- **연간 절감 목표**: ${target_savings * 12:.2f}\n\n")

def main():
    """메인 함수"""
    print("💰 Cost Optimization 보고서 생성 중...")
    
    # 보고서 디렉토리 설정
    report_dir = Path("/home/ec2-user/amazonqcli_lab/report")
    os.chdir(report_dir)
    
    # JSON 데이터 파일들 로드
    ec2_data = load_json_file("compute_ec2_instances.json")
    rds_data = load_json_file("database_rds_instances.json")
    ebs_data = load_json_file("storage_ebs_volumes.json")
    s3_data = load_json_file("storage_s3_buckets.json")
    
    # 비용 계산
    ec2_costs = calculate_ec2_costs(ec2_data)
    rds_costs = calculate_rds_costs(rds_data)
    storage_costs = calculate_storage_costs(ebs_data, s3_data)
    
    total_estimated_cost = ec2_costs["estimated_monthly_cost"] + rds_costs["estimated_monthly_cost"] + storage_costs["ebs_cost"] + storage_costs["s3_cost"]
    
    # 보고서 파일 생성
    report_path = report_dir / "09-cost-optimization.md"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as report_file:
            # 헤더 작성
            report_file.write("# 비용 최적화 분석\n\n")
            
            # 각 섹션 작성
            write_current_cost_overview(report_file, ec2_costs, rds_costs, storage_costs)
            write_cost_optimization_opportunities(report_file, ec2_costs, rds_costs, storage_costs, ebs_data)
            write_detailed_recommendations(report_file, ec2_costs, rds_costs)
            write_monitoring_and_alerts(report_file)
            write_action_plan(report_file, total_estimated_cost)
            
            # 마무리
            report_file.write("---\n")
            report_file.write("*비용 최적화 분석 완료*\n")
            report_file.write(f"\n**생성 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            report_file.write("**주의**: 이 보고서의 비용 추정치는 대략적인 값이며, 실제 AWS 청구서와 다를 수 있습니다.\n")
        
        print("✅ Cost Optimization 생성 완료: 09-cost-optimization.md")
        print(f"📊 총 예상 월간 비용: ${total_estimated_cost:.2f}")
        
    except IOError as e:
        print(f"❌ 보고서 파일 생성 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
