#!/usr/bin/env python3
"""
권장사항 HTML 개선 스크립트
번호가 매겨진 권장사항을 더 아름답게 렌더링
"""

import re
import sys
from pathlib import Path

def enhance_recommendations_html(html_content):
    """권장사항 HTML을 개선합니다."""
    
    # 1. 번호가 매겨진 권장사항 패턴 찾기 (여러 패턴 지원)
    patterns = [
        # 패턴 1: <p>1. <strong>제목</strong>: 내용</p>
        (r'<p>(\d+)\.\s*<strong>([^<]+)</strong>:\s*([^<]*)</p>', 'with_colon'),
        # 패턴 2: <p>1. <strong>제목</strong></p> 다음에 내용
        (r'<p>(\d+)\.\s*<strong>([^<]+)</strong></p>\s*<p>([^<]*)</p>', 'separate_paragraphs'),
        # 패턴 3: 단순한 형태 1. **제목**
        (r'(\d+)\.\s*\*\*([^*]+)\*\*:\s*([^\n]*)', 'markdown_style')
    ]
    
    enhanced_content = html_content
    
    for pattern, pattern_type in patterns:
        def replace_recommendation(match):
            number = match.group(1)
            title = match.group(2)
            content = match.group(3) if len(match.groups()) >= 3 else ""
            
            return f'''<div class="recommendation-item">
    <div class="recommendation-number">{number}</div>
    <div class="recommendation-content">
        <strong class="recommendation-title">{title}</strong>
        {f': <span class="recommendation-text">{content}</span>' if content.strip() else ''}
    </div>
</div>'''
        
        enhanced_content = re.sub(pattern, replace_recommendation, enhanced_content)
    
    # 2. 리스트 항목 내의 권장사항도 처리
    # <li>1. <strong>제목</strong>: 내용</li> 패턴
    li_pattern = r'<li>(\d+)\.\s*<strong>([^<]+)</strong>:\s*([^<]*)</li>'
    
    def replace_li_recommendation(match):
        number = match.group(1)
        title = match.group(2)
        content = match.group(3)
        
        return f'''<li class="recommendation-item">
    <div class="recommendation-number">{number}</div>
    <div class="recommendation-content">
        <strong class="recommendation-title">{title}</strong>: 
        <span class="recommendation-text">{content}</span>
    </div>
</li>'''
    
    enhanced_content = re.sub(li_pattern, replace_li_recommendation, enhanced_content)
    
    # 3. 우선순위 섹션에 클래스 추가
    priority_patterns = [
        (r'<h3[^>]*>🔴[^<]*높은 우선순위[^<]*</h3>', '<h3 class="high-priority-header">🔴 높은 우선순위</h3>'),
        (r'<h3[^>]*>🟡[^<]*중간 우선순위[^<]*</h3>', '<h3 class="medium-priority-header">🟡 중간 우선순위</h3>'),
        (r'<h3[^>]*>🟢[^<]*낮은 우선순위[^<]*</h3>', '<h3 class="low-priority-header">🟢 낮은 우선순위</h3>'),
        (r'<h4[^>]*>🔴[^<]*높은 우선순위[^<]*</h4>', '<h4 class="high-priority-header">🔴 높은 우선순위</h4>'),
        (r'<h4[^>]*>🟡[^<]*중간 우선순위[^<]*</h4>', '<h4 class="medium-priority-header">🟡 중간 우선순위</h4>'),
        (r'<h4[^>]*>🟢[^<]*낮은 우선순위[^<]*</h4>', '<h4 class="low-priority-header">🟢 낮은 우선순위</h4>')
    ]
    
    for pattern, replacement in priority_patterns:
        enhanced_content = re.sub(pattern, replacement, enhanced_content, flags=re.IGNORECASE)
    
    return enhanced_content

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 enhance-recommendations.py <html_file>")
        sys.exit(1)
    
    html_file = Path(sys.argv[1])
    
    if not html_file.exists():
        print(f"Error: File {html_file} not found")
        sys.exit(1)
    
    try:
        # HTML 파일 읽기
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 권장사항 개선
        enhanced_content = enhance_recommendations_html(content)
        
        # 파일에 다시 쓰기
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f"✅ 권장사항 HTML 개선 완료: {html_file}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
