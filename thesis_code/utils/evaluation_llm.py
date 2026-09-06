import os
import json
import jieba
import re
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import BERTScorer
import torch
import pandas as pd

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_path(*parts):
    return os.path.join(CODE_DIR, *parts)

llm_scorer = BERTScorer(model_type= 'bert-base-chinese', lang="zh", batch_size=1,device='cuda' if torch.cuda.is_available() else 'cpu')
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

stopwords_file = project_path('baseline', 'stopwords.txt')
pattern = re.compile(r'[\u4e00-\u9fff]')
stopwords = []
with open(stopwords_file, 'r', encoding='utf-8') as file:
    for line in file:
        stopwords.append(line.strip())

original_path = project_path('data', 'extracted_original_data_data0405.json')
with open(original_path, 'r', encoding='utf-8') as file:
    original_data = json.load(file)


def evaluation_llm(data_type, name, metric_type, output_path):
    with open(project_path('data', f'cleaned_{data_type}.json'), 'r', encoding='utf-8') as file:
        llm_data = json.load(file)

    # 处理标准
    score_all = []
    score_first = []
    score_others = []
    for user in original_data:
        for u in llm_data:
            if u["user_id"] == user["user_id"]:
                llm_user = u
        for task_id, task in user["task"].items():
            for step_id, step in task.items():
                query1 = llm_user["task"][task_id][step_id]["query"]
                #print(f"用户{user['user_id']} 任务{task_id} 步数{step_id}")
                query2 = step["query"]
                if "BERTScore" in metric_type:
                    score = float(llm_scorer.score([query1], [query2])[-1].item())
                elif "BLEU" in metric_type:
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

data_type = ""

# output_path = project_path('evaluation', 'new', 'prompt_jaccard.csv')
# output_path = project_path('evaluation', 'new', 'prompt_bleu.csv')
output_path = project_path('evaluation', 'new', 'prompt_bert.csv')

# evaluation_llm("", "3 标准", "Jaccard相似度", output_path)
# evaluation_llm("", "3 标准", "BLEU", output_path)
evaluation_llm("", "3 标准", "BERTScore", output_path)

# evaluation_llm("wo_charactor", "8 无用户", "Jaccard相似度", output_path)
# evaluation_llm("wo_charactor", "8 无用户", "BLEU", output_path)
evaluation_llm("wo_charactor", "8 无用户", "BERTScore", output_path)

# evaluation_llm("wo_guidance", "9 无示例", "Jaccard相似度", output_path)
# evaluation_llm("wo_guidance", "9 无示例", "BLEU", output_path)
evaluation_llm("wo_guidance", "9 无示例", "BERTScore", output_path)

# evaluation_llm("wo_guidance_charactor", "10 无用户无示例", "Jaccard相似度", output_path)
# evaluation_llm("wo_guidance_charactor", "10 无用户无示例", "BLEU", output_path)
evaluation_llm("wo_guidance_charactor", "10 无用户无示例", "BERTScore", output_path)




# output_path = project_path('evaluation', 'new', 'actions_jaccard.csv')
# output_path = project_path('evaluation', 'new', 'actions_bleu.csv')
output_path = project_path('evaluation', 'new', 'actions_bert.csv')

# evaluation_llm("", "3 标准", "Jaccard相似度", output_path)
# evaluation_llm("", "3 标准", "BLEU", output_path)
evaluation_llm("", "3 标准", "BERTScore", output_path)

# evaluation_llm("wo_thought", "4 无理由", "Jaccard相似度", output_path)
# evaluation_llm("wo_thought", "4 无理由", "BLEU", output_path)
evaluation_llm("wo_thought", "4 无理由", "BERTScore", output_path)

# evaluation_llm("wo_feedback", "5 无反馈", "Jaccard相似度", output_path)
# evaluation_llm("wo_feedback", "5 无反馈", "BLEU", output_path)
evaluation_llm("wo_feedback", "5 无反馈", "BERTScore", output_path)

# evaluation_llm("wo_thought_feedback", "6 无理由无反馈", "Jaccard相似度", output_path)
# evaluation_llm("wo_thought_feedback", "6 无理由无反馈", "BLEU", output_path)
evaluation_llm("wo_thought_feedback", "6 无理由无反馈", 'BERTScore', output_path)

evaluation_llm("wo_observation", "7 无观察", 'BERTScore', output_path)
