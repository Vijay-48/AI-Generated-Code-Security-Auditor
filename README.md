<p align="center">
  <img src="https://raw.githubusercontent.com/Vijay-48/ai-code-security-auditor/main/assets/logo-light.svg" alt="AI Code Security Auditor" width="360"/>
</p>

<p align="center">
  <b>Automated Security Audits with LLM-Powered Fixes</b>
</p>

<p align="center">
  <a href="https://github.com/Vijay-48/ai-code-security-auditor/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/your-org/ai-code-security-auditor.svg"></a>
  <a href="https://hub.docker.com/r/vijay48/ai-code-security-auditor"><img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/your-org/ai-code-security-auditor"></a>
</p>

---

# 🔐 AI-Generated Code Security Auditor

An automated security auditing service that scans code or repositories, detects vulnerabilities, and generates ready-to-apply **git diffs** using static analysis, RAG-enhanced context, and Deepseek R1 LLM via OpenRouter.

---

## 🚀 What It Does

1. **Ingest Code**  
   Accepts raw code via REST API or GitHub push/PR webhooks.

2. **Static Analysis**  
   Uses [Bandit](https://bandit.readthedocs.io/en/latest/) (Python) and [Semgrep](https://semgrep.dev/) (multi-language) for scanning.

3. **Normalize Findings**  
   Outputs standardized vulnerability reports (CWE ID, severity, snippet, etc.).

4. **RAG Remediation**  
   Queries a ChromaDB vector store of fix patterns for the identified issues.

5. **LLM-Powered Diff Generation**  
   Prompts Deepseek R1 via OpenRouter to generate secure, minimal git diff patches with in-line comments.

6. **Patch Assessment**  
   Uses LLM scoring on correctness, quality, and performance impact.

7. **Response Aggregation**  
   Returns JSON with full audit results, patches, and fix quality scores.

8. **CI/CD Integration**  
   Easily integrates with GitHub webhooks and Actions for automated security PR reviews.

---

## 🔑 Key Features

- 🔎 Static + LLM: Combines deterministic scanners with AI patching.
- 🌐 Multi-Language Support: Python, JavaScript, Java, Go (extendable).
- 💡 RAG-Driven: Fixes guided by best-practice CWE remediation patterns.
- 🧠 Smart Patching: Diff includes only minimal, necessary edits.
- 🎯 Quality Scoring: Fixes rated 0–10 for transparency.
- 🔒 Secure: Verifies GitHub webhook payloads via HMAC signature.
- 🐳 Containerized: Comes with Docker and Docker Compose support.

---

## 📦 Prerequisites

- Docker Desktop *(for container deployment)*
- Python 3.11+ *(for local running)*
- OpenRouter API Key (for Deepseek R1)
- Optional: GitHub Personal Access Token and Webhook Secret

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/Vijay-48/ai-code-security-auditor.git
cd ai-code-security-auditor
````

### 2. Configure your environment

Create and update your `.env`:

```ini
OPENROUTER_API_KEY=sk-...
OPENROUTER_REFERER=http://localhost:8000
OPENROUTER_TITLE="AI Code Security Auditor"
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

### 3. Start the application

**Using Docker Compose**

```bash
docker compose up --build
# App running at http://localhost:8000
```

**Or run locally**

```bash
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🛠 Configuration

| Variable                   | Default                   | Description                               |
| -------------------------- | ------------------------- | ----------------------------------------- |
| `OPENROUTER_API_KEY`       | *(required)*              | API key for Deepseek R1 via OpenRouter    |
| `GITHUB_TOKEN`             | *(optional)*              | Used for commenting on PRs                |
| `GITHUB_WEBHOOK_SECRET`    | *(optional)*              | Secret to verify incoming GitHub webhooks |
| `CHROMA_PERSIST_DIRECTORY` | `./chroma_db`             | Local vector DB storage                   |
| `BANDIT_CONFIG_PATH`       | `./configs/bandit.yaml`   | Custom Bandit rules (optional)            |
| `SEMGREP_RULES_PATH`       | `./configs/semgrep-rules` | Custom Semgrep rules (optional)           |

---

## 📡 Usage

### ✅ Health Check

```bash
GET /health
# Response: { "status": "ok", "version": "1.0.0" }
```

### 🔍 Audit Raw Code

```bash
POST /audit
Content-Type: application/json

{
  "code": "import os\ndef insecure(): os.system('rm -rf /')",
  "language": "python",
  "filename": "danger.py"
}
```

**Response JSON**

```json
{
  "scan_results": { ... },
  "vulnerabilities": [ ... ],
  "remediation_suggestions": [ ... ],
  "patches": [ ... ],
  "assessments": [ ... ]
}
```

---

## 🔁 GitHub Webhook Setup

1. Go to `Settings → Webhooks → Add Webhook`
2. Use:

   * **Payload URL**: `https://your-app.com/webhook/github`
   * **Content type**: `application/json`
   * **Secret**: your `GITHUB_WEBHOOK_SECRET`
3. Enable on events: `Push`, `Pull requests`

Your FastAPI app will verify webhook signatures and auto-audit changed files.

---

## 🧱 Project Structure

```bash
.
├── app/
│   ├── agents/
│   │   └── security_agent.py        # LangGraph security workflow
│   ├── services/
│   │   ├── scanner.py               # Bandit + Semgrep logic
│   │   ├── rag_service.py           # ChromaDB lookup
│   │   └── llm_service.py           # Deepseek R1 integration
│   ├── main.py                      # FastAPI entrypoint
│   └── config.py                    # Pydantic settings
├── data/
│   ├── remediation_patterns/        # Fix template embeddings
│   └── vulnerability_templates/
├── configs/
│   ├── bandit.yaml
│   └── semgrep-rules/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚙️ CI/CD Integration

Example **GitHub Action** for PRs:

```yaml
name: Security Audit

on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Security Auditor
        run: |
          curl -X POST https://your-app.com/audit \
            -H "Content-Type: application/json" \
            -d "$(jq -n '{ code: input, language: "python" }')"
```

---

## 🤝 Contributing

We welcome PRs!

```bash
# Create a feature branch
git checkout -b feat/your-feature

# Add tests in `tests/`
# Then open a PR 🚀
```
