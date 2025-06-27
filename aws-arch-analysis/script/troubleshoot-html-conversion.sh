#!/bin/bash
# HTML 변환 문제 진단 및 해결 스크립트

HTML_DIR="/home/ec2-user/amazonqcli_lab/html-report"
REPORT_DIR="/home/ec2-user/amazonqcli_lab/report"
SCRIPT_DIR="/home/ec2-user/amazonqcli_lab/aws-arch-analysis/script"

echo "🛠️ HTML 변환 문제 진단 및 해결 시작..."
echo "📅 진단 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 문제 진단 함수
diagnose_problem() {
    echo "🔍 문제 진단 중..."
    
    # 1. Markdown 파일 확인
    echo ""
    echo "📝 Markdown 파일 상태:"
    if [ -d "$REPORT_DIR" ]; then
        md_files=$(ls "$REPORT_DIR"/*.md 2>/dev/null | wc -l)
        echo "  - 발견된 Markdown 파일: $md_files개"
        
        if [ "$md_files" -lt 10 ]; then
            echo "  ❌ 문제: Markdown 파일 부족 ($md_files/10)"
            return 1
        fi
        
        # 빈 파일 확인
        echo "  - 파일 크기 확인:"
        for md_file in "$REPORT_DIR"/*.md; do
            if [ -f "$md_file" ]; then
                size=$(stat -f%z "$md_file" 2>/dev/null || stat -c%s "$md_file" 2>/dev/null)
                filename=$(basename "$md_file")
                if [ "$size" -lt 100 ]; then
                    echo "    ⚠️ $filename: ${size}bytes (너무 작음)"
                else
                    echo "    ✅ $filename: ${size}bytes"
                fi
            fi
        done
    else
        echo "  ❌ 문제: report 디렉토리 없음"
        return 1
    fi
    
    # 2. HTML 디렉토리 확인
    echo ""
    echo "🌐 HTML 디렉토리 상태:"
    if [ -d "$HTML_DIR" ]; then
        html_files=$(ls "$HTML_DIR"/*.html 2>/dev/null | wc -l)
        echo "  - 발견된 HTML 파일: $html_files개"
        
        if [ "$html_files" -lt 11 ]; then
            echo "  ❌ 문제: HTML 파일 부족 ($html_files/11)"
            return 2
        fi
    else
        echo "  ❌ 문제: html-report 디렉토리 없음"
        return 2
    fi
    
    # 3. 스크립트 파일 확인
    echo ""
    echo "🔧 스크립트 파일 상태:"
    scripts=("generate-html-reports.sh" "convert-md-to-html.sh")
    for script in "${scripts[@]}"; do
        if [ -f "$SCRIPT_DIR/$script" ]; then
            if [ -x "$SCRIPT_DIR/$script" ]; then
                echo "  ✅ $script: 실행 가능"
            else
                echo "  ⚠️ $script: 실행 권한 없음"
                chmod +x "$SCRIPT_DIR/$script"
                echo "    🔧 실행 권한 부여 완료"
            fi
        else
            echo "  ❌ $script: 파일 없음"
            return 3
        fi
    done
    
    return 0
}

# 자동 해결 함수
auto_fix() {
    local problem_code=$1
    
    echo ""
    echo "🔧 자동 해결 시도 중..."
    
    case $problem_code in
        1)
            echo "📝 Markdown 파일 문제 해결 중..."
            echo "  - Markdown 보고서 재생성 실행"
            cd "$SCRIPT_DIR"
            if [ -f "generate-all-reports.sh" ]; then
                ./generate-all-reports.sh
            else
                echo "  ⚠️ generate-all-reports.sh 스크립트 없음"
                echo "  💡 수동으로 보고서를 재생성하세요"
            fi
            ;;
        2)
            echo "🌐 HTML 파일 문제 해결 중..."
            echo "  - HTML 변환 스크립트 재실행"
            cd "$SCRIPT_DIR"
            ./generate-html-reports.sh
            ;;
        3)
            echo "🔧 스크립트 파일 문제 해결 중..."
            echo "  - 필요한 스크립트 파일들을 확인하세요"
            echo "  - 스크립트 디렉토리: $SCRIPT_DIR"
            ;;
        *)
            echo "🔄 전체 프로세스 재실행"
            cd "$SCRIPT_DIR"
            ./generate-html-reports.sh
            ;;
    esac
}

# 수동 해결 가이드
manual_fix_guide() {
    echo ""
    echo "📖 수동 해결 가이드"
    echo "=================="
    
    echo ""
    echo "🔴 문제 1: Markdown 파일 부족"
    echo "해결 방법:"
    echo "  cd $SCRIPT_DIR"
    echo "  ./generate-all-reports.sh  # 모든 보고서 재생성"
    
    echo ""
    echo "🔴 문제 2: HTML 파일 부족"
    echo "해결 방법:"
    echo "  cd $SCRIPT_DIR"
    echo "  ./convert-md-to-html.sh    # HTML 변환만 재실행"
    
    echo ""
    echo "🔴 문제 3: 특정 파일 누락"
    echo "해결 방법:"
    echo "  # 누락된 Markdown 파일 확인"
    echo "  ls -la $REPORT_DIR/*.md"
    echo "  # 누락된 HTML 파일 확인"
    echo "  ls -la $HTML_DIR/*.html"
    
    echo ""
    echo "🔴 문제 4: 파일 크기가 너무 작음"
    echo "해결 방법:"
    echo "  # 해당 보고서 개별 재생성"
    echo "  cd $SCRIPT_DIR"
    echo "  ./generate-[specific]-report.sh"
    
    echo ""
    echo "🔴 문제 5: Assets 폴더 누락"
    echo "해결 방법:"
    echo "  cd $SCRIPT_DIR"
    echo "  ./generate-html-reports.sh  # 전체 재실행"
}

# 메인 실행 로직
main() {
    # 1. 문제 진단
    diagnose_problem
    problem_code=$?
    
    if [ $problem_code -eq 0 ]; then
        echo ""
        echo "🎉 문제 없음! 모든 것이 정상입니다."
        echo "🔍 최종 검증을 위해 validate-html-conversion.sh를 실행하세요."
        return 0
    fi
    
    # 2. 자동 해결 시도
    echo ""
    read -p "🤖 자동 해결을 시도하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        auto_fix $problem_code
        
        echo ""
        echo "🔍 해결 후 재검증 중..."
        sleep 2
        
        # 재검증
        diagnose_problem
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 문제 해결 완료!"
            echo "🔍 최종 검증: ./validate-html-conversion.sh"
        else
            echo ""
            echo "⚠️ 자동 해결 실패. 수동 해결이 필요합니다."
            manual_fix_guide
        fi
    else
        manual_fix_guide
    fi
}

# 스크립트 실행
main "$@"
