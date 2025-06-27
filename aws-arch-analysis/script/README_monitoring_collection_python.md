# Steampipe 모니터링 수집 스크립트 - Python 버전

## 개요

`steampipe_monitoring_collection.sh`를 Python으로 변환한 버전입니다. AWS 모니터링 및 로깅 리소스 데이터를 Steampipe를 통해 수집하는 스크립트입니다.

## 파일 정보

- **원본**: `steampipe_monitoring_collection.sh` (8,934 바이트)
- **Python 버전**: `steampipe_monitoring_collection.py` (약 12KB)
- **변환 완료일**: 2025-06-25

## 주요 기능

### 수집 대상 리소스 (26개 카테고리)

#### ✅ 실제 데이터 수집 성공 (7개)
1. **CloudWatch 알람 상세 정보** - 알람 구성, 상태, 메트릭 정보
2. **CloudWatch 로그 그룹 상세 정보** - 로그 그룹 설정, 보존 기간
3. **CloudWatch 로그 스트림** - 로그 스트림 메타데이터
4. **CloudWatch 메트릭 필터** - 로그 메트릭 변환 규칙
5. **AWS Config 적합성 팩** - 컴플라이언스 규칙 팩
6. **AWS Well-Architected 워크로드** - 아키텍처 검토 워크로드
7. **AWS Service Catalog 포트폴리오** - 서비스 카탈로그 포트폴리오

#### ⚠️ 서비스 미지원/데이터 없음 (18개)
- CloudWatch 대시보드, Insights 쿼리, 복합 알람
- X-Ray 관련 서비스 (추적, 서비스 맵, 암호화)
- CloudWatch Application/Container Insights
- CloudWatch Synthetics, RUM, Evidently
- AWS Systems Manager 관련 서비스
- AWS Cost 관련 서비스
- AWS Resource Groups, License Manager

#### ❌ 오류 발생 (1개)
- **AWS Personal Health Dashboard 이벤트** - 권한 또는 서비스 제한

## 사용법

### 기본 실행
```bash
python3 steampipe_monitoring_collection.py
```

### 옵션 지정 실행
```bash
# 특정 리전 지정
python3 steampipe_monitoring_collection.py -r us-west-2

# 출력 디렉토리 지정
python3 steampipe_monitoring_collection.py -d /custom/path

# 리전과 디렉토리 모두 지정
python3 steampipe_monitoring_collection.py -r eu-west-1 -d /tmp/reports
```

### 도움말 확인
```bash
python3 steampipe_monitoring_collection.py --help
```

## 실행 결과 예시

```
📊 Steampipe 기반 모니터링 및 로깅 리소스 데이터 수집 시작
Region: ap-northeast-2
Report Directory: /tmp/test_monitoring_report

✅ CloudWatch 알람 상세 정보 완료 (monitoring_cloudwatch_alarms.json, 1658 bytes)
✅ CloudWatch 로그 그룹 상세 정보 완료 (monitoring_cloudwatch_log_groups.json, 500 bytes)
✅ CloudWatch 로그 스트림 완료 (monitoring_cloudwatch_log_streams.json, 553 bytes)
✅ CloudWatch 메트릭 필터 완료 (monitoring_cloudwatch_metric_filters.json, 499 bytes)
⚠️ CloudWatch 대시보드 - 서비스 미지원 (monitoring_cloudwatch_dashboards.json, 2 bytes)
...
❌ AWS Personal Health Dashboard 이벤트 실패 - monitoring_health_events.json

모니터링 및 로깅 리소스 데이터 수집 완료!
성공: 7/26
🎉 모니터링 및 로깅 리소스 데이터 수집이 완료되었습니다!
```

## 생성되는 파일

### 데이터 파일 (JSON 형식)
```
monitoring_cloudwatch_alarms.json              # CloudWatch 알람
monitoring_cloudwatch_log_groups.json          # 로그 그룹
monitoring_cloudwatch_log_streams.json         # 로그 스트림
monitoring_cloudwatch_metric_filters.json      # 메트릭 필터
monitoring_config_conformance_packs.json       # Config 적합성 팩
monitoring_wellarchitected_workloads.json      # Well-Architected 워크로드
monitoring_servicecatalog_portfolios.json      # Service Catalog 포트폴리오
... (총 26개 파일)
```

