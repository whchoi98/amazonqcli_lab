# Steampipe 결과를 Notion으로 자동 Export하는 방법

## 방법 1: Notion API를 사용한 직접 연동

### 1. Notion Integration 생성

1. [Notion Developers](https://developers.notion.com/)에 접속
2. "My integrations" → "New integration" 클릭
3. Integration 이름 설정 (예: "Steampipe Export")
4. **Internal Integration Token** 복사 및 저장

### 2. Notion 데이터베이스 준비

1. Notion에서 새 페이지 생성
2. 데이터베이스 생성 (테이블 형태)
3. 필요한 컬럼 추가:
   - Title (제목)
   - Query (쿼리 내용)
   - Results (결과)
   - Timestamp (실행 시간)
   - Status (상태)

### 3. 데이터베이스 권한 설정

1. 데이터베이스 페이지에서 "Share" 클릭
2. 생성한 Integration 추가
3. "Can edit" 권한 부여

### 4. Python 스크립트 작성

```python
#!/usr/bin/env python3
import os
import json
import subprocess
import requests
from datetime import datetime

# Notion 설정
NOTION_TOKEN = "your_notion_integration_token"
DATABASE_ID = "your_database_id"

def run_steampipe_query(query):
    """Steampipe 쿼리 실행"""
    try:
        result = subprocess.run(
            ['steampipe', 'query', query, '--output', 'json'],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}

def create_notion_page(title, query, results):
    """Notion 페이지 생성"""
    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 결과를 마크다운 테이블로 변환
    markdown_table = format_results_as_markdown(results)
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "Query": {
                "rich_text": [{"text": {"content": query}}]
            },
            "Timestamp": {
                "date": {"start": datetime.now().isoformat()}
            },
            "Status": {
                "select": {"name": "Completed"}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "code",
                "code": {
                    "caption": [],
                    "rich_text": [{"type": "text", "text": {"content": query}}],
                    "language": "sql"
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": markdown_table}}]
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def format_results_as_markdown(results):
    """결과를 마크다운 테이블로 변환"""
    if not results or "error" in results:
        return f"Error: {results.get('error', 'Unknown error')}"
    
    if not results.get('rows'):
        return "No results found"
    
    # 헤더 생성
    headers = list(results['rows'][0].keys()) if results['rows'] else []
    markdown = "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # 데이터 행 추가
    for row in results['rows'][:50]:  # 최대 50행으로 제한
        values = [str(row.get(header, "")) for header in headers]
        markdown += "| " + " | ".join(values) + " |\n"
    
    return markdown

# 사용 예제
if __name__ == "__main__":
    query = "SELECT instance_id, instance_type, instance_state FROM aws_ec2_instance LIMIT 10;"
    title = f"EC2 Instances Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    results = run_steampipe_query(query)
    notion_response = create_notion_page(title, query, results)
    
    print(f"Notion page created: {notion_response}")
```

## 방법 2: GitHub Actions를 통한 자동화

### 1. GitHub Repository 설정

```yaml
# .github/workflows/steampipe-to-notion.yml
name: Steampipe to Notion Export

on:
  schedule:
    - cron: '0 9 * * 1'  # 매주 월요일 9시
  workflow_dispatch:  # 수동 실행 가능

jobs:
  export-to-notion:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Steampipe
      run: |
        curl -s https://raw.githubusercontent.com/turbot/steampipe/main/install.sh | bash
        steampipe plugin install aws
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Run Steampipe queries and export to Notion
      env:
        NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
        DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
      run: |
        python3 scripts/steampipe_to_notion.py
```

## 방법 3: 로컬 자동화 스크립트

### 1. 환경 설정

```bash
# 환경 변수 설정
export NOTION_TOKEN="your_notion_integration_token"
export NOTION_DATABASE_ID="your_database_id"

# Python 패키지 설치
pip3 install requests python-dotenv
```

### 2. 설정 파일 생성

```bash
# .env 파일 생성
cat > ~/.steampipe_notion.env << EOF
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id
EOF
```

### 3. 고급 Python 스크립트

```python
#!/usr/bin/env python3
"""
Steampipe to Notion Export Tool
고급 기능이 포함된 자동 export 도구
"""

import os
import json
import subprocess
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv

class SteampipeNotionExporter:
    def __init__(self):
        load_dotenv(os.path.expanduser('~/.steampipe_notion.env'))
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def run_query(self, query, output_format='json'):
        """Steampipe 쿼리 실행"""
        try:
            cmd = ['steampipe', 'query', query, '--output', output_format]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if output_format == 'json':
                return json.loads(result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return {"error": f"Query failed: {e.stderr}"}
    
    def create_database_page(self, title, query, results, tags=None):
        """Notion 데이터베이스에 페이지 생성"""
        url = f"{self.base_url}/pages"
        
        # 결과 처리
        if isinstance(results, dict) and "error" in results:
            status = "Failed"
            content_blocks = [self._create_error_block(results["error"])]
        else:
            status = "Success"
            content_blocks = [
                self._create_query_block(query),
                self._create_results_block(results)
            ]
        
        # 페이지 속성
        properties = {
            "Title": {"title": [{"text": {"content": title}}]},
            "Query": {"rich_text": [{"text": {"content": query}}]},
            "Timestamp": {"date": {"start": datetime.now().isoformat()}},
            "Status": {"select": {"name": status}}
        }
        
        # 태그 추가
        if tags:
            properties["Tags"] = {
                "multi_select": [{"name": tag} for tag in tags]
            }
        
        data = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
            "children": content_blocks
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def _create_query_block(self, query):
        """SQL 쿼리 블록 생성"""
        return {
            "object": "block",
            "type": "code",
            "code": {
                "caption": [{"type": "text", "text": {"content": "SQL Query"}}],
                "rich_text": [{"type": "text", "text": {"content": query}}],
                "language": "sql"
            }
        }
    
    def _create_results_block(self, results):
        """결과 테이블 블록 생성"""
        if isinstance(results, str):
            # CSV 형태의 결과
            return {
                "object": "block",
                "type": "code",
                "code": {
                    "caption": [{"type": "text", "text": {"content": "Results"}}],
                    "rich_text": [{"type": "text", "text": {"content": results}}],
                    "language": "plain text"
                }
            }
        
        # JSON 형태의 결과를 테이블로 변환
        table_markdown = self._format_as_table(results)
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": table_markdown}}]
            }
        }
    
    def _create_error_block(self, error_message):
        """에러 블록 생성"""
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": f"Error: {error_message}"}}],
                "icon": {"emoji": "❌"},
                "color": "red_background"
            }
        }
    
    def _format_as_table(self, results):
        """JSON 결과를 마크다운 테이블로 변환"""
        if not results or not results.get('rows'):
            return "No results found"
        
        rows = results['rows']
        if not rows:
            return "No data returned"
        
        # 헤더 추출
        headers = list(rows[0].keys())
        
        # 마크다운 테이블 생성
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        # 데이터 행 추가 (최대 100행)
        for row in rows[:100]:
            values = []
            for header in headers:
                value = str(row.get(header, ""))
                # 특수 문자 이스케이프
                value = value.replace("|", "\\|").replace("\n", " ")
                values.append(value)
            table += "| " + " | ".join(values) + " |\n"
        
        if len(rows) > 100:
            table += f"\n*Showing first 100 rows of {len(rows)} total results*"
        
        return table
    
    def export_predefined_reports(self):
        """미리 정의된 보고서들 실행"""
        reports = [
            {
                "title": "EC2 Instances Overview",
                "query": """
                    SELECT 
                        instance_id,
                        instance_type,
                        instance_state,
                        availability_zone,
                        public_ip_address,
                        private_ip_address,
                        launch_time
                    FROM aws_ec2_instance 
                    ORDER BY launch_time DESC 
                    LIMIT 50;
                """,
                "tags": ["AWS", "EC2", "Infrastructure"]
            },
            {
                "title": "S3 Buckets Security Check",
                "query": """
                    SELECT 
                        name,
                        region,
                        versioning_enabled,
                        public_access_block_configuration,
                        server_side_encryption_configuration
                    FROM aws_s3_bucket;
                """,
                "tags": ["AWS", "S3", "Security"]
            },
            {
                "title": "IAM Users without MFA",
                "query": """
                    SELECT 
                        name,
                        user_id,
                        create_date,
                        password_last_used,
                        mfa_enabled
                    FROM aws_iam_user 
                    WHERE mfa_enabled = false;
                """,
                "tags": ["AWS", "IAM", "Security", "MFA"]
            }
        ]
        
        results = []
        for report in reports:
            print(f"Running report: {report['title']}")
            query_results = self.run_query(report['query'])
            notion_result = self.create_database_page(
                title=f"{report['title']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                query=report['query'],
                results=query_results,
                tags=report['tags']
            )
            results.append(notion_result)
            print(f"✅ Report exported to Notion")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Export Steampipe results to Notion')
    parser.add_argument('--query', '-q', help='SQL query to execute')
    parser.add_argument('--title', '-t', help='Title for the Notion page')
    parser.add_argument('--tags', help='Comma-separated tags')
    parser.add_argument('--reports', '-r', action='store_true', 
                       help='Run predefined reports')
    
    args = parser.parse_args()
    
    exporter = SteampipeNotionExporter()
    
    if args.reports:
        exporter.export_predefined_reports()
    elif args.query:
        title = args.title or f"Steampipe Query - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        tags = args.tags.split(',') if args.tags else None
        
        results = exporter.run_query(args.query)
        notion_result = exporter.create_database_page(title, args.query, results, tags)
        print(f"Exported to Notion: {notion_result}")
    else:
        print("Please provide a query with --query or use --reports for predefined reports")

if __name__ == "__main__":
    main()
```

## 방법 4: Cron을 통한 정기 실행

### 1. Cron 작업 설정

```bash
# crontab 편집
crontab -e

# 매일 오전 9시에 보고서 실행
0 9 * * * /usr/bin/python3 /home/ec2-user/steampipe_notion_exporter.py --reports

# 매주 월요일 오전 10시에 보안 체크
0 10 * * 1 /usr/bin/python3 /home/ec2-user/steampipe_notion_exporter.py --query "SELECT * FROM aws_iam_user WHERE mfa_enabled = false" --title "Weekly MFA Check"
```

## 방법 5: Webhook을 통한 실시간 연동

### 1. Flask 웹훅 서버

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify
import threading
from steampipe_notion_exporter import SteampipeNotionExporter

app = Flask(__name__)
exporter = SteampipeNotionExporter()

@app.route('/webhook/steampipe', methods=['POST'])
def steampipe_webhook():
    data = request.json
    
    query = data.get('query')
    title = data.get('title', f"Webhook Query - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    tags = data.get('tags', [])
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    # 백그라운드에서 실행
    def run_export():
        results = exporter.run_query(query)
        exporter.create_database_page(title, query, results, tags)
    
    thread = threading.Thread(target=run_export)
    thread.start()
    
    return jsonify({"status": "Query submitted for processing"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 설치 및 설정 스크립트

```bash
#!/bin/bash
# setup_steampipe_notion.sh

echo "🚀 Steampipe to Notion Export 설정 시작..."

# Python 패키지 설치
pip3 install requests python-dotenv flask

# 스크립트 다운로드 및 실행 권한 부여
chmod +x steampipe_notion_exporter.py

# 환경 변수 설정 도움말
echo "📝 다음 단계를 완료하세요:"
echo "1. Notion Integration Token 발급"
echo "2. Notion Database ID 확인"
echo "3. ~/.steampipe_notion.env 파일에 토큰 설정"
echo ""
echo "예시:"
echo "NOTION_TOKEN=secret_your_token_here"
echo "NOTION_DATABASE_ID=your_database_id_here"
echo ""
echo "✅ 설정 완료 후 다음 명령어로 테스트:"
echo "python3 steampipe_notion_exporter.py --reports"
```

## 사용 예제

```bash
# 미리 정의된 보고서 실행
python3 steampipe_notion_exporter.py --reports

# 커스텀 쿼리 실행
python3 steampipe_notion_exporter.py --query "SELECT * FROM aws_s3_bucket" --title "S3 Buckets Report" --tags "AWS,S3,Storage"

# 웹훅 서버 시작
python3 webhook_server.py
```

이제 Steampipe 쿼리 결과를 자동으로 Notion으로 export할 수 있는 완전한 시스템이 구축되었습니다!
