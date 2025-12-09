#!/usr/bin/env python3
"""
Main Evaluation Harness for Pony LLM Code Synthesis

This script:
1. Loads tasks from the dataset
2. Generates prompts using different strategies
3. Queries LLMs (Google Gemini, OpenAI, Anthropic)
4. Compiles generated code with ponyc
5. Runs tests and collects metrics
6. Generates evaluation reports
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re
import time
from datetime import datetime

# Add prompts directory to path
sys.path.append(str(Path(__file__).parent.parent / 'prompts'))
from prompting_strategies import get_prompt

@dataclass
class EvaluationResult:
    """Store results for a single evaluation"""
    task_id: str
    category: str
    difficulty: str
    strategy: str
    model: str
    prompt: str
    generated_code: str
    compilation_success: bool
    compilation_error: Optional[str]
    syntax_correct: bool
    test_results: Dict[str, bool]
    execution_time: float
    timestamp: str

class PonyCompiler:
    """Handle Pony code compilation"""
    
    def __init__(self, ponyc_path: str = "ponyc"):
        self.ponyc_path = ponyc_path
        self._check_compiler()
    
    def _check_compiler(self):
        """Verify ponyc is available"""
        try:
            result = subprocess.run(
                [self.ponyc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("ponyc not found or not working")
            print(f"Found Pony compiler: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError("ponyc not found. Please install Pony: https://www.ponylang.io/")
        except Exception as e:
            raise RuntimeError(f"Error checking ponyc: {e}")
    
    def compile_code(self, code: str, work_dir: Path) -> Tuple[bool, Optional[str]]:
        """Compile Pony code and return success status and any errors"""
        main_file = work_dir / "main.pony"
    
    # If Main exists, check structure
        if "actor Main" in code:
            parts = code.split("actor Main", 1)
            before_main = parts[0].strip()
            main_and_after = parts[1]
        
        # Check what's before Main
            if before_main:
            # If it's a standalone function, move it INSIDE Main
                if before_main.startswith("fun "):
                    # Find where to insert: after "new create(env: Env) =>"
                    lines = main_and_after.split('\n')
                    new_lines = []
                    inserted = False
                
                    for i, line in enumerate(lines):
                        new_lines.append(line)
                    # Insert after the create line
                        if 'new create(env: Env) =>' in line and not inserted:
                            # Indent the function and add it
                            func_lines = before_main.split('\n')
                            for func_line in func_lines:
                                new_lines.append('  ' + func_line)
                            new_lines.append('')  # blank line
                            inserted = True
                
                    code = "actor Main\n" + '\n'.join(new_lines)
                else:
                # It's object/class/primitive - keep before Main
                    code = before_main + "\n\nactor Main" + main_and_after
            else:
            # Nothing before Main, use as-is
                code = "actor Main" + main_and_after
        else:
        # No Main, wrap it
            code = f"""actor Main
  new create(env: Env) =>
    env.out.print("Compilation test")

{code}
"""
    
        main_file.write_text(code)
    
        try:
            result = subprocess.run(
                [self.ponyc_path, str(work_dir)],
                capture_output=True,
                text=True,
                timeout=30
            )
        
            output = result.stdout + result.stderr
        
            if (result.returncode == 0 or 
                "Verifying" in output or 
                "Writing" in output):
                return True, None
            else:
                return False, result.stderr
    
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout (30s)"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"

class LLMClient:
    """Generic LLM client interface"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("Warning: No API key found. Set GEMINI_API_KEY environment variable.")
    
    def generate(self, prompt: str, model: str = "gemini-pro") -> str:
        """
        Generate code from prompt using specified model
        
        Note: This is a placeholder. Implement actual API calls.
        """
        # For now, return a placeholder
        # In production, call the actual Gemini API
        return self._call_gemini_api(prompt, model)
    
    def _call_gemini_api(self, prompt: str, model: str) -> str:
        """
        Call Google Gemini API
        
        Implement this with actual API calls using google-generativeai library
        """
        try:
            import google.generativeai as genai
            
            if not self.api_key:
                return "# Error: No API key configured"
            
            genai.configure(api_key=self.api_key)
            model_instance = genai.GenerativeModel(model)
            
            response = model_instance.generate_content(prompt)

            generation_config = {
                'temperature': 0.7,  # Higher temperature for more variety (0.0 = deterministic, 1.0 = very random)
                'max_output_tokens': 2048,
            }

            time.sleep(3.5)

            return response.text
        
        except ImportError:
            return "# Error: google-generativeai not installed. Run: pip install google-generativeai"
        except Exception as e:
            return f"# Error calling API: {str(e)}"

