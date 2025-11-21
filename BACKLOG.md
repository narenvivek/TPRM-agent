# TPRM Agent - Feature Backlog

## Current Version
**v1.0.0** - Initial Release (2024-11-20)

---

## High Priority (v1.x - Next 8 Weeks)

### Feature 1: Combined Multi-Document Analysis
**Target**: v1.1.0 (Week 2)
**Priority**: P0 (Critical)

**Description**: Analyze all vendor documents together for holistic risk assessment

**User Stories**:
- As a risk analyst, I want to analyze all documents at once so I can identify cross-document inconsistencies
- As a compliance officer, I want to see a comprehensive vendor report so I can make informed approval decisions
- As an auditor, I want to understand contradictions across documents so I can request clarifications

**Technical Requirements**:
- New endpoint: `POST /vendors/{vendor_id}/analyze-all`
- AI prompt enhancement for cross-document synthesis
- Detection of contradictions (e.g., SOC2 cert vs. pentest findings)
- Go/No-Go decision framework
- Comprehensive report generation

**Acceptance Criteria**:
- [ ] Can analyze 5+ documents simultaneously
- [ ] Cross-document insights generated
- [ ] Decision recommendation provided with justification
- [ ] Results stored in Airtable
- [ ] UI shows "Analyze All Documents" button
- [ ] Performance: <30s for 5 documents

**Dependencies**: None

**Estimated Effort**: 5 days

---

### Feature 2: Risk Matrix Configuration
**Target**: v1.2.0 (Week 4)
**Priority**: P0 (Critical)

**Description**: Visual risk matrix based on spend and criticality with configurable thresholds

**User Stories**:
- As a risk manager, I want to visualize vendors on a risk matrix so I can prioritize high-risk vendors
- As an executive, I want to configure risk thresholds so I can align with our risk appetite
- As an analyst, I want to see vendor distribution across risk quadrants so I can identify trends

**Technical Requirements**:
- Risk matrix configuration API endpoints
- Enhanced vendor model with business criticality and regulatory impact
- Frontend risk matrix visualization (heatmap with recharts/D3.js)
- Configurable spend ranges and criticality weights
- Automatic vendor positioning on matrix

**Acceptance Criteria**:
- [ ] Interactive risk matrix visualization
- [ ] Configurable spend ranges (default: 10k-100k, 100k-500k, 500k-1M, 1M-3M)
- [ ] Criticality score calculation with weighted factors
- [ ] Color-coded risk zones (green/yellow/red)
- [ ] Click vendor bubble to view details
- [ ] Admin UI for configuration

**Dependencies**: None

**Estimated Effort**: 7 days

---

### Feature 3: EntraID (Azure AD) Authentication
**Target**: v1.3.0 (Week 6)
**Priority**: P0 (Critical)

**Description**: Enterprise SSO with Microsoft Entra ID for secure authentication

**User Stories**:
- As a user, I want to sign in with my corporate account so I don't need separate credentials
- As an IT admin, I want SSO integration so I can manage access centrally
- As a security officer, I want audit logs of user actions so I can track compliance

**Technical Requirements**:
- Backend: fastapi-azure-auth integration
- Frontend: @azure/msal-react integration
- User context in API requests
- Role-based access control (RBAC)
- Audit logging

**Acceptance Criteria**:
- [ ] SSO login with Azure AD
- [ ] Protected API endpoints
- [ ] User profile display
- [ ] Role-based permissions (Viewer, Analyst, Admin)
- [ ] Audit log of user actions
- [ ] Automatic token refresh

**Dependencies**: Azure AD tenant configuration

**Estimated Effort**: 8 days

---

## Medium Priority (v2.x - Weeks 7-8)

### Feature 4: Specialized AI Agent with Memory
**Target**: v2.0.0 (Week 8)
**Priority**: P1 (High)

**Description**: Full autonomous AI agent with LangGraph, memory, and decision-making capabilities

**User Stories**:
- As a risk analyst, I want the agent to autonomously gather vendor intelligence so I can save time
- As a manager, I want the agent to provide Go/No-Go decisions so I can act quickly
- As an analyst, I want the agent to remember previous assessments so I can track vendor changes

**Technical Requirements**:
- LangGraph agent with multi-step planning
- Vector store (ChromaDB) for document memory
- RAG for context retrieval
- Specialized TPRM prompts
- Tool integration (document analysis, CASB, OSINT)
- Agent execution UI with progress tracking

**Acceptance Criteria**:
- [ ] Agent autonomously plans multi-step analysis
- [ ] Retrieves relevant context from document memory
- [ ] Makes Go/No-Go decisions with justification
- [ ] UI shows agent thinking process
- [ ] Can interrupt/correct agent during execution
- [ ] Results include confidence scores

**Dependencies**:
- Feature 1 (Combined Analysis)
- Feature 5 (MCP Tools)

**Estimated Effort**: 10 days

---

### Feature 5: MCP Tools for CASB Integration
**Target**: v2.0.0 (Week 8)
**Priority**: P1 (High)

**Description**: Out-of-box integrations with Microsoft Defender for Cloud Apps and Netskope CCI

