#!/bin/bash

# PDF Chat Bot - Development Environment Setup Script
# This script automates the development environment setup process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        REQUIRED_VERSION="3.11"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            log_success "Python $PYTHON_VERSION found"
        else
            log_error "Python 3.11+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    
    # Check Git
    if command_exists git; then
        log_success "Git found"
    else
        log_error "Git not found. Please install Git"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "pdf-chat-bot/app.py" ]; then
        log_error "Please run this script from the project root directory"
        exit 1
    fi
}

# Create virtual environment
setup_virtual_environment() {
    log_info "Setting up virtual environment..."
    
    if [ -d ".venv" ]; then
        log_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf .venv
            log_info "Removed existing virtual environment"
        else
            log_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv .venv
    log_success "Virtual environment created"
}

# Activate virtual environment
activate_virtual_environment() {
    log_info "Activating virtual environment..."
    
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        log_success "Virtual environment activated"
    else
        log_error "Virtual environment not found"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install main dependencies
    if [ -f "pdf-chat-bot/requirements.txt" ]; then
        pip install -r pdf-chat-bot/requirements.txt
        log_success "Main dependencies installed"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Install development dependencies if they exist
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        log_success "Development dependencies installed"
    else
        log_info "No development dependencies file found, skipping"
    fi
    
    # Install common development tools
    log_info "Installing development tools..."
    pip install black isort flake8 mypy pytest pytest-cov pre-commit
    log_success "Development tools installed"
}

# Setup environment file
setup_environment_file() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env file from template"
            log_warning "Please edit .env file with your configuration values"
        else
            # Create basic .env file
            cat > .env << EOF
# PDF Chat Bot Configuration
GOOGLE_API_KEY=your_gemini_api_key_here

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Development Configuration
DEBUG=true
LOG_LEVEL=INFO

# Database Configuration
CHROMA_DB_PATH=./chroma_db
EOF
            log_success "Created basic .env file"
            log_warning "Please edit .env file with your actual API keys and configuration"
        fi
    else
        log_info ".env file already exists"
    fi
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."
    
    # Create pre-commit config if it doesn't exist
    if [ ! -f ".pre-commit-config.yaml" ]; then
        cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=88]
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF
        log_success "Created pre-commit configuration"
    fi
    
    # Install pre-commit hooks
    pre-commit install
    log_success "Pre-commit hooks installed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    # Create directories if they don't exist
    mkdir -p pdf-chat-bot/data/uploads
    mkdir -p pdf-chat-bot/logs
    mkdir -p chroma_db
    mkdir -p tests/unit
    mkdir -p tests/integration
    mkdir -p tests/fixtures
    
    log_success "Directories created"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Check if we can import main modules
    python3 -c "
import sys
try:
    import streamlit
    import langchain
    import chromadb
    print('✓ All main dependencies can be imported')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    # Check if the app can start (basic syntax check)
    python3 -c "
import sys
sys.path.append('pdf-chat-bot')
try:
    # Basic syntax check
    with open('pdf-chat-bot/app.py', 'r') as f:
        compile(f.read(), 'pdf-chat-bot/app.py', 'exec')
    print('✓ Application syntax is valid')
except SyntaxError as e:
    print(f'✗ Syntax error in app.py: {e}')
    sys.exit(1)
"
    
    log_success "Installation verified successfully"
}

# Display next steps
display_next_steps() {
    log_success "Setup completed successfully!"
    echo
    log_info "Next steps:"
    echo "1. Edit .env file with your actual configuration:"
    echo "   - Add your Google Gemini API key"
    echo "   - Adjust other settings as needed"
    echo
    echo "2. Activate the virtual environment:"
    echo "   source .venv/bin/activate"
    echo
    echo "3. Run the application:"
    echo "   cd pdf-chat-bot"
    echo "   streamlit run app.py"
    echo
    echo "4. Run tests:"
    echo "   pytest tests/ -v"
    echo
    echo "5. Format code before committing:"
    echo "   black pdf-chat-bot/"
    echo "   isort pdf-chat-bot/"
    echo
    log_info "For more information, see CONTRIBUTING.md"
}

# Main execution
main() {
    echo "========================================"
    echo "PDF Chat Bot - Development Setup"
    echo "========================================"
    echo
    
    check_prerequisites
    setup_virtual_environment
    activate_virtual_environment
    install_dependencies
    setup_environment_file
    setup_pre_commit
    create_directories
    verify_installation
    display_next_steps
}

# Run main function
main "$@"