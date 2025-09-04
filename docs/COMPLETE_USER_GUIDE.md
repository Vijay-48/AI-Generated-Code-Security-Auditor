# 🛡️ AI Code Security Auditor - Complete User Guide

> **The definitive guide to installing, configuring, and using the AI Code Security Auditor**

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation)
3. [Configuration](#-configuration)
4. [Basic Usage](#-basic-usage)
5. [Advanced Features](#-advanced-features)
6. [API Server](#-api-server)
7. [Command Reference](#-command-reference)
8. [Troubleshooting](#-troubleshooting)
9. [Best Practices](#-best-practices)

---

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor.git
cd AI-Generated-Code-Security-Auditor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API key (get from https://openrouter.ai/)
export OPENROUTER_API_KEY="your-api-key-here"

# 4. Test the installation
python -m auditor.cli --help

# 5. Run your first scan
echo 'import os; os.system(user_input)' > test.py
python -m auditor.cli scan --path test.py
rm test.py
```

---

## 📦 Installation

### Prerequisites

- **Python 3.11+** (required)
- **4GB RAM** minimum (8GB+ recommended)
- **2GB disk space** for models and data
- **Internet connection** for AI model access

### Method 1: Development Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor.git
cd AI-Generated-Code-Security-Auditor

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m auditor.cli --help
```

### Method 2: Direct Installation

```bash
# Install required packages directly
pip install fastapi uvicorn click requests pydantic
pip install bandit semgrep safety
pip install chromadb sentence-transformers
pip install redis celery
pip install pandas matplotlib seaborn

# Clone and use
git clone https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor.git
cd AI-Generated-Code-Security-Auditor
```

### Verify Installation

```bash
# Test CLI
python -m auditor.cli --help

# Test imports
python -c "
from app.services.scanner import SecurityScanner
from app.services.rag_service import RAGRemediationService
from app.services.llm_service import LLMService
print('✅ All imports successful')
"
```

---

## ⚙️ Configuration

### 1. API Key Setup (Required)

The auditor requires an OpenRouter API key for AI functionality.

#### Get Your API Key
1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Create a free account
3. Navigate to "API Keys"
4. Generate a new key

#### Set the API Key

**Option A: Environment Variable (Recommended)**
```bash
# Linux/macOS
export OPENROUTER_API_KEY="your-api-key-here"
echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Windows
set OPENROUTER_API_KEY=your-api-key-here
```

**Option B: .env File**
```bash
# Create .env file in project root
echo 'OPENROUTER_API_KEY=your-api-key-here' > .env
```

### 2. Optional: Redis Setup (For Better Performance)

Redis provides caching and improves performance significantly.

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

**Configure Redis:**
```bash
export REDIS_URL="redis://localhost:6379/0"
```

---

## 🔍 Basic Usage

### 1. Your First Security Scan

```bash
# Create a test file with vulnerabilities
cat > vulnerable_example.py << 'EOF'
import os
import subprocess
import sqlite3

# SQL Injection vulnerability
def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return conn.execute(query).fetchall()

# Command Injection vulnerability  
def run_command(user_input):
    os.system(user_input)
    
# Shell Injection vulnerability
def execute_cmd(cmd):
    subprocess.call(cmd, shell=True)

# Hardcoded secret
API_KEY = "sk-1234567890abcdef"
EOF

# Scan the file
python -m auditor.cli scan --path vulnerable_example.py

# Clean up
rm vulnerable_example.py
```

### 2. Scan a Directory

```bash
# Scan current directory
python -m auditor.cli scan --path .

# Scan with filters
python -m auditor.cli scan \
  --path ./src \
  --severity-filter high \
  --exclude "*/tests/*" \
  --exclude "*/node_modules/*"
```

### 3. Different Output Formats

```bash
# Table format (default)
python -m auditor.cli scan --path . --output-format table

# JSON format for automation
python -m auditor.cli scan --path . --output-format json --output-file results.json

# GitHub Actions format
python -m auditor.cli scan --path . --output-format github --output-file security-report.md

# SARIF format for security tools
python -m auditor.cli scan --path . --output-format sarif --output-file security.sarif
```

### 4. Analyze Code Directly

```bash
# Analyze a code snippet
python -m auditor.cli analyze \
  --code "import os; os.system(user_input)" \
  --language python

# With specific model
python -m auditor.cli analyze \
  --code "SELECT * FROM users WHERE id = " + userId \
  --language javascript \
  --model "meta-llama/llama-3.3-70b-instruct:free"
```

---

## 🚀 API Server

### Start the Server

```bash
# Method 1: Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Method 2: Background with logging
uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# Method 3: Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Test the Server

```bash
# Health check
curl http://localhost:8000/health

# List available models
curl http://localhost:8000/models

# Audit code via API
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os; os.system(user_input)",
    "language": "python"
  }'
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/models` | GET | List available AI models |
| `/audit` | POST | Audit code snippet |
| `/scan` | POST | Scan file or directory |
| `/analytics/trends` | GET | Vulnerability trends |
| `/analytics/summary` | GET | Security summary |

---

## 🎯 Advanced Features

### 1. Multi-Model Analysis

```bash
# Enable advanced analysis with multiple models
python -m auditor.cli scan --path . --advanced

# Use specific model for different tasks
python -m auditor.cli scan \
  --path . \
  --model "agentica-org/deepcoder-14b-preview:free"  # Best for code patches
```

### 2. Adding New AI Models

The AI Code Security Auditor supports multiple model providers and can be extended to include new models.

#### Current Model Architecture

The system uses a flexible model architecture with these components:

- **ModelType class**: Defines available models in `app/services/llm_client.py`
- **LLMService**: Manages model selection and API calls
- **Configuration**: Models configured via environment variables

#### A. Adding OpenAI Models

**Step 1: Install OpenAI SDK**
```bash
pip install openai
```

**Step 2: Create OpenAI Client**
Create `app/services/openai_client.py`:

```python
import os
import openai
from typing import List, Dict, Any

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    def query_openai(self, messages: List[Dict], model: str = "gpt-4", 
                     max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """Query OpenAI API with messages"""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not configured")
            
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

# Available OpenAI models
class OpenAIModels:
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
```

**Step 3: Update ModelType Class**
Edit `app/services/llm_client.py`:

```python
class ModelType:
    """Recommended models for different use cases"""
    # OpenRouter models (existing)
    DEEPCODER = "agentica-org/deepcoder-14b-preview:free"
    KIMI = "moonshotai/kimi-dev-72b:free"
    QWEN = "qwen/qwen-2.5-coder-32b-instruct:free"
    LLAMA = "meta-llama/llama-3.3-70b-instruct:free"
    
    # OpenAI models (new)
    OPENAI_GPT4 = "openai/gpt-4"
    OPENAI_GPT4_TURBO = "openai/gpt-4-turbo-preview"
    OPENAI_GPT35_TURBO = "openai/gpt-3.5-turbo"
    OPENAI_GPT4O = "openai/gpt-4o"
    OPENAI_GPT4O_MINI = "openai/gpt-4o-mini"
```

**Step 4: Update LLMService**
Edit `app/services/llm_service.py`:

```python
from app.services.openai_client import OpenAIClient

class LLMService:
    def __init__(self):
        # Existing OpenRouter setup
        self.openrouter_headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.OPENROUTER_REFERER,
            "X-Title": settings.OPENROUTER_TITLE
        }
        
        # New OpenAI client
        self.openai_client = OpenAIClient()
        
    async def _call_model(self, messages, max_tokens, temperature, model=None):
        """Universal model calling method"""
        if model is None:
            model = self.patch_model
            
        # Route to appropriate provider
        if model.startswith("openai/"):
            openai_model = model.replace("openai/", "")
            return await self._call_openai(messages, max_tokens, temperature, openai_model)
        else:
            return await self._call_openrouter(messages, max_tokens, temperature, model)
    
    async def _call_openai(self, messages, max_tokens, temperature, model):
        """Call OpenAI API"""
        import asyncio
        # Run OpenAI call in thread pool since it's not async
        loop = asyncio.get_event_loop()
        response_content = await loop.run_in_executor(
            None, 
            self.openai_client.query_openai,
            messages, model, max_tokens, temperature
        )
        return {"choices": [{"message": {"content": response_content}}]}
```

**Step 5: Configuration**
Add to your `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Update model list to include OpenAI models
OPENROUTER_MODELS=agentica-org/deepcoder-14b-preview:free,moonshotai/kimi-dev-72b:free,qwen/qwen-2.5-coder-32b-instruct:free,meta-llama/llama-3.3-70b-instruct:free,openai/gpt-4,openai/gpt-4-turbo-preview,openai/gpt-3.5-turbo
```

**Step 6: Usage**
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"

# Use OpenAI models
python -m auditor.cli scan --path . --model "openai/gpt-4"
python -m auditor.cli analyze --code "import os; os.system(cmd)" --language python --model "openai/gpt-4-turbo-preview"
```

#### B. Adding Offline/Local Models

**Option 1: Using Ollama (Recommended)**

**Step 1: Install Ollama**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**Step 2: Download Models**
```bash
# Download popular code models
ollama pull codellama:7b
ollama pull codellama:13b
ollama pull deepseek-coder:6.7b
ollama pull starcoder:7b
ollama pull phind-codellama:34b
```

**Step 3: Create Ollama Client**
Create `app/services/ollama_client.py`:

```python
import requests
import json
from typing import List, Dict

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
    def query_ollama(self, messages: List[Dict], model: str = "codellama:7b",
                     max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """Query local Ollama model"""
        
        # Convert messages to single prompt for Ollama
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            },
            "stream": False
        }
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["response"]
    
    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert OpenAI-style messages to single prompt"""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"
    
    def list_models(self) -> List[str]:
        """List available local models"""
        response = requests.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        return [model["name"] for model in response.json()["models"]]

# Available Ollama models
class OllamaModels:
    CODELLAMA_7B = "codellama:7b"
    CODELLAMA_13B = "codellama:13b"
    DEEPSEEK_CODER = "deepseek-coder:6.7b"
    STARCODER = "starcoder:7b"
    PHIND_CODELLAMA = "phind-codellama:34b"
```

**Step 4: Update ModelType**
```python
class ModelType:
    # Existing models...
    
    # Ollama local models
    OLLAMA_CODELLAMA_7B = "ollama/codellama:7b"
    OLLAMA_CODELLAMA_13B = "ollama/codellama:13b"
    OLLAMA_DEEPSEEK = "ollama/deepseek-coder:6.7b"
    OLLAMA_STARCODER = "ollama/starcoder:7b"
```

**Step 5: Update LLMService**
```python
from app.services.ollama_client import OllamaClient

class LLMService:
    def __init__(self):
        # Existing setup...
        self.ollama_client = OllamaClient()
        
    async def _call_model(self, messages, max_tokens, temperature, model=None):
        """Universal model calling method"""
        if model is None:
            model = self.patch_model
            
        # Route to appropriate provider
        if model.startswith("openai/"):
            openai_model = model.replace("openai/", "")
            return await self._call_openai(messages, max_tokens, temperature, openai_model)
        elif model.startswith("ollama/"):
            ollama_model = model.replace("ollama/", "")
            return await self._call_ollama(messages, max_tokens, temperature, ollama_model)
        else:
            return await self._call_openrouter(messages, max_tokens, temperature, model)
    
    async def _call_ollama(self, messages, max_tokens, temperature, model):
        """Call local Ollama model"""
        import asyncio
        loop = asyncio.get_event_loop()
        response_content = await loop.run_in_executor(
            None,
            self.ollama_client.query_ollama,
            messages, model, max_tokens, temperature
        )
        return {"choices": [{"message": {"content": response_content}}]}
```

**Option 2: Using Hugging Face Transformers**

**Step 1: Install Dependencies**
```bash
pip install transformers torch accelerate bitsandbytes
```

**Step 2: Create Local Model Client**
Create `app/services/local_model_client.py`:

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Dict
import os

class LocalModelClient:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self, model_name: str, model_path: str = None):
        """Load a local model"""
        if model_name in self.models:
            return
            
        try:
            if model_path:
                # Load from local path
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
            else:
                # Download from Hugging Face
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
            
            self.tokenizers[model_name] = tokenizer
            self.models[model_name] = model
            print(f"✅ Loaded model: {model_name}")
            
        except Exception as e:
            print(f"❌ Failed to load model {model_name}: {e}")
            raise
    
    def query_local_model(self, messages: List[Dict], model_name: str,
                         max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """Query local model"""
        if model_name not in self.models:
            self.load_model(model_name)
        
        tokenizer = self.tokenizers[model_name]
        model = self.models[model_name]
        
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages, tokenizer)
        
        # Generate response
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        return response.strip()
    
    def _messages_to_prompt(self, messages: List[Dict], tokenizer) -> str:
        """Convert messages to model-specific prompt format"""
        # This can be customized per model
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"### System:\n{content}")
            elif role == "user":
                prompt_parts.append(f"### User:\n{content}")
            elif role == "assistant":
                prompt_parts.append(f"### Assistant:\n{content}")
        
        prompt_parts.append("### Assistant:\n")
        return "\n\n".join(prompt_parts)

# Popular local code models
class LocalModels:
    CODELLAMA_7B = "codellama/CodeLlama-7b-Instruct-hf"
    CODELLAMA_13B = "codellama/CodeLlama-13b-Instruct-hf"
    STARCODER = "bigcode/starcoder"
    DEEPSEEK_CODER = "deepseek-ai/deepseek-coder-6.7b-instruct"
    CODE_T5 = "Salesforce/codet5p-770m"
```

**Step 3: Configuration**
Add to your `.env`:

```env
# Local model configuration
LOCAL_MODELS_PATH=/path/to/your/models
USE_GPU=true
MODEL_CACHE_DIR=./model_cache

# Add local models to available models
OPENROUTER_MODELS=agentica-org/deepcoder-14b-preview:free,local/codellama-7b,local/starcoder,local/deepseek-coder
```

**Step 4: Usage**
```bash
# Use local models (no API key needed)
python -m auditor.cli scan --path . --model "ollama/codellama:7b"
python -m auditor.cli scan --path . --model "local/starcoder"

# Check available local models
python -c "
from app.services.ollama_client import OllamaClient
client = OllamaClient()
print('Available Ollama models:', client.list_models())
"
```

#### C. Adding Custom Model Providers

**Step 1: Create Provider Interface**
Create `app/services/base_model_provider.py`:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseModelProvider(ABC):
    """Base class for model providers"""
    
    @abstractmethod
    async def query_model(self, messages: List[Dict], model: str, 
                         max_tokens: int, temperature: float) -> str:
        """Query the model provider"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models"""
        pass
    
    @abstractmethod
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get model information"""
        pass
```

**Step 2: Implement Custom Provider**
Example for Anthropic Claude:

```python
import anthropic
from app.services.base_model_provider import BaseModelProvider

class AnthropicProvider(BaseModelProvider):
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def query_model(self, messages: List[Dict], model: str = "claude-3-sonnet-20240229",
                         max_tokens: int = 2000, temperature: float = 0.1) -> str:
        """Query Anthropic Claude"""
        # Convert OpenAI format to Anthropic format
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=user_messages
        )
        
        return response.content[0].text
    
    def list_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        model_info = {
            "claude-3-opus-20240229": {
                "name": "Claude 3 Opus",
                "description": "Most capable model for complex tasks",
                "context_length": 200000,
                "use_case": "complex_analysis"
            },
            "claude-3-sonnet-20240229": {
                "name": "Claude 3 Sonnet", 
                "description": "Balanced performance and speed",
                "context_length": 200000,
                "use_case": "general_purpose"
            }
        }
        return model_info.get(model, {})
```

#### D. Model Management Commands

Add these commands to your CLI for model management:

**Step 1: Create Model Management CLI**
Create `app/cli/model_commands.py`:

```python
import click
from app.services.ollama_client import OllamaClient
from app.services.local_model_client import LocalModelClient

@click.group()
def models():
    """Model management commands"""
    pass

@models.command()
def list_local():
    """List available local models"""
    try:
        ollama_client = OllamaClient()
        ollama_models = ollama_client.list_models()
        
        click.echo("🤖 Available Local Models:")
        click.echo("=" * 50)
        
        if ollama_models:
            click.echo("\n📦 Ollama Models:")
            for model in ollama_models:
                click.echo(f"  • {model}")
        else:
            click.echo("  No Ollama models found. Install with: ollama pull <model>")
            
    except Exception as e:
        click.echo(f"❌ Error listing models: {e}")

@models.command()
@click.argument('model_name')
def download(model_name):
    """Download a model via Ollama"""
    try:
        import subprocess
        click.echo(f"📥 Downloading {model_name}...")
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"✅ Successfully downloaded {model_name}")
        else:
            click.echo(f"❌ Failed to download {model_name}: {result.stderr}")
    except Exception as e:
        click.echo(f"❌ Error downloading model: {e}")

@models.command()
@click.argument('model_name')
def info(model_name):
    """Get information about a model"""
    # Implementation for model info
    pass
```

**Step 2: Usage Examples**

```bash
# List all available models (OpenRouter + Local)
python -m auditor.cli models

# List only local models
python -m auditor.cli models list-local

# Download a new local model
python -m auditor.cli models download codellama:13b

# Get model information
python -m auditor.cli models info "gpt-4"

# Test different models
python -m auditor.cli analyze \
  --code "import subprocess; subprocess.call(cmd, shell=True)" \
  --language python \
  --model "ollama/codellama:7b"

python -m auditor.cli analyze \
  --code "import subprocess; subprocess.call(cmd, shell=True)" \
  --language python \
  --model "openai/gpt-4"
```

#### E. Model Performance Comparison

Create a model benchmarking tool:

```bash
# Create benchmark script
cat > benchmark_models.py << 'EOF'
#!/usr/bin/env python3
import time
import asyncio
from app.services.llm_service import LLMService

async def benchmark_models():
    """Benchmark different models on security analysis"""
    
    test_code = """
import os
import subprocess
def run_command(user_input):
    os.system(user_input)
    subprocess.call(user_input, shell=True)
"""
    
    models_to_test = [
        "agentica-org/deepcoder-14b-preview:free",
        "openai/gpt-4",
        "ollama/codellama:7b",
        "local/starcoder"
    ]
    
    llm_service = LLMService()
    results = {}
    
    for model in models_to_test:
        try:
            start_time = time.time()
            
            messages = [
                {"role": "system", "content": "Analyze this code for security vulnerabilities."},
                {"role": "user", "content": f"Code:\n{test_code}"}
            ]
            
            response = await llm_service._call_model(messages, 1000, 0.1, model)
            
            end_time = time.time()
            duration = end_time - start_time
            
            results[model] = {
                "duration": duration,
                "response_length": len(response["choices"][0]["message"]["content"]),
                "status": "success"
            }
            
            print(f"✅ {model}: {duration:.2f}s")
            
        except Exception as e:
            results[model] = {
                "duration": None,
                "response_length": 0,
                "status": f"error: {e}"
            }
            print(f"❌ {model}: {e}")
    
    # Print results
    print("\n📊 Benchmark Results:")
    print("=" * 60)
    for model, result in results.items():
        if result["status"] == "success":
            print(f"{model:40} | {result['duration']:6.2f}s | {result['response_length']:4d} chars")
        else:
            print(f"{model:40} | {result['status']}")

if __name__ == "__main__":
    asyncio.run(benchmark_models())
EOF

python benchmark_models.py
```

This comprehensive model extension system allows you to:

1. **Add OpenAI models** with full API integration
2. **Use local models** via Ollama or Hugging Face
3. **Create custom providers** for any API
4. **Manage models** via CLI commands
5. **Benchmark performance** across different models
6. **Mix and match** models for different use cases

#### Summary: Model Extension Capabilities

This comprehensive model extension system allows you to:

1. **Add OpenAI models** with full API integration (GPT-4, GPT-3.5, etc.)
2. **Use local models** via Ollama or Hugging Face Transformers
3. **Create custom providers** for any API (Anthropic, Cohere, etc.)
4. **Manage models** via CLI commands (list, download, benchmark)
5. **Benchmark performance** across different models
6. **Mix and match** models for different use cases

**Quick Start Examples:**
```bash
# OpenAI models (requires OPENAI_API_KEY)
python -m auditor.cli scan --path . --model "openai/gpt-4"

# Local models via Ollama (no API key needed)
ollama pull codellama:7b
python -m auditor.cli scan --path . --model "ollama/codellama:7b"

# List all available models
python -m auditor.cli models

# Benchmark different models
python benchmark_models.py
```

The system maintains backward compatibility while providing flexibility to use the best model for each specific security analysis task.

### 3. Custom Filtering

```bash
# Include specific file types
python -m auditor.cli scan \
  --include "*.py" \
  --include "*.js" \
  --include "*.java"

# Exclude common directories
python -m auditor.cli scan \
  --exclude "*/tests/*" \
  --exclude "*/node_modules/*" \
  --exclude "*/.git/*" \
  --exclude "*/venv/*" \
  --exclude "*/__pycache__/*"

# Severity filtering
python -m auditor.cli scan --severity-filter critical  # Only critical issues
python -m auditor.cli scan --severity-filter high      # High and critical
python -m auditor.cli scan --severity-filter medium    # Medium, high, critical
```

### 3. CI/CD Integration

```bash
# Fail build on high severity issues
python -m auditor.cli scan --path . --fail-on-high

# Generate reports for CI
python -m auditor.cli scan \
  --path . \
  --output-format github \
  --output-file security-report.md \
  --severity-filter medium
```

### 4. Analytics Commands

```bash
# View vulnerability trends
python -m auditor.cli trends-detailed --period 30 --include-forecast

# Top security rules analysis
python -m auditor.cli top-rules --limit 15 --severity high

# Performance analysis
python -m auditor.cli performance --include-models --breakdown-language

# Generate comprehensive report
python -m auditor.cli generate-report \
  --report-type security_summary \
  --time-range 7d \
  --format markdown \
  --save weekly-report.md
```

---

## 📖 Command Reference

### Core Commands

```bash
# Main CLI entry point
python -m auditor.cli [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]

# Global options
--api-url TEXT     # API base URL (default: http://localhost:8000)
--api-key TEXT     # API authentication key
--help             # Show help message
```

### Scanning Commands

```bash
# Scan files/directories
python -m auditor.cli scan [OPTIONS]
  --path TEXT                    # Path to scan (default: .)
  --model TEXT                   # AI model to use
  --output-format [table|json|github|markdown|sarif]
  --output-file TEXT             # Save output to file
  --severity-filter [all|critical|high|medium|low]
  --include TEXT                 # Include patterns (repeatable)
  --exclude TEXT                 # Exclude patterns (repeatable)
  --advanced/--no-advanced       # Multi-model analysis
  --fail-on-high/--no-fail-on-high  # Exit with error on high findings

# Analyze code directly
python -m auditor.cli analyze [OPTIONS]
  --code TEXT                    # Code to analyze (required)
  --language TEXT                # Programming language (required)
  --model TEXT                   # AI model to use
  --advanced/--no-advanced       # Advanced analysis
```

### Model Management

```bash
# List available models
python -m auditor.cli models
```

### Analytics Commands

```bash
# Vulnerability trends
python -m auditor.cli trends-detailed [OPTIONS]
  --period INTEGER               # Days to analyze (default: 30)
  --granularity [hourly|daily|weekly]
  --include-forecast             # Include forecasting
  --output [table|json|csv]
  --save TEXT                    # Save to file
  --visual                       # Enhanced visualizations

# Top security rules
python -m auditor.cli top-rules [OPTIONS]
  --limit INTEGER                # Number of rules (default: 10)
  --time-range TEXT              # Time range (default: 30d)
  --severity [critical|high|medium|low]
  --tool [bandit|semgrep]
  --output [table|json|csv]
  --save TEXT                    # Save to file

# Performance analysis
python -m auditor.cli performance [OPTIONS]
  --include-cache                # Cache metrics
  --include-models               # Model performance
  --breakdown-language           # Language breakdown
  --output [table|json|csv]
  --save TEXT                    # Save to file

# Generate reports
python -m auditor.cli generate-report [OPTIONS]
  --report-type [security_summary|vulnerability_trends|performance_analysis|top_rules_analysis]
  --time-range [1h|24h|7d|30d|90d|365d]
  --format [markdown|json|csv|text]
  --save TEXT                    # Save to file
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError" or Import Errors

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import app.main; print('✅ Import successful')"
```

#### 2. "API key not configured"

```bash
# Check if API key is set
echo $OPENROUTER_API_KEY

# Set the API key
export OPENROUTER_API_KEY="your-api-key-here"

# Test API access
python -m auditor.cli models
```

#### 3. "Failed to connect to localhost port 8000"

```bash
# Check if server is running
curl http://localhost:8000/health

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for server to start
sleep 5
curl http://localhost:8000/health
```

#### 4. Redis Connection Issues

```bash
# Check Redis status
redis-cli ping

# If Redis not available, disable caching
export REDIS_URL=""

# Or install Redis
sudo apt install redis-server  # Ubuntu/Debian
brew install redis             # macOS
```

#### 5. Permission Errors

```bash
# Fix permissions
chmod +x $(which python)

# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debug Mode

```bash
# Enable debug logging
export AUDITOR_DEBUG=true
export AUDITOR_LOG_LEVEL=DEBUG

# Run with verbose output
python -m auditor.cli scan . --verbose
```

### Performance Issues

```bash
# Use faster model for classification
python -m auditor.cli scan . --model "qwen/qwen-2.5-coder-32b-instruct:free"

# Reduce file scope
python -m auditor.cli scan . --exclude "*/node_modules/*" --exclude "*/venv/*"

# Enable Redis caching
export REDIS_URL="redis://localhost:6379/0"
```

---

## 💡 Best Practices

### 1. Project Setup

```bash
# Create project-specific configuration
mkdir -p .auditor
cat > .auditor/config.yaml << 'EOF'
# Project-specific auditor configuration
scanning:
  default_excludes:
    - "*/tests/*"
    - "*/node_modules/*"
    - "*/.git/*"
    - "*/venv/*"
    - "*/__pycache__/*"
  
  severity_threshold: "medium"
  
models:
  preferred: "agentica-org/deepcoder-14b-preview:free"
  
output:
  format: "github"
  save_reports: true
EOF
```

### 2. CI/CD Integration

```bash
# Create GitHub Actions workflow
mkdir -p .github/workflows
cat > .github/workflows/security-audit.yml << 'EOF'
name: Security Audit
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run security audit
      run: |
        python -m auditor.cli scan . \
          --output-format sarif \
          --output-file security.sarif \
          --fail-on-high
      env:
        OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: security.sarif
EOF
```

### 3. Pre-commit Hook

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running security audit..."
python -m auditor.cli scan --staged-only --severity-filter high
if [ $? -ne 0 ]; then
    echo "❌ Security issues found. Commit rejected."
    exit 1
fi
echo "✅ Security audit passed."
EOF

chmod +x .git/hooks/pre-commit
```

### 4. Regular Monitoring

```bash
# Weekly security report
cat > weekly_audit.sh << 'EOF'
#!/bin/bash
echo "🛡️ Weekly Security Audit Report"
echo "================================"

# Generate comprehensive report
python -m auditor.cli generate-report \
  --report-type security_summary \
  --time-range 7d \
  --format markdown \
  --save "reports/weekly-$(date +%Y-%m-%d).md"

# Scan current codebase
python -m auditor.cli scan . \
  --output-format json \
  --output-file "reports/current-scan-$(date +%Y-%m-%d).json"

echo "✅ Reports saved to reports/ directory"
EOF

chmod +x weekly_audit.sh
```

### 5. Model Selection Guidelines

```bash
# For code patches and fixes
python -m auditor.cli scan . --model "agentica-org/deepcoder-14b-preview:free"

# For fast classification and triage
python -m auditor.cli scan . --model "qwen/qwen-2.5-coder-32b-instruct:free"

# For detailed security explanations
python -m auditor.cli scan . --model "moonshotai/kimi-dev-72b:free"

# For comprehensive quality assessment
python -m auditor.cli scan . --model "meta-llama/llama-3.3-70b-instruct:free"

# For multi-model analysis (best results)
python -m auditor.cli scan . --advanced
```

---

## 🎯 Example Workflows

### 1. Daily Development Workflow

```bash
# Morning: Quick scan of changes
git diff --name-only HEAD~1 | xargs python -m auditor.cli scan --path

# Before commit: Security check
python -m auditor.cli scan . --severity-filter high --fail-on-high

# Weekly: Comprehensive analysis
python -m auditor.cli scan . --advanced --output-format markdown --output-file weekly-report.md
```

### 2. Code Review Workflow

```bash
# Scan PR changes
git diff origin/main --name-only | xargs python -m auditor.cli scan --path

# Generate review comments
python -m auditor.cli scan . --output-format github --output-file pr-security-review.md
```

### 3. Release Preparation

```bash
# Comprehensive security audit
python -m auditor.cli scan . \
  --advanced \
  --output-format sarif \
  --output-file release-security-audit.sarif \
  --fail-on-high

# Generate security report
python -m auditor.cli generate-report \
  --report-type security_summary \
  --time-range 30d \
  --format markdown \
  --save release-security-report.md
```

---

## 📞 Support & Resources

- **📚 Documentation**: [Full Documentation Index](00-DOCUMENTATION_INDEX.md)
- **🐛 Issues**: [GitHub Issues](https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor/discussions)
- **🔧 API Reference**: [OpenRouter API](https://openrouter.ai/docs)

---

## 🎉 You're Ready!

You now have everything you need to use the AI Code Security Auditor effectively. Start with basic scans and gradually explore advanced features as you become more comfortable with the tool.

**Quick reminder of the essential commands:**

```bash
# Basic scan
python -m auditor.cli scan --path .

# With API key
export OPENROUTER_API_KEY="your-key"
python -m auditor.cli scan --path . --advanced

# Start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Happy auditing! 🛡️✨
