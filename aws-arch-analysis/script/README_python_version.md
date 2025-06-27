# AWS 종합 분석 스크립트 - Python 버전

## 개요

기존의 bash 스크립트 `aws-comprehensive-analysis.sh`를 Python으로 변환한 버전입니다. 더 나은 오류 처리, 모듈화, 그리고 유지보수성을 제공합니다.

## 파일 구조

```
script/
├── aws_comprehensive_analysis.py    # 메인 실행 스크립트
├── report_utils.py                  # 보고서 생성 유틸리티
├── html_generator.py                # HTML 변환 및 대시보드 생성
├── report_generators.py             # 보고서 생성기 관리자
└── README_python_version.md         # 이 파일
```

## 사전 요구사항

### 필수 도구
- Python 3.6+
- AWS CLI (구성 완료)
- Steampipe (설치 및 구성 완료)

### Python 패키지 (선택사항)
```bash
# HTML 변환을 위한 markdown 패키지 (권장)
pip install markdown
```

## 사용법

### 1. 기본 실행
```bash
cd /home/ec2-user/code/amazonqcli_lab/aws-arch-analysis/script
python3 aws_comprehensive_analysis.py
```

### 2. 직접 실행 (실행 권한이 있는 경우)
```bash
./aws_comprehensive_analysis.py
```

## 주요 기능

### Phase 1: 환경 검증
- 필수 도구 설치 확인 (steampipe, aws, python3)
- AWS 자격 증명 확인
- 디렉토리 구조 생성

### Phase 2: 기존 보고서 백업
- 이전 보고서 자동 백업
- 타임스탬프 기반 백업 디렉토리 생성

### Phase 3: AWS 데이터 수집
- Steampipe를 통한 AWS 리소스 쿼리
- JSON 형태로 분석 데이터 저장
- 오류 발생 시 빈 데이터셋으로 계속 진행

### Phase 4: 데이터 분석
- 수집된 JSON 데이터 분석
- 리소스 통계 계산
- 비용 정보 집계

### Phase 5: Markdown 보고서 생성
- 10개 영역별 상세 보고서 생성
- 템플릿 기반 일관된 형식
- 실제 데이터 기반 동적 내용 생성

### Phase 6: HTML 변환
- Markdown을 HTML로 변환 (markdown 패키지 필요)
- 전문적인 스타일링 적용
- 네비게이션 링크 포함

### Phase 7: 대시보드 생성
- 인터랙티브 메인 대시보드
- 메트릭 카드 및 네비게이션 그리드
- 반응형 디자인

### Phase 8-10: 최종 처리
- 파일 검증
- 요약 정보 생성
- 완료 메시지 및 통계 출력

## 생성되는 보고서

### Markdown 보고서 (10개)
1. `01-executive-summary.md` - 전체 계정 분석 요약
2. `02-networking-analysis.md` - 네트워킹 분석
3. `03-computing-analysis.md` - 컴퓨팅 분석
4. `04-storage-analysis.md` - 스토리지 분석
5. `05-database-analysis.md` - 데이터베이스 분석
6. `06-security-analysis.md` - 보안 분석
7. `07-cost-optimization.md` - 비용 최적화
8. `08-application-monitoring.md` - 애플리케이션 서비스
9. `09-comprehensive-recommendations.md` - 종합 권장사항
10. `10-implementation-guide.md` - 구현 가이드

### HTML 보고서 (10개)
- 각 Markdown 보고서의 HTML 버전
- 전문적인 스타일링 적용
- 메인 대시보드로의 네비게이션 링크

### 대시보드
- `index.html` - 메인 대시보드
- 인터랙티브 메트릭 카드
- 각 보고서로의 직접 링크

### 분석 데이터
- `*.json` - Steampipe 쿼리 결과
- `analysis_summary.txt` - 분석 요약

## 출력 예시

```
╔══════════════════════════════════════════════════════════════╗
║                AWS 계정 종합 분석 보고서 생성기                ║
║                     자동화 스크립트 v2.0                      ║
╚══════════════════════════════════════════════════════════════╝

[STEP] Phase 1: 환경 준비 및 검증
[100%] [██████████████████████████████████████████████████] 환경 검증 중...
[SUCCESS] 환경 검증 완료

[STEP] Phase 2: 기존 보고서 백업
[100%] [██████████████████████████████████████████████████] 기존 보고서 백업 중...
[INFO] 백업할 기존 보고서가 없습니다.

...

╔══════════════════════════════════════════════════════════════╗
║                    🎉 분석 완료! 🎉                          ║
╚══════════════════════════════════════════════════════════════╝

[SUCCESS] AWS 계정 종합 분석 보고서가 성공적으로 생성되었습니다!

📊 분석 결과 요약:
  • VPC: 3개
  • EC2 인스턴스: 5개
  • 보안 그룹: 12개
  • 월간 총 비용: $45.67

📁 생성된 파일:
  • 보고서 위치: /path/to/report/comprehensive-analysis
  • 메인 대시보드: /path/to/report/comprehensive-analysis/index.html
  • Markdown 보고서: 10개
  • HTML 보고서: 10개

⏱️ 실행 시간: 2분 34초
```

## 장점

### Bash 버전 대비 개선사항
1. **더 나은 오류 처리**: 예외 처리 및 복구 메커니즘
2. **모듈화**: 기능별로 분리된 모듈 구조
3. **타입 힌트**: 코드 가독성 및 IDE 지원 향상
4. **JSON 처리**: 내장 json 모듈로 안전한 데이터 처리
5. **크로스 플랫폼**: Windows/Linux/macOS 지원
6. **확장성**: 새로운 기능 추가 용이

### 유지보수성
- 각 기능이 별도 클래스/함수로 분리
- 설정 가능한 매개변수
- 명확한 인터페이스 정의

## 문제 해결

### 일반적인 문제

#### 1. markdown 패키지 없음
```bash
pip install markdown
```
또는 HTML 변환 없이 Markdown 보고서만 생성됩니다.

#### 2. 권한 오류
```bash
chmod +x aws_comprehensive_analysis.py
```

#### 3. AWS 자격 증명 오류
```bash
aws configure
aws sts get-caller-identity
```

#### 4. Steampipe 연결 오류
```bash
steampipe service start
steampipe query "select 1"
```

### 디버깅

Python 스크립트는 더 상세한 오류 메시지를 제공합니다:
- 스택 트레이스로 정확한 오류 위치 파악
- 각 단계별 상태 메시지
- 실패한 쿼리나 파일에 대한 구체적 정보

## 커스터마이징

### 새로운 보고서 추가
1. `report_generators.py`에 새 메서드 추가
2. `generate_all_reports()` 메서드에 등록
3. HTML 변환 목록에 추가

### 쿼리 수정
`collect_aws_data()` 메서드의 `queries` 딕셔너리에서 Steampipe 쿼리를 수정할 수 있습니다.

### 스타일 변경
`html_generator.py`의 CSS 스타일을 수정하여 HTML 보고서의 외관을 변경할 수 있습니다.

## 기여

이 Python 버전은 원본 bash 스크립트의 모든 기능을 포함하면서 더 나은 구조와 확장성을 제공합니다. 추가 기능이나 개선사항이 있으면 언제든 기여해 주세요.
