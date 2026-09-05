# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import openai

import os
import json
from prompt_library_wo_feedback import *

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
openai.api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")

INPUT_FILE = 'data0405.json'

DATA_PATH = os.path.join("data", INPUT_FILE)

class GenerateQuery:
    def __init__(self, prompt_type):
        self.prompt_type = prompt_type
        self.model_type = "gpt-3.5-turbo-0125"
        self.temperature = 1
        self.output_path = os.path.join("data", f"output_data_{prompt_type}.json")
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            self.all_data = json.load(file)

    def get_history(self, user_id, task_id, step_num):

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
            present_step["thought"] = user["task"][task_id]["content"][step_keys[i]]["thought"] if "thought" in user["task"][task_id]["content"][step_keys[i]] else "被是没说。"

            present_step["query"] = user["task"][task_id]["content"][step_keys[i]][
                "query"]

            present_step["clicked_pages"] = [
                {"title": item["title"], "snippet": item["snippet"]}
                for item in user["task"][task_id]["content"][step_keys[i]]["SERP"]
                if item["click_or_not"] == 1
            ]
            present_step["satisfaction_thought"] = user["task"][task_id]["content"][step_keys[i]][
                "satisfaction_thought"] if "satisfaction_thought" in user["task"][task_id]["content"][step_keys[i]] else "被是没说。"

            if "satisfaction" in user["task"][task_id]["content"][step_keys[i]]:
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

    def compose_prompt(self, user_id, task_id, step_num):

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
            if "thought" not in self.prompt_type:
                history += f'<思考{index + 1}> ' + action["thought"] + f' </思考{index + 1}>\n'

            history += f'<查询{index + 1}> ' + action["query"] + f' </查询{index + 1}>\n'
            if "observation" not in self.prompt_type:
                history += f'<观察{index + 1}>\n'
                for action2 in action["clicked_pages"]:
                    clicked_pages_count += 1
                    history += f'\t<文档{clicked_pages_count}>\n'
                    history += f'\t\t<标题> ' + action2["title"] + f' </标题>\n'
                    history += f'\t\t<摘要> ' + action2["snippet"] + f' </摘要>\n'
                    history += f'\t</文档{clicked_pages_count}>\n'
                history+=f'</观察{index + 1}>\n'
            if "feedback" not in self.prompt_type:
                if "satisfaction" in action:
                    history += f'<反馈{index + 1}> ' + action["satisfaction"] + action[
                        "satisfaction_thought"] + f' </反馈{index + 1}>\n'
                else:
                    history += f'<反馈{index + 1}> ' + action["satisfaction_thought"] + f' </反馈{index + 1}>\n'

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

        return output_prompt

    def generate_query(self, user_id, task_id, step_num):

        prompt = self.compose_prompt(user_id, task_id, step_num)

        if self.model_type == "gpt-3.5-turbo-0125":

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            return completion.choices[0].message.content

        if self.model_type == "gpt-3.5-turbo-instruct":
            completion = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=100,
                temperature=self.temperature
            )

            return completion.choices[0].text

    def save_output(self, user_id, task_id, step_num, output):
        for user_num, user in enumerate(self.output_data):
            if user["user_id"] == user_id:
                self.output_data[user_num]["task"][task_id][str(step_num+1)] = output

    def re_simulate(self, steps):

        for sp in steps:
            arg_sp = sp.split(" ")
            user_id = int(arg_sp[0])
            task_id = arg_sp[1]
            step_num = int(arg_sp[2]) - 1

            print("用户：{}, 任务：{}，步数：{}".format(user_id, task_id, step_num + 1))
            output = self.generate_query(user_id, task_id, step_num)
            print(f"输出：{output}")
            self.save_output(user_id, task_id, step_num, output)

        with open(self.output_path, 'w',
                  encoding='utf-8') as file:
            json.dump(self.output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    def main_simulate(self):

        for user_num, user in enumerate(self.all_data):
            for task_id, task in user["task"].items():
                step_count = len(task["content"])
                for step_num in range(step_count):
                    print("用户：{}(序号 {}), 任务：{}，步数：{}".format(user["user_id"], user_num+1, task_id, step_num+1))
                    flag = 0
                    for u in self.output_data:
                        if u.get("user_id") == user["user_id"] and str(step_num+1) in u["task"][task_id]:
                            print("之前已经模拟该步骤，跳过")
                            flag = 1
                    if flag:
                        continue
                    output = self.generate_query(user["user_id"], task_id, step_num)
                    print(f"输出：{output}")
                    self.save_output(user["user_id"], task_id, step_num, output)

                with open(self.output_path, 'w', encoding='utf-8') as file:
                    json.dump(self.output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

        pass
        return

if __name__ == "__main__":

    print("hi")
    generator = GenerateQuery("wo_thought")
    prompt = generator.compose_prompt(30, '7', 2)
    print(prompt+"\n")
