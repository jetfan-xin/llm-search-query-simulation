import os
import json
from bert_score import score

from evaluation_jaccard import get_queries_with_tasks

# from transformers import BertTokenizer, BertModel
import torch
import torch.nn.functional as F
from project_paths import project_path


def bert_score_cn(reference, candidate, tokenizer, model):

    # 对参考文本和候选文本进行编码
    tokens_ref = tokenizer(reference, return_tensors='pt', padding=True, truncation=True, max_length=128)
    tokens_cand = tokenizer(candidate, return_tensors='pt', padding=True, truncation=True, max_length=128)

    # 获取嵌入向量
    with torch.no_grad():
        embeddings_ref = model(**tokens_ref)['last_hidden_state']
        embeddings_cand = model(**tokens_cand)['last_hidden_state']

    # 计算余弦相似度矩阵
    embeddings_ref = torch.mean(embeddings_ref, dim=1)
    embeddings_cand = torch.mean(embeddings_cand, dim=1)
    cosine_sim_matrix = F.cosine_similarity(embeddings_cand.unsqueeze(1), embeddings_ref.unsqueeze(0), dim=2)

    # 对于每个候选嵌入，找到与之相似度最高的参考嵌入，并计算平均相似度
    max_similarities = cosine_sim_matrix.max(dim=1).values
    score = max_similarities.mean().item()

    return score



def bert_score_sets_avg(references, candidates, tokenizer, model):
    # 批量编码参考文本和候选文本
    tokens_ref = tokenizer(references, return_tensors='pt', padding=True, truncation=True, max_length=128)
    tokens_cand = tokenizer(candidates, return_tensors='pt', padding=True, truncation=True, max_length=128)

    # 获取嵌入向量
    with torch.no_grad():
        embeddings_ref = model(**tokens_ref)['last_hidden_state']
        embeddings_cand = model(**tokens_cand)['last_hidden_state']

    # 计算每个文本的嵌入向量平均值
    embeddings_ref_mean = torch.mean(embeddings_ref, dim=1)
    embeddings_cand_mean = torch.mean(embeddings_cand, dim=1)

    # 计算余弦相似度矩阵
    cosine_sim_matrix = F.cosine_similarity(embeddings_cand_mean.unsqueeze(1), embeddings_ref_mean.unsqueeze(0), dim=2)

    # 对于每个候选嵌入，计算其与所有参考嵌入的平均相似度
    average_similarities = cosine_sim_matrix.mean(dim=1)

    # 计算这些平均相似度的平均值作为BERT Score
    score = average_similarities.mean().item()

    return score, average_similarities.tolist()

def bert_socre_package(cands, refs):
    P, R, F1 = score(cands, refs, model_type="bert-base-chinese",lang="zh", verbose=True)
    print(F1)
    # print(f"System level F1 score: {F1.mean():.3f}")
    return F1

# def evaluation_llm_bert(original_path, generate_path, tokenizer, model, output_file):
#
#     with open(original_path, 'r', encoding='utf-8') as file:
#         original_data = json.load(file)
#
#     with open(generate_path, 'r', encoding='utf-8') as file:
#         generate_data = json.load(file)
#
#     # Initialize lists to store BERT scores
#     bert_score_list = []
#     bert_score_list_first = []
#     bert_score_list_others = []
#
#     bert_score_with_tasks = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
#     bert_score_with_tasks_first = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
#     bert_score_with_tasks_others = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
#
#     # Iterate through the dataset to compute BERT scores for each query
#     for user_num, user in enumerate(generate_data):
#         # for task_id in generate_data[user_id]:
#         ori_user = {}
#         for ori_u in original_data:
#             if ori_u["user_id"] == user["user_id"]:
#                 ori_user = ori_u
#                 break
#         for task_id, task in user["task"].items():
#             for query_step in list(task.keys()):
#                 # Calculate BERT score for each pair of original and generated queries
#                 bert_score = bert_score_cn(ori_user["task"][task_id][query_step]["query"], task[query_step]["query"], tokenizer, model)
#                 bert_score_list.append(bert_score)
#
#                 bert_score_with_tasks[task_id].append(bert_score)
#
#                 if query_step == "1":
#                     bert_score_list_first.append(bert_score)
#                     bert_score_with_tasks_first[task_id].append(bert_score)
#                 else:
#                     bert_score_list_others.append(bert_score)
#                     bert_score_with_tasks_others[task_id].append(bert_score)
#
#
#
#     for task_id in [str(i) for i in range(1, 11)]:
#         average_bert_score = sum(bert_score_with_tasks[task_id]) / len(bert_score_with_tasks[task_id])
#         average_bert_score_first = sum(bert_score_with_tasks_first[task_id]) / len(bert_score_with_tasks_first[task_id])
#         average_bert_score_others = sum(bert_score_with_tasks_others[task_id]) / len(bert_score_with_tasks_others[task_id])
#
#         print(f"task {task_id}: Average BERT Score: {average_bert_score}")
#         print(f"task {task_id}: Average first BERT Score: {average_bert_score_first}")
#         print(f"task {task_id}: Average other BERT Score: {average_bert_score_others}\n")
#
#
#     # Print the average BERT score
#     if bert_score_list:
#         average_bert_score = sum(bert_score_list) / len(bert_score_list)
#         print(f"Average BERT Score: {average_bert_score}")
#     if bert_score_list_first:
#         average_bert_score_first = sum(bert_score_list_first) / len(bert_score_list_first)
#         print(f"Average first BERT Score: {average_bert_score_first}")
#     if bert_score_list_others:
#         average_bert_score_others = sum(bert_score_list_others) / len(bert_score_list_others)
#         print(f"Average other BERT Score: {average_bert_score_others}")
#
#     # 将更新后的数据写回文件
#     with open(project_path('evaluation', 'bert', "bert_score_list"+output_file), 'w',encoding='utf-8') as file:
#         json.dump(bert_score_list, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
#     with open(project_path('evaluation', 'bert', "bert_score_list_first"+output_file), 'w',encoding='utf-8') as file:
#         json.dump(bert_score_list_first, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
#     with open(project_path('evaluation', 'bert', "bert_score_list_others"+output_file), 'w',encoding='utf-8') as file:
#         json.dump(bert_score_list_others, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)


