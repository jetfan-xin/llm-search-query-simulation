# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import os
import json
import jieba
import re

def get_queries_with_tasks(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    queries = {}
    for user in data:
        for task_id, task_content in user["task"].items():
            queries.setdefault(task_id, [])
            for query_content in task_content.values():
                query = query_content['query']
                queries[task_id].append(query)
    return queries

class Jaccard_Evaluation:
    pass

    def __init__(self):
        stopwords_file = os.path.join('baseline', 'stopwords.txt')
        task_description_path = os.path.join("baseline", '1', "corpus", "task_description.json")

        with open(task_description_path, 'r', encoding='utf-8') as file:
            self.task_description = json.load(file)

        self.pattern = re.compile(r'[\u4e00-\u9fff]')

        self.stopwords = []
        with open(stopwords_file, 'r', encoding='utf-8') as file:
            for line in file:
                self.stopwords.append(line.strip())

        original_path = os.path.join('data', f'extracted_original_data_data0405.json')
        self.original_queries = get_queries_with_tasks(original_path)

        with open(original_path, 'r', encoding='utf-8') as file:
            self.original_queries_with_steps = json.load(file)

    def jaccard_similarity(self, set1, set2):
        pass
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0

    def query2terms(self, query):
        return set([t for t in jieba.cut(query) if t not in self.stopwords and re.search(self.pattern, t)])

    def evaluation_description_jaccard(self, queries):
        pass
        jcd_qset2desc = {}
        jcd_q2desc = {}
        jcd_q2desc["average"] = {}
        jcd_intra = {}
        jcd_intra["average"] = {}

        temp1 = []
        temp2 = []
        temp3 = []
        for task_id, task_queries in queries.items():

            description_set = set(self.task_description[task_id])
            task_terms = []
            for query in task_queries:
                task_terms.extend(self.query2terms(query))
            query_set = set(task_terms)
            jcd_value = self.jaccard_similarity(query_set, description_set)
            jcd_qset2desc[task_id] = jcd_value
            temp1.append(jcd_value)

            jcd_q2desc[task_id] = []
            for query in task_queries:
                jcd_value = self.jaccard_similarity(self.query2terms(query), description_set)
                jcd_q2desc[task_id].append(jcd_value)

            jcd_q2desc["average"][task_id] = sum(jcd_q2desc[task_id]) / len(jcd_q2desc[task_id])
            temp2.append(jcd_q2desc["average"][task_id])

            jcd_intra[task_id] = []
            for i, query1 in enumerate(task_queries):
                for j, query2 in enumerate(task_queries):
                    if i < j:
                        query1_tokens = self.query2terms(query1)
                        query2_tokens = self.query2terms(query2)
                        jcd_value = self.jaccard_similarity(query1_tokens, query2_tokens)
                        jcd_intra[task_id].append(jcd_value)

            jcd_intra["average"][task_id] = sum(jcd_intra[task_id]) / len(jcd_intra[task_id])
            temp3.append(jcd_intra["average"][task_id])

        jcd_qset2desc["0"] = sum(temp1) / len(temp1)
        jcd_q2desc["average"]["0"] = sum(temp2) / len(temp2)
        jcd_intra["average"]["0"] = sum(temp3) / len(temp3)
        return jcd_qset2desc, jcd_q2desc, jcd_intra

    def evaluation_inter_llm_jaccard(self, queries):
        pass

        jcd_inter_pair = {}
        jcd_inter_pair["average"] = {}

        jcd_inter_query = {}
        jcd_inter_query["average"] = {}

        jcd_inter_set = {}
        jcd_inter_set["average"] = {}

        gen_queries_with_tasks = {}

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
        jcd_inter_pair["average"]["0"] = sum(temp) / len(temp)

        temp2 = []
        for task_id in range(1, 11):
            jcd_inter_query[str(task_id)] = []
            for i, query1 in enumerate(gen_queries_with_tasks[str(task_id)]):
                for j, query2 in enumerate(gen_queries_with_tasks[str(task_id)]):
                    if i < j:
                        query1_tokens = self.query2terms(query1)
                        query2_tokens = self.query2terms(query2)
                        jcd_value = self.jaccard_similarity(query1_tokens, query2_tokens)
                        jcd_inter_query[str(task_id)].append(jcd_value)

            jcd_inter_query["average"][str(task_id)] = sum(jcd_inter_query[str(task_id)]) / len(jcd_inter_query[str(task_id)])
            temp2.append(jcd_inter_query["average"][str(task_id)])
        jcd_inter_query["average"]["0"] = sum(temp2) / len(temp2)

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
        pass

        jcd_inter_query = {}
        jcd_inter_query["average"] = {}

        jcd_inter_set = {}
        jcd_inter_set["average"] = {}

        temp2 = []
        for task_id in range(1, 11):
            jcd_inter_query[str(task_id)] = []
            for i, query1 in enumerate(self.original_queries[str(task_id)]):
                for j, query2 in enumerate(queries[str(task_id)]):
                    if i < j:
                        query1_tokens = self.query2terms(query1)
                        query2_tokens = self.query2terms(query2)
                        jcd_value = self.jaccard_similarity(query1_tokens, query2_tokens)
                        jcd_inter_query[str(task_id)].append(jcd_value)

            jcd_inter_query["average"][str(task_id)] = sum(jcd_inter_query[str(task_id)]) / len(jcd_inter_query[str(task_id)])
            temp2.append(jcd_inter_query["average"][str(task_id)])
        jcd_inter_query["average"]["0"] = sum(temp2) / len(temp2)

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
    prompt_type = "wo_charactor"

    jcd = Jaccard_Evaluation()
