# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import os
import json
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from evaluation_jaccard import get_queries_with_tasks

def evaluation_llm_bleu(original_path, generate_path, output_file):

    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    with open(generate_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)

    bleu_score_list = []
    bleu_score_list_first = []
    bleu_score_list_others = []

    bleu_score_with_tasks = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
    bleu_score_with_tasks_first = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                   "10": []}
    bleu_score_with_tasks_others = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                    "10": []}

    for user_num, user in enumerate(generate_data):

        for ori_u in original_data:
            if ori_u["user_id"] == user["user_id"]:
                ori_user = ori_u
                break
        for task_id, task in user["task"].items():
            for query_step in list(task.keys()):

                smoothie = SmoothingFunction().method1
                bleu_score = sentence_bleu([ori_user["task"][task_id][query_step]["query"]],
                                           task[query_step]["query"],
                                           weights=(0.5, 0.5, 0, 0), smoothing_function=smoothie)
                bleu_score_list.append(bleu_score)

                bleu_score_with_tasks[task_id].append(bleu_score)

                if query_step == "1":
                    bleu_score_list_first.append(bleu_score)
                    bleu_score_with_tasks_first[task_id].append(bleu_score)
                else:
                    bleu_score_list_others.append(bleu_score)
                    bleu_score_with_tasks_others[task_id].append(bleu_score)

    for task_id in [str(i) for i in range(1, 11)]:
        average_bleu_score = sum(bleu_score_with_tasks[task_id]) / len(bleu_score_with_tasks[task_id])
        average_bleu_score_first = sum(bleu_score_with_tasks_first[task_id]) / len(bleu_score_with_tasks_first[task_id])
        average_bleu_score_others = sum(bleu_score_with_tasks_others[task_id]) / len(
            bleu_score_with_tasks_others[task_id])

        print(f"task {task_id}: Average BERT Score: {average_bleu_score}")
        print(f"task {task_id}: Average first BERT Score: {average_bleu_score_first}")
        print(f"task {task_id}: Average other BERT Score: {average_bleu_score_others}\n")

    with open(os.path.join('evaluation', 'bleu', "bleu_with_tasks" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bleu_score_with_tasks, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(os.path.join('evaluation', 'bleu', "bleu_with_tasks_first" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bleu_score_with_tasks_first, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(os.path.join('evaluation', 'bleu', "bleu_with_tasks_others" + output_file), 'w',
              encoding='utf-8') as file:
        json.dump(bleu_score_with_tasks_others, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    if bleu_score_list:
        average_bleu_score = sum(bleu_score_list) / len(bleu_score_list)
        print(f"Average BLEU Score: {average_bleu_score}")
    if bleu_score_list_first:
        average_bleu_score_first = sum(bleu_score_list_first) / len(bleu_score_list_first)
        print(f"Average first BLEU Score: {average_bleu_score_first}")
    if bleu_score_list_others:
        average_bleu_score_others = sum(bleu_score_list_others) / len(bleu_score_list_others)
        print(f"Average other BLEU Score: {average_bleu_score_others}")

    pass

def evaluation_bl_bleu(generate_file):
    generate_path = os.path.join('baseline','2', 'output', generate_file)
    with open(generate_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)

    original_path = os.path.join('data', f'extracted_original_data_all.json')
    original_queries = get_queries_with_tasks(original_path)
    bleu_with_tasks = {}
    bleu_scores_all = []
    for task_id, task in generate_data.items():
        bleu_scores = []
        bleu_with_tasks[task_id] = []
        for g_i in task:
            length = min(len(g_i), len(original_queries[task_id]))
            if len(g_i) != len(original_queries[task_id]):
                print("长度不等")
            smoothie = SmoothingFunction().method1
            score_list = [sentence_bleu([original], generated, weights=(0.5, 0.5, 0, 0), smoothing_function=smoothie)
                          for original, generated in zip(original_queries[task_id][:length], g_i[:length])]
            bleu_scores.extend(score_list)
            bleu_with_tasks[task_id].append(score_list)
        average_bleu_score = sum(bleu_scores) / len(bleu_scores)
        bleu_scores_all.append(average_bleu_score)
        print(f"task {task_id}: Average BLEU Score: {average_bleu_score}")

    print(f"\nALL: Average BLEU Score: {sum(bleu_scores_all) / len(bleu_scores_all)}")
    with open(os.path.join('evaluation', 'bleu', "baseline2_bleu_with_tasks.json"), 'w', encoding='utf-8') as file:
        json.dump(bleu_with_tasks, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    pass

if __name__ == '__main__':

    model_type = "wo_guidance_charactor"

    generate_path = os.path.join('data', f'cleaned_{model_type}.json')
    original_path = os.path.join('data', f'extracted_original_data_all.json')
    output_file = f'_{model_type}.json'
    evaluation_llm_bleu(original_path, generate_path, output_file)