def evaluation_llm_bert_package(original_path, generate_path, output_file):
    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    with open(generate_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)

    # Initialize lists to store BERT scores
    bert_score_list = []
    bert_score_list_first = []
    bert_score_list_others = []

    bert_score_with_tasks = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
    bert_score_with_tasks_first = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                   "10": []}
    bert_score_with_tasks_others = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                    "10": []}

    # Iterate through the dataset to compute BERT scores for each query
    for user_num, user in enumerate(generate_data):
        # for task_id in generate_data[user_id]:
        ori_user = {}
        for ori_u in original_data:
            if ori_u["user_id"] == user["user_id"]:
                ori_user = ori_u
                break
        for task_id, task in user["task"].items():
            for query_step in list(task.keys()):
                # Calculate BERT score for each pair of original and generated queries
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

    # Print the average BERT score
    if bert_score_list:
        average_bert_score = sum(bert_score_list) / len(bert_score_list)
        print(f"Average BERT Score: {average_bert_score}")
    if bert_score_list_first:
        average_bert_score_first = sum(bert_score_list_first) / len(bert_score_list_first)
        print(f"Average first BERT Score: {average_bert_score_first}")
    if bert_score_list_others:
        average_bert_score_others = sum(bert_score_list_others) / len(bert_score_list_others)
        print(f"Average other BERT Score: {average_bert_score_others}")

    # 将更新后的数据写回文件
    with open(project_path('evaluation', 'bert', "p_bert_score_list" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bert_score_list, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(project_path('evaluation', 'bert', "p_bert_score_list_first" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bert_score_list_first, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(project_path('evaluation', 'bert', "p_bert_score_list_others" + output_file), 'w',
              encoding='utf-8') as file:
        json.dump(bert_score_list_others, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

#
# def evaluation_bl_bert(original_path, bl_data_path, tokenizer, model):
#
#     with open(bl_data_path, 'r', encoding='utf-8') as file:
#         generate_data = json.load(file)
#
#     output_data = {}
#     # 获取每个task下的原始query
#     original_queries = get_queries_with_tasks(original_path)
#
#     bert_scores_all = []
#     for task_id, task in generate_data.items() :
#         bert_scores = []
#         output_data[task_id] = []
#         for g_i in task:
#             length = min(len(g_i), len(original_queries[task_id]))
#             if len(g_i) != len(original_queries[task_id]):
#                 print("长度不等")
#             references = original_queries[task_id][:length]
#             candidates = g_i[:length]
#             score, scores_list = bert_score_sets_avg(references, candidates, tokenizer, model)
#             bert_scores.append(score)
#             output_data[task_id].append(scores_list)
#         average_bert_score = sum(bert_scores) / len(bert_scores)
#         bert_scores_all.append(average_bert_score)
#         print(f"task {task_id}: Average BERT Score: {average_bert_score}")
#
#     print(f"\nALL: Average BERT Score: {sum(bert_scores_all) / len(bert_scores_all)}")
#
#     with open(project_path('evaluation', 'bert', "bert_score_basline2.json"), 'w', encoding='utf-8') as file:
#         json.dump(output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)


def evaluation_bl_bert_package(original_path, bl_data_path):

    with open(bl_data_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)
    output_data = {}
    # 获取每个task下的原始query
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

    with open(project_path('evaluation', 'bert', "bert_score_basline1_package.json"), 'w', encoding='utf-8') as file:
        json.dump(output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    # 初始化模型和分词器
    model_name = 'bert-base-chinese'
    # tokenizer = BertTokenizer.from_pretrained(model_name)
    # model = BertModel.from_pretrained(model_name)

    prompt_type = "" # "all_prompt" #'wo_guidance'

    # generate_path = project_path('data', f'cleaned_output_output_data_data0405_gpt-3.5-turbo-0125_repeatedEXP.json')
    # generate_path = project_path('data', f'cleaned_output_output_data_{data_file}_{llm_model}_temp{temp}.json')
    generate_path = project_path('data', f'cleaned_{prompt_type}.json')
    original_path = project_path('data', f'extracted_original_data_all.json')
    bl_data_path = project_path('baseline', '1', 'output', 'baseline1_data.json')

    output_file = f'_{prompt_type}.json'
    #
    # evaluation_llm_bert(original_path, generate_path, tokenizer, model, output_file)
    # evaluation_bl_bert(original_path, bl_data_path, tokenizer, model)
    # evaluation_bl_bert_package(original_path, bl_data_path)
    evaluation_llm_bert_package(original_path, generate_path, output_file)


    """
    # baseline
    task 1: Average BERT Score: 0.7981671452522278
    task 2: Average BERT Score: 0.8157214462757111
    task 3: Average BERT Score: 0.795785129070282
    task 4: Average BERT Score: 0.838881927728653
    task 5: Average BERT Score: 0.8308537185192109
    task 6: Average BERT Score: 0.8209433794021607
    task 7: Average BERT Score: 0.8020581007003784
    task 8: Average BERT Score: 0.8087828755378723
    task 9: Average BERT Score: 0.8268480837345124
    task 10: Average BERT Score: 0.8239584743976593    
    ALL: Average BERT Score: 0.8162000280618669

    # 示例：动物保护组织 temp=1
    Average BERT Score: 0.8299229350692401
    Average first BERT Score: 0.856329248327276
    Average other BERT Score: 0.8129934520048547
    
    # 示例：缓解压力 temp=1
    Average BERT Score: 0.8685839501788205
    Average first BERT Score: 0.8742707770446251
    Average other BERT Score: 0.8646851799871341
    
    # 示例：缓解压力 temp=0.5
    Average BERT Score: 0.8670623026589692
    Average first BERT Score: 0.8716830200162428
    Average other BERT Score: 0.8638944349672214

    # 示例：缓解压力 temp=1.5
    Average BERT Score: 0.8601949168055245
    Average first BERT Score: 0.867160410823294
    Average other BERT Score: 0.8554359859044952
    
    # 无示例 temp=1
    Average BERT Score: 0.870231862573102
    Average first BERT Score: 0.8738138587310397
    Average other BERT Score: 0.8677761205262889
    
    # 无示例 temp=0.5
    Average BERT Score: 0.8668459248409031
    Average first BERT Score: 0.8732185304164887
    Average other BERT Score: 0.8624769990325819
    
    # 无示例 无角色 temp=1
    Average BERT Score: 0.870216965675354
    Average first BERT Score: 0.8768713451665023
    Average other BERT Score: 0.8656548615324864
    
    # 示例：缓解压力 无角色 temp=1
    Average BERT Score: 0.8679883683212676
    Average first BERT Score: 0.8742577168448218
    Average other BERT Score: 0.863690233399682
    
    # 无示例 无角色 无思考 temp=1
    Average BERT Score: 0.8744579509297729
    Average first BERT Score: 0.8863181253959392
    Average other BERT Score: 0.8663268620522592
    
    # 无示例 无角色 无思考 无反馈 temp=1
    Average BERT Score: 0.870387977587391
    Average first BERT Score: 0.8828174605451781
    Average other BERT Score: 0.8618665826517922
    
    # 无示例 无角色 无思考输出 temp=1
    Average BERT Score: 0.876163914778791
    Average first BERT Score: 0.8812793452164223
    Average other BERT Score: 0.8726568820910533
        
    # 无角色 无思考输出 temp=1
    Average BERT Score: 0.877988287058318
    Average first BERT Score: 0.8879261448465544
    Average other BERT Score: 0.8711750985037351
    
    # 无思考输出 temp=1
    Average BERT Score: 0.8765853110068643
    Average first BERT Score: 0.8868032525325643
    Average other BERT Score: 0.8695801028686776
    
    # 无思考输出 无思考 无反馈 temp=1
    Average BERT Score: 0.870387977587391
    Average first BERT Score: 0.8828174605451781
    Average other BERT Score: 0.8618665826517922
    
    # 无思考输出 无思考 temp=1
    Average BERT Score: 0.8762500312435343
    Average first BERT Score: 0.8899869756451968
    Average other BERT Score: 0.8668322679421581
    
    # 无思考输出 无反馈 temp=1
    Average BERT Score: 0.8764001106814616
    Average first BERT Score: 0.8857316473434711
    Average other BERT Score: 0.870002603277247
    
    # 无思考输出 无观察 temp=1
    Average BERT Score: 0.8765310154389199
    Average first BERT Score: 0.8920064323935015
    Average other BERT Score: 0.865921391522067
    
    """