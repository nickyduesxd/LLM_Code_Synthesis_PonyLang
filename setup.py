#!/usr/bin/env python3
"""
Setup script for Pony LLM Evaluation Framework
Checks dependencies, creates directories, validates configuration
"""

import subprocess
import sys
from pathlib import Path
import os

class SetupChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.base_dir = Path(__file__).parent
    
    def check_python_version(self):
        """Check Python version >= 3.8"""
        print("Checking Python version...", end=" ")
        if sys.version_info < (3, 8):
            self.errors.append("Python 3.8+ required")
            print("❌")
        else:
            print(f"✓ (Python {sys.version_info.major}.{sys.version_info.minor})")
    
    def check_ponyc(self):
        """Check if ponyc compiler is installed"""
        print("Checking Pony compiler...", end=" ")
        try:
            result = subprocess.run(
                ["ponyc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✓ ({version})")
            else:
                self.errors.append("ponyc found but not working properly")
                print("❌")
        except FileNotFoundError:
            self.errors.append("ponyc not found. Install from: https://www.ponylang.io/")
            print("❌")
        except Exception as e:
            self.errors.append(f"Error checking ponyc: {e}")
            print("❌")
    
    def check_python_packages(self):
        """Check if required Python packages are installed"""
        print("Checking Python packages...", end=" ")
        
        required_packages = [
            'google-generativeai',
            'pandas',
            'matplotlib',
            'seaborn',
            'numpy'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        if missing:
            self.warnings.append(f"Missing packages: {', '.join(missing)}")
            self.warnings.append("Run: pip install -r requirements.txt")
            print("⚠️")
        else:
            print("✓")
    
    def check_api_keys(self):
        """Check if API keys are configured"""
        print("Checking API keys...", end=" ")
        
        api_keys = {
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
        }
        
        configured = [k for k, v in api_keys.items() if v]
        
        if not configured:
            self.warnings.append("No API keys configured")
            self.warnings.append("Set GEMINI_API_KEY environment variable")
            print("⚠️")
        else:
            print(f"✓ ({', '.join(configured)})")
    
    def create_directories(self):
        """Create necessary directories"""
        print("Creating directories...", end=" ")
        
        directories = [
            'results',
            'evaluation/generated_code',
            'evaluation/compilation_work',
            'tests'
        ]
        
        for dir_path in directories:
            full_path = self.base_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
        
        print("✓")
    
    def validate_dataset(self):
        """Validate dataset file exists and is valid JSON"""
        print("Validating dataset...", end=" ")
        
        dataset_path = self.base_dir / 'dataset' / 'pony_tasks.json'
        
        if not dataset_path.exists():
            self.errors.append(f"Dataset not found: {dataset_path}")
            print("❌")
            return
        
        try:
            import json
            with open(dataset_path, 'r') as f:
                data = json.load(f)
                task_count = len(data.get('tasks', []))
                print(f"✓ ({task_count} tasks)")
        except Exception as e:
            self.errors.append(f"Invalid dataset JSON: {e}")
            print("❌")
    
    def create_env_template(self):
        """Create .env.template file"""
        print("Creating .env template...", end=" ")
        
        env_template = self.base_dir / '.env.template'
        
        template_content = """# API Keys for LLM Evaluation
# Copy this file to .env and fill in your actual keys

# Google Gemini API Key (Primary)
GEMINI_API_KEY=your_gemini_key_here

# OpenAI API Key (Optional)
OPENAI_API_KEY=your_openai_key_here

# Anthropic Claude API Key (Optional)
ANTHROPIC_API_KEY=your_anthropic_key_here
"""
        
        env_template.write_text(template_content)
        print("✓")
    
    def run_all_checks(self):
        """Run all setup checks"""
        print("\n" + "="*60)
        print("Pony LLM Evaluation Framework - Setup Check")
        print("="*60 + "\n")
        
        self.check_python_version()
        self.check_ponyc()
        self.check_python_packages()
        self.check_api_keys()
        self.create_directories()
        self.validate_dataset()
        self.create_env_template()
        
        print("\n" + "="*60)
        
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("✅ All checks passed! Ready to run evaluations.")
        elif not self.errors:
            print("⚠️  Setup complete with warnings. Review above.")
        else:
            print("❌ Setup incomplete. Fix errors above.")
            return False
        
        print("="*60 + "\n")
        return True

def main():
    checker = SetupChecker()
    success = checker.run_all_checks()
    
    if success:
        print("Next steps:")
        print("1. Set your API key: export GEMINI_API_KEY='your_key'")
        print("2. Run evaluation: cd evaluation && python evaluator.py")
        print("3. Analyze results: python analyze_results.py <results_file>")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
