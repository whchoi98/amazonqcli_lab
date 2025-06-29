#!/usr/bin/env python3
"""
HTML 변환 및 대시보드 생성 모듈
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict

try:
    import markdown
except ImportError:
    print("Warning: markdown 패키지가 설치되지 않았습니다. pip install markdown을 실행하세요.")
    markdown = None

class HTMLConverter:
    """Markdown을 HTML로 변환하는 클래스"""
    
    def __init__(self, aws_account_id: str):
        self.aws_account_id = aws_account_id
    
    def convert_md_to_html(self, input_file: str, output_file: str, title: str):
        """Markdown 파일을 HTML로 변환"""
        if not markdown:
            print(f"Markdown 패키지가 없어 {input_file} 변환을 건너뜁니다.")
            return
        
        try:
            # Markdown 내용 읽기
            with open(input_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Markdown을 HTML로 변환
            md = markdown.Markdown(extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.toc',
                'markdown.extensions.fenced_code'
            ])
            
            html_content = md.convert(markdown_content)
            
            # HTML 템플릿 생성
            html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 10px; 
            box-shadow: 0 0 20px rgba(0,0,0,0.1); 
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
        }}
        th, td {{ 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }}
        th {{ 
            background-color: #3498db; 
            color: white; 
        }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        code {{ 
            background: #f4f4f4; 
            padding: 2px 4px; 
            border-radius: 3px; 
        }}
        pre {{ 
            background: #2c3e50; 
            color: white; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto; 
        }}
        .nav-back {{ 
            display: inline-block; 
            margin-bottom: 20px; 
            padding: 10px 20px; 
            background: #3498db; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="nav-back">← 메인 대시보드로 돌아가기</a>
        {html_content}
        <hr>
        <p><small>생성일: {datetime.now().strftime('%Y년 %m월 %d일')} | AWS 계정: {self.aws_account_id}</small></p>
    </div>
</body>
</html>"""
            
            # HTML 파일 쓰기
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            print(f"✅ {input_file} → {output_file}")
            
        except Exception as e:
            print(f"❌ {input_file} 변환 실패: {e}")
    
    def convert_all_markdown_files(self):
        """모든 Markdown 파일을 HTML로 변환"""
        files_to_convert = [
            ("01-executive-summary.md", "01-executive-summary.html", "전체 계정 분석 요약"),
            ("02-networking-analysis.md", "02-networking-analysis.html", "네트워킹 분석"),
            ("03-computing-analysis.md", "03-computing-analysis.html", "컴퓨팅 분석"),
            ("04-storage-analysis.md", "04-storage-analysis.html", "스토리지 분석"),
            ("05-database-analysis.md", "05-database-analysis.html", "데이터베이스 분석"),
            ("06-security-analysis.md", "06-security-analysis.html", "보안 분석"),
            ("07-cost-optimization.md", "07-cost-optimization.html", "비용 최적화"),
            ("08-application-monitoring.md", "08-application-monitoring.html", "애플리케이션 서비스"),
            ("09-comprehensive-recommendations.md", "09-comprehensive-recommendations.html", "종합 권장사항"),
            ("10-implementation-guide.md", "10-implementation-guide.html", "구현 가이드")
        ]
        
        for md_file, html_file, title in files_to_convert:
            if os.path.exists(md_file):
                self.convert_md_to_html(md_file, html_file, title)

