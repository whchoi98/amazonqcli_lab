# AWS 계정 종합 분석 보고서 생성 프롬프트 - Part 2: Phase 1-3

## 🌐 Phase 1: 네트워킹 분석 (networking.html)

### 데이터 소스
- **Steampipe 쿼리**: `aws_vpc`, `aws_subnet`, `aws_ec2_transit_gateway`, `aws_vpc_security_group`
- **AWS CLI**: `aws ec2 describe-vpcs`, `aws ec2 describe-subnets`

### HTML 구조 및 콘텐츠

#### 1. 페이지 헤더
```html
<header>
    <h1>🌐 Phase 1: 네트워킹 리소스 완전 분석</h1>
    <p>VPC, 서브넷, Transit Gateway, 보안 그룹 등 네트워킹 인프라의 전체적인 구조와 설정을 분석합니다.</p>
</header>
```

#### 2. VPC 아키텍처 현황 테이블
```html
<section>
    <h2>📊 VPC 아키텍처 현황</h2>
    <table class="analysis-table">
        <thead>
            <tr>
                <th>VPC 이름</th>
                <th>VPC ID</th>
                <th>CIDR Block</th>
                <th>타입</th>
                <th>프로젝트</th>
                <th>상태</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Default VPC</strong> <span class="status-default">기본</span></td>
                <td><span class="vpc-id">vpc-04d5341141a8cd55f</span></td>
                <td><span class="cidr-block">172.31.0.0/16</span></td>
                <td>기본 VPC</td>
                <td>-</td>
                <td><span class="status-available">Available</span></td>
            </tr>
            <!-- 5개 VPC 데이터 -->
        </tbody>
    </table>
</section>
```

#### 3. 아키텍처 다이어그램
```html
<div class="architecture-diagram">
    <h3>📐 아키텍처 다이어그램</h3>
    <p>🌐 Internet Gateway ↔ 🛡️ DMZVPC (10.11.0.0/16) ↔ 🔗 Transit Gateway</p>
    <p>↕️</p>
    <p>🏢 mgmtvpc (10.254.0.0/16) ↔ 💼 VPC01 (10.1.0.0/16) ↔ 💼 VPC02 (10.2.0.0/16)</p>
</div>
```

#### 4. Transit Gateway 상세 정보
```html
<div class="tgw-info">
    <h3>Transit Gateway 상세 정보</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
        <div><strong>TGW ID:</strong> tgw-02b9f9ddcb9aa49e0</div>
        <div><strong>상태:</strong> <span class="status-available">Available</span></div>
        <div><strong>ASN:</strong> 65001 (사용자 정의)</div>
    </div>
</div>
```

#### 5. 서브넷 분석 (35개)
```html
<div class="subnet-grid">
    <div class="subnet-card public">
        <h4>🌐 퍼블릭 서브넷</h4>
        <p><strong>개수:</strong> 12개</p>
        <p><strong>특징:</strong> Internet Gateway 연결</p>
    </div>
    <!-- 프라이빗, 전용 서브넷 카드들 -->
</div>
```

#### 6. 보안 그룹 위험 분석
```html
<div class="summary-grid">
    <div class="summary-card warning">
        <h3>🔴 보안 위험 발견</h3>
        <ul>
            <li>일부 그룹에서 0.0.0.0/0 오픈 규칙</li>
            <li>과도한 포트 범위 허용</li>
        </ul>
    </div>
</div>
```

### 스타일링 특징
- **테이블**: 호버 효과, 색상 코딩
- **카드 레이아웃**: 서브넷 타입별 색상 구분
- **아키텍처 다이어그램**: 시각적 표현

---

## 💻 Phase 2: 컴퓨팅 분석 (computing.html)

### 데이터 소스
- **Steampipe 쿼리**: `aws_ec2_instance`, `aws_eks_cluster`, `aws_eks_node_group`
- **AWS CLI**: `aws ec2 describe-instances`, `aws eks describe-cluster`

### HTML 구조 및 콘텐츠

#### 1. EC2 인스턴스 현황 메트릭
```html
<div class="workload-distribution">
    <div class="workload-card">
        <div class="workload-number">18</div>
        <div>총 인스턴스</div>
    </div>
    <div class="workload-card">
        <div class="workload-number">18</div>
        <div>실행 중</div>
    </div>
    <!-- 기타 메트릭들 -->
</div>
```

#### 2. 인스턴스 타입별 분포 테이블
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>인스턴스 타입</th>
            <th>개수</th>
            <th>vCPU</th>
            <th>메모리</th>
            <th>상태</th>
            <th>월간 예상 비용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>t3.small</strong></td>
            <td>12개</td>
            <td>2 vCPU</td>
            <td>2 GB</td>
            <td><span class="status-available">Running</span></td>
            <td>$183.96</td>
        </tr>
        <!-- 4개 인스턴스 타입 데이터 -->
    </tbody>
</table>
```

#### 3. VPC별 인스턴스 분포
```html
<div class="instance-grid">
    <div class="instance-card running">
        <h4>🌐 Default VPC</h4>
        <p><strong>인스턴스:</strong> 1개 (t3.medium)</p>
        <p><strong>용도:</strong> Cloud9 개발 환경</p>
        <p><strong>비용:</strong> $30.66/월</p>
    </div>
    <!-- 5개 VPC별 카드들 -->
