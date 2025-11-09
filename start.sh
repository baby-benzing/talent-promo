#!/bin/bash
# Quick start script for running all services

set -e

PROJECT_DIR="/Users/pmv/tech/talent-promo"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Research Agent - Service Startup                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo ""
    echo "Copy the example and add your OpenAI API key:"
    echo "  cp apps/api/.env.example .env"
    echo "  # Then edit .env and add your OPENAI_API_KEY"
    echo ""
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo ""
    echo "Create it with:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r apps/api/requirements.txt"
    echo ""
    exit 1
fi

# Check if temporal is installed
if ! command -v temporal &> /dev/null; then
    echo -e "${RED}❌ Temporal CLI not found!${NC}"
    echo ""
    echo "Install it with:"
    echo "  brew install temporal"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found!${NC}"
echo ""
echo "This script will open 3 terminal windows:"
echo "  1. Temporal Server (http://localhost:8233)"
echo "  2. Temporal Worker (processes workflows)"
echo "  3. FastAPI Server (http://localhost:8000)"
echo ""
echo -e "${YELLOW}Press Enter to continue or Ctrl+C to cancel...${NC}"
read

# macOS - use Terminal.app
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Opening terminal windows..."
    
    # Terminal 1: Temporal Server
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR' && echo '▶️  Starting Temporal Server...' && temporal server start-dev"
    activate
end tell
EOF
    
    sleep 2
    
    # Terminal 2: Worker
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR' && source venv/bin/activate && echo '▶️  Starting Temporal Worker...' && python -m temporal.worker"
end tell
EOF
    
    sleep 2
    
    # Terminal 3: API
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR/apps/api' && source ../../venv/bin/activate && echo '▶️  Starting FastAPI Server...' && uvicorn main:app --reload"
end tell
EOF
    
    echo ""
    echo -e "${GREEN}✅ Services starting in new terminal windows!${NC}"
    echo ""
    echo "Wait ~10 seconds for everything to start, then:"
    echo ""
    echo "  Run the test:"
    echo "    python test_workflow.py"
    echo ""
    echo "  Or use curl:"
    echo "    curl -X POST http://localhost:8000/api/research-agent/analyze \\"
    echo "      -H 'Content-Type: application/json' \\"
    echo "      -d '{\"job_title\": \"Software Engineer\"}'"
    echo ""
    echo "  View Temporal UI:"
    echo "    open http://localhost:8233"
    echo ""
    echo "  View API docs:"
    echo "    open http://localhost:8000/docs"
    echo ""
    
else
    # Linux/Other - provide tmux instructions
    echo -e "${YELLOW}⚠️  Auto-start is macOS only.${NC}"
    echo ""
    echo "On Linux, use tmux:"
    echo ""
    echo "  # Terminal 1"
    echo "  temporal server start-dev"
    echo ""
    echo "  # Terminal 2"
    echo "  cd '$PROJECT_DIR' && source venv/bin/activate && python -m temporal.worker"
    echo ""
    echo "  # Terminal 3"
    echo "  cd '$PROJECT_DIR/apps/api' && source ../../venv/bin/activate && uvicorn main:app --reload"
    echo ""
fi

