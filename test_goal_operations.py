import asyncio
import json
from logic import goal_operations, profile_operations

async def run_goal_and_profile_tests():
    print("\n" + "="*20 + " GOAL & PROFILE TESTS " + "="*20)
    mock_user_id = "user_goals_789"

    # --- 测试 Goals ---
    print("\n--- 1. 创建层级目标 ---")
    root_goal_id = await goal_operations.create_goal({
        "user_id": mock_user_id,
        "name": "Become a Better Person",
        "weight": 100
    })
    
    tech_goal_id = await goal_operations.create_goal({
        "user_id": mock_user_id,
        "name": "Learn Technology",
        "parent_id": root_goal_id,
        "weight": 50
    })

    await goal_operations.create_goal({
        "user_id": mock_user_id,
        "name": "Master Python & AI",
        "parent_id": tech_goal_id,
        "weight": 80
    })

    print("\n--- 2. 获取并打印目标树 ---")
    goal_tree = await goal_operations.get_goal_tree_for_user(mock_user_id)
    # 使用json库来美化打印嵌套的字典
    print(json.dumps(goal_tree, indent=2, default=str)) # default=str处理ObjectId

    # --- 测试 User Profiles ---
    print("\n--- 3. 添加用户画像条目 ---")
    await profile_operations.add_profile_entry({
        "user_id": mock_user_id,
        "text": "Is a student learning software development.",
        "scope": "background",
        "confidence": 95
    })
    await profile_operations.add_profile_entry({
        "user_id": mock_user_id,
        "text": "Prefers to work in the morning.",
        "scope": "habit",
        "confidence": 80
    })

    print("\n--- 4. 获取整合后的画像文本 ---")
    profile_text = await profile_operations.get_user_profile_as_text(mock_user_id)
    print(profile_text)

    # --- 清理数据 (在真实应用中你可能不会这么做) ---
    print("\n--- 5. 清理测试数据 ---")
    await goals_collection.delete_many({"user_id": mock_user_id})
    await user_profiles_collection.delete_many({"user_id": mock_user_id})
    print("Cleanup complete.")

if __name__ == "__main__":
    # 你可以只运行最新的测试
    asyncio.run(run_goal_and_profile_tests())