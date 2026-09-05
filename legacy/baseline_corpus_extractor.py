# Historical 2024 thesis code, prepared for public review in September 2026.
# Comments/examples were removed for privacy; see docs/PROVENANCE.md.
# Chinese prompt text is retained as part of the experimental implementation.

import json
import os
import re
import jieba
from prompt_library_s import all_task_background, all_task_goal
import sqlite3

OCR_PATH = r"data/OCRtxtzhongnew"
SQ_PATH = r'data/db.sqlite3'

class QueryExtractor:
    def __init__(self):
        self.stopwords_file = os.path.join('baseline', 'stopwords.txt')
        self.input_file = os.path.join('data', 'data_update0302.json')

        self.output_file1 = os.path.join('baseline', 'corpus', 'task_description.json')
        self.output_file2 = os.path.join('baseline', 'corpus', 'title.json')
        self.output_file3 = os.path.join('baseline', 'corpus', 'abstract.json')
        self.output_file4 = os.path.join('baseline', 'corpus', 'content.json')

        self.stopwords = []
        with open(self.stopwords_file, 'r', encoding='utf-8') as file:
            for line in file:
                self.stopwords.append(line.strip())

        self.pattern = re.compile(r'[\u4e00-\u9fff]')

        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        conn = sqlite3.connect(SQ_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, query FROM search_api_queryserp")
        db_rows = cursor.fetchall()

        self.db_queries = {row[1]: row[0] for row in db_rows}

    def run(self):

        corpus1 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
        for task_id, task_description in enumerate([all_task_background[key] + all_task_goal[key] for key in all_task_background]):
            corpus1[str(task_id+1)].extend([t for t in jieba.cut(task_description) if
                                 t not in self.stopwords and re.search(self.pattern, t)])

        corpus2 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
        corpus3 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}
        corpus4 = {'1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [], '8': [], '9': [], '10': []}

        folders = next(os.walk(OCR_PATH))[1]

        for user in self.data:
            for task_id, task_content in user["task"].items():
                for json_query_id, query_content in task_content["content"].items():
                    print(json_query_id)

                    query = query_content["query"]
                    sq_query_id = self.db_queries[query]

                    if str(sq_query_id) in folders:
                        joined_content = self.read_txt_files(os.path.join(OCR_PATH, str(sq_query_id)))
                    else:
                        joined_content = ""

                    corpus4[task_id].extend([t for t in jieba.cut(joined_content) if
                                             t not in self.stopwords and re.search(self.pattern, t)])

                    for link in query_content["SERP"]:

                        corpus2[task_id].extend([t for t in jieba.cut(link['title']) if
                                                 t not in self.stopwords and re.search(self.pattern, t)])

                        corpus3[task_id].extend([t for t in jieba.cut(link['snippet']) if
                                                 t not in self.stopwords and re.search(self.pattern, t)])

        with open(self.output_file1, 'w', encoding='utf-8') as file:
            json.dump(corpus1, file, ensure_ascii=False)

        with open(self.output_file2, 'w', encoding='utf-8') as file:
            json.dump(corpus2, file, ensure_ascii=False)

        with open(self.output_file3, 'w', encoding='utf-8') as file:
            json.dump(corpus3, file, ensure_ascii=False)

        with open(self.output_file4, 'w', encoding='utf-8') as file:
            json.dump(corpus4, file, ensure_ascii=False)

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
