# No-Code/Low-Code AI Agent Platforms for TPRM

## Top Platforms Comparison

### **1. n8n (RECOMMENDED for your use case)**
**Type**: Open-source workflow automation + AI agents
**Cost**: Free (self-hosted) or $20/month (cloud)
**Best For**: Complex multi-step agents with API integrations

**Pros:**
- ✅ **Self-hostable** (complete control)
- ✅ Built-in **AI nodes** (OpenAI, Anthropic, Google AI)
- ✅ **800+ integrations** including Airtable, Microsoft APIs, Google Workspace
- ✅ **Vector database** support (Pinecone, Qdrant)
- ✅ **HTTP nodes** for custom API calls (Microsoft Defender)
- ✅ **Python code nodes** when you need custom logic
- ✅ **Webhooks** for triggering from your web app
- ✅ Active community + extensive documentation

**Cons:**
- Steeper learning curve than Zapier
- Need to host it somewhere (but can run locally)

**Perfect for TPRM because:**
- Connect to Airtable directly
- Call Microsoft Defender API easily
- Chain multiple AI models
- Store context in vector databases
- Trigger from your existing FastAPI backend

---

### **2. Google Vertex AI Agent Builder**
**Type**: Fully managed Google Cloud service
**Cost**: Pay-as-you-go (Gemini API usage)
**Best For**: Enterprise deployments on Google Cloud

**Pros:**
- ✅ **No infrastructure** management
- ✅ Native **Gemini integration**
- ✅ **Enterprise-grade** security
- ✅ Built-in **data connectors** (BigQuery, Cloud Storage)
- ✅ **Multi-turn conversations** with memory
- ✅ **Grounding with Google Search**

**Cons:**
- ❌ Locked into Google Cloud ecosystem
- ❌ Less flexible than n8n for custom workflows
- ❌ Harder to integrate with Microsoft Defender API

**Good if:** You're already on Google Cloud and want managed infrastructure

---

### **3. LangFlow**
**Type**: Visual builder for LangChain agents
**Cost**: Free (open-source)
**Best For**: LangChain developers who want visual debugging

**Pros:**
- ✅ Drag-and-drop LangChain components
- ✅ **Real-time preview** of agent execution
- ✅ Export to Python code
- ✅ Built for AI agents specifically

**Cons:**
- ❌ Less mature than n8n
- ❌ Fewer integrations
- ❌ Requires more LangChain knowledge

---

### **4. Flowise**
**Type**: Similar to LangFlow, visual LangChain builder
**Cost**: Free (open-source)
**Best For**: Quick prototyping of RAG agents

**Pros:**
- ✅ Beautiful UI
- ✅ Easy RAG setup
- ✅ Good for document Q&A agents

**Cons:**
- ❌ Limited compared to n8n for complex workflows
- ❌ Fewer enterprise integrations

---

### **5. Make (formerly Integromat)**
**Type**: Commercial workflow automation
**Cost**: $9-29/month
**Best For**: Non-technical users, polished UI

**Pros:**
- ✅ Beautiful visual interface
- ✅ OpenAI integration
- ✅ Many SaaS integrations

**Cons:**
- ❌ Can get expensive at scale
- ❌ Not as powerful as n8n for AI agents
- ❌ Limited AI-specific features

---

### **6. Microsoft Power Automate + AI Builder**
**Type**: Microsoft's no-code platform
**Cost**: Included with M365 licenses
**Best For**: Already using Microsoft 365

**Pros:**
- ✅ **Native Microsoft integration** (Defender, Teams, SharePoint)
- ✅ AI Builder for document processing
- ✅ Already licensed if you have M365

**Cons:**
- ❌ Limited AI agent capabilities
- ❌ More focused on RPA than AI agents
- ❌ Not great for complex multi-step reasoning

---

## **RECOMMENDATION: n8n**

### Why n8n is Best for Your TPRM System:

