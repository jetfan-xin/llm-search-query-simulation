# 后续output_data_{INPUT_FILE.strip('.json')}_{self.model_type}.json需要调整到和extracted_thought_query_v1.json相同格式
# import time
import openai
# from openai import OpenAI
import os
import json
from prompt_library_s import *

openai.api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("OPENAI_API_BASE"):
    openai.api_base = os.getenv("OPENAI_API_BASE")
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CODE_DIR, "data")
INPUT_FILE = "user5,9,13,17,21,25,29,2,6,10,14,18,22,26,30.json" # "user3,7,11,15,19,23,27,31.json" #"user4,8,12,16,20,24,28,32.json"
DATA_PATH = os.path.join(DATA_DIR, INPUT_FILE)
INPUT_STEM = os.path.splitext(INPUT_FILE)[0]
# OUTPUT_PATH 根据API输出文件名称不同


class GenerateQuery:
    def __init__(self, model_type):
        self.model_type = model_type
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            self.all_data = json.load(file)  # 获取所有数据
        # 获取输出数据
        try:
            with open(os.path.join(DATA_DIR, f"output_data_{INPUT_STEM}_{self.model_type}.json"), 'r', encoding='utf-8') as file:
                self.output_data = json.load(file)
        except FileNotFoundError:
            # 创建存储架构,包括用户和任务
            self.output_data = []
            for user in self.all_data:
                user_dict = {}
                user_dict["user_id"] = user["user_id"]
                user_dict["task"] = {}
                for task_id in user["task"].keys():
                    user_dict["task"][task_id] = {}
                self.output_data.append(user_dict)

    def get_history(self, user_id, task_id, step_num):  # 获取历史搜索记录
        # user_id: str
        # task_id: all_data中是"1"到“10”
        # step_num：0为没有历史记录
        user = {}
        for item in self.all_data:
            if item["user_id"] == user_id:
                user = item

        output = {}
        output["profile"] = {}
        if user["gender"] == "male":
            output["profile"]["gender"] = "男"
        else:
            output["profile"]["gender"] = "女"

        output["profile"]["age"] = user["age"]
        output["profile"]["field"] = user["field"]

        if user["search_frequency"] == "frequently":
            output["profile"]["search_frequency"] = "一天使用多次"
        else:
            output["profile"]["search_frequency"] = "一天一次"

        if user["search_history"] == "very long":
            output["profile"]["search_history"] = "五年以上"
        elif user["search_history"] == "long":
            output["profile"]["search_history"] = "3-5年"
        else:
            output["profile"]["search_history"] = "1-3年"

        if user["task"][task_id]["pre_knowledge_scale"] == 1:
            output["profile"]["pre_knowledge_scale"] = "完全不了解"
        elif user["task"][task_id]["pre_knowledge_scale"] == 2:
            output["profile"]["pre_knowledge_scale"] = "有些微了解"
        elif user["task"][task_id]["pre_knowledge_scale"] == 3:
            output["profile"]["pre_knowledge_scale"] = "有点了解"
        elif user["task"][task_id]["pre_knowledge_scale"] == 4:
            output["profile"]["pre_knowledge_scale"] = "比较了解"
        else:
            output["profile"]["pre_knowledge_scale"] = "非常了解"

        if user["task"][task_id]["pre_interest_scale"] == 1:
            output["profile"]["pre_interest_scale"] = "完全没兴趣"
        elif user["task"][task_id]["pre_interest_scale"] == 2:
            output["profile"]["pre_interest_scale"] = "有些微兴趣"
        elif user["task"][task_id]["pre_interest_scale"] == 3:
            output["profile"]["pre_interest_scale"] = "有点兴趣"
        elif user["task"][task_id]["pre_interest_scale"] == 4:
            output["profile"]["pre_interest_scale"] = "比较有兴趣"
        else:
            output["profile"]["pre_interest_scale"] = "非常有兴趣"

        if user["task"][task_id]["pre_difficulty_scale"] == 1:
            output["profile"]["pre_difficulty_scale"] = "完全没困难"
        elif user["task"][task_id]["pre_difficulty_scale"] == 2:
            output["profile"]["pre_difficulty_scale"] = "有些微困难"
        elif user["task"][task_id]["pre_difficulty_scale"] == 3:
            output["profile"]["pre_difficulty_scale"] = "有点困难"
        elif user["task"][task_id]["pre_difficulty_scale"] == 4:
            output["profile"]["pre_difficulty_scale"] = "比较有困难"
        else:
            output["profile"]["pre_difficulty_scale"] = "非常有困难"

        step_keys = list(user["task"][task_id]["content"].keys())
        output["history"] = []
        for i in range(step_num):
            present_step = {}
            present_step["thought"] = user["task"][task_id]["content"][step_keys[i]]["thought"] if "thought" in user["task"][task_id]["content"][step_keys[i]] else "被试没说。"
            present_step["query"] = user["task"][task_id]["content"][step_keys[i]][
                "query"]  # "可持续生活的实践与建议 可持续生活的好处",
            # 从给定的JSON数据中提取点击过的所有网页的标题和摘要
            present_step["clicked_pages"] = [
                {"title": item["title"], "snippet": item["snippet"]}
                for item in user["task"][task_id]["content"][step_keys[i]]["SERP"]
                if item["click_or_not"] == 1
            ]
            present_step["satisfaction_thought"] = user["task"][task_id]["content"][step_keys[i]][
                "satisfaction_thought"] if "satisfaction_thought" in user["task"][task_id]["content"][step_keys[i]] else "被试没说。"

            if user["task"][task_id]["content"][step_keys[i]]["satisfaction"] == 1:
                present_step["satisfaction"] = "我完全不满意这次查询。"
            elif user["task"][task_id]["content"][step_keys[i]]["satisfaction"] == 2:
                present_step["satisfaction"] = "我有些微满意这次查询。"
            elif user["task"][task_id]["content"][step_keys[i]]["satisfaction"] == 3:
                present_step["satisfaction"] = "我有点满意这次查询。"
            elif user["task"][task_id]["content"][step_keys[i]]["satisfaction"] == 4:
                present_step["satisfaction"] = "我比较满意这次查询。"
            else:
                present_step["satisfaction"] = "我非常满意这次查询。"

            output["history"].append(present_step)
        return output

    def compose_prompt(self, user_id, task_id, step_num):  # 获取组装好的提示
        # task_id: all_data中是"1"到“10”
        task_background = all_task_background[task_id]
        task_goal = all_task_goal[task_id]
        all_history = self.get_history(user_id, task_id, step_num)
        gender = all_history["profile"]["gender"]
        age = all_history["profile"]["age"]
        field = all_history["profile"]["field"]
        search_frequency = all_history["profile"]["search_frequency"]
        search_history = all_history["profile"]["search_history"]
        pre_knowledge_scale = all_history["profile"]["pre_knowledge_scale"]
        pre_interest_scale = all_history["profile"]["pre_interest_scale"]
        pre_difficulty_scale = all_history["profile"]["pre_difficulty_scale"]
        history = ""
        clicked_pages_count = 0
        for index, action in enumerate(all_history["history"]):
            history += f'<思考{index + 1}> ' + action["thought"] + f' </思考{index + 1}>\n'
            history += f'<查询{index + 1}> ' + action["query"] + f' </查询{index + 1}>\n'
            history += f'<观察{index + 1}>\n'
            for action2 in action["clicked_pages"]:
                clicked_pages_count += 1
                history += f'\t<文档{clicked_pages_count}>\n'
                history += f'\t\t<标题> ' + action2["title"] + f' </标题>\n'
                history += f'\t\t<摘要> ' + action2["snippet"] + f' </摘要>\n'
                history += f'\t</文档{clicked_pages_count}>\n'
            history += f'<反馈{index + 1}> ' + action["satisfaction"] + action["satisfaction_thought"] + f' </反馈{index + 1}>\n'

        if history == "":
            history = '<无历史操作>\n'

        output_prompt = main_prompt.format(
            task_background=task_background,
            task_goal=task_goal,
            gender=gender,
            age=age,
            field=field,
            search_frequency=search_frequency,
            search_history=search_history,
            pre_knowledge_scale=pre_knowledge_scale,
            pre_interest_scale=pre_interest_scale,
            pre_difficulty_scale=pre_difficulty_scale,
            history=history,
            guidance=guidance,
            step=step_num + 1
        )
        # print(f"提示：{output_prompt}")
        return output_prompt

    def generate_query(self, user_id, task_id, step_num):
        # client = OpenAI(api_key=api_key, base_url=api_base)
        # client = OpenAI(api_key=api_key)
        prompt = self.compose_prompt(user_id, task_id, step_num)

        if self.model_type == "gpt-3.5-turbo-0125":
            # completion = client.chat.completions.create(
            #     model="gpt-3.5-turbo-0125",
            #     messages=[
            #         {"role": "system", "content": "You are a helpful assistant."},
            #         {"role": "user", "content": prompt}
            #     ]
            # )
            # return completion.choices[0].message.content
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content

        if self.model_type == "gpt-3.5-turbo-instruct":
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=150,
                temperature=0
            )
            return completion.choices[0].text

    def save_output(self, user_id, task_id, step_num, output):
        for user_num, user in enumerate(self.output_data):
            if user["user_id"] == user_id:
                self.output_data[user_num]["task"][task_id][str(step_num+1)] = output  # 直接将字符串存入，后续自行更改格式

    def re_simulate(self, steps):
        # 补充生成错误查询
        for sp in steps:
            arg_sp = sp.split(" ")
            user_id = int(arg_sp[0])
            task_id = arg_sp[1]
            step_num = int(arg_sp[2]) - 1

            print("用户：{}, 任务：{}，步数：{}".format(user_id, task_id, step_num + 1))
            output = self.generate_query(user_id, task_id, step_num)
            print(f"输出：{output}")
            self.save_output(user_id, task_id, step_num, output)
            # time.sleep(18)
        # 将更新后的数据写回文件
        with open(os.path.join(DATA_DIR, f"output_data_{INPUT_STEM}_{self.model_type}.json"), 'w',
                  encoding='utf-8') as file:
            json.dump(self.output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    def main_simulate(self):  # 重新写循环，首先检查目前有的数据是否有缺漏（在当前代码基础上加上缺漏打印），检查出来后修改代码为有啥生成啥版。
        # 生成查询
        for user_num, user in enumerate(self.all_data):
            for task_id, task in user["task"].items():
                step_count = len(task["content"])
                for step_num in range(step_count):
                    print("用户：{}(序号 {}), 任务：{}，步数：{}".format(user["user_id"], user_num+1, task_id, step_num+1))
                    flag = 0
                    for u in self.output_data:
                        if u.get("user_id") == user["user_id"] and str(step_num+1) in u["task"][task_id]:  # 之前已经生成该步骤，跳过
                            print("之前已经模拟该步骤，跳过")
                            flag = 1
                    if flag:
                        continue
                    output = self.generate_query(user["user_id"], task_id, step_num)
                    print(f"输出：{output}")
                    self.save_output(user["user_id"], task_id, step_num, output)
                    # time.sleep(18)
                # 将更新后的数据写回文件
                with open(os.path.join(DATA_DIR, f"output_data_{INPUT_STEM}_{self.model_type}.json"), 'w', encoding='utf-8') as file:
                    json.dump(self.output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

        # user_num = 1
        # task_id = "1"
        # step_num = 3
        # # output = self.get_history(user_num, task_id, step_num)
        # # print("获取到的历史为：\n", output)
        # # output = self.compose_prompt(user_num, task_id, step_num)
        # # print(f"获取到的提示为：{output}")
        # output = self.generate_query(user_num, task_id, step_num)
        # print(f"输出：{output}")
        # self.save_output(user_num, task_id, step_num, output)

        """
        输出：
            [
                {
                    "步骤": 1,
                    "类型": "思考",
                    "内容": "我对可持续生活方式感兴趣，想了解一些实践和建议。通过搜索需找到可持续生活方式的实践方法和对环境的积极影响。"
                },
                {
                    "步骤": 1,
                    "类型": "查询",
                    "内容": "可持续生活方式的实践和建议"
                }
            ]            
        """
        return


if __name__ == "__main__":
    # generator = GenerateQuery("gpt-3.5-turbo-instruct")
    generator = GenerateQuery("gpt-3.5-turbo-0125")
    generator.main_simulate()

    # 重新生成查询
    # regenerate_path = os.path.join("data", "regenerated.json")
    # with open(regenerate_path, 'r', encoding='utf-8') as file:
    #     regenerate_steps = json.load(file)  # 获取所有数据
    # generator.re_simulate(regenerate_steps)
