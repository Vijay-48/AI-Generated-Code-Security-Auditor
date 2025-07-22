#!/bin/bash
# AI Code Security Auditor - Production Deployment Script
# Version: 2.0.0

set -e

echo "🚀 AI Code Security Auditor v2.0.0 - Production Deployment"
echo "==========================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo ""
    echo "🔍 Checking Prerequisites..."
    echo "----------------------------"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 not found. Please install Python 3.11 or higher."
        exit 1
    fi
    
    # Check pip
    if command -v pip &> /dev/null; then
        print_status "pip found"
    else
        print_error "pip not found. Please install pip."
        exit 1
    fi
    
    # Check git (optional)
    if command -v git &> /dev/null; then
        print_status "Git found"
    else
        print_warning "Git not found. Some features may be limited."
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        print_status "Docker found"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker not found. Container deployment not available."
        DOCKER_AVAILABLE=false
    fi
}

# Installation options
install_from_source() {
    echo ""
    echo "📦 Installing from Source..."
    echo "----------------------------"
    
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Are you in the correct directory?"
        exit 1
    fi
    
    # Install in development mode
    pip install -e .
    print_status "Installed from source in development mode"
}

install_from_pypi() {
    echo ""
    echo "📦 Installing from PyPI..."
    echo "--------------------------"
    
    pip install ai-code-security-auditor
    print_status "Installed from PyPI"
}

# Environment setup
setup_environment() {
    echo ""
    echo "🔧 Environment Setup..."
    echo "----------------------"
    
    # Check for OpenRouter API key
    if [ -z "$OPENROUTER_API_KEY" ]; then
        print_warning "OPENROUTER_API_KEY not set"
        echo "   Get your free API key at: https://openrouter.ai/"
        echo "   Then run: export OPENROUTER_API_KEY='your-key-here'"
        echo ""
        read -p "Do you want to enter your API key now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter your OpenRouter API key: " API_KEY
            export OPENROUTER_API_KEY="$API_KEY"
            echo "export OPENROUTER_API_KEY='$API_KEY'" >> ~/.bashrc
            print_status "API key configured"
        fi
    else
        print_status "OpenRouter API key found"
    fi
    
    # Optional: Redis setup
    if command -v redis-server &> /dev/null; then
        print_status "Redis found - caching will be available"
    else
        print_warning "Redis not found - caching will be disabled"
        echo "   Install Redis for better performance: apt-get install redis-server"
    fi
}

# Verification
verify_installation() {
    echo ""
    echo "✅ Verifying Installation..."
    echo "----------------------------"
    
    # Check if auditor command is available
    if command -v auditor &> /dev/null; then
        print_status "CLI tool 'auditor' is available"
        
        # Test basic functionality
        echo "Testing basic functionality..."
        auditor --help > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_status "CLI help command works"
        else
            print_error "CLI help command failed"
            exit 1
        fi
        
        # Test models command
        auditor models > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_status "Models command works"
        else
            print_warning "Models command failed (API key may be missing)"
        fi
        
    else
        print_error "CLI tool 'auditor' not found in PATH"
        echo "   Try: pip install -e . (if installing from source)"
        echo "   Or: pip install ai-code-security-auditor"
        exit 1
    fi
    
    # Check if we can import the package
    python3 -c "import app.main; print('✅ FastAPI app can be imported')" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_status "FastAPI application imports successfully"
    else
        print_warning "FastAPI application import failed - some dependencies may be missing"
    fi
}

