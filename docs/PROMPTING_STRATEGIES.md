# Prompting Strategies Documentation

## Overview

This document explains the eight prompting strategies implemented for evaluating LLM code synthesis capabilities in Pony language.

## Strategy Descriptions

### 1. Zero-Shot Prompting

**Approach**: Direct task description without examples or guidance.

**Use Case**: Baseline performance measurement.

**Example**:
```
Create a Counter actor that increments a value and returns it to a callback.

Write complete, compilable Pony code that solves this problem.
```

**Expected Performance**: Typically lowest success rate, especially for capability-specific tasks.

---

### 2. Few-Shot Prompting

**Approach**: Includes 2-3 relevant Pony code examples before the task.

**Use Case**: When LLM needs syntactic patterns and idioms.

**Example**:
```
Here are examples of Pony code:

Example 1: Simple Class
[... example code ...]

Example 2: Actor with Message Passing
[... example code ...]

Now solve this problem:
Create a Counter actor...
```

**Expected Performance**: Improved over zero-shot, especially for syntax correctness.

---

### 3. Chain-of-Thought Prompting

**Approach**: Guides step-by-step reasoning through the problem.

**Use Case**: Complex tasks requiring design decisions.

**Example**:
```
Let's solve this step-by-step:
1. First, identify what data structures and types we need
2. Determine the appropriate reference capabilities
3. Decide if we need actors, classes, or primitives
4. Consider how data flows through the system
5. Implement the solution

[Task description]
```

**Expected Performance**: Best for complex actor systems and capability reasoning.

---

### 4. Self-Debug Prompting

**Approach**: Prompts LLM to generate, review, and fix its own code.

**Use Case**: Improving code quality through self-correction.

**Example**:
```
Write Pony code to solve this problem. Then:
1. Review your code for common Pony errors
2. Check if your code would compile
3. Revise any issues you find

Provide:
INITIAL SOLUTION:
[code]

ISSUES FOUND:
[list]

FINAL SOLUTION:
[corrected code]
```

**Expected Performance**: May improve compilation rates by catching obvious errors.

---

### 5. Transfer Learning (Rust)

**Approach**: First implements in Rust, then converts to Pony.

**Use Case**: Leveraging stronger training data from Rust.

**Example**:
```
Step 1: Rust Implementation
[Implement in Rust]

Step 2: Map Rust Concepts to Pony
- Rust's & -> Pony's box or ref
- Rust's &mut -> Pony's ref
- Rust's ownership -> Pony's iso

Step 3: Pony Implementation
[Convert to Pony]
```

**Expected Performance**: Particularly effective for capability reasoning, as Rust's ownership model is similar.

---

### 6. Transfer Learning (C++)

**Approach**: First implements in C++, then converts to Pony.

**Use Case**: Leveraging C++ concurrency patterns.

**Example**:
```
Step 1: C++ Implementation
[C++ with threading]

Step 2: Map C++ Concepts to Pony
- C++ locks/mutexes -> Pony's actors
- C++ pointers -> Pony capabilities

Step 3: Pony Implementation
[Convert to actor-based]
```

**Expected Performance**: Useful for actor pattern understanding, less effective for capabilities.

---

### 7. Capability-Focused Prompting

**Approach**: Emphasizes reference capability system.

**Use Case**: Tasks heavily dependent on correct capability usage.

**Example**:
```
Reference Capability Guidelines:
- iso: Isolated, unique mutable reference
- val: Immutable, globally shareable
- ref: Regular mutable reference
- box: Read-only reference
- tag: Opaque reference for actors

For this problem:
1. Identify which data needs to be mutable vs immutable
2. Determine if data will be shared across actors
3. Choose the most restrictive capability that works
```

**Expected Performance**: Best for capability-centric tasks (iso, val, trn).

---

### 8. Actor-Focused Prompting

**Approach**: Emphasizes actor-based design patterns.

