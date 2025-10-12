# 📁 Project Structure

## Overview

This document describes the organization of the AI Code Security Auditor project.

```
AI-Generated-Code-Security-Auditor/
│
├── 📂 .github/                      # GitHub specific files
│   ├── ISSUE_TEMPLATE/              # Issue templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/                   # CI/CD workflows
│   └── PULL_REQUEST_TEMPLATE.md     # PR template
│
├── 📂 app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry
│   ├── config.py                    # Configuration management
│   ├── monitoring.py                # Application monitoring
│   ├── websocket_manager.py         # WebSocket connections
│   ├── celery_app.py                # Celery task queue
│   │
│   ├── 📂 agents/                   # AI agent implementations
│   │   ├── __init__.py
│   │   └── security_agent.py        # Main security analysis agent
│   │
│   ├── 📂 api/                      # API endpoints
│   │   ├── __init__.py
│   │   ├── async_endpoints.py       # Async API routes
│   │   └── endpoints.py             # Sync API routes
│   │
│   ├── 📂 services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── llm_service.py           # LLM integration
│   │   ├── scanner.py               # Security scanning
│   │   ├── analytics_service.py     # Analytics & reporting
│   │   ├── cache_service.py         # Caching layer
│   │   └── rag_service.py           # RAG for remediation
│   │
│   ├── 📂 utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── file_utils.py            # File operations
│   │   ├── format_utils.py          # Output formatting
│   │   └── validation.py            # Input validation
│   │
│   └── 📂 workers/                  # Background workers
│       ├── __init__.py
│       ├── scan_worker.py           # Scan processing
│       └── repo_scan_worker.py      # Repository scanning
│
├── 📂 auditor/                      # CLI package
│   ├── __init__.py
│   └── cli.py                       # Command-line interface
│
├── 📂 cli_visuals/                  # CLI visualization
│   ├── __init__.py
│   ├── charts.py                    # Chart generation
│   ├── formatters.py                # Output formatters
│   ├── heatmap.py                   # Vulnerability heatmaps
│   └── terminal.py                  # Terminal UI components
│
├── 📂 tests/                        # Test files
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── backend_test.py              # Backend tests
│   ├── test_api.py                  # API tests
│   ├── test_scanner.py              # Scanner tests
│   │
│   ├── 📂 demo_files/               # Demo vulnerable code
│   │   ├── demo_sql_injection.py
│   │   ├── demo_command_injection.py
│   │   ├── demo_xss_vulnerabilities.py
│   │   ├── demo_insecure_crypto.py
│   │   ├── demo_insecure_deserialization.py
│   │   ├── demo_path_traversal.py
│   │   ├── demo_javascript_vulns.js
│   │   ├── demo_java_vulns.java
│   │   └── demo_golang_vulns.go
│   │
│   └── 📂 test_files/               # Test fixtures
│       └── sample_vulnerable_code.py
│
├── 📂 docs/                         # Documentation
│   ├── 00-DOCUMENTATION_INDEX.md    # Documentation index
│   ├── 01-PROJECT_OVERVIEW.md       # Project overview
│   ├── 02-LOCAL_SETUP_GUIDE.md      # Setup guide
│   ├── 03-LOCAL_TESTING_GUIDE.md    # Testing guide
│   ├── 04-README.md                 # API documentation
│   ├── 05-CLI_Commands.md           # CLI reference
│   ├── 06-DIRECTORY_STRUCTURE.md    # Directory structure
│   ├── FEATURES.md                  # Feature list
│   ├── COMPLETE_USER_GUIDE.md       # Complete guide
│   └── [other documentation files]
│
├── 📂 scripts/                      # Utility scripts
│   ├── auditor.sh                   # Quick run script
│   ├── setup_hackathon.py           # Hackathon setup
│   ├── deploy_to_pypi.sh            # PyPI deployment
│   └── start_server.sh              # Server startup
│
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 requirements.txt              # Python dependencies
├── 📄 setup.sh                      # Setup script
│
├── 📄 README.md                     # Main README
├── 📄 CONTRIBUTING.md               # Contribution guide
├── 📄 CODE_OF_CONDUCT.md            # Code of conduct
├── 📄 CHANGELOG.md                  # Version history
├── 📄 LICENSE                       # MIT License
│
├── 📄 QUICK_START.md                # Quick start guide
├── 📄 FIX_COMMAND_DOCUMENTATION.md  # Fix command docs
├── 📄 FIXES_APPLIED_REPORT.md       # Fix report example
├── 📄 PROJECT_STRUCTURE.md          # This file
│
└── 📄 [other configuration files]
```

