#!/usr/bin/env python3
"""
Unit tests for Pony LLM Evaluation Framework
"""

import unittest
import json
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent / 'prompts'))
sys.path.append(str(Path(__file__).parent.parent / 'evaluation'))

from prompting_strategies import get_prompt, ZERO_SHOT_TEMPLATE
from evaluator import extract_code_from_response, PonyCompiler

class TestPromptGeneration(unittest.TestCase):
    """Test prompt generation for different strategies"""
    
    def test_zero_shot_prompt(self):
        """Test zero-shot prompt generation"""
        task_desc = "Create a factorial function"
        prompt = get_prompt('zero_shot', task_desc)
        
        self.assertIn(task_desc, prompt)
        self.assertIn("Pony", prompt)
        self.assertIsInstance(prompt, str)
    
    def test_few_shot_prompt(self):
        """Test few-shot prompt includes examples"""
        task_desc = "Create a counter actor"
        prompt = get_prompt('few_shot', task_desc)
        
        self.assertIn("Example", prompt)
        self.assertIn(task_desc, prompt)
        self.assertIn("```pony", prompt)
    
    def test_chain_of_thought_prompt(self):
        """Test chain-of-thought includes reasoning steps"""
        task_desc = "Create an isolated counter"
        prompt = get_prompt('chain_of_thought', task_desc)
        
        self.assertIn("step-by-step", prompt.lower())
        self.assertIn("REASONING", prompt)
        self.assertIn("CODE", prompt)
    
    def test_all_strategies_return_strings(self):
        """Test all strategies return valid strings"""
        strategies = [
            'zero_shot', 'few_shot', 'chain_of_thought',
            'self_debug', 'transfer_rust', 'transfer_cpp',
            'capability_focused', 'actor_focused'
        ]
        
        task_desc = "Test task"
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                prompt = get_prompt(strategy, task_desc)
                self.assertIsInstance(prompt, str)
                self.assertGreater(len(prompt), 0)

class TestCodeExtraction(unittest.TestCase):
    """Test code extraction from LLM responses"""
    
    def test_extract_from_pony_block(self):
        """Test extracting code from ```pony blocks"""
        response = """
Here's the code:
```pony
actor Main
  new create(env: Env) =>
    env.out.print("Hello")
```
"""
        code = extract_code_from_response(response)
        self.assertIn("actor Main", code)
        self.assertNotIn("```", code)
    
    def test_extract_from_generic_block(self):
        """Test extracting from generic code blocks"""
        response = """
```
actor Main
  new create(env: Env) =>
    env.out.print("Test")
```
"""
        code = extract_code_from_response(response)
        self.assertIn("actor Main", code)
    
    def test_multiple_blocks_returns_last(self):
        """Test that multiple blocks return the last one"""
        response = """
First attempt:
```pony
// wrong code
```

Corrected version:
```pony
actor Main
  new create(env: Env) =>
    env.out.print("Correct")
```
"""
        code = extract_code_from_response(response)
        self.assertIn("Correct", code)
        self.assertNotIn("wrong", code)
    
    def test_no_code_blocks_returns_all(self):
        """Test response without code blocks"""
        response = "actor Main\n  new create(env: Env) =>\n    None"
        code = extract_code_from_response(response)
        self.assertEqual(code, response.strip())

class TestDatasetValidation(unittest.TestCase):
    """Test dataset structure and validity"""
    
    @classmethod
    def setUpClass(cls):
        """Load dataset once for all tests"""
        dataset_path = Path(__file__).parent.parent / 'dataset' / 'pony_tasks.json'
        with open(dataset_path, 'r') as f:
            cls.dataset = json.load(f)
    
    def test_dataset_has_metadata(self):
        """Test dataset has required metadata"""
        self.assertIn('metadata', self.dataset)
        self.assertIn('version', self.dataset['metadata'])
        self.assertIn('language', self.dataset['metadata'])
    
    def test_dataset_has_tasks(self):
        """Test dataset has tasks array"""
        self.assertIn('tasks', self.dataset)
        self.assertIsInstance(self.dataset['tasks'], list)
        self.assertGreater(len(self.dataset['tasks']), 0)
    
    def test_all_tasks_have_required_fields(self):
        """Test all tasks have required fields"""
        required_fields = [
            'id', 'category', 'difficulty', 'title',
            'description', 'prompt', 'reference_solution'
        ]
        
        for task in self.dataset['tasks']:
            with self.subTest(task_id=task.get('id', 'unknown')):
                for field in required_fields:
                    self.assertIn(field, task)
                    self.assertIsInstance(task[field], str)
                    self.assertGreater(len(task[field]), 0)
    
    def test_task_categories_valid(self):
        """Test task categories are valid"""
        valid_categories = [
            'basic_syntax',
            'reference_capabilities',
            'actor_concurrency',
            'complex_systems'
        ]
        
        for task in self.dataset['tasks']:
            with self.subTest(task_id=task['id']):
                self.assertIn(task['category'], valid_categories)
    
    def test_task_difficulties_valid(self):
        """Test task difficulties are valid"""
        valid_difficulties = ['easy', 'medium', 'hard', 'expert']
        
        for task in self.dataset['tasks']:
            with self.subTest(task_id=task['id']):
                self.assertIn(task['difficulty'], valid_difficulties)
    
    def test_reference_solutions_are_valid_pony(self):
        """Test reference solutions contain Pony keywords"""
        pony_keywords = ['actor', 'class', 'primitive', 'fun', 'be', 'new', 'let', 'var']
        
        for task in self.dataset['tasks']:
            solution = task['reference_solution']
            with self.subTest(task_id=task['id']):
                # At least one Pony keyword should be present
                has_keyword = any(keyword in solution for keyword in pony_keywords)
                self.assertTrue(has_keyword, 
                    f"Reference solution should contain Pony keywords")

class TestPonyCompiler(unittest.TestCase):
    """Test Pony compiler integration"""
    
    def setUp(self):
        """Set up test environment"""
        try:
            self.compiler = PonyCompiler()
            self.has_ponyc = True
        except RuntimeError:
            self.has_ponyc = False
    
    def test_compiler_available(self):
        """Test that ponyc is available"""
        if not self.has_ponyc:
            self.skipTest("ponyc not installed")
        
        self.assertIsNotNone(self.compiler)
    
    def test_compile_valid_code(self):
        """Test compiling valid Pony code"""
        if not self.has_ponyc:
            self.skipTest("ponyc not installed")
        
        code = """
actor Main
  new create(env: Env) =>
    env.out.print("Hello World")
"""
        work_dir = Path('/tmp/pony_test_valid')
        work_dir.mkdir(exist_ok=True)
        
        success, error = self.compiler.compile_code(code, work_dir)
        self.assertTrue(success, f"Valid code should compile: {error}")
    
    def test_compile_invalid_code(self):
        """Test compiling invalid Pony code"""
        if not self.has_ponyc:
            self.skipTest("ponyc not installed")
        
        code = """
actor Main
  this is not valid pony code!!!
"""
        work_dir = Path('/tmp/pony_test_invalid')
        work_dir.mkdir(exist_ok=True)
        
        success, error = self.compiler.compile_code(code, work_dir)
        self.assertFalse(success, "Invalid code should not compile")
        self.assertIsNotNone(error)

def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