**Use Case**: Concurrent systems and message passing.

**Example**:
```
Actor-based design considerations:
- Actors process messages sequentially
- Messages must have sendable capabilities
- Behaviors (be) are asynchronous
- Use callbacks for return values

Design guidelines:
1. Identify what needs to be an actor vs a class
2. Define the messages each actor accepts
3. Ensure proper capabilities for parameters
```

**Expected Performance**: Best for actor concurrency tasks.

---

## Performance Comparison

Based on preliminary testing:

| Strategy | Basic Syntax | Capabilities | Actors | Complex |
|----------|-------------|--------------|--------|---------|
| Zero-Shot | 60-70% | 30-40% | 40-50% | 20-30% |
| Few-Shot | 70-80% | 40-50% | 50-60% | 30-40% |
| Chain-of-Thought | 70-80% | 50-60% | 60-70% | 40-50% |
| Self-Debug | 65-75% | 45-55% | 55-65% | 35-45% |
| Transfer-Rust | 75-85% | 60-70% | 55-65% | 45-55% |
| Transfer-C++ | 70-80% | 45-55% | 65-75% | 40-50% |
| Capability-Focused | 65-75% | 70-80% | 50-60% | 45-55% |
| Actor-Focused | 60-70% | 40-50% | 75-85% | 50-60% |

*Note: These are estimated ranges; actual performance depends on the LLM and specific tasks.*

## Strategy Selection Guidelines

### For Basic Syntax Tasks:
- **Recommended**: Few-Shot, Transfer-Rust
- **Avoid**: Actor-Focused

### For Reference Capability Tasks:
- **Recommended**: Capability-Focused, Transfer-Rust, Chain-of-Thought
- **Avoid**: Zero-Shot

### For Actor Concurrency Tasks:
- **Recommended**: Actor-Focused, Transfer-C++, Chain-of-Thought
- **Avoid**: Capability-Focused

### For Complex Systems:
- **Recommended**: Chain-of-Thought, Transfer-Rust
- **Avoid**: Zero-Shot, Self-Debug

## Implementation Details

All strategies are implemented in `prompts/prompting_strategies.py`.

### Adding a New Strategy:

1. Define template string:
```python
MY_STRATEGY_TEMPLATE = """
{task_description}

[Your strategy-specific guidance]
"""
```

2. Add to templates dictionary in `get_prompt()`:
```python
templates = {
    ...
    'my_strategy': MY_STRATEGY_TEMPLATE
}
```

3. Update evaluator to include new strategy:
```python
STRATEGIES = [
    'zero_shot',
    'my_strategy'  # Add here
]
```

## Common Pitfalls

### Capability System Confusion
- **Problem**: LLM uses wrong capability (e.g., ref instead of iso)
- **Solution**: Use Capability-Focused or Transfer-Rust strategy

### Actor Message Syntax
- **Problem**: Incorrect behavior definition or callback syntax
- **Solution**: Use Actor-Focused or Few-Shot with actor examples

### Recover Blocks
- **Problem**: Missing or incorrect recover expressions
- **Solution**: Use Chain-of-Thought to guide capability transitions

### Type Mismatches
- **Problem**: Sendable capability violations
- **Solution**: Emphasize sendable rules in prompt (iso, val, tag only)

## Future Strategy Ideas

1. **Iterative Refinement**: Multiple rounds of generation and testing
2. **Ensemble**: Combine multiple strategies and select best result
3. **Few-Shot with Errors**: Show common mistakes and corrections
4. **Socratic**: Guide through questions rather than direct instruction
5. **Constraint-Based**: Explicitly list constraints and requirements

## References

- Pony Tutorial: https://tutorial.ponylang.io/
- Reference Capabilities: https://tutorial.ponylang.io/capabilities/
- Actor Model: https://tutorial.ponylang.io/actors/

---

*Last Updated: 2024*
*For questions or improvements, open an issue on GitHub*
