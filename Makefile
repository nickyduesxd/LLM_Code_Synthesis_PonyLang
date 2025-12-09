.PHONY: help setup install test run quick batch analyze clean

# Default target
help:
	@echo "Pony LLM Evaluation Framework - Make Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make setup      - Run setup validation"
	@echo ""
	@echo "Evaluation:"
	@echo "  make run        - Run full evaluation"
	@echo "  make quick      - Run quick test (3 tasks)"
	@echo "  make batch      - Run batch evaluations"
	@echo ""
	@echo "Analysis:"
	@echo "  make analyze    - Analyze latest results"
	@echo ""
	@echo "Testing:"
	@echo "  make test       - Run unit tests"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean      - Clean generated files"
	@echo "  make clean-all  - Clean everything including results"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✓ Installation complete"

# Run setup validation
setup:
	@echo "Running setup validation..."
	python3 setup.py

# Run unit tests
test:
	@echo "Running tests..."
	cd tests && python3 test_framework.py

# Run full evaluation
run:
	@echo "Running full evaluation..."
	@echo "This may take a while..."
	cd evaluation && python3 evaluator.py

# Quick test with limited tasks
quick:
	# Quick test with limited tasks
quick:
	@echo "Running quick test..."
	@cd evaluation && python3 quick_test.py || python3 -c "from evaluator import Evaluator; from pathlib import Path; import time; evaluator = Evaluator(dataset_path=Path('../dataset/pony_tasks.json'), output_dir=Path('../results')/f'quick_{int(time.time())}', strategies=['zero_shot', 'few_shot'], models=['gemini-2.5-flash']); evaluator.run_evaluation(task_filter=['basic_001', 'basic_002', 'actor_001'])"

# Run batch evaluations
batch:
	@echo "Running batch evaluations..."
	cd evaluation && python3 batch_runner.py

# Analyze latest results
analyze:
	@echo "Analyzing latest results..."
	@LATEST=$$(ls -t results/*/evaluation_results.json | head -1); \
	if [ -z "$$LATEST" ]; then \
		echo "No results found. Run 'make run' first."; \
	else \
		echo "Analyzing: $$LATEST"; \
		cd evaluation && python3 analyze_results.py ../$$LATEST; \
	fi

# Clean generated files (keep results)
clean:
	@echo "Cleaning generated files..."
	rm -rf evaluation/generated_code/*
	rm -rf evaluation/compilation_work/*
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	@echo "✓ Cleaned"

# Clean everything including results
clean-all: clean
	@echo "Cleaning all results..."
	rm -rf results/*
	@echo "✓ Everything cleaned"

# Check environment
check:
	@echo "Environment Check"
	@echo "================="
	@echo -n "Python: "
	@python3 --version
	@echo -n "Pony: "
	@ponyc --version || echo "NOT INSTALLED"
	@echo -n "API Key: "
	@if [ -n "$$GEMINI_API_KEY" ]; then echo "SET"; else echo "NOT SET"; fi
	@echo ""
	@echo "Python Packages:"
	@python3 -c "import google.generativeai" 2>/dev/null && echo "  ✓ google-generativeai" || echo "  ✗ google-generativeai"
	@python3 -c "import pandas" 2>/dev/null && echo "  ✓ pandas" || echo "  ✗ pandas"
	@python3 -c "import matplotlib" 2>/dev/null && echo "  ✓ matplotlib" || echo "  ✗ matplotlib"

# Show dataset statistics
dataset-info:
	@echo "Dataset Information"
	@echo "==================="
	@python3 -c " \
	import json; \
	with open('dataset/pony_tasks.json') as f: \
		data = json.load(f); \
		tasks = data['tasks']; \
		print(f'Total Tasks: {len(tasks)}'); \
		from collections import Counter; \
		cats = Counter(t['category'] for t in tasks); \
		diffs = Counter(t['difficulty'] for t in tasks); \
		print('\\nBy Category:'); \
		for cat, count in sorted(cats.items()): \
			print(f'  {cat}: {count}'); \
		print('\\nBy Difficulty:'); \
		for diff, count in sorted(diffs.items()): \
			print(f'  {diff}: {count}'); \
	"

# List results
list-results:
	@echo "Available Results:"
	@echo "=================="
	@ls -lth results/ 2>/dev/null | head -15 || echo "No results found"

# Quick start
quickstart:
	@chmod +x quickstart.sh
	@./quickstart.sh
