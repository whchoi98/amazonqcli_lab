# AWS 계정 종합 분석 보고서 - 메인 가이드

## 📋 개요
이 가이드는 AWS 계정에 대한 종합적인 분석을 수행하고 전문적인 보고서를 생성합니다.

## 환경 및 역할
당신은 AWS의 수준높은 아키텍트 입니다. AWS 계정 내의 아키텍쳐를 상세분석하려고 합니다.
출력 결과들은 반드시 한글로 출력되어야 합니다.
리전은 ap-northeast-2 입니다.

## 🗂️ 프롬프트 구조

### 단계별 가이드 파일
각 프롬프트 파일을 순서대로 참조하여 단계별로 진행하세요. 데이터 수집은 steampipe 기반으로 수집합니다.
1. **[01-role-and-environment.md](./01-role-and-environment.md)** - 역할 정의 및 환경 설정
2. **[02-data-collection-guide.md](./02-data-collection-guide.md)** - 데이터 수집 전략
3. **[03-execution-methods.md](./03-execution-methods.md)** - 실행 방법론
4. **[04-report-generation-guide.md](./04-report-generation-guide.md)** - 보고서 생성 가이드
5. **[05-html-conversion-guide.md](./05-html-conversion-guide.md)** - HTML 변환 및 배포

## 📊 생성되는 보고서
- **01-executive-summary.md** - 경영진 요약
- **02-networking-analysis.md** - 네트워킹 분석
- **03-compute-analysis.md** - 컴퓨팅/컨테이너 분석
- **04-storage-analysis.md** - 스토리지 분석
- **05-database-analysis.md** - 데이터베이스 분석
- **06-security-analysis.md** - 보안 분석
- **07-cost-optimization.md** - 비용 최적화
- **08-application-analysis.md** - 애플리케이션 분석
- **09-monitoring-analysis.md** - 모니터링 분석
- **10-comprehensive-recommendations.md** - 종합 권장사항
- index.html , 10개 markdown을 HTML로 변환

## 🎯 사용 방법
1. 각 프롬프트 파일을 순서대로 읽고 따라하세요
2. 체크리스트를 활용하여 진행 상황을 확인하세요
3. 필요에 따라 특정 섹션만 선택적으로 실행하세요

---
**📌 참고**: 상세한 내용은 각 개별 프롬프트 파일을 참조하세요.
