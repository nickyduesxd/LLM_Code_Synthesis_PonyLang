# Pony Language LLM Code Synthesis Evaluation

A comprehensive framework for evaluating Large Language Model (LLM) capabilities in synthesizing Pony programming language code across different prompting strategies.

## Overview

This project systematically evaluates how well LLMs (particularly Google Gemini) can generate correct Pony code, focusing on:
- Reference capability system (iso, val, ref, box, trn, tag)
- Actor-based concurrency patterns
- Message passing and safe data sharing
- Compile-time memory safety

## Features

- **15+ Curated Pony Tasks** across 4 categories
- **8 Prompting Strategies**: zero-shot, few-shot, chain-of-thought, self-debug, transfer learning, etc.
- **Automated Compilation Testing** with ponyc compiler
- **Comprehensive Analysis** with visualizations and metrics
- **Multiple LLM Support**: Gemini, OpenAI, Anthropic

## Project Structure

```
ponylang-llm-eval/
├── dataset/
│   └── pony_tasks.json          # Task definitions and test cases
├── prompts/
│   └── prompting_strategies.py  # Different prompting templates
├── evaluation/
│   ├── evaluator.py             # Main evaluation harness
│   └── analyze_results.py       # Analysis and visualization
├── pony_examples/
│   └── reference_implementations.pony  # Example Pony code
├── results/                     # Generated results (created at runtime)
├── tests/                       # Test cases
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Prerequisites

### 1. Install Pony Compiler

**macOS:**
```bash
brew install ponyc
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ponyc
```

**From Source:**
```bash
git clone https://github.com/ponylang/ponyc
cd ponyc
make
sudo make install
```

Verify installation:
```bash
ponyc --version
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys

Create a `.env` file in the project root:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
ANTHROPIC_API_KEY=your_anthropic_key_here  # Optional
```

Or export environment variables:
```bash
export GEMINI_API_KEY="your_key_here"
```

## Quick Start

### 1. Run Evaluation

```bash
cd evaluation
python evaluator.py
```

This will:
- Load all tasks from the dataset
- Generate prompts using all strategies
- Query the LLM for each task/strategy combination
- Compile generated code with ponyc
- Save results and generate reports

### 2. Analyze Results

```bash
python analyze_results.py ../results/eval_<timestamp>/evaluation_results.json
```

This generates:
- Success rate charts by strategy
- Category-wise performance analysis
- Difficulty-based breakdowns
- Heatmaps and comparative statistics
- Error analysis reports

## Task Categories

### 1. Basic Syntax (6 tasks)
- Factorial, Fibonacci, array operations
- Tests fundamental Pony syntax and control flow

### 2. Reference Capabilities (3 tasks)
- Immutable buffers (val)
- Isolated counters (iso)
- Read-only wrappers (box)
- Tests understanding of capability system

### 3. Actor Concurrency (3 tasks)
- Counter actors
- Echo actors with callbacks
- Worker pools
- Tests actor-based programming

### 4. Complex Systems (3 tasks)
- Producer-consumer patterns
- Banking system with transfers
- Distributed counters
- Tests real-world concurrent systems

## Prompting Strategies

### 1. Zero-Shot
Direct task description without examples

### 2. Few-Shot
Includes 2-3 Pony code examples before the task

### 3. Chain-of-Thought
Guides step-by-step reasoning about capabilities and design

### 4. Self-Debug
Prompts LLM to review and fix its own code

### 5. Transfer Learning (Rust/C++)
First solves in familiar language, then converts to Pony

### 6. Capability-Focused
Emphasizes reference capability selection

### 7. Actor-Focused
Emphasizes actor design patterns

### 8. Transfer C++
Converts from C++ to Pony

## Evaluation Metrics

- **Compilation Success Rate**: % of generated code that compiles
- **Syntax Correctness**: Proper Pony syntax usage
- **Capability Correctness**: Appropriate reference capability usage
- **Test Pass Rate**: Functional correctness (when tests available)
- **Execution Time**: Time per task/strategy

## Example Usage

### Run Specific Tasks

```python
# In evaluator.py
TASK_FILTER = ['basic_001', 'actor_001']  # Only these tasks
evaluator.run_evaluation(task_filter=TASK_FILTER)
```

### Test Single Strategy

```python
STRATEGIES = ['zero_shot']  # Only zero-shot
```

### Add Custom Task

Edit `dataset/pony_tasks.json`:

```json
{
  "id": "custom_001",
  "category": "basic_syntax",
  "difficulty": "easy",
  "title": "Hello World",
  "description": "Create a Pony actor that prints Hello World",
  "prompt": "Write a Pony Main actor that prints 'Hello World'",
  "reference_solution": "actor Main\n  new create(env: Env) =>\n    env.out.print(\"Hello World\")",
  "test_cases": []
}
```

## Results Interpretation

### Success Rate Benchmarks
- **>80%**: Excellent LLM performance on this category
- **60-80%**: Good performance, some challenges remain
- **40-60%**: Moderate difficulty for LLM
- **<40%**: Significant challenges, needs improvement

### Expected Challenges
- Reference capability reasoning (especially iso/trn)
- Recover blocks and capability transitions
- Complex actor communication patterns
- Callback lambda syntax

## Troubleshooting

### Ponyc Not Found
```bash
# Check if ponyc is in PATH
which ponyc

# If not, add to PATH or specify full path in config.yaml
ponyc:
  path: "/usr/local/bin/ponyc"
```

### API Rate Limits
Add delays between API calls in `evaluator.py`:
```python
import time
time.sleep(1)  # 1 second delay
```

### Compilation Timeouts
Increase timeout in `config.yaml`:
```yaml
evaluation:
  compilation_timeout: 60  # seconds
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add new tasks to `dataset/pony_tasks.json`
4. Add new prompting strategies to `prompts/prompting_strategies.py`
5. Submit a pull request

## Research Applications

This framework is designed for research on:
- LLM code synthesis capabilities in low-resource languages
- Effectiveness of prompting strategies for capability systems
- Transfer learning from mainstream to niche languages
- Actor-based concurrency pattern synthesis


## License

MIT License

## Acknowledgments

- Pony Language Team for the excellent documentation
- Google for Gemini API access
- Johns Hopkins University Machine Programming Course

## Contact

For questions or issues, please open an issue on GitHub or contact nzayfma1@jh.edu.

---

**Note**: This is a research project for evaluating LLM capabilities. Generated code should be reviewed before production use.
