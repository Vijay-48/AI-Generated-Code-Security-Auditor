# 🛡️ AI-Generated Code Security Auditor

An automated security auditing service that scans code snippets or repository events, detects vulnerabilities, and generates ready-to-apply git diffs to fix them—powered by static analysis, retrieval-augmented generation (RAG), and the Deepseek R1 LLM via OpenRouter.

---

## 🚀 What It Does

1. **Ingest Code**  
   - Accepts raw code via REST API or GitHub push/PR webhooks.

2. **Static Analysis**  
   - Uses Bandit (for Python) and Semgrep (multi-language) to detect vulnerabilities.

3. **Normalize Findings**  
   - Unifies scanner output into a common schema: `ID`, `title`, `CWE`, `severity`, `snippet`, etc.

4. **Retrieval-Augmented Remediation**  
   - Performs RAG lookups from ChromaDB (seeded with CWE-to-fix patterns).

5. **Diff Generation**  
   - Prompts Deepseek R1 via OpenRouter to generate minimal, commented `git diff` patches.

6. **Patch Assessment**  
   - LLM scores each fix on correctness, completeness, code quality, and performance impact.

7. **Response Aggregation**  
   - Returns a full JSON payload: scan results, vulnerability list, fix suggestions, diffs, and assessments.

8. **CI/CD & GitHub Integration**  
   - Can auto-comment on pull requests or apply fixes once approved via GitHub Actions/webhooks.

---

## 🔑 Key Features

- ✅ **Multi-Language Support**: Python, JavaScript, Java, Go (easily extendable).
- 🧠 **Static + AI-Driven**: Combines deterministic analysis with LLM diff generation.
- 📚 **Retrieval-Augmented Generation**: Uses vector DB of secure remediation templates.
- 🔧 **Autonomous Patching**: Minimal and readable git diffs with inline comments.
- 📊 **Quality Scoring**: Each patch rated 0–10 for transparency.
- 🔐 **Secure Webhooks**: GitHub webhook payload verification via HMAC.
- 📦 **Containerized**: Dockerfile + Compose for simple deployment.

---

## 📦 Prerequisites

- Docker Desktop (for containerized deployments)  
- Python 3.11+ (for local development)  
- OpenRouter API key (for Deepseek R1)  
- (Optional) GitHub Personal Access Token & Webhook Secret  

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ai-code-security-auditor.git
cd ai-code-security-auditor
````

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in required values:

```ini
OPENROUTER_API_KEY=sk-...
OPENROUTER_REFERER=http://localhost:8000
OPENROUTER_TITLE="AI Code Security Auditor"
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

### 3. With Docker Compose

```bash
docker compose up --build
```

The app will be running at: [http://localhost:8000](http://localhost:8000)

### 4. Without Docker

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🛠 Configuration

You can modify settings in `app/config.py` or via `.env`.

| Variable                   | Default                    | Description                                |
| -------------------------- | -------------------------- | ------------------------------------------ |
| `OPENROUTER_API_KEY`       | *none*                     | API key for Deepseek R1 via OpenRouter     |
| `OPENROUTER_REFERER`       | `http://localhost:8000`    | HTTP-Referer header for OpenRouter         |
| `OPENROUTER_TITLE`         | `AI Code Security Auditor` | Title header for OpenRouter ranking        |
| `GITHUB_TOKEN`             | *none*                     | GitHub token for API interactions          |
| `GITHUB_WEBHOOK_SECRET`    | *none*                     | Secret to verify GitHub webhook payloads   |
| `CHROMA_PERSIST_DIRECTORY` | `./chroma_db`              | Directory to persist Chroma vector store   |
| `BANDIT_CONFIG_PATH`       | `./configs/bandit.yaml`    | Optional custom Bandit rules file          |
| `SEMGREP_RULES_PATH`       | `./configs/semgrep-rules`  | Optional custom Semgrep rule set directory |

---

## 📡 Usage

### Health Check

```http
GET /health
```

**Response:**

```json
{ "status": "ok", "version": "1.0.0" }
```

---

### Audit Code

```http
POST /audit
Content-Type: application/json
```

**Body:**

```json
{
  "code": "import os\ndef insecure(): os.system('rm -rf /')",
  "language": "python",
  "filename": "danger.py"
}
```

**Response:**

```json
{
  "scan_results": { … },
  "vulnerabilities": [ … ],
  "remediation_suggestions": [ … ],
  "patches": [ … ],
  "assessments": [ … ]
}
```

---

### GitHub Webhook

In your GitHub repository:

**Settings → Webhooks → Add webhook**

* **Payload URL**: `https://ai-security.viam.com/webhook/github`
* **Content type**: `application/json`
* **Secret**: Your `GITHUB_WEBHOOK_SECRET`
* **Events**: *Pushes*, *Pull requests*

The FastAPI app will handle `/webhook/github`, verify the `X-Hub-Signature-256`, and then audit changed files.

---

## 📁 Project Structure

```bash
.
├── app/
│   ├── agents/
│   │   └── security_agent.py        # LangGraph logic
│   ├── services/
│   │   ├── scanner.py               # Bandit & Semgrep
│   │   ├── rag_service.py           # ChromaDB RAG lookup
│   │   └── llm_service.py           # Deepseek R1 via OpenRouter
│   ├── main.py                      # FastAPI entrypoint
│   └── config.py                    # Pydantic settings
├── data/
│   ├── remediation_patterns/        # Optional fix templates
│   └── vulnerability_templates/
├── configs/
│   ├── bandit.yaml                  # Bandit config override
│   └── semgrep-rules/               # Custom Semgrep rules
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔄 CI/CD Integration

Example GitHub Actions workflow:

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
          curl -X POST https://ai-security.viam.com/audit \
            -H "Content-Type: application/json" \
            -d "$(jq -n '{ code: input, language: "python" }')"
```

You can also auto-comment on PRs using the `GITHUB_TOKEN` and the JSON response.

---

## 🤝 Contributing

1. Fork and clone the repo.
2. Create a branch: `git checkout -b feat/your-feature`
3. Add tests under `tests/`
4. Submit a pull request describing your change.
