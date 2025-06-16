# EKS 노드 H/W 이슈 발생 시 인지 및 대응 방법

## 1. 하드웨어 이슈 조기 인지 방법

### 1.1 시스템 레벨 모니터링

#### **Node Problem Detector 설치**
```yaml
# node-problem-detector.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-problem-detector
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: node-problem-detector
  template:
    metadata:
      labels:
        app: node-problem-detector
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-problem-detector
        image: registry.k8s.io/node-problem-detector/node-problem-detector:v0.8.19
        securityContext:
          privileged: true
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        volumeMounts:
        - name: log
          mountPath: /var/log
          readOnly: true
        - name: kmsg
          mountPath: /dev/kmsg
          readOnly: true
        - name: localtime
          mountPath: /etc/localtime
          readOnly: true
        - name: config
          mountPath: /config
          readOnly: true
        command:
        - /node-problem-detector
        - --logtostderr
        - --config.system-log-monitor=/config/kernel-monitor.json,/config/docker-monitor.json
        - --config.system-stats-monitor=/config/system-stats-monitor.json
      volumes:
      - name: log
        hostPath:
          path: /var/log/
      - name: kmsg
        hostPath:
          path: /dev/kmsg
      - name: localtime
        hostPath:
          path: /etc/localtime
      - name: config
        configMap:
          name: node-problem-detector-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: node-problem-detector-config
  namespace: kube-system
data:
  kernel-monitor.json: |
    {
      "plugin": "kmsg",
      "logPath": "/dev/kmsg",
      "lookback": "5m",
      "bufferSize": 10,
      "source": "kernel-monitor",
      "conditions": [
        {
          "type": "KernelDeadlock",
          "reason": "KernelHasNoDeadlock",
          "message": "kernel has no deadlock"
        },
        {
          "type": "ReadonlyFilesystem",
          "reason": "FilesystemIsNotReadonly",
          "message": "Filesystem is not read-only"
        }
      ],
      "rules": [
        {
          "type": "temporary",
          "reason": "OOMKilling",
          "pattern": "Killed process \\d+ (.+) total-vm:\\d+kB, anon-rss:\\d+kB, file-rss:\\d+kB.*"
        },
        {
          "type": "temporary",
          "reason": "TaskHung",
          "pattern": "task \\S+:\\w+ blocked for more than \\w+ seconds\\."
        },
        {
          "type": "temporary",
          "reason": "UnregisterNetDevice",
          "pattern": "unregister_netdevice: waiting for \\w+ to become free. Usage count = \\d+"
        },
        {
          "type": "temporary",
          "reason": "KernelOops",
          "pattern": "BUG: unable to handle kernel NULL pointer dereference at .*"
        },
        {
          "type": "temporary",
          "reason": "KernelOops",
          "pattern": "divide error: 0000 \\[#\\d+\\] SMP"
        },
        {
          "type": "permanent",
          "condition": "KernelDeadlock",
          "reason": "AUFSUmountHung",
          "pattern": "task umount\\.aufs:\\w+ blocked for more than \\w+ seconds\\."
        },
        {
          "type": "permanent",
          "condition": "KernelDeadlock",
          "reason": "DockerHung",
          "pattern": "task docker:\\w+ blocked for more than \\w+ seconds\\."
        },
        {
          "type": "permanent",
          "condition": "ReadonlyFilesystem",
          "reason": "FilesystemIsReadonly",
          "pattern": "Remounting filesystem read-only"
        }
      ]
    }
  system-stats-monitor.json: |
    {
      "cpu": {
        "metricsConfigs": [
          {
            "type": "cpu/load_1m",
            "threshold": 8.0
          },
          {
            "type": "cpu/load_5m", 
            "threshold": 6.0
          }
        ]
      },
      "disk": {
        "metricsConfigs": [
          {
            "type": "disk/io_time",
            "threshold": 0.95
          },
          {
            "type": "disk/weighted_io",
            "threshold": 100.0
          }
        ]
      },
      "memory": {
        "metricsConfigs": [
          {
            "type": "memory/available_bytes",
            "threshold": 100000000
          }
        ]
      }
    }
```

