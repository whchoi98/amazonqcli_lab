# Data Events 빠른 분석 방법

## 현재 상황 분석
- 초기에 데이터 이벤트 없이 분석 → 유의미한 데이터 부족
- 필요한 IAM 역할에만 데이터 이벤트 활성화
- **문제**: 로그 볼륨이 너무 커서 분석 속도 저하

## 빠른 분석을 위한 최적화 전략

### 1. 실시간 스트리밍 분석

#### Amazon Kinesis Data Firehose + Analytics
```json
{
  "DeliveryStreamName": "cloudtrail-data-events-stream",
  "ExtendedS3DestinationConfiguration": {
    "BucketARN": "arn:aws:s3:::my-analysis-bucket",
    "Prefix": "year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
    "ProcessingConfiguration": {
      "Enabled": true,
      "Processors": [{
        "Type": "Lambda",
        "Parameters": [{
          "ParameterName": "LambdaArn",
          "ParameterValue": "arn:aws:lambda:region:account:function:FilterDataEvents"
        }]
      }]
    }
  }
}
```

#### 실시간 필터링 Lambda 함수
```python
import json
import base64

def lambda_handler(event, context):
    output = []
    
    for record in event['records']:
        # Base64 디코딩
        payload = json.loads(base64.b64decode(record['data']))
        
        # 중요한 데이터 이벤트만 필터링
        if should_analyze_event(payload):
            # 필요한 필드만 추출하여 크기 축소
            filtered_event = {
                'eventTime': payload.get('eventTime'),
                'eventName': payload.get('eventName'),
                'userIdentity': payload.get('userIdentity', {}).get('type'),
                'sourceIPAddress': payload.get('sourceIPAddress'),
                'resources': [r.get('resourceName') for r in payload.get('resources', [])]
            }
            
            output.append({
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(
                    json.dumps(filtered_event).encode('utf-8')
                ).decode('utf-8')
            })
        else:
            # 불필요한 이벤트는 제외
            output.append({
                'recordId': record['recordId'],
                'result': 'ProcessingFailed'
            })
    
    return {'records': output}

def should_analyze_event(event):
    # 분석이 필요한 이벤트만 선별
    important_events = [
        'GetObject', 'PutObject', 'DeleteObject',
        'Invoke', 'GetItem', 'PutItem', 'DeleteItem'
    ]
    return event.get('eventName') in important_events
```

### 2. 파티셔닝 및 인덱싱 최적화

#### S3 파티셔닝 전략
```bash
# 효율적인 파티셔닝 구조
s3://my-cloudtrail-bucket/
├── AWSLogs/account-id/CloudTrail/region/
│   ├── year=2024/month=01/day=15/hour=14/
│   │   ├── service=s3/
│   │   ├── service=lambda/
│   │   └── service=dynamodb/
```

#### AWS Glue를 통한 자동 파티셔닝
```python
import boto3

def create_glue_crawler():
    glue = boto3.client('glue')
    
    glue.create_crawler(
        Name='cloudtrail-data-events-crawler',
        Role='arn:aws:iam::account:role/GlueServiceRole',
        DatabaseName='cloudtrail_db',
        Targets={
            'S3Targets': [{
                'Path': 's3://my-cloudtrail-bucket/AWSLogs/',
                'Exclusions': ['**/_SUCCESS', '**/_temporary/**']
            }]
        },
        Schedule='cron(0 1 * * ? *)',  # 매일 새벽 1시 실행
        SchemaChangePolicy={
            'UpdateBehavior': 'UPDATE_IN_DATABASE',
            'DeleteBehavior': 'LOG'
        }
    )
```

### 3. Amazon Athena 최적화 쿼리

#### 파티션 프루닝 활용
```sql
-- 효율적인 쿼리 (파티션 활용)
SELECT 
    eventtime,
    eventname,
    useridentity.type as user_type,
    sourceipaddress,
    resources[1].resourcename as resource
FROM cloudtrail_data_events
WHERE 
    year = '2024' 
    AND month = '01'
    AND day = '15'
    AND eventcategory = 'Data'
    AND eventsource = 's3.amazonaws.com'
    AND eventname IN ('GetObject', 'PutObject', 'DeleteObject')
LIMIT 1000;
```

