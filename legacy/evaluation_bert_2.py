# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import os
import json
from evaluation_jaccard import get_queries_with_tasks

from bert_score import BERTScorer
import torch

bl_data_num = [82, 66, 73, 89, 100, 55, 85, 53, 76, 58]

def evaluation_llm_bert_package(original_path, generate_path, output_file):
    scorer = BERTScorer(model_type="bert-base-chinese", lang="zh", batch_size=1,
                        device='cuda' if torch.cuda.is_available() else 'cpu')
    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    with open(generate_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)

    bert_score_list = []
    bert_score_list_first = []
    bert_score_list_others = []

    bert_score_with_tasks = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
    bert_score_with_tasks_first = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                   "10": []}
    bert_score_with_tasks_others = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                    "10": []}

    for user_num, user in enumerate(generate_data):

        ori_user = {}
        for ori_u in original_data:
            if ori_u["user_id"] == user["user_id"]:
                ori_user = ori_u
                break
        for task_id, task in user["task"].items():
            for query_step in list(task.keys()):

                bert_score = float(scorer.score([task[query_step]["query"]], [ori_user["task"][task_id][query_step]["query"]])[-1].item())
                bert_score_list.append(bert_score)

                bert_score_with_tasks[task_id].append(bert_score)

                if query_step == "1":
                    bert_score_list_first.append(bert_score)
                    bert_score_with_tasks_first[task_id].append(bert_score)
                else:
                    bert_score_list_others.append(bert_score)
                    bert_score_with_tasks_others[task_id].append(bert_score)

    for task_id in [str(i) for i in range(1, 11)]:
        average_bert_score = sum(bert_score_with_tasks[task_id]) / len(bert_score_with_tasks[task_id])
        average_bert_score_first = sum(bert_score_with_tasks_first[task_id]) / len(bert_score_with_tasks_first[task_id])
        average_bert_score_others = sum(bert_score_with_tasks_others[task_id]) / len(
            bert_score_with_tasks_others[task_id])

        print(f"task {task_id}: Average BERT Score: {average_bert_score}")
        print(f"task {task_id}: Average first BERT Score: {average_bert_score_first}")
        print(f"task {task_id}: Average other BERT Score: {average_bert_score_others}\n")

    if bert_score_list:
        average_bert_score = sum(bert_score_list) / len(bert_score_list)
        print(f"Average BERT Score: {average_bert_score}")
    if bert_score_list_first:
        average_bert_score_first = sum(bert_score_list_first) / len(bert_score_list_first)
        print(f"Average first BERT Score: {average_bert_score_first}")
    if bert_score_list_others:
        average_bert_score_others = sum(bert_score_list_others) / len(bert_score_list_others)
        print(f"Average other BERT Score: {average_bert_score_others}")

    with open(os.path.join('evaluation', 'bert', "p_bert_score_list" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bert_score_list, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(os.path.join('evaluation', 'bert', "p_bert_score_list_first" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bert_score_list_first, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(os.path.join('evaluation', 'bert', "p_bert_score_list_others" + output_file), 'w',
              encoding='utf-8') as file:
        json.dump(bert_score_list_others, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

def evaluation_bl_bert_package(original_path, bl_data_path):

    with open(bl_data_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)
    output_data = {}

    original_queries = get_queries_with_tasks(original_path)

    bert_scores_all = []
    for task_id, task in generate_data.items():

        scorer = BERTScorer(model_type="bert-base-chinese", lang="zh", batch_size=bl_data_num[int(task_id)-1],
                                device='cuda' if torch.cuda.is_available() else 'cpu')
        bert_scores = []
        output_data[task_id] = []
        for g_i in task:
            length = min(len(g_i), len(original_queries[task_id]))
            if len(g_i) != len(original_queries[task_id]):
                print("长度不等")
            references = original_queries[task_id][:length]
            candidates = g_i[:length]

            score_list = [float(f1_score.item()) for f1_score in scorer.score(candidates, references)[-1]]

            bert_scores.extend(list(score_list))
            output_data[task_id].extend(list(score_list))
        average_bert_score = sum(bert_scores) / len(bert_scores)
        bert_scores_all.append(average_bert_score)
        print(f"task {task_id}: Average BERT Score: {average_bert_score}")

    print(f"\nALL: Average BERT Score: {sum(bert_scores_all) / len(bert_scores_all)}")

    with open(os.path.join('evaluation', 'bert', "p_bert_score_basline1.json"), 'w', encoding='utf-8') as file:
        json.dump(output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

if __name__ == '__main__':

    model_name = 'bert-base-chinese'

    prompt_type = "tol_temp1.5"
    print(prompt_type)

    generate_path = os.path.join('data', f'cleaned_{prompt_type}.json')
    original_path = os.path.join('data', f'extracted_original_data_all.json')
    bl_data_path = os.path.join('baseline', '1', 'output', 'baseline1_data.json')

    output_file = f'_{prompt_type}.json'

    evaluation_llm_bert_package(original_path, generate_path, output_file)

    pass
