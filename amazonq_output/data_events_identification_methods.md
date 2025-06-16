# Data Events 식별 방법

## 1. CloudTrail 직접 분석

### CloudTrail Insights 활용
```bash
# CloudTrail 로그에서 데이터 이벤트 조회
aws logs filter-log-events \
  --log-group-name CloudTrail/DataEvents \
  --filter-pattern '{ $.eventCategory = "Data" }'
```

### 수동 로그 분석
- CloudTrail 로그를 직접 파싱하여 데이터 이벤트 추출
- S3, Lambda, DynamoDB 등의 데이터 액세스 패턴 분석

## 2. AWS Config를 통한 리소스 사용 추적

### Config Rules 설정
```json
{
  "ConfigRuleName": "s3-bucket-data-access-tracking",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "S3_BUCKET_LOGGING_ENABLED"
  }
}
```

## 3. 서비스별 네이티브 로깅

### Amazon S3
- **S3 Server Access Logs**: 객체 수준 액세스 로깅
- **S3 CloudTrail Data Events**: 상세한 API 호출 추적

```bash
# S3 버킷에 대한 데이터 이벤트 활성화
aws cloudtrail put-event-selectors \
  --trail-name my-trail \
  --event-selectors '[{
    "ReadWriteType": "All",
    "IncludeManagementEvents": false,
    "DataResources": [{
      "Type": "AWS::S3::Object",
      "Values": ["arn:aws:s3:::my-bucket/*"]
    }]
  }]'
```

### AWS Lambda
- **Lambda 실행 로그**: CloudWatch Logs를 통한 함수 실행 추적
- **X-Ray 트레이싱**: 상세한 실행 경로 분석

### Amazon DynamoDB
- **DynamoDB Streams**: 테이블 데이터 변경 추적
- **CloudTrail Data Events**: DynamoDB 테이블 액세스 로깅

## 4. 사용자 정의 분석 도구

### AWS CLI 스크립트 예시
```bash
#!/bin/bash
# S3 데이터 이벤트 분석 스크립트

# 특정 기간의 S3 데이터 이벤트 조회
aws logs filter-log-events \
  --log-group-name /aws/cloudtrail \
  --start-time $(date -d '7 days ago' +%s)000 \
  --filter-pattern '{ $.eventSource = "s3.amazonaws.com" && $.eventCategory = "Data" }' \
  --query 'events[*].[eventTime,sourceIPAddress,userIdentity.type,eventName,resources[0].resourceName]' \
  --output table
```

### Python 분석 스크립트
```python
import boto3
import json
from datetime import datetime, timedelta

def analyze_data_events():
    cloudtrail = boto3.client('cloudtrail')
    
    # 지난 7일간의 데이터 이벤트 조회
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    response = cloudtrail.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventCategory',
                'AttributeValue': 'Data'
            }
        ],
        StartTime=start_time,
        EndTime=end_time
    )
    
    # 사용된 데이터 액세스 권한 분석
    permissions = set()
    for event in response['Events']:
        event_detail = json.loads(event['CloudTrailEvent'])
        permissions.add(event_detail['eventName'])
    
    return list(permissions)
```

## 5. 서드파티 도구 활용

### Steampipe를 통한 분석
```sql
-- S3 데이터 이벤트 분석
select 
  event_time,
  event_name,
  source_ip_address,
  user_identity_type,
  resources
from aws_cloudtrail_event
where 
  event_category = 'Data'
  and event_source = 's3.amazonaws.com'
  and event_time >= now() - interval '7 days';
```

### CloudQuery 활용
```yaml
# cloudquery 설정으로 데이터 이벤트 수집
kind: source
spec:
  name: aws
  path: cloudquery/aws
  version: "v15.0.0"
  tables: 
    - aws_cloudtrail_events
  destinations:
    - postgresql
```

## 6. 실시간 모니터링 설정

### CloudWatch Events/EventBridge
```json
{
  "Rules": [{
    "Name": "S3DataEventRule",
    "EventPattern": {
      "source": ["aws.s3"],
      "detail-type": ["AWS API Call via CloudTrail"],
      "detail": {
        "eventCategory": ["Data"]
      }
    },
    "Targets": [{
      "Id": "1",
      "Arn": "arn:aws:lambda:region:account:function:ProcessDataEvent"
    }]
  }]
}
```

## 7. 권장 접근 방법

### 단계별 구현
1. **1단계**: CloudTrail 데이터 이벤트 활성화 (필요한 리소스만)
2. **2단계**: CloudWatch Logs Insights로 기본 분석
3. **3단계**: 사용자 정의 스크립트로 권한 매핑
4. **4단계**: 정기적인 분석 자동화

### 비용 최적화 팁
- 모든 리소스가 아닌 중요한 리소스만 데이터 이벤트 활성화
- 로그 보존 기간을 적절히 설정
- 분석 후 불필요한 데이터 이벤트 로깅 비활성화

## 결론

Data Events 식별을 위해서는 IAM Access Analyzer 대신 **CloudTrail 데이터 이벤트를 직접 분석**하거나, **서비스별 네이티브 로깅**을 활용해야 합니다. 각 방법의 비용과 복잡성을 고려하여 조직의 요구사항에 맞는 접근 방식을 선택하는 것이 중요합니다.