**User Stories**:
- As a security analyst, I want CASB risk scores included in assessments so I can validate vendor claims
- As a compliance officer, I want to check OAuth permissions so I can assess data access risks
- As an auditor, I want to see security alerts so I can identify active threats

**Technical Requirements**:
- MCP server for Microsoft Defender for Cloud Apps
- MCP server for Netskope CCI
- API clients for CASB platforms
- Risk score normalization (Defender 0-10 → 0-100)
- Tool registration in agent system
- Error handling and fallback

**MCP Tools**:
**Microsoft Defender**:
- get_app_risk_score
- get_oauth_permissions
- check_security_alerts

**Netskope**:
- get_cci_score
- get_risk_assessment

**Acceptance Criteria**:
- [ ] Can query Microsoft Defender API
- [ ] Can query Netskope API
- [ ] Risk scores normalized to 0-100 scale
- [ ] CASB data included in vendor reports
- [ ] Graceful degradation if CASB unavailable
- [ ] Caching for rate limit management

**Dependencies**:
- Microsoft Defender API access
- Netskope API access

**Estimated Effort**: 8 days

---

## Infrastructure & DevOps

### Kubernetes Deployment
**Status**: ✅ Completed
**Documentation**: `KUBERNETES.md`

**Deliverables**:
- [x] K8s manifests for backend, frontend, n8n
- [x] ConfigMap and Secrets management
- [x] PersistentVolume for document storage
- [x] Ingress with SSL/TLS
- [x] HorizontalPodAutoscaler for auto-scaling
- [x] Health checks and probes
- [x] Docker build scripts

---

### Version Management
**Status**: ✅ Completed
**Documentation**: `VERSION_MANAGEMENT.md`

**Deliverables**:
- [x] Semantic versioning strategy
- [x] VERSION file
- [x] CHANGELOG.md
- [x] Release notes template
- [x] Version bump script (`scripts/bump-version.sh`)
- [x] Git workflow documentation
- [x] CI/CD GitHub Actions example

---

## Low Priority (Future Enhancements)

### Feature 6: n8n Agent Workflows
**Target**: v2.1.0
**Priority**: P2 (Medium)

**Description**: Visual agent workflows using n8n for orchestration

**Requirements**:
- n8n installation and configuration
- Pre-built workflow templates
- Webhook integration with FastAPI
- Scheduled monitoring workflows

**Effort**: 5 days

---

### Feature 7: Advanced OSINT
**Target**: v2.2.0
**Priority**: P2 (Medium)

**Description**: Open-source intelligence gathering for vendors

**Features**:
- Breach database checks (HaveIBeenPwned)
- Certificate verification
- News/incident monitoring
- Social media sentiment analysis

**Effort**: 6 days

---

### Feature 8: Compliance Framework Mapping
**Target**: v2.3.0
**Priority**: P3 (Low)

**Description**: Map vendor controls to compliance frameworks (SOC2, ISO27001, NIST)

**Features**:
- Framework templates
- Gap analysis
- Control mapping
- Compliance reporting

**Effort**: 7 days

---

### Feature 9: Vendor Portal
**Target**: v3.0.0
**Priority**: P3 (Low)

**Description**: Self-service portal for vendors to upload documents

**Features**:
- Vendor-specific login
- Document upload by vendors
- Status tracking
- Automated notifications

**Effort**: 12 days

---

## Technical Debt

### Code Quality
- [ ] Add comprehensive unit tests (target: 80% coverage)
- [ ] Add integration tests
- [ ] Add E2E tests with Playwright
- [ ] Implement type checking in Python (mypy)
- [ ] ESLint configuration for frontend
- [ ] Code documentation (docstrings)

### Performance
- [ ] Implement Redis caching for Airtable queries
- [ ] Add CDN for static assets
- [ ] Optimize Gemini API calls (batching)
- [ ] Database indexing (if migrating from Airtable)

### Security
- [ ] Implement rate limiting
- [ ] Add API key rotation
- [ ] Security headers (HSTS, CSP)
- [ ] Vulnerability scanning (Dependabot)
- [ ] Penetration testing

### Monitoring
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Log aggregation (ELK/Loki)
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring

---

## Release Schedule

| Version | Features | Target Date | Status |
|---------|----------|-------------|--------|
| v1.0.0 | Initial Release | 2024-11-20 | ✅ Released |
| v1.1.0 | Combined Analysis | Week 2 | 🔄 Planned |
| v1.2.0 | Risk Matrix | Week 4 | 📋 Backlog |
| v1.3.0 | EntraID Auth | Week 6 | 📋 Backlog |
| v2.0.0 | AI Agent + CASB | Week 8 | 📋 Backlog |
| v2.1.0 | n8n Workflows | TBD | 💡 Future |
| v2.2.0 | OSINT | TBD | 💡 Future |
| v2.3.0 | Compliance Mapping | TBD | 💡 Future |
| v3.0.0 | Vendor Portal | TBD | 💡 Future |

---

## Notes

- **n8n Integration**: Confirmed for use in agent development
- **CASB Platforms**: Microsoft Defender for Cloud Apps and Netskope CCI prioritized
- **Kubernetes**: Production-ready manifests available
- **Version Management**: Full workflow established with automated scripts

---

Last Updated: 2024-11-20
