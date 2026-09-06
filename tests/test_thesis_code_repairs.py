"""Dependency-free checks for scoped repairs to the 2024 thesis code."""

import ast
import contextlib
import importlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "thesis_code"
sys.path.insert(0, str(CODE))


class ThesisCodeRepairTests(unittest.TestCase):
    def test_prompt_variant_modules_exist(self):
        tree = ast.parse((CODE / "simulator.py").read_text())
        assignment = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "PROMPT_VARIANTS"
        )
        variants = ast.literal_eval(assignment.value)
        self.assertIn("standard", variants)
        self.assertIn("wo_feedback", variants)
        for module_name, _ in variants.values():
            self.assertTrue((CODE / f"{module_name}.py").is_file(), module_name)

    def test_json_first_response_parser(self):
        module = importlib.import_module("clean_answers")
        thought, query = module.parse_generated_response([
            {"步骤": 1, "类型": "思考", "内容": "先找定义"},
            {"步骤": 1, "类型": "查询", "内容": "测试查询"},
        ])
        self.assertEqual(thought, "先找定义")
        self.assertEqual(query, "测试查询")

        thought, query = module.parse_generated_response(
            '```json\n{"类型": "查询", "内容": "围栏中的查询"}\n```'
        )
        self.assertEqual(thought, "")
        self.assertEqual(query, "围栏中的查询")

    def test_query_only_extraction_keeps_query(self):
        module = importlib.import_module("extract_query")
        source = [{
            "user_id": 1,
            "task": {
                "1": {
                    "content": {
                        "event-1": {"query": "synthetic query", "thought": "synthetic rationale"}
                    }
                }
            },
        }]
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            input_path = directory / "input.json"
            output_path = directory / "output.json"
            input_path.write_text(json.dumps(source))
            old_input, old_output = module.original_path, module.generate_path
            module.original_path, module.generate_path = str(input_path), str(output_path)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    module.extract_query(only_query=True)
            finally:
                module.original_path, module.generate_path = old_input, old_output
            output = json.loads(output_path.read_text())
        self.assertEqual(output[0]["task"]["1"]["1"], {"query": "synthetic query"})


if __name__ == "__main__":
    unittest.main()
