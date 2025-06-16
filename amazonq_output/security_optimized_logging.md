# 보안 관점에서 CloudTrail Data Events 최적화 방안

## 현재 문제점
- 데이터 이벤트 로그 볼륨이 과도하게 많음
- 보안 분석에 필요한 핵심 이벤트가 노이즈에 묻힘
- 비용 증가와 분석 효율성 저하

## 보안 중심 최적화 전략

### 1. 위험 기반 선별적 로깅 (Risk-Based Selective Logging)

#### 고위험 리소스만 집중 모니터링
```json
{
  "EventSelectors": [
    {
      "ReadWriteType": "All",
      "IncludeManagementEvents": false,
      "DataResources": [
        {
          "Type": "AWS::S3::Object",
          "Values": [
            "arn:aws:s3:::production-sensitive-data/*",
            "arn:aws:s3:::customer-pii-bucket/*",
            "arn:aws:s3:::financial-records/*"
          ]
        },
        {
          "Type": "AWS::Lambda::Function",
          "Values": [
            "arn:aws:lambda:*:*:function:payment-processor",
            "arn:aws:lambda:*:*:function:user-authentication"
          ]
        }
      ]
    }
  ]
}
```

#### 보안 관련 중요 이벤트만 필터링
```python
# 보안 관점에서 중요한 이벤트 정의
SECURITY_CRITICAL_EVENTS = {
    's3.amazonaws.com': [
        'GetObject',      # 민감 데이터 접근
        'PutObject',      # 데이터 업로드
        'DeleteObject',   # 데이터 삭제
        'GetObjectAcl',   # 권한 조회
        'PutObjectAcl'    # 권한 변경
    ],
    'lambda.amazonaws.com': [
        'Invoke'          # 함수 실행
    ],
    'dynamodb.amazonaws.com': [
        'GetItem',        # 데이터 조회
        'PutItem',        # 데이터 삽입
        'DeleteItem',     # 데이터 삭제
        'Scan',           # 전체 스캔
        'Query'           # 쿼리 실행
    ]
}

def is_security_relevant_event(event):
    """보안 관련 중요 이벤트인지 판단"""
    event_source = event.get('eventSource')
    event_name = event.get('eventName')
    
    return event_name in SECURITY_CRITICAL_EVENTS.get(event_source, [])
```

### 2. 시간 기반 적응형 로깅 (Time-Based Adaptive Logging)

#### 업무시간 vs 비업무시간 차등 적용
```python
def get_logging_strategy():
    """시간대별 로깅 전략 결정"""
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # 업무시간 (월-금 9-18시): 상세 로깅
    if current_day < 5 and 9 <= current_hour <= 18:
        return {
            'sample_rate': 1.0,  # 100% 로깅
            'events': 'all_security_events'
        }
    
    # 저녁시간 (18-23시): 중요 이벤트만
    elif 18 <= current_hour <= 23:
        return {
            'sample_rate': 0.3,  # 30% 샘플링
            'events': 'high_risk_only'
        }
    
    # 심야/주말: 이상 행위 탐지 중심
    else:
        return {
            'sample_rate': 0.1,  # 10% 샘플링
            'events': 'anomaly_detection'
        }
```

### 3. 사용자/역할 기반 차등 모니터링

#### 권한 수준별 로깅 강도 조절
```json
{
  "HighPrivilegeRoles": [
    "arn:aws:iam::*:role/AdminRole",
    "arn:aws:iam::*:role/SecurityRole",
    "arn:aws:iam::*:role/DatabaseAdminRole"
  ],
  "LoggingPolicy": {
    "HighPrivilege": {
      "DataEvents": "ALL",
      "SampleRate": 1.0,
      "RealTimeAlert": true
    },
    "StandardUser": {
      "DataEvents": "CRITICAL_ONLY",
      "SampleRate": 0.2,
      "RealTimeAlert": false
    },
    "ServiceAccount": {
      "DataEvents": "ANOMALY_BASED",
      "SampleRate": 0.05,
      "RealTimeAlert": false
    }
  }
}
```

### 4. 실시간 보안 이벤트 필터링

#### EventBridge를 통한 즉시 대응
```json
{
  "Rules": [
    {
      "Name": "HighRiskDataAccess",
      "EventPattern": {
        "source": ["aws.s3"],
        "detail-type": ["AWS API Call via CloudTrail"],
        "detail": {
          "eventCategory": ["Data"],
          "eventName": ["GetObject", "PutObject"],
          "resources": {
            "ARN": [
              {"prefix": "arn:aws:s3:::production-sensitive-data/"}
            ]
          },
          "sourceIPAddress": [
            {"anything-but": {"prefix": "10.0."}}  # 내부 IP가 아닌 경우
          ]
        }
      },
      "Targets": [
        {
          "Id": "SecurityAlert",
          "Arn": "arn:aws:lambda:region:account:function:SecurityIncidentHandler"
        }
      ]
    }
  ]
}
```

### 5. 지능형 이상 탐지 기반 로깅

