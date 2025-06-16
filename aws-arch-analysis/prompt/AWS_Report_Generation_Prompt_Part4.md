# AWS 계정 종합 분석 보고서 생성 프롬프트 - Part 4: Phase 7-9

## 📊 Phase 7: 모니터링 분석 템플릿 (monitoring.html)

### 데이터 수집 쿼리
```sql
-- CloudWatch 알람 정보
SELECT name, state_value, state_reason, 
       alarm_description, metric_name, namespace,
       comparison_operator, threshold
FROM aws_cloudwatch_alarm;

-- CloudTrail 설정
SELECT name, s3_bucket_name, include_global_service_events,
       is_multi_region_trail, kms_key_id, status
FROM aws_cloudtrail_trail;

-- VPC Flow Logs 상태
SELECT flow_log_id, resource_type, resource_id,
       traffic_type, log_destination_type, flow_log_status
FROM aws_vpc_flow_log;

-- GuardDuty 탐지기 상태
SELECT detector_id, status, service_role,
       finding_publishing_frequency, created_at
FROM aws_guardduty_detector;
```

### HTML 구조 및 콘텐츠

#### 1. 모니터링 현황 개요
```html
<section>
    <h2>⚠️ 현재 모니터링 상태</h2>
    <div class="monitoring-status">
        <h3>🔍 모니터링 현황 요약</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div><strong>CloudWatch 에이전트:</strong> [AGENT_STATUS]</div>
            <div><strong>Container Insights:</strong> [INSIGHTS_STATUS]</div>
            <div><strong>알람 설정:</strong> [ALARM_COUNT]개</div>
            <div><strong>전체 가시성:</strong> [VISIBILITY_PERCENTAGE]%</div>
        </div>
        
        <h4>주요 모니터링 갭</h4>
        <ul>
            <li>🔴 <strong>심각한 문제:</strong> 애플리케이션 레벨 모니터링 부재</li>
            <li>🟡 <strong>중간 문제:</strong> 인프라 메트릭 수집 부족</li>
            <li>🟢 <strong>부분적 해결:</strong> EKS 컨트롤 플레인 로깅 활성화</li>
        </ul>
    </div>
</section>
```

#### 2. 모니터링 서비스별 현황
```html
<div class="monitoring-grid">
    <div class="monitoring-card inactive">
        <h4>❌ CloudWatch Agent</h4>
        <p><strong>상태:</strong> 미설치</p>
        <p><strong>영향:</strong> 상세 메트릭 부족</p>
        <ul>
            <li>메모리 사용률 모니터링 불가</li>
            <li>디스크 사용률 모니터링 불가</li>
            <li>커스텀 메트릭 수집 불가</li>
        </ul>
        <p><strong>권장:</strong> 모든 EC2에 설치</p>
    </div>
    
    <div class="monitoring-card partial">
        <h4>⚠️ CloudWatch Logs</h4>
        <p><strong>상태:</strong> 부분적 활성화</p>
        <p><strong>영향:</strong> 로그 분석 제한</p>
        <ul>
            <li>EKS 컨트롤 플레인 로그 수집</li>
            <li>애플리케이션 로그 수집 부족</li>
            <li>중앙화된 로깅 부족</li>
        </ul>
        <p><strong>권장:</strong> 전체 로그 중앙화</p>
    </div>
</div>
```

#### 3. 권장 모니터링 구성
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>모니터링 도구</th>
            <th>현재 상태</th>
            <th>권장 구성</th>
            <th>예상 비용</th>
            <th>구현 우선순위</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>CloudWatch Agent</strong></td>
            <td>❌ 미설치</td>
            <td>모든 EC2 인스턴스</td>
            <td>$15/월</td>
            <td>🔴 High</td>
        </tr>
        <tr>
            <td><strong>Container Insights</strong></td>
            <td>❌ 비활성화</td>
            <td>EKS 클러스터</td>
            <td>$25/월</td>
            <td>🔴 High</td>
        </tr>
    </tbody>
</table>
```

---

## 🎯 Phase 8: 권장사항 템플릿 (recommendations.html)

### HTML 구조 및 콘텐츠

#### 1. 권장사항 요약
```html
<section>
    <h2>📊 권장사항 요약</h2>
    <div class="impact-metrics">
        <div class="impact-card">
            <div class="impact-value" style="color: #dc3545;">[HIGH_PRIORITY_COUNT]</div>
            <div>High Priority 항목</div>
        </div>
        <div class="impact-card">
            <div class="impact-value" style="color: #ffc107;">[MEDIUM_PRIORITY_COUNT]</div>
            <div>Medium Priority 항목</div>
        </div>
        <div class="impact-card">
            <div class="impact-value" style="color: #28a745;">$[MONTHLY_SAVINGS]</div>
            <div>월간 절약 가능</div>
        </div>
    </div>
