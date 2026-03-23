# Product Requirements Document (PRD)

## AI Code Security Auditor

## 1. Product Overview

### Product Name
AI Code Security Auditor

### Product Type
AI-powered code security analysis system.

### Objective

Detect security vulnerabilities in source code using a hybrid approach combining:

- Static code analysis
- Retrieval-Augmented Generation (RAG)
- Large Language Models (LLMs)

The system analyzes source code, identifies vulnerabilities mapped to security standards such as OWASP Top 10 and CWE, explains the security risks, and generates remediation patches.

### Primary Function

Automate secure code review by providing:

- vulnerability detection
- vulnerability explanation
- AI-generated remediation patches
- structured security reports

## 2. Problem Statement

Manual code review for security vulnerabilities is time-consuming and inconsistent. Traditional static analyzers rely on predefined rules and may produce false positives or miss contextual vulnerabilities.

Existing cloud-based AI code scanners introduce the following constraints:

- code privacy concerns
- dependency on external services
- limited customization
- restricted offline usage

The system addresses these limitations by providing a configurable AI-assisted code security auditing system capable of operating in local environments.

## 3. Goals and Objectives

### Primary Goals

- Detect common software security vulnerabilities.
- Map detected vulnerabilities to recognized standards.
- Provide detailed explanations of security risks.
- Generate secure remediation code patches.

### Secondary Goals

- Provide contextual code analysis using RAG.
- Allow operation in local environments without cloud dependency.
- Support multiple programming languages.

## 4. Target Users

| User Type | Description |
| --- | --- |
| Software Developers | Developers performing security analysis during development |
| Security Engineers | Security professionals reviewing application vulnerabilities |
| DevOps Engineers | Engineers integrating security checks into CI/CD pipelines |
| Students / Researchers | Individuals studying secure coding practices |

## 5. Key Features

### 5.1 Code Input

Supported inputs:

- single source file
- multiple files
- full project directory
- Git repository

Accepted languages (initial scope):

- Python
- JavaScript
- Java

### 5.2 Static Code Analysis

Rule-based vulnerability detection before AI analysis.

Detectable vulnerabilities include:

| Category | Example |
| --- | --- |
| SQL Injection | unsafe SQL queries |
| Command Injection | unsafe system commands |
| Hardcoded Secrets | API keys |
| Insecure Deserialization | unsafe object loading |
| Insecure Randomness | non-cryptographic random functions |

Static analysis performs initial filtering and vulnerability identification.

### 5.3 Code Chunking

Large source files are divided into logical chunks.

Chunk types:

- imports
- functions
- classes
- logic blocks

Purpose:

- maintain LLM context limits
- improve semantic retrieval

### 5.4 Retrieval-Augmented Generation (RAG)

RAG is used to provide relevant context to the LLM.

Pipeline:

- code chunks are converted into embeddings
- embeddings are stored in a vector database
- relevant code segments are retrieved during analysis
- retrieved context is passed to the LLM

Vector database options:

- FAISS
- Chroma

### 5.5 LLM Security Analysis

Large Language Models analyze code for deeper contextual vulnerabilities.

Supported LLMs (via OpenRouter):

- DeepCoder
- Qwen
- Kimi
- LLaMA 3.3

The LLM performs:

- vulnerability reasoning
- exploit explanation
- security recommendations
- patch generation

### 5.6 Taint Analysis

Tracks data flow between:

- source (user input)
- sink (dangerous operations)

Example sources:

- HTTP request input
- form input
- file input

Example sinks:

- database queries
- system commands
- file writes

Purpose: identify injection vulnerabilities.

### 5.7 Dependency Security Analysis

The system scans dependency files.

Supported files:

- requirements.txt
- package.json
- pom.xml

Detection includes:

- outdated packages
- known CVEs
- insecure libraries

### 5.8 Patch Generation

For each vulnerability, the system generates secure code fixes.

Patch output includes:

- corrected code
- explanation of fix
- severity classification

### 5.9 Security Report Generation

Output reports contain:

- vulnerability description
- affected file
- vulnerability category
- severity level
- recommended fix
- AI-generated patch

Supported report formats:

- JSON
- Markdown
- HTML

## 6. System Architecture

High-level architecture:

```text
User Input
   |
   v
Code Ingestion Module
   |
   v
Static Security Analyzer
   |
   v
Chunking + Embedding Generator
   |
   v
Vector Database (FAISS / Chroma)
   |
   v
RAG Context Retrieval
   |
   v
LLM Security Analysis
   |
   v
Patch Generator
   |
   v
Security Report Generator
```

## 7. Technical Stack

### Backend

- Python
- FastAPI

### AI Frameworks

- HuggingFace Transformers
- OpenRouter API

### LLM Models

- DeepCoder
- Qwen
- Kimi
- LLaMA 3.3

### Vector Databases

- FAISS
- Chroma

### Data Processing

- Python AST
- Regex-based scanners

## 8. API Design

### Scan Code Endpoint

`POST /scan`

Input:

```json
{
  "repository": "path or repo url"
}
```

Output:

```json
{
  "issues": [
    {
      "file": "auth.py",
      "severity": "High",
      "vulnerability": "SQL Injection",
      "description": "User input directly used in query",
      "patch": "..."
    }
  ]
}
```

### Health Endpoint

`GET /health`

Response:

```json
{
  "status": "running",
  "models_loaded": true
}
```

## 9. Functional Requirements

| ID | Requirement |
| --- | --- |
| FR1 | Accept source code as input |
| FR2 | Detect vulnerabilities using static analysis |
| FR3 | Generate embeddings for code chunks |
| FR4 | Retrieve relevant code context |
| FR5 | Analyze vulnerabilities using LLM |
| FR6 | Map vulnerabilities to OWASP categories |
| FR7 | Generate code patches |
| FR8 | Produce security reports |

## 10. Non-Functional Requirements

### Performance

- scan time under 60 seconds for small projects

### Scalability

- support projects up to 100k lines of code

### Security

- prevent code leakage
- optional offline operation

### Reliability

- stable API response
- fault-tolerant scanning

## 11. Installation Requirements

### Minimum Environment

- Python 3.10+
- 16 GB RAM recommended
- optional GPU for local models

### Dependencies

- FastAPI
- FAISS
- Transformers
- Uvicorn
- OpenRouter API client

## 12. Known Limitations

- installation may vary depending on OS
- vector database configuration may require additional setup
- large repositories may increase analysis time

## 13. Success Metrics

| Metric | Target |
| --- | --- |
| Vulnerability detection accuracy | >80% |
| False positive rate | <20% |
| Average scan time | <60 seconds |
| Supported languages | >=3 |

## 14. Future Enhancements

Potential improvements include:

- CI/CD integration
- GitHub pull request scanning
- IDE integration
- automated patch pull requests
- multi-language vulnerability models
- dynamic code analysis

## 15. Development Roadmap

### Phase 1

- static vulnerability detection
- FastAPI backend

### Phase 2

- RAG pipeline
- vector database integration

### Phase 3

- LLM vulnerability reasoning
- patch generation

### Phase 4

- report generation
- dependency scanning

### Phase 5

- CI/CD integration
- IDE plugins
