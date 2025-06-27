# AWS 계정 종합 분석 - 단계별 권장 프롬프트

## 📋 개요

이 문서는 AWS 계정에 대한 종합적인 분석을 수행하기 위한 단계별 권장 프롬프트를 제공합니다. 각 프롬프트는 01-05번 가이드 파일과 연계하여 체계적인 분석을 진행할 수 있도록 구성되었습니다.

---

## 🎯 Phase 1: 역할 정의 및 환경 설정

**참조 파일**: `01-role-and-environment.md`

### 권장 프롬프트

```
AWS 클라우드 아키텍트로서 현재 계정에서 ap-northeast-2 리전에 대한 종합적인 분석.

먼저 분석 환경을 설정하고 역할을 정의해주세요:

1. **계정 정보 확인**: 현재 AWS 계정 정보를 확인하고 분석 범위를 설정
2. **도구 검증**: 필요한 도구들(Steampipe, AWS CLI, Python 패키지)의 설치 상태 확인  
3. **디렉토리 준비**: 분석 결과를 저장할 디렉토리 구조를 준비
4. **분석 계획**: 8개 주요 영역(네트워킹, 컴퓨팅, 스토리지, 데이터베이스, 보안, 애플리케이션, 모니터링, 비용)에 대한 분석 계획을 수립

환경 검증 스크립트를 실행하여 분석 준비 상태를 확인:
```bash
cd ~/amazonqcli_lab/aws-arch-analysis/script
./check-environment.sh
```
```

### 예상 결과
- ✅ AWS CLI 설치 확인
- ✅ Steampipe 설치 및 AWS 플러그인 확인
- ✅ Python 패키지 설치 상태 확인
- ✅ 분석 디렉토리 구조 생성

---

## 📊 Phase 2: 데이터 수집 전략

**참조 파일**: `02-data-collection-guide.md`

### 권장 프롬프트

```
AWS 계정의 모든 리소스에 대한 체계적인 데이터 수집을 시작.

8개 영역에 대해 Steampipe 기반 데이터 수집을 실행:

1. **네트워킹**: VPC, 서브넷, 보안 그룹, 라우팅 테이블, NAT Gateway 등
2. **컴퓨팅**: EC2 인스턴스, Auto Scaling, Load Balancer, Lambda 함수 등  
3. **스토리지**: EBS 볼륨, S3 버킷, EFS, 백업 정책 등
4. **데이터베이스**: RDS, Aurora, DynamoDB, ElastiCache 등
5. **보안**: IAM 역할/정책, KMS 키, 보안 그룹 규칙 등
6. **애플리케이션**: API Gateway, SNS, SQS, EventBridge 등
7. **모니터링**: CloudWatch 로그/알람, X-Ray 등
8. **비용**: 리소스 사용량 및 비용 최적화 기회


각 영역별 데이터 수집을 순차적으로 실행.
```

---

## 🔧 Phase 3: 실행 방법론

**참조 파일**: `03-execution-methods.md`

### 프롬프트

