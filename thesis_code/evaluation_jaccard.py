import os
import json
import jieba
import re
from project_paths import project_path

def get_queries_with_tasks(path): # extracted_original_data_all.json]
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 获取每个task下的原始query
    queries = {}
    for user in data:
        for task_id, task_content in user["task"].items():
            queries.setdefault(task_id, [])
            for query_content in task_content.values():
                query = query_content['query']
                queries[task_id].append(query)
    return queries

class Jaccard_Evaluation:
    '''
    We begin to answer our second research question by exploring the similarity at the term-level.
    To accomplish this, we ￿rst want to determine how many queries were exactly duplicated
    in the human versus automatic query sets. On average, 2.7 queries match in CW12B and 0.2 in ROBUST,
    with at most 8 and 2 matches for any one topic respectively in the two collections.
    '''

    # plots the Jaccard similarity between each query and its associated backstory.
    # shows the Jaccard similarity between all pairs of query variations for each topic.

    # Query Jaccard Similarity: within a query set (Intra), between the query sets (Inter) and with TREC’s topic Title.
    # measure the Jaccard similarity between the automatic and human generated queries.

    # 1. 原始查询
    # 1.1 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    # 1.2 查询集合&背景，计算整体均值，收集所有jaccard similarity数据点
    # 1.3 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图

    # 2. llm模拟查询
    # 2.1 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    # 2.2 查询集合&背景，计算整体均值，收集所有jaccard similarity数据点
    # 2.3 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图

    # 3. 基线模拟查询
    # 3.1 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    # 3.2 查询集合&背景，计算整体均值，收集所有jaccard similarity数据点
    # 3.3 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图

    # 4. 原始查询&模拟查询
    #   4.1 对于llm模拟查询，计算每个（原始查询，模拟查询）对的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    #   4.2 对于llm模拟查询，计算每个任务 每个模拟查询 & 每个原始查询 之间的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    #   4.3 对于llm模拟查询，计算每个任务 原始查询集合 & 模拟查询集合 之间的jaccard similarity，计算整体均值
    #   4.4 对于基线模拟查询，计算每个任务 每个模拟查询 & 每个原始查询 之间的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
    #   4.5 对于基线模拟查询，计算每个任务 原始查询集合 & 模拟查询集合 之间的jaccard similarity，计算整体均值

    def __init__(self):
        stopwords_file = project_path('baseline', 'stopwords.txt')
        task_description_path = project_path("baseline", '1', "corpus", "task_description.json")

        with open(task_description_path, 'r', encoding='utf-8') as file:
            self.task_description = json.load(file)

        self.pattern = re.compile(r'[\u4e00-\u9fff]')

        self.stopwords = []
        with open(stopwords_file, 'r', encoding='utf-8') as file:
            for line in file:
                self.stopwords.append(line.strip())

        original_path = project_path('data', f'extracted_original_data_data0405.json')
        self.original_queries = get_queries_with_tasks(original_path)

        with open(original_path, 'r', encoding='utf-8') as file:
            self.original_queries_with_steps = json.load(file)

    def jaccard_similarity(self, set1, set2):
        """计算两个集合的 Jaccard 相似度"""
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0

    def query2terms(self, query):
        return set([t for t in jieba.cut(query) if t not in self.stopwords and re.search(self.pattern, t)])

    def evaluation_description_jaccard(self, queries):
        """
        1. 查询集合&背景，计算所有主题 & 整体的jaccard similarity
        2. 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        3. 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图

        :param queries: 字典，key:task_id, value:查询list，可能是原始查询、llm模拟查询或基线模拟查询
        """
        jcd_qset2desc = {}
        jcd_q2desc = {}
        jcd_q2desc["average"] = {}
        jcd_intra = {}
        jcd_intra["average"] = {}

        temp1 = [] # 收集每个主题的jcd
        temp2 = []
        temp3 = []
        for task_id, task_queries in queries.items():
            # 查询集合&背景，计算所有主题 & 整体的jaccard similarity
            description_set = set(self.task_description[task_id])
            task_terms = []
            for query in task_queries:
                task_terms.extend(self.query2terms(query))
            query_set = set(task_terms)
            jcd_value = self.jaccard_similarity(query_set, description_set)
            jcd_qset2desc[task_id] = jcd_value
            temp1.append(jcd_value)

            # 每个查询&背景，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
            jcd_q2desc[task_id] = []
            for query in task_queries:
                jcd_value = self.jaccard_similarity(self.query2terms(query), description_set)
                jcd_q2desc[task_id].append(jcd_value)

            jcd_q2desc["average"][task_id] = sum(jcd_q2desc[task_id]) / len(jcd_q2desc[task_id])
            temp2.append(jcd_q2desc["average"][task_id])

            # 每个任务内所有可能的查询pair，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
            jcd_intra[task_id] = []
            for i, query1 in enumerate(task_queries):
                for j, query2 in enumerate(task_queries):
                    if i < j:  # To avoid repeating comparisons
                        query1_tokens = self.query2terms(query1)
                        query2_tokens = self.query2terms(query2)
                        jcd_value = self.jaccard_similarity(query1_tokens, query2_tokens)
                        jcd_intra[task_id].append(jcd_value)

            jcd_intra["average"][task_id] = sum(jcd_intra[task_id]) / len(jcd_intra[task_id])
            temp3.append(jcd_intra["average"][task_id])

        jcd_qset2desc["0"] = sum(temp1) / len(temp1)  # 保存jcd均值，task_id为0
        jcd_q2desc["average"]["0"] = sum(temp2) / len(temp2)  # 保存jcd均值，task_id为0
        jcd_intra["average"]["0"] = sum(temp3) / len(temp3)  # 保存jcd均值，task_id为0
        return jcd_qset2desc, jcd_q2desc, jcd_intra

    def evaluation_inter_llm_jaccard(self, queries):
        """
        原始查询 & llm模拟查询
        :param queries: 格式：
                        [
                            {
                                "user_id": 21,
                                "task": {
                                    "1": {
                                        "1": {
                                            "thought": "我需要搜索可持续生活方式的实践和建议，因此我可以思考一些可持续生活方式的方面，例如食物、交通和能源消耗等。我可以使用“可持续生活方式”、“生态文明”等词语来搜索相关信息。",
                                            "query": "可持续生活方式"
                                        }
        """
        #   4.1 对于llm模拟查询，计算每个（原始查询，模拟查询）对的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        #   4.2 对于llm模拟查询，计算每个任务 每个模拟查询 & 每个原始查询 之间的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        #   4.3 对于llm模拟查询，计算每个任务 原始查询集合 & 模拟查询集合 之间的jaccard similarity，计算整体均值
        jcd_inter_pair = {}
        jcd_inter_pair["average"] = {}

        jcd_inter_query = {}
        jcd_inter_query["average"] = {}

        jcd_inter_set = {}
        jcd_inter_set["average"] = {}

        gen_queries_with_tasks = {}  # "task_id" : [q1, q2, ...]

        # 1. 对于llm模拟查询，计算每个（原始查询，模拟查询）对的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        for user in queries:
            user_id = user["user_id"]
            ori_user = {}
            for ori_u in self.original_queries_with_steps:
                if ori_u["user_id"] == user_id:
                    ori_user = ori_u
                    break
            for task_id, task in user["task"].items():
                if task_id not in jcd_inter_pair:
                    jcd_inter_pair[task_id] = []

                if task_id not in gen_queries_with_tasks:
                    gen_queries_with_tasks[task_id] = []

                for step_id, step_content in task.items():
                    generated_query = step_content["query"]
                    gen_queries_with_tasks[task_id].append(generated_query)
                    original_query = self.query2terms(ori_user["task"][task_id][step_id]["query"])
                    jcd_value = self.jaccard_similarity(self.query2terms(generated_query), original_query)
                    jcd_inter_pair[task_id].append(jcd_value)

        temp = []
        for task_id in range(1, 11):
            jcd_inter_pair["average"][str(task_id)] = sum(jcd_inter_pair[str(task_id)]) / len(jcd_inter_pair[str(task_id)])
            temp.append(jcd_inter_pair["average"][str(task_id)])
        jcd_inter_pair["average"]["0"] = sum(temp) / len(temp)  # 保存jcd均值，task_id为0

        # 2. 对于llm模拟查询，计算每个任务 每个模拟查询 & 每个原始查询 之间的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        temp2 = []
        for task_id in range(1, 11):
            jcd_inter_query[str(task_id)] = []
            for generated_query in gen_queries_with_tasks[str(task_id)]:
                for original_query in self.original_queries[str(task_id)]:
                    generated_tokens = self.query2terms(generated_query)
                    original_tokens = self.query2terms(original_query)
                    jcd_value = self.jaccard_similarity(generated_tokens, original_tokens)
                    jcd_inter_query[str(task_id)].append(jcd_value)

            jcd_inter_query["average"][str(task_id)] = sum(jcd_inter_query[str(task_id)]) / len(jcd_inter_query[str(task_id)])
            temp2.append(jcd_inter_query["average"][str(task_id)])
        jcd_inter_query["average"]["0"] = sum(temp2) / len(temp2)  # 保存jcd均值，task_id为0
        # print(jcd_inter_query["average"]["0"])

        # 3. 对于llm模拟查询，计算每个任务 原始查询集合 & 模拟查询集合 之间的jaccard similarity，计算整体均值
        temp3 = []
        for task_id in range(1, 11):
            list1 = []
            for q in self.original_queries[str(task_id)]:
                list1.extend(list(self.query2terms(q)))

            set1 = set(list1)

            list2 = []
            for q in gen_queries_with_tasks[str(task_id)]:
                list2.extend(list(self.query2terms(q)))
            set2 = set(list2)

            jcd_value = self.jaccard_similarity(set1, set2)
            jcd_inter_set[str(task_id)] = jcd_value
            temp3.append(jcd_value)
        jcd_inter_set["0"] = sum(temp3) / len(temp3)

        return jcd_inter_pair, jcd_inter_query, jcd_inter_set

    def evaluation_inter_bl_jaccard(self, queries):
        """
        原始查询 & baseline模拟查询
        :param queries: 格式："task_id" : [q1, q2, ...]
        # 对于基线模拟查询，计算每个任务 每个模拟查询 & 每个原始查询 之间的jaccard similarity，计算任务均值和整体均值，收集所有jaccard similarity数据点，用于绘制每个任务的箱线图和整体箱线图
        # 对于基线模拟查询，计算每个任务 原始查询集合 & 模拟查询集合 之间的jaccard similarity，计算整体均值
        """

        jcd_inter_query = {}
        jcd_inter_query["average"] = {}

        jcd_inter_set = {}
        jcd_inter_set["average"] = {}

        temp2 = []
        for task_id in range(1, 11):
            jcd_inter_query[str(task_id)] = []
            # 两个不同集合之间要计算完整笛卡尔积；原版沿用了集合内部去重
            # 的 ``i < j`` 条件，漏掉了大部分跨集合配对。
            for original_query in self.original_queries[str(task_id)]:
                for generated_query in queries[str(task_id)]:
                    original_tokens = self.query2terms(original_query)
                    generated_tokens = self.query2terms(generated_query)
                    jcd_value = self.jaccard_similarity(original_tokens, generated_tokens)
                    jcd_inter_query[str(task_id)].append(jcd_value)

            jcd_inter_query["average"][str(task_id)] = sum(jcd_inter_query[str(task_id)]) / len(jcd_inter_query[str(task_id)])
            temp2.append(jcd_inter_query["average"][str(task_id)])
        jcd_inter_query["average"]["0"] = sum(temp2) / len(temp2)  # 保存jcd均值，task_id为0
        # print(jcd_inter_query["average"]["0"])
        # 3. 对于llm模拟查询，计算每个任务 原始查询集合 & 模拟查询集合 之间的jaccard similarity，计算整体均值
        temp3 = []
        for task_id in range(1, 11):
            list1 = []
            for q in self.original_queries[str(task_id)]:
                list1.extend(list(self.query2terms(q)))

            set1 = set(list1)

            list2 = []
            for q in queries[str(task_id)]:
                list2.extend(list(self.query2terms(q)))
            set2 = set(list2)

            jcd_value = self.jaccard_similarity(set1, set2)
            jcd_inter_set[str(task_id)] = jcd_value
            temp3.append(jcd_value)
        jcd_inter_set["0"] = sum(temp3) / len(temp3)

        return jcd_inter_query, jcd_inter_set

