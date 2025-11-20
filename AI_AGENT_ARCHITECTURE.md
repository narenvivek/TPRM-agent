# AI Agent Architecture for TPRM System

## Current State vs. Desired State

### Current (Web App with AI)
- User uploads document → API extracts text → Gemini analyzes → Returns results
- Manual trigger for each step
- No autonomous decision-making
- Single-shot analysis

### Desired (AI Agent)
- **Autonomous Agent** that plans and executes multi-step vendor analysis
- **Proactive intelligence gathering** from multiple sources
- **Continuous monitoring** and risk assessment
- **Human-in-the-loop** for critical decisions only

---

## Proposed Architecture

### **1. Agent Framework: LangGraph + CrewAI**

```
┌─────────────────────────────────────────────────────────────┐
│                    TPRM AI Agent System                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Orchestrator│  │ Task Planner │  │ Memory Store │      │
│  │    Agent     │◄─┤    Agent     │◄─┤  (Vector DB) │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                     │
│         ├──► Specialized Sub-Agents:                         │
│         │                                                     │
│         ├─► Document Analyst Agent                           │
│         │   • Extract & parse documents (PDF/DOCX/TXT)       │
│         │   • Identify document type (SOC2, ISO, Pentest)    │
│         │   • Extract key security controls                  │
│         │                                                     │
│         ├─► Risk Assessment Agent                            │
│         │   • Analyze compliance gaps                        │
│         │   • Calculate risk scores                          │
│         │   • Generate findings & recommendations            │
│         │                                                     │
│         ├─► CASB Integration Agent                           │
│         │   • Query Microsoft Defender for Cloud Apps        │
│         │   • Retrieve vendor risk scores                    │
│         │   • Check OAuth permissions & data access          │
│         │   • Monitor anomalous behavior                     │
│         │                                                     │
│         ├─► OSINT (Open Source Intelligence) Agent           │
│         │   • Search breach databases (HaveIBeenPwned)       │
│         │   • Check vendor security posture                  │
│         │   • Monitor news/social media for incidents        │
│         │   • Verify certifications (SOC2/ISO registries)    │
│         │                                                     │
│         ├─► Report Generation Agent                          │
│         │   • Synthesize findings from all sources           │
│         │   • Generate executive summary                     │
│         │   • Create remediation roadmap                     │
│         │                                                     │
│         └─► Monitoring Agent (Continuous)                    │
│             • Watch for vendor changes                        │
│             • Trigger re-assessment on events                │
│             • Alert on elevated risks                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## **2. Agent Workflow: Autonomous Vendor Analysis**

### **Phase 1: Discovery & Ingestion**
```python
Agent Task: "Analyze new vendor: Acme Corp"

Step 1: Document Collection Agent
  → Fetch uploaded documents from Airtable
  → Classify documents (SOC2, ISO27001, Pentest, Policy docs)
  → Extract text and structured data

Step 2: CASB Integration Agent
  → Query Microsoft Defender for Cloud Apps API
  → GET /api/v1/apps?filter=name:eq:AcmeCorp
  → Retrieve:
      - App risk score (0-10)
      - OAuth permissions requested
      - Data access patterns
      - Compliance certifications
      - User activity anomalies
```

### **Phase 2: Multi-Source Analysis**
```python
Step 3: Parallel Analysis (All agents work simultaneously)

Document Analyst Agent:
  → Analyze SOC2 report → Extract control evidence
  → Parse pentest results → Identify vulnerabilities

Risk Assessment Agent:
  → Compare against compliance frameworks
  → Calculate inherent vs residual risk
  → Generate risk matrix

OSINT Agent:
  → Check if vendor domain in breach databases
  → Verify ISO/SOC2 certification validity
  → Search for recent security incidents
  → Check Trustpilot/G2 reviews for security mentions

CASB Agent (Microsoft Defender):
  → Analyze OAuth scope creep
  → Check for shadow IT usage
  → Review data exfiltration patterns
```

### **Phase 3: Synthesis & Decision**
```python
Step 4: Orchestrator Agent
  → Aggregate findings from all sub-agents
  → Resolve conflicts (e.g., SOC2 cert vs breach found)
  → Calculate final risk score using weighted model:
      - Document analysis: 40%
      - CASB risk score: 30%
      - OSINT findings: 20%
      - Historical performance: 10%

Step 5: Report Generation Agent
  → Create comprehensive report
  → Highlight critical findings
  → Generate action items
  → Assign priority levels

Step 6: Human-in-the-Loop Decision
  → If risk_score > threshold (e.g., 70):
      → Flag for manual review
      → Agent proposes 3 remediation options
  → Else:
      → Auto-approve vendor
      → Schedule next review date
```

---

## **3. Technology Stack**

### **Agent Framework**
- **LangGraph**: For building stateful, multi-agent workflows
- **CrewAI**: For coordinating specialized agents
- **LangChain**: For LLM orchestration and tool integration

### **LLMs**
- **Primary**: Google Gemini 2.5 Flash (fast, cost-effective)
- **Secondary**: OpenAI GPT-4 for complex reasoning tasks
- **Embeddings**: OpenAI text-embedding-3-small for vector search

### **Tools & Integrations**
```python
Agent Tools = [
    # Document Processing
    "document_parser",      # Extract text from PDF/DOCX
    "document_classifier",  # Identify doc type using LLM

    # CASB Integration
    "microsoft_defender_api",  # Query Cloud App Security
    "oauth_analyzer",          # Analyze permissions

    # OSINT
    "haveibeenpwned_api",     # Breach checks
    "certifications_db",      # Verify certs
    "web_search",             # Google/Bing for incidents

    # Data Storage
    "airtable_read_write",    # Store findings
    "vector_db_search",       # RAG for historical context

    # Communication
    "email_sender",           # Alert stakeholders
    "slack_notifier",         # Real-time updates
]
```

### **Infrastructure**
- **Vector Database**: Pinecone or ChromaDB (for RAG)
- **Task Queue**: Celery + Redis (for async agent tasks)
- **Monitoring**: LangSmith for agent observability

---

## **4. Microsoft Defender for Cloud Apps Integration**

### **API Endpoints to Use**
```python
# 1. Get App Risk Score
GET /api/v1/apps/{app_id}
Response: {
    "name": "Acme Corp",
    "risk_score": 7.5,  # 0-10 scale
    "categories": ["Collaboration", "Storage"],
    "certifications": ["SOC2", "ISO27001"],
    "compliance": {
        "GDPR": true,
        "HIPAA": false
    }
}

