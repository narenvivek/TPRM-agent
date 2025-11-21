# Kubernetes Deployment Guide

## Overview

This guide provides comprehensive Kubernetes deployment manifests for the TPRM Agent system, including:
- FastAPI backend deployment
- Next.js frontend deployment
- n8n workflow engine deployment
- Persistent storage for documents
- Ingress configuration
- Secret management
- Auto-scaling policies

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │                    Ingress                          │ │
│  │  (NGINX/Traefik with SSL/TLS)                      │ │
│  └───────┬─────────────────┬────────────────┬─────────┘ │
│          │                 │                │           │
│  ┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐   │
│  │  Frontend    │  │   Backend    │  │    n8n     │   │
│  │  (Next.js)   │  │  (FastAPI)   │  │  (Agents)  │   │
│  │  Port: 3000  │  │  Port: 8000  │  │  Port: 5678│   │
│  │  Replicas: 2+│  │  Replicas: 3+│  │  Replicas:1│   │
│  └──────────────┘  └──────┬───────┘  └────────────┘   │
│                           │                            │
│                    ┌──────▼───────┐                    │
│                    │ PersistentVol│                    │
│                    │  (Documents)  │                    │
│                    └──────────────┘                    │
│                                                          │
│  External Services:                                     │
│  - Airtable (SaaS)                                      │
│  - Google Gemini AI (API)                               │
│  - Microsoft Defender (API)                             │
│  - Netskope (API)                                       │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm (optional, for n8n)
- Docker registry access
- Storage class for PersistentVolumes

## Directory Structure

```
k8s/
├── base/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── pvc.yaml
│   └── ingress.yaml
├── backend/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── frontend/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── n8n/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── pvc.yaml
└── kustomization.yaml
```

---

## 1. Namespace

**File**: `k8s/base/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tprm-agent
  labels:
    app: tprm-agent
    environment: production
```

---

## 2. ConfigMap

**File**: `k8s/base/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tprm-config
  namespace: tprm-agent
data:
  # Backend configuration
  STORAGE_TYPE: "local"
  STORAGE_PATH: "/app/uploads"
  BASE_URL: "https://api.tprm.example.com"

  # Frontend configuration
  NEXT_PUBLIC_API_URL: "https://api.tprm.example.com"

  # n8n configuration
  N8N_HOST: "n8n.tprm.example.com"
  N8N_PROTOCOL: "https"
  N8N_PORT: "443"
  WEBHOOK_URL: "https://n8n.tprm.example.com"

  # Feature flags
  FEATURE_COMBINED_ANALYSIS: "true"
  FEATURE_RISK_MATRIX: "true"
  FEATURE_ENTRA_AUTH: "true"
```

---

## 3. Secrets

**File**: `k8s/base/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tprm-secrets
  namespace: tprm-agent
type: Opaque
stringData:
  # Airtable
  AIRTABLE_API_KEY: "YOUR_AIRTABLE_PAT"
  AIRTABLE_BASE_ID: "YOUR_BASE_ID"

  # Google Gemini
  GEMINI_API_KEY: "YOUR_GEMINI_KEY"

  # Azure AD / EntraID
  AZURE_TENANT_ID: "YOUR_TENANT_ID"
  AZURE_CLIENT_ID: "YOUR_CLIENT_ID"
  AZURE_CLIENT_SECRET: "YOUR_CLIENT_SECRET"

  # CASB Platforms
  DEFENDER_API_TOKEN: "YOUR_DEFENDER_TOKEN"
  DEFENDER_TENANT_ID: "YOUR_DEFENDER_TENANT"
  NETSKOPE_API_TOKEN: "YOUR_NETSKOPE_TOKEN"
  NETSKOPE_TENANT: "YOUR_NETSKOPE_TENANT"

  # n8n
  N8N_ENCRYPTION_KEY: "YOUR_N8N_ENCRYPTION_KEY"
```

**Note**: In production, use external secret management:
- **Azure**: Azure Key Vault with CSI driver
- **AWS**: AWS Secrets Manager with External Secrets Operator
- **GCP**: Google Secret Manager
- **HashiCorp Vault**: Vault Agent Injector

---

## 4. Persistent Volume Claim

**File**: `k8s/base/pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: tprm-documents-pvc
  namespace: tprm-agent
spec:
  accessModes:
    - ReadWriteMany  # Required for multi-pod access
  storageClassName: standard  # Or your cluster's storage class
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: n8n-data-pvc
  namespace: tprm-agent
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 10Gi
```

---

## 5. Backend Deployment

