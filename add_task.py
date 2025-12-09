import json
import sys
from pathlib import Path

def get_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def get_multiline_input(prompt):
    """Get multiline input (end with empty line)"""
    print(f"{prompt}")
    print("(Enter your code, then press Enter twice to finish)")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    return "\n".join(lines[:-1])  # Remove last empty line

def create_task():
    
    # Get task ID
    task_id = get_input("Task ID (e.g., basic_004)")
    while not task_id:
        print("Task ID is required!")
        task_id = get_input("Task ID (e.g., basic_004)")
    
    category_choice = get_input("Choose category (1-4)")
    categories = {
        '1': 'basic_syntax',
        '2': 'reference_capabilities',
        '3': 'actor_concurrency',
        '4': 'complex_systems'
    }
    category = categories.get(category_choice, 'basic_syntax')
    
    diff_choice = get_input("Choose difficulty (1-4)")
    difficulties = {
        '1': 'easy',
        '2': 'medium',
        '3': 'hard',
        '4': 'expert'
    }
    difficulty = difficulties.get(diff_choice, 'medium')
    
    # Get task details
    title = get_input("Task title (e.g., 'Array Reversal')")
    description = get_input("Task description (brief)")
    prompt = get_input("Task prompt for LLM")
    
    # Get reference solution
    print("\nReference solution:")
    reference_solution = get_multiline_input("Paste your Pony code")
    
    # Get test cases
    print("\nTest cases (optional, press Enter to skip)")
    test_cases = []
    add_tests = get_input("Add test cases? (y/n)", "n")
    
    if add_tests.lower() == 'y':
        while True:
            test_input = get_input("Test input (or 'done')")
            if test_input.lower() == 'done':
                break
            test_expected = get_input("Expected output")
            test_cases.append({
                "input": test_input,
                "expected": test_expected
            })
    
    # Get tags
    tags_input = get_input("Tags (comma-separated, e.g., 'recursion,arrays')", "")
    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    
    # Create task object
    task = {
        "id": task_id,
        "category": category,
        "difficulty": difficulty,
        "title": title,
        "description": description,
        "prompt": prompt,
        "reference_solution": reference_solution,
        "test_cases": test_cases,
        "tags": tags
    }
    
    return task

def add_task_to_dataset(task, dataset_path):
    """Add task to existing dataset"""
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    # Check for duplicate ID
    existing_ids = [t['id'] for t in dataset['tasks']]
    if task['id'] in existing_ids:
        print(f"\n⚠️  Warning: Task ID '{task['id']}' already exists!")
        overwrite = get_input("Overwrite existing task? (y/n)", "n")
        if overwrite.lower() != 'y':
            print("Aborting.")
            return False
        # Remove old task
        dataset['tasks'] = [t for t in dataset['tasks'] if t['id'] != task['id']]
    
    # Add new task
    dataset['tasks'].append(task)
    
    # Update metadata
    dataset['metadata']['total_tasks'] = len(dataset['tasks'])
    
    # Save
    with open(dataset_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"\n✅ Task '{task['id']}' added to dataset!")
    print(f"Total tasks: {dataset['metadata']['total_tasks']}")
    
    return True

def preview_task(task):
    """Preview the created task"""
    print("\n" + "="*60)
    print("TASK PREVIEW")
    print("="*60)
    print(f"\nID: {task['id']}")
    print(f"Category: {task['category']}")
    print(f"Difficulty: {task['difficulty']}")
    print(f"Title: {task['title']}")
    print(f"\nDescription: {task['description']}")
    print(f"\nPrompt: {task['prompt']}")
    print(f"\nReference Solution:")
    print(task['reference_solution'])
    print(f"\nTest Cases: {len(task['test_cases'])}")
    print(f"Tags: {', '.join(task['tags'])}")
    print("="*60 + "\n")

def main():
    """Main entry point"""
    dataset_path = Path(__file__).parent / 'dataset' / 'pony_tasks.json'
    
    if not dataset_path.exists():
        print(f"Error: Dataset not found at {dataset_path}")
        sys.exit(1)
    
    while True:
        task = create_task()
        preview_task(task)
        
        confirm = get_input("Add this task to dataset? (y/n)", "y")
        if confirm.lower() == 'y':
            if add_task_to_dataset(task, dataset_path):
                print("\nSuccess")
            else:
                print("\nFailed to add task")
        
        another = get_input("\nCreate another task? (y/n)", "n")
        if another.lower() != 'y':
            break
    
    print("\nDone")

if __name__ == "__main__":
    main()
