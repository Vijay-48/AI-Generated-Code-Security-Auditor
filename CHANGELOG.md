# Changelog

All notable changes to AI Code Security Auditor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-12

### 🎉 Major Release - Auto-Fix Capability

### Added
- **Automatic Fix Application** - `--apply` flag to automatically apply security patches to files
- **Automatic Backup Creation** - Creates `.backup` files before applying fixes
- **Interactive Mode** - `--interactive` flag to review each fix before applying
- **Targeted Fixes** - `--vuln-id` flag to fix specific vulnerabilities
- Smart code matching using multiple strategies
- Line-number based replacement with indentation preservation
- Comprehensive fix command documentation
- Enhanced patch parsing for AI-generated diffs
- Support for git diff format patches

### Changed
- Improved `fix` command now applies changes instead of just reporting
- Enhanced diff extraction logic
- Better error handling and user feedback
- Improved CLI output formatting

### Fixed
- Fixed JSON parsing issues in AI responses
- Fixed code matching for complex patterns
- Improved vulnerable code detection accuracy

### Documentation
- Added `FIX_COMMAND_DOCUMENTATION.md` with 10+ usage examples
- Added `FIXES_APPLIED_REPORT.md` with before/after comparisons
- Updated README with new fix command options
- Added comprehensive PPT slide content

## [1.5.0] - 2025-09-XX

### Added
- GroqCloud integration for ultra-fast AI inference
- OpenRouter API support for multi-model access
- Dual API provider with automatic fallback
- 20+ AI models support
- Enhanced model routing system

### Changed
- Simplified configuration with `.env` file
- Improved CLI interface
- Better error messages

## [1.0.0] - 2025-08-XX

### Added
- Initial release
- CLI interface for security scanning
- Bandit integration for Python security linting
- Semgrep integration for multi-language analysis
- Secret detection capabilities
- Multiple output formats (JSON, Table, SARIF, GitHub Actions)
- AI-powered vulnerability analysis
- FastAPI server for API access
- Comprehensive documentation

---

## Version History

- **v2.0.0** - Auto-fix capability, enhanced CLI
- **v1.5.0** - Multi-AI provider support
- **v1.0.0** - Initial release

---

## Upgrade Guide

### From 1.x to 2.0

**New Features:**
```bash
# Old way (report only)
python -m auditor.cli fix --path app.py

# New way (apply fixes)
python -m auditor.cli fix --path app.py --apply --backup
```

**Breaking Changes:**
- None - fully backward compatible

**Migration Steps:**
1. Pull latest code
2. Install dependencies: `pip install -r requirements.txt`
3. Update .env file if needed
4. Run tests: `pytest tests/`
5. Try new fix command: `python -m auditor.cli fix --help`

---

For full details, see the [GitHub Releases](https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor/releases).