**File**: `k8s/backend/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tprm-backend
  namespace: tprm-agent
  labels:
    app: tprm-backend
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tprm-backend
  template:
    metadata:
      labels:
        app: tprm-backend
        version: v1.0.0
    spec:
      containers:
      - name: fastapi
        image: your-registry/tprm-backend:1.0.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: STORAGE_TYPE
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: STORAGE_TYPE
        - name: STORAGE_PATH
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: STORAGE_PATH
        - name: BASE_URL
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: BASE_URL
        - name: AIRTABLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: AIRTABLE_API_KEY
        - name: AIRTABLE_BASE_ID
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: AIRTABLE_BASE_ID
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: GEMINI_API_KEY
        - name: AZURE_TENANT_ID
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: AZURE_TENANT_ID
        - name: AZURE_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: AZURE_CLIENT_ID
        - name: AZURE_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: AZURE_CLIENT_SECRET
        volumeMounts:
        - name: documents
          mountPath: /app/uploads
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: documents
        persistentVolumeClaim:
          claimName: tprm-documents-pvc
```

**File**: `k8s/backend/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tprm-backend
  namespace: tprm-agent
  labels:
    app: tprm-backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: tprm-backend
```

**File**: `k8s/backend/hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tprm-backend-hpa
  namespace: tprm-agent
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tprm-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 6. Frontend Deployment

**File**: `k8s/frontend/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tprm-frontend
  namespace: tprm-agent
  labels:
    app: tprm-frontend
    version: v1.0.0
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tprm-frontend
  template:
    metadata:
      labels:
        app: tprm-frontend
        version: v1.0.0
    spec:
      containers:
      - name: nextjs
        image: your-registry/tprm-frontend:1.0.0
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: NEXT_PUBLIC_API_URL
        - name: NEXT_PUBLIC_AZURE_TENANT_ID
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: AZURE_TENANT_ID
        - name: NEXT_PUBLIC_AZURE_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: AZURE_CLIENT_ID
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**File**: `k8s/frontend/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tprm-frontend
  namespace: tprm-agent
  labels:
    app: tprm-frontend
spec:
  type: ClusterIP
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
    name: http
  selector:
    app: tprm-frontend
```

**File**: `k8s/frontend/hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tprm-frontend-hpa
  namespace: tprm-agent
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tprm-frontend
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 7. n8n Deployment

**File**: `k8s/n8n/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
  namespace: tprm-agent
  labels:
    app: n8n
    version: v1.0.0
spec:
  replicas: 1  # n8n doesn't support multi-instance by default
  selector:
    matchLabels:
      app: n8n
  template:
    metadata:
      labels:
        app: n8n
        version: v1.0.0
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        ports:
        - containerPort: 5678
          name: http
        env:
        - name: N8N_HOST
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: N8N_HOST
        - name: N8N_PROTOCOL
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: N8N_PROTOCOL
        - name: N8N_PORT
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: N8N_PORT
        - name: WEBHOOK_URL
          valueFrom:
            configMapKeyRef:
              name: tprm-config
              key: WEBHOOK_URL
        - name: N8N_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: tprm-secrets
              key: N8N_ENCRYPTION_KEY
        - name: EXECUTIONS_DATA_SAVE_ON_SUCCESS
          value: "all"
        - name: EXECUTIONS_DATA_SAVE_ON_ERROR
          value: "all"
        volumeMounts:
        - name: n8n-data
          mountPath: /home/node/.n8n
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 5678
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthz
            port: 5678
          initialDelaySeconds: 30
          periodSeconds: 5
      volumes:
      - name: n8n-data
        persistentVolumeClaim:
          claimName: n8n-data-pvc
```

**File**: `k8s/n8n/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: n8n
  namespace: tprm-agent
  labels:
    app: n8n
spec:
  type: ClusterIP
  ports:
  - port: 5678
    targetPort: 5678
    protocol: TCP
    name: http
  selector:
    app: n8n
```

---

## 8. Ingress

**File**: `k8s/base/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tprm-ingress
  namespace: tprm-agent
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"  # For large file uploads
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - tprm.example.com
    - api.tprm.example.com
    - n8n.tprm.example.com
    secretName: tprm-tls-cert
  rules:
  - host: tprm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: tprm-frontend
            port:
              number: 3000
  - host: api.tprm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: tprm-backend
            port:
              number: 8000
  - host: n8n.tprm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: n8n
            port:
              number: 5678
```

---

## 9. Docker Images

### Backend Dockerfile

**File**: `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PDF/DOCX processing
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create uploads directory
RUN mkdir -p /app/uploads

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

**File**: `frontend/Dockerfile`

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build Next.js app
RUN npm run build

# Production image
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

**Note**: Update `next.config.js` to enable standalone output:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}

module.exports = nextConfig
```

---

## 10. Build & Push Images

**File**: `scripts/build-and-push.sh`

```bash
#!/bin/bash

VERSION=${1:-"1.0.0"}
REGISTRY=${2:-"your-registry"}

echo "Building images for version ${VERSION}..."

# Build backend
docker build -t ${REGISTRY}/tprm-backend:${VERSION} ./backend
docker push ${REGISTRY}/tprm-backend:${VERSION}

# Build frontend
docker build -t ${REGISTRY}/tprm-frontend:${VERSION} ./frontend
docker push ${REGISTRY}/tprm-frontend:${VERSION}

