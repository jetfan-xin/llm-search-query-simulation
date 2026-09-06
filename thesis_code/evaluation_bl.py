import os
import json
import jieba
import re
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import BERTScorer
import torch
import pandas as pd
from project_paths import project_path
bl_data_num = [82, 66, 73, 89, 100, 55, 85, 53, 76, 58]

smoothie = SmoothingFunction().method1

def query2terms(query):
    return set([t for t in jieba.cut(query) if t not in stopwords and re.search(pattern, t)])

def jaccard_similarity(query1, query2):
    """计算两个集合的 Jaccard 相似度"""
    set1 = query2terms(query1)
    set2 = query2terms(query2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def bleu(q1, q2):
    return sentence_bleu([q1],q2,weights=(0.5, 0.5, 0, 0), smoothing_function=smoothie)

def get_queries_with_tasks(data):
    # 获取每个task下的分步的query
    queries = {}
    for user in data:
        for task_id, task in user["task"].items():
            queries.setdefault(task_id, {"1":[], "2":[]})
            for step_id, step in task.items():
                if step_id == "1":
                    queries[task_id]["1"].append(step["query"])
                else:
                    queries[task_id]["2"].append(step["query"])
    return queries


stopwords_file = project_path('baseline', 'stopwords.txt')
pattern = re.compile(r'[\u4e00-\u9fff]')
stopwords = []
with open(stopwords_file, 'r', encoding='utf-8') as file:
    for line in file:
        stopwords.append(line.strip())

original_path = project_path('data', 'extracted_original_data_data0405.json')
with open(original_path, 'r', encoding='utf-8') as file:
    original_data = json.load(file)
original_queries_with_tasks = get_queries_with_tasks(original_data)

bl1_path = project_path('baseline', '1', 'output', 'baseline1_data.json')
with open(bl1_path, 'r', encoding='utf-8') as file:
    bl1_queries_with_tasks = json.load(file)

bl2_path = project_path('baseline', '2', 'output', 'baseline2_data.json')
with open(bl2_path, 'r', encoding='utf-8') as file:
    bl2_queries_with_tasks = json.load(file)

bl_scorer = []
for i in range(10):
    # 实例化BERTScorer，指定使用的模型和语言
    bl_scorer.append(BERTScorer(model_type="bert-base-chinese", lang="zh", batch_size=bl_data_num[i],
                            device='cuda' if torch.cuda.is_available() else 'cpu'))


def evaluation_bl(data, name, metric_type, output_path):
    score_all = []
    score_first = []
    score_others = []
    # 处理基线
    bl_queries_with_tasks = {}
    for task_id in [str(j) for j in range(1, 11)]:
        bl_queries_with_tasks[task_id] = []
        for i in range(10):
            bl_queries_with_tasks[task_id].extend(data[task_id][i])

    num = [0]*10  # for 10 task

    for i in range(10): # round
        if "BERTScore" in metric_type:
            for task_id, task in original_queries_with_tasks.items():
                # if task_id == "1":
                for step_id, step in task.items():
                    length = len(original_queries_with_tasks[task_id][step_id])
                    length2 = len(bl_queries_with_tasks[task_id][num[int(task_id) - 1]: num[int(task_id) - 1] + length])
                    if length2 != length:
                        print("长度不等")
                        print(length, length2)
                        length = length2
                    score_list = [float(f1_score.item()) for f1_score in bl_scorer[int(task_id) - 1].score(
                        bl_queries_with_tasks[task_id][num[int(task_id) - 1]: num[int(task_id) - 1] + length],
                        original_queries_with_tasks[task_id][step_id][:length])[-1]]
                    for score in score_list:
                        score_all.append({metric_type: score, "name": name, "position": "总体"})
                    if step_id == "1":
                        for score in score_list:
                            score_all.append({metric_type: score, "name": name, "position": "第1次查询"})
                    else:
                        for score in score_list:
                            score_all.append({metric_type: score, "name": name, "position": ">=2次查询"})
                    num[int(task_id) - 1] += length
        else:
            for user in original_data:
                for task_id, task in user["task"].items():
                    # if task_id == "1":
                    for step_id, step in task.items():
                        try:
                            query1 = bl_queries_with_tasks[task_id][num[int(task_id)-1]]
                        except:
                            print(user["user_id"], task_id, step_id)
                        num[int(task_id)-1] += 1
                        query2 = step["query"]
                        if "BLEU" in metric_type:
                            score = bleu(query2, query1)
                        else:
                            score = jaccard_similarity(query1, query2)
                        score_all.append({metric_type: score, "name":name, "position": "总体"})
                        if step_id == "1":
                            score_first.append({metric_type: score, "name":name, "position": "第1次查询"})
                        else:
                            score_others.append({metric_type: score, "name":name, "position": ">=2次查询"})

    # 把以上数据以dataFrame格式存储到文件中（续写，不要清空文件内原有内容），便于后续绘制seaborn嵌套箱线图
    # 补全代码：
    # 将分数列表转换为DataFrame
    df_all = pd.DataFrame(score_all)
    df_first = pd.DataFrame(score_first)
    df_others = pd.DataFrame(score_others)
    # 合并三个DataFrame
    df = pd.concat([df_all, df_first, df_others])

    try:
        with open(output_path, 'x') as f:  # 尝试创建文件
            df.to_csv(f, index=False, mode='w', header=True)  # 如果文件不存在，则写入并包含头
    except FileExistsError:  # 如果文件已存在
        with open(output_path, 'a') as f:  # 打开文件追加数据
            df.to_csv(f, index=False, mode='a', header=False)  # 追加数据，不包含头



output_path = project_path('evaluation', 'new', 'actions_bert.csv')

# evaluation_bl(bl2_queries_with_tasks, "1 随机选择", "Jaccard相似度", output_path)
# evaluation_bl(bl2_queries_with_tasks, "1 随机选择", "BLEU", output_path)
evaluation_bl(bl2_queries_with_tasks, "1 随机选择", "BERTScore", output_path)

# evaluation_bl(bl1_queries_with_tasks, "2 频率选择", "Jaccard相似度", output_path)
# evaluation_bl(bl1_queries_with_tasks, "2 频率选择", "BLEU", output_path)
evaluation_bl(bl1_queries_with_tasks, "2 频率选择", "BERTScore", output_path)


# output_path = stopwords_file = project_path('evaluation', 'new', 'prompt_bert.csv')

# evaluation_bl(bl1_queries_with_tasks, "1 随机选择", "Jaccard相似度", output_path)
# evaluation_bl(bl1_queries_with_tasks, "1 随机选择", "BLEU", output_path)
# evaluation_bl(bl1_queries_with_tasks, "1 随机选择", "BERTScore", output_path)

# evaluation_bl(bl2_queries_with_tasks, "2 频率选择", "Jaccard相似度", output_path)
# evaluation_bl(bl2_queries_with_tasks, "2 频率选择", "BLEU", output_path)
# evaluation_bl(bl2_queries_with_tasks, "2 频率选择", "BERTScore", output_path)

