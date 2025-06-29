#!/usr/bin/env python3
"""
AWS 아키텍처 분석 보고서 Markdown → HTML 변환기
sample/index.html 스타일을 기반으로 전문적인 HTML 보고서 생성
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

try:
    import markdown
    from markdown.extensions import tables, codehilite, toc
except ImportError:
    print("❌ markdown 패키지가 설치되지 않았습니다.")
    print("설치 명령어: pip3 install markdown")
    exit(1)

class MarkdownToHtmlConverter:
    def __init__(self, report_dir="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report", 
                 output_dir="/home/ec2-user/amazonqcli_lab/html-report"):
        self.report_dir = Path(report_dir)
        self.output_dir = Path(output_dir)
        self.account_id = self.get_account_id()
        self.analysis_date = datetime.now().strftime("%Y-%m-%d")
        
        # 보고서 메타데이터
        self.reports = [
            {
                'file': '01-executive-summary.md',
                'html': '01-executive-summary.html',
                'title': '📊 전체 계정 분석 요약',
                'description': 'AWS 계정의 전반적인 상태와 주요 지표를 요약합니다.',
                'score': '양호 (79.7/100)',
                'icon': '📊'
            },
            {
                'file': '02-networking-analysis.md',
                'html': '02-networking-analysis.html',
                'title': '🌐 네트워킹 분석',
                'description': 'VPC, 서브넷, 보안 그룹 등 네트워킹 리소스를 분석합니다.',
                'score': '양호 (85/100)',
                'icon': '🌐'
            },
            {
                'file': '03-compute-analysis.md',
                'html': '03-compute-analysis.html',
                'title': '💻 컴퓨팅 분석',
                'description': 'EC2, Lambda, EKS 등 컴퓨팅 리소스를 분석합니다.',
                'score': '양호 (78/100)',
                'icon': '💻'
            },
            {
                'file': '05-database-analysis.md',
                'html': '05-database-analysis.html',
                'title': '🗄️ 데이터베이스 분석',
                'description': 'RDS, DynamoDB 등 데이터베이스 리소스를 분석합니다.',
                'score': '우수 (88/100)',
                'icon': '🗄️'
            },
            {
                'file': '05-storage-analysis.md',
                'html': '05-storage-analysis.html',
                'title': '💾 스토리지 분석',
                'description': 'EBS, S3, EFS 등 스토리지 리소스를 분석합니다.',
                'score': '양호 (82/100)',
                'icon': '💾'
            },
            {
                'file': '06-security-analysis.md',
                'html': '06-security-analysis.html',
                'title': '🔐 보안 분석',
                'description': 'IAM, KMS 등 보안 및 자격 증명 서비스를 분석합니다.',
                'score': '보통 (75/100)',
                'icon': '🔐'
            },
            {
                'file': '07-application-analysis.md',
                'html': '07-application-analysis.html',
                'title': '🌐 애플리케이션 분석',
                'description': 'API Gateway, SNS 등 애플리케이션 서비스를 분석합니다.',
                'score': '양호 (80/100)',
                'icon': '🌐'
            },
            {
                'file': '08-monitoring-analysis.md',
                'html': '08-monitoring-analysis.html',
                'title': '📊 모니터링 분석',
                'description': 'CloudWatch, 로깅 등 모니터링 서비스를 분석합니다.',
                'score': '보통 (70/100)',
                'icon': '📊'
            },
            {
                'file': '09-cost-optimization.md',
                'html': '09-cost-optimization.html',
                'title': '💰 비용 최적화',
                'description': '비용 절감 기회와 최적화 방안을 제시합니다.',
                'score': '보통 (70/100)',
                'icon': '💰'
            },
            {
                'file': '10-recommendations.md',
                'html': '10-recommendations.html',
                'title': '🎯 종합 권장사항',
                'description': '전체 분석 결과를 바탕으로 한 종합적인 개선 방안입니다.',
                'score': '실행 계획',
                'icon': '🎯'
            }
        ]
        
    def get_account_id(self):
        """AWS 계정 ID 가져오기"""
        try:
            import subprocess
            result = subprocess.run(['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "N/A"
        except:
            return "N/A"
    
    def get_score_class(self, score):
        """점수에 따른 CSS 클래스 반환"""
        if "우수" in score or "90" in score:
            return "excellent"
        elif "양호" in score or "80" in score or "85" in score or "78" in score or "82" in score:
            return "good"
        elif "보통" in score or "70" in score or "75" in score:
            return "fair"
        else:
            return "poor"
    
    def create_output_directory(self):
        """출력 디렉토리 생성"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 출력 디렉토리 생성: {self.output_dir}")
    
    def get_base_css(self):
        """기본 CSS 스타일 반환"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .nav-card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
        }
        
        .nav-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            text-decoration: none;
            color: inherit;
        }
        
        .nav-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .nav-card p {
            color: #666;
            margin-bottom: 15px;
        }
        
        .score {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .score.excellent {
            background-color: #d4edda;
            color: #155724;
        }
        
        .score.good {
            background-color: #d1ecf1;
            color: #0c5460;
        }
        
        .score.fair {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .score.poor {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        .summary-section {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .summary-section h2 {
            color: #667eea;
            margin-bottom: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        tr:hover {
            background: #e3f2fd;
        }
        
        .content {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        .nav-back {
            display: inline-block;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s ease;
        }
        
        .nav-back:hover {
            background: #5a6fd8;
            text-decoration: none;
            color: white;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin: 30px 0 15px 0;
            font-weight: 600;
        }
        
        h1 {
            font-size: 2.2em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        h2 {
            font-size: 1.8em;
            color: #667eea;
        }
        
        h3 {
            font-size: 1.4em;
            color: #5a6fd8;
        }
        
        p {
            margin: 15px 0;
        }
        
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
        }
        
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }
        
        pre code {
            background: none;
            color: inherit;
        }
        
        ul, ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        
        li {
            margin: 8px 0;
        }
        
        blockquote {
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            background: #f8f9fa;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .priority-high {
            color: #dc3545;
            font-weight: bold;
        }
        
        .priority-medium {
            color: #ffc107;
            font-weight: bold;
        }
        
        .priority-low {
            color: #28a745;
            font-weight: bold;
        }
        """
    
    def create_index_html(self):
        """메인 인덱스 페이지 생성"""
        # 네비게이션 카드 생성
        nav_cards = ""
        for report in self.reports:
            score_class = self.get_score_class(report['score'])
            nav_cards += f"""
            <a href="{report['html']}" class="nav-card">
                <h3>{report['title']}</h3>
                <p>{report['description']}</p>
                <span class="score {score_class}">{report['score']}</span>
            </a>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS 계정 종합 분석 보고서</title>
    <style>
        {self.get_base_css()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 AWS 계정 종합 분석 보고서</h1>
            <p>계정 ID: {self.account_id} | 리전: ap-northeast-2 | 분석일: {self.analysis_date}</p>
        </div>
        
        <div class="nav-grid">
            {nav_cards}
        </div>
        
        <div class="summary-section">
            <h2>📋 분석 개요</h2>
            <p><strong>분석 도구:</strong> Steampipe + AWS CLI + Amazon Q</p>
            <p><strong>분석 방법:</strong> 실제 수집된 JSON 데이터 기반 체계적 분석</p>
            <p><strong>보고서 구성:</strong> 10개 섹션별 상세 분석</p>
            <p><strong>총 데이터 크기:</strong> 약 30KB+ 상세 분석 보고서</p>
        </div>
        
        <div class="summary-section">
            <h2>🎯 주요 발견 사항</h2>
            <table>
                <tr>
                    <th>분야</th>
                    <th>현황</th>
                    <th>주요 이슈</th>
                    <th>우선순위</th>
                </tr>
                <tr>
                    <td>네트워킹</td>
                    <td>VPC 5개, 보안 그룹 25개</td>
                    <td>VPC 구성 최적화 필요</td>
                    <td class="priority-medium">중간</td>
                </tr>
                <tr>
                    <td>컴퓨팅</td>
                    <td>EC2 34개, EKS 1개</td>
                    <td>인스턴스 타입 최적화 권장</td>
                    <td class="priority-medium">중간</td>
                </tr>
                <tr>
                    <td>스토리지</td>
                    <td>EBS 34개 (960GB)</td>
                    <td>암호화 설정 강화 필요</td>
                    <td class="priority-high">높음</td>
                </tr>
                <tr>
                    <td>보안</td>
                    <td>IAM 사용자 2개, 역할 47개</td>
                    <td>IAM 정책 강화 필요</td>
                    <td class="priority-high">높음</td>
                </tr>
                <tr>
                    <td>모니터링</td>
                    <td>로그 그룹 7개, 알람 0개</td>
                    <td>CloudWatch 알람 설정 부족</td>
                    <td class="priority-high">높음</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>"""
        
        index_path = self.output_dir / "index.html"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 메인 인덱스 페이지 생성: {index_path}")
    
    def convert_markdown_to_html(self, md_file, html_file, title):
        """개별 Markdown 파일을 HTML로 변환"""
        md_path = self.report_dir / md_file
        html_path = self.output_dir / html_file
        
        if not md_path.exists():
            print(f"⚠️ 파일 없음: {md_path}")
            return
        
        # Markdown 파일 읽기
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Markdown을 HTML로 변환
        md = markdown.Markdown(extensions=['tables', 'codehilite', 'toc'])
        html_body = md.convert(md_content)
        
        # 우선순위 색상 적용
        html_body = re.sub(r'🔴', '<span class="priority-high">🔴</span>', html_body)
        html_body = re.sub(r'🟡', '<span class="priority-medium">🟡</span>', html_body)
        html_body = re.sub(r'🟢', '<span class="priority-low">🟢</span>', html_body)
        
        # 완전한 HTML 문서 생성
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AWS 계정 종합 분석 보고서</title>
    <style>
        {self.get_base_css()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>AWS 계정 종합 분석 보고서</p>
        </div>
        <div class="content">
            <a href="index.html" class="nav-back">← 메인 페이지로 돌아가기</a>
            {html_body}
        </div>
    </div>
</body>
</html>"""
        
        # HTML 파일 저장
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 변환 완료: {md_file} → {html_file}")
    
    def convert_all(self):
        """모든 보고서 변환"""
        print("🚀 AWS 아키텍처 분석 보고서 HTML 변환 시작...")
        print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 출력 디렉토리 생성
        self.create_output_directory()
        
        # 메인 인덱스 페이지 생성
        self.create_index_html()
        
        # 각 보고서 변환
        for report in self.reports:
            self.convert_markdown_to_html(
                report['file'], 
                report['html'], 
                report['title']
            )
        
        print(f"🎉 모든 HTML 보고서 생성 완료!")
        print(f"📁 출력 디렉토리: {self.output_dir}")
        print(f"🌐 메인 페이지: {self.output_dir}/index.html")
        print(f"📅 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 생성된 파일 목록 출력
        html_files = list(self.output_dir.glob("*.html"))
        print(f"\n📋 생성된 HTML 파일 ({len(html_files)}개):")
        for html_file in sorted(html_files):
            size = html_file.stat().st_size
            print(f"  - {html_file.name} ({size:,} bytes)")

def main():
    """메인 실행 함수"""
    converter = MarkdownToHtmlConverter()
    converter.convert_all()

if __name__ == "__main__":
    main()