</section>
```

#### 2. High Priority 섹션
```html
<section>
    <h2>🔴 High Priority (즉시 실행 - 1주 내)</h2>
    <div class="priority-section high">
        <h3>1. 보안 강화 (Critical)</h3>
        <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 8px;">
            <h4>🔒 암호화 및 보안 설정</h4>
            <ul>
                <li>✅ <strong>EBS 볼륨 전체 암호화</strong> - [UNENCRYPTED_COUNT]개 미암호화 볼륨</li>
                <li>✅ <strong>보안 그룹 규칙 검토</strong> - 과도한 권한 제한</li>
                <li>✅ <strong>IMDSv2 강제 적용</strong> - 메타데이터 보안 강화</li>
            </ul>
            <p><strong>예상 효과:</strong> 보안 위험 95% 제거</p>
        </div>
        
        <h3>2. 즉시 비용 절감</h3>
        <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 8px;">
            <h4>💰 Reserved Instance 구매</h4>
            <ul>
                <li>💰 <strong>Reserved Instance 구매</strong> - 월 $[RI_SAVINGS] 절약</li>
                <li>💰 <strong>미사용 리소스 정리</strong> - 월 $[CLEANUP_SAVINGS] 절약</li>
            </ul>
            <p><strong>예상 효과:</strong> 월 $[TOTAL_SAVINGS] 절약</p>
        </div>
    </div>
</section>
```

---

## 🔧 Phase 9: 구현 가이드 템플릿 (implementation.html)

### HTML 구조 및 콘텐츠

#### 1. 구현 가이드 헤더
```html
<header>
    <h1>🔧 Phase 9: 단계별 구현 가이드</h1>
    <p>권장사항을 실제로 구현하기 위한 구체적인 스크립트, 명령어, 체크리스트를 제공합니다.</p>
</header>
```

#### 2. Week 1-2 구현 섹션
```html
<section>
    <h2>📋 Week 1-2: 보안 및 즉시 비용 절감</h2>
    <div class="implementation-section">
        <h3>🔒 EBS 암호화 활성화</h3>
        <div class="code-block">
# EBS 암호화 기본 활성화
aws ec2 enable-ebs-encryption-by-default --region ap-northeast-2

# 기존 볼륨 암호화 (예시)
aws ec2 create-snapshot --volume-id vol-1234567890abcdef0 --description "Pre-encryption snapshot"
        </div>
        
        <h3>💰 Reserved Instance 구매</h3>
        <div class="code-block">
# RI 오퍼링 검색
aws ec2 describe-reserved-instances-offerings \
  --instance-type t3.small \
  --product-description "Linux/UNIX" \
  --region ap-northeast-2

# RI 구매 (예시)
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id 12345678-1234-1234-1234-123456789012 \
  --instance-count 12
        </div>
    </div>
</section>
```

#### 3. ROI 계산
```html
<section>
    <h2>📊 ROI 계산</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
        <div style="text-align: center; background: white; padding: 20px; border-radius: 10px;">
            <div style="font-size: 2.5em; font-weight: bold; color: #28a745;">$8,088</div>
            <div>연간 절약</div>
        </div>
        <div style="text-align: center; background: white; padding: 20px; border-radius: 10px;">
            <div style="font-size: 2.5em; font-weight: bold; color: #3498db;">즉시</div>
            <div>투자 회수 기간</div>
        </div>
    </div>
</section>
```

### 자동화 스크립트 템플릿
```bash
#!/bin/bash
# AWS 최적화 자동 배포 스크립트

set -e

echo "🚀 AWS 최적화 배포 시작..."

# 1. EBS 기본 암호화 활성화
echo "🔒 EBS 기본 암호화 활성화 중..."
aws ec2 enable-ebs-encryption-by-default --region ap-northeast-2

# 2. CloudWatch Agent 설치 (모든 인스턴스)
echo "📊 CloudWatch Agent 배포 중..."
INSTANCE_IDS=$(aws ec2 describe-instances \
  --region ap-northeast-2 \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].InstanceId' \
  --output text)

for INSTANCE_ID in $INSTANCE_IDS; do
  echo "Installing CloudWatch Agent on $INSTANCE_ID"
  aws ssm send-command \
    --region ap-northeast-2 \
    --document-name "AWS-ConfigureAWSPackage" \
    --parameters action=Install,name=AmazonCloudWatchAgent \
    --targets "Key=instanceids,Values=$INSTANCE_ID"
done

echo "✅ 배포 완료!"
```

이것은 Part 4로, Phase 7-9에 대한 상세한 프롬프트를 제공합니다.
