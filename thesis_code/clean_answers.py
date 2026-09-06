# 用于提取出生成答案中的thought和query，并保存在cleaned_output_data_v1.json中
# cleaned_output_data_v1.json 和 extracted_original_data_v1.json格式相同

import os
import json
import re
from project_paths import project_path
DATA_FILE = "user5,9,13,17,21,25,29,2,6,10,14,18,22,26,30" #"user3,7,11,15,19,23,27,31"# "user4,8,12,16,20,24,28,32.json"
MODEL = "gpt-3.5-turbo-0125"

original_path = project_path('data', 'output_data_wo_observation.json') # project_path('data', f'output_data_{DATA_FILE}_{MODEL}.json')
generate_path = project_path('data', f'cleaned_wo_observation.json')
error_path = project_path('data', 'regenerated.json')


def parse_generated_response(input_value):
    """从历史接口保存的响应中提取思考和查询。

    优先解析模型被要求返回的 JSON；为了兼容已经保存的非严格输出，仍保留
    原实验使用的正则表达式作为回退路径。
    """
    if isinstance(input_value, (dict, list)):
        parsed = input_value
        input_str = json.dumps(input_value, ensure_ascii=False)
    else:
        input_str = str(input_value).strip()
        if input_str.startswith("```"):
            input_str = re.sub(r'^```(?:json)?\s*|\s*```$', '', input_str, flags=re.IGNORECASE)
        try:
            parsed = json.loads(input_str)
        except json.JSONDecodeError:
            parsed = None

    records = parsed if isinstance(parsed, list) else [parsed]
    thought = ""
    query = ""
    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("类型") == "思考":
            thought = str(record.get("内容", ""))
        elif record.get("类型") == "查询":
            query = str(record.get("内容", ""))
        # 兼容直接使用字段名的响应。
        thought = str(record.get("thought", thought))
        query = str(record.get("query", query))

    if not thought:
        match = re.search(r'"类型"\s*:\s*"思考"\s*,\s*"内容"\s*:\s*"(.*?)"', input_str)
        thought = match.group(1) if match else ""
    if not query:
        match = re.search(r'"类型"\s*:\s*"查询"\s*,\s*"内容"\s*:\s*"(.*?)"', input_str)
        query = match.group(1) if match else ""
    return thought, query

def extract_query():
    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)  # 获取所有数据

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
                # 提取原始数据中的思考和查询
                input_str = user["task"][task_i][query_step]
                thought, query = parse_generated_response(input_str)
                if "thought" not in original_path and "_s." not in original_path:
                    if not thought:
                        print(f"用户{user_dict['user_id']} 任务{task_i} 步骤{query_step} 找不到 思考")
                        error_step.add(str(user_dict['user_id']) + " " + task_i + " " + query_step)
                    user_dict["task"][task_i][query_step]["thought"] = thought

                if not query:
                    print(f"用户{user_dict['user_id']} 任务{task_i} 步骤{query_step} 找不到 查询")
                    error_step.add(str(user_dict['user_id']) + " " + task_i + " " + query_step)
                user_dict["task"][task_i][query_step]["query"] = query

        generate_data.append(user_dict)

    # 所有用户处理完成后再写一次，避免每处理一位用户就覆盖完整输出。
    with open(generate_path, 'w', encoding='utf-8') as file:
        json.dump(generate_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    # 将生成出错的步骤存入json文件，方便后续补充生成
    with open(error_path, 'w', encoding='utf-8') as file:
        json.dump(sorted(error_step), file, ensure_ascii=False)



if __name__ == "__main__":
    extract_query()
