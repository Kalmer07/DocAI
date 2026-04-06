#!/usr/bin/env bash
# =============================================================================
# AI Document Analyzer - Universal Runner Script
# =============================================================================
# This script:
# 1. Checks environment and dependencies
# 2. Attempts to start the application with multiple fallback strategies
# 3. Provides clear error messages and recovery instructions
# =============================================================================

set -e  # Exit on first error (we'll handle exceptions)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# =============================================================================
# Configuration
# =============================================================================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PYTHON_VENV="$PROJECT_ROOT/venv"

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# =============================================================================
# Helper Functions
# =============================================================================

check_command() {
    command -v "$1" >/dev/null 2>&1
}

check_ollama() {
    if curl -s "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# =============================================================================
# Environment Checks
# =============================================================================

echo "=============================================="
echo "  AI Document Analyzer - Startup Script"
echo "=============================================="
echo ""

# Check Python
log_info "Checking Python..."
if check_command python3; then
    PYTHON_CMD="python3"
    log_success "Python 3 found: $($PYTHON_CMD --version)"
elif check_command python; then
    PYTHON_CMD="python"
    log_success "Python found: $($PYTHON_CMD --version)"
else
    log_error "Python not found. Please install Python 3.8+"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python"
    echo "  Windows: Download from python.org"
    exit 1
fi

# Check Node.js
log_info "Checking Node.js..."
if check_command node; then
    NODE_VERSION=$(node --version)
    log_success "Node.js found: $NODE_VERSION"
else
    log_warn "Node.js not found. Frontend will not be available."
    log_info "Install Node.js 18+ for frontend: https://nodejs.org/"
fi

# Check Ollama
log_info "Checking Ollama connection..."
if check_ollama; then
    log_success "Ollama is running at $OLLAMA_URL"
else
    log_warn "Ollama not reachable at $OLLAMA_URL"
    echo "  Install Ollama: https://ollama.ai/"
    echo "  Or set OLLAMA_URL environment variable"
fi

# =============================================================================
# Backend Setup
# =============================================================================

echo ""
log_info "Setting up backend..."
cd "$BACKEND_DIR"

# Create virtual environment if not exists
if [ ! -d "$PYTHON_VENV" ]; then
    log_info "Creating Python virtual environment..."
    $PYTHON_CMD -m venv "$PYTHON_VENV"
fi

# Activate virtual environment
source "$PYTHON_VENV/bin/activate"

# Install dependencies
log_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    log_success "Backend dependencies installed"
else
    log_warn "requirements.txt not found, creating default..."
    cat > requirements.txt << 'EOF'
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
aiohttp>=3.9.0
pymupdf>=1.23.0
python-docx>=1.1.0
python-multipart>=0.0.6
EOF
    pip install --quiet -r requirements.txt
fi

# =============================================================================
# Frontend Setup
# =============================================================================

if check_command node && check_command npm; then
    echo ""
    log_info "Setting up frontend..."
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        
        # Try different package managers
        if check_command pnpm; then
            log_info "Using pnpm..."
            pnpm install || {
                log_warn "pnpm failed, trying npm..."
                npm install
            }
        elif check_command yarn; then
            log_info "Using yarn..."
            yarn install || {
                log_warn "yarn failed, trying npm..."
                npm install
            }
        else
            log_info "Using npm..."
            npm install || {
                log_error "npm install failed"
                echo "Try: cd $FRONTEND_DIR && npm install"
            }
        fi
        
        log_success "Frontend dependencies installed"
    fi
    
    cd "$PROJECT_ROOT"
else
    log_warn "Skipping frontend setup (Node.js not available)"
fi

# =============================================================================
# Start Services
# =============================================================================

echo ""
log_info "Starting services..."

# Function to start backend with fallbacks
start_backend() {
    cd "$BACKEND_DIR"
    source "$PYTHON_VENV/bin/activate"
    
    log_info "Starting FastAPI backend on port $BACKEND_PORT..."
    
    # Try different ways to start
    if python -m uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload 2>&1; then
        return 0
    elif uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload 2>&1; then
        return 0
    elif python main.py 2>&1; then
        return 0
    else
        log_error "Failed to start backend"
        return 1
    fi
}

# Function to start frontend with fallbacks
start_frontend() {
    if ! check_command node; then
        log_warn "Cannot start frontend without Node.js"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    log_info "Starting Vite dev server on port $FRONTEND_PORT..."
    
    # Try different ways to start
    if npm run dev -- --port "$FRONTEND_PORT" 2>&1; then
        return 0
    elif npx vite --port "$FRONTEND_PORT" 2>&1; then
        return 0
    else
        log_error "Failed to start frontend"
        return 1
    fi
}

# Start in background or foreground based on args
if [ "$1" == "--backend-only" ]; then
    log_info "Starting backend only..."
    start_backend
elif [ "$1" == "--frontend-only" ]; then
    log_info "Starting frontend only..."
    start_frontend
else
    # Start both (backend in background, frontend in foreground)
    log_info "Starting backend in background..."
    start_backend &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is still running
    if kill -0 $BACKEND_PID 2>/dev/null; then
        log_success "Backend started (PID: $BACKEND_PID)"
        echo ""
        log_info "Backend API: http://localhost:$BACKEND_PORT"
        log_info "API Docs: http://localhost:$BACKEND_PORT/docs"
        echo ""
        
        if check_command node; then
            log_info "Starting frontend..."
            echo ""
            log_info "Frontend: http://localhost:$FRONTEND_PORT"
            echo ""
            start_frontend
            
            # Cleanup on exit
            trap "kill $BACKEND_PID 2>/dev/null" EXIT
        else
            log_warn "Frontend not available (Node.js required)"
            log_info "Press Ctrl+C to stop backend"
            wait $BACKEND_PID
        fi
    else
        log_error "Backend failed to start"
        exit 1
    fi
fi

# =============================================================================
# Completion
# =============================================================================

echo ""
log_success "=============================================="
log_success "  Application is running!"
log_success "=============================================="
echo ""
echo "  📡 Backend API:  http://localhost:$BACKEND_PORT"
echo "  📚 API Docs:     http://localhost:$BACKEND_PORT/docs"
if check_command node; then
    echo "  🖥️  Frontend:     http://localhost:$FRONTEND_PORT"
fi
echo "  🤖 Ollama:       $OLLAMA_URL"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""
