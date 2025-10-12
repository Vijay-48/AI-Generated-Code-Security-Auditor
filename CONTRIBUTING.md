# Contributing to AI Code Security Auditor

Thank you for considering contributing to AI Code Security Auditor! 🎉

## 🌟 How Can I Contribute?

### Reporting Bugs
- Use the GitHub issue tracker
- Follow the bug report template
- Include detailed reproduction steps
- Provide environment details

### Suggesting Features
- Check if feature is already requested
- Use the feature request template
- Explain the use case clearly
- Provide examples if possible

### Code Contributions

#### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI-Generated-Code-Security-Auditor.git
   cd AI-Generated-Code-Security-Auditor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run tests**
   ```bash
   python -m pytest tests/
   ```

#### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Run linters
   black app/ auditor/
   ruff app/ auditor/
   
   # Run tests
   pytest tests/
   
   # Test CLI commands
   python -m auditor.cli scan --path tests/demo_sql_injection.py
   ```

4. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing new feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `perf:` Performance improvements
   - `chore:` Maintenance tasks

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

## 📋 Code Style Guidelines

### Python
- Follow PEP 8
- Use type hints where appropriate
- Document functions with docstrings
- Keep functions focused and small
- Maximum line length: 100 characters

### Example
```python
def scan_file(file_path: str, model: str = "llama-3.1-8b-instant") -> Dict[str, Any]:
    """Scan a file for security vulnerabilities.
    
    Args:
        file_path: Path to the file to scan
        model: AI model to use for analysis
        
    Returns:
        Dictionary containing scan results with vulnerabilities
        
    Raises:
        FileNotFoundError: If file_path doesn't exist
    """
    # Implementation here
    pass
```

## 🧪 Testing Guidelines

- Write tests for new features
- Maintain test coverage above 80%
- Use meaningful test names
- Test edge cases
- Mock external API calls

Example test:
```python
def test_scan_detects_sql_injection():
    """Test that scanner detects SQL injection vulnerabilities."""
    code = "cursor.execute(f'SELECT * FROM users WHERE id={user_id}')"
    result = scan_code(code, language='python')
    assert any('SQL injection' in v['title'] for v in result['vulnerabilities'])
```

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions/classes
- Update relevant documentation in `/docs`
- Include examples in documentation
- Keep docs clear and concise

## 🔍 Review Process

1. All PRs require review from maintainers
2. CI checks must pass
3. Code coverage should not decrease
4. Documentation must be updated
5. Breaking changes need discussion

## 💬 Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Focus on the code, not the person
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)

## 🎯 Priority Areas

We especially welcome contributions in:
- [ ] Support for new programming languages
- [ ] Additional security rule patterns
- [ ] Performance optimizations
- [ ] Documentation improvements
- [ ] Test coverage expansion
- [ ] Bug fixes
- [ ] UI/UX enhancements

## 📞 Getting Help

- GitHub Issues: For bugs and features
- Discussions: For questions and ideas
- Discord: [Coming soon]
- Email: [maintainer email]

## 🏆 Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for making AI Code Security Auditor better! 🚀