### 로그 파일
```
steampipe_monitoring_collection.log            # 실행 로그
steampipe_monitoring_errors.log                # 오류 로그
```

## Python 버전의 장점

### 1. 향상된 오류 처리
```python
try:
    result = subprocess.run(['steampipe', 'query', query], check=True)
    # 성공 처리
except subprocess.CalledProcessError as e:
    # 구체적인 오류 정보 제공
    self.logger.error(f"쿼리 실패: {e}")
```

### 2. 객체 지향 설계
```python
class SteampipeMonitoringCollector:
    def __init__(self, region, report_dir):
        self.region = region
        self.report_dir = Path(report_dir)
        self.logger = Logger()
```

### 3. 타입 힌트 지원
```python
def execute_steampipe_query(self, description: str, query: str, output_file: str) -> bool:
    """명확한 함수 시그니처"""
```

### 4. 강력한 명령행 인수 처리
```python
parser = argparse.ArgumentParser(description="...")
parser.add_argument('-r', '--region', help='AWS 리전 설정')
```

### 5. 경로 처리 개선
```python
from pathlib import Path
self.report_dir = Path(report_dir)
self.report_dir.mkdir(parents=True, exist_ok=True)
```

## 환경 요구사항

### 필수 도구
- Python 3.6+
- Steampipe (AWS 플러그인 포함)
- AWS CLI (구성 완료)

### 설치 확인
```bash
# Steampipe 설치 확인
steampipe --version

# AWS 플러그인 확인
steampipe plugin list | grep aws

# AWS 자격 증명 확인
aws sts get-caller-identity
```

## 문제 해결

### 일반적인 문제

#### 1. Steampipe 미설치
```bash
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)"
steampipe plugin install aws
```

#### 2. AWS 플러그인 미설치
```bash
steampipe plugin install aws
```

#### 3. AWS 자격 증명 오류
```bash
aws configure
# 또는
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

#### 4. 권한 부족 오류
일부 서비스 (예: Personal Health Dashboard)는 특별한 권한이 필요할 수 있습니다.

### 디버깅

#### 로그 파일 확인
```bash
# 실행 로그
cat steampipe_monitoring_collection.log

# 오류 로그
cat steampipe_monitoring_errors.log
```

#### 개별 쿼리 테스트
```bash
steampipe query "select name from aws_cloudwatch_alarm limit 5"
```

## 성능 비교

| 항목 | Bash 버전 | Python 버전 |
|------|-----------|-------------|
| 실행 시간 | ~30-60초 | ~30-60초 (동일) |
| 메모리 사용량 | 낮음 | 약간 높음 |
| 오류 처리 | 기본적 | 상세함 |
| 로깅 | 기본적 | 구조화됨 |
| 확장성 | 제한적 | 우수함 |

## 확장 가능성

### 새로운 쿼리 추가
```python
def get_monitoring_queries(self) -> List[Tuple[str, str, str]]:
    return [
        # 기존 쿼리들...
        (
            "새로운 서비스 설명",
            "SELECT * FROM aws_new_service WHERE region = '{self.region}'",
            "new_service_output.json"
        )
    ]
```

### 출력 형식 변경
현재는 JSON만 지원하지만, CSV, YAML 등 다른 형식으로 쉽게 확장 가능합니다.

### 병렬 처리 추가
```python
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(self.execute_steampipe_query, desc, query, file) 
               for desc, query, file in queries]
```

## 결론

Python 버전은 원본 bash 스크립트의 모든 기능을 유지하면서도:
- 더 나은 오류 처리
- 구조화된 코드
- 확장 가능한 아키텍처
- 크로스 플랫폼 지원

을 제공합니다. 특히 대규모 환경에서의 안정성과 유지보수성이 크게 향상되었습니다.
