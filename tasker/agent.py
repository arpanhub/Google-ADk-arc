from google.adk.agents import Agent
from typing import Dict, List

tasks = []
task_id_counter = 1

def add_task(task: str, priority: str) -> Dict:
    """Adds a task to the to-do list.

    Args:
        task (str): The task to add.
        priority (str): The priority of the task (high, medium, low).

    Returns:
        Dict: A dictionary containing the status and result of the operation.
    """
    global tasks, task_id_counter
    new_task = {"id": task_id_counter, "task": task, "priority": priority, "completed": False}
    tasks.append(new_task)
    task_id_counter += 1
    return {"status": "success", "result": f"Task '{task}' added with priority '{priority}' and ID '{new_task['id']}'."}

def list_tasks() -> Dict:
    """Lists all tasks in the to-do list.

    Returns:
        Dict: A dictionary containing the status and a list of tasks.
    """
    global tasks
    if not tasks:
        return {"status": "success", "result": "No tasks in the to-do list."}
    else:
        return {"status": "success", "result": tasks}

def complete_task(task_id: str) -> Dict:
    """Marks a task as complete.

    Args:
        task_id (str): The ID of the task to mark as complete.

    Returns:
        Dict: A dictionary containing the status and result of the operation.
    """
    global tasks
    try:
        task_id_int = int(task_id)
    except ValueError:
        return {"status": "error", "result": "Invalid task ID. Task ID must be an integer."}

    for task in tasks:
        if task["id"] == task_id_int:
            task["completed"] = True
            return {"status": "success", "result": f"Task with ID '{task_id}' marked as complete."}
    return {"status": "error", "result": f"Task with ID '{task_id}' not found."}

def delete_task(task_id: str) -> Dict:
    """Deletes a task from the to-do list.

    Args:
        task_id (str): The ID of the task to delete.

    Returns:
        Dict: A dictionary containing the status and result of the operation.
    """
    global tasks
    try:
        task_id_int = int(task_id)
    except ValueError:
        return {"status": "error", "result": "Invalid task ID. Task ID must be an integer."}

    original_length = len(tasks)
    tasks = [task for task in tasks if task["id"] != task_id_int]
    if len(tasks) < original_length:
        return {"status": "success", "result": f"Task with ID '{task_id}' deleted."}
    else:
        return {"status": "error", "result": f"Task with ID '{task_id}' not found."}

root_agent = Agent(
    name="tasker",
    model="gemini-2.0-flash",
    description="A task management agent that helps users manage their to-do lists.",
    instruction="The agent should first greet the user informally and ask what operation they would like to perform (add, list, complete, delete).",
    tools=[add_task, list_tasks, complete_task, delete_task]
)