# CloudTrail Data Events: 선택적 분석/알림 접근법

## 현실적 제약사항 인식
- CloudTrail Trail 생성 시 데이터 이벤트 로깅 여부가 결정됨
- 이미 활성화된 데이터 이벤트 로깅을 세밀하게 제어하기 어려움
- **해결책**: 로그는 그대로 두고, 분석과 알림을 선택적으로 처리

## 선택적 분석/알림 전략

### 1. EventBridge를 통한 실시간 선별적 알림

#### 보안 중요 이벤트만 실시간 처리
```json
{
  "Rules": [
    {
      "Name": "CriticalDataAccess",
      "EventPattern": {
        "source": ["aws.s3"],
        "detail-type": ["AWS API Call via CloudTrail"],
        "detail": {
          "eventCategory": ["Data"],
          "eventName": ["GetObject", "PutObject", "DeleteObject"],
          "resources": {
            "ARN": [
              {"prefix": "arn:aws:s3:::production-sensitive-"},
              {"prefix": "arn:aws:s3:::customer-pii-"},
              {"prefix": "arn:aws:s3:::financial-"}
            ]
          }
        }
      },
      "Targets": [
        {
          "Id": "SecurityTeamAlert",
          "Arn": "arn:aws:sns:region:account:security-alerts"
        }
      ]
    },
    {
      "Name": "AdminAccountDataActivity",
      "EventPattern": {
        "source": ["aws.s3"],
        "detail-type": ["AWS API Call via CloudTrail"],
        "detail": {
          "eventCategory": ["Data"],
          "userIdentity": {
            "sessionContext": {
              "sessionIssuer": {
                "arn": [{"prefix": "arn:aws:iam::*:role/Admin"}]
              }
            }
          }
        }
      },
      "Targets": [
        {
          "Id": "AdminActivityAlert",
          "Arn": "arn:aws:lambda:region:account:function:ProcessAdminActivity"
        }
      ]
    }
  ]
}
```

### 2. CloudWatch Logs Insights를 통한 선택적 분석

#### 보안 관점 핵심 쿼리들
```sql
-- 1. 외부 IP에서의 민감 데이터 접근
fields @timestamp, sourceIPAddress, userIdentity.type, eventName, resources.0.resourceName
| filter eventCategory = "Data"
| filter eventSource = "s3.amazonaws.com"
| filter not (sourceIPAddress like /^10\./ or sourceIPAddress like /^172\./ or sourceIPAddress like /^192\.168\./)
| filter resources.0.resourceName like /production-sensitive|customer-pii|financial/
| sort @timestamp desc
| limit 100

-- 2. 비정상적인 시간대 데이터 접근 (심야 시간)
fields @timestamp, sourceIPAddress, userIdentity.type, eventName, resources.0.resourceName
| filter eventCategory = "Data"
| filter datefloor(@timestamp, 1h) like /T0[0-6]:|T2[2-3]:/  # 새벽 0-6시, 밤 22-23시
| filter eventName in ["GetObject", "PutObject", "DeleteObject"]
| stats count() by userIdentity.type, sourceIPAddress
| sort count desc

-- 3. 대량 데이터 접근 패턴
fields @timestamp, sourceIPAddress, userIdentity.type, eventName
| filter eventCategory = "Data"
| filter eventName = "GetObject"
| stats count() as access_count by sourceIPAddress, userIdentity.type, bin(5m)
| filter access_count > 100  # 5분간 100회 이상 접근
| sort @timestamp desc
```

### 3. 계층화된 대시보드 구성

#### Tier 1: 실시간 보안 모니터링 대시보드
```json
{
  "widgets": [
    {
      "type": "log",
      "properties": {
        "query": "SOURCE '/aws/cloudtrail' | fields @timestamp, sourceIPAddress, eventName, resources.0.resourceName\n| filter eventCategory = \"Data\"\n| filter eventName in [\"GetObject\", \"PutObject\", \"DeleteObject\"]\n| filter resources.0.resourceName like /production-sensitive|customer-pii/\n| sort @timestamp desc\n| limit 50",
        "region": "us-east-1",
        "title": "Critical Data Access (Real-time)",
        "view": "table"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/CloudTrail", "DataEventCount", "EventName", "GetObject", {"stat": "Sum"}],
          [".", ".", ".", "PutObject", {"stat": "Sum"}],
          [".", ".", ".", "DeleteObject", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Data Events Volume (Last 24h)"
      }
    }
  ]
}
```

#### Tier 2: 보안 분석 대시보드
```json
{
  "widgets": [
    {
      "type": "log",
      "properties": {
        "query": "SOURCE '/aws/cloudtrail' | fields @timestamp, sourceIPAddress, userIdentity.type, eventName\n| filter eventCategory = \"Data\"\n| stats count() as event_count by sourceIPAddress, userIdentity.type\n| sort event_count desc\n| limit 20",
        "region": "us-east-1",
        "title": "Top Data Event Sources",
        "view": "table"
      }
    }
  ]
}
```

### 4. Steampipe를 통한 선택적 보안 분석

