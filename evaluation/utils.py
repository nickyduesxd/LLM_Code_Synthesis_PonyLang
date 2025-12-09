#!/usr/bin/env python3
"""
Utility functions for Pony LLM Evaluation Framework
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

def load_json(file_path: Path) -> Dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")

def save_json(data: Dict, file_path: Path, pretty: bool = True):
    """Save data to JSON file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)

def extract_pony_capabilities(code: str) -> List[str]:
    """
    Extract reference capabilities used in Pony code
    Returns list of capabilities: iso, trn, ref, val, box, tag
    """
    capabilities = []
    capability_pattern = r'\b(iso|trn|ref|val|box|tag)\b'
    matches = re.findall(capability_pattern, code)
    return list(set(matches))  # Return unique capabilities

def count_actors(code: str) -> int:
    """Count number of actor definitions in code"""
    return len(re.findall(r'\bactor\s+\w+', code))

def count_behaviors(code: str) -> int:
    """Count number of behavior definitions (be) in code"""
    return len(re.findall(r'\s+be\s+\w+', code))

def has_recover_block(code: str) -> bool:
    """Check if code uses recover blocks"""
    return 'recover' in code

def analyze_pony_code(code: str) -> Dict:
    """
    Analyze Pony code and extract features
    Returns dict with code characteristics
    """
    return {
        'capabilities_used': extract_pony_capabilities(code),
        'num_actors': count_actors(code),
        'num_behaviors': count_behaviors(code),
        'uses_recover': has_recover_block(code),
        'num_lines': len(code.split('\n')),
        'has_main': 'actor Main' in code
    }

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def create_timestamp() -> str:
    """Create timestamp string for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def sanitize_filename(name: str) -> str:
    """Sanitize string for use in filename"""
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Limit length
    return name[:100]

def extract_error_type(error_message: str) -> str:
    """
    Extract error type from ponyc compilation error
    Returns simplified error category
    """
    if not error_message:
        return "unknown"
    
    error_patterns = {
        'syntax': r'syntax error|unexpected token',
        'type': r'type mismatch|expected.*got',
        'capability': r'capability|sendable|recover',
        'reference': r'can\'t find|undefined|not found',
        'assignment': r'can\'t assign|immutable',
    }
    
    error_lower = error_message.lower()
    for error_type, pattern in error_patterns.items():
        if re.search(pattern, error_lower):
            return error_type
    
    return "other"

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate simple similarity score between two strings
    Returns value between 0 and 1
    """
    # Simple Jaccard similarity on words
    words1 = set(str1.lower().split())
    words2 = set(str2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def compare_with_reference(generated: str, reference: str) -> Dict:
    """
    Compare generated code with reference solution
    Returns dict with comparison metrics
    """
    gen_analysis = analyze_pony_code(generated)
    ref_analysis = analyze_pony_code(reference)
    
    return {
        'similarity_score': calculate_similarity(generated, reference),
        'capabilities_match': set(gen_analysis['capabilities_used']) == set(ref_analysis['capabilities_used']),
        'actors_match': gen_analysis['num_actors'] == ref_analysis['num_actors'],
        'behaviors_match': gen_analysis['num_behaviors'] == ref_analysis['num_behaviors'],
        'uses_recover_match': gen_analysis['uses_recover'] == ref_analysis['uses_recover']
    }

def batch_process_results(results: List[Dict], batch_size: int = 10) -> List[List[Dict]]:
    """Split results into batches for processing"""
    return [results[i:i + batch_size] for i in range(0, len(results), batch_size)]

def filter_tasks_by_criteria(
    tasks: List[Dict],
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    min_id: Optional[int] = None,
    max_id: Optional[int] = None
) -> List[Dict]:
    """
    Filter tasks based on various criteria
    """
    filtered = tasks
    
    if category:
        filtered = [t for t in filtered if t['category'] == category]
    
    if difficulty:
        filtered = [t for t in filtered if t['difficulty'] == difficulty]
    
    if min_id is not None:
        filtered = [t for t in filtered if int(t['id'].split('_')[1]) >= min_id]
    
    if max_id is not None:
        filtered = [t for t in filtered if int(t['id'].split('_')[1]) <= max_id]
    
    return filtered

def print_progress_bar(iteration: int, total: int, prefix: str = '', length: int = 50):
    """Print a progress bar"""
    percent = 100 * (iteration / float(total))
    filled = int(length * iteration // total)
    bar = '█' * filled + '-' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent:.1f}% ({iteration}/{total})', end='\r')
    if iteration == total:
        print()

def get_task_stats(tasks: List[Dict]) -> Dict:
    """Get statistics about tasks in dataset"""
    from collections import Counter
    
    categories = Counter(t['category'] for t in tasks)
    difficulties = Counter(t['difficulty'] for t in tasks)
    
    return {
        'total_tasks': len(tasks),
        'by_category': dict(categories),
        'by_difficulty': dict(difficulties)
    }

def validate_pony_syntax_basic(code: str) -> Tuple[bool, Optional[str]]:
    """
    Basic syntax validation without compiling
    Checks for common syntax errors
    """
    checks = [
        (r'actor\s+\w+', "No actor definition found"),
        (r'new\s+create\(.*?\)\s*=>', "No constructor found"),
    ]
    
    for pattern, error_msg in checks:
        if not re.search(pattern, code):
            return False, error_msg
    
    # Check for balanced braces (simple check)
    if code.count('{') != code.count('}'):
        return False, "Unbalanced braces"
    
    return True, None

class CodeFormatter:
    """Format code for display"""
    
    @staticmethod
    def truncate(text: str, max_length: int = 100) -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def indent(text: str, spaces: int = 2) -> str:
        """Indent all lines of text"""
        indent_str = " " * spaces
        return "\n".join(indent_str + line for line in text.split("\n"))
    
    @staticmethod
    def remove_comments(code: str) -> str:
        """Remove comments from Pony code"""
        # Remove single-line comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

# Example usage
if __name__ == "__main__":
    # Test code analysis
    sample_code = """
    actor Counter
      var _count: U64 = 0
      
      be increment() =>
        _count = _count + 1
      
      be get_value(callback: {(U64)} val) =>
        callback(_count)
    """
    
    analysis = analyze_pony_code(sample_code)
    print("Code Analysis:")
    print(json.dumps(analysis, indent=2))
    
    # Test error type extraction
    error_msg = "Error: syntax error - unexpected token"
    error_type = extract_error_type(error_msg)
    print(f"\nError type: {error_type}")