# Start services
start_services() {
    echo ""
    echo "🚀 Starting Services..."
    echo "----------------------"
    
    # Option 1: Direct FastAPI
    echo "Choose deployment method:"
    echo "1) Development server (uvicorn)"
    echo "2) Production server (gunicorn)" 
    echo "3) Docker container"
    echo "4) Skip service startup"
    
    read -p "Enter your choice (1-4): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            print_info "Starting development server on port 8001..."
            echo "Access API at: http://localhost:8001"
            echo "API docs at: http://localhost:8001/docs"
            echo "Press Ctrl+C to stop"
            echo ""
            uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
            ;;
        2)
            if command -v gunicorn &> /dev/null; then
                print_info "Starting production server on port 8001..."
                echo "Access API at: http://localhost:8001"
                echo "Press Ctrl+C to stop"
                echo ""
                gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
            else
                print_error "Gunicorn not found. Install with: pip install gunicorn"
                exit 1
            fi
            ;;
        3)
            if [ "$DOCKER_AVAILABLE" = true ]; then
                print_info "Building and starting Docker container..."
                if [ -f "docker-compose.yml" ]; then
                    docker-compose up --build
                else
                    print_error "docker-compose.yml not found"
                    exit 1
                fi
            else
                print_error "Docker not available"
                exit 1
            fi
            ;;
        4)
            print_info "Service startup skipped"
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Generate example configuration
generate_config() {
    echo ""
    echo "📝 Generating Example Configuration..."
    echo "------------------------------------"
    
    mkdir -p ~/.config/auditor
    
    cat > ~/.config/auditor/config.yaml << 'EOF'
# AI Code Security Auditor Configuration
# Version: 2.0.0

api:
  host: "0.0.0.0"
  port: 8001
  workers: 4
  
scanning:
  default_model: "agentica-org/deepcoder-14b-preview:free"
  timeout: 300
  max_file_size: "10MB"
  
analytics:
  retention_days: 365
  cache_ttl: 3600
  
output:
  default_format: "table"
  colors: true
  progress_bars: true
  
filters:
  default_excludes:
    - "*/node_modules/*"
    - "*/.git/*" 
    - "*/venv/*"
    - "*/test*/*"
    - "*/build/*"
    - "*/dist/*"

models:
  preferred:
    code_patches: "agentica-org/deepcoder-14b-preview:free"
    quality_assessment: "meta-llama/llama-3.3-70b-instruct:free"
    fast_classification: "qwen/qwen-2.5-coder-32b-instruct:free"
    security_explanations: "moonshotai/kimi-dev-72b:free"
EOF

    print_status "Configuration generated at ~/.config/auditor/config.yaml"
}

# Quick demo
run_demo() {
    echo ""
    echo "🎯 Running Quick Demo..."
    echo "-----------------------"
    
    # Create sample vulnerable code
    cat > /tmp/vulnerable_sample.py << 'EOF'
import os
import subprocess

# Secret credentials (this will be detected)
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
DATABASE_URL = "mysql://admin:password123@localhost/db"

def unsafe_function(user_input):
    # Command injection vulnerability
    os.system(f"echo {user_input}")
    
def sql_injection(user_id):
    # SQL injection vulnerability  
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def path_traversal(filename):
    # Path traversal vulnerability
    with open(f"./uploads/{filename}", 'r') as f:
        return f.read()
EOF

    print_info "Created sample vulnerable code at /tmp/vulnerable_sample.py"
    print_info "Running security analysis..."
    echo ""
    
    # Run the scan
    auditor analyze --code "$(cat /tmp/vulnerable_sample.py)" --language python
    
    # Clean up
    rm /tmp/vulnerable_sample.py
    
    echo ""
    print_status "Demo completed! The tool detected multiple vulnerabilities in the sample code."
}

# Main deployment flow
main() {
    echo "Welcome to the AI Code Security Auditor deployment script!"
    echo "This script will help you install and configure the auditor."
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Ask for installation method
    echo ""
    echo "📦 Choose Installation Method:"
    echo "1) Install from PyPI (recommended for users)"
    echo "2) Install from source (recommended for developers)" 
    echo "3) Docker only (containerized deployment)"
    
    read -p "Enter your choice (1-3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            install_from_pypi
            ;;
        2)  
            install_from_source
            ;;
        3)
            if [ "$DOCKER_AVAILABLE" = false ]; then
                print_error "Docker not available"
                exit 1
            fi
            print_info "Docker deployment selected - skipping pip installation"
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    # Environment setup
    setup_environment
    
    # Generate configuration
    generate_config
    
    # Verify installation (skip for Docker-only)
    if [[ $REPLY != "3" ]]; then
        verify_installation
        
        # Ask if user wants to run demo
        echo ""
        read -p "Would you like to run a quick demo? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            run_demo
        fi
    fi
    
    # Start services
    start_services
    
    # Final message
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================"
    print_status "AI Code Security Auditor v2.0.0 is ready to use!"
    echo ""
    echo "📖 Quick Start:"
    echo "   • CLI: auditor scan ."
    echo "   • API: http://localhost:8001/docs"
    echo "   • Help: auditor --help"
    echo ""
    echo "📚 Documentation:"
    echo "   • README.md - Complete usage guide"
    echo "   • docs/CLI_Commands.md - CLI reference"
    echo "   • CHANGELOG.md - Version history"
    echo ""
    echo "🆘 Support:"
    echo "   • GitHub Issues: Report bugs and feature requests"
    echo "   • GitHub Discussions: Community support"
    echo ""
    echo "⭐ Don't forget to star us on GitHub if this tool helps you!"
}

# Run main function
main "$@"