#### 컬럼형 저장 포맷 활용
```sql
-- Parquet 형식으로 CTAS (Create Table As Select)
CREATE TABLE cloudtrail_optimized
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    partitioned_by = ARRAY['year', 'month', 'day', 'service']
) AS
SELECT 
    eventtime,
    eventname,
    useridentity,
    sourceipaddress,
    resources,
    year(from_iso8601_timestamp(eventtime)) as year,
    month(from_iso8601_timestamp(eventtime)) as month,
    day(from_iso8601_timestamp(eventtime)) as day,
    eventsource as service
FROM cloudtrail_raw_data
WHERE eventcategory = 'Data';
```

### 4. Steampipe 고성능 분석

#### 병렬 처리 설정
```hcl
# ~/.steampipe/config/aws.spc
connection "aws" {
  plugin = "aws"
  
  # 병렬 처리 최적화
  max_error_retry_attempts = 3
  min_error_retry_delay     = "1s"
  
  # 캐싱 활용
  cache     = true
  cache_ttl = 300
}
```

#### 최적화된 Steampipe 쿼리
```sql
-- 인덱스 활용한 빠른 조회
select 
  event_time,
  event_name,
  user_identity_type,
  source_ip_address,
  resources ->> 0 as primary_resource
from aws_cloudtrail_event
where 
  event_time >= now() - interval '1 day'
  and event_category = 'Data'
  and event_source = 's3.amazonaws.com'
  and event_name in ('GetObject', 'PutObject')
order by event_time desc
limit 100;
```

### 5. 실시간 대시보드 구축

#### CloudWatch Dashboard
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/CloudTrail", "DataEventCount", "EventName", "GetObject"],
          [".", ".", ".", "PutObject"],
          [".", ".", ".", "DeleteObject"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "S3 Data Events (Last 24h)"
      }
    }
  ]
}
```

#### Grafana + CloudWatch 연동
```yaml
# grafana-dashboard.yaml
apiVersion: 1
datasources:
  - name: CloudWatch
    type: cloudwatch
    access: proxy
    jsonData:
      defaultRegion: us-east-1
      authType: default
```

### 6. 비용 최적화된 분석 주기

#### 스마트 샘플링 전략
```python
def smart_sampling_strategy():
    """
    시간대별 다른 샘플링 비율 적용
    """
    current_hour = datetime.now().hour
    
    if 9 <= current_hour <= 17:  # 업무시간
        return 0.1  # 10% 샘플링
    elif 18 <= current_hour <= 22:  # 저녁시간
        return 0.05  # 5% 샘플링
    else:  # 심야시간
        return 0.01  # 1% 샘플링
```

#### 계층적 분석 접근법
```bash
#!/bin/bash
# 1단계: 요약 데이터 생성 (매시간)
aws athena start-query-execution \
  --query-string "
    CREATE TABLE hourly_summary AS
    SELECT 
      date_trunc('hour', from_iso8601_timestamp(eventtime)) as hour,
      eventname,
      count(*) as event_count,
      count(distinct sourceipaddress) as unique_ips
    FROM cloudtrail_data_events
    WHERE eventtime >= current_timestamp - interval '1' day
    GROUP BY 1, 2
  "

# 2단계: 이상 패턴 감지 후 상세 분석
python detect_anomalies.py --input hourly_summary --threshold 1000
```

## 권장 구현 순서

### Phase 1: 즉시 적용 가능 (1-2주)
1. **Athena 쿼리 최적화**: 파티션 프루닝 적용
2. **Steampipe 캐싱**: 반복 쿼리 성능 향상
3. **샘플링 전략**: 중요 이벤트만 선별 분석

### Phase 2: 중기 개선 (1-2개월)
1. **실시간 스트리밍**: Kinesis + Lambda 필터링
2. **컬럼형 저장**: Parquet 포맷 전환
3. **자동화된 파티셔닝**: Glue Crawler 설정

### Phase 3: 고도화 (3-6개월)
1. **ML 기반 이상 탐지**: Amazon Lookout 활용
2. **예측적 분석**: 패턴 기반 사전 필터링
3. **통합 대시보드**: 실시간 모니터링 환경

## 예상 성능 개선 효과

| 방법 | 분석 속도 개선 | 비용 절감 | 구현 복잡도 |
|------|---------------|-----------|-------------|
| 파티션 최적화 | 5-10배 | 30-50% | 낮음 |
| 실시간 필터링 | 10-20배 | 60-80% | 중간 |
| 컬럼형 저장 | 3-5배 | 20-30% | 중간 |
| 스마트 샘플링 | 20-50배 | 80-90% | 높음 |

이러한 접근 방식을 통해 대용량 데이터 이벤트 로그를 효율적으로 분석할 수 있습니다.
