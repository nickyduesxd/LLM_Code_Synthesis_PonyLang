# Troubleshooting Guide

## Common Issues and Solutions

### Setup Issues

#### 1. Ponyc Compiler Not Found

**Error**:
```
RuntimeError: ponyc not found. Please install Pony
```

**Solutions**:

**macOS**:
```bash
brew install ponyc
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ponyc
```

**From Source**:
```bash
git clone https://github.com/ponylang/ponyc
cd ponyc
make
sudo make install
```

**Verify Installation**:
```bash
ponyc --version
```

---

#### 2. Python Packages Missing

**Error**:
```
ModuleNotFoundError: No module named 'google.generativeai'
```

**Solution**:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install google-generativeai pandas matplotlib seaborn numpy
```

---

#### 3. API Key Not Configured

**Error**:
```
Warning: No API key found
```

**Solutions**:

**Option 1: Environment Variable**
```bash
export GEMINI_API_KEY='your_api_key_here'
```

**Option 2: .env File**
Create `.env` in project root:
```
GEMINI_API_KEY=your_api_key_here
```

**Option 3: System-wide (Linux/Mac)**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export GEMINI_API_KEY='your_api_key_here'
```

---

### Compilation Issues

#### 4. Compilation Timeout

**Error**:
```
Compilation timeout (30s)
```

**Solution**:

Edit `config.yaml`:
```yaml
evaluation:
  compilation_timeout: 60  # Increase to 60 seconds
```

Or modify in code:
```python
# In evaluator.py
result = subprocess.run(
    [self.ponyc_path, str(work_dir)],
    capture_output=True,
    text=True,
    timeout=60  # Increase timeout
)
```

---

#### 5. High Compilation Failure Rate

**Symptoms**:
- Most generated code fails to compile
- Success rate <20%

**Possible Causes**:
1. Wrong LLM model
2. Suboptimal prompting strategy
3. Complex tasks for model

**Solutions**:

**1. Check Model**:
```python
# Use latest/best model
MODELS = ['gemini-1.5-pro']  # Instead of older versions
```

**2. Try Different Strategies**:
```python
# Start with few-shot instead of zero-shot
STRATEGIES = ['few_shot', 'chain_of_thought']
```

**3. Filter to Easier Tasks**:
```python
TASK_FILTER = ['basic_001', 'basic_002']  # Start simple
```

---

### API Issues

#### 6. API Rate Limiting

**Error**:
```
429 Too Many Requests
```

**Solution**:

Add delays between API calls in `evaluator.py`:
```python
import time

def evaluate_task(self, task, strategy, model):
    # ... existing code ...
    
    response = self.llm_client.generate(prompt, model)
    time.sleep(2)  # Add 2-second delay
    
    # ... rest of code ...
```

Or reduce concurrent evaluations:
```python
# Evaluate in smaller batches
for task in tasks:
    evaluate_task(task, strategy, model)
    time.sleep(1)  # Delay between tasks
```

---

#### 7. API Authentication Failed

**Error**:
```
401 Unauthorized
```

**Solutions**:

1. **Verify API Key**:
```bash
echo $GEMINI_API_KEY
```

2. **Check Key Validity**: Log into Google AI Studio and regenerate key

3. **Test API Key**:
```python
import google.generativeai as genai
genai.configure(api_key='your_key')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Test")
print(response.text)
```

---

### Runtime Issues

#### 8. Out of Memory

**Error**:
```
MemoryError
```

**Solutions**:

1. **Reduce Batch Size**:
```python
# In batch_runner.py
task_filter=['basic_001']  # Process fewer tasks
```

2. **Clean Work Directory**:
```bash
make clean
```

3. **Increase System Memory**: Run on machine with more RAM

---

#### 9. Slow Evaluation

**Symptoms**:
- Taking hours to complete
- Many API calls

**Solutions**:

1. **Reduce Task Count**:
```python
# Test with subset first
TASK_FILTER = ['basic_001', 'basic_002', 'basic_003']
```

2. **Reduce Strategies**:
```python
STRATEGIES = ['zero_shot', 'few_shot']  # Just 2 strategies
```

