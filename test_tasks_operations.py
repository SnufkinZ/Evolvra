import asyncio
from operation_library import task_operations

async def run_test_flow():
    print("--- 1. Create a new task ---")
    mock_user_id = "user_async_123"
    new_task_data = {
        "user_id": mock_user_id,
        "name": "Initial Task Name",
        "status": "active",
        "description": "This is the original description.",
        "priority": 50
    }
    task_id = await task_operations.create_task(new_task_data)
    
    print("\n--- 2. View the task before update ---")
    task_before_update = await task_operations.get_task_by_id(task_id)
    print("Before Update:", task_before_update)

    print("\n--- 3. Update the task ---")
    fields_to_update = {
        "name": "Updated Task Name!",
        "status": "completed",
        "notes": "This task was updated successfully." # 甚至可以添加新字段
    }
    await task_operations.update_task(task_id, fields_to_update)

    print("\n--- 4. View the updated task ---")
    task_after_update = await task_operations.get_task_by_id(task_id)
    print("After Update:", task_after_update)
    # 你会看到 name 和 status 被修改了，description 和 priority 保持不变，
    # 并且多了一个新的 'notes' 字段。

    print("\n--- 5. Get active tasks for user ---")
    active_tasks = await task_operations.get_active_tasks_for_user(mock_user_id)
    print("Active tasks found:", len(active_tasks))

    print("\n--- 6. Delete the task ---")
    await task_operations.delete_task(task_id)
    deleted_task = await task_operations.get_task_by_id(task_id)
    print("Task after deletion:", deleted_task)

if __name__ == "__main__":
    asyncio.run(run_test_flow())