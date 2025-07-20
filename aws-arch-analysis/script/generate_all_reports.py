#!/usr/bin/env python3
"""
AWS 계정 분석 - 모든 보고서 일괄 생성 스크립트
수집된 JSON 데이터를 바탕으로 10개 분석 보고서를 생성합니다.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        # 스크립트의 실제 위치를 기준으로 경로 설정
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self.report_dir = project_root / "aws-arch-analysis" / "report"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 보고서 생성 스크립트 매핑 (실제 존재하는 스크립트만)
        self.report_scripts = [
            ("01-executive-summary.md", "generate_executive_summary.py", "경영진 요약"),
            ("02-networking-analysis.md", "generate-networking-report-awscli.py", "네트워킹 분석"),
            ("05-storage-analysis.md", "generate_storage_report.py", "스토리지 분석"),
            ("05-database-analysis.md", "generate_database_report.py", "데이터베이스 분석"),
            ("06-security-analysis.md", "generate_security_report.py", "보안 분석"),
            ("07-application-analysis.md", "generate-application-report.py", "애플리케이션 분석"),
            ("09-cost-optimization.md", "generate-cost-report.py", "비용 최적화"),
            ("09-monitoring-analysis.md", "generate_monitoring_report.py", "모니터링 분석"),
            ("10-comprehensive-recommendations.md", "generate_recommendations.py", "종합 권장사항")
        ]
        
        self.start_time = datetime.now()
        self.results = []

    def log_info(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\033[0;34m[{timestamp}]\033[0m {message}")

    def log_success(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\033[0;32m[{timestamp}]\033[0m ✅ {message}")

    def log_error(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\033[0;31m[{timestamp}]\033[0m ❌ {message}")

    def run_report_script(self, report_name: str, script_name: str, description: str) -> bool:
        """개별 보고서 생성 스크립트 실행"""
        script_path = self.script_dir / script_name
        
        if not script_path.exists():
            self.log_error(f"{description} 스크립트를 찾을 수 없습니다: {script_path}")
            return False
        
        self.log_info(f"📝 {description} 보고서 생성 중...")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.script_dir),
                capture_output=True,
                text=True,
                timeout=120  # 2분 타임아웃
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                # 생성된 보고서를 올바른 위치로 이동
                old_path = self.report_dir / report_name
                new_path = self.report_dir / report_name
                
                if old_path.exists():
                    old_path.rename(new_path)
                
                if new_path.exists():
                    self.log_success(f"{description} 보고서 생성 완료 ({duration:.1f}초)")
                    self.results.append({
                        "name": description,
                        "file": report_name,
                        "status": "success",
                        "duration": duration
                    })
                    return True
                else:
                    self.log_error(f"{description} 보고서 파일을 찾을 수 없습니다")
                    return False
            else:
                self.log_error(f"{description} 보고서 생성 실패: {result.stderr}")
                self.results.append({
                    "name": description,
                    "file": report_name,
                    "status": "failed",
                    "duration": duration,
                    "error": result.stderr
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.log_error(f"{description} 보고서 생성 타임아웃")
            return False
        except Exception as e:
            self.log_error(f"{description} 보고서 생성 중 예외 발생: {str(e)}")
            return False

    def generate_all_reports(self):
        """모든 보고서 생성 실행"""
        self.log_info("📋 AWS 계정 분석 보고서 일괄 생성 시작")
        self.log_info(f"📁 보고서 저장 위치: {self.report_dir}")
        self.log_info(f"📊 생성 대상: {len(self.report_scripts)}개 보고서")
        print()
        
        success_count = 0
        
        for i, (report_name, script_name, description) in enumerate(self.report_scripts, 1):
            self.log_info(f"[{i}/{len(self.report_scripts)}] {description} 처리 중...")
            
            if self.run_report_script(report_name, script_name, description):
                success_count += 1
            
            # 스크립트 간 간격
            if i < len(self.report_scripts):
                time.sleep(1)
            
            print()
        
        # 결과 요약
        self.print_summary(success_count)

    def print_summary(self, success_count: int):
        """보고서 생성 결과 요약 출력"""
        total_time = datetime.now() - self.start_time
        
        print("=" * 80)
        self.log_info("📊 AWS 분석 보고서 생성 완료 요약")
        print("=" * 80)
        
        print(f"🕐 총 소요 시간: {total_time}")
        print(f"✅ 성공: {success_count}/{len(self.report_scripts)}")
        print(f"❌ 실패: {len(self.report_scripts) - success_count}/{len(self.report_scripts)}")
        print()
        
        # 상세 결과
        for result in self.results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            duration = result.get("duration", 0)
            print(f"{status_icon} {result['name']:<20} ({duration:.1f}초) - {result['status']}")
        
        print()
        
        # 생성된 보고서 파일 확인
        md_files = list(self.report_dir.glob("*.md"))
        self.log_info(f"📁 생성된 보고서: {len(md_files)}개")
        
        for md_file in sorted(md_files):
            size = md_file.stat().st_size
            print(f"  📄 {md_file.name} ({size:,} bytes)")
        
        print()
        self.log_info("🎉 AWS 계정 분석 보고서 생성이 완료되었습니다!")
        self.log_info(f"📂 생성된 보고서 위치: {self.report_dir}")
        
        # 다음 단계 안내
        print()
        self.log_info("💡 다음 단계:")
        print("  1. 생성된 보고서 검토 및 내용 확인")
        print("  2. HTML 변환을 통한 웹 기반 보고서 생성")
        print("  3. 경영진 및 이해관계자와 결과 공유")

def main():
    """메인 실행 함수"""
    try:
        generator = ReportGenerator()
        generator.generate_all_reports()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
