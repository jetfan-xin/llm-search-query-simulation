import os
import json
from evaluation_jaccard import get_queries_with_tasks
from bert_score import BERTScorer
import torch
from prompt_library_s import all_task_background, all_task_goal
from project_paths import project_path
bl_data_num = [82, 66, 73, 89, 100, 55, 85, 53, 76, 58]

def get_queries_with_tasks(data_path):
    # 获取每个task下的分步的query
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
    # 1. 原始查询
    # 1.1 每个查询&背 景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    # 1.3 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图

    # 2. llm模拟查询
    # 2.1 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    # 2.3 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图

    # 3. 基线模拟查询
    # 3.1 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    # 3.3 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图

    def __init__(self):
        self.scorer = BERTScorer(model_type='bert-base-chinese', lang="zh", batch_size=1,
                            device='cuda' if torch.cuda.is_available() else 'cpu')

        self.task_description = {}
        for task_id, task_background in all_task_background.items():
            self.task_description[task_id] = all_task_background[task_id]+all_task_goal[task_id]

    def evaluation_description_jaccard(self, name, queries):
        """
        1. 查询集合&背景，计算所有主题 & 整体的jaccard similarity
        2. 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        3. 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        :param queries: 字典，key:task_id, value:查询list，可能是原始查询、llm模拟查询或基线模拟查询
        """

        bert_q2desc = []
        bert_intra = []

        for task_id, task_queries in queries.items():
            print("task:", task_id)
            # 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
            for query in task_queries:
                score = float(self.scorer.score([query], [self.task_description[task_id]])[-1].item())
                bert_q2desc.append(score)
                # print("\tquery:", query, "score:", score)

            # 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
            for i, query1 in enumerate(task_queries):
                for j, query2 in enumerate(task_queries):
                    if i < j:  # To avoid repeating comparisons
                        score = float(self.scorer.score([query1], [query2])[-1].item())
                        bert_intra.append(score)
                        # print("\tquery1:", query1, "query2:", query2, "score:", score)

        print(f"{name}\t{sum(bert_q2desc) / len(bert_q2desc)}\t{sum(bert_intra) / len(bert_intra)}")  # 保存jcd均值，task_id为0

bert_evaluation = Bert_Evaluation()

# original = get_queries_with_tasks(project_path('data', 'extracted_original_data_data0405.json'))
# bert_evaluation.evaluation_description_jaccard("真实查询", original)

bl2 = get_queries_with_tasks(project_path('baseline', '2', 'output', 'baseline2_data.json'))
bert_evaluation.evaluation_description_jaccard("随机选择", bl2)

bl1 = get_queries_with_tasks(project_path('baseline', '1', 'output', 'baseline1_data.json'))
bert_evaluation.evaluation_description_jaccard("频率选择", bl1)

standard = get_queries_with_tasks(project_path('data', 'cleaned_.json'))
bert_evaluation.evaluation_description_jaccard("标准", standard)

wo_thought = get_queries_with_tasks(project_path('data', 'cleaned_wo_thought.json'))
bert_evaluation.evaluation_description_jaccard("无理由", wo_thought)

wo_feedback = get_queries_with_tasks(project_path('data', 'cleaned_wo_feedback.json'))
bert_evaluation.evaluation_description_jaccard("无反馈", wo_feedback)

wo_thought_feedback = get_queries_with_tasks(project_path('data', 'cleaned_wo_thought_feedback.json'))
bert_evaluation.evaluation_description_jaccard("无理由无反馈", wo_thought_feedback)

wo_observation = get_queries_with_tasks(project_path('data', 'cleaned_wo_observation.json'))
bert_evaluation.evaluation_description_jaccard("无观察", wo_observation)

wo_charactor = get_queries_with_tasks(project_path('data', 'cleaned_wo_charactor.json'))
bert_evaluation.evaluation_description_jaccard("无用户", wo_charactor)

wo_guidance = get_queries_with_tasks(project_path('data', 'cleaned_wo_guidance.json'))
bert_evaluation.evaluation_description_jaccard("无示例", wo_guidance)

wo_guidance_charactor = get_queries_with_tasks(project_path('data', 'cleaned_wo_guidance_charactor.json'))
bert_evaluation.evaluation_description_jaccard("无用户无示例", wo_guidance_charactor)

tol_exp = get_queries_with_tasks(project_path('data', 'cleaned_tol_exp.json'))
bert_evaluation.evaluation_description_jaccard("不恰当示例", tol_exp)

tol = get_queries_with_tasks(project_path('data', 'cleaned_tol.json'))
bert_evaluation.evaluation_description_jaccard("温度=1", tol)

tol_5 = get_queries_with_tasks(project_path('data', 'cleaned_tol_temp0.5.json'))
bert_evaluation.evaluation_description_jaccard("温度=0.5", tol_5)

tol_15 = get_queries_with_tasks(project_path('data', 'cleaned_tol_temp1.5.json'))
bert_evaluation.evaluation_description_jaccard("温度=1.5", tol_15)







