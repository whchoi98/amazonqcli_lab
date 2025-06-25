#!/usr/bin/env python3
"""
Python 버전 AWS 분석 스크립트 테스트
"""

import sys
import subprocess
import shutil
from pathlib import Path

def test_environment():
    """환경 테스트"""
    print("🔍 환경 테스트 시작...")
    
    # Python 버전 확인
    print(f"Python 버전: {sys.version}")
    
    # 필수 도구 확인
    tools = ['aws', 'steampipe', 'python3']
    for tool in tools:
        if shutil.which(tool):
            print(f"✅ {tool}: 설치됨")
        else:
            print(f"❌ {tool}: 설치되지 않음")
    
    # AWS 자격 증명 확인
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, check=True)
        print("✅ AWS 자격 증명: 구성됨")
    except subprocess.CalledProcessError:
        print("❌ AWS 자격 증명: 구성되지 않음")
    
    # Steampipe 연결 확인
    try:
        result = subprocess.run(['steampipe', 'query', 'select 1'], 
                              capture_output=True, text=True, check=True)
        print("✅ Steampipe: 연결됨")
    except subprocess.CalledProcessError:
        print("❌ Steampipe: 연결 실패")
    
    # 선택적 패키지 확인
    try:
        import markdown
        print("✅ markdown 패키지: 설치됨 (HTML 변환 가능)")
    except ImportError:
        print("⚠️ markdown 패키지: 설치되지 않음 (HTML 변환 불가)")

def test_modules():
    """모듈 import 테스트"""
    print("\n📦 모듈 테스트 시작...")
    
    modules = [
        'report_utils',
        'html_generator', 
        'report_generators'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}: import 성공")
        except ImportError as e:
            print(f"❌ {module}: import 실패 - {e}")

def main():
    """메인 테스트 함수"""
    print("🧪 AWS 종합 분석 스크립트 Python 버전 테스트")
    print("=" * 50)
    
    test_environment()
    test_modules()
    
    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("\n💡 다음 단계:")
    print("1. 모든 ✅ 항목이 표시되면 스크립트 실행 준비 완료")
    print("2. ❌ 항목이 있으면 해당 도구/패키지 설치 필요")
    print("3. 실행: python3 aws_comprehensive_analysis.py")

if __name__ == "__main__":
    main()