#### 보안팀 전용 분석 쿼리
```sql
-- 고위험 데이터 접근 패턴 분석
with high_risk_access as (
  select 
    event_time,
    source_ip_address,
    user_identity_type,
    event_name,
    resources ->> 0 as resource_name
  from aws_cloudtrail_event
  where 
    event_category = 'Data'
    and event_time >= now() - interval '24 hours'
    and (
      resources ->> 0 like '%production-sensitive%'
      or resources ->> 0 like '%customer-pii%'
      or resources ->> 0 like '%financial%'
    )
),
ip_analysis as (
  select 
    source_ip_address,
    count(*) as access_count,
    count(distinct resource_name) as unique_resources,
    array_agg(distinct event_name) as event_types
  from high_risk_access
  group by source_ip_address
)
select 
  source_ip_address,
  access_count,
  unique_resources,
  event_types,
  case 
    when access_count > 1000 then 'HIGH'
    when access_count > 100 then 'MEDIUM'
    else 'LOW'
  end as risk_level
from ip_analysis
order by access_count desc;
```

### 5. 자동화된 보안 분석 파이프라인

#### Lambda 기반 주기적 분석
```python
import boto3
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """주기적 보안 분석 (매시간 실행)"""
    
    logs_client = boto3.client('logs')
    sns_client = boto3.client('sns')
    
    # 지난 1시간 동안의 고위험 데이터 접근 분석
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    query = """
    fields @timestamp, sourceIPAddress, userIdentity.type, eventName, resources.0.resourceName
    | filter eventCategory = "Data"
    | filter eventName in ["GetObject", "PutObject", "DeleteObject"]
    | filter resources.0.resourceName like /production-sensitive|customer-pii|financial/
    | stats count() as access_count by sourceIPAddress, userIdentity.type
    | sort access_count desc
    """
    
    response = logs_client.start_query(
        logGroupName='/aws/cloudtrail',
        startTime=int(start_time.timestamp()),
        endTime=int(end_time.timestamp()),
        queryString=query
    )
    
    # 결과 분석 및 알림 처리
    query_id = response['queryId']
    
    # 쿼리 완료 대기 후 결과 처리
    results = wait_for_query_completion(logs_client, query_id)
    
    # 이상 패턴 감지 시 알림
    for result in results:
        if int(result[2]['value']) > 50:  # 1시간에 50회 이상 접근
            send_security_alert(sns_client, result)
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Analyzed {len(results)} access patterns')
    }

def send_security_alert(sns_client, result):
    """보안 알림 발송"""
    message = f"""
    🚨 High-Risk Data Access Detected
    
    IP Address: {result[0]['value']}
    User Type: {result[1]['value']}
    Access Count: {result[2]['value']} (last hour)
    
    Please investigate immediately.
    """
    
    sns_client.publish(
        TopicArn='arn:aws:sns:region:account:security-alerts',
        Message=message,
        Subject='Security Alert: High-Risk Data Access'
    )
```

### 6. 비용 효율적인 분석 스케줄링

#### 분석 우선순위 기반 스케줄링
```yaml
# CloudWatch Events 스케줄
AnalysisSchedule:
  CriticalAnalysis:
    Schedule: "rate(5 minutes)"  # 5분마다
    Query: "고위험 리소스 실시간 모니터링"
    
  SecurityAnalysis:
    Schedule: "rate(1 hour)"     # 1시간마다
    Query: "이상 패턴 탐지 및 분석"
    
  ComplianceAnalysis:
    Schedule: "rate(1 day)"      # 1일마다
    Query: "규정 준수 리포트 생성"
    
  TrendAnalysis:
    Schedule: "rate(7 days)"     # 1주마다
    Query: "장기 트렌드 분석"
```

## 구현 우선순위

### Phase 1: 즉시 구현 (1주)
1. **EventBridge 규칙 설정**: 고위험 이벤트 실시간 알림
2. **CloudWatch 대시보드**: 핵심 보안 메트릭 시각화
3. **기본 Logs Insights 쿼리**: 자주 사용하는 보안 분석 쿼리

### Phase 2: 단기 구현 (1개월)
1. **자동화된 분석 파이프라인**: Lambda 기반 주기적 분석
2. **Steampipe 통합**: 고급 보안 분석 쿼리
3. **알림 최적화**: 노이즈 제거 및 우선순위 기반 알림

### Phase 3: 중장기 구현 (3개월)
1. **ML 기반 이상 탐지**: Amazon Lookout 연동
2. **통합 보안 대시보드**: 모든 분석 결과 통합
3. **자동 대응 시스템**: 특정 패턴 감지 시 자동 조치

## 예상 효과

| 접근 방식 | 구현 복잡도 | 비용 효율성 | 보안 효과 | 유지보수성 |
|-----------|-------------|-------------|-----------|------------|
| 선택적 로깅 | 높음 | 높음 | 중간 | 낮음 |
| **선택적 분석** | **중간** | **높음** | **높음** | **높음** |

## 핵심 장점

1. **현실적 접근**: CloudTrail 구조적 제약 인정
2. **유연성**: 분석 기준을 언제든 조정 가능
3. **비용 효율성**: 필요한 분석만 수행
4. **확장성**: 새로운 보안 요구사항 쉽게 추가
5. **유지보수성**: 로그 구조 변경 없이 분석 로직만 수정

이 접근 방식이 CloudTrail의 특성을 고려한 가장 현실적이고 효과적인 해결책입니다.
