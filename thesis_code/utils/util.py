# 用于评估基线和标准实验每步的三个指标
import os
import json
import jieba
import re
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import BERTScorer
import torch

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_path(*parts):
    return os.path.join(CODE_DIR, *parts)

def get_queries_with_tasks(data):
    # 获取每个task下的分步的query
    queries = {}
    for user in data:
        for task_id, task in user["task"].items():
            queries.setdefault(task_id, {"1":[], "2":[], "3":[], "4": []})
            for step_id, step in task.items():
                if step_id == "1":
                    queries[task_id]["1"].append(step["query"])
                elif step_id == "2":
                    queries[task_id]["2"].append(step["query"])
                elif step_id == "3":
                    queries[task_id]["3"].append(step["query"])
                else:
                    queries[task_id]["4"].append(step["query"])
    return queries

bl_data_num = [82, 66, 73, 89, 100, 55, 85, 53, 76, 58]

smoothie = SmoothingFunction().method1

stopwords_file = project_path('baseline', 'stopwords.txt')
pattern = re.compile(r'[\u4e00-\u9fff]')
stopwords = []
with open(stopwords_file, 'r', encoding='utf-8') as file:
    for line in file:
        stopwords.append(line.strip())

original_path = project_path('data', 'extracted_original_data_data0405.json')
with open(original_path, 'r', encoding='utf-8') as file:
    original_queries_with_steps = json.load(file)

original_queries_with_tasks = get_queries_with_tasks(original_queries_with_steps)


bl1_path = project_path('baseline', '1', 'output', 'baseline1_data.json')
with open(bl1_path, 'r', encoding='utf-8') as file:
    bl1_queries_with_tasks = json.load(file)

bl2_path = project_path('baseline', '2', 'output', 'baseline2_data.json')
with open(bl2_path, 'r', encoding='utf-8') as file:
    bl2_queries_with_tasks = json.load(file)

llm_path = project_path('data', 'cleaned_.json')
with open(llm_path, 'r', encoding='utf-8') as file:
    llm_queries_with_steps = json.load(file)

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


def evaluation_with_steps(metric_type):
    step1 = []
    step2 = []
    step3 = []
    step4 = []
    # 处理基线
    for bl_queries in [bl2_queries_with_tasks, bl1_queries_with_tasks]:
        bl_queries_with_tasks = {}
        for task_id in [str(j) for j in range(1, 11)]:
            bl_queries_with_tasks[task_id] = []
            for i in range(10):
                bl_queries_with_tasks[task_id].extend(bl_queries[task_id][i])
        # for 10 task
        s1 = []
        s2 = []
        s3 = []
        s4 = []
        num = [0]*10  # for 10 task

        for i in range(10): # round
            if "bert" in metric_type:
                for task_id, task in original_queries_with_tasks.items():
                    for step_id, step in task.items():
                        if step_id == "1":
                            length = len(original_queries_with_tasks[task_id]["1"])
                            score_list = [float(f1_score.item()) for f1_score in bl_scorer[int(task_id) - 1].score(bl_queries_with_tasks[task_id][num[int(task_id) - 1]: num[int(task_id) - 1] + length], original_queries_with_tasks[task_id]["1"])[-1]]
                            num[int(task_id)-1] += length
                            s1.extend(score_list)
                        elif step_id == "2":
                            length = len(original_queries_with_tasks[task_id]["2"])
                            score_list = [float(f1_score.item()) for f1_score in bl_scorer[int(task_id) - 1].score(
                                bl_queries_with_tasks[task_id][num[int(task_id) - 1]: num[int(task_id) - 1] + length],
                                original_queries_with_tasks[task_id]["2"])[-1]]
                            num[int(task_id) - 1] += length
                            s2.extend(score_list)
                        elif step_id == "3":
                            length = len(original_queries_with_tasks[task_id]["3"])
                            score_list = [float(f1_score.item()) for f1_score in bl_scorer[int(task_id) - 1].score(
                                bl_queries_with_tasks[task_id][num[int(task_id) - 1]: num[int(task_id) - 1] + length],
                                original_queries_with_tasks[task_id]["3"])[-1]]
                            num[int(task_id) - 1] += length
                            s3.extend(score_list)
                        else:
                            length = len(original_queries_with_tasks[task_id]["4"])
                            score_list = [float(f1_score.item()) for f1_score in bl_scorer[int(task_id) - 1].score(
                                bl_queries_with_tasks[task_id][num[int(task_id) - 1]: num[int(task_id) - 1] + length],
                                original_queries_with_tasks[task_id]["4"])[-1]]
                            num[int(task_id) - 1] += length
                            s4.extend(score_list)
            else:
                for user in original_queries_with_steps:
                    for task_id, task in user["task"].items():
                        for step_id, step in task.items():
                            query1 = bl_queries_with_tasks[task_id][num[int(task_id)-1]]
                            num[int(task_id)-1] += 1
                            query2 = step["query"]

                            if "bleu" in metric_type:
                                score = bleu(query2, query1)
                            else:
                                score = jaccard_similarity(query1, query2)
                            if step_id == "1":
                                s1.append(score)
                            elif step_id == "2":
                                s2.append(score)
                            elif step_id == "3":
                                s3.append(score)
                            else:
                                s4.append(score)

        step1.append(sum(s1) / len(s1))
        step2.append(sum(s2) / len(s2))
        step3.append(sum(s3) / len(s3))
        step4.append(sum(s4) / len(s4))

    # 处理标准
    # for 10 task
    s1 = []
    s2 = []
    s3 = []
    s4 = []

    for user in original_queries_with_steps:
        for u in llm_queries_with_steps:
            if u["user_id"] == user["user_id"]:
                llm_user = u
        for task_id, task in user["task"].items():
            for step_id, step in task.items():
                query1 = llm_user["task"][task_id][step_id]["query"]
                #print(f"用户{user['user_id']} 任务{task_id} 步数{step_id}")
                num[int(task_id) - 1] += 1
                query2 = step["query"]
                if "bert" in metric_type:
                    score = float(llm_scorer.score([query1], [query2])[-1].item())
                elif "bleu" in metric_type:
                    score = bleu(query2, query1)
                else:
                    score = jaccard_similarity(query1, query2)
                if step_id == "1":
                    s1.append(score)
                elif step_id == "2":
                    s2.append(score)
                elif step_id == "3":
                    s3.append(score)
                else:
                    s4.append(score)

    step1.append(sum(s1) / len(s1))
    step2.append(sum(s2) / len(s2))
    step3.append(sum(s3) / len(s3))
    step4.append(sum(s4) / len(s4))

    print(step1, "\n", step2, "\n", step3, "\n", step4)
    return step1, step2, step3, step4


