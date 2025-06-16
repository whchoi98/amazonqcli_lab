# AWS 계정 종합 분석 보고서 생성 프롬프트 - Part 3: Phase 4-6

## 🗄️ Phase 4: 데이터베이스 분석 (database.html)

### 데이터 소스
- **Steampipe 쿼리**: `aws_rds_db_instance`, `aws_rds_db_cluster`, `aws_elasticache_cluster`
- **AWS CLI**: `aws rds describe-db-instances`, `aws elasticache describe-cache-clusters`
- **분석 결과**: 관리형 데이터베이스 서비스 미발견

### HTML 구조 및 콘텐츠

#### 1. 데이터베이스 현황 경고
```html
<div class="no-database-info">
    <h3>⚠️ 관리형 데이터베이스 서비스 현황</h3>
    <p>현재 서울 리전에서 활성화된 관리형 데이터베이스 서비스가 제한적으로 발견되었습니다.</p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
        <div><strong>RDS 인스턴스:</strong> 0개</div>
        <div><strong>Aurora 클러스터:</strong> 0개</div>
        <div><strong>ElastiCache:</strong> 0개</div>
        <div><strong>DynamoDB:</strong> 기본 테이블만 존재</div>
    </div>
</div>
```

#### 2. 데이터베이스 요구사항 분석 테이블
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>워크로드 유형</th>
            <th>현재 구성</th>
            <th>권장 데이터베이스</th>
            <th>예상 비용</th>
            <th>장점</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>웹 애플리케이션</strong></td>
            <td>EC2 기반</td>
            <td>RDS MySQL/PostgreSQL</td>
            <td>$50-150/월</td>
            <td>관리 부담 감소</td>
        </tr>
        <!-- 기타 워크로드 타입들 -->
    </tbody>
</table>
```

#### 3. 서비스별 권장사항 카드
```html
<div class="service-grid">
    <div class="service-card recommended">
        <h4>🚀 RDS/Aurora 검토</h4>
        <p><strong>우선순위:</strong> High</p>
        <ul>
            <li>관리형 관계형 데이터베이스</li>
            <li>자동 백업 및 복구</li>
            <li>Multi-AZ 고가용성</li>
        </ul>
        <p><strong>예상 비용:</strong> $80-200/월</p>
    </div>
    <!-- 기타 서비스 카드들 */
</div>
```

#### 4. 아키텍처 권장사항
```html
<div class="database-recommendation">
    <h3>📐 권장 아키텍처 패턴</h3>
    
    <h4>1. 기본 웹 애플리케이션</h4>
    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px;">
        <p><strong>구성:</strong> ALB → EKS → RDS MySQL (Multi-AZ) + ElastiCache Redis</p>
        <p><strong>예상 비용:</strong> $120-250/월</p>
    </div>
</div>
```

---

## 🔐 Phase 5: 보안 분석 (security.html)

### 데이터 소스
- **Steampipe 쿼리**: `aws_iam_role`, `aws_vpc_security_group`, `aws_ebs_volume`
- **AWS CLI**: `aws iam list-roles`, `aws ec2 describe-security-groups`

### HTML 구조 및 콘텐츠

#### 1. 보안 현황 개요
```html
<div class="security-overview">
    <h3>🔍 보안 상태 요약</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
        <div><strong>IAM 역할:</strong> 15개</div>
        <div><strong>보안 그룹:</strong> 8개</div>
        <div><strong>암호화 상태:</strong> 부분적</div>
        <div><strong>전체 위험도:</strong> 중간</div>
    </div>
    
    <h4>주요 보안 이슈</h4>
    <ul>
        <li>🔴 <strong>높은 위험:</strong> EBS 볼륨 50% 미암호화</li>
        <li>🟡 <strong>중간 위험:</strong> 일부 보안 그룹 과도한 권한</li>
    </ul>
</div>
```

#### 2. IAM 분석 테이블
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>역할 유형</th>
            <th>개수</th>
            <th>설명</th>
            <th>권한 수준</th>
            <th>위험도</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>EC2 Service Role</strong></td>
            <td>8개</td>
            <td>EC2 인스턴스용 역할</td>
            <td>제한적</td>
            <td><span style="color: #28a745;">낮음</span></td>
        </tr>
        <!-- 기타 역할 타입들 -->
    </tbody>
</table>
```

#### 3. 보안 그룹 위험 분석
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>보안 그룹</th>
            <th>VPC</th>
            <th>인바운드 규칙</th>
            <th>아웃바운드 규칙</th>
            <th>위험도</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>default (Default VPC)</td>
            <td>Default</td>
            <td>SSH (0.0.0.0/0)</td>
            <td>All Traffic</td>
            <td><span style="color: #dc3545;">높음</span></td>
        </tr>
        <!-- 기타 보안 그룹들 -->
    </tbody>
