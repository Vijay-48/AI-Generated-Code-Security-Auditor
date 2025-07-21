# Testing GitHub Actions CLI exclusion patterns

## Expected Results:
- Should scan: test_vulnerable_samples.py (detect ~10 vulnerabilities)
- Should exclude: tests_should_be_excluded/* (0 detections from this directory)
- Should exclude: node_modules_should_be_excluded/* (0 detections from this directory)

## Test Command:
```bash
python auditor/cli.py scan \
  --path . \
  --model "agentica-org/deepcoder-14b-preview:free" \
  --output-format github \
  --output-file security-report.md \
  --severity-filter medium \
  --exclude "*/tests_should_be_excluded/*" \
  --exclude "*/node_modules_should_be_excluded/*" \
  --exclude "*/tests/*" \
  --exclude "*/node_modules/*" \
  --exclude "*/.git/*" \
  --exclude "*/chroma_db/*" \
  --exclude "*/myenv/*" \
  --no-advanced
```
