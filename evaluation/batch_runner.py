#!/usr/bin/env python3
"""
Batch Evaluation Runner
Run evaluations with different configurations in sequence
"""

import sys
import time
from pathlib import Path
from typing import List, Dict
import json

sys.path.append(str(Path(__file__).parent))
from evaluator import Evaluator

class BatchRunner:
    """Run multiple evaluation configurations"""
    
    def __init__(self, output_base_dir: Path):
        self.output_base_dir = output_base_dir
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        self.results_summary = []
    
    def run_configuration(
        self,
        config_name: str,
        strategies: List[str],
        models: List[str],
        task_filter: List[str] = None
    ):
        """Run evaluation with specific configuration"""
        print(f"\n{'='*70}")
        print(f"RUNNING CONFIGURATION: {config_name}")
        print(f"{'='*70}\n")
        
        output_dir = self.output_base_dir / config_name
        dataset_path = Path(__file__).parent.parent / 'dataset' / 'pony_tasks.json'
        
        evaluator = Evaluator(
            dataset_path=dataset_path,
            output_dir=output_dir,
            strategies=strategies,
            models=models
        )
        
        start_time = time.time()
        evaluator.run_evaluation(task_filter=task_filter)
        duration = time.time() - start_time
        
        # Collect summary
        total = len(evaluator.results)
        successful = sum(1 for r in evaluator.results if r.compilation_success)
        
        summary = {
            'config_name': config_name,
            'strategies': strategies,
            'models': models,
            'total_evaluations': total,
            'successful': successful,
            'success_rate': successful / total if total > 0 else 0,
            'duration_seconds': duration,
            'output_dir': str(output_dir)
        }
        
        self.results_summary.append(summary)
        
        print(f"\n✓ Configuration '{config_name}' complete")
        print(f"  Success Rate: {summary['success_rate']*100:.1f}%")
        print(f"  Duration: {duration:.1f}s")
    
    def save_batch_summary(self):
        """Save summary of all batch runs"""
        summary_file = self.output_base_dir / 'batch_summary.json'
        
        with open(summary_file, 'w') as f:
            json.dump(self.results_summary, f, indent=2)
        
        # Also create text report
        report_file = self.output_base_dir / 'batch_report.txt'
        
        with open(report_file, 'w') as f:
            f.write("BATCH EVALUATION SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            
            for summary in self.results_summary:
                f.write(f"Configuration: {summary['config_name']}\n")
                f.write(f"  Strategies: {', '.join(summary['strategies'])}\n")
                f.write(f"  Models: {', '.join(summary['models'])}\n")
                f.write(f"  Success Rate: {summary['success_rate']*100:.1f}%\n")
                f.write(f"  Duration: {summary['duration_seconds']:.1f}s\n")
                f.write(f"  Output: {summary['output_dir']}\n")
                f.write("-" * 70 + "\n\n")
            
            # Overall statistics
            total_evals = sum(s['total_evaluations'] for s in self.results_summary)
            total_success = sum(s['successful'] for s in self.results_summary)
            total_duration = sum(s['duration_seconds'] for s in self.results_summary)
            
            f.write("OVERALL STATISTICS\n")
            f.write("=" * 70 + "\n")
            f.write(f"Total Configurations: {len(self.results_summary)}\n")
            f.write(f"Total Evaluations: {total_evals}\n")
            f.write(f"Total Successful: {total_success}\n")
            f.write(f"Overall Success Rate: {total_success/total_evals*100:.1f}%\n")
            f.write(f"Total Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)\n")
        
        print(f"\n✓ Batch summary saved to {summary_file}")
        print(f"✓ Batch report saved to {report_file}")

def main():
    """Run predefined batch configurations"""
    
    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = BASE_DIR / 'results' / f'batch_{int(time.time())}'
    
    runner = BatchRunner(OUTPUT_DIR)
    
    # Configuration 1: Compare all strategies on basic tasks
    print("\n🚀 Starting batch evaluation...")
    
    runner.run_configuration(
        config_name='all_strategies_basic',
        strategies=[
            'zero_shot',
            'few_shot',
            'chain_of_thought',
            'self_debug',
            'capability_focused'
        ],
        models=['gemini-2.5-flash'],
        task_filter=['basic_001', 'basic_002', 'basic_003']
    )
    
    # Configuration 2: Test actor tasks with actor-focused strategy
    runner.run_configuration(
        config_name='actor_focused_eval',
        strategies=['actor_focused', 'zero_shot'],
        models=['gemini-2.5-flash'],
        task_filter=['actor_001', 'actor_002', 'actor_003']
    )
    
    # Configuration 3: Capability tasks with specialized prompting
    runner.run_configuration(
        config_name='capability_focused_eval',
        strategies=['capability_focused', 'zero_shot', 'few_shot'],
        models=['gemini-2.5-flash'],
        task_filter=['cap_001', 'cap_002', 'cap_003']
    )
    
    # Configuration 4: Transfer learning comparison
    runner.run_configuration(
        config_name='transfer_learning',
        strategies=['transfer_rust', 'transfer_cpp', 'zero_shot'],
        models=['gemini-2.5-flash'],
        task_filter=['basic_001', 'basic_002', 'actor_001']
    )
    
    # Save batch summary
    runner.save_batch_summary()
    
    print("\n" + "=" * 70)
    print("✅ ALL BATCH EVALUATIONS COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("\nTo analyze individual configurations, run:")
    print("  python analyze_results.py <config_dir>/evaluation_results.json")

if __name__ == "__main__":
    main()
