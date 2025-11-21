# Kubernetes Deployment Guide - TPRM Agent

## Prerequisites

### 1. Install Required Tools
```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm (for Cert Manager)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Cert Manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 2. Configure Cluster
```bash
# Verify cluster connection
kubectl cluster-info

# Create namespace
kubectl apply -f namespace.yaml
```

## Security Setup

### 1. Create Secrets

**IMPORTANT:** Never commit actual secrets to Git!

```bash
# Create secrets from environment variables
kubectl create secret generic tprm-backend-secrets \
  --from-literal=AIRTABLE_API_KEY="${AIRTABLE_API_KEY}" \
  --from-literal=AIRTABLE_BASE_ID="${AIRTABLE_BASE_ID}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_API_KEY}" \
  --from-literal=SECRET_KEY="$(openssl rand -base64 32)" \
  -n tprm-agent

# Or use External Secrets Operator (recommended for production)
# See: https://external-secrets.io/
```

### 2. Configure ConfigMap
```bash
# Edit secrets.yaml with your domain
sed -i 's/yourdomain.com/your-actual-domain.com/g' secrets.yaml
kubectl apply -f secrets.yaml
```

### 3. Update Ingress Configuration
```bash
# Edit ingress.yaml
# 1. Replace 'yourdomain.com' with your actual domain
# 2. Replace 'your-email@yourdomain.com' with your email
# 3. Update image registry paths in deployments

sed -i 's/yourdomain.com/your-actual-domain.com/g' ingress.yaml
sed -i 's/your-email@yourdomain.com/admin@your-domain.com/g' ingress.yaml
```

## Deployment Steps

### 1. Install Cert Manager (if not already installed)
```bash
# Add Helm repository
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install Cert Manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0 \
  --set installCRDs=true

# Verify installation
kubectl get pods -n cert-manager
```

### 2. Deploy Application
```bash
# Deploy in order
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f network-policy.yaml

# Deploy Ingress and Cert Manager resources
kubectl apply -f ingress.yaml

# Verify deployments
kubectl get all -n tprm-agent
kubectl get certificate -n tprm-agent
kubectl get ingress -n tprm-agent
```

### 3. Monitor Certificate Issuance
```bash
# Watch certificate status
kubectl describe certificate tprm-tls-cert -n tprm-agent

# Check certificate order
kubectl get certificaterequest -n tprm-agent

# View Cert Manager logs
kubectl logs -n cert-manager -l app=cert-manager -f
```

### 4. Verify Deployment
```bash
# Check pod status
kubectl get pods -n tprm-agent

# View logs
kubectl logs -f deployment/tprm-backend -n tprm-agent
kubectl logs -f deployment/tprm-frontend -n tprm-agent

# Test endpoints
curl -k https://api.yourdomain.com/health
curl -k https://yourdomain.com
```

## SSL/TLS Certificate Management

### Using Let's Encrypt with Cert Manager

The deployment is configured to automatically provision SSL certificates using Let's Encrypt.

#### Test with Staging First
```bash
# Use staging issuer for testing
kubectl edit ingress tprm-ingress -n tprm-agent
# Change annotation to: cert-manager.io/cluster-issuer: "letsencrypt-staging"

# Apply changes
kubectl apply -f ingress.yaml

# Verify certificate
kubectl describe certificate tprm-tls-cert -n tprm-agent
```

#### Switch to Production
```bash
# Once staging works, switch to production
kubectl edit ingress tprm-ingress -n tprm-agent
# Change annotation to: cert-manager.io/cluster-issuer: "letsencrypt-prod"

# Delete old certificate to force renewal
kubectl delete certificate tprm-tls-cert -n tprm-agent

