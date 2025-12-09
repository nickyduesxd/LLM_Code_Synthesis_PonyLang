# Project Documentation - Pony LLM Code Synthesis Evaluation

## Project Overview

This research project evaluates Large Language Model (LLM) capabilities in synthesizing code for Pony, an actor-model programming language with a unique reference capability system. The project is designed for academic research in machine programming and LLM code synthesis.

## Research Motivation

Pony presents unique challenges for LLMs due to:

1. **Limited Training Data**: Few Pony programs exist compared to mainstream languages
2. **Reference Capabilities**: Complex type system (iso, trn, ref, val, box, tag)
3. **Actor-Based Concurrency**: Message-passing paradigm without traditional locks
4. **Compile-Time Safety**: Strong guarantees that must be satisfied

This makes Pony an ideal testbed for evaluating:
- LLM generalization to low-resource languages
- Understanding of advanced type systems
- Concurrency pattern synthesis

## Research Questions

1. **RQ1**: How accurately can LLMs synthesize syntactically correct Pony programs?
2. **RQ2**: To what extent do LLMs understand Pony's reference capability system?
3. **RQ3**: How does performance vary across task complexities?
4. **RQ4**: Do specialized prompting strategies improve synthesis quality?

## Methodology

### Dataset Construction

**15 Curated Tasks** across 4 categories:
- **Basic Syntax** (6 tasks): Factorial, Fibonacci, array operations
- **Reference Capabilities** (3 tasks): iso, val, box usage
- **Actor Concurrency** (3 tasks): Message passing, worker pools
- **Complex Systems** (3 tasks): Producer-consumer, banking, distributed counters

Each task includes:
- Problem description
- Reference solution
- Test cases
- Difficulty rating

### Prompting Strategies (8 Total)

1. **Zero-Shot**: Baseline, no examples
2. **Few-Shot**: 2-3 Pony examples
3. **Chain-of-Thought**: Step-by-step reasoning
4. **Self-Debug**: Generate, review, fix
5. **Transfer-Rust**: Leverage Rust similarity
6. **Transfer-C++**: Map from C++ concurrency
7. **Capability-Focused**: Emphasize capabilities
8. **Actor-Focused**: Emphasize actor patterns

### Evaluation Metrics

- **Compilation Success Rate**: % that compile with ponyc
- **Syntax Correctness**: Proper Pony syntax
- **Capability Correctness**: Appropriate capability usage
- **Functional Correctness**: Passes test cases (when available)
- **Execution Time**: Time per evaluation

### Models Tested

Primary: Google Gemini Pro
Optional: OpenAI GPT-4, Anthropic Claude

## Project Structure

```
ponylang-llm-eval/
├── dataset/                 # Task definitions
│   └── pony_tasks.json      # 15 curated tasks
├── prompts/                 # Prompting strategies
│   └── prompting_strategies.py
├── evaluation/              # Core evaluation
│   ├── evaluator.py         # Main harness
│   ├── analyze_results.py   # Analysis/viz
│   ├── batch_runner.py      # Batch configs
│   └── utils.py             # Helper functions
├── pony_examples/           # Reference implementations
├── docs/                    # Documentation
│   ├── PROMPTING_STRATEGIES.md
│   └── TROUBLESHOOTING.md
├── tests/                   # Unit tests
├── notebooks/               # Jupyter notebooks
├── results/                 # Generated results
├── config.yaml              # Configuration
├── requirements.txt         # Dependencies
├── setup.py                 # Setup validation
├── quickstart.sh            # Quick start script
├── Makefile                 # Common commands
└── README.md                # Main documentation
```

## Key Features

1. **Automated Compilation Testing**: Every generated code sample is compiled with ponyc
2. **Multiple Prompting Strategies**: Compare effectiveness across 8 strategies
3. **Comprehensive Analysis**: Automated generation of charts, heatmaps, reports
4. **Extensible Architecture**: Easy to add new tasks, strategies, or models
5. **Research-Ready**: Designed for academic publication

## Usage Workflow

### 1. Setup
```bash
# Install Pony compiler
brew install ponyc  # or appropriate for your OS

# Install Python dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY='your_key'

# Validate setup
python setup.py
```

### 2. Run Evaluation
```bash
# Quick test (3 tasks, 2 strategies)
make quick

# Full evaluation
make run

# Batch evaluations
make batch
```