1. **Flexibility**: Can do everything the others can, plus custom code
2. **Cost**: Free if self-hosted
3. **Integration**: Easy connection to Airtable, Microsoft Defender, your FastAPI backend
4. **AI Native**: Built-in support for OpenAI, Gemini, Anthropic
5. **Extensible**: Python code nodes when visual isn't enough

---

## **n8n Architecture for TPRM Agents**

```
┌─────────────────────────────────────────────────────────────┐
│                     n8n Workflow Canvas                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Trigger] Webhook from Web App                              │
│      ↓                                                        │
│  [Airtable] Get Vendor Details                               │
│      ↓                                                        │
│  ┌───────────────── Parallel Branches ────────────────┐      │
│  │                                                      │      │
│  ├─► [HTTP] Microsoft Defender API                     │      │
│  │   └─► [AI] Gemini: Analyze CASB risk                │      │
│  │                                                      │      │
│  ├─► [Airtable] Get Uploaded Documents                 │      │
│  │   └─► [Code] Extract Text from PDF                  │      │
│  │       └─► [AI] Gemini: Analyze Document             │      │
│  │                                                      │      │
│  └─► [HTTP] HaveIBeenPwned API                         │      │
│      └─► [AI] Gemini: Assess breach risk               │      │
│                                                      │      │
│  [Merge] Combine All Results                                 │
│      ↓                                                        │
│  [AI Agent] Gemini: Synthesize Final Report                  │
│      ↓                                                        │
│  [Airtable] Update Vendor with Risk Score                    │
│      ↓                                                        │
│  [Condition] If Risk > 70 → Send Slack Alert                 │
│              Else → Auto-approve                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## **Implementation Plan with n8n**

### **Step 1: Install n8n**

```bash
# Option A: Docker (Recommended)
cd /home/naren/TPRM-agent
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Option B: NPM
npm install -g n8n
n8n start

# Access at: http://localhost:5678
```

### **Step 2: Create Your First Agent Workflow**

**Workflow: "Vendor Risk Analysis Agent"**

1. **Trigger Node**: Webhook
   - URL: `http://localhost:5678/webhook/analyze-vendor`
   - Method: POST
   - Body: `{ "vendor_id": "recXXX" }`

2. **Airtable Node**: Get Vendor Record
   - Operation: Get
   - Table: Vendors
   - Record ID: `{{ $json.vendor_id }}`

3. **HTTP Node**: Microsoft Defender API
   - Method: GET
   - URL: `https://portal.cloudappsecurity.com/api/v1/apps/?filter[name][eq]={{ $json.name }}`
   - Headers:
     - `Authorization: Token YOUR_DEFENDER_TOKEN`

4. **AI Agent Node**: Gemini Analysis
   - Model: gemini-2.5-flash
   - Prompt:
     ```
     Analyze this vendor's security posture:

     Vendor: {{ $node["Airtable"].json["name"] }}
     CASB Risk Score: {{ $node["HTTP Request"].json["data"][0]["riskScore"] }}
     Documents: {{ $node["Airtable Get Documents"].json }}

     Provide:
     1. Overall risk score (0-100)
     2. Key findings
     3. Recommendations

     Format as JSON.
     ```

5. **Code Node**: Parse AI Response
   ```javascript
   const result = JSON.parse($json.output);
   return {
     risk_score: result.risk_score,
     risk_level: result.risk_score > 70 ? 'High' :
                 result.risk_score > 40 ? 'Medium' : 'Low',
     findings: result.findings,
     recommendations: result.recommendations
   };
   ```

6. **Airtable Node**: Update Vendor
   - Operation: Update
   - Table: Vendors
   - Record ID: `{{ $json.vendor_id }}`
   - Fields: Risk Score, Risk Level, Last Assessed

7. **IF Node**: Check Risk Level
   - Condition: `{{ $json.risk_score }} > 70`
   - True Branch → **Slack Node**: Send Alert
   - False Branch → **HTTP Node**: Notify web app

