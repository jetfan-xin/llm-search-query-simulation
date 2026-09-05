# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import os
import json
import re
DATA_FILE = "user5,9,13,17,21,25,29,2,6,10,14,18,22,26,30"
MODEL = "gpt-3.5-turbo-0125"

original_path = os.path.join('data', 'output_data_wo_observation.json')
generate_path = os.path.join('data', f'cleaned_wo_observation.json')
error_path = os.path.join('data', 'regenerated.json')

def extract_query():
    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    error_step = set()
    generate_data = []
    for user in original_data:
        user_dict = {}
        user_dict["user_id"] = user["user_id"]
        user_dict["task"] = {}
        for task_i in user["task"].keys():
            user_dict["task"][task_i] = {}
            for query_step in list(user["task"][task_i].keys()):
                user_dict["task"][task_i][query_step] = {}

                input_str = user["task"][task_i][query_step]
                if "thought" not in original_path and "_s." not in original_path:

                    thought_match = re.search(r'"类型": "思考",\s*"内容": "(.*?)"', input_str)
                    if thought_match:
                        thought = thought_match.group(1)
                    else:
                        thought = ""
                        print(f"用户{user_dict['user_id']} 任务{task_i} 步骤{query_step} 找不到 思考")
                        error_step.add(str(user_dict['user_id']) + " " + task_i + " " + query_step)
                    user_dict["task"][task_i][query_step]["thought"] = thought

                query_match = re.search(r'"类型": "查询",\s*"内容": "(.*?)"', input_str)
                if query_match:
                    query = query_match.group(1)
                else:
                    query = ""
                    print(f"用户{user_dict['user_id']} 任务{task_i} 步骤{query_step} 找不到 查询")
                    error_step.add(str(user_dict['user_id']) + " " + task_i + " " + query_step)
                user_dict["task"][task_i][query_step]["query"] = query

        generate_data.append(user_dict)

        with open(generate_path, 'w', encoding='utf-8') as file:
            json.dump(generate_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

        with open(error_path, 'w', encoding='utf-8') as file:
            json.dump(list(error_step), file, ensure_ascii=False)

if __name__ == "__main__":
    extract_query()
