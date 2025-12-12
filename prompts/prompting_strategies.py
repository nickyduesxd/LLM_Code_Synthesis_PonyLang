"""
Prompting Strategy Templates for Pony LLM Evaluation

This module contains different prompting strategies to test LLM code synthesis:
1. Zero-shot
2. Few-shot
3. Chain-of-thought
4. Self-debug
5. Transfer (from C++/Rust)
"""

PONY_LANGUAGE_CONTEXT = """
Pony is an actor-model programming language with:
- Reference capabilities: iso (isolated), trn (transition), ref (reference), val (value), box (read-only), tag (opaque)
- Actor-based concurrency with message passing
- No data races by design
- Compile-time memory safety
"""

# ========== ZERO-SHOT PROMPTING ==========
ZERO_SHOT_TEMPLATE = """
{task_description}

Write complete, compilable Pony code that solves this problem.

Requirements:
- Use proper Pony syntax
- Apply appropriate reference capabilities
- Ensure code compiles with ponyc
- Follow Pony best practices

Provide only the code, no explanations.
"""

# ========== FEW-SHOT PROMPTING ==========
FEW_SHOT_TEMPLATE = """
{language_context}

Here are examples of Pony code:

Example 1: Simple Class
```pony
class Point
  let x: F64
  let y: F64
  
  new create(x': F64, y': F64) =>
    x = x'
    y = y'
  
  fun distance_from_origin(): F64 =>
    (x.pow(2) + y.pow(2)).sqrt()
```

Example 2: Simple Primitive
```pony
primitive Factorial
  fun apply(n: U64): U64 =>
    if n <= 1 then
      1
    else
      n * apply(n - 1)
    end
```

Example 3: Actor with Message Passing
```pony
actor Counter
  var _count: U64 = 0
  
  be increment() =>
    _count = _count + 1
  
  be get_count(callback: {(U64)} val) =>
    callback(_count)
```

Now solve this problem:

{task_description}

Provide complete, compilable Pony code.
"""

# ========== CHAIN-OF-THOUGHT PROMPTING ==========
CHAIN_OF_THOUGHT_TEMPLATE = """
{language_context}

{task_description}

Let's solve this step-by-step:

1. First, identify what data structures and types we need
2. Determine the appropriate reference capabilities for thread safety
3. Decide if we need actors, classes, or primitives
4. Consider how data flows through the system
5. Implement the solution with proper Pony syntax

Think through each step, then provide the complete Pony code implementation.

Format your response as:
REASONING:
[Your step-by-step analysis]

CODE:
```pony
[Your implementation]
```
"""

# ========== SELF-DEBUG PROMPTING ==========
SELF_DEBUG_TEMPLATE = """
{task_description}

Write Pony code to solve this problem. Then:
1. Review your code for common Pony errors:
   - Incorrect reference capabilities
   - Type mismatches
   - Missing recover blocks
   - Improper actor message passing
   - Capability violations

2. Check if your code would compile with ponyc
3. Revise any issues you find

Provide your initial solution and then your debugged final version.

Format:
INITIAL SOLUTION:
```pony
[Your first attempt]
```

ISSUES FOUND:
[List any problems]

FINAL SOLUTION:
```pony
[Your corrected code]
```
"""

# ========== TRANSFER LEARNING PROMPTING ==========
TRANSFER_RUST_TEMPLATE = """
{task_description}

First, implement this in Rust, then convert it to Pony.

Step 1: Rust Implementation
Think about how you would solve this using Rust's ownership system.

Step 2: Map Rust Concepts to Pony
- Rust's & -> Pony's box or ref
- Rust's &mut -> Pony's ref
- Rust's ownership -> Pony's iso
- Rust's Arc/Rc -> Pony's val or tag
- Rust's Send -> Pony's iso or val

Step 3: Pony Implementation
Convert your Rust solution to Pony, applying the appropriate reference capabilities.

Provide both implementations:

RUST VERSION:
```rust
[Your Rust code]
```

PONY VERSION:
```pony
[Your Pony code]
```
"""

TRANSFER_CPP_TEMPLATE = """
{task_description}

First, implement this in C++, then convert it to Pony.

Step 1: C++ Implementation
Consider how you would solve this using C++ with proper memory management.

Step 2: Map C++ Concepts to Pony
- C++ pointers -> Pony reference capabilities
- C++ const -> Pony's val or box
- C++ smart pointers -> Pony's iso or val
- C++ threading -> Pony's actors
- C++ locks/mutexes -> Not needed in Pony (actors handle this)

Step 3: Pony Implementation
Convert your C++ solution to Pony, replacing manual synchronization with actors.

Provide both implementations:

C++ VERSION:
```cpp
[Your C++ code]
```

PONY VERSION:
```pony
[Your Pony code]
```
"""

# ========== CAPABILITY-FOCUSED PROMPTING ==========
CAPABILITY_FOCUSED_TEMPLATE = """
{language_context}

{task_description}

Special focus on reference capabilities:

Reference Capability Guidelines:
- `iso`: Isolated, unique mutable reference (like Rust's owned mutable)
- `trn`: Transition, preparing to become iso or val
- `ref`: Regular mutable reference (for local use)
- `val`: Immutable, globally shareable (like Rust's Arc<T>)
- `box`: Read-only reference (like Rust's &T)
- `tag`: Opaque reference, can only send messages (for actors)

For this problem:
1. Identify which data needs to be mutable vs immutable
2. Determine if data will be shared across actors
3. Choose the most restrictive capability that works
4. Use `recover` blocks if you need to change capabilities

Provide your solution with comments explaining capability choices:

```pony
[Your implementation with capability reasoning]
```
"""