if __name__ == '__main__':
    prompt_type = "wo_charactor" # all_prompt

    jcd = Jaccard_Evaluation()
    # # # 获取llm模拟查询
    # llm_data_path = project_path('data', f'cleaned_{prompt_type}.json')

    # # 任务4.
    # with open(llm_data_path, 'r', encoding='utf-8') as file:
    #     llm_data = json.load(file)
    # llm_jcd_inter_pair, llm_jcd_inter_query, llm_jcd_inter_set = jcd.evaluation_inter_llm_jaccard(llm_data)
    #
    # llm_jcd_inter_pair_path = project_path('evaluation', 'jaccard', f'llm_jcd_inter_pair_{prompt_type}.json')
    # llm_jcd_inter_query_path = project_path('evaluation', 'jaccard', f'llm_jcd_inter_query_{prompt_type}.json')
    # llm_jcd_inter_set_path = project_path('evaluation', 'jaccard', f'llm_jcd_inter_set_{prompt_type}.json')
    #
    # with open(llm_jcd_inter_pair_path, 'w', encoding='utf-8') as file:
    #     json.dump(llm_jcd_inter_pair, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    # with open(llm_jcd_inter_query_path, 'w', encoding='utf-8') as file:
    #     json.dump(llm_jcd_inter_query, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    # with open(llm_jcd_inter_set_path, 'w', encoding='utf-8') as file:
    #     json.dump(llm_jcd_inter_set, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    #

    # # 任务1.2.3.
    # llm_jcd_qset2desc, llm_jcd_q2desc, llm_jcd_intra = jcd.evaluation_description_jaccard(get_queries_with_tasks(llm_data_path))
    #
    # llm_jcd_qset2desc_path = project_path('evaluation', 'jaccard', f'llm_jcd_qset2desc_{prompt_type}.json')
    # llm_jcd_q2desc_path = project_path('evaluation', 'jaccard', f'llm_jcd_q2desc_{prompt_type}.json')
    # llm_jcd_intra_path = project_path('evaluation', 'jaccard', f'llm_jcd_intra_{prompt_type}.json')
    #
    # with open(llm_jcd_qset2desc_path, 'w', encoding='utf-8') as file:
    #     json.dump(llm_jcd_qset2desc, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    # with open(llm_jcd_q2desc_path, 'w', encoding='utf-8') as file:
    #     json.dump(llm_jcd_q2desc, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    # with open(llm_jcd_intra_path, 'w', encoding='utf-8') as file:
    #     json.dump(llm_jcd_intra, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    #
    #
    # # 获取基线模拟查询
    # baseline_data_path = project_path('baseline', '2', 'output', 'baseline2_data.json')
    # with open(baseline_data_path, 'r', encoding='utf-8') as file:
    #     baseline_data = json.load(file)
    #
    # baseline_queries = []
    # for i in range(10):
    #     baseline_queries.append({})
    #     for task_id, task in baseline_data.items():
    #         baseline_queries[i][task_id] = task[i]
    #
    #     # 任务4.
    #     bl_jcd_inter_query, bl_jcd_inter_set = jcd.evaluation_inter_bl_jaccard(baseline_queries[i])
    #     bl_jcd_inter_query_path = project_path('evaluation', 'jaccard', f'bl2_jcd_inter_query_{i}.json')
    #     bl_jcd_inter_set_path = project_path('evaluation', 'jaccard', f'bl2_jcd_inter_set_{i}.json')
    #     with open(bl_jcd_inter_query_path, 'w', encoding='utf-8') as file:
    #         json.dump(bl_jcd_inter_query, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    #     with open(bl_jcd_inter_set_path, 'w', encoding='utf-8') as file:
    #         json.dump(bl_jcd_inter_set, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    #
    #     # 任务1.2.3.
    #     bl_jcd_qset2desc, bl_jcd_q2desc, bl_jcd_intra = jcd.evaluation_description_jaccard(baseline_queries[i])
    #
    #     bl_jcd_qset2desc_path = project_path('evaluation', 'jaccard', f'bl2_jcd_qset2desc_{i}.json')
    #     bl_jcd_q2desc_path = project_path('evaluation', 'jaccard', f'bl2_jcd_q2desc_{i}.json')
    #     bl_jcd_intra_path = project_path('evaluation', 'jaccard', f'bl2_jcd_intra_{i}.json')
    #
    #     with open(bl_jcd_qset2desc_path, 'w', encoding='utf-8') as file:
    #         json.dump(bl_jcd_qset2desc, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    #     with open(bl_jcd_q2desc_path, 'w', encoding='utf-8') as file:
    #         json.dump(bl_jcd_q2desc, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    #     with open(bl_jcd_intra_path, 'w', encoding='utf-8') as file:
    #         json.dump(bl_jcd_intra, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
    #
    #