### **Step 3: Integrate with Your Web App**

In your FastAPI backend, trigger the n8n workflow:

```python
# backend/app/main.py

@app.post("/vendors/{vendor_id}/analyze-with-agent")
async def analyze_with_agent(vendor_id: str):
    """Trigger n8n agent workflow for comprehensive analysis"""

    n8n_webhook_url = "http://localhost:5678/webhook/analyze-vendor"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            n8n_webhook_url,
            json={"vendor_id": vendor_id}
        )

    return {
        "message": "AI Agent analysis initiated",
        "workflow_id": response.json().get("executionId")
    }
```

---

## **Advanced: Multi-Agent Setup in n8n**

### **Workflow 1: Document Processing Agent**
- Triggered when document is uploaded
- Extracts text, classifies type
- Stores embeddings in vector DB
- Updates Airtable

### **Workflow 2: CASB Monitoring Agent**
- Runs on schedule (daily)
- Queries Microsoft Defender for all vendors
- Detects changes in risk scores
- Triggers alerts if score increases

### **Workflow 3: Comprehensive Analysis Agent**
- Triggered manually or on new vendor
- Calls Workflow 1 + 2
- Performs OSINT checks
- Generates final report

### **Workflow 4: Continuous Monitoring Agent**
- Runs weekly
- Re-analyzes all "High" risk vendors
- Checks for cert expiration
- Sends summary email

---

## **Google Alternative: Vertex AI Agent Builder**

If you prefer Google's managed solution:

### **Setup Steps:**

1. **Go to Google Cloud Console** → Vertex AI → Agent Builder

2. **Create Agent:**
   ```
   Agent Type: Generative AI Agent
   Model: Gemini 2.5 Flash
   ```

3. **Add Tools:**
   - Data Store (upload your documents)
   - Extensions (custom API calls)
   - Grounding (Google Search)

4. **Define Agent Instructions:**
   ```
   You are a TPRM analyst. When given a vendor:
   1. Search our document store for their compliance docs
   2. Call Microsoft Defender API to get CASB risk score
   3. Analyze all data and provide a comprehensive risk assessment
   ```

5. **Create Extension for Microsoft Defender:**
   ```yaml
   openapi: 3.0.0
   paths:
     /api/v1/apps:
       get:
         operationId: getAppRisk
         parameters:
           - name: name
             in: query
             schema:
               type: string
   ```

6. **Deploy & Get API Endpoint**

**Cons vs n8n:**
- Less visual workflow control
- Harder to debug
- More expensive at scale
- Locked to Google Cloud

---

## **My Recommendation: Start with n8n**

### **Week 1: MVP**
1. Install n8n locally
2. Create basic "Vendor Analysis" workflow
3. Integrate Airtable + Gemini
4. Test with 1 vendor

### **Week 2: Add Microsoft Defender**
1. Get Defender API credentials
2. Add HTTP node to query CASB
3. Enhance AI synthesis

### **Week 3: Add OSINT**
1. Add breach check APIs
2. Add cert verification
3. Build reporting

### **Week 4: Production**
1. Deploy n8n to cloud (Railway, Render, or DigitalOcean)
2. Connect to production Airtable
3. Add monitoring & alerts

---

## **Quick Start: Try n8n Now**

```bash
# Terminal 1: Start n8n
npx n8n

# Terminal 2: Keep your FastAPI backend running
cd backend && uvicorn app.main:app --reload

# Open browser
# n8n: http://localhost:5678
# Your app: http://localhost:3000
```

**First Workflow to Build:**
"When vendor is created in Airtable → Call Gemini to suggest risk level → Update Airtable"

This takes ~10 minutes to build in n8n's visual editor!

---

**Would you like me to:**
1. Help you install n8n and build the first workflow?
2. Create a detailed n8n workflow template you can import?
3. Show you how to integrate n8n with your existing FastAPI backend?