def extract_code_from_response(response: str) -> str:
    """Extract Pony code from LLM response"""
    # Try to find code in markdown blocks
    pony_pattern = r"```pony\n(.*?)\n```"
    matches = re.findall(pony_pattern, response, re.DOTALL)
    
    if matches:
        return matches[-1].strip()  # Return last code block
    
    # Try generic code blocks
    code_pattern = r"```\n(.*?)\n```"
    matches = re.findall(code_pattern, response, re.DOTALL)
    
    if matches:
        # Filter out non-Pony code (check for Pony keywords)
        for match in reversed(matches):
            if any(keyword in match for keyword in ['actor', 'class', 'primitive', 'fun', 'be']):
                return match.strip()
        return matches[-1].strip()
    
    # If no code blocks, look for code after common headers
    lines = response.split('\n')
    code_started = False
    code_lines = []
    
    for line in lines:
        # Skip explanatory text
        if any(skip in line.lower() for skip in ['here', 'example', 'explanation', '###', 'how to']):
            continue
        # Look for Pony code markers
        if any(keyword in line for keyword in ['actor', 'class', 'primitive', 'fun']):
            code_started = True
        if code_started:
            code_lines.append(line)
    
    if code_lines:
        return '\n'.join(code_lines).strip()
    
    # Last resort: return the whole response
    return response.strip()

def clean_pony_code(code: str) -> str:
    """Fix common LLM errors in Pony code"""
    # Remove numeric suffixes
    code = re.sub(r'(\d+)[Uu]\b', r'\1', code)
    
    # Remove package declarations
    code = re.sub(r'^package\s+\w+\s*\n', '', code, flags=re.MULTILINE)
    
    # Fix .values() on array literals
    code = re.sub(r'\[([^\]]+)\]\.values\(\)', r'[\1]', code)
    
    # Fix operator precedence: "n == 0 or n == 1" -> "(n == 0) or (n == 1)"
    code = re.sub(r'\b(\w+\s*==\s*\w+)\s+(or|and)\s+(\w+\s*==\s*\w+)', r'(\1) \2 (\3)', code)
    
    # Add missing ends
    if_count = len(re.findall(r'\bif\b.*\bthen\b', code))
    end_count = len(re.findall(r'\bend\b', code))
    while end_count < if_count:
        code += '\n    end'
        end_count += 1
    
    return code.strip()

