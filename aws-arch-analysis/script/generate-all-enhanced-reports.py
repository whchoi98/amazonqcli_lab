#!/usr/bin/env python3
"""
모든 보고서를 새로운 데이터 기반 권장사항 기준으로 생성하는 통합 스크립트
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def run_report_generator(script_name: str, report_name: str) -> bool:
    """개별 보고서 생성기를 실행합니다."""
    try:
        print(f"\n🔄 {report_name} 생성 중...")
        start_time = time.time()
        
        result = subprocess.run([
            sys.executable, script_name
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {report_name} 생성 완료 ({duration:.1f}초)")
            if result.stdout:
                # 권장사항 통계만 출력
                lines = result.stdout.split('\n')
                for line in lines:
                    if '권장사항 통계:' in line or '- 높은 우선순위:' in line or '- 중간 우선순위:' in line or '- 낮은 우선순위:' in line or '- 총 권장사항:' in line:
                        print(f"   {line.strip()}")
            return True
        else:
            print(f"❌ {report_name} 생성 실패")
            if result.stderr:
                print(f"   오류: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ {report_name} 실행 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 Enhanced AWS 계정 분석 보고서 일괄 생성")
    print("=" * 60)
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 보고서 생성 순서 (의존성 고려)
    reports = [
        ("generate-networking-report.py", "🌐 네트워킹 분석"),
        ("generate-compute-report.py", "💻 컴퓨팅 분석"),
        ("generate_storage_report.py", "💾 스토리지 분석"),
        ("generate_database_report.py", "🗄️ 데이터베이스 분석"),
        ("generate_security_report.py", "🛡️ 보안 분석"),
        ("generate-cost-report.py", "💰 비용 최적화"),
        ("generate-application-report.py", "🌐 애플리케이션 분석"),
        ("generate_monitoring_report.py", "📈 모니터링 분석"),
        ("generate_recommendations.py", "🎯 종합 권장사항"),
        ("generate_executive_summary.py", "📊 경영진 요약")
    ]
    
    successful_reports = []
    failed_reports = []
    total_start_time = time.time()
    
    # 각 보고서 순차 생성
    for script_name, report_name in reports:
        success = run_report_generator(script_name, report_name)
        if success:
            successful_reports.append(report_name)
        else:
            failed_reports.append(report_name)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 보고서 생성 결과 요약")
    print("=" * 60)
    
    print(f"✅ 성공한 보고서: {len(successful_reports)}개")
    for report in successful_reports:
        print(f"   - {report}")
    
    if failed_reports:
        print(f"\n❌ 실패한 보고서: {len(failed_reports)}개")
        for report in failed_reports:
            print(f"   - {report}")
    
    print(f"\n⏱️ 총 소요 시간: {total_duration:.1f}초")
    print(f"📅 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 보고서 파일 확인
    report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
    if report_dir.exists():
        md_files = list(report_dir.glob("*.md"))
        total_size = sum(f.stat().st_size for f in md_files)
        
        print(f"\n📁 생성된 보고서 파일:")
        print(f"   - 파일 수: {len(md_files)}개")
        print(f"   - 총 크기: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        print(f"   - 위치: {report_dir}")
    
    # 권장사항 통계 집계 (간단한 예시)
    print(f"\n🎯 전체 권장사항 요약:")
    print(f"   - 모든 보고서가 데이터 기반 권장사항 생성 기준 적용")
    print(f"   - 우선순위별 분류: 높음/중간/낮음")
    print(f"   - 정량적 효과 및 구현 난이도 포함")
    print(f"   - 실행 가능한 구체적 가이드 제공")
    
    if len(successful_reports) == len(reports):
        print("\n🎉 모든 보고서가 성공적으로 생성되었습니다!")
        return 0
    else:
        print(f"\n⚠️ {len(failed_reports)}개의 보고서 생성에 실패했습니다.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