#### **CloudWatch Agent 설정**
```yaml
# cloudwatch-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cwagentconfig
  namespace: amazon-cloudwatch
data:
  cwagentconfig.json: |
    {
      "agent": {
        "region": "us-west-2"
      },
      "logs": {
        "metrics_collected": {
          "kubernetes": {
            "cluster_name": "my-cluster",
            "metrics_collection_interval": 60
          }
        },
        "force_flush_interval": 15
      },
      "metrics": {
        "namespace": "CWAgent",
        "metrics_collected": {
          "cpu": {
            "measurement": [
              "cpu_usage_idle",
              "cpu_usage_iowait",
              "cpu_usage_user",
              "cpu_usage_system"
            ],
            "metrics_collection_interval": 60,
            "resources": [
              "*"
            ],
            "totalcpu": false
          },
          "disk": {
            "measurement": [
              "used_percent",
              "inodes_free"
            ],
            "metrics_collection_interval": 60,
            "resources": [
              "*"
            ]
          },
          "diskio": {
            "measurement": [
              "io_time",
              "read_bytes",
              "write_bytes",
              "reads",
              "writes"
            ],
            "metrics_collection_interval": 60,
            "resources": [
              "*"
            ]
          },
          "mem": {
            "measurement": [
              "mem_used_percent"
            ],
            "metrics_collection_interval": 60
          },
          "netstat": {
            "measurement": [
              "tcp_established",
              "tcp_time_wait"
            ],
            "metrics_collection_interval": 60
          },
          "swap": {
            "measurement": [
              "swap_used_percent"
            ],
            "metrics_collection_interval": 60
          }
        }
      }
    }
```

### 1.2 하드웨어 특화 모니터링

#### **SMART 모니터링 (디스크 건강도)**
```bash
#!/bin/bash
# smart-monitor.sh
# DaemonSet으로 배포하여 각 노드에서 실행

check_disk_health() {
    local device=$1
    local smart_output=$(smartctl -a $device 2>/dev/null)
    
    # SMART 상태 확인
    if echo "$smart_output" | grep -q "SMART overall-health self-assessment test result: PASSED"; then
        echo "DISK_HEALTHY: $device"
    else
        echo "DISK_WARNING: $device - SMART test failed"
        # CloudWatch 메트릭 전송
        aws cloudwatch put-metric-data \
            --namespace "EKS/NodeHealth" \
            --metric-data MetricName=DiskHealth,Value=0,Unit=Count,Dimensions=NodeName=$NODE_NAME,Device=$device
    fi
    
    # 중요 SMART 속성 확인
    local reallocated_sectors=$(echo "$smart_output" | grep "Reallocated_Sector_Ct" | awk '{print $10}')
    local pending_sectors=$(echo "$smart_output" | grep "Current_Pending_Sector" | awk '{print $10}')
    
    if [[ $reallocated_sectors -gt 0 ]] || [[ $pending_sectors -gt 0 ]]; then
        echo "DISK_CRITICAL: $device - Bad sectors detected"
        # 노드에 taint 추가
        kubectl taint node $NODE_NAME disk-health=critical:NoSchedule --overwrite
    fi
}

# 모든 디스크 검사
for device in $(lsblk -d -o NAME | grep -E '^(sd|nvme)' | sed 's/^/\/dev\//'); do
    check_disk_health $device
done
```

#### **메모리 오류 모니터링**
```bash
#!/bin/bash
# memory-monitor.sh

check_memory_errors() {
    # ECC 메모리 오류 확인
    if [ -d /sys/devices/system/edac/mc ]; then
        for mc in /sys/devices/system/edac/mc/mc*; do
            if [ -f "$mc/ce_count" ]; then
                ce_count=$(cat "$mc/ce_count")
                ue_count=$(cat "$mc/ue_count")
                
                if [[ $ce_count -gt 0 ]] || [[ $ue_count -gt 0 ]]; then
                    echo "MEMORY_ERROR: Correctable=$ce_count, Uncorrectable=$ue_count"
                    
                    # CloudWatch 메트릭 전송
                    aws cloudwatch put-metric-data \
                        --namespace "EKS/NodeHealth" \
                        --metric-data MetricName=MemoryErrors,Value=$((ce_count + ue_count)),Unit=Count,Dimensions=NodeName=$NODE_NAME
                    
                    # 심각한 오류 시 노드 격리
                    if [[ $ue_count -gt 0 ]]; then
                        kubectl taint node $NODE_NAME memory-error=critical:NoSchedule --overwrite
                        kubectl cordon $NODE_NAME
                    fi
                fi
            fi
        done
    fi
    
    # dmesg에서 메모리 관련 오류 확인
    if dmesg | tail -100 | grep -i "memory error\|mce\|machine check"; then
        echo "MEMORY_WARNING: Memory errors detected in dmesg"
    fi
}

check_memory_errors
```