</table>
```

#### 4. 암호화 상태 분석
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>서비스</th>
            <th>암호화 상태</th>
            <th>KMS 키</th>
            <th>암호화 비율</th>
            <th>권장사항</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>EBS 볼륨</strong></td>
            <td>부분 암호화</td>
            <td>일부 적용</td>
            <td>50%</td>
            <td>전체 암호화 필요</td>
        </tr>
        <!-- 기타 서비스들 */
    </tbody>
</table>
```

#### 5. 컴플라이언스 상태
```html
<div class="compliance-status">
    <h3>🏛️ 보안 프레임워크 준수 현황</h3>
    
    <h4>AWS Well-Architected Security Pillar</h4>
    <div style="background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
            <div><strong>Identity & Access:</strong> 70% 준수</div>
            <div><strong>Data Protection:</strong> 50% 준수</div>
            <div><strong>Infrastructure Protection:</strong> 60% 준수</div>
        </div>
    </div>
</div>
```

---

## 💰 Phase 6: 비용 최적화 분석 (cost-optimization.html)

### 데이터 소스
- **AWS Cost Explorer API**: 비용 데이터
- **Steampipe 쿼리**: 리소스 사용률 분석
- **AWS Pricing API**: 가격 정보

### HTML 구조 및 콘텐츠

#### 1. 현재 비용 분석 개요
```html
<div class="cost-overview">
    <h3>💸 비용 구조 분석</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
        <div><strong>총 월간 비용:</strong> $1,400</div>
        <div><strong>컴퓨팅 비용:</strong> $1,168 (83%)</div>
        <div><strong>네트워킹 비용:</strong> $144 (10%)</div>
        <div><strong>스토리지 비용:</strong> $53 (4%)</div>
    </div>
</div>
```

#### 2. 서비스별 비용 분석 테이블
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>서비스 카테고리</th>
            <th>예상 비용</th>
            <th>비중</th>
            <th>주요 구성 요소</th>
            <th>최적화 기회</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>EC2 인스턴스</strong></td>
            <td>$1,055.58</td>
            <td>75%</td>
            <td>18개 인스턴스</td>
            <td>Reserved Instance</td>
        </tr>
        <!-- 기타 서비스들 -->
    </tbody>
</table>
```

#### 3. 즉시 적용 가능한 절약 방안
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>최적화 방법</th>
            <th>대상</th>
            <th>현재 비용</th>
            <th>절약 금액</th>
            <th>절약률</th>
            <th>구현 난이도</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Reserved Instance (1년)</strong></td>
            <td>t3.small (12개)</td>
            <td>$183.96</td>
            <td>$110.37</td>
            <td>60%</td>
            <td>쉬움</td>
        </tr>
        <!-- 기타 최적화 방법들 -->
    </tbody>
</table>
```

#### 4. 예상 절약 효과 메트릭
```html
<div class="savings-metrics">
    <div class="metric-card">
        <div class="metric-value" style="color: #28a745;">$524</div>
        <div>월간 절약</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #28a745;">46%</div>
        <div>절약률</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #28a745;">$6,291</div>
        <div>연간 절약</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #3498db;">$876</div>
        <div>최적화 후 월비용</div>
    </div>
</div>
```

#### 5. 상세 최적화 전략 카드
```html
<div class="optimization-grid">
    <div class="optimization-card high-impact">
        <h4>💎 Reserved Instance 전략</h4>
        <p><strong>절약 효과:</strong> $278.56/월</p>
        <ul>
            <li>1년 약정으로 30-60% 절약</li>
            <li>안정적인 워크로드에 적용</li>
            <li>즉시 구매 가능</li>
        </ul>
        <p><strong>구현 방법:</strong> AWS 콘솔에서 RI 구매</p>
    </div>
    <!-- 기타 최적화 전략들 */
</div>
```

#### 6. 단계별 구현 로드맵
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>단계</th>
            <th>기간</th>
            <th>최적화 항목</th>
            <th>절약 금액</th>
            <th>누적 절약</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>1단계</strong></td>
            <td>1주</td>
            <td>RI 구매, Elastic IP 해제</td>
            <td>$285.86</td>
            <td>$285.86</td>
        </tr>
        <!-- 기타 단계들 -->
    </tbody>
</table>
```

### 스타일링 특징
- **메트릭 카드**: 큰 숫자와 색상으로 임팩트 강조
- **최적화 카드**: 임팩트별 색상 구분 (high-impact는 녹색)
- **ROI 섹션**: 투자 대비 효과 시각화

이것은 Part 3입니다. 계속해서 Phase 7-9에 대한 프롬프트를 작성하겠습니다.
