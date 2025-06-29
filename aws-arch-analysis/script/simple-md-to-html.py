#!/usr/bin/env python3
"""
간단한 Markdown to HTML 변환기
"""
import re
import os
import sys
from pathlib import Path

def process_markdown_formatting(text):
    """기본 Markdown 포맷팅을 HTML로 변환"""
    if not text:
        return text
    
    # 1. 볼드 텍스트 (**text** -> <strong>text</strong>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # 2. 이탤릭 텍스트 (*text* -> <em>text</em>)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', text)
    
    # 3. 인라인 코드
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # 4. 링크
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    return text

def convert_markdown_table(text):
    """Markdown 테이블을 HTML로 변환"""
    lines = text.split('\n')
    result = []
    in_table = False
    table_rows = []
    
    for line in lines:
        if '|' in line and line.strip():
            # 구분선 건너뛰기
            if re.match(r'^\s*\|[\s\-\|:]+\|\s*$', line):
                continue
                
            if not in_table:
                in_table = True
                table_rows = []
            
            # 테이블 행 처리
            cells = [cell.strip() for cell in line.split('|')]
            if cells and not cells[0]:
                cells = cells[1:]
            if cells and not cells[-1]:
                cells = cells[:-1]
            
            table_rows.append(cells)
        else:
            if in_table and table_rows:
                result.append(convert_table_to_html(table_rows))
                table_rows = []
                in_table = False
            result.append(line)
    
    if in_table and table_rows:
        result.append(convert_table_to_html(table_rows))
    
    return '\n'.join(result)

def convert_table_to_html(table_rows):
    """테이블 행들을 HTML로 변환 - 개선된 버전"""
    if not table_rows:
        return ""
    
    html = ['<table class="analysis-table">']
    
    # 헤더
    if table_rows:
        html.append('  <thead>')
        html.append('    <tr>')
        for cell in table_rows[0]:
            cell_content = process_markdown_formatting(cell)
            html.append(f'      <th>{cell_content}</th>')
        html.append('    </tr>')
        html.append('  </thead>')
    
    # 데이터 행
    if len(table_rows) > 1:
        html.append('  <tbody>')
        for row in table_rows[1:]:
            html.append('    <tr>')
            for i, cell in enumerate(row):
                cell_content = process_markdown_formatting(cell)
                
                # 상태 값에 따른 데이터 속성 추가
                data_attr = ""
                cell_lower = cell.lower().strip()
                if cell_lower in ['available', 'running', 'active']:
                    data_attr = ' data-status="available"'
                elif cell_lower in ['stopped', 'terminated', 'inactive']:
                    data_attr = ' data-status="stopped"'
                elif cell_lower == 'running':
                    data_attr = ' data-status="running"'
                
                html.append(f'      <td{data_attr}>{cell_content}</td>')
            html.append('    </tr>')
        html.append('  </tbody>')
    
    html.append('</table>')
    return '\n'.join(html)

def convert_markdown_lists(text):
    """Markdown 리스트를 HTML로 변환"""
    lines = text.split('\n')
    result = []
    in_list = False
    list_items = []
    
    for line in lines:
        list_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.+)', line)
        if list_match:
            content = list_match.group(3)
            
            if not in_list:
                in_list = True
                list_items = []
            
            item_content = process_markdown_formatting(content)
            list_items.append(item_content)
        else:
            if in_list and list_items:
                result.append('<ul>')
                for item in list_items:
                    result.append(f'  <li>{item}</li>')
                result.append('</ul>')
                list_items = []
                in_list = False
            result.append(line)
    
    if in_list and list_items:
        result.append('<ul>')
        for item in list_items:
            result.append(f'  <li>{item}</li>')
        result.append('</ul>')
    
    return '\n'.join(result)

def convert_markdown_headers(text):
    """Markdown 헤더를 HTML로 변환"""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        header_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if header_match:
            level = len(header_match.group(1))
            content = process_markdown_formatting(header_match.group(2))
            result.append(f'<h{level}>{content}</h{level}>')
        else:
            result.append(line)
    
    return '\n'.join(result)

def convert_numbered_recommendations(text):
    """번호가 매겨진 권장사항을 HTML로 변환"""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        rec_match = re.match(r'^(\d+)\.\s*\*\*([^*]+)\*\*:\s*(.+)', line.strip())
        if rec_match:
            number = rec_match.group(1)
            title = rec_match.group(2)
            content = rec_match.group(3)
            
            html_line = f'<div class="recommendation-item">'
            html_line += f'<span class="recommendation-number">{number}.</span> '
            html_line += f'<strong>{title}</strong>: {content}'
            html_line += f'</div>'
            
            result.append(html_line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def convert_markdown_to_html(markdown_content):
    """전체 Markdown을 HTML로 변환"""
    # 1. 번호가 매겨진 권장사항 변환
    html_content = convert_numbered_recommendations(markdown_content)
    
    # 2. 테이블 변환
    html_content = convert_markdown_table(html_content)
    
    # 3. 리스트 변환
    html_content = convert_markdown_lists(html_content)
    
    # 4. 헤더 변환
    html_content = convert_markdown_headers(html_content)
    
    # 5. 단락 처리
    paragraphs = html_content.split('\n\n')
    processed_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            if para.startswith(('<h', '<table', '<ul', '<ol', '<div', '<p')):
                processed_paragraphs.append(para)
            else:
                para = process_markdown_formatting(para)
                if para:
                    processed_paragraphs.append(f'<p>{para}</p>')
    
    return '\n\n'.join(processed_paragraphs)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 simple-md-to-html.py <markdown_file>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    report_dir = "/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report"
    
    try:
        file_path = os.path.join(report_dir, md_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        html_content = convert_markdown_to_html(markdown_content)
        print(html_content)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