# ========== ACTOR-FOCUSED PROMPTING ==========
ACTOR_FOCUSED_TEMPLATE = """
{language_context}

{task_description}

Actor-based design considerations:
- Actors process messages sequentially (no race conditions)
- Messages must have sendable capabilities (iso, val, tag)
- Behaviors (be) are asynchronous message handlers
- Use callbacks or promises for return values
- Each actor has its own heap

Design guidelines:
1. Identify what needs to be an actor vs a class
2. Define the messages (behaviors) each actor accepts
3. Ensure proper capabilities for message parameters
4. Consider how actors communicate results back

Provide your actor-based solution:

```pony
[Your implementation]
```
"""

# ========== CONTRASTIVE PROMPTING ==========
CONTRASTIVE_TEMPLATE = """
{language_context}

{task_description}

Common Pony Mistakes to AVOID:

WRONG - Standalone functions:
```pony
fun factorial(n: U64): U64 =>  // Error: functions must be in class/primitive/actor
  n * factorial(n - 1)
```

CORRECT - Functions in primitives:
```pony
primitive Factorial
  fun apply(n: U64): U64 =>
    if n <= 1 then 1 else n * apply(n - 1) end
```

WRONG - Missing constructor:
```pony
class Counter
  var _count: U64  // Error: must initialize in constructor
```

CORRECT - Proper initialization:
```pony
class Counter
  var _count: U64
  new create() => _count = 0
```

WRONG - Capability violations:
```pony
actor Main
  new create(env: Env) =>
    let arr = [1, 2, 3]  // Error: array literal type unclear
```

CORRECT - Explicit types:
```pony
actor Main
  new create(env: Env) =>
    let arr: Array[U64] val = [1; 2; 3]
```

Now solve the task, avoiding these common errors:
```pony
[Your correct implementation]
```
"""

# ========== ANALOGICAL PROMPTING ==========
ANALOGICAL_TEMPLATE = """
{language_context}

Task: {task_description}

Before solving this, let's think of similar Pony programming problems and how they were solved.

Step 1: Generate 2-3 analogous problems in Pony that share similar patterns
Step 2: Briefly show how those analogous problems would be solved
Step 3: Apply the learned patterns to solve the current task

Format your response as:

ANALOGOUS PROBLEMS:
Problem 1: [Similar problem description]
Solution approach: [Brief solution sketch]

Problem 2: [Similar problem description]  
Solution approach: [Brief solution sketch]

SOLUTION TO CURRENT TASK:
```pony
[Your implementation applying the patterns]
```
"""

# ========== EXPERT METACOGNITIVE PROMPTING ==========
EXPERT_METACOGNITIVE_TEMPLATE = """
You are an expert Pony programming language developer with 10+ years of experience. You deeply understand:
- Reference capabilities and their implications for memory safety
- Actor-based concurrency patterns
- The Pony type system and compiler requirements
- Common pitfalls and best practices

{task_description}

Before coding, analyze your approach metacognitively:

METACOGNITIVE ANALYSIS:
1. What is the core challenge in this problem?
2. What Pony-specific features are most relevant (capabilities, actors, etc.)?
3. What are potential pitfalls I need to avoid?
4. What is my confidence level in different parts of the solution?
5. How will I verify correctness?

IMPLEMENTATION STRATEGY:
[Your detailed plan]

FINAL IMPLEMENTATION:
```pony
[Your code with inline comments explaining key decisions]
```

VERIFICATION:
[How you verified this would compile and work correctly]
"""


def get_prompt(strategy: str, task_description: str, category: str = "") -> str:
    """
    Generate a prompt based on the selected strategy.
    
    Args:
        strategy: One of ['zero_shot', 'few_shot', 'chain_of_thought', 
                         'self_debug', 'transfer_rust', 'transfer_cpp',
                         'capability_focused', 'actor_focused']
        task_description: The problem description
        category: Task category for specialized prompts
    
    Returns:
        Formatted prompt string
    """
    templates = {
        'zero_shot': ZERO_SHOT_TEMPLATE,
        'few_shot': FEW_SHOT_TEMPLATE,
        'chain_of_thought': CHAIN_OF_THOUGHT_TEMPLATE,
        'self_debug': SELF_DEBUG_TEMPLATE,
        'transfer_rust': TRANSFER_RUST_TEMPLATE,
        'transfer_cpp': TRANSFER_CPP_TEMPLATE,
        'capability_focused': CAPABILITY_FOCUSED_TEMPLATE,
        'actor_focused': ACTOR_FOCUSED_TEMPLATE,
        'contrapositive': CONTRASTIVE_TEMPLATE,
        'analogical': ANALOGICAL_TEMPLATE,
        'expert_persona': EXPERT_METACOGNITIVE_TEMPLATE
    }
    
    template = templates.get(strategy, ZERO_SHOT_TEMPLATE)
    
    return template.replace('{language_context}', PONY_LANGUAGE_CONTEXT).replace('{task_description}', task_description)
