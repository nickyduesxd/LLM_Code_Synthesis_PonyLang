#!/usr/bin/env python3
"""
Analysis and Visualization Script for Pony LLM Evaluation Results
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from typing import List, Dict 

def analyze_retries(results: List[dict]) -> dict:
    """Analyze retry patterns and statistics"""
    retry_stats = {
        'total_tasks': len(results),
        'succeeded_on_first_try': 0,
        'succeeded_on_retry': 0,
        'never_succeeded': 0,
        'retry_attempts': [],
        'by_strategy': {}
    }
    
    for r in results:
        strategy = r['strategy']
        if strategy not in retry_stats['by_strategy']:
            retry_stats['by_strategy'][strategy] = {
                'first_try': 0,
                'retry_success': 0,
                'failed': 0,
                'retry_counts': []
            }
        
        if r['compilation_success']:
            retry_count = r.get('retry_count', 0)
            if retry_count == 0:
                retry_stats['succeeded_on_first_try'] += 1
                retry_stats['by_strategy'][strategy]['first_try'] += 1
            else:
                retry_stats['succeeded_on_retry'] += 1
                retry_stats['retry_attempts'].append(retry_count)
                retry_stats['by_strategy'][strategy]['retry_success'] += 1
                retry_stats['by_strategy'][strategy]['retry_counts'].append(retry_count)
        else:
            retry_stats['never_succeeded'] += 1
            retry_stats['by_strategy'][strategy]['failed'] += 1
    
    # Calculate averages
    if retry_stats['retry_attempts']:
        retry_stats['mean_retries_when_needed'] = sum(retry_stats['retry_attempts']) / len(retry_stats['retry_attempts'])
        retry_stats['max_retries_needed'] = max(retry_stats['retry_attempts'])
    else:
        retry_stats['mean_retries_when_needed'] = 0
        retry_stats['max_retries_needed'] = 0
    
    # Calculate improvement from retries
    if retry_stats['total_tasks'] > 0:
        retry_stats['first_try_success_rate'] = (retry_stats['succeeded_on_first_try'] / retry_stats['total_tasks']) * 100
        total_successes = retry_stats['succeeded_on_first_try'] + retry_stats['succeeded_on_retry']
        retry_stats['final_success_rate'] = (total_successes / retry_stats['total_tasks']) * 100
        retry_stats['improvement_from_retries'] = retry_stats['final_success_rate'] - retry_stats['first_try_success_rate']
    
    return retry_stats


class ResultAnalyzer:
    def __init__(self, results_file: Path, output_dir: Path):
        self.results_file = results_file
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'r') as f:
            self.results = json.load(f)
        
        self.df = pd.DataFrame(self.results)
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def generate_all_analyses(self):
        print("Generating analysis reports...")
        self.success_rate_by_strategy()
        self.success_rate_by_category()
        self.success_rate_by_difficulty()
        self.strategy_category_heatmap()
        self.execution_time_analysis()
        self.error_analysis()
        self.retry_analysis()
        self.comparative_analysis()
        print(f"\n✓ All analyses saved to {self.output_dir}")
    
    def success_rate_by_strategy(self):
        strategy_stats = self.df.groupby('strategy').agg({
            'compilation_success': ['mean', 'count', 'sum']
        }).round(3)
        strategy_stats.columns = ['success_rate', 'total_attempts', 'successful']
        strategy_stats = strategy_stats.sort_values('success_rate', ascending=False)
        strategy_stats.to_csv(self.output_dir / 'strategy_success_rates.csv')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        strategies = strategy_stats.index
        success_rates = strategy_stats['success_rate'] * 100
        bars = ax.bar(range(len(strategies)), success_rates, color='steelblue')
        ax.set_xlabel('Prompting Strategy', fontsize=12)
        ax.set_ylabel('Success Rate (%)', fontsize=12)
        ax.set_title('Compilation Success Rate by Prompting Strategy', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(strategies)))
        ax.set_xticklabels(strategies, rotation=45, ha='right')
        ax.set_ylim(0, 100)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'strategy_success_rates.png', dpi=300)
        plt.close()
        print(f"✓ Strategy analysis saved")
    
    def success_rate_by_category(self):
        category_stats = self.df.groupby('category').agg({
            'compilation_success': ['mean', 'count', 'sum']
        }).round(3)
        category_stats.columns = ['success_rate', 'total_attempts', 'successful']
        category_stats = category_stats.sort_values('success_rate', ascending=False)
        category_stats.to_csv(self.output_dir / 'category_success_rates.csv')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = category_stats.index
        success_rates = category_stats['success_rate'] * 100
        bars = ax.bar(range(len(categories)), success_rates, color='coral')
        ax.set_xlabel('Task Category', fontsize=12)
        ax.set_ylabel('Success Rate (%)', fontsize=12)
        ax.set_title('Compilation Success Rate by Task Category', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_ylim(0, 100)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'category_success_rates.png', dpi=300)
        plt.close()
        print(f"✓ Category analysis saved")
    
    def success_rate_by_difficulty(self):
        difficulty_stats = self.df.groupby('difficulty').agg({
            'compilation_success': ['mean', 'count', 'sum']
        }).round(3)
        difficulty_stats.columns = ['success_rate', 'total_attempts', 'successful']
        difficulty_order = ['easy', 'medium', 'hard', 'expert']
        difficulty_stats = difficulty_stats.reindex(
            [d for d in difficulty_order if d in difficulty_stats.index]
        )
        difficulty_stats.to_csv(self.output_dir / 'difficulty_success_rates.csv')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        difficulties = difficulty_stats.index
        success_rates = difficulty_stats['success_rate'] * 100
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(difficulties)))
        bars = ax.bar(range(len(difficulties)), success_rates, color=colors)
        ax.set_xlabel('Difficulty Level', fontsize=12)
        ax.set_ylabel('Success Rate (%)', fontsize=12)
        ax.set_title('Compilation Success Rate by Difficulty', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(difficulties)))
        ax.set_xticklabels(difficulties)
        ax.set_ylim(0, 100)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'difficulty_success_rates.png', dpi=300)
        plt.close()
        print(f"✓ Difficulty analysis saved")
    
    def strategy_category_heatmap(self):
        pivot = self.df.pivot_table(
            values='compilation_success',
            index='strategy',
            columns='category',
            aggfunc='mean'
        )
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot * 100, annot=True, fmt='.1f', cmap='YlGnBu',
                   cbar_kws={'label': 'Success Rate (%)'}, ax=ax)
        ax.set_title('Success Rate Heatmap: Strategy vs Category', fontsize=14, fontweight='bold')
        ax.set_xlabel('Task Category', fontsize=12)
        ax.set_ylabel('Prompting Strategy', fontsize=12)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'strategy_category_heatmap.png', dpi=300)
        plt.close()
        print(f"✓ Heatmap saved")
    
    def execution_time_analysis(self):
        time_stats = self.df.groupby('strategy')['execution_time'].agg(['mean', 'median', 'std']).round(2)
        time_stats.to_csv(self.output_dir / 'execution_times.csv')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        strategies = time_stats.index
        mean_times = time_stats['mean']
        bars = ax.bar(range(len(strategies)), mean_times, color='mediumpurple')
        ax.set_xlabel('Prompting Strategy', fontsize=12)
        ax.set_ylabel('Average Execution Time (s)', fontsize=12)
        ax.set_title('Average Execution Time by Strategy', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(strategies)))
        ax.set_xticklabels(strategies, rotation=45, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}s', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'execution_times.png', dpi=300)
        plt.close()
        print(f"✓ Execution time analysis saved")
    
    def error_analysis(self):
        failed = self.df[self.df['compilation_success'] == False]
        if len(failed) == 0:
            print("✓ No compilation errors to analyze")
            return
        
        with open(self.output_dir / 'error_analysis.txt', 'w') as f:
            f.write("COMPILATION ERROR ANALYSIS\n" + "=" * 60 + "\n\n")
            f.write(f"Total Failed Compilations: {len(failed)}\n\n")
            f.write("Errors by Strategy:\n")
            for strategy, count in failed.groupby('strategy').size().sort_values(ascending=False).items():
                f.write(f"  {strategy}: {count}\n")
            f.write("\n" + "=" * 60 + "\n\n")
            f.write("Sample Compilation Errors:\n\n")
            for idx, row in failed.head(10).iterrows():
                f.write(f"Task: {row['task_id']} | Strategy: {row['strategy']}\n")
                if row['compilation_error']:
                    f.write(f"Error: {row['compilation_error'][:200]}...\n")
                f.write("-" * 60 + "\n\n")
        print(f"✓ Error analysis saved")


    def retry_analysis(self):
        """Analyze and visualize retry statistics"""
        retry_stats = analyze_retries(self.results)
    
    # Save text report
        with open(self.output_dir / 'retry_analysis.txt', 'w') as f:
            f.write("RETRY ANALYSIS\n" + "=" * 60 + "\n\n")
            f.write(f"Total Tasks: {retry_stats['total_tasks']}\n")
            f.write(f"Succeeded on First Try: {retry_stats['succeeded_on_first_try']} ({retry_stats.get('first_try_success_rate', 0):.1f}%)\n")
            f.write(f"Succeeded After Retry: {retry_stats['succeeded_on_retry']}\n")
            f.write(f"Never Succeeded: {retry_stats['never_succeeded']}\n")
            f.write(f"Final Success Rate: {retry_stats.get('final_success_rate', 0):.1f}%\n")
            f.write(f"Improvement from Retries: +{retry_stats.get('improvement_from_retries', 0):.1f}%\n\n")
        
            if retry_stats['retry_attempts']:
                f.write(f"Mean Retries (when needed): {retry_stats['mean_retries_when_needed']:.2f}\n")
                f.write(f"Max Retries Needed: {retry_stats['max_retries_needed']}\n\n")
        
            f.write("=" * 60 + "\n")
            f.write("BY STRATEGY\n")
            f.write("=" * 60 + "\n\n")
            for strategy, stats in retry_stats['by_strategy'].items():
                total = stats['first_try'] + stats['retry_success'] + stats['failed']
                f.write(f"{strategy}:\n")
                f.write(f"  First Try Success: {stats['first_try']}/{total}\n")
                f.write(f"  Retry Success: {stats['retry_success']}/{total}\n")
                f.write(f"  Failed: {stats['failed']}/{total}\n")
                if stats['retry_counts']:
                    f.write(f"  Avg Retries Needed: {sum(stats['retry_counts'])/len(stats['retry_counts']):.2f}\n")
                f.write("\n")
    
        print(f"✓ Retry analysis saved") 
    
    def comparative_analysis(self):
        with open(self.output_dir / 'comparative_summary.txt', 'w') as f:
            total = len(self.df)
            successful = self.df['compilation_success'].sum()
            f.write("COMPARATIVE ANALYSIS SUMMARY\n" + "=" * 60 + "\n\n")
            f.write(f"Total Evaluations: {total}\n")
            f.write(f"Overall Success Rate: {successful/total*100:.1f}%\n\n")
            
            best_strategy = self.df.groupby('strategy')['compilation_success'].mean().idxmax()
            best_rate = self.df.groupby('strategy')['compilation_success'].mean().max()
            f.write(f"Best Strategy: {best_strategy} ({best_rate*100:.1f}%)\n")
            
            best_category = self.df.groupby('category')['compilation_success'].mean().idxmax()
            best_cat_rate = self.df.groupby('category')['compilation_success'].mean().max()
            f.write(f"Easiest Category: {best_category} ({best_cat_rate*100:.1f}%)\n\n")
            
            worst_category = self.df.groupby('category')['compilation_success'].mean().idxmin()
            worst_cat_rate = self.df.groupby('category')['compilation_success'].mean().min()
            f.write(f"Hardest Category: {worst_category} ({worst_cat_rate*100:.1f}%)\n")
        print(f"✓ Comparative summary saved")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <results_file.json>")
        sys.exit(1)
    
    results_file = Path(sys.argv[1])
    output_dir = results_file.parent / 'analysis'
    analyzer = ResultAnalyzer(results_file, output_dir)
    analyzer.generate_all_analyses()

if __name__ == "__main__":
    main()
