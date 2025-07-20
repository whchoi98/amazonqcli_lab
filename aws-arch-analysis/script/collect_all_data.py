#!/usr/bin/env python3
"""
AWS 계정 종합 데이터 수집 스크립트
모든 Steampipe 기반 데이터 수집 스크립트를 병렬 또는 순차적으로 실행

사용법:
    python collect_all_data.py              # 병렬 처리 (기본값, 빠름)
    python collect_all_data.py --sequential # 순차 처리 (안정적)

병렬 처리 특징:
- 최대 4개 스크립트 동시 실행
- 전체 실행 시간 단축 (약 50-70% 단축)
- 시스템 리소스 효율적 활용
- 타임아웃 10분으로 증가

순차 처리 특징:
- 하나씩 차례대로 실행
- 안정적이고 예측 가능한 실행
- 디버깅 및 문제 해결에 유리
- 타임아웃 10분
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import concurrent.futures
import threading

class AWSDataCollector:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        # 스크립트의 실제 위치를 기준으로 경로 설정
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self.report_dir = project_root / "aws-arch-analysis" / "report"
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
            ("비용 분석", "steampipe_cost_collection.py"),
            ("IaC 분석", "steampipe_iac_analysis_collection.py")
        ]
        
        self.start_time = datetime.now()
        self.results = []
        self.lock = threading.Lock()  # 결과 리스트 동기화용

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

    def run_collection_script(self, name: str, script_name: str) -> dict:
        """개별 수집 스크립트 실행 (병렬 처리용)"""
        script_path = self.script_dir / script_name
        
        if not script_path.exists():
            self.log_error(f"{name} 스크립트를 찾을 수 없습니다: {script_path}")
            return {
                "name": name,
                "script": script_name,
                "status": "not_found",
                "duration": 0
            }
        
        self.log_info(f"🚀 {name} 데이터 수집 시작...")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.script_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10분 타임아웃 (병렬 처리시 여유있게)
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                self.log_success(f"{name} 데이터 수집 완료 ({duration:.1f}초)")
                return {
                    "name": name,
                    "script": script_name,
                    "status": "success",
                    "duration": duration,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                self.log_error(f"{name} 데이터 수집 실패 (코드: {result.returncode})")
                if result.stderr:
                    self.log_error(f"오류: {result.stderr[:200]}...")  # 오류 메시지 축약
                return {
                    "name": name,
                    "script": script_name,
                    "status": "failed",
                    "duration": duration,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            self.log_error(f"{name} 데이터 수집 타임아웃 (10분 초과)")
            return {
                "name": name,
                "script": script_name,
                "status": "timeout",
                "duration": 600
            }
        except Exception as e:
            self.log_error(f"{name} 데이터 수집 중 예외 발생: {str(e)}")
            return {
                "name": name,
                "script": script_name,
                "status": "error",
                "error": str(e),
                "duration": 0
            }

    def collect_all_data(self):
        """모든 데이터 수집 실행 (병렬 처리)"""
        self.log_info("🎯 AWS 계정 종합 데이터 수집 시작 (병렬 처리)")
        self.log_info(f"📁 데이터 저장 위치: {self.report_dir}")
        self.log_info(f"📊 수집 대상: {len(self.collection_scripts)}개 영역")
        self.log_info(f"🚀 최대 동시 실행: {min(4, len(self.collection_scripts))}개 스크립트")
        print()
        
        # ThreadPoolExecutor를 사용한 병렬 처리
        max_workers = min(4, len(self.collection_scripts))  # 최대 4개 동시 실행
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 모든 작업을 제출
            future_to_script = {
                executor.submit(self.run_collection_script, name, script_name): (name, script_name)
                for name, script_name in self.collection_scripts
            }
            
            # 완료된 작업들을 처리
            completed_count = 0
            for future in concurrent.futures.as_completed(future_to_script):
                name, script_name = future_to_script[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    with self.lock:
                        self.results.append(result)
                    
                    self.log_info(f"[{completed_count}/{len(self.collection_scripts)}] {name} 처리 완료")
                    
                except Exception as exc:
                    self.log_error(f"{name} 실행 중 예외 발생: {exc}")
                    with self.lock:
                        self.results.append({
                            "name": name,
                            "script": script_name,
                            "status": "exception",
                            "error": str(exc),
                            "duration": 0
                        })
        
        # 결과를 원래 순서대로 정렬
        script_order = {script_name: i for i, (_, script_name) in enumerate(self.collection_scripts)}
        self.results.sort(key=lambda x: script_order.get(x["script"], 999))
        
    def collect_all_data_sequential(self):
        """모든 데이터 수집 실행 (순차 처리)"""
        self.log_info("🎯 AWS 계정 종합 데이터 수집 시작 (순차 처리)")
        self.log_info(f"📁 데이터 저장 위치: {self.report_dir}")
        self.log_info(f"📊 수집 대상: {len(self.collection_scripts)}개 영역")
        print()
        
        for i, (name, script_name) in enumerate(self.collection_scripts, 1):
            self.log_info(f"[{i}/{len(self.collection_scripts)}] {name} 영역 처리 중...")
            
            result = self.run_collection_script(name, script_name)
            self.results.append(result)
            
            # 스크립트 간 간격
            if i < len(self.collection_scripts):
                time.sleep(1)
            
            print()
        
        # 결과 요약
        success_count = sum(1 for r in self.results if r["status"] == "success")
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
        
        # 명령행 인수로 실행 모드 선택
        if len(sys.argv) > 1 and sys.argv[1] == "--sequential":
            collector.collect_all_data_sequential()
        else:
            # 기본값: 병렬 처리
            collector.collect_all_data()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
