#!/bin/bash
# AI Code Security Auditor CLI Wrapper

# Set environment variables
export OPENROUTER_API_KEY="*************************************************"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1/chat/completions"

# Run the CLI with all passed arguments
cd /app
python -m auditor.cli "$@"