# 2. Get OAuth Permissions
GET /api/v1/apps/{app_id}/oauth/permissions
Response: {
    "permissions": [
        {"scope": "files.read", "risk": "medium"},
        {"scope": "mail.send", "risk": "high"}
    ]
}

# 3. Monitor Anomalies
GET /api/v1/alerts?app={app_id}&severity=high
Response: {
    "alerts": [
        {
            "type": "unusual_data_download",
            "severity": "high",
            "timestamp": "2024-11-20T10:00:00Z"
        }
    ]
}
```

### **Agent Logic for CASB**
```python
class CASBAgent:
    async def analyze_vendor(self, vendor_name: str):
        # Step 1: Find app in Defender
        app = await self.find_app(vendor_name)

        # Step 2: Get risk score
        risk = await self.get_risk_score(app.id)

        # Step 3: Analyze OAuth permissions
        permissions = await self.analyze_permissions(app.id)
        excessive_permissions = [p for p in permissions if p.risk == "high"]

        # Step 4: Check for recent alerts
        alerts = await self.get_alerts(app.id)

        # Step 5: Return assessment
        return {
            "casb_risk_score": risk.score,
            "excessive_permissions": excessive_permissions,
            "recent_incidents": alerts,
            "recommendation": self.generate_recommendation(risk, permissions, alerts)
        }
```

---

## **5. Implementation Roadmap**

### **Phase 1: Foundation (Week 1-2)**
- [ ] Set up LangGraph + CrewAI framework
- [ ] Create base Orchestrator Agent
- [ ] Implement Document Analyst Agent
- [ ] Integrate with existing Gemini AI analysis

### **Phase 2: CASB Integration (Week 3)**
- [ ] Set up Microsoft Defender API credentials
- [ ] Implement CASB Integration Agent
- [ ] Test with real vendor data
- [ ] Create risk score normalization logic

### **Phase 3: OSINT & Enrichment (Week 4)**
- [ ] Implement OSINT Agent
- [ ] Integrate breach databases
- [ ] Add certification verification
- [ ] Build news/incident monitoring

### **Phase 4: Autonomous Workflows (Week 5)**
- [ ] Create end-to-end agent workflow
- [ ] Implement task planning agent
- [ ] Add human-in-the-loop approval gates
- [ ] Build reporting agent

### **Phase 5: Continuous Monitoring (Week 6)**
- [ ] Implement Monitoring Agent
- [ ] Set up scheduled re-assessments
- [ ] Create alert system
- [ ] Add Slack/Email notifications

---

## **6. Example: Full Agent Workflow**

```python
# User creates new vendor in UI
vendor = Vendor(name="Dropbox", criticality="High")

# Agent system kicks off automatically
orchestrator = TPRMOrchestrator()
task = orchestrator.create_task(f"Perform comprehensive analysis of {vendor.name}")

# Agent plans the workflow
plan = task_planner.plan([
    "Collect all uploaded documents",
    "Query Microsoft Defender for Cloud Apps",
    "Search for security incidents",
    "Analyze documents with Gemini",
    "Synthesize findings",
    "Generate report",
    "Recommend approval/rejection"
])

# Agents execute in parallel
results = await asyncio.gather(
    document_agent.analyze(vendor.id),
    casb_agent.query_defender(vendor.name),
    osint_agent.search_threats(vendor.name),
)

# Orchestrator synthesizes
final_report = orchestrator.synthesize(results)

# Decision gate
if final_report.risk_score > 70:
    # High risk - flag for human review
    await slack.notify(
        channel="#vendor-review",
        message=f"⚠️ {vendor.name} requires manual review. Risk Score: {final_report.risk_score}",
        report=final_report
    )
else:
    # Auto-approve
    vendor.status = "Approved"
    vendor.risk_score = final_report.risk_score
    await airtable.update(vendor)
```

---

## **7. Benefits Over Current System**

| Current Web App | AI Agent System |
|----------------|-----------------|
| Manual upload & analysis | **Autonomous** end-to-end workflow |
| Single document source | **Multi-source** intelligence (docs + CASB + OSINT) |
| One-time analysis | **Continuous monitoring** with alerts |
| Static risk scores | **Dynamic** risk assessment with context |
| No external validation | **Cross-verification** across sources |
| Human does all thinking | **Agent plans & executes**, human approves |

---

## **8. Next Steps**

1. **Approve Architecture**: Review and approve this design
2. **Microsoft Defender Access**: Obtain API credentials for Cloud App Security
3. **Install Agent Framework**:
   ```bash
   pip install langgraph crewai langchain pinecone-client celery redis
   ```
4. **Start with MVP**: Build Document Analyst + CASB Agent first
5. **Iterate**: Add more agents incrementally

---

**Would you like me to start implementing this AI Agent architecture?**

I can begin with:
1. Setting up the LangGraph orchestrator
2. Creating the first specialized agent (Document Analyst or CASB)
3. Implementing the multi-step workflow with autonomous planning