echo "Images pushed successfully!"
echo "Backend: ${REGISTRY}/tprm-backend:${VERSION}"
echo "Frontend: ${REGISTRY}/tprm-frontend:${VERSION}"
```

---

## 11. Deployment Commands

### Initial Setup

```bash
# Create namespace
kubectl apply -f k8s/base/namespace.yaml

# Create secrets (edit with your credentials first!)
kubectl apply -f k8s/base/secrets.yaml

# Create ConfigMap
kubectl apply -f k8s/base/configmap.yaml

# Create PVCs
kubectl apply -f k8s/base/pvc.yaml

# Deploy backend
kubectl apply -f k8s/backend/

# Deploy frontend
kubectl apply -f k8s/frontend/

# Deploy n8n
kubectl apply -f k8s/n8n/

# Create ingress
kubectl apply -f k8s/base/ingress.yaml
```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n tprm-agent

# Check pods
kubectl get pods -n tprm-agent

# Check services
kubectl get svc -n tprm-agent

# Check ingress
kubectl get ingress -n tprm-agent

# View logs
kubectl logs -f deployment/tprm-backend -n tprm-agent
kubectl logs -f deployment/tprm-frontend -n tprm-agent
kubectl logs -f deployment/n8n -n tprm-agent
```

### Update Deployment

```bash
# Update backend image
kubectl set image deployment/tprm-backend \
  fastapi=your-registry/tprm-backend:1.1.0 \
  -n tprm-agent

# Update frontend image
kubectl set image deployment/tprm-frontend \
  nextjs=your-registry/tprm-frontend:1.1.0 \
  -n tprm-agent

# Rollback if needed
kubectl rollout undo deployment/tprm-backend -n tprm-agent
```

---

## 12. Production Considerations

### Storage Options

**Cloud Provider Storage Classes**:

```yaml
# Azure
storageClassName: azure-disk
# or
storageClassName: azure-file  # For ReadWriteMany

# AWS
storageClassName: gp3
# or
storageClassName: efs-sc  # For ReadWriteMany

# GCP
storageClassName: standard-rwo
# or
storageClassName: filestore  # For ReadWriteMany
```

### Monitoring

Install Prometheus + Grafana:

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

**ServiceMonitor for Backend**:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tprm-backend-monitor
  namespace: tprm-agent
spec:
  selector:
    matchLabels:
      app: tprm-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Security

**NetworkPolicy** (restrict pod-to-pod communication):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tprm-network-policy
  namespace: tprm-agent
spec:
  podSelector:
    matchLabels:
      app: tprm-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: tprm-frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # External APIs (Airtable, Gemini, etc.)
```

### Backup Strategy

**Velero for PVC backups**:

```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket tprm-backups \
  --backup-location-config region=us-east-1

# Create backup schedule
velero schedule create tprm-daily \
  --schedule="@daily" \
  --include-namespaces tprm-agent
```

---

## 13. CI/CD Integration

**GitHub Actions Example** (`.github/workflows/deploy.yml`):

```yaml
name: Build and Deploy to K8s

on:
  push:
    tags:
      - 'v*'

env:
  REGISTRY: ghcr.io
  NAMESPACE: tprm-agent

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set version
      id: version
      run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

    - name: Build and push images
      run: |
        ./scripts/build-and-push.sh ${{ steps.version.outputs.VERSION }} ${{ env.REGISTRY }}

    - name: Set up kubectl
      uses: azure/k8s-set-context@v3
      with:
        kubeconfig: ${{ secrets.KUBECONFIG }}

    - name: Deploy to K8s
      run: |
        kubectl set image deployment/tprm-backend \
          fastapi=${{ env.REGISTRY }}/tprm-backend:${{ steps.version.outputs.VERSION }} \
          -n ${{ env.NAMESPACE }}

        kubectl set image deployment/tprm-frontend \
          nextjs=${{ env.REGISTRY }}/tprm-frontend:${{ steps.version.outputs.VERSION }} \
          -n ${{ env.NAMESPACE }}

    - name: Wait for rollout
      run: |
        kubectl rollout status deployment/tprm-backend -n ${{ env.NAMESPACE }}
        kubectl rollout status deployment/tprm-frontend -n ${{ env.NAMESPACE }}
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n tprm-agent

# Check logs
kubectl logs <pod-name> -n tprm-agent

# Check for resource constraints
kubectl top pods -n tprm-agent
```

### PVC Not Binding

```bash
# Check PVC status
kubectl get pvc -n tprm-agent

# Check available storage classes
kubectl get storageclass

# Check PV
kubectl get pv
```

### Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress events
kubectl describe ingress tprm-ingress -n tprm-agent

# Test internal service
kubectl run curl --image=curlimages/curl -it --rm -- \
  curl http://tprm-backend.tprm-agent.svc.cluster.local:8000/health
```

---

This comprehensive Kubernetes setup provides production-ready deployment with auto-scaling, monitoring, and security best practices.
