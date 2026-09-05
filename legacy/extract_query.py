# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import json
import os

DATA_FILE = "data0405"
original_path = os.path.join('data', DATA_FILE + ".json")
generate_path = os.path.join('data', f'extracted_original_data_{DATA_FILE}.json')

def extract_query(only_query):
    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    generate_data = []
    for user in original_data:
        user_dict = {"user_id": user["user_id"], "task": {}}
        for task_i in [str(i) for i in range(1, 11)]:
            if task_i not in user["task"]:
                print(f"user {user['user_id']} 缺少 task {task_i}")
            else:
                user_dict["task"][task_i] = {}
                for query_step, content_id in enumerate(list(user["task"][task_i]["content"].keys())):
                    user_dict["task"][task_i][str(query_step+1)] = {}

                    if not only_query:
                        if "thought" in user["task"][task_i]["content"][content_id]:
                            user_dict["task"][task_i][str(query_step+1)]["thought"] = user["task"][task_i]["content"][content_id]["thought"]
                        else:
                            user_dict["task"][task_i][str(query_step + 1)]["thought"] = ""
                            print(f"user {user['user_id']} task {task_i} query {content_id} 缺少 query thought")

                        user_dict["task"][task_i][str(query_step+1)]["query"] = user["task"][task_i]["content"][content_id]["query"]

        generate_data.append(user_dict)

    with open(generate_path, 'w', encoding='utf-8') as file:
        json.dump(generate_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    only_query = 0
    extract_query(only_query)
