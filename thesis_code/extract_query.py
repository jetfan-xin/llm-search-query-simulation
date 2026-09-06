import json
import os
# 方便评估。从原始数据中抽取user_id, task, query thought & query.
# 因为数据集不完整，当前没有完全生成。
# cleaned_output_data_v1.json 和 extracted_original_data_v1.json格式相同

# 设置原始数据和目标数据的路径

# 同时提取query和thought时
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CODE_DIR, 'data')
DATA_FILE = "data0405" # "user4,8,12,16,20,24,28,32"
original_path = os.path.join(DATA_DIR, DATA_FILE + ".json")
generate_path = os.path.join(DATA_DIR, f'extracted_original_data_{DATA_FILE}.json')

# 只提取query时
# DATA_FILE = "data_update0302"
# original_path = os.path.join('data', DATA_FILE + ".json")
# generate_path = os.path.join('data', f'extracted_original_data_all.json')


def extract_query(only_query):
    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)  # 一次性读取所有数据

    generate_data = []
    for user in original_data:
        user_dict = {"user_id": user["user_id"], "task": {}}
        for task_i in [str(i) for i in range(1, 11)]:
            if task_i not in user["task"]: # 缺少task就不把task_id加入json数据中
                print(f"user {user['user_id']} 缺少 task {task_i}")
            else:
                user_dict["task"][task_i] = {}
                for query_step, content_id in enumerate(list(user["task"][task_i]["content"].keys())):
                    user_dict["task"][task_i][str(query_step+1)] = {}

                    if not only_query: #同时提取thought
                        if "thought" in user["task"][task_i]["content"][content_id]:
                            user_dict["task"][task_i][str(query_step+1)]["thought"] = user["task"][task_i]["content"][content_id]["thought"]
                        else:
                            user_dict["task"][task_i][str(query_step + 1)]["thought"] = ""
                            print(f"user {user['user_id']} task {task_i} query {content_id} 缺少 query thought")

                    # 查询字段对两种模式都必需。原版把这一行缩进在
                    # ``not only_query`` 分支内，导致只提取查询时输出空字典。
                    user_dict["task"][task_i][str(query_step+1)]["query"] = user["task"][task_i]["content"][content_id]["query"]

        generate_data.append(user_dict)
    # 将更新后的数据写回文件
    with open(generate_path, 'w', encoding='utf-8') as file:
        json.dump(generate_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    only_query = 0
    extract_query(only_query)
