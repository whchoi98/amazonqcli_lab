#!/bin/bash

# 🛠️ Amazon Q MCP 서버 설정 스크립트
# MCP (Model Context Protocol) 서버들을 설정하여 Amazon Q의 기능을 확장합니다.

set -e

echo "======================================================"
echo "🚀 Amazon Q MCP 서버 설정 시작"
echo "======================================================"

# 1. 먼저 디렉토리가 존재하는지 확인하고 필요하면 생성합니다
echo "📁 [1/2] MCP 설정 디렉토리 생성 중..."
mkdir -p ~/.aws/amazonq/
echo "✅ 디렉토리 생성 완료: ~/.aws/amazonq/"

# 2. MCP 설정 파일 생성
echo "📝 [2/2] MCP 설정 파일 생성 중..."
cat > ~/.aws/amazonq/mcp.json << 'EOF'
{
  "mcpServers": {
    "aws-knowledge-mcp-server": {
      "url": "https://knowledge-mcp.global.api.aws",
      "type": "http"
    },
    "awslabs.core-mcp-server": {
      "command": "uvx",
      "args": [
        "awslabs.core-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "autoApprove": [],
      "disabled": false
    },
    "awslabs.aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_DOCUMENTATION_PARTITION": "aws"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.cdk-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.cdk-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.aws-diagram-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-diagram-mcp-server"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "autoApprove": [],
      "disabled": false
    },
    "awslabs.cfn-mcp-server": {
      "command": "uvx",
      "args": [
        "awslabs.cfn-mcp-server@latest"
      ],
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.cloudwatch-mcp-server": {
      "autoApprove": [],
      "disabled": false,
      "command": "uvx",
      "args": [
        "awslabs.cloudwatch-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "transportType": "stdio"
    },
    "awslabs.eks-mcp-server": {
      "command": "uvx",
      "args": [
        "awslabs.eks-mcp-server@latest",
        "--allow-write",
        "--allow-sensitive-data-access"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_REGION": "ap-northeast-2"
      },
      "autoApprove": [],
      "disabled": false
    },
    "awslabs.cost-explorer-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.cost-explorer-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.aws-api-mcp-server": {
      "command": "uvx",
      "args": [
        "awslabs.aws-api-mcp-server@latest"
      ],
      "env": {
        "AWS_REGION": "us-east-1"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.terraform-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.terraform-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.code-doc-gen-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.code-doc-gen-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.iam-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.iam-mcp-server@latest"],
      "env": {
        "AWS_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    },
    "awslabs.billing-cost-management-mcp-server": {
      "command": "uvx",
      "args": [
         "awslabs.billing-cost-management-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_REGION": "us-east-1"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.ccapi-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.ccapi-mcp-server@latest"],
      "env": {
        "DEFAULT_TAGS": "enabled",
        "SECURITY_SCANNING": "enabled",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    },
    "awslabs.cloudtrail-mcp-server": {
      "autoApprove": [],
      "disabled": false,
      "command": "uvx",
      "args": [
        "awslabs.cloudtrail-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "transportType": "stdio"
    }
  }
}
EOF

echo "✅ MCP 설정 파일 생성 완료: ~/.aws/amazonq/mcp.json"

# 설정 파일 확인
echo ""
echo "📋 생성된 MCP 서버 목록:"
echo "   🌐 aws-knowledge-mcp-server - AWS 지식 베이스 (HTTP)"
echo "   🔧 awslabs.core-mcp-server - 핵심 AWS 기능"
echo "   📚 awslabs.aws-documentation-mcp-server - AWS 문서 검색"
echo "   🏗️  awslabs.cdk-mcp-server - AWS CDK 지원"
echo "   📊 awslabs.aws-diagram-mcp-server - AWS 아키텍처 다이어그램"
echo "   ☁️  awslabs.cfn-mcp-server - CloudFormation 지원"
echo "   📈 awslabs.cloudwatch-mcp-server - CloudWatch 모니터링"
echo "   🚀 awslabs.eks-mcp-server - EKS 클러스터 관리"
echo "   💰 awslabs.cost-explorer-mcp-server - 비용 분석"
echo "   🔌 awslabs.aws-api-mcp-server - AWS API 호출"
echo "   🌍 awslabs.terraform-mcp-server - Terraform 지원"
echo "   📝 awslabs.code-doc-gen-mcp-server - 코드 문서 생성"
echo "   🔐 awslabs.iam-mcp-server - IAM 관리"
echo "   💳 awslabs.billing-cost-management-mcp-server - 청구 및 비용 관리"
echo "   🛡️  awslabs.ccapi-mcp-server - 보안 및 컴플라이언스"
echo "   📋 awslabs.cloudtrail-mcp-server - CloudTrail 로그 분석"

echo ""
echo "======================================================"
echo "🎉 MCP 서버 설정이 완료되었습니다!"
echo ""
echo "💡 사용 방법:"
echo "   1. Amazon Q CLI를 재시작하세요"
echo "   2. 이제 확장된 기능들을 사용할 수 있습니다"
echo ""
echo "🔍 설정 파일 위치: ~/.aws/amazonq/mcp.json"
echo "======================================================"