```
수집된 데이터를 바탕으로 전문적인 분석 보고서를 생성.

다음 순서로 실행:

1. **전체 분석 프로세스 실행**:
   ```bash
   cd ~/amazonqcli_lab/aws-arch-analysis/script
   ./run-complete-analysis.sh
   ```

2. **개별 보고서 생성** (필요시):
   - Executive Summary: `./generate-executive-summary.sh`
   - 네트워킹 분석: `./generate-networking-report.sh`  
   - 컴퓨팅 분석: `./generate-compute-report.sh`
   - 데이터베이스 분석: `./generate-database-report.sh`
   - 스토리지 분석: `./generate-storage-report.sh`
   - 보안 분석: `./generate-security-report.sh`
   - 애플리케이션 분석: `./generate-application-report.sh`
   - 모니터링 분석: `./generate-monitoring-report.sh`
   - 비용 최적화: `./generate-cost-report.sh`
   - 종합 권장사항: `./generate-recommendations.sh`

3. **품질 검증**: 
   ```bash
   ls -la ~/amazonqcli_lab/report/*.md
   wc -l ~/amazonqcli_lab/report/*.md
   ```

각 보고서는 실제 수집된 데이터를 기반으로 구체적인 분석과 권장사항을 포함.
```

### 예상 결과
- 📝 10개 Markdown 보고서 생성
- 📊 각 보고서 최소 100바이트 이상
- 🎯 실제 데이터 기반 분석 내용

---

## 📝 Phase 4: 보고서 생성 가이드

**참조 파일**: `04-report-generation-guide.md`

### 프롬프트

```
생성된 Markdown 보고서들을 검토하고 완성도 향상.

다음 10개 보고서가 모두 생성되었는지 확인하고 내용을 검토:

1. **01-executive-summary.md**: 경영진 요약 (전체 점수 79.7/100, 주요 발견사항)
2. **02-networking-analysis.md**: 5개 VPC, 36개 서브넷, 26개 보안 그룹 분석
3. **03-compute-analysis.md**: 34개 EC2 인스턴스, Auto Scaling, Load Balancer 분석
4. **04-database-analysis.md**: 2개 RDS 인스턴스, Aurora 클러스터, ElastiCache 분석
5. **05-storage-analysis.md**: 34개 EBS 볼륨, 스토리지 최적화 분석
6. **06-security-analysis.md**: 44개 IAM 역할, KMS 키, 보안 강화 방안
7. **07-application-analysis.md**: EventBridge, 애플리케이션 서비스 분석
8. **08-monitoring-analysis.md**: 8개 로그 그룹, 모니터링 강화 방안
9. **09-cost-optimization.md**: 비용 최적화 기회 및 권장사항
10. **10-recommendations.md**: 우선순위별 종합 권장사항

**검증 기준**:
- ✅ 파일 크기: 각각 최소 100바이트 이상
- ✅ 내용 품질: 실제 데이터에 기반한 구체적인 분석
- ✅ 권장사항: 우선순위별 실행 가능한 권장사항 포함

각 보고서의 주요 내용을 요약하여 보고해주세요.
```

### 예상 결과
- 📊 전체 분석 점수: 79.7/100 (양호)
- 🔴 높은 우선순위: IAM 보안 강화, 미사용 리소스 정리
- 🟡 중간 우선순위: 모니터링 강화, 백업 정책 수립
- 🟢 낮은 우선순위: 컨테이너 최적화, 네트워크 최적화

---

## 🌐 Phase 5: HTML 변환 및 배포

**참조 파일**: `05-html-conversion-guide.md`

### 권장 프롬프트

```
10개 Markdown 보고서를 전문적인 HTML 웹 대시보드로 변환.

**핵심 목표**: 10개 Markdown → 11개 HTML (index.html + 10개 보고서) 완전 변환

다음 3단계로 실행해주세요:

1. **HTML 변환 실행**:
   ```bash
   cd ~/amazonqcli_lab/aws-arch-analysis/script
   ./generate-html-reports.sh
   ```

2. **변환 결과 검증**:
   ```bash
   ./validate-html-conversion.sh
   ```

3. **문제 해결** (필요시):
   ```bash
   ./troubleshoot-html-conversion.sh
   ```

**성공 기준**:
- ✅ HTML 파일 개수: 정확히 11개
- ✅ 각 파일 크기: 3KB 이상  
- ✅ 네비게이션 링크: 모든 파일에 포함
- ✅ Assets 폴더: CSS, JS 파일 완전 구성

최종적으로 웹 서버를 실행하여 완성된 대시보드를 확인:
```bash
cd ~/amazonqcli_lab/html-report
python3 -m http.server 8080
```

브라우저에서 http://localhost:8080 접속하여 다음을 확인해주세요:
- 메인 대시보드 로딩
- 각 보고서 링크 클릭 테스트
- 네비게이션 메뉴 작동 확인
```

### 예상 결과
- 🌐 11개 HTML 파일 생성
- 🎨 완전한 Assets 구조 (CSS 3개, JS 4개, JSON 3개)
- 📱 반응형 디자인 지원
- 🖨️ 인쇄 최적화 지원

---

## 🚀 통합 실행 프롬프트 (전체 프로세스)

### 권장 프롬프트

```
현재 AWS 계정에 대한 완전한 종합 분석을 수행해주세요.

**목표**: 8개 영역 데이터 수집 → 10개 전문 보고서 생성 → 11개 HTML 파일 변환

**실행 순서**:

1. **환경 준비**: 
   ```bash
   cd ~/amazonqcli_lab/aws-arch-analysis/script
   ./check-environment.sh
   ```

2. **전체 분석 실행**:
   ```bash
   ./run-complete-analysis.sh
   ```

3. **HTML 변환**:
   ```bash
   ./generate-html-reports.sh
   ./validate-html-conversion.sh
   ```

4. **최종 확인**:
   ```bash
   cd ~/amazonqcli_lab/html-report
   python3 -m http.server 8080
   ```

**예상 결과**:
- 📊 데이터 수집: 150+ JSON 파일
- 📝 분석 보고서: 10개 Markdown 파일  
- 🌐 웹 대시보드: 11개 HTML 파일 + Assets
- 🎯 전체 분석 점수: 79.7/100 (양호)
- 🔴 우선 조치: IAM 보안 강화, 미사용 리소스 정리

**참고 데이터** (이전 분석 결과):
- VPC: 5개, EC2: 34개, RDS: 2개, EBS: 34개
- 보안 그룹: 26개, IAM 역할: 44개
- 네트워킹 성공률: 72% (13/18)
- 데이터베이스 성공률: 50% (10/20)

이전 분석 결과를 참고하여 개선된 분석을 수행해주세요.
```

---

## 📋 체크리스트

### Phase 1 완료 기준
- [ ] AWS 계정 정보 확인 완료
- [ ] 분석 도구 설치 및 검증 완료
- [ ] 디렉토리 구조 준비 완료
- [ ] 8개 영역 분석 계획 수립 완료

### Phase 2 완료 기준
- [ ] 네트워킹 데이터 수집 완료 (13/18 이상)
- [ ] 컴퓨팅 데이터 수집 완료
- [ ] 데이터베이스 데이터 수집 완료 (10/20 이상)
- [ ] 기타 영역 데이터 수집 완료

### Phase 3 완료 기준
- [ ] 전체 분석 스크립트 실행 완료
- [ ] 10개 보고서 생성 완료
- [ ] 보고서 품질 검증 완료

### Phase 4 완료 기준
- [ ] 10개 Markdown 파일 존재 확인
- [ ] 각 파일 크기 100바이트 이상 확인
- [ ] 실제 데이터 기반 내용 확인
- [ ] 권장사항 포함 확인

### Phase 5 완료 기준
- [ ] 11개 HTML 파일 생성 확인
- [ ] Assets 폴더 완전 구성 확인
- [ ] 네비게이션 링크 작동 확인
- [ ] 웹 서버 실행 및 접속 확인

---

**💡 팁**: 각 단계별로 체크리스트를 확인하며 진행하면 누락 없이 완전한 분석을 수행할 수 있습니다!
