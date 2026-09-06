import os
import json
from collections import defaultdict
from project_paths import project_path
INPUT_FILE = 'data0405.json'
DATA_PATH = project_path("data", INPUT_FILE)

with open(DATA_PATH, 'r', encoding='utf-8') as file:
    data = json.load(file)  # 获取所有数据

pre_knowledge_scale_qt = [[] for x in range(5)]
pre_interest_scale_qt = [[] for x in range(5)]
pre_difficulty_scale_qt = [[] for x in range(5)]
female_qt = []
male_qt = []
field_qt = defaultdict(list)
age_qt = defaultdict(list)

pre_knowledge_scale_ct = [[] for x in range(5)]
pre_interest_scale_ct = [[] for x in range(5)]
pre_difficulty_scale_ct = [[] for x in range(5)]
female_ct = []
male_ct = []
field_ct = defaultdict(list)
age_ct = defaultdict(list)
for user in data:
    for task_id, task in user["task"].items():
        query_times = len(task["content"].keys())
        if user["gender"] == "female":
            female_qt.append(query_times)
        else:
            male_qt.append(query_times)
        if "人工智能" in user["field"]:
            field_qt["人工智能"].append(query_times)
        elif "信息" in user["field"]:
            field_qt["信息学"].append(query_times)
        elif "经济学" in user["field"] or "金融" in user["field"] or "国际贸易" in user["field"] or "商" in user["field"]:
            field_qt["经济/商/金融"].append(query_times)
        elif "统计" in user["field"]:
            field_qt["统计"].append(query_times)
        elif "国" in user["field"] or "明德" in user["field"] or "求是" in user["field"] or "新闻" in user["field"] or "哲" in user["field"] or "中共党史" in user["field"]:
            field_qt["文史哲"].append(query_times)
        else:
            field_qt["其他"].append(query_times)

        age_qt[str(user["age"])].append(query_times)
        pre_knowledge_scale_qt[task["pre_knowledge_scale"]-1].append(query_times)
        pre_interest_scale_qt[task["pre_interest_scale"] - 1].append(query_times)
        pre_difficulty_scale_qt[task["pre_difficulty_scale"] - 1].append(query_times)
        for step_id, step in task["content"].items():
            click_times = 0
            for web in step["SERP"]:
                if web["click_or_not"] == 1:
                    click_times += 1
            pre_knowledge_scale_ct[task["pre_knowledge_scale"] - 1].append(click_times)
            pre_interest_scale_ct[task["pre_interest_scale"] - 1].append(click_times)
            pre_difficulty_scale_ct[task["pre_difficulty_scale"] - 1].append(click_times)
            if user["gender"] == "female":
                female_ct.append(click_times)
            else:
                male_ct.append(click_times)
            if "人工智能" in user["field"]:
                field_ct["人工智能"].append(click_times)
            elif "信息" in user["field"]:
                field_ct["信息学"].append(click_times)
            elif "经济学" in user["field"] or "金融" in user["field"] or "国际贸易" in user["field"] or "商" in user[
                "field"]:
                field_ct["经济/商/金融"].append(click_times)
            elif "统计" in user["field"]:
                field_ct["统计"].append(click_times)
            elif "国" in user["field"] or "明德" in user["field"] or "求是" in user["field"] or "新闻" in user[
                "field"] or "哲" in user["field"] or "中共党史" in user["field"]:
                field_ct["文史哲"].append(click_times)
            else:
                field_ct["其他"].append(click_times)
            age_ct[str(user["age"])].append(click_times)
def show_res(name, ls):
    print(name)
    for i, l in enumerate(ls):
        print(f"{sum(l)/len(l)}")

def show_dict_res(name, ls):
    print(name)
    for id, l in ls.items():
        print(f"{id}\t{sum(l)/len(l)}")

print("一项任务上的平均查询次数")
show_res("\n对任务主题的了解程度", pre_knowledge_scale_qt)
show_res("\n对任务的感兴趣程度", pre_interest_scale_qt)
show_res("\n预计完成任务困难程度", pre_difficulty_scale_qt)
print("\n女", sum(female_qt)/len(female_qt))
print("\n男", sum(male_qt)/len(male_qt))
show_dict_res('\n学院专业', field_qt)
show_dict_res('\n年龄', age_qt)
print("\n\n搜索结果页面上平均网页点击次数")
show_res("\n对任务主题的了解程度", pre_knowledge_scale_ct)
show_res("\n对任务的感兴趣程度", pre_interest_scale_ct)
show_res("\n预计完成任务困难程度", pre_difficulty_scale_ct)
print("\n女", sum(female_ct)/len(female_ct))
print("\n男", sum(male_ct)/len(male_ct))
show_dict_res("\n学院专业", field_ct)
show_dict_res('\n年龄', age_ct)