class DashboardGenerator:
    """메인 대시보드 생성기"""
    
    def __init__(self, aws_account_id: str, aws_region: str, analysis_results: Dict):
        self.aws_account_id = aws_account_id
        self.aws_region = aws_region
        self.analysis_results = analysis_results
    
    def generate_dashboard(self):
        """메인 대시보드 HTML 생성"""
        dashboard_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS 계정 종합 분석 보고서</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            padding: 20px; 
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            background: white; 
            border-radius: 15px; 
            padding: 40px; 
            margin-bottom: 30px; 
            text-align: center; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
        }}
        .header h1 {{ 
            font-size: 2.5em; 
            color: #2c3e50; 
            margin-bottom: 20px; 
        }}
        .metrics {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        .metric {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
        }}
        .metric .number {{ 
            font-size: 2em; 
            font-weight: bold; 
            color: #3498db; 
        }}
        .nav-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }}
        .nav-card {{ 
            background: white; 
            border-radius: 10px; 
            padding: 25px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            transition: transform 0.3s ease; 
            cursor: pointer; 
        }}
        .nav-card:hover {{ transform: translateY(-5px); }}
        .nav-card h3 {{ 
            color: #3498db; 
            margin-bottom: 15px; 
        }}
        .footer {{ 
            text-align: center; 
            padding: 30px; 
            color: white; 
            margin-top: 30px; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ AWS 계정 종합 분석 보고서</h1>
            <p>계정 ID: {self.aws_account_id} | 리전: {self.aws_region} | 생성일: {datetime.now().strftime('%Y년 %m월 %d일')}</p>
            <div class="metrics">
                <div class="metric">
                    <div class="number">{self.analysis_results['vpc_count']}</div>
                    <div>VPC 개수</div>
                </div>
                <div class="metric">
                    <div class="number">{self.analysis_results['ec2_count']}</div>
                    <div>EC2 인스턴스</div>
                </div>
                <div class="metric">
                    <div class="number">{self.analysis_results['security_group_count']}</div>
                    <div>보안 그룹</div>
                </div>
                <div class="metric">
                    <div class="number">${self.analysis_results['total_cost']:.2f}</div>
                    <div>월간 비용</div>
                </div>
            </div>
        </div>
        
        <div class="nav-grid">
            <div class="nav-card" onclick="window.open('01-executive-summary.html', '_blank')">
                <h3>📋 전체 계정 분석 요약</h3>
                <p>AWS 계정의 전반적인 현황과 핵심 발견사항 요약</p>
            </div>
            <div class="nav-card" onclick="window.open('02-networking-analysis.html', '_blank')">
                <h3>🌐 네트워킹 분석</h3>
                <p>VPC, 서브넷, 보안 그룹 등 네트워크 아키텍처 분석</p>
            </div>
            <div class="nav-card" onclick="window.open('03-computing-analysis.html', '_blank')">
                <h3>💻 컴퓨팅 분석</h3>
                <p>EC2, EKS 등 컴퓨팅 리소스 현황 및 최적화 방안</p>
            </div>
            <div class="nav-card" onclick="window.open('04-storage-analysis.html', '_blank')">
                <h3>💾 스토리지 분석</h3>
                <p>S3, EBS 등 스토리지 서비스 분석 및 최적화</p>
            </div>
            <div class="nav-card" onclick="window.open('05-database-analysis.html', '_blank')">
                <h3>🗄️ 데이터베이스 분석</h3>
                <p>RDS, ElastiCache 등 데이터베이스 서비스 분석</p>
            </div>
            <div class="nav-card" onclick="window.open('06-security-analysis.html', '_blank')">
                <h3>🔒 보안 분석</h3>
                <p>보안 그룹, IAM 등 보안 아키텍처 분석</p>
            </div>
            <div class="nav-card" onclick="window.open('07-cost-optimization.html', '_blank')">
                <h3>💰 비용 최적화</h3>
                <p>서비스별 비용 분석 및 최적화 전략</p>
            </div>
            <div class="nav-card" onclick="window.open('08-application-monitoring.html', '_blank')">
                <h3>📊 애플리케이션 서비스</h3>
                <p>모니터링, 로깅 등 애플리케이션 서비스 분석</p>
            </div>
            <div class="nav-card" onclick="window.open('09-comprehensive-recommendations.html', '_blank')">
                <h3>🎯 종합 권장사항</h3>
                <p>전체 분석 결과 기반 전략적 권장사항</p>
            </div>
            <div class="nav-card" onclick="window.open('10-implementation-guide.html', '_blank')">
                <h3>🛠️ 구현 가이드</h3>
                <p>단계별 구현 방법 및 실행 가이드</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>AWS 계정 종합 분석 보고서</strong></p>
            <p>자동 생성: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')} | 분석 도구: Steampipe + AWS CLI</p>
        </div>
    </div>
</body>
</html>"""
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        print("✅ 메인 대시보드 생성 완료: index.html")
