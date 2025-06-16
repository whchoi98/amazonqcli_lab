# IAM Access Analyzer와 CloudTrail 데이터 이벤트 관계

## 핵심 질문에 대한 답변

**보안팀의 판단이 맞습니다.** IAM Access Analyzer의 정책 생성 기능에서는 CloudTrail 데이터 이벤트 로그가 불필요합니다.

## 왜 데이터 이벤트가 불필요한가?

### 1. Access Analyzer의 제한사항
- IAM Access Analyzer는 **관리 이벤트(Management Events)**만 분석합니다
- **데이터 이벤트(Data Events)**는 정책 생성 과정에서 식별하지 않습니다
- 문서에 명시된 내용: "IAM Access Analyzer는 생성된 정책에서 Amazon S3 데이터 이벤트와 같은 데이터 이벤트에 대한 작업 수준 활동을 식별하지 않습니다"

### 2. 관리 이벤트 vs 데이터 이벤트

#### 관리 이벤트 (Management Events)
- AWS 계정의 리소스에 대한 관리 작업
- 예시: S3 버킷 생성/삭제, IAM 정책 변경, EC2 인스턴스 시작/중지
- **Access Analyzer가 분석하는 이벤트**

#### 데이터 이벤트 (Data Events)
- 리소스 내부의 데이터에 대한 작업
- 예시: S3 객체 읽기/쓰기, Lambda 함수 실행
- **Access Analyzer가 분석하지 않는 이벤트**

## 실제 영향

### Access Analyzer가 식별할 수 있는 권한
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "*"
    }
  ]
}
```

### Access Analyzer가 식별할 수 없는 권한
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

## 권장사항

### 1. 비용 최적화
- 데이터 이벤트 로깅은 비용이 높습니다
- Access Analyzer 목적으로는 불필요한 비용입니다

### 2. 보안 관점
- 관리 이벤트만으로도 충분한 정책 생성 가능
- 데이터 이벤트는 별도의 보안 모니터링 목적으로 활용

### 3. 실무 적용
- Access Analyzer: 관리 이벤트만 활성화
- 보안 모니터링: 필요시 데이터 이벤트 별도 활성화
- 감사 목적: CloudTrail 직접 활용

## 결론

보안팀의 판단이 정확합니다. IAM Access Analyzer의 정책 생성 기능은 데이터 이벤트 수준의 권한을 식별하지 못하므로, 해당 로그를 활성화할 필요가 없습니다. 이는 비용 효율적이면서도 Access Analyzer의 본래 목적에 부합하는 설정입니다.
