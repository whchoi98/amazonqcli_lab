AWS 계정 종합 분석 보고서
1.환경
- region : ap-northeast-2

2. 데이터 수집 도구
- Steampipe로 우선 수집해줘 : SQL 기반 AWS 리소스 분석
- AWS CLI: 추가 리소스 정보 수집
- Bash 스크립트: 자동화된 데이터 처리
- cloudformation 배포 내용 분석
- terraform 배포 내용 분석
- AWS CDK 배포 내용 분석
- 수집된 데이터는 ~/report에 json 형태로 수집

3. 계정 분석 방법
- 스크립트 활용 : ~/amazonqcli_lab/aws-arch-analysis/script 내의 모든 Script를 실행
- 수집된 데이터는 ~/amazonqcli_lab/report 에 생성되고, 이 데이터를 기반으로 상세하게 분석.
  
4. 보고서 생성 도구
- 보고서 생성 : ~/amazonqcli_lab/report 에 생성
- 보고서 유형 : Markdown으로 보고서를 작성.
- Markdown은 전체 계정 분석 요약, 네트워킹 분석, 컴퓨팅 분석, 스토리지 분석, 데이터베이스 분석, 보안 분석, 비용 최적화, 애플리케이션 서비스 및 모니터링 분석, 종합 분석 및 권장사항, 구현가이드 파트로 분리해서 생성


5. 보고서 생성 후 HTML로 변환
- index.html 파일 생성 : 전체 계정 분석 요약
- 분리해서 생성된 보고서 : 네트워킹 분석, 컴퓨팅 분석, 스토리지 분석, 데이터베이스 분석, 보안 분석, 비용 최적화, 애플리케이션 서비스 및 모니터링 분석, 종합 분석 및 권장사항, 구현가이드 파트는 각각 html로 변환
- ~/amazonqcli_lab/aws-arch-analysis/prompt/markdown-to-html-conversion-prompt.md 프롬프트를 사용해서, markdown을 HTML로 변환
- ~/amazonqcli_lab/aws-arch-analysis/sample/ 안에 있는 HTML 파일들을 참조해서 변환.

