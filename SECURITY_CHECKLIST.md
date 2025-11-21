# Security Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment Security Checklist

### Environment Configuration
- [ ] `.env` file created from `.env.example` with actual values
- [ ] `SECRET_KEY` generated with `openssl rand -base64 32`
- [ ] `ENVIRONMENT=production` set
- [ ] `DEBUG=False` set
- [ ] `ALLOWED_ORIGINS` contains only production domains (no `*`)
- [ ] All API keys rotated and secured

### Secrets Management
- [ ] No secrets committed to Git (check with `git log -S "AIRTABLE_API_KEY"`)
- [ ] Secrets stored in Azure Key Vault / AWS Secrets Manager
- [ ] `.env` file in `.gitignore`
- [ ] Kubernetes secrets created (not from YAML file)

### Application Security
- [ ] Rate limiting enabled (`RATE_LIMIT_ENABLED=true`)
- [ ] Audit logging enabled (`AUDIT_LOG_ENABLED=true`)
- [ ] File size limits configured (`MAX_FILE_SIZE=10485760`)
- [ ] CORS origins restricted (no wildcards)
- [ ] Security headers middleware enabled

### Docker/Container Security
- [ ] Containers run as non-root user
- [ ] Read-only root filesystem enabled
- [ ] Capabilities dropped (`CAP_DROP=ALL`)
- [ ] Health checks configured
- [ ] No secrets in Docker images (use env vars)
- [ ] Images scanned for vulnerabilities (`docker scan`)

### Kubernetes Security
- [ ] Secrets created via `kubectl create secret` (not YAML)
- [ ] Network policies applied
- [ ] Pod security context configured (`runAsNonRoot: true`)
- [ ] Resource limits set
- [ ] Service accounts created
- [ ] RBAC policies defined
- [ ] Ingress TLS configured
- [ ] Cert Manager installed and working

### SSL/TLS Configuration
- [ ] Cert Manager installed
- [ ] ClusterIssuer created (letsencrypt-prod)
- [ ] Ingress annotations correct (`cert-manager.io/cluster-issuer`)
- [ ] Certificate auto-renewal tested
- [ ] TLS 1.2+ enforced
- [ ] HSTS header enabled (production)

### Monitoring & Logging
- [ ] Audit logs directory writable (`logs/`)
- [ ] Log rotation configured
- [ ] Monitoring alerts configured
- [ ] Prometheus scraping enabled
- [ ] Error tracking (Sentry, etc.) configured

### Network Security
- [ ] Firewall rules configured
- [ ] DDoS protection enabled (Cloudflare, etc.)
- [ ] Rate limiting at load balancer level
- [ ] Web Application Firewall (WAF) considered

### Dependency Security
- [ ] All dependencies pinned to specific versions
- [ ] Vulnerabilities scanned (`pip-audit`, `npm audit`)
- [ ] No known critical vulnerabilities
- [ ] Dependency update policy in place

### Access Control (When EntraID Implemented)
- [ ] EntraID authentication configured
- [ ] User roles defined
- [ ] Least privilege access enforced
- [ ] Session timeout configured

### Backup & Recovery
- [ ] Backup strategy defined
- [ ] Persistent volumes backed up
- [ ] Restore procedure tested
- [ ] RTO/RPO defined

### Testing
- [ ] Path traversal tests passed
- [ ] File upload validation tested
- [ ] Rate limiting verified
- [ ] Security headers checked (`curl -I`)
- [ ] SSL certificate valid (`openssl s_client -connect`)
- [ ] Penetration testing completed (optional but recommended)

### Documentation
- [ ] Security implementation documented
- [ ] Incident response plan created
- [ ] Runbooks updated
- [ ] Team trained on security procedures

### Compliance
- [ ] GDPR requirements reviewed
- [ ] SOC2 controls documented
- [ ] Data retention policies defined
- [ ] Privacy policy updated

---

## Post-Deployment Verification

### Immediate (Day 1)
```bash
# 1. Verify application is running
kubectl get pods -n tprm-agent

# 2. Check certificate status
kubectl get certificate -n tprm-agent

# 3. Test SSL certificate
curl -I https://yourdomain.com

# 4. Verify security headers
curl -I https://api.yourdomain.com/health

# 5. Check audit logs
kubectl logs -f deployment/tprm-backend -n tprm-agent

# 6. Test rate limiting (should get 429 after limits)
for i in {1..11}; do curl https://api.yourdomain.com/vendors; done
```

### Week 1
- [ ] Monitor audit logs daily
- [ ] Review failed requests
- [ ] Check resource usage
- [ ] Verify backups working
- [ ] Test alert notifications

### Month 1
- [ ] Run vulnerability scan
- [ ] Review and rotate secrets
- [ ] Test disaster recovery
- [ ] Update dependencies (security patches)
- [ ] Review security metrics

---

## Quick Security Tests

### Test 1: Path Traversal Protection
```bash
# Should return 400 Bad Request
curl https://api.yourdomain.com/files/../../../etc/passwd
```

### Test 2: Security Headers
```bash
# Check all headers present
curl -I https://api.yourdomain.com/health | grep -E "X-|Content-Security|Strict-Transport"
```

### Test 3: SSL/TLS Configuration
```bash
# Test SSL certificate and protocols
nmap --script ssl-enum-ciphers -p 443 yourdomain.com
```

### Test 4: Rate Limiting
```bash
# Should get 429 on 11th request
for i in {1..15}; do
  echo "Request $i:"
  curl -w "\nStatus: %{http_code}\n" https://api.yourdomain.com/vendors
  sleep 1
done
```

### Test 5: File Upload Validation
```bash
# Rename malware.exe to malware.pdf - should be rejected
curl -F "files=@malware.pdf" https://api.yourdomain.com/vendors/rec123/documents/upload
# Expected: "File extension does not match file type"
```

---

## Emergency Contacts

- **Security Team:** security@yourdomain.com
- **DevOps On-Call:** [PagerDuty/Opsgenie]
- **Cert Manager Issues:** https://cert-manager.io/docs/troubleshooting/
- **Let's Encrypt Status:** https://letsencrypt.status.io/

---

## Quick Reference: Security Incident

**If you detect a security incident:**

1. **DO NOT PANIC** - Follow the incident response plan
2. **Isolate:** Scale affected pods to 0
3. **Preserve Evidence:** Backup logs immediately
4. **Notify:** Contact security team
5. **Investigate:** Analyze audit logs
6. **Remediate:** Patch and redeploy
7. **Document:** Write incident report

```bash
# Emergency: Scale down compromised deployment
kubectl scale deployment/tprm-backend --replicas=0 -n tprm-agent

# Preserve logs
kubectl logs deployment/tprm-backend -n tprm-agent > incident-logs-$(date +%Y%m%d-%H%M%S).log

# Backup audit logs
kubectl exec deployment/tprm-backend -n tprm-agent -- \
  cat /app/logs/audit.log > audit-backup-$(date +%Y%m%d-%H%M%S).log
```

---

**Last Updated:** 2025-11-20
**Version:** 1.1.0
