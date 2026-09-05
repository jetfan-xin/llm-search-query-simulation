# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import json
import os

data_path = os.path.join('data', "data0405.json")

def check_completion():
    with open(data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    query_thought_num = 0
    query_sat_thought_num = 0
    checked_page_num = 0
    for user in data:

        for task_i in [str(i) for i in range(1, 11)]:
            if task_i not in user["task"]:

                pass
            else:
                for query_step, content_id in enumerate(list(user["task"][task_i]["content"].keys())):
                    if "thought" not in user["task"][task_i]["content"][content_id]:

                        pass
                    else:

                        if "被试没说" not in user["task"][task_i]["content"][content_id]["thought"] and user["task"][task_i]["content"][content_id]["thought"] !="":
                            query_thought_num +=1
                    if "satisfaction_thought" not in user["task"][task_i]["content"][content_id]:

                        pass
                    else:

                        if "被试没说" not in user["task"][task_i]["content"][content_id]["satisfaction_thought"] and user["task"][task_i]["content"][content_id]["satisfaction_thought"] !="":
                            query_sat_thought_num +=1
                    for rank, link in enumerate(user["task"][task_i]["content"][content_id]["SERP"]):
                        if link["click_or_not"] == 1:
                            checked_page_num+=1

    print(query_thought_num, query_sat_thought_num, checked_page_num)
if __name__ == "__main__":
    check_completion()
