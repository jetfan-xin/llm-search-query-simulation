# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import os
import json
from evaluation_jaccard import get_queries_with_tasks
from bert_score import BERTScorer
import torch
from prompt_library_s import all_task_background, all_task_goal
bl_data_num = [82, 66, 73, 89, 100, 55, 85, 53, 76, 58]

def get_queries_with_tasks(data_path):

    with open(data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    queries = {}
    if "baseline" in data_path:
        for task_id, task in data.items():
            queries[task_id] = task[0]

    else:
        for user in data:
            for task_id, task in user["task"].items():
                queries.setdefault(task_id, [])
                for step_id, step in task.items():
                    queries[task_id].append(step["query"])
    return queries

class Bert_Evaluation:

    def __init__(self):
        self.scorer = BERTScorer(model_type='bert-base-chinese', lang="zh", batch_size=1,
                            device='cuda' if torch.cuda.is_available() else 'cpu')

        self.task_description = {}
        for task_id, task_background in all_task_background.items():
            self.task_description[task_id] = all_task_background[task_id]+all_task_goal[task_id]

    def evaluation_description_jaccard(self, name, queries):
        pass

        bert_q2desc = []
        bert_intra = []

        for task_id, task_queries in queries.items():
            print("task:", task_id)

            for query in task_queries:
                score = float(self.scorer.score([query], [self.task_description[task_id]])[-1].item())
                bert_q2desc.append(score)

            for i, query1 in enumerate(task_queries):
                for j, query2 in enumerate(task_queries):
                    if i < j:
                        score = float(self.scorer.score([query1], [query2])[-1].item())
                        bert_intra.append(score)

        print(f"{name}\t{sum(bert_q2desc) / len(bert_q2desc)}\t{sum(bert_intra) / len(bert_intra)}")

bert_evaluation = Bert_Evaluation()

bl2 = get_queries_with_tasks(os.path.join('baseline', '2', 'output', 'baseline2_data.json'))
bert_evaluation.evaluation_description_jaccard("随机选择", bl2)

bl1 = get_queries_with_tasks(os.path.join('baseline', '1', 'output', 'baseline1_data.json'))
bert_evaluation.evaluation_description_jaccard("频率选择", bl1)

standard = get_queries_with_tasks(os.path.join('data', 'cleaned_.json'))
bert_evaluation.evaluation_description_jaccard("标准", standard)

wo_thought = get_queries_with_tasks(os.path.join('data', 'cleaned_wo_thought.json'))
bert_evaluation.evaluation_description_jaccard("无理由", wo_thought)

wo_feedback = get_queries_with_tasks(os.path.join('data', 'cleaned_wo_feedback.json'))
bert_evaluation.evaluation_description_jaccard("无反馈", wo_feedback)

wo_thought_feedback = get_queries_with_tasks(os.path.join('data', 'cleaned_wo_thought_feedback.json'))
bert_evaluation.evaluation_description_jaccard("无理由无反馈", wo_thought_feedback)

wo_observation = get_queries_with_tasks(os.path.join('data', 'cleaned_wo_observation.json'))
bert_evaluation.evaluation_description_jaccard("无观察", wo_observation)

wo_charactor = get_queries_with_tasks(os.path.join('data', 'cleaned_wo_charactor.json'))
bert_evaluation.evaluation_description_jaccard("无用户", wo_charactor)

wo_guidance = get_queries_with_tasks(os.path.join('data', 'cleaned_wo_guidance.json'))
bert_evaluation.evaluation_description_jaccard("无示例", wo_guidance)

wo_guidance_charactor = get_queries_with_tasks(os.path.join('data', 'cleaned_wo_guidance_charactor.json'))
bert_evaluation.evaluation_description_jaccard("无用户无示例", wo_guidance_charactor)

tol_exp = get_queries_with_tasks(os.path.join('data', 'cleaned_tol_exp.json'))
bert_evaluation.evaluation_description_jaccard("不恰当示例", tol_exp)

tol = get_queries_with_tasks(os.path.join('data', 'cleaned_tol.json'))
bert_evaluation.evaluation_description_jaccard("温度=1", tol)

tol_5 = get_queries_with_tasks(os.path.join('data', 'cleaned_tol_temp0.5.json'))
bert_evaluation.evaluation_description_jaccard("温度=0.5", tol_5)

tol_15 = get_queries_with_tasks(os.path.join('data', 'cleaned_tol_temp1.5.json'))
bert_evaluation.evaluation_description_jaccard("温度=1.5", tol_15)