3. **Use Faster Model**:
```python
MODELS = ['gemini-pro']  # Instead of larger models
```

---

### Analysis Issues

#### 10. No Results to Analyze

**Error**:
```
FileNotFoundError: evaluation_results.json not found
```

**Solution**:

1. **Check Results Directory**:
```bash
ls -la results/
```

2. **Run Evaluation First**:
```bash
make run
```

3. **Verify Output Path**:
```python
# Check evaluator.py output_dir
print(f"Results saved to: {output_dir}")
```

---

#### 11. Visualization Errors

**Error**:
```
ImportError: No module named 'matplotlib'
```

**Solution**:
```bash
pip install matplotlib seaborn
```

If using headless server:
```python
# Add to analyze_results.py
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
```

---

### Code Generation Issues

#### 12. Generated Code Missing Main Actor

**Symptom**: Compilation fails because no main actor

**Solution**:

The evaluator automatically wraps code. Verify in `evaluator.py`:
```python
if "actor Main" not in code:
    code = f"""actor Main
  new create(env: Env) =>
    env.out.print("Compilation test")

{code}
"""
```

---

#### 13. Incorrect Capability Usage

**Symptom**: Many capability-related compilation errors

**Solution**:

1. **Use Capability-Focused Strategy**:
```python
STRATEGIES = ['capability_focused']
```

2. **Analyze Error Patterns**:
```bash
# Check error_analysis.txt in results
cat results/*/analysis/error_analysis.txt
```

3. **Improve Prompts**: Add more capability examples in few-shot

---

### Platform-Specific Issues

#### 14. Permission Denied (Linux/Mac)

**Error**:
```
Permission denied: './quickstart.sh'
```

**Solution**:
```bash
chmod +x quickstart.sh
chmod +x setup.py
```

---

#### 15. Path Issues (Windows)

**Error**:
```
FileNotFoundError: [WinError 3] Path not found
```

**Solution**:

Use forward slashes or pathlib:
```python
from pathlib import Path
path = Path('results') / 'eval_123'  # Works on all platforms
```

---

## Debugging Tips

### Enable Verbose Logging

```python
# In evaluator.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Single Task

```python
# Quick test with one task
evaluator.run_evaluation(task_filter=['basic_001'])
```

### Examine Generated Code

```bash
# View generated code
ls evaluation/generated_code/
cat evaluation/generated_code/basic_001_zero_shot_gemini-pro.pony
```

### Check Compilation Errors

```bash
# Manually compile generated code
cd evaluation/compilation_work/basic_001_zero_shot_gemini-pro/
ponyc .
```

---

## Getting Help

If you're still experiencing issues:

1. **Check Logs**: Look in `results/*/evaluation_results.json`
2. **Run Tests**: `make test` to verify setup
3. **Check Environment**: `make check`
4. **Review Dataset**: `make dataset-info`
5. **Open Issue**: Create GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment info (OS, Python version, ponyc version)

---

## Performance Optimization

### Speed Up Evaluations

1. **Parallel Processing** (advanced):
```python
from multiprocessing import Pool
# Process tasks in parallel
```

2. **Cache API Responses**:
```python
# Save responses to avoid re-querying
cache_file = f"cache/{task_id}_{strategy}.json"
```

3. **Skip Compilation** (for prompt testing):
```python
# In evaluator.py, comment out compilation step
# success, error = self.compiler.compile_code(...)
```

---

## FAQ

**Q: How long should a full evaluation take?**
A: With 15 tasks × 8 strategies × 1 model = 120 evaluations at ~10s each = ~20 minutes

**Q: Can I use multiple API keys?**
A: Yes, implement key rotation in `LLMClient` class

**Q: Can I add my own tasks?**
A: Yes! Edit `dataset/pony_tasks.json` and add new tasks

**Q: Can I test other LLMs?**
A: Yes, implement additional clients in `evaluator.py`

**Q: Where are results saved?**
A: `results/eval_<timestamp>/` directory

---

*Last Updated: 2024*
*For additional help, consult the README.md or open an issue*
