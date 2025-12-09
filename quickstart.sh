#!/bin/bash
# Quick Start Script for Pony LLM Evaluation Framework

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Pony LLM Evaluation Framework - Quick Start${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Check if ponyc is installed
echo -e "${YELLOW}Checking for Pony compiler...${NC}"
if command -v ponyc &> /dev/null; then
    PONY_VERSION=$(ponyc --version)
    echo -e "${GREEN}✓ Found: $PONY_VERSION${NC}"
else
    echo -e "${RED}✗ ponyc not found!${NC}"
    echo -e "  Install from: https://www.ponylang.io/"
    echo -e "  macOS: brew install ponyc"
    echo -e "  Ubuntu: sudo apt-get install ponyc"
    exit 1
fi

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check/install Python packages
echo -e "\n${YELLOW}Checking Python packages...${NC}"
if python3 -c "import google.generativeai" 2>/dev/null; then
    echo -e "${GREEN}✓ Required packages installed${NC}"
else
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Packages installed${NC}"
fi

# Check for API key
echo -e "\n${YELLOW}Checking API configuration...${NC}"
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠ GEMINI_API_KEY not set${NC}"
    echo -e "  Set it with: export GEMINI_API_KEY='your_key_here'"
    echo -e "  Or create a .env file"
    
    read -p "Do you want to enter your API key now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Gemini API key: " api_key
        export GEMINI_API_KEY="$api_key"
        echo -e "${GREEN}✓ API key set for this session${NC}"
    else
        echo -e "${RED}Cannot proceed without API key${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ API key configured${NC}"
fi

# Create directories
echo -e "\n${YELLOW}Setting up directories...${NC}"
mkdir -p results evaluation/generated_code evaluation/compilation_work
echo -e "${GREEN}✓ Directories created${NC}"

# Run setup check
echo -e "\n${YELLOW}Running setup validation...${NC}"
python3 setup.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Setup validation failed. Please fix errors above.${NC}"
    exit 1
fi

# Show menu
echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}What would you like to do?${NC}"
echo -e "${BLUE}================================================${NC}"
echo "1. Run full evaluation (all tasks, all strategies)"
echo "2. Run quick test (3 tasks, 2 strategies)"
echo "3. Run batch evaluations"
echo "4. Run tests"
echo "5. View existing results"
echo "6. Exit"
echo -e "${BLUE}================================================${NC}"

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo -e "\n${GREEN}Running full evaluation...${NC}"
        cd evaluation
        python3 evaluator.py
        ;;
    2)
        echo -e "\n${GREEN}Running quick test...${NC}"
        cd evaluation
        # Run with limited tasks and strategies
        python3 -c "
from evaluator import Evaluator
from pathlib import Path
import time

output_dir = Path('../results') / f'quick_test_{int(time.time())}'
evaluator = Evaluator(
    dataset_path=Path('../dataset/pony_tasks.json'),
    output_dir=output_dir,
    strategies=['zero_shot', 'few_shot'],
    models=['gemini-pro']
)
evaluator.run_evaluation(task_filter=['basic_001', 'basic_002', 'actor_001'])
"
        ;;
    3)
        echo -e "\n${GREEN}Running batch evaluations...${NC}"
        cd evaluation
        python3 batch_runner.py
        ;;
    4)
        echo -e "\n${GREEN}Running tests...${NC}"
        cd tests
        python3 test_framework.py
        ;;
    5)
        echo -e "\n${YELLOW}Available results:${NC}"
        ls -lt results/ | head -10
        echo -e "\n${YELLOW}To analyze a result, run:${NC}"
        echo "  cd evaluation"
        echo "  python3 analyze_results.py ../results/<dir>/evaluation_results.json"
        ;;
    6)
        echo -e "\n${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✓ Done!${NC}"
echo -e "\n${YELLOW}To analyze results, run:${NC}"
echo "  cd evaluation"
echo "  python3 analyze_results.py ../results/<timestamp>/evaluation_results.json"