# evaluation_with_steps(jaccard_similarity)

llm_scorer = BERTScorer(model_type="bert-base-chinese", lang="zh", batch_size=1,device='cuda' if torch.cuda.is_available() else 'cpu')

bl_scorer = []
for i in range(10):
    # 实例化BERTScorer，指定使用的模型和语言
    bl_scorer.append(BERTScorer(model_type="bert-base-chinese", lang="zh", batch_size=bl_data_num[i],
                            device='cuda' if torch.cuda.is_available() else 'cpu'))

# evaluation_with_steps("bleu")
evaluation_with_steps("bert")



# jaccard
'''
标准
 [0.0907118439651399, 0.12747570548912981, 0.4555137965482791] 
 [0.07800140095594654, 0.09781376451830982, 0.31539686463928907] 
 [0.06996861360861387, 0.08861728826728857, 0.407860606060606] 
 [0.05982686757686779, 0.07420766439442927, 0.36467099567099553]
'''

'''
wo_guidance
 [0.0907118439651399, 0.12747570548912981, 0.45899226252674497] 
 [0.07800140095594654, 0.09781376451830982, 0.3124730908821819] 
 [0.06996861360861387, 0.08861728826728857, 0.42208282828282817] 
 [0.05982686757686779, 0.07420766439442927, 0.34649999999999975]
'''

'''
不恰当示例
 [0.0907118439651399, 0.12747570548912981, 0.365948400258745] 
 [0.07800140095594654, 0.09781376451830982, 0.1408662465480647] 
 [0.06996861360861387, 0.08861728826728857, 0.3044853146853147] 
 [0.05982686757686779, 0.07420766439442927, 0.23242496392496392]
温度=1
[0.0907118439651399, 0.12747570548912981, 0.4020279815969471] 
 [0.07800140095594654, 0.09781376451830982, 0.33036448680388086] 
 [0.06996861360861387, 0.08861728826728857, 0.37316219336219336] 
 [0.05982686757686779, 0.07420766439442927, 0.32056673881673875]
'''

# bleu
'''
 [0.08485926807839562, 0.12025040790293898, 0.4407855927133155] 
 [0.0749539947070669, 0.10337895905646252, 0.3805450871361278] 
 [0.06943701825318725, 0.09358308751598751, 0.4349473495328857] 
 [0.05705228455754839, 0.07905068193885775, 0.40116747541544184]
'''

'''
 [0.5772920591461247, 0.6147678360240213, 0.8044359673713816] 
 [0.5764631529799615, 0.607949908213182, 0.7641062077247736] 
 [0.5809110555648803, 0.6070079032659531, 0.7902774229049683] 
 [0.5686414869725704, 0.5896915210485458, 0.7579162615537643]
'''
