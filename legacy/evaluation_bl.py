# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import os
import json
import jieba
import re
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import BERTScorer
import torch
import pandas as pd
bl_data_num = [82, 66, 73, 89, 100, 55, 85, 53, 76, 58]

smoothie = SmoothingFunction().method1

def query2terms(query):
    return set([t for t in jieba.cut(query) if t not in stopwords and re.search(pattern, t)])

def jaccard_similarity(query1, query2):
    pass
    set1 = query2terms(query1)
    set2 = query2terms(query2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def bleu(q1, q2):
    return sentence_bleu([q1],q2,weights=(0.5, 0.5, 0, 0), smoothing_function=smoothie)

def get_queries_with_tasks(data):

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

stopwords_file = os.path.join('baseline', 'stopwords.txt')
pattern = re.compile(r'[\u4e00-\u9fff]')
stopwords = []
with open(stopwords_file, 'r', encoding='utf-8') as file:
    for line in file:
        stopwords.append(line.strip())

original_path = os.path.join('data', 'extracted_original_data_data0405.json')
with open(original_path, 'r', encoding='utf-8') as file:
    original_data = json.load(file)
original_queries_with_tasks = get_queries_with_tasks(original_data)

bl1_path = os.path.join('baseline', '1', 'output', 'baseline1_data.json')
with open(bl1_path, 'r', encoding='utf-8') as file:
    bl1_queries_with_tasks = json.load(file)

bl2_path = os.path.join('baseline', '2', 'output', 'baseline2_data.json')
with open(bl2_path, 'r', encoding='utf-8') as file:
    bl2_queries_with_tasks = json.load(file)

bl_scorer = []
for i in range(10):

    bl_scorer.append(BERTScorer(model_type="bert-base-chinese", lang="zh", batch_size=bl_data_num[i],
                            device='cuda' if torch.cuda.is_available() else 'cpu'))

def evaluation_bl(data, name, metric_type, output_path):
    score_all = []
    score_first = []
    score_others = []

    bl_queries_with_tasks = {}
    for task_id in [str(j) for j in range(1, 11)]:
        bl_queries_with_tasks[task_id] = []
        for i in range(10):
            bl_queries_with_tasks[task_id].extend(data[task_id][i])

    num = [0]*10

    for i in range(10):
        if "BERTScore" in metric_type:
            for task_id, task in original_queries_with_tasks.items():

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

    df_all = pd.DataFrame(score_all)
    df_first = pd.DataFrame(score_first)
    df_others = pd.DataFrame(score_others)

    df = pd.concat([df_all, df_first, df_others])

    try:
        with open(output_path, 'x') as f:
            df.to_csv(f, index=False, mode='w', header=True)
    except FileExistsError:
        with open(output_path, 'a') as f:
            df.to_csv(f, index=False, mode='a', header=False)

output_path = os.path.join('evaluation', 'new', 'actions_bert.csv')

evaluation_bl(bl2_queries_with_tasks, "1 随机选择", "BERTScore", output_path)

evaluation_bl(bl1_queries_with_tasks, "2 频率选择", "BERTScore", output_path)
