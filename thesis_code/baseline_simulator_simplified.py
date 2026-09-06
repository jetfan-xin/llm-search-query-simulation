import os
import json
import jieba
from scipy.stats import poisson
import random
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import csv
import glob
import pandas as pd
from project_paths import project_path

SIMULATE_ROUNDS = 10  # 对于每个查询生成的模拟查询次数比例


class QuerySimulatorOptimized:
    def __init__(self, len_strategy, term_strategy):
        self.len_strategy = len_strategy
        self.term_strategy = term_strategy
        self.data = self.load_initial_data()
        self.queries, self.queries_with_users = self.process_queries()
        self.token_length, self.term_length = self.calculate_statistics()
        self.corpus = self.load_corpus()
        self.query_len_statistics = self.calculate_query_len_statistics()

    def load_initial_data(self):
        with open(project_path('data', 'data_update0302.json'), 'r', encoding='utf-8') as file:
            return json.load(file)

    def process_queries(self):
        queries = {}
        queries_with_users = {}
        for user in self.data:
            user_id = str(user["user_id"])
            queries_with_users.setdefault(user_id, {})
            for task_id, task_content in user["task"].items():
                queries.setdefault(task_id, [])
                queries_with_users[user_id].setdefault(task_id, [])
                for query_content in task_content["content"].values():
                    query = query_content['query']
                    queries[task_id].append(query)
                    queries_with_users[user_id][task_id].append(query)
        return queries, queries_with_users

    def calculate_statistics(self):
        token_length = {}
        term_length = {}
        unique_queries = set(query for queries in self.queries.values() for query in queries)
        cut_queries = {query: list(jieba.cut(query)) for query in unique_queries}
        for task_id, queries in self.queries.items():
            token_length[task_id] = [len(query.replace(" ", "")) for query in queries]
            term_length[task_id] = [len(cut_queries[query]) for query in queries]
        return token_length, term_length

    def load_corpus(self):
        corpus = {}
        for corpus_name in ['task_description', 'title', 'abstract', 'content']:
            with open(project_path('baseline', '2', 'corpus', f'{corpus_name}.json'), 'r', encoding='utf-8') as f:
                corpus[corpus_name] = json.load(f)

        if self.term_strategy == 'random':
            for corpus_name in ['task_description', 'title', 'abstract', 'content']:
                for task_id in corpus[corpus_name]:
                    corpus[corpus_name][task_id] = list(set(corpus[corpus_name][task_id]))

        return corpus

    def calculate_query_len_statistics(self):
        statistics = {}
        for task_id in self.token_length:
            statistics[task_id] = {
                'token_length': round(sum(self.token_length[task_id]) / len(self.token_length[task_id]), 2),
                'term_length': round(sum(self.term_length[task_id]) / len(self.term_length[task_id]), 2)
            }
        return statistics

    def simulate(self, num, task_id, alpha, beta, gamma, delta):
        # 根据给定的alpha, beta, gamma, delta比例合并不同的语料库
        corpus = self.corpus['task_description'][task_id] * alpha + \
                 self.corpus['title'][task_id] * beta + \
                 self.corpus['abstract'][task_id] * gamma + \
                 self.corpus['content'][task_id] * delta
        term_len = len(corpus)
        if term_len == 0:
            raise ValueError("语料为空；请检查语料文件和 alpha/beta/gamma/delta 配置")

        query_simulated = []

        lambd = self.query_len_statistics[task_id][self.len_strategy]
        random_query_length = [l + 1 for l in poisson.rvs(lambd - 1, size=num)]

        if self.len_strategy == 'term_length':
            for q_length in random_query_length:
                query = ' '.join(random.sample(corpus, min(q_length, term_len)))
                query_simulated.append(query)
            return query_simulated

        if self.len_strategy == 'token_length':
            for q_length in random_query_length:
                surplus_length = q_length
                query = []
                while surplus_length > 0:
                    new_term = random.choice(corpus)
                    try_times = 10
                    while new_term in query or len(new_term) > surplus_length:
                        new_term = random.choice(corpus)
                        try_times -= 1
                        if try_times <= 0:
                            break
                    if len(new_term) > surplus_length:
                        break
                    query.append(new_term)
                    surplus_length -= len(new_term)

                query = ' '.join(query)
                query_simulated.append(query)
            return query_simulated

    def _evaluation_bleu(self, generated, original):
        smoothie = SmoothingFunction().method1
        return sentence_bleu([original], generated, weights=(0.5, 0.5, 0, 0), smoothing_function=smoothie)

    def evaluation_bleu_with_tasks(self):  # 按任务保存. SIMULATE_ROUNDS = 10
        # evaluation_all = [['task_id', 'alpha', 'beta', 'gamma', 'delta', 'bleu']]

        for task_id in self.queries:
            evaluation_all = [['task_id', 'alpha', 'beta', 'gamma', 'delta', 'bleu']]
            queries = self.queries[task_id]
            num = len(queries)
            evaluation = []

            max_bleu = 0.0

            for delta in [i for i in range(0, 5, 5)]:
                for alpha in [i for i in range(0, 105 - delta, 5)]:
                    for beta in [i for i in range(0, 105 - alpha - delta, 5)]:
                        gamma = 100 - alpha - beta - delta
                        # print(f"{alpha}\t{beta}\t{gamma}\t{delta}")
                        bleu_scores = []
                        for i in range(SIMULATE_ROUNDS):
                            query_simulated = self.simulate(num, task_id, alpha, beta, gamma, delta)
                            bleu_scores.extend([self._evaluation_bleu(generated, original)
                                                for generated, original in zip(query_simulated, queries)])

                        average_bleu = round(sum(bleu_scores) / len(bleu_scores), 4)

                        if average_bleu > max_bleu:
                            max_bleu = average_bleu

                        if average_bleu >= max_bleu * 0.9:
                            evaluation.append(
                                [task_id, alpha / 100, beta / 100, gamma / 100, delta / 100, average_bleu])
                            print(
                                f"{task_id}\t{alpha / 100}\t{beta / 100}\t{gamma / 100}\t{delta / 100}\t{average_bleu}")

            # print("bbbb")
            # Sort evaluations for each task by BLEU score in descending order and take top 10
            evaluation.sort(key=lambda x: x[5], reverse=True)
            evaluation_all.extend(evaluation[:10])
            # print("aaaa")

            # Save evaluation to CSV
            filename = project_path('baseline', '2', 'output', f'output_task_{self.len_strategy}_{task_id}.csv')
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(evaluation_all)

    # 按照user分类, 同时query_len遵循task分布
    def evaluation_bleu_with_users(self):

        # evaluation_all = [['user_id', 'alpha', 'beta', 'gamma', 'delta', 'bleu']]
        # evaluation_best = [0.0969, 0.0961, 0.098, 0.0973, 0.0948, 0.0957, 0.0959, 0.0966, 0.0959, 0.0982, 0.1038, 0.0961] # 20-31
        evaluation_best = []
        for user_id, user_queries in self.queries_with_users.items():
            # if int(user_id) >= 32: # 中断再继续
            evaluation_all = [['user_id', 'alpha', 'beta', 'gamma', 'delta', 'bleu']]
            max_bleu = 0.0
            print(user_id)

            for delta in [i for i in range(0, 5, 5)]:
            # for delta in [i for i in range(0, 15, 5)]:
                for alpha in [i for i in range(0, 105 - delta, 5)]:
                    for beta in [i for i in range(0, 105 - alpha - delta, 5)]:
                        gamma = 100 - alpha - beta - delta

                        bleu_scores = []

                        for task_id, queries in user_queries.items():
                            queries = self.queries[task_id]
                            num = len(queries)

                            for i in range(SIMULATE_ROUNDS):
                                query_simulated = self.simulate(num, task_id, alpha, beta, gamma, delta)
                                bleu_scores.extend([self._evaluation_bleu(generated, original)
                                                    for generated, original in zip(query_simulated, queries)])

                        average_bleu = round(sum(bleu_scores) / len(bleu_scores), 4)

                        # 用于确定最佳的参数
                        if average_bleu > max_bleu:
                            max_bleu = average_bleu
                            print(max_bleu)

                        if average_bleu >= max_bleu * 0.9:
                            evaluation_all.append(
                                [user_id, alpha / 100, beta / 100, gamma / 100, delta / 100, average_bleu])
                            print(
                                f"{user_id}\t{alpha / 100}\t{beta / 100}\t{gamma / 100}\t{delta / 100}\t{average_bleu}")

            evaluation_best.append(max_bleu)
            filename = project_path('baseline', '2', 'output',  f'output_user_{self.len_strategy}_{self.term_strategy}_{user_id}.csv')
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(evaluation_all)
        print(f"Average best BLEU across users: {sum(evaluation_best) / len(evaluation_best)}")

    def ranked_for_users(self):
        # 获取当前目录下所有前缀相同的 CSV 文件
        file_pattern = project_path('baseline', '2', 'output', f'output_user_{self.len_strategy}_{self.term_strategy}_*.csv')
        csv_files = glob.glob(file_pattern)

        for filename in csv_files:
            # 读取文件
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                next(reader)
                output = [['user_id', 'alpha', 'beta', 'gamma', 'delta', 'bleu']]
                temp = []
                temp.append(next(reader))
                user_id = temp[0][0]
                for row in reader:
                    if row[0] == user_id:
                        temp.append(row)
                    else:
                        temp.sort(key=lambda x: x[5], reverse=True)
                        output.extend(temp[:10])

                        user_id = row[0]
                        temp = []
                        temp.append(row)

                temp.sort(key=lambda x: x[5], reverse=True)
                output.extend(temp[:10])

            with open(
                    project_path('baseline', '2', 'output', f'output_user_{self.len_strategy}_{self.term_strategy}_{user_id}_ranked.csv'),
                    'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(output)

    def caculate_best_args(self):
        # 计算两种bleu评估方法下，最佳的参数对于每个task、所有task平均、所有user平均是多少。保存参数到baseline1_best_args.csv中

        # 1. 对于所有tasks方法下参数文件
        file_pattern = project_path('baseline', '2', 'output', f'output_task_{self.len_strategy}_*.csv')
        csv_files = glob.glob(file_pattern)

        ## 存储所有文件处理后的数据
        output_data = []


        ## 遍历每个 CSV 文件
        for file in csv_files:
            ### 读取 CSV 文件
            df = pd.read_csv(file)

            ### 计算阈值
            threshold = 0.9 * df.iloc[0]['bleu']

            ### 找到满足条件的行，并计算平均值
            selected_rows = df[df['bleu'] >= threshold]
            if not selected_rows.empty:
                avg_values = selected_rows[['alpha', 'beta', 'gamma', 'delta', 'bleu']].mean()
                task_id = selected_rows.iloc[0]['task_id']  # 获取 task_id
                output_data.append({'id': task_id, **avg_values})

        ## 创建 DataFrame 存储输出数据
        output_df = pd.DataFrame(output_data)

        ## 计算所有行的平均值并添加到 DataFrame 末尾
        overall_avg_values = output_df[['alpha', 'beta', 'gamma', 'delta', 'bleu']].mean()
        overall_avg_row = {'id': 'tasks_average', **overall_avg_values}
        output_df = pd.concat([output_df, pd.DataFrame([overall_avg_row])], ignore_index=True)


        # 2. 对于所有methods方法下参数文件
        file_pattern = project_path('baseline', '2', 'output', f'output_user_{self.len_strategy}_{self.term_strategy}_*_ranked.csv')
        csv_files = glob.glob(file_pattern)

        ## 存储所有文件处理后的数据
        output_data = []

        ## 遍历每个 CSV 文件
        for file in csv_files:
            ### 读取 CSV 文件
            df = pd.read_csv(file)

            ### 计算阈值
            threshold = 0.9 * df.iloc[0]['bleu']

            ### 找到满足条件的行，并计算平均值
            selected_rows = df[df['bleu'] >= threshold]
            if not selected_rows.empty:
                avg_values = selected_rows[['alpha', 'beta', 'gamma', 'delta', 'bleu']].mean()
                output_data.append({**avg_values})

        ## 计算所有users行的平均值并添加到 DataFrame 末尾
        users_df = pd.DataFrame(output_data)
        users_avg_values = users_df[['alpha', 'beta', 'gamma', 'delta', 'bleu']].mean()
        users_avg_row = {'id': 'users_average', **users_avg_values}
        output_df = pd.concat([output_df, pd.DataFrame([users_avg_row])], ignore_index=True)

        # 将结果写入输出文件
        output_file = project_path('baseline', '2', 'output', "baseline1_best_args.csv")
        output_df.to_csv(output_file, index=False)

    def simulation_with_best_args(self, alpha, beta, gamma):
        output_data = {}
        for task_id in self.queries:
            output_data[task_id] = []
            queries = self.queries[task_id]
            num = len(queries)

            for i in range(SIMULATE_ROUNDS):
                query_simulated = self.simulate(num, task_id, alpha, beta, gamma, 0)
                output_data[task_id].append(query_simulated)

        # Save evaluation to CSV
        filename = project_path('baseline', '2', 'output', f'baseline2_data.json')
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(output_data, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    # q = QuerySimulatorOptimized('term_length', 'frequent')
    q = QuerySimulatorOptimized('term_length', 'random') # 不打算做，反正效果也不好

    # q.evaluation_bleu_with_tasks()
    # q.evaluation_bleu_with_users()  # Average best BLEU across users: 0.11099333333333333
    # q.ranked_for_users()
    # q.caculate_best_args()
    q.simulation_with_best_args(100, 0, 0) # 采用平均task的参数采样 0.6	0.4	0.0015
