# 📁 Project Directory Structure

## 🏗️ Organized File Structure Overview

The project has been reorganized for better maintainability and clarity. Here's the complete directory structure:

```
/app/
├── 📚 docs/                          # 📖 All documentation files
│   ├── README.md                     # Main project documentation
│   ├── LOCAL_SETUP_GUIDE.md         # Complete setup instructions
│   ├── PROJECT_OVERVIEW.md          # Executive summary & features
│   ├── CHANGELOG.md                  # Version history
│   ├── CLI_Commands.md               # CLI reference guide
│   ├── test_result.md                # Testing results and protocols
│   ├── CICD_PIPELINE_TEST_RESULTS.md # CI/CD testing documentation
│   ├── FINAL_REGRESSION_TEST_REPORT.md # Regression testing results
│   ├── GH_ACTIONS_VALIDATION_REPORT.md # GitHub Actions validation
│   ├── GITHUB_ACTIONS_SIMULATION_RESULT.md # CI/CD simulation results
│   ├── LOCAL_TESTING_GUIDE.md       # Local testing instructions
│   ├── PHASE_7C_IMPLEMENTATION.md   # Phase 7C development notes
│   ├── gh_actions_test_plan.md      # GitHub Actions test planning
│   ├── security-report.md           # Security analysis report
│   ├── security-report-cicd.md      # CI/CD security report
│   └── README_backup.md             # Backup documentation
│
├── 🧪 test_files/                    # 🔬 All testing and debugging files
│   ├── 📊 test_data/                # Test data and sample files
│   │   ├── test_payload.json        # API test payloads
│   │   ├── test_payload_detailed.json # Detailed test scenarios
│   │   ├── test_exact_payload.json  # Exact match testing
│   │   ├── advanced_analysis_test.json # Advanced feature tests
│   │   ├── regression_test_results.json # Regression test data
│   │   ├── test_comprehensive_javascript.js # JS vulnerability samples
│   │   ├── test_js_vulnerabilities.js # JavaScript security tests
│   │   └── ...
│   │
│   ├── 🔧 debug_scripts/            # Debug and demo scripts
│   │   ├── debug_agent.py           # Agent debugging tools
│   │   ├── debug_endpoint.py        # API endpoint testing
│   │   ├── debug_fastapi_agent.py   # FastAPI debugging
│   │   ├── debug_scanner.py         # Scanner debugging utilities
│   │   ├── final_validation.py      # Final validation scripts
│   │   ├── phase5_final_demo.py     # Phase 5 demonstration
│   │   ├── phase9_demo.py           # Phase 9 features demo
│   │   └── visual_demo.py           # Visual components demo
│   │
│   ├── 📱 sample_code/              # Code samples for testing
│   ├── test_chroma_db/              # Test database files
│   ├── tests_should_be_excluded/    # Test exclusion examples
│   ├── node_modules_should_be_excluded/ # Node.js exclusion examples
│   ├── backend_test.py              # Backend functionality tests
│   ├── comprehensive_backend_test.py # Comprehensive backend testing
│   ├── comprehensive_websocket_demo.py # WebSocket functionality demo
│   ├── test_api_endpoints.py        # API endpoint testing
│   ├── test_cli_scan.py             # CLI scanning tests
│   ├── test_comprehensive_python.py # Python security tests
│   ├── test_edge_case_*.py          # Edge case testing scripts
│   ├── test_multi_model.py          # Multi-model AI testing
│   ├── test_openrouter.py           # OpenRouter integration tests
│   ├── test_secrets.py              # Secret detection testing
│   ├── test_vulnerable.py           # Vulnerability detection tests
│   ├── test_vulnerable_samples.py   # Sample vulnerable code
│   ├── test_websocket_*.py          # WebSocket testing utilities
│   └── quick_websocket_test.py      # Quick WebSocket validation
│
├── 🚀 scripts/                      # 🛠️ Deployment and utility scripts
│   ├── deploy.sh                    # Deployment automation
│   ├── docker-entrypoint.sh         # Docker container entry point
│   └── example_session.sh           # Usage example session
│
├── 🗂️ temp_files/                   # 🗑️ Temporary and generated files
│   ├── analytics.db                 # Analytics database (generated)
│   ├── dump.rdb                     # Redis dump file
│   ├── =0.4.6, =8.0.0, etc.       # Temporary build artifacts
│   ├── errors/                      # Error logs and debugging info
│   └── myenv/                       # Virtual environment (if present)
│
├── 🏢 app/                          # 🚀 Main application code
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   ├── monitoring.py                # Monitoring and metrics
│   ├── websocket_manager.py         # WebSocket connection management
│   ├── celery_app.py               # Celery task queue configuration
│   ├── agents/                      # AI agent implementations
│   ├── api/                         # API endpoint definitions
│   ├── models/                      # Data models and schemas
│   ├── services/                    # Business logic services
│   ├── utils/                       # Utility functions
│   └── workers/                     # Background task workers
│
├── 🖥️ auditor/                      # 💻 CLI application
│   ├── __init__.py                  # Package initialization
│   └── cli.py                       # Command-line interface
│
├── ✅ tests/                        # 🧪 Unit and integration tests
│   ├── conftest.py                  # Test configuration
│   ├── test_api.py                  # API testing
│   ├── test_agent.py                # Agent testing
│   ├── test_llm_service.py         # LLM service testing
│   ├── test_rag_service.py         # RAG service testing
│   └── test_scanner.py             # Scanner service testing
│
├── 🎨 cli_visuals/                  # 📊 CLI visualization components
│   ├── charts.py                    # Chart generation
│   ├── formatters.py               # Output formatting
│   ├── heatmap.py                  # Heatmap visualization
│   └── terminal.py                 # Terminal display utilities
│
├── 🐳 docker/                       # 🐋 Docker configuration
│   ├── docker-compose.test.yml     # Testing environment
│   ├── docker-compose.dev.yml      # Development environment
│   ├── entrypoint.sh               # Container entry script
│   └── seed_db.py                  # Database seeding
│
├── 📊 monitoring/                   # 📈 Monitoring configuration
│   └── prometheus.yml              # Prometheus metrics config
│
├── 🌐 nginx/                        # ⚡ Web server configuration
│   └── nginx.conf                  # Nginx configuration
│
├── 💾 chroma_db/                    # 🗄️ Vector database storage
├── 📦 ai_code_security_auditor.egg-info/ # Python package metadata
├── 🏠 Root Configuration Files      # 📋 Project configuration
│   ├── pyproject.toml              # Python project configuration
│   ├── requirements.txt            # Python dependencies
│   ├── docker-compose.yml          # Production Docker setup
│   ├── docker-compose.prod.yml     # Production Docker configuration
│   ├── Dockerfile                  # Container build instructions
│   ├── Dockerfile.prod             # Production container build
│   ├── .env                        # Environment variables
│   ├── .env.example               # Environment template
│   ├── LICENSE                     # Project license
│   └── .dockerignore              # Docker ignore patterns
```