# Reapply
kubectl apply -f ingress.yaml
```

### Certificate Renewal
Cert Manager automatically renews certificates 30 days before expiry. No manual intervention required!

## Alternative: Using Pangolin Reverse Proxy

If using an external reverse proxy like Pangolin:

1. **Remove Ingress TLS configuration** - let Pangolin handle SSL termination
2. **Configure Pangolin** to forward traffic to Kubernetes Service
3. **Update ALLOWED_ORIGINS** in ConfigMap to include Pangolin's domain

```bash
# Modify Ingress to not handle TLS
kubectl edit ingress tprm-ingress -n tprm-agent
# Remove tls section

# Update backend to trust Pangolin's IPs
# Add to backend-deployment.yaml under env:
- name: FORWARDED_ALLOW_IPS
  value: "*"  # Or specific Pangolin IP
```

## Scaling

### Manual Scaling
```bash
# Scale backend
kubectl scale deployment tprm-backend --replicas=5 -n tprm-agent

# Scale frontend
kubectl scale deployment tprm-frontend --replicas=3 -n tprm-agent
```

### Horizontal Pod Autoscaler
```bash
kubectl autoscale deployment tprm-backend \
  --cpu-percent=70 \
  --min=3 --max=10 \
  -n tprm-agent
```

## Monitoring & Logging

### View Audit Logs
```bash
# Access audit logs from persistent volume
kubectl exec -it deployment/tprm-backend -n tprm-agent -- tail -f /app/logs/audit.log
```

### Prometheus Metrics
Pods are annotated for Prometheus scraping:
```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "8000"
prometheus.io/path: "/metrics"
```

## Troubleshooting

### Pods Not Starting
```bash
# Check events
kubectl describe pod <pod-name> -n tprm-agent

# Check logs
kubectl logs <pod-name> -n tprm-agent --previous
```

### Certificate Issues
```bash
# Check certificate status
kubectl describe certificate tprm-tls-cert -n tprm-agent

# Check challenge
kubectl get challenges -n tprm-agent

# Debug Cert Manager
kubectl logs -n cert-manager deployment/cert-manager
```

### Network Policy Issues
```bash
# Temporarily disable network policies for debugging
kubectl delete networkpolicy --all -n tprm-agent

# Re-enable after debugging
kubectl apply -f network-policy.yaml
```

## Security Hardening Checklist

- [ ] Secrets stored in external secret manager (not in Git)
- [ ] Network policies applied and tested
- [ ] Pod Security Standards enforced
- [ ] Resource limits configured
- [ ] Non-root containers verified
- [ ] Read-only root filesystems enabled
- [ ] TLS certificates auto-renewed
- [ ] Audit logging enabled
- [ ] RBAC policies defined
- [ ] Image vulnerabilities scanned

## Backup & Disaster Recovery

### Backup Persistent Volumes
```bash
# Backup uploads
kubectl exec deployment/tprm-backend -n tprm-agent -- \
  tar czf - /app/uploads | cat > uploads-backup-$(date +%Y%m%d).tar.gz

# Backup logs
kubectl exec deployment/tprm-backend -n tprm-agent -- \
  tar czf - /app/logs | cat > logs-backup-$(date +%Y%m%d).tar.gz
```

### Restore
```bash
# Restore uploads
cat uploads-backup.tar.gz | kubectl exec -i deployment/tprm-backend -n tprm-agent -- \
  tar xzf - -C /
```

## Updates & Rollbacks

### Rolling Update
```bash
# Update image
kubectl set image deployment/tprm-backend \
  backend=your-registry/tprm-backend:v1.2.0 \
  -n tprm-agent

# Monitor rollout
kubectl rollout status deployment/tprm-backend -n tprm-agent
```

### Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/tprm-backend -n tprm-agent

# Rollback to specific revision
kubectl rollout undo deployment/tprm-backend --to-revision=2 -n tprm-agent
```

## Clean Up
```bash
# Delete all resources
kubectl delete namespace tprm-agent

# Keep namespace but delete deployment
kubectl delete -f backend-deployment.yaml
kubectl delete -f frontend-deployment.yaml
kubectl delete -f ingress.yaml
```