#### Amazon GuardDuty와 연계
```python
def intelligent_logging_decision(event):
    """GuardDuty 위협 인텔리전스 기반 로깅 결정"""
    
    # GuardDuty 위협 IP 목록 확인
    if is_threat_ip(event.get('sourceIPAddress')):
        return {'log': True, 'priority': 'HIGH', 'alert': True}
    
    # 비정상적인 접근 패턴 감지
    if detect_anomalous_pattern(event):
        return {'log': True, 'priority': 'MEDIUM', 'alert': False}
    
    # 정상 패턴
    return {'log': False, 'priority': 'LOW', 'alert': False}

def detect_anomalous_pattern(event):
    """이상 패턴 감지 로직"""
    user_identity = event.get('userIdentity', {})
    
    # 새로운 지역에서의 접근
    if is_new_geographic_location(event):
        return True
    
    # 비정상적인 시간대 접근
    if is_unusual_time_access(event):
        return True
    
    # 대량 데이터 접근
    if is_bulk_data_access(event):
        return True
    
    return False
```

### 6. 계층화된 보안 로깅 아키텍처

#### 3단계 로깅 전략
```yaml
# Tier 1: 실시간 보안 모니터링 (최소한의 로그)
RealTimeMonitoring:
  Events:
    - 관리자 계정 활동
    - 외부 IP에서의 민감 데이터 접근
    - 권한 변경 관련 활동
  Storage: "CloudWatch Logs (7일 보존)"
  Cost: "최소"

# Tier 2: 보안 분석용 로그 (선별적 로그)
SecurityAnalysis:
  Events:
    - 중요 리소스 데이터 이벤트
    - 이상 패턴 감지된 활동
    - 규정 준수 관련 이벤트
  Storage: "S3 Standard (90일 보존)"
  Cost: "중간"

# Tier 3: 장기 보관용 로그 (압축된 로그)
LongTermRetention:
  Events:
    - 요약된 보안 메트릭
    - 월별 집계 데이터
    - 규정 준수 증빙 자료
  Storage: "S3 Glacier (7년 보존)"
  Cost: "최소"
```

### 7. 보안 메트릭 기반 최적화

#### 핵심 보안 지표 모니터링
```sql
-- Steampipe를 통한 보안 메트릭 분석
WITH security_metrics AS (
  SELECT 
    date_trunc('hour', event_time) as hour,
    user_identity_type,
    source_ip_address,
    event_name,
    COUNT(*) as event_count,
    COUNT(DISTINCT source_ip_address) as unique_ips
  FROM aws_cloudtrail_event
  WHERE 
    event_category = 'Data'
    AND event_time >= now() - interval '24 hours'
  GROUP BY 1, 2, 3, 4
)
SELECT 
  hour,
  SUM(CASE WHEN event_count > 100 THEN 1 ELSE 0 END) as high_volume_events,
  SUM(CASE WHEN unique_ips > 10 THEN 1 ELSE 0 END) as suspicious_ip_patterns,
  COUNT(DISTINCT user_identity_type) as user_types
FROM security_metrics
GROUP BY hour
ORDER BY hour DESC;
```

### 8. 자동화된 로그 수명주기 관리

#### 보안 중요도 기반 자동 분류
```python
def classify_log_retention(event):
    """보안 중요도에 따른 로그 보존 정책 결정"""
    
    security_score = calculate_security_score(event)
    
    if security_score >= 8:  # 고위험
        return {
            'retention': '7_years',
            'storage_class': 'STANDARD',
            'encryption': 'KMS',
            'access_logging': True
        }
    elif security_score >= 5:  # 중위험
        return {
            'retention': '1_year',
            'storage_class': 'STANDARD_IA',
            'encryption': 'SSE-S3',
            'access_logging': False
        }
    else:  # 저위험
        return {
            'retention': '90_days',
            'storage_class': 'GLACIER',
            'encryption': 'SSE-S3',
            'access_logging': False
        }
```

## 구현 우선순위 (보안 관점)

### Phase 1: 즉시 구현 (1주)
1. **고위험 리소스 식별 및 선별적 로깅**
2. **실시간 보안 알림 설정**
3. **관리자 계정 활동 100% 로깅**

### Phase 2: 단기 구현 (1개월)
1. **시간 기반 적응형 로깅**
2. **이상 패턴 탐지 로직**
3. **자동화된 로그 분류**

### Phase 3: 중장기 구현 (3개월)
1. **ML 기반 위협 탐지**
2. **통합 보안 대시보드**
3. **규정 준수 자동화**

## 예상 효과

| 최적화 방법 | 로그 볼륨 감소 | 보안 효과 | 비용 절감 |
|-------------|----------------|-----------|-----------|
| 선별적 로깅 | 60-80% | 높음 | 70% |
| 시간 기반 로깅 | 40-60% | 중간 | 50% |
| 이상 탐지 기반 | 70-90% | 매우 높음 | 80% |
| 계층화 아키텍처 | 50-70% | 높음 | 60% |

## 보안 거버넌스 고려사항

### 규정 준수 요구사항
- **PCI DSS**: 카드 데이터 접근 로그 필수
- **GDPR**: 개인정보 처리 로그 보관
- **SOX**: 재무 데이터 접근 감사 추적

### 로그 무결성 보장
- **CloudTrail Log File Validation** 활성화
- **S3 Object Lock**으로 변조 방지
- **KMS 암호화**로 기밀성 보장

이러한 보안 중심 최적화를 통해 로그 볼륨을 크게 줄이면서도 보안 효과는 오히려 향상시킬 수 있습니다.
