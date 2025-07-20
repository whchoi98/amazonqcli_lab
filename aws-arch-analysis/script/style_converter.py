#!/usr/bin/env python3
import markdown
import os
from datetime import datetime

def main():
    # 스크립트의 실제 위치를 기준으로 경로 설정
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    input_file = str(project_root / "aws-arch-analysis" / "report" / "aws-resources-detailed-report.md")
    output_file = str(project_root / "aws-arch-analysis" / "report" / "aws-resources-style-based.html")
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['markdown.extensions.tables', 'markdown.extensions.toc'])
    
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    html_content = md.convert(markdown_content)
    
    # Create HTML with Style directory styling
    html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS 자원 상세 현황 보고서</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6; color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .report-header {{ 
            background: white; border-radius: 15px; padding: 40px; margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); text-align: center;
        }}
        .report-header h1 {{ font-size: 2.5em; color: #2c3e50; margin-bottom: 20px; font-weight: 700; }}
        .report-meta {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px; margin-top: 20px;
        }}
        .meta-item {{ 
            background: #f8f9fa; padding: 15px; border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .executive-summary {{ 
            background: white; border-radius: 15px; padding: 40px; margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px; }}
        .summary-card {{ padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); }}
        .summary-card.success {{ 
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left: 5px solid #28a745;
        }}
        .summary-card.warning {{ 
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 5px solid #ffc107;
        }}
        .cost-overview {{ 
            background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
            padding: 30px; border-radius: 12px; border: 2px solid #28a745;
        }}
        .cost-metrics {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;
        }}
        .metric {{ 
            text-align: center; background: white; padding: 20px;
            border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        .metric-value {{ 
            display: block; font-size: 2em; font-weight: bold;
            color: #3498db; margin-bottom: 5px;
        }}
        .metric-label {{ display: block; color: #7f8c8d; font-size: 0.9em; }}
        .detail-page {{ 
            background: white; border-radius: 15px; padding: 40px; margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .breadcrumb {{ 
            background: #f8f9fa; padding: 15px 20px; border-radius: 8px; margin-bottom: 30px;
        }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .workload-distribution {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; margin: 20px 0;
        }}
        .workload-card {{ 
            text-align: center; background: white; padding: 20px;
            border-radius: 10px; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }}
        .workload-number {{ 
            font-size: 2.5em; font-weight: bold; color: #3498db; margin-bottom: 10px;
        }}
        table {{ 
            width: 100%; border-collapse: collapse; margin: 20px 0; background: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;
        }}
        th {{ background: #3498db; color: white; padding: 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #e9ecef; }}
        tr:hover {{ background: #f8f9fa; }}
        h1 {{ font-size: 2.5em; color: #2c3e50; margin-bottom: 20px; font-weight: 700; }}
        h2 {{ 
            color: #2c3e50; font-size: 1.8em; margin: 30px 0 20px 0;
            padding-bottom: 10px; border-bottom: 3px solid #3498db;
        }}
        h3 {{ color: #34495e; font-size: 1.4em; margin: 25px 0 15px 0; font-weight: 600; }}
        h4 {{ color: #5a6c7d; font-size: 1.2em; margin: 20px 0 10px 0; font-weight: 600; }}
        .nav-buttons {{ 
            display: flex; justify-content: space-between; margin-top: 40px;
            padding-top: 20px; border-top: 1px solid #e9ecef;
        }}
        .nav-btn {{ 
            background: #3498db; color: white; padding: 12px 24px; border-radius: 8px;
            text-decoration: none; font-weight: 500; transition: all 0.3s ease;
        }}
        .nav-btn:hover {{ background: #2980b9; transform: translateY(-2px); }}
        code {{ 
            background: #f8f9fa; padding: 2px 6px; border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace; color: #e83e8c; font-size: 0.9em;
        }}
        pre {{ 
            background: #f8f9fa; padding: 20px; border-radius: 8px; overflow-x: auto;
            margin: 20px 0; border-left: 4px solid #3498db;
        }}
        @media (max-width: 768px) {{ 
            .container {{ padding: 10px; }}
            .detail-page {{ padding: 20px; }}
            .summary-grid {{ grid-template-columns: 1fr; }}
            h1 {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="#overview">🏠 개요</a> > <strong>AWS 자원 상세 현황 보고서</strong>
        </div>

        <header class="report-header">
            <h1>🎯 AWS 자원 상세 현황 보고서</h1>
            <div class="report-meta">
                <div class="meta-item"><strong>분석 대상:</strong> AWS 계정 349131490815</div>
                <div class="meta-item"><strong>분석 리전:</strong> ap-northeast-2 (서울)</div>
                <div class="meta-item"><strong>분석 일시:</strong> {datetime.now().strftime('%Y년 %m월 %d일')}</div>
                <div class="meta-item"><strong>분석 도구:</strong> Steampipe + AWS CLI + Python</div>
            </div>
        </header>

        <section class="executive-summary">
            <h2>📋 Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card success">
                    <h3>✅ 강점</h3>
                    <ul>
                        <li>멀티 VPC 아키텍처 (5개 VPC)</li>
                        <li>EKS 기반 컨테이너 플랫폼 (v1.31)</li>
                        <li>고가용성 구성 (2개 AZ)</li>
                        <li>적절한 네트워크 분리</li>
                    </ul>
                </div>
                <div class="summary-card warning">
                    <h3>⚠️ 개선 기회</h3>
                    <ul>
                        <li>비용 최적화: 월 $800 절약 가능</li>
                        <li>보안 강화: 29개 EBS 볼륨 암호화</li>
                        <li>모니터링 개선 필요</li>
                        <li>성능 최적화 기회</li>
                    </ul>
                </div>
            </div>
            
            <div class="cost-overview">
                <h3>💰 비용 분석 요약</h3>
                <div class="cost-metrics">
                    <div class="metric">
                        <span class="metric-value">$2,900</span>
                        <span class="metric-label">현재 월간 비용</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">$800</span>
                        <span class="metric-label">절약 가능 금액</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">28%</span>
                        <span class="metric-label">절감 비율</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">$9,600</span>
                        <span class="metric-label">연간 절약 효과</span>
                    </div>
                </div>
            </div>
        </section>

        <div class="detail-page">
            <h2>📊 주요 지표</h2>
            <div class="workload-distribution">
                <div class="workload-card">
                    <div class="workload-number">34</div>
                    <div>EC2 인스턴스</div>
                </div>
                <div class="workload-card">
                    <div class="workload-number">5</div>
                    <div>VPC</div>
                </div>
                <div class="workload-card">
                    <div class="workload-number">1</div>
                    <div>EKS 클러스터</div>
                </div>
                <div class="workload-card">
                    <div class="workload-number">14</div>
                    <div>CloudFormation 스택</div>
                </div>
            </div>
            
            {html_content}
        </div>

        <div class="nav-buttons">
            <a href="#overview" class="nav-btn">📊 개요로 돌아가기</a>
            <a href="#recommendations" class="nav-btn">💡 권장사항 보기</a>
        </div>
    </div>

    <script>
        document.querySelectorAll('td').forEach(function(cell) {{
            const text = cell.textContent.toLowerCase();
            if (text.includes('available') || text.includes('running') || text.includes('active')) {{
                cell.style.color = '#28a745';
                cell.style.fontWeight = 'bold';
            }}
        }});
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) target.scrollIntoView({{ behavior: 'smooth' }});
            }});
        }});
    </script>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Style-based HTML created: {output_file}")
    print(f"📊 File size: {os.path.getsize(output_file)} bytes")
    print(f"🎨 Based on: ~/amazonqcli_lab/Style/ HTML files")

if __name__ == "__main__":
    main()
