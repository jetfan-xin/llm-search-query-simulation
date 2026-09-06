import os
import json
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from evaluation_jaccard import get_queries_with_tasks
from project_paths import project_path

def evaluation_llm_bleu(original_path, generate_path, output_file):
    # Load the original and generated data from JSON files
    with open(original_path, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    with open(generate_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)

    # Initialize lists to store BLEU scores
    bleu_score_list = []
    bleu_score_list_first = []
    bleu_score_list_others = []

    bleu_score_with_tasks = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
    bleu_score_with_tasks_first = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                   "10": []}
    bleu_score_with_tasks_others = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],
                                    "10": []}

    # Iterate through the dataset to compute BLEU scores for each query
    for user_num, user in enumerate(generate_data):
        # for task_id in generate_data[user_id]:
        for ori_u in original_data:
            if ori_u["user_id"] == user["user_id"]:
                ori_user = ori_u
                break
        for task_id, task in user["task"].items():
            for query_step in list(task.keys()):
                # Calculate BLEU score for each pair of original and generated queries
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

    # 将更新后的数据写回文件
    with open(project_path('evaluation', 'bleu', "bleu_with_tasks" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bleu_score_with_tasks, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(project_path('evaluation', 'bleu', "bleu_with_tasks_first" + output_file), 'w', encoding='utf-8') as file:
        json.dump(bleu_score_with_tasks_first, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    with open(project_path('evaluation', 'bleu', "bleu_with_tasks_others" + output_file), 'w',
              encoding='utf-8') as file:
        json.dump(bleu_score_with_tasks_others, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    # Print the average BLEU score
    if bleu_score_list:
        average_bleu_score = sum(bleu_score_list) / len(bleu_score_list)
        print(f"Average BLEU Score: {average_bleu_score}")
    if bleu_score_list_first:
        average_bleu_score_first = sum(bleu_score_list_first) / len(bleu_score_list_first)
        print(f"Average first BLEU Score: {average_bleu_score_first}")
    if bleu_score_list_others:
        average_bleu_score_others = sum(bleu_score_list_others) / len(bleu_score_list_others)
        print(f"Average other BLEU Score: {average_bleu_score_others}")

    """
    # 示例：动物保护组织 temp=1
    Average BLEU Score: 0.31508412118710044
    Average first BLEU Score: 0.3843254019118801
    Average other BLEU Score: 0.27069249870152706

    # 示例：缓解压力 temp=1
    Average BLEU Score: 0.3707329154085929
    Average first BLEU Score: 0.3852510474351573
    Average other BLEU Score: 0.3607795861232407

    # 示例：缓解压力 temp=0.5
    Average BLEU Score: 0.3660047953857383
    Average first BLEU Score: 0.378367612835039
    Average other BLEU Score: 0.3575291049358635

    # 示例：缓解压力 temp=1.5
    Average BLEU Score: 0.344388561295253
    Average first BLEU Score: 0.362590927893919
    Average other BLEU Score: 0.33195242903280847

    # 无示例 temp=1
    Average BLEU Score: 0.375931334599167
    Average first BLEU Score: 0.38318992647842853
    Average other BLEU Score: 0.37095499501291074

    # 无示例 temp=0.5
    Average BLEU Score: 0.36546517884376795
    Average first BLEU Score: 0.3820082360453521
    Average other BLEU Score: 0.35412360298452605

    # 无示例 无角色 temp=1
    Average BLEU Score: 0.38335928821450066
    Average first BLEU Score: 0.3972118192685362
    Average other BLEU Score: 0.37386228110889735

    # 示例：缓解压力 无角色 temp=1
    Average BLEU Score: 0.36274703949063547
    Average first BLEU Score: 0.3806938320532722
    Average other BLEU Score: 0.35044309187086126

    # 无示例 无角色 无思考 temp=1
    Average BLEU Score: 0.4068154374065456
    Average first BLEU Score: 0.42767390833638874
    Average other BLEU Score: 0.39251530367213716

    # 清洗后：无示例 无角色 temp=1
    Average BLEU Score: 0.37538262534267436
    Average first BLEU Score: 0.39479893315127884
    Average other BLEU Score: 0.3620712086417397

    # 无示例 无角色 无思考 无反馈 temp=1
    Average BLEU Score: 0.38143049997806067
    Average first BLEU Score: 0.41567188699940605
    Average other BLEU Score: 0.35795531738659425

    # 无示例 无角色 无思考输出 temp=1
    Average BLEU Score: 0.4102193928106136
    Average first BLEU Score: 0.41440934934208784
    Average other BLEU Score: 0.40734684577957886

    # 无角色 无思考输出 temp=1
    Average BLEU Score: 0.4173687834306447
    Average first BLEU Score: 0.44019039596824616
    Average other BLEU Score: 0.40172276065072837

    # 无示例 无思考输出 temp=1
    Average BLEU Score: 0.41406393363431443
    Average first BLEU Score: 0.4396319232193288
    Average other BLEU Score: 0.39653505188572186
    
    # 无思考输出 temp=1
    Average BLEU Score: 0.41779838482721937
    Average first BLEU Score: 0.4407855927133155
    Average other BLEU Score: 0.40203883332138507
    
    # 无思考输出 无思考 无反馈 temp=1
    Average BLEU Score: 0.41358829039991063
    Average first BLEU Score: 0.45824332787996286
    Average other BLEU Score: 0.38297372569727484
    
    # 无思考输出 无思考 temp=1
    Average BLEU Score: 0.41550502767587305
    Average first BLEU Score: 0.4555226286807282
    Average other BLEU Score: 0.3880697929444112
    
    # 无思考输出 无反馈 temp=1
    Average BLEU Score: 0.4148817295198305
    Average first BLEU Score: 0.439651507618445
    Average other BLEU Score: 0.3979000849604972
    
    # 无思考输出 无观察 temp=1
    Average BLEU Score: 0.4164133636045874
    Average first BLEU Score: 0.4547671683328629
    Average other BLEU Score: 0.390118792987094
    """


def evaluation_bl_bleu(generate_file):
    generate_path = project_path('baseline','2', 'output', generate_file)
    with open(generate_path, 'r', encoding='utf-8') as file:
        generate_data = json.load(file)

    # 获取每个task下的原始query

    original_path = project_path('data', f'extracted_original_data_all.json')
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
    with open(project_path('evaluation', 'bleu', "baseline2_bleu_with_tasks.json"), 'w', encoding='utf-8') as file:
        json.dump(bleu_with_tasks, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    """
    task 1: Average BLEU Score: 0.10087494101822016
    task 2: Average BLEU Score: 0.122811068947332
    task 3: Average BLEU Score: 0.16370496339563406
    task 4: Average BLEU Score: 0.11106010714412536
    task 5: Average BLEU Score: 0.05541965187432057
    task 6: Average BLEU Score: 0.1482202412328813
    task 7: Average BLEU Score: 0.07781173729460909
    task 8: Average BLEU Score: 0.09723401128542215
    task 9: Average BLEU Score: 0.12509735606035013
    task 10: Average BLEU Score: 0.07854867741976239
    
    ALL: Average BLEU Score: 0.10807827556726572


    # 随机
    task 1: Average BLEU Score: 0.07955982790406929
    task 2: Average BLEU Score: 0.06909428819688078
    task 3: Average BLEU Score: 0.07471653712832049
    task 4: Average BLEU Score: 0.09230868068060051
    task 5: Average BLEU Score: 0.06797348960493192
    task 6: Average BLEU Score: 0.0682423995398762
    task 7: Average BLEU Score: 0.05346847344046152
    task 8: Average BLEU Score: 0.09887866422194513
    task 9: Average BLEU Score: 0.07737019122328008
    task 10: Average BLEU Score: 0.07200131679434756
    
    ALL: Average BLEU Score: 0.07536138687347134
    
    进程已结束,退出代码0

    

    """


if __name__ == '__main__':
    # evaluation_bl_bleu("baseline2_data.json")

    model_type = "wo_guidance_charactor" # all_prompt
    #
    generate_path = project_path('data', f'cleaned_{model_type}.json')
    original_path = project_path('data', f'extracted_original_data_all.json')
    output_file = f'_{model_type}.json'
    evaluation_llm_bleu(original_path, generate_path, output_file)