## 🎯 Directory Purpose Guide

### 📚 `docs/` - Documentation Hub
All project documentation in one place:
- **Setup guides** for local development
- **API documentation** and references  
- **Testing reports** and validation results
- **Feature specifications** and implementation notes
- **Change logs** and version history

### 🧪 `test_files/` - Testing & Development
Comprehensive testing infrastructure:
- **Test data**: JSON payloads, sample vulnerable code
- **Debug scripts**: Development and debugging utilities  
- **Edge cases**: Boundary condition testing
- **Integration tests**: Multi-component testing scenarios
- **Performance tests**: Load and stress testing tools

### 🚀 `scripts/` - Automation & Deployment
Production deployment and utility scripts:
- **Deployment automation** for various environments
- **Container management** and orchestration
- **Usage examples** and demonstration scripts

### 🗂️ `temp_files/` - Generated & Temporary
System-generated and temporary files:
- **Build artifacts** from development processes
- **Database snapshots** and cache dumps
- **Virtual environments** (when created locally)
- **Error logs** and debugging information

### 🏢 `app/` - Core Application
The heart of the AI Security Auditor:
- **FastAPI backend** with REST API endpoints
- **AI agent implementations** with multi-model support
- **Security services** (scanning, analysis, reporting)
- **Business logic** and data processing

### 🖥️ `auditor/` - CLI Interface  
Professional command-line tools:
- **15+ CLI commands** for security scanning
- **Rich terminal interface** with progress bars
- **Multiple output formats** (JSON, SARIF, GitHub Actions)
- **Advanced analytics** and reporting features

## 🔄 Migration Notes

### Files Moved:
- ✅ **16 .md files** → `docs/`
- ✅ **25+ test files** → `test_files/`  
- ✅ **Test data files** → `test_files/test_data/`
- ✅ **Debug scripts** → `test_files/debug_scripts/`
- ✅ **Shell scripts** → `scripts/`
- ✅ **Temporary files** → `temp_files/`

### Benefits of Organization:
- 🎯 **Clear separation** between production code and testing
- 📚 **Centralized documentation** for easy maintenance
- 🔍 **Better discoverability** of files and resources
- 🚀 **Cleaner root directory** for professional appearance
- 🛡️ **Improved security** by separating test data from production

## 🚀 Usage After Reorganization

### Documentation Access:
```bash
# View main documentation
cat docs/README.md
cat docs/LOCAL_SETUP_GUIDE.md
cat docs/PROJECT_OVERVIEW.md
```

### Testing:
```bash
# Run test scripts
python test_files/backend_test.py
python test_files/debug_scripts/phase9_demo.py
```

### Deployment:
```bash
# Use deployment scripts
bash scripts/deploy.sh
bash scripts/example_session.sh
```

All core functionality remains unchanged - only file locations have been organized for better project management! 🎉