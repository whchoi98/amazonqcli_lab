#!/usr/bin/env python3
"""
빠른 Markdown to HTML 변환기
올바른 경로를 사용하여 생성된 보고서를 HTML로 변환
"""

import os
import markdown
from pathlib import Path
import shutil

def create_html_template(title, content, nav_links=""):
    """HTML 템플릿 생성"""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AWS 계정 분석 보고서</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .nav-menu {{
            background: #2c3e50;
            padding: 15px;
            margin: -30px -30px 30px -30px;
            border-radius: 10px 10px 0 0;
        }}
        .nav-menu a {{
            color: white;
            text-decoration: none;
            margin-right: 20px;
            padding: 8px 12px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }}
        .nav-menu a:hover {{
            background-color: #34495e;
        }}
        .status-success {{ color: #27ae60; font-weight: bold; }}
        .status-warning {{ color: #f39c12; font-weight: bold; }}
        .status-error {{ color: #e74c3c; font-weight: bold; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-menu">
            <a href="index.html">🏠 대시보드</a>
            <a href="01-executive-summary.html">📊 경영진 요약</a>
            <a href="02-networking-analysis.html">🌐 네트워킹</a>
            <a href="05-storage-analysis.html">💾 스토리지</a>
            <a href="05-database-analysis.html">🗄️ 데이터베이스</a>
            <a href="06-security-analysis.html">🔒 보안</a>
            <a href="07-application-analysis.html">🌐 애플리케이션</a>
            <a href="09-cost-optimization.html">💰 비용최적화</a>
            <a href="09-monitoring-analysis.html">📊 모니터링</a>
            <a href="10-recommendations.html">🛠️ 권장사항</a>
        </div>
        {content}
    </div>
</body>
</html>"""

def create_index_html(output_dir):
    """메인 인덱스 페이지 생성"""
    index_content = """
    <h1>🏠 AWS 계정 분석 대시보드</h1>
    
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; margin-top: 0;">📋 분석 개요</h2>
        <p><strong>분석 일자:</strong> 2025년 6월 26일</p>
        <p><strong>AWS 계정:</strong> 613137910751</p>
        <p><strong>분석 리전:</strong> ap-northeast-2 (서울)</p>
        <p><strong>수집된 데이터:</strong> 114개 JSON 파일 (1.5MB)</p>
    </div>

    <h2>📊 생성된 분석 보고서</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="01-executive-summary.html" style="text-decoration: none; color: #2c3e50;">📊 경영진 요약</a></h3>
            <p>전체 인프라 현황과 주요 발견사항을 요약한 경영진용 보고서</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="02-networking-analysis.html" style="text-decoration: none; color: #2c3e50;">🌐 네트워킹 분석</a></h3>
            <p>VPC, 서브넷, 보안그룹 등 네트워킹 인프라 상세 분석</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="05-storage-analysis.html" style="text-decoration: none; color: #2c3e50;">💾 스토리지 분석</a></h3>
            <p>EBS, S3 등 스토리지 리소스 사용 현황 및 최적화 방안</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="05-database-analysis.html" style="text-decoration: none; color: #2c3e50;">🗄️ 데이터베이스 분석</a></h3>
            <p>RDS, ElastiCache 등 데이터베이스 서비스 구성 및 성능 분석</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="06-security-analysis.html" style="text-decoration: none; color: #2c3e50;">🔒 보안 분석</a></h3>
            <p>IAM, KMS 등 보안 설정 현황 및 보안 강화 방안</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="07-application-analysis.html" style="text-decoration: none; color: #2c3e50;">🌐 애플리케이션 분석</a></h3>
            <p>API Gateway, EventBridge 등 애플리케이션 서비스 분석</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="09-cost-optimization.html" style="text-decoration: none; color: #2c3e50;">💰 비용 최적화</a></h3>
            <p>비용 분석 및 최적화 기회 식별</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="09-monitoring-analysis.html" style="text-decoration: none; color: #2c3e50;">📊 모니터링 분석</a></h3>
            <p>CloudWatch 등 모니터링 도구 활용 현황 분석</p>
        </div>
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
            <h3><a href="10-recommendations.html" style="text-decoration: none; color: #2c3e50;">🛠️ 종합 권장사항</a></h3>
            <p>전체 분석 결과를 바탕으로 한 통합 권장사항</p>
        </div>
    </div>

    <h2>🎯 주요 발견사항</h2>
    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="color: #856404; margin-top: 0;">⚠️ 주요 개선 필요 사항</h3>
        <ul>
            <li><strong>VPC Flow Logs 미활성화:</strong> 네트워크 트래픽 모니터링 강화 필요</li>
            <li><strong>CloudTrail 미구성:</strong> API 호출 로깅 및 감사 추적 설정 필요</li>
            <li><strong>Config 규칙 미설정:</strong> 리소스 구성 준수 모니터링 필요</li>
            <li><strong>GuardDuty 미활성화:</strong> 위협 탐지 서비스 구성 필요</li>
        </ul>
    </div>

    <div style="background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="color: #0c5460; margin-top: 0;">✅ 잘 구성된 영역</h3>
        <ul>
            <li><strong>네트워킹 인프라:</strong> 멀티 VPC 아키텍처 및 Transit Gateway 연결</li>
            <li><strong>데이터베이스:</strong> RDS Aurora 및 ElastiCache 클러스터 운영</li>
            <li><strong>컨테이너:</strong> EKS 클러스터 및 Kubernetes 리소스 관리</li>
            <li><strong>암호화:</strong> KMS 키를 통한 데이터 암호화 적용</li>
        </ul>
    </div>
    """
    
    index_html = create_html_template("AWS 계정 분석 대시보드", index_content)
    
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

def convert_markdown_to_html():
    """Markdown 파일들을 HTML로 변환"""
    input_dir = Path("/home/ec2-user/amazonqcli_lab/aws-arch-analysis/report")
    output_dir = Path("/home/ec2-user/amazonqcli_lab/html-report")
    
    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Markdown to HTML 변환 시작...")
    print(f"📁 입력 디렉토리: {input_dir}")
    print(f"📁 출력 디렉토리: {output_dir}")
    
    # 메인 인덱스 페이지 생성
    create_index_html(output_dir)
    print("✅ index.html 생성 완료")
    
    # Markdown 파일 목록
    md_files = list(input_dir.glob("*.md"))
    print(f"📋 발견된 Markdown 파일: {len(md_files)}개")
    
    converted_count = 0
    
    for md_file in md_files:
        try:
            # Markdown 파일 읽기
            with open(md_file, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            # Markdown을 HTML로 변환
            html_content = markdown.markdown(
                md_content,
                extensions=['tables', 'fenced_code', 'toc']
            )
            
            # HTML 파일명 생성
            html_filename = md_file.stem + ".html"
            html_path = output_dir / html_filename
            
            # 제목 추출 (첫 번째 # 헤더)
            title = md_file.stem.replace("-", " ").title()
            if md_content.startswith("#"):
                title = md_content.split("\n")[0].replace("#", "").strip()
            
            # 완전한 HTML 페이지 생성
            full_html = create_html_template(title, html_content)
            
            # HTML 파일 저장
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            
            file_size = html_path.stat().st_size
            print(f"✅ {html_filename} 생성 완료 ({file_size:,} bytes)")
            converted_count += 1
            
        except Exception as e:
            print(f"❌ {md_file.name} 변환 실패: {str(e)}")
    
    print(f"\n🎉 변환 완료!")
    print(f"📊 성공: {converted_count}/{len(md_files)} 파일")
    print(f"📁 출력 위치: {output_dir}")
    
    # 생성된 HTML 파일 목록
    html_files = list(output_dir.glob("*.html"))
    print(f"\n📋 생성된 HTML 파일 ({len(html_files)}개):")
    for html_file in sorted(html_files):
        size = html_file.stat().st_size
        print(f"  📄 {html_file.name} ({size:,} bytes)")
    
    return len(html_files)

if __name__ == "__main__":
    try:
        total_files = convert_markdown_to_html()
        print(f"\n🌐 브라우저에서 확인:")
        print(f"  file:///home/ec2-user/amazonqcli_lab/html-report/index.html")
        print(f"\n💡 로컬 웹 서버 실행:")
        print(f"  cd /home/ec2-user/amazonqcli_lab/html-report")
        print(f"  python3 -m http.server 8080")
        print(f"  브라우저에서 http://localhost:8080 접속")
        
    except Exception as e:
        print(f"❌ 변환 중 오류 발생: {str(e)}")
