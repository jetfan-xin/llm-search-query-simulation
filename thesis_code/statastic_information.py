# 真实查询、基线和标准实验的模拟查询在所有搜索任务上的查询中
# 总模拟查询个数、唯一查询个数、
# 平均词数、查询中词数的最小值和最大值。
import json
import jieba
import os
from project_paths import project_path

def get_queries(data_path):
    with open(data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    queries = []

    if "baseline" in data_path:
        for task_id, task in data.items():
            for round in task:
                queries.extend(round)

    else:
        for user in data:
            for task_id, task in user["task"].items():
                for step_id, step in task.items():
                    queries.append(step["query"])
    print("总模拟查询个数:", len(queries))
    print("唯一查询个数:", len(set(queries)))

    words_num = [len(list(jieba.cut(query))) for query in queries]
    print("平均词数:", sum(words_num) / len(words_num))
    print("查询中词数的最小值:", min(words_num))
    print("查询中词数的最大值:", max(words_num))


get_queries(project_path('data', 'extracted_original_data_data0405.json'))
get_queries(project_path('baseline', '2', 'output', 'baseline2_data.json'))
get_queries(project_path('baseline', '1', 'output', 'baseline1_data.json'))
get_queries(project_path('data', 'cleaned_.json'))