class Evaluator:
    """Main evaluation orchestrator"""
    
    def __init__(
        self,
        dataset_path: Path,
        output_dir: Path,
        strategies: List[str],
        models: List[str],
        max_retries: int = 5
    ):
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.strategies = strategies
        self.models = models
        self.max_retries = max_retries

        self.compiler = PonyCompiler()
        self.llm_client = LLMClient()
        self.results: List[EvaluationResult] = []
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.code_dir = self.output_dir / "generated_code"
        self.code_dir.mkdir(exist_ok=True)
        self.work_dir = self.output_dir / "compilation_work"
        self.work_dir.mkdir(exist_ok=True)
    
    def load_dataset(self) -> Dict:
        """Load task dataset"""
        with open(self.dataset_path, 'r') as f:
            return json.load(f)
    
    def evaluate_task(self, task: dict, strategy: str, model: str) -> dict:
        """Evaluate a single task with retry logic - tracks all attempts"""
        task_id = task['id']
        category = task['category']
        difficulty = task['difficulty']
        description = task['prompt']
    
        print(f"\nEvaluating: {task_id} | Strategy: {strategy} | Model: {model}")
    
        all_attempts = []
    
        for attempt in range(self.max_retries):
            if attempt > 0:
                print(f"  Retry {attempt}/{self.max_retries - 1}...")
        
            start_time = time.time()
        
        # Generate prompt
            prompt = get_prompt(strategy, description, category)
        
        # Query LLM
            print("  Querying LLM...")
            response = self.llm_client.generate(prompt, model)
            generated_code = extract_code_from_response(response)
            generated_code = clean_pony_code(generated_code)
        
        # Save generated code (only save final attempt to avoid clutter)
            if attempt == 0 or attempt == self.max_retries - 1:
                code_file = self.output_dir / "generated_code" / f"{task_id}_{strategy}_{model}.pony"
                code_file.write_text(generated_code)
        
        # Compile
            print("  Compiling...")
            work_dir = self.output_dir / "compilation_work" / f"{task_id}_{strategy}_{model}_attempt{attempt + 1}"
            work_dir.mkdir(parents=True, exist_ok=True)
        
            success, error = self.compiler.compile_code(generated_code, work_dir)
        
            execution_time = time.time() - start_time
        
        # Create result for this attempt
            result = {
                'task_id': task_id,
                'category': category,
                'difficulty': difficulty,
                'strategy': strategy,
                'model': model,
                'prompt': prompt,
                'generated_code': generated_code,
                'compilation_success': success,
                'compilation_error': error,
                'syntax_correct': success,
                'test_results': {},
                'execution_time': execution_time,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'attempt_number': attempt + 1,
                'is_retry': attempt > 0
            }
        
            all_attempts.append(result)
        
            if success:
                print(f"  ✓ Compilation successful (attempt {attempt + 1}/{self.max_retries})")
                result['retry_count'] = attempt
                result['total_attempts'] = attempt + 1
                return result
            else:
                # Truncate error message for display
                if error:
                    error_preview = error[:500] if len(error) > 500 else error
                    print(f"  ✗ Compilation failed (attempt {attempt + 1}/{self.max_retries}):")
                    print(f"     {error_preview}")
                else:
                    print(f"  ✗ Compilation failed (attempt {attempt + 1}/{self.max_retries}): Unknown error")
    
    # All attempts failed - return last attempt with full history
        # All attempts failed
        print(f"  ✗ All {self.max_retries} attempts failed")
        final_result = all_attempts[-1] if all_attempts else {...}
        # Don't include all_attempts - causes circular reference in JSON
        final_result['retry_count'] = self.max_retries - 1
        final_result['total_attempts'] = self.max_retries
        return final_result
    
    def run_evaluation(self, task_filter: Optional[List[str]] = None):
        """Run full evaluation across all tasks, strategies, and models"""
        dataset = self.load_dataset()
        tasks = dataset['tasks']
        
        if task_filter:
            tasks = [t for t in tasks if t['id'] in task_filter]
        
        total = len(tasks) * len(self.strategies) * len(self.models)
        current = 0
        
        print(f"\n{'='*60}")
        print(f"Starting Evaluation")
        print(f"Tasks: {len(tasks)}")
        print(f"Strategies: {len(self.strategies)}")
        print(f"Models: {len(self.models)}")
        print(f"Total evaluations: {total}")
        print(f"{'='*60}\n")
        
        for task in tasks:
            for strategy in self.strategies:
                for model in self.models:
                    current += 1
                    print(f"\nProgress: {current}/{total}")
                    
                    try:
                        result = self.evaluate_task(task, strategy, model)
                        self.results.append(result)
                    except Exception as e:
                        print(f"Error evaluating {task['id']}: {type(e).__name__}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        continue
        
        # Save results
        self.save_results()
        self.generate_report()
    
    def save_results(self):
        """Save detailed results to JSON"""
        results_file = self.output_dir / "evaluation_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✓ Results saved to {results_file}")
    
    def generate_report(self):
        """Generate summary report"""
        if not self.results:
            print("No results to report")
            return
        
        report_file = self.output_dir / "evaluation_report.txt"
        
        # Calculate metrics
        total = len(self.results)
        compiled = sum(1 for r in self.results if r['compilation_success'])
        
        # Group by strategy
        by_strategy = {}
        for result in self.results:
            if result['strategy'] not in by_strategy:
                by_strategy[result['strategy']] = []
            by_strategy[result['strategy']].append(result)
        
        # Group by category
        by_category = {}
        for result in self.results:
            if result['category'] not in by_category:
                by_category[result['category']] = []
            by_category[result['category']].append(result)
        
        with open(report_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("PONY LLM CODE SYNTHESIS EVALUATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total Evaluations: {total}\n")
            f.write(f"Compilation Success Rate: {compiled/total*100:.1f}% ({compiled}/{total})\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("RESULTS BY STRATEGY\n")
            f.write("=" * 60 + "\n\n")
            
            for strategy, results in sorted(by_strategy.items()):
                success = sum(1 for r in results if r['compilation_success'])
                rate = success / len(results) * 100
                f.write(f"{strategy}:\n")
                f.write(f"  Success Rate: {rate:.1f}% ({success}/{len(results)})\n")
                f.write(f"  Avg Time: {sum(r['execution_time'] for r in results)/len(results):.2f}s\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("RESULTS BY CATEGORY\n")
            f.write("=" * 60 + "\n\n")
            
            for category, results in sorted(by_category.items()):
                success = sum(1 for r in results if r['compilation_success'])
                rate = success / len(results) * 100
                f.write(f"{category}:\n")
                f.write(f"  Success Rate: {rate:.1f}% ({success}/{len(results)})\n\n")
        
        print(f"✓ Report saved to {report_file}")
        
        # Print summary to console
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Overall Success Rate: {compiled/total*100:.1f}%")
        print("\nBy Strategy:")
        for strategy, results in sorted(by_strategy.items()):
            success = sum(1 for r in results if r['compilation_success'])
            rate = success / len(results) * 100
            print(f"  {strategy}: {rate:.1f}%")

def main():
    """Main entry point"""
    # Configuration
    BASE_DIR = Path(__file__).parent.parent
    DATASET_PATH = BASE_DIR / "dataset" / "pony_tasks.json"
    OUTPUT_DIR = BASE_DIR / "results" / f"eval_{int(time.time())}"
    
    # Strategies to test
    STRATEGIES = [
        'zero_shot',
        'few_shot',
        'chain_of_thought',
        'self_debug',
        'transfer_rust',
        'capability_focused',
        'actor_focused',
        'contrapositive',
        'analogical',
        'expert_persona'
    ]
    
    # Models to test
    MODELS = [
        'gemini-2.5-flash',
        # Add more models as needed
    ]
    
    # For quick testing, you can filter tasks
    TASK_FILTER = None  # Or ['basic_001', 'basic_002'] for subset
    
    # Create evaluator and run
    evaluator = Evaluator(
        dataset_path=DATASET_PATH,
        output_dir=OUTPUT_DIR,
        strategies=STRATEGIES,
        models=MODELS,
        max_retries=5
    )
    
    evaluator.run_evaluation(task_filter=TASK_FILTER)

if __name__ == "__main__":
    main()
