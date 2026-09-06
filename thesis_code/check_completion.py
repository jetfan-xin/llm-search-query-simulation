import json
import os
from project_paths import project_path
# 检查是否缺少task, query thought, query satisfaction_thought, click thought, click usefulness_thought

# 填入标注后数据路径
data_path = project_path('data', "data0405.json")

def check_completion():
    with open(data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)  # 一次性读取所有数据
    query_thought_num = 0
    query_sat_thought_num = 0
    checked_page_num = 0
    for user in data:

        for task_i in [str(i) for i in range(1, 11)]:
            if task_i not in user["task"]:
                # print(f"user {user['user_id']} 缺少 task {task_i}")
                pass
            else:
                for query_step, content_id in enumerate(list(user["task"][task_i]["content"].keys())):
                    if "thought" not in user["task"][task_i]["content"][content_id]:
                        # print(f"user {user['user_id']} task {task_i} query {content_id} 缺少 query thought")
                        pass
                    else:
                        # print(user["task"][task_i]["content"][content_id]["thought"])
                        if "被试没说" not in user["task"][task_i]["content"][content_id]["thought"] and user["task"][task_i]["content"][content_id]["thought"] !="":
                            query_thought_num +=1
                    if "satisfaction_thought" not in user["task"][task_i]["content"][content_id]:
                        # print(f"user {user['user_id']} task {task_i} query {content_id} 缺少 query satisfaction_thought")
                        pass
                    else:
                        # print(user["task"][task_i]["content"][content_id]["satisfaction_thought"])
                        if "被试没说" not in user["task"][task_i]["content"][content_id]["satisfaction_thought"] and user["task"][task_i]["content"][content_id]["satisfaction_thought"] !="":
                            query_sat_thought_num +=1
                    for rank, link in enumerate(user["task"][task_i]["content"][content_id]["SERP"]):
                        if link["click_or_not"] == 1:
                            checked_page_num+=1
                            # if "thought" not in link:
                            #     print(f"user {user['user_id']} task {task_i} query {content_id} link {rank+1} 缺少 click thought")
                            # if "usefulness_thou ght" not in link:
                            #     print(f"user {user['user_id']} task {task_i} query {content_id} link {rank+1} 缺少 click usefulness_thought")

    print(query_thought_num, query_sat_thought_num, checked_page_num)
if __name__ == "__main__":
    check_completion()