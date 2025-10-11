#!/bin/bash
# AI Code Security Auditor CLI Wrapper

# Set environment variables
export OPENROUTER_API_KEY="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"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1/chat/completions"

# Run the CLI with all passed arguments
cd /app
python -m auditor.cli "$@"