### 1.3 네트워크 하드웨어 모니터링

#### **네트워크 인터페이스 상태 모니터링**
```bash
#!/bin/bash
# network-monitor.sh

check_network_health() {
    local interface=$1
    
    # 인터페이스 통계 확인
    local rx_errors=$(cat /sys/class/net/$interface/statistics/rx_errors)
    local tx_errors=$(cat /sys/class/net/$interface/statistics/tx_errors)
    local rx_dropped=$(cat /sys/class/net/$interface/statistics/rx_dropped)
    local tx_dropped=$(cat /sys/class/net/$interface/statistics/tx_dropped)
    
    local total_errors=$((rx_errors + tx_errors + rx_dropped + tx_dropped))
    
    if [[ $total_errors -gt 1000 ]]; then
        echo "NETWORK_WARNING: $interface - High error rate: $total_errors"
        
        # CloudWatch 메트릭 전송
        aws cloudwatch put-metric-data \
            --namespace "EKS/NodeHealth" \
            --metric-data MetricName=NetworkErrors,Value=$total_errors,Unit=Count,Dimensions=NodeName=$NODE_NAME,Interface=$interface
    fi
    
    # 링크 상태 확인
    if ! ethtool $interface | grep -q "Link detected: yes"; then
        echo "NETWORK_CRITICAL: $interface - Link down"
        kubectl taint node $NODE_NAME network-issue=critical:NoSchedule --overwrite
    fi
}

# 모든 네트워크 인터페이스 확인
for interface in $(ls /sys/class/net/ | grep -E '^(eth|ens|eni)'); do
    check_network_health $interface
done
```

## 2. 파드 영향 최소화 방법

### 2.1 Proactive Node Management

#### **Node Health Check Controller**
```yaml
# node-health-controller.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-health-controller
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: node-health-controller
  template:
    metadata:
      labels:
        app: node-health-controller
    spec:
      serviceAccountName: node-health-controller
      containers:
      - name: controller
        image: node-health-controller:latest
        env:
        - name: CLUSTER_NAME
          value: "my-cluster"
        - name: DRAIN_TIMEOUT
          value: "300s"
        - name: HEALTH_CHECK_INTERVAL
          value: "60s"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: node-health-controller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-health-controller
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch", "patch", "update"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "delete"]
- apiGroups: [""]
  resources: ["events"]
  verbs: ["create"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: node-health-controller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: node-health-controller
subjects:
- kind: ServiceAccount
  name: node-health-controller
  namespace: kube-system
```

#### **Graceful Node Drain Script**
```bash
#!/bin/bash
# graceful-drain.sh

NODE_NAME=$1
DRAIN_TIMEOUT=${2:-300}

echo "Starting graceful drain for node: $NODE_NAME"

# 1. 노드를 스케줄링 불가능하게 설정
kubectl cordon $NODE_NAME

# 2. 중요한 파드 식별 및 우선순위 설정
CRITICAL_NAMESPACES=("kube-system" "monitoring" "logging")
CRITICAL_PODS=()

for ns in "${CRITICAL_NAMESPACES[@]}"; do
    pods=$(kubectl get pods -n $ns --field-selector spec.nodeName=$NODE_NAME -o name)
    CRITICAL_PODS+=($pods)
done

# 3. 일반 파드부터 점진적 드레인
echo "Draining non-critical pods..."
kubectl drain $NODE_NAME \
    --ignore-daemonsets \
    --delete-emptydir-data \
    --timeout=${DRAIN_TIMEOUT}s \
    --grace-period=30 \
    --exclude-namespace=kube-system

# 4. 중요 파드 개별 처리
for pod in "${CRITICAL_PODS[@]}"; do
    echo "Gracefully evicting critical pod: $pod"
    kubectl delete $pod --grace-period=60 --wait=true
done

# 5. 노드 상태 확인
remaining_pods=$(kubectl get pods --all-namespaces --field-selector spec.nodeName=$NODE_NAME --no-headers | wc -l)
if [[ $remaining_pods -eq 0 ]]; then
    echo "✅ Node $NODE_NAME successfully drained"
else
    echo "⚠️  Warning: $remaining_pods pods still running on $NODE_NAME"
fi
```

### 2.2 Pod Disruption Budget 설정

#### **중요 애플리케이션 PDB 설정**
```yaml
# critical-app-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: critical-app-pdb
  namespace: production
spec:
  minAvailable: 2  # 최소 2개 파드 유지
  selector:
    matchLabels:
      app: critical-app
      tier: production
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: database-pdb
  namespace: production
spec:
  maxUnavailable: 1  # 최대 1개까지만 중단 허용
  selector:
    matchLabels:
      app: database
      role: primary
```

