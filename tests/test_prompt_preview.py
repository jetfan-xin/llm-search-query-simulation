"""2026 offline checks of retained history selection and prompt assembly."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from preview_prompt import VARIANTS, build_preview


class PromptPreviewTests(unittest.TestCase):
    def test_all_variants_build(self):
        for variant in VARIANTS:
            for step in (1, 2, 3):
                with self.subTest(variant=variant, step=step):
                    result = build_preview(variant, step)
                    self.assertGreater(result['prompt_characters'], 100)
                    self.assertEqual(result['prior_query_count'], step - 1)
                    self.assertEqual(result['network_calls'], 0)

    def test_no_current_or_future_query_leakage(self):
        for variant in VARIANTS:
            prompt = build_preview(variant, 2)['prompt']
            self.assertIn('quiet public libraries', prompt)
            self.assertNotIn('library weekend opening hours', prompt)
            self.assertNotIn('FUTURE_QUERY_NOT_VISIBLE', prompt)
            self.assertNotIn('FUTURE_FEEDBACK_NOT_VISIBLE', prompt)

    def test_first_query_has_no_recorded_history(self):
        prompt = build_preview('standard', 1)['prompt']
        self.assertNotIn('quiet public libraries', prompt)
        self.assertNotIn('SYNTHETIC_FEEDBACK', prompt)

    def test_only_clicked_results_enter_history(self):
        prompt = build_preview('standard', 2)['prompt']
        self.assertIn('SYNTHETIC_OBSERVATION', prompt)
        self.assertNotIn('UNCLICKED_RESULT_NOT_VISIBLE', prompt)

    def test_rationale_ablation(self):
        self.assertIn('SYNTHETIC_RATIONALE', build_preview('standard', 2)['prompt'])
        self.assertNotIn('SYNTHETIC_RATIONALE', build_preview('no-rationale', 2)['prompt'])

    def test_feedback_ablation(self):
        self.assertIn('SYNTHETIC_FEEDBACK', build_preview('standard', 2)['prompt'])
        self.assertNotIn('SYNTHETIC_FEEDBACK', build_preview('no-feedback', 2)['prompt'])

    def test_observation_ablation(self):
        self.assertNotIn('SYNTHETIC_OBSERVATION', build_preview('no-observation', 2)['prompt'])

    def test_profile_ablation(self):
        self.assertIn('Synthetic study participant', build_preview('standard', 2)['prompt'])
        self.assertNotIn('Synthetic study participant', build_preview('no-profile', 2)['prompt'])

    def test_example_ablation(self):
        self.assertIn('Synthetic demonstration:', build_preview('standard', 2)['prompt'])
        self.assertNotIn('Synthetic demonstration:', build_preview('no-example', 2)['prompt'])

    def test_invalid_inputs(self):
        for step in (0, -1, 4, True):
            with self.assertRaises(ValueError):
                build_preview('standard', step)
        with self.assertRaises(ValueError):
            build_preview('not-a-variant', 2)


if __name__ == '__main__':
    unittest.main()
