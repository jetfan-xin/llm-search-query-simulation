# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import json
import jieba
import os

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

get_queries(os.path.join('data', 'extracted_original_data_data0405.json'))
get_queries(os.path.join('baseline', '2', 'output', 'baseline2_data.json'))
get_queries(os.path.join('baseline', '1', 'output', 'baseline1_data.json'))
get_queries(os.path.join('data', 'cleaned_.json'))