### 3. Analyze Results
```bash
# Automatic analysis
make analyze

# Or manual
cd evaluation
python analyze_results.py ../results/eval_*/evaluation_results.json
```

### 4. Review Results

Results include:
- `evaluation_results.json`: Raw data
- `evaluation_report.txt`: Summary
- `analysis/`: Charts and statistics
  - Strategy success rates
  - Category performance
  - Heatmaps
  - Error analysis

## Expected Outcomes

Based on preliminary experiments:

**Overall Success Rates** (estimated):
- Basic Syntax: 60-80%
- Reference Capabilities: 40-60%
- Actor Concurrency: 50-70%
- Complex Systems: 30-50%

**Best Strategies** (by category):
- Basic: Few-Shot, Transfer-Rust
- Capabilities: Capability-Focused, Transfer-Rust
- Actors: Actor-Focused, Chain-of-Thought
- Complex: Chain-of-Thought, Transfer-Rust

**Common Errors**:
- Incorrect capability usage (iso vs ref vs val)
- Missing recover blocks
- Sendable violations
- Actor callback syntax errors

## Academic Applications

This framework supports research on:

1. **LLM Generalization**: How do models trained on mainstream languages handle niche paradigms?
2. **Prompting Engineering**: Which strategies work best for capability systems?
3. **Transfer Learning**: Can knowledge from similar languages (Rust, Erlang) transfer to Pony?
4. **Synthetic Data**: Can generated code be used to improve LLM training data?

## Publication Potential

Suitable for:
- Machine programming workshops (MAPS, ML4Code)
- Programming language venues (PLDI, OOPSLA)
- Software engineering conferences (ICSE, FSE)
- AI conferences with PL tracks (AAAI, IJCAI)

## Future Extensions

1. **Fine-Tuning**: Train models on generated Pony corpus
2. **RAG Systems**: Retrieve-augment generation with Pony docs
3. **Iterative Refinement**: Multiple generation-test cycles
4. **User Studies**: Compare with human developers
5. **Cross-Language**: Extend to other actor languages (Erlang, Elixir, Scala Akka)

## Limitations

1. **Dataset Size**: 15 tasks is small; more needed for robust conclusions
2. **Manual Test Cases**: Limited automated functional testing
3. **Single LLM Focus**: Primarily tested on Gemini
4. **Compilation-Only**: Doesn't test runtime behavior extensively
5. **No Performance Metrics**: Doesn't evaluate generated code performance

## Contributing

Contributions welcome! Areas for improvement:
- Additional tasks (especially advanced capabilities)
- New prompting strategies
- Support for more LLMs
- Enhanced test cases
- Performance benchmarks

## Citation

If you use this framework in your research:

```bibtex
@misc{ponyllmeval2024,
  title={Evaluating LLM Code Synthesis Capabilities on Pony Language},
  author={Your Name},
  year={2024},
  institution={Johns Hopkins University},
  note={Machine Programming Course Project}
}
```

## License

MIT License - See LICENSE file

## Acknowledgments

- **Pony Language Team**: For excellent documentation and tooling
- **Google**: For Gemini API access
- **Johns Hopkins University**: For academic support
- **Professor Sabnani**: For course guidance

## Contact

- GitHub: [your-repo-url]
- Email: [your-email]
- Course: Machine Programming, JHU

---

## Appendix: Technical Details

### Compilation Process

For each generated code sample:
1. Wrap in Main actor if needed
2. Write to temporary directory
3. Run `ponyc <directory>`
4. Capture stdout/stderr
5. Record success/failure
6. Extract error messages

### Capability System Primer

Pony's six reference capabilities:

- **iso**: Isolated mutable, unique reference
- **trn**: Transition, becoming iso or val
- **ref**: Mutable reference (local only)
- **val**: Immutable, globally shareable
- **box**: Read-only reference
- **tag**: Opaque, can only send messages

Rules:
- Actors can only receive: iso, val, tag
- Reading requires: ref, val, box
- Writing requires: ref, iso, trn

### Actor Model Primer

Key concepts:
- Actors are independent entities
- Communication via asynchronous messages
- No shared mutable state
- Sequential message processing per actor
- Behaviors (`be`) handle messages

Example:
```pony
actor Counter
  var _count: U64 = 0
  
  be increment() =>
    _count = _count + 1
  
  be get(callback: {(U64)} val) =>
    callback(_count)
```

---

*This documentation is maintained as part of the Pony LLM Evaluation Framework project*
*Last Updated: December 2024*
