AWS 계정 종합 분석 보고서 프롬프트
- AWS_Report_Implementation_Guide.md를 기반으로 현재 계정을 상세하게 분석진단해줘
- 상세 분석은 aws-diagnosis-prompt.md, aws-diagnosis-prompt-part2.md 롤 참고해줘.
- markdown으로 결과를 생성 (AWS 자원은 streampipe로 추출하고, glow를 활용해서, markdown을 뷰티파이)
- 상세하게 분석된 리포트는 마크다운으로 네트워킹 분석, 컴퓨팅 분석, 스토리지 분석, 데이터베이스 분석, 보안 분석, 비용 최적화, 모니터링 분석, 권장사항, 구현가이드 파트로 분석해줘.
- 생성된 마크다운은 HTML로 AWS_Report_Generation_Prompt_Part1.md, AWS_Report_Generation_Prompt_Part2.md, AWS_Report_Generation_Prompt_Part3.md, AWS_Report_Generation_Prompt_Part4.md 를 참조해서 생성해줘.
- HTML은 HTML_STYLE_GUIDE.md를 기반으로 변환해줘.
- ~/amazonqcli_lab/sample 의 HTML 스타일로 작성해줘.
- index.html에서 요약하고, 네트워킹 분석, 컴퓨팅 분석, 스토리지 분석, 데이터베이스 분석, 보안 분석, 비용 최적화, 모니터링 분석, 권장사항, 구현가이드 상세보고서로 링크를 연결하도록 구성
- 결과물은 ~/amazonqcli_lab/report 에 생성해줘.