## Key Directories

### `/app` - Core Application
Contains all backend logic, API endpoints, and business services.

**Key Files:**
- `main.py` - FastAPI application
- `config.py` - Configuration management with Pydantic
- `agents/security_agent.py` - AI-powered security analysis
- `services/llm_service.py` - LLM integration layer

### `/auditor` - CLI Package
Command-line interface for the tool.

**Key Files:**
- `cli.py` - All CLI commands (scan, fix, analyze, models, etc.)

### `/tests` - Test Suite
All test files and demo vulnerable code samples.

**Includes:**
- Unit tests
- Integration tests
- Demo files for testing and demonstration

### `/docs` - Documentation
Comprehensive documentation for users and developers.

**Includes:**
- Setup guides
- API documentation
- CLI reference
- Feature documentation

## Important Files

### Configuration
- `.env` - Environment variables (API keys, configuration)
- `.env.example` - Template for environment setup
- `requirements.txt` - Python package dependencies

### Documentation
- `README.md` - Main project documentation
- `CONTRIBUTING.md` - How to contribute
- `CHANGELOG.md` - Version history
- `LICENSE` - MIT License

### Scripts
- `setup.sh` - One-command setup script
- `first_run_setup.py` - Initial setup utility

## Code Organization Principles

### 1. Separation of Concerns
- API layer (`/app/api`)
- Business logic (`/app/services`)
- Data access (`/app/utils`)
- CLI interface (`/auditor`)

### 2. Modularity
Each module has a single responsibility:
- `scanner.py` - Vulnerability scanning
- `llm_service.py` - AI integration
- `analytics_service.py` - Analytics & reporting

### 3. Testability
- Test files mirror source structure
- Mock external dependencies
- Isolated unit tests

### 4. Documentation
- Every module has docstrings
- Complex logic is commented
- README files in key directories

## File Naming Conventions

### Python Files
- `snake_case` for all Python files
- `test_*.py` for test files
- `demo_*.py` for demo/example files

### Documentation
- `SCREAMING_SNAKE_CASE.md` for root docs
- `kebab-case.md` for subdirectory docs
- Numbered prefix for ordered docs (e.g., `01-`, `02-`)

### Configuration
- `.env` for environment variables
- `.example` suffix for templates
- `.gitignore` for Git ignore rules

## Dependencies

### Core Dependencies
- `fastapi` - Web framework
- `click` - CLI framework
- `bandit` - Python security linter
- `semgrep` - Multi-language scanner
- `openai` - OpenAI API client
- `httpx` - Async HTTP client

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatter
- `ruff` - Fast linter
- `mypy` - Type checker

## Entry Points

### CLI
```bash
python -m auditor.cli [command]
```

### API Server
```bash
uvicorn app.main:app --reload
```

### Tests
```bash
pytest tests/
```

## Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `GROQ_API_KEY` or `OPENROUTER_API_KEY` - AI provider keys

**Optional:**
- `DEFAULT_MODEL` - Default AI model
- `API_PORT` - API server port
- `MAX_FILE_SIZE_MB` - Max file size limit

## Adding New Features

### 1. Core Logic
Add to appropriate service in `/app/services/`

### 2. API Endpoint
Add to `/app/api/endpoints.py` or `/app/api/async_endpoints.py`

### 3. CLI Command
Add to `/auditor/cli.py`

### 4. Tests
Add to `/tests/test_*.py`

### 5. Documentation
Update relevant docs in `/docs/` and `README.md`

## Build & Deployment

### Local Development
```bash
bash setup.sh
python -m auditor.cli scan --path tests/demo_sql_injection.py
```

### Docker (if available)
```bash
docker build -t ai-code-auditor .
docker run -it ai-code-auditor
```

### PyPI Package (future)
```bash
pip install ai-code-security-auditor
```

---

## Questions?

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.