</div>
```

#### 4. EKS 클러스터 상세 분석
```html
<div class="eks-cluster-info">
    <h3>eksworkshop 클러스터 상세 정보</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
        <div><strong>Kubernetes 버전:</strong> 1.31 (최신)</div>
        <div><strong>상태:</strong> <span class="status-available">ACTIVE</span></div>
        <div><strong>플랫폼 버전:</strong> eks.28</div>
    </div>
    
    <h4>보안 및 로깅 설정</h4>
    <ul>
        <li>✅ <strong>모든 컨트롤 플레인 로그 활성화</strong></li>
        <li>✅ <strong>Secrets 암호화 (KMS)</strong></li>
        <li>✅ <strong>OIDC 활성화</strong></li>
    </ul>
</div>
```

#### 5. 비용 최적화 기회 테이블
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>최적화 방법</th>
            <th>대상</th>
            <th>현재 비용</th>
            <th>절약 금액</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Reserved Instance</strong></td>
            <td>t3.small (12개)</td>
            <td>$183.96</td>
            <td>$73.59</td>
        </tr>
        <!-- 기타 최적화 방법들 -->
    </tbody>
</table>
```

### 스타일링 특징
- **메트릭 카드**: 큰 숫자 강조
- **인스턴스 카드**: VPC별 색상 구분
- **EKS 정보**: 오렌지 테마 강조

---

## 💾 Phase 3: 스토리지 분석 (storage.html)

### 데이터 소스
- **Steampipe 쿼리**: `aws_ebs_volume`, `aws_ebs_snapshot`
- **AWS CLI**: `aws ec2 describe-volumes`, `aws ec2 describe-snapshots`

### HTML 구조 및 콘텐츠

#### 1. 스토리지 메트릭 대시보드
```html
<div class="storage-metrics">
    <div class="metric-card">
        <div class="metric-value" style="color: #3498db;">18</div>
        <div>총 볼륨 수</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #28a745;">360GB</div>
        <div>총 용량</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #ffc107;">$36</div>
        <div>월간 비용</div>
    </div>
    <div class="metric-card">
        <div class="metric-value" style="color: #dc3545;">50%</div>
        <div>암호화 비율</div>
    </div>
</div>
```

#### 2. 볼륨 타입별 분포 테이블
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>볼륨 타입</th>
            <th>개수</th>
            <th>총 용량</th>
            <th>암호화</th>
            <th>IOPS</th>
            <th>월간 비용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>gp3</strong></td>
            <td>12개</td>
            <td>240 GB</td>
            <td>6개 암호화</td>
            <td>3,000 IOPS</td>
            <td>$24.00</td>
        </tr>
        <!-- gp2 볼륨 데이터 -->
    </tbody>
</table>
```

#### 3. 암호화 상태 분석
```html
<div class="encryption-status">
    <h3>⚠️ 암호화 상태 요약</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
        <div><strong>암호화된 볼륨:</strong> 9개 (50%)</div>
        <div><strong>미암호화 볼륨:</strong> 9개 (50%)</div>
        <div><strong>KMS 키 사용:</strong> 활성화</div>
    </div>
    
    <h4>보안 위험 평가</h4>
    <ul>
        <li>🔴 <strong>높은 위험:</strong> 50% 볼륨이 암호화되지 않음</li>
        <li>⚠️ <strong>컴플라이언스 위험:</strong> 데이터 보호 규정 미준수</li>
    </ul>
</div>
```

#### 4. 볼륨별 상세 분석 카드
```html
<div class="volume-grid">
    <div class="volume-card encrypted">
        <h4>✅ 암호화된 gp3 볼륨</h4>
        <p><strong>개수:</strong> 6개</p>
        <p><strong>용량:</strong> 120GB</p>
        <p><strong>상태:</strong> 보안 준수</p>
    </div>
    <div class="volume-card unencrypted">
        <h4>❌ 미암호화 gp3 볼륨</h4>
        <p><strong>개수:</strong> 6개</p>
        <p><strong>상태:</strong> 암호화 필요</p>
    </div>
    <!-- 기타 볼륨 카드들 -->
</div>
```

#### 5. 스토리지 최적화 기회
```html
<table class="analysis-table">
    <thead>
        <tr>
            <th>최적화 방법</th>
            <th>대상</th>
            <th>현재 비용</th>
            <th>절약 금액</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>gp2 → gp3 전환</strong></td>
            <td>6개 볼륨 (120GB)</td>
            <td>$12.00</td>
            <td>$2.40</td>
        </tr>
        <!-- 기타 최적화 방법들 -->
    </tbody>
</table>
```

### 스타일링 특징
- **메트릭 카드**: 색상별 의미 구분
- **볼륨 카드**: 암호화 상태별 색상 (녹색/빨간색)
- **경고 섹션**: 오렌지 테마로 주의 환기

이것은 Part 2입니다. 계속해서 Phase 4-6에 대한 프롬프트를 작성하겠습니다.
