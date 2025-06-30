#!/usr/bin/env python3
"""
테이블 헤더만 검정색 볼드로 하고, 다른 행들은 일반 스타일로 변경하는 스크립트
"""

import os
import re
from pathlib import Path

def fix_header_only_black():
    """테이블 헤더만 검정색 볼드로 하고, 나머지 행은 일반 스타일로 변경"""
    
    # 스크립트 위치 기반 상대 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "..", "..")
    html_dir = Path(os.path.join(project_root, "html-report"))
    
    if not html_dir.exists():
        print("❌ HTML 디렉토리를 찾을 수 없습니다.")
        return
    
    print("🎨 테이블 헤더만 검정색 볼드로 변경 중...")
    
    # 수정된 CSS 스타일
    header_only_css = """
/* 테이블 헤더만 검정색 볼드 */
table th {
    color: #000000 !important;
    font-weight: 700;
    background-color: #f8f9fa !important;
}

/* 테이블 헤더 링크도 검정색 */
table th a {
    color: #000000 !important;
    text-decoration: none;
}

table th a:hover {
    color: #333333 !important;
    text-decoration: underline;
}

/* 일반 테이블 셀은 기본 스타일 */
table td {
    color: #2c3e50 !important;
    font-weight: 500;
}

/* 첫 번째 열만 약간 진하게 (헤더 제외) */
table td:first-child {
    color: #000000 !important;
    font-weight: 600;
}

/* 첫 번째 열 링크 */
table td:first-child a {
    color: #000000 !important;
    text-decoration: none;
}

table td:first-child a:hover {
    color: #333333 !important;
    text-decoration: underline;
}
"""
    
    # CSS 파일 업데이트
    css_file = html_dir / "assets" / "css" / "style.css"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # 기존 테이블 관련 스타일 제거
        css_content = re.sub(
            r'/\* 테이블 첫 번째 행.*?\*/',
            '',
            css_content,
            flags=re.DOTALL
        )
        
        css_content = re.sub(
            r'/\* 테이블 첫 번째 열.*?\*/',
            '',
            css_content,
            flags=re.DOTALL
        )
        
        # 기존 헤더 스타일 제거
        css_content = re.sub(
            r'/\* 모든 테이블 헤더.*?\*/',
            '',
            css_content,
            flags=re.DOTALL
        )
        
        # 새로운 스타일 추가
        css_content += header_only_css
        
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print("✅ CSS 파일 업데이트 완료")
    
    # HTML 파일들 처리
    html_files = list(html_dir.glob("*.html"))
    processed_files = 0
    
    for html_file in html_files:
        if html_file.name.startswith('.'):
            continue
            
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 불필요한 인라인 스타일 제거
            content = re.sub(
                r'<td[^>]*style="[^"]*color:[^;"]*;?[^"]*"([^>]*)>',
                r'<td\1>',
                content
            )
            
            content = re.sub(
                r'<tr[^>]*style="[^"]*color:[^;"]*;?[^"]*"([^>]*)>',
                r'<tr\1>',
                content
            )
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            processed_files += 1
            print(f"✅ 처리 완료: {html_file.name}")
            
        except Exception as e:
            print(f"❌ 오류 발생 ({html_file.name}): {e}")
    
    print(f"\n🎉 테이블 스타일 수정 완료!")
    print(f"📊 처리된 파일: {processed_files}개")
    print(f"🎨 헤더 (th): 검정색 볼드 (#000000, font-weight: 700)")
    print(f"📄 일반 셀 (td): 기본 색상 (#2c3e50, font-weight: 500)")
    print(f"📋 첫 번째 열: 검정색 semi-bold (#000000, font-weight: 600)")
    
    return processed_files

if __name__ == "__main__":
    fix_header_only_black()
