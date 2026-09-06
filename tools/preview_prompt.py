#!/usr/bin/env python3
"""Exercise original prompt-building methods on a synthetic fixture, offline.

Added in 2026. No SDK import, constructor, model call or participant-data access.
Only literal prompt definitions and two inspected historical methods are loaded.
"""

import argparse
import ast
import json
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
VARIANTS = {
    'standard': ('prompt_library_s.py', ''),
    'no-rationale': ('prompt_library_wo_thought.py', 'wo_thought'),
    'no-feedback': ('prompt_library_wo_feedback.py', 'wo_feedback'),
    'no-rationale-feedback': ('prompt_library_wo_thought_feedback.py', 'wo_thought_feedback'),
    'no-observation': ('prompt_library_wo_observation.py', 'wo_observation'),
    'no-profile': ('prompt_library_wo_charactor_s.py', 'wo_charactor'),
    'no-example': ('prompt_library_wo_guidance_s.py', 'wo_guidance'),
    'no-profile-example': ('prompt_library_wo_guidance_charactor_s.py', 'wo_guidance_charactor'),
    'rationale-output': ('prompt_library_tol.py', 'all_prompt'),
}


def build_preview(variant='standard', step=2):
    if variant not in VARIANTS:
        raise ValueError('Unknown preview variant')
    fixture = json.loads((ROOT / 'examples/synthetic_session.json').read_text())
    if fixture.get('synthetic') is not True:
        raise ValueError('The offline preview requires an explicitly synthetic fixture')
    task_id = fixture['task_id']
    events = fixture['users'][0]['task'][task_id]['content']
    if type(step) is not int or not 1 <= step <= len(events):
        raise ValueError('Step must be between 1 and the synthetic session length')

    filename, prompt_type = VARIANTS[variant]
    template_tree = ast.parse((ROOT / 'thesis_code' / filename).read_text())
    namespace = {}
    for node in template_tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            namespace[node.targets[0].id] = ast.literal_eval(node.value)
    prompt_module = SimpleNamespace(
        all_task_background={task_id: fixture['task_background']},
        all_task_goal={task_id: fixture['task_goal']},
        main_prompt=namespace['main_prompt'],
        guidance='' if 'guidance' in prompt_type else fixture['example'],
    )

    source = ROOT / 'thesis_code' / 'simulator.py'
    tree = ast.parse(source.read_text())
    original_class = next(node for node in tree.body
                          if isinstance(node, ast.ClassDef) and node.name == 'GenerateQuery')
    methods = [node for node in original_class.body
               if isinstance(node, ast.FunctionDef) and node.name in ('get_history', 'compose_prompt')]
    if len(methods) != 2:
        raise ValueError('Expected exactly the two reviewed prompt-building methods')
    # No top-level code, SDK imports, file-reading constructor or generation methods.
    preview_class = ast.ClassDef(name='OfflinePromptBuilder', bases=[], keywords=[],
                                body=methods, decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[preview_class], type_ignores=[]))
    exec(compile(module, str(source), 'exec'), namespace)
    builder = namespace['OfflinePromptBuilder']()
    builder.all_data = fixture['users']
    builder.prompt_type = prompt_type
    builder.prompt_module = prompt_module
    prompt = builder.compose_prompt(fixture['users'][0]['user_id'], task_id, step - 1)
    return {
        'mode': 'synthetic offline preview, added in 2026',
        'variant': variant,
        'query_step': step,
        'prior_query_count': step - 1,
        'template': filename,
        'prompt_characters': len(prompt),
        'network_calls': 0,
        'prompt': prompt,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=VARIANTS, default='standard')
    parser.add_argument('--step', type=int, default=2)
    parser.add_argument('--show-prompt', action='store_true')
    args = parser.parse_args()
    try:
        result = build_preview(args.variant, args.step)
    except ValueError as error:
        parser.error(str(error))
    if not args.show_prompt:
        result.pop('prompt')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
