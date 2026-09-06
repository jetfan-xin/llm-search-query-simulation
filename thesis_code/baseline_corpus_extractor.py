import json
import os
import re
import jieba
from prompt_library_s import all_task_background, all_task_goal
import sqlite3
from project_paths import project_path

# 用于基线模拟方法，提取每个任务对应的四个词汇数据集（任务描述、网页标题、网页摘要、网页内容）。
OCR_PATH = project_path("data", "OCRtxtzhongnew")
SQ_PATH = project_path('data', 'db.sqlite3')

class QueryExtractor:
    def __init__(self):
        self.stopwords_file = project_path('baseline', 'stopwords.txt')
        self.input_file = project_path('data', 'data_update0302.json')
        # 两个基线共享同一份语料；原工作目录中保存了两份相同副本。
        self.output_dirs = [
            project_path('baseline', '1', 'corpus'),
            project_path('baseline', '2', 'corpus'),
        ]

        self.stopwords = []
        with open(self.stopwords_file, 'r', encoding='utf-8') as file:
            for line in file:
                self.stopwords.append(line.strip())

        self.pattern = re.compile(r'[\u4e00-\u9fff]')

        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # 连接数据库
        conn = sqlite3.connect(SQ_PATH)
        cursor = conn.cursor()
        # 获取数据库中所有的查询
        cursor.execute("SELECT id, query FROM search_api_queryserp")
        db_rows = cursor.fetchall()
        # 转换数据库结果为查询到ID的映射，这样查询效率更高
        self.db_queries = {row[1]: row[0] for row in db_rows}

    def run(self):
        # 获取所有任务描述 description
        corpus1 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
        for task_id, task_description in enumerate([all_task_background[key] + all_task_goal[key] for key in all_task_background]):
            corpus1[str(task_id+1)].extend([t for t in jieba.cut(task_description) if
                                 t not in self.stopwords and re.search(self.pattern, t)])

        # 获取所有网页标题、网页摘要、网页内容 title & abstract & content
        corpus2 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
        corpus3 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
        corpus4 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}

        # 获取OCR文件夹中的所有文件夹名
        folders = next(os.walk(OCR_PATH))[1]

        for user in self.data:
            for task_id, task_content in user["task"].items():
                for json_query_id, query_content in task_content["content"].items():
                    print(json_query_id)
                    # 获取从db.sqlite 获取 content
                    query = query_content["query"]
                    sq_query_id = self.db_queries[query]
                    # 检查目标文件夹是否在列表中
                    if str(sq_query_id) in folders:
                        joined_content = self.read_txt_files(os.path.join(OCR_PATH, str(sq_query_id)))
                    else:
                        joined_content = ""

                    # content
                    corpus4[task_id].extend([t for t in jieba.cut(joined_content) if
                                             t not in self.stopwords and re.search(self.pattern, t)])

                    for link in query_content["SERP"]:
                        # title
                        corpus2[task_id].extend([t for t in jieba.cut(link['title']) if
                                                 t not in self.stopwords and re.search(self.pattern, t)])
                        # abstract
                        corpus3[task_id].extend([t for t in jieba.cut(link['snippet']) if
                                                 t not in self.stopwords and re.search(self.pattern, t)])



        corpora = {
            'task_description.json': corpus1,
            'title.json': corpus2,
            'abstract.json': corpus3,
            'content.json': corpus4,
        }
        for output_dir in self.output_dirs:
            os.makedirs(output_dir, exist_ok=True)
            for filename, corpus in corpora.items():
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as file:
                    json.dump(corpus, file, ensure_ascii=False)

    def read_txt_files(self, folder_path):
        joined_content = ""
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    joined_content += file_content + "\n"
        return joined_content

if __name__ == "__main__":
    generator = QueryExtractor()
    generator.run()
