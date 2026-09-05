# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import os
import json
from bert_score import score

from evaluation_jaccard import get_queries_with_tasks

import torch
import torch.nn.functional as F

def bert_score_cn(reference, candidate, tokenizer, model):

    tokens_ref = tokenizer(reference, return_tensors='pt', padding=True, truncation=True, max_length=128)
    tokens_cand = tokenizer(candidate, return_tensors='pt', padding=True, truncation=True, max_length=128)

    with torch.no_grad():
        embeddings_ref = model(**tokens_ref)['last_hidden_state']
        embeddings_cand = model(**tokens_cand)['last_hidden_state']

    embeddings_ref = torch.mean(embeddings_ref, dim=1)
    embeddings_cand = torch.mean(embeddings_cand, dim=1)
    cosine_sim_matrix = F.cosine_similarity(embeddings_cand.unsqueeze(1), embeddings_ref.unsqueeze(0), dim=2)

    max_similarities = cosine_sim_matrix.max(dim=1).values
    score = max_similarities.mean().item()

    return score

def bert_score_sets_avg(references, candidates, tokenizer, model):

    tokens_ref = tokenizer(references, return_tensors='pt', padding=True, truncation=True, max_length=128)
    tokens_cand = tokenizer(candidates, return_tensors='pt', padding=True, truncation=True, max_length=128)

    with torch.no_grad():
        embeddings_ref = model(**tokens_ref)['last_hidden_state']
        embeddings_cand = model(**tokens_cand)['last_hidden_state']

    embeddings_ref_mean = torch.mean(embeddings_ref, dim=1)
    embeddings_cand_mean = torch.mean(embeddings_cand, dim=1)

    cosine_sim_matrix = F.cosine_similarity(embeddings_cand_mean.unsqueeze(1), embeddings_ref_mean.unsqueeze(0), dim=2)

    average_similarities = cosine_sim_matrix.mean(dim=1)

    score = average_similarities.mean().item()

    return score, average_similarities.tolist()

def bert_socre_package(cands, refs):
    P, R, F1 = score(cands, refs, model_type="bert-base-chinese",lang="zh", verbose=True)
    print(F1)

    return F1

def evaluation_llm_bert_package(original_path, generate_path, output_file):
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

                bert_score = float(bert_socre_package([ori_user["task"][task_id][query_step]["query"]], [task[query_step]["query"]]))
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
    for task_id, task in generate_data.items() :
        bert_scores = []
        output_data[task_id] = []
        for g_i in task:
            length = min(len(g_i), len(original_queries[task_id]))
            if len(g_i) != len(original_queries[task_id]):
                print("长度不等")
            references = original_queries[task_id][:length]
            candidates = g_i[:length]
            score_list = bert_socre_package(references, candidates)
            bert_scores.extend(list(score_list))
            output_data[task_id].extend(list(score_list))
        average_bert_score = sum(bert_scores) / len(bert_scores)
        bert_scores_all.append(average_bert_score)
        print(f"task {task_id}: Average BERT Score: {average_bert_score}")

    print(f"\nALL: Average BERT Score: {sum(bert_scores_all) / len(bert_scores_all)}")

    with open(os.path.join('evaluation', 'bert', "bert_score_basline1_package.json"), 'w', encoding='utf-8') as file:
        json.dump(output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

if __name__ == '__main__':

    model_name = 'bert-base-chinese'

    prompt_type = ""

    generate_path = os.path.join('data', f'cleaned_{prompt_type}.json')
    original_path = os.path.join('data', f'extracted_original_data_all.json')
    bl_data_path = os.path.join('baseline', '1', 'output', 'baseline1_data.json')

    output_file = f'_{prompt_type}.json'

    evaluation_llm_bert_package(original_path, generate_path, output_file)

    pass
