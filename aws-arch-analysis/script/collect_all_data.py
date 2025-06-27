#!/usr/bin/env python3
"""
AWS 계정 종합 데이터 수집 스크립트
모든 Steampipe 기반 데이터 수집 스크립트를 순차적으로 실행
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

class AWSDataCollector:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.report_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.collection_scripts = [
            ("네트워킹", "steampipe_networking_collection.py"),
            ("컴퓨팅", "steampipe_compute_collection.py"),
            ("컨테이너", "steampipe_container_collection.py"),
            ("스토리지", "steampipe_storage_collection.py"),
            ("데이터베이스", "steampipe_database_collection.py"),
            ("보안", "steampipe_security_collection.py"),
            ("애플리케이션", "steampipe_application_collection.py"),
            ("모니터링", "steampipe_monitoring_collection.py"),
            ("IaC 분석", "steampipe_iac_analysis_collection.py")
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

    def log_warning(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\033[1;33m[{timestamp}]\033[0m ⚠️ {message}")

    def run_collection_script(self, name: str, script_name: str) -> bool:
        """개별 수집 스크립트 실행"""
        script_path = self.script_dir / script_name
        
        if not script_path.exists():
            self.log_error(f"{name} 스크립트를 찾을 수 없습니다: {script_path}")
            return False
        
        self.log_info(f"🚀 {name} 데이터 수집 시작...")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.script_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                self.log_success(f"{name} 데이터 수집 완료 ({duration:.1f}초)")
                self.results.append({
                    "name": name,
                    "script": script_name,
                    "status": "success",
                    "duration": duration,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                return True
            else:
                self.log_error(f"{name} 데이터 수집 실패 (코드: {result.returncode})")
                self.log_error(f"오류: {result.stderr}")
                self.results.append({
                    "name": name,
                    "script": script_name,
                    "status": "failed",
                    "duration": duration,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                })
                return False
                
        except subprocess.TimeoutExpired:
            self.log_error(f"{name} 데이터 수집 타임아웃 (5분 초과)")
            self.results.append({
                "name": name,
                "script": script_name,
                "status": "timeout",
                "duration": 300
            })
            return False
        except Exception as e:
            self.log_error(f"{name} 데이터 수집 중 예외 발생: {str(e)}")
            self.results.append({
                "name": name,
                "script": script_name,
                "status": "error",
                "error": str(e)
            })
            return False

    def collect_all_data(self):
        """모든 데이터 수집 실행"""
        self.log_info("🎯 AWS 계정 종합 데이터 수집 시작")
        self.log_info(f"📁 데이터 저장 위치: {self.report_dir}")
        self.log_info(f"📊 수집 대상: {len(self.collection_scripts)}개 영역")
        print()
        
        success_count = 0
        
        for i, (name, script_name) in enumerate(self.collection_scripts, 1):
            self.log_info(f"[{i}/{len(self.collection_scripts)}] {name} 영역 처리 중...")
            
            if self.run_collection_script(name, script_name):
                success_count += 1
            
            # 스크립트 간 간격
            if i < len(self.collection_scripts):
                time.sleep(2)
            
            print()
        
        # 결과 요약
        self.print_summary(success_count)

    def print_summary(self, success_count: int):
        """수집 결과 요약 출력"""
        total_time = datetime.now() - self.start_time
        
        print("=" * 80)
        self.log_info("📊 AWS 데이터 수집 완료 요약")
        print("=" * 80)
        
        print(f"🕐 총 소요 시간: {total_time}")
        print(f"✅ 성공: {success_count}/{len(self.collection_scripts)}")
        print(f"❌ 실패: {len(self.collection_scripts) - success_count}/{len(self.collection_scripts)}")
        print()
        
        # 상세 결과
        for result in self.results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            duration = result.get("duration", 0)
            print(f"{status_icon} {result['name']:<12} ({duration:.1f}초) - {result['status']}")
        
        print()
        
        # 생성된 파일 통계
        json_files = list(self.report_dir.glob("*.json"))
        log_files = list(self.report_dir.glob("*.log"))
        
        self.log_info(f"📁 생성된 파일: JSON {len(json_files)}개, 로그 {len(log_files)}개")
        
        # 총 데이터 크기
        total_size = sum(f.stat().st_size for f in json_files)
        self.log_info(f"💾 총 데이터 크기: {total_size / 1024 / 1024:.1f} MB")
        
        print()
        self.log_info("🎉 AWS 계정 종합 데이터 수집이 완료되었습니다!")
        self.log_info(f"📂 수집된 데이터 위치: {self.report_dir}")

def main():
    """메인 실행 함수"""
    try:
        collector = AWSDataCollector()
        collector.collect_all_data()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