### 2.3 Multi-AZ 배포 전략

#### **Anti-Affinity 규칙 설정**
```yaml
# multi-az-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resilient-app
spec:
  replicas: 6
  selector:
    matchLabels:
      app: resilient-app
  template:
    metadata:
      labels:
        app: resilient-app
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - resilient-app
            topologyKey: kubernetes.io/hostname  # 노드별 분산
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - resilient-app
            topologyKey: topology.kubernetes.io/zone  # AZ별 분산
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: node-health
                operator: NotIn
                values:
                - "critical"
                - "warning"
      containers:
      - name: app
        image: resilient-app:latest
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 3. 자동화된 대응 시스템

### 3.1 EventBridge 기반 자동 대응

#### **CloudWatch 알람 → EventBridge → Lambda**
```python
# node-health-responder.py
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

eks_client = boto3.client('eks')
ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    """
    CloudWatch 알람 이벤트를 처리하여 자동으로 노드 교체
    """
    try:
        # CloudWatch 알람 정보 파싱
        alarm_data = json.loads(event['Records'][0]['Sns']['Message'])
        alarm_name = alarm_data['AlarmName']
        
        # 노드 정보 추출
        if 'NodeName' in alarm_data['Trigger']['Dimensions']:
            node_name = next(d['value'] for d in alarm_data['Trigger']['Dimensions'] if d['name'] == 'NodeName')
            
            logger.info(f"Processing hardware issue for node: {node_name}")
            
            # 1. 노드 상태 확인
            node_status = check_node_status(node_name)
            
            if node_status['severity'] == 'CRITICAL':
                # 2. 긴급 노드 교체
                replace_node_immediately(node_name)
            elif node_status['severity'] == 'WARNING':
                # 3. 점진적 노드 교체 스케줄링
                schedule_node_replacement(node_name)
            
            return {
                'statusCode': 200,
                'body': json.dumps(f'Successfully processed alarm for node {node_name}')
            }
            
    except Exception as e:
        logger.error(f"Error processing alarm: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def check_node_status(node_name):
    """노드 상태 상세 확인"""
    # CloudWatch 메트릭 조회
    cloudwatch = boto3.client('cloudwatch')
    
    # 최근 5분간 메트릭 확인
    metrics = cloudwatch.get_metric_statistics(
        Namespace='EKS/NodeHealth',
        MetricName='HardwareErrors',
        Dimensions=[{'Name': 'NodeName', 'Value': node_name}],
        StartTime=datetime.utcnow() - timedelta(minutes=5),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Sum']
    )
    
    error_count = sum(point['Sum'] for point in metrics['Datapoints'])
    
    if error_count > 10:
        return {'severity': 'CRITICAL', 'error_count': error_count}
    elif error_count > 5:
        return {'severity': 'WARNING', 'error_count': error_count}
    else:
        return {'severity': 'INFO', 'error_count': error_count}

def replace_node_immediately(node_name):
    """긴급 노드 교체"""
    logger.info(f"Initiating immediate replacement for node: {node_name}")
    
    # 1. 노드 격리
    isolate_node(node_name)
    
    # 2. 새 노드 프로비저닝 (Karpenter 또는 ASG)
    trigger_node_provisioning()
    
    # 3. 알림 발송
    send_notification(f"Critical hardware issue detected on {node_name}. Node replacement initiated.")

def schedule_node_replacement(node_name):
    """점진적 노드 교체 스케줄링"""
    logger.info(f"Scheduling gradual replacement for node: {node_name}")
    
    # 1. 노드에 taint 추가 (새 파드 스케줄링 방지)
    add_node_taint(node_name, "hardware-warning=true:NoSchedule")
    
    # 2. 교체 스케줄 등록 (예: 다음 유지보수 창구)
    schedule_maintenance_replacement(node_name)
    
    # 3. 모니터링 강화
    increase_monitoring(node_name)

def isolate_node(node_name):
    """노드 격리 (cordon + drain)"""
    import subprocess
    
    # kubectl 명령 실행
    subprocess.run(['kubectl', 'cordon', node_name])
    subprocess.run(['kubectl', 'drain', node_name, '--ignore-daemonsets', '--delete-emptydir-data', '--timeout=300s'])

def send_notification(message):
    """SNS를 통한 알림 발송"""
    sns = boto3.client('sns')
    sns.publish(
        TopicArn='arn:aws:sns:region:account:eks-alerts',
        Message=message,
        Subject='EKS Node Hardware Issue Alert'
    )
```

### 3.2 Prometheus 기반 모니터링 및 알림

#### **Prometheus Rules**
```yaml
# node-hardware-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: node-hardware-monitoring
  namespace: monitoring
spec:
  groups:
  - name: node.hardware
    rules:
    - alert: NodeDiskErrors
      expr: increase(node_disk_io_errors_total[5m]) > 10
      for: 2m
      labels:
        severity: warning
        component: disk
      annotations:
        summary: "High disk I/O errors on {{ $labels.instance }}"
        description: "Node {{ $labels.instance }} has {{ $value }} disk I/O errors in the last 5 minutes"
    
    - alert: NodeMemoryErrors
      expr: node_memory_MemErrors_total > 0
      for: 0m
      labels:
        severity: critical
        component: memory
      annotations:
        summary: "Memory errors detected on {{ $labels.instance }}"
        description: "Node {{ $labels.instance }} has {{ $value }} memory errors"
    
    - alert: NodeHighIOWait
      expr: rate(node_cpu_seconds_total{mode="iowait"}[5m]) * 100 > 50
      for: 5m
      labels:
        severity: warning
        component: cpu
      annotations:
        summary: "High I/O wait on {{ $labels.instance }}"
        description: "Node {{ $labels.instance }} has {{ $value }}% I/O wait time"
    
    - alert: NodeNetworkErrors
      expr: increase(node_network_receive_errs_total[5m]) + increase(node_network_transmit_errs_total[5m]) > 100
      for: 2m
      labels:
        severity: warning
        component: network
      annotations:
        summary: "High network errors on {{ $labels.instance }}"
        description: "Node {{ $labels.instance }} has {{ $value }} network errors in the last 5 minutes"
```

## 4. 모니터링 대시보드

### 4.1 Grafana 대시보드 설정

#### **노드 하드웨어 상태 대시보드**
```json
{
  "dashboard": {
    "title": "EKS Node Hardware Health",
    "panels": [
      {
        "title": "Disk Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "node_disk_io_errors_total",
            "legendFormat": "{{ instance }} - {{ device }}"
          }
        ]
      },
      {
        "title": "Memory Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_memory_MemErrors_total[5m])",
            "legendFormat": "{{ instance }}"
          }
        ]
      },
      {
        "title": "Network Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_errs_total[5m]) + rate(node_network_transmit_errs_total[5m])",
            "legendFormat": "{{ instance }} - {{ device }}"
          }
        ]
      },
      {
        "title": "CPU I/O Wait",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_cpu_seconds_total{mode=\"iowait\"}[5m]) * 100",
            "legendFormat": "{{ instance }}"
          }
        ]
      }
    ]
  }
}
```

## 5. 운영 절차서

### 5.1 하드웨어 이슈 대응 플레이북

#### **Level 1: 경고 (Warning)**
1. **감지**: 모니터링 시스템에서 경고 알림
2. **확인**: 노드 상태 및 메트릭 상세 분석
3. **조치**: 
   - 노드에 taint 추가 (새 파드 스케줄링 방지)
   - 모니터링 주기 단축
   - 다음 유지보수 창구에 교체 스케줄링

#### **Level 2: 심각 (Critical)**
1. **감지**: 즉시 알림 (SMS, 전화)
2. **확인**: 노드 및 파드 상태 긴급 점검
3. **조치**:
   - 노드 즉시 격리 (cordon)
   - 파드 graceful eviction
   - 새 노드 자동 프로비저닝
   - 장애 노드 교체 요청

### 5.2 체크리스트

#### **사전 예방 체크리스트**
- [ ] Node Problem Detector 설치 및 설정
- [ ] CloudWatch Agent 구성
- [ ] Prometheus 모니터링 규칙 설정
- [ ] PodDisruptionBudget 설정
- [ ] Multi-AZ 배포 확인
- [ ] 자동 대응 Lambda 함수 배포

#### **장애 대응 체크리스트**
- [ ] 노드 상태 확인
- [ ] 파드 영향도 분석
- [ ] 노드 격리 실행
- [ ] 파드 재배치 확인
- [ ] 새 노드 프로비저닝 상태 확인
- [ ] 서비스 정상성 검증

이러한 종합적인 접근 방식을 통해 EKS 노드의 하드웨어 이슈를 조기에 감지하고, 파드에 미치는 영향을 최소화할 수 있습니다.
