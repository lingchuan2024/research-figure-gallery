"""Generate deterministic synthetic demo CSVs for all six templates (F01/F02/F06/F07/F08/F09)."""
from pathlib import Path
import csv
import numpy as np

HERE = Path(__file__).resolve().parent
DEMO_DIR = HERE / 'data' / 'demo'


def write_csv(name, fieldnames, rows):
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    with (DEMO_DIR / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    rng = np.random.default_rng(20261121)
    methods = ['baseline', 'auto_rerank', 'agent_rerank']
    subsets = ['Direct', 'Bridge', 'Comparison']

    # 1. observations.csv (F01 & F02 binary) + observations_bounded.csv (F02 continuous nDCG)
    obs_rows = []
    bounded_rows = []
    tool_rows = []

    for i in range(1, 121):
        qid = f'q{i:03d}'
        subset = subsets[(i - 1) % 3]
        diff = rng.normal(0.0, 0.7)
        base_ndcg = float(np.clip(0.56 - 0.12 * diff + rng.normal(0, 0.08), 0.05, 0.98))

        for m in methods:
            if m == 'baseline':
                p = 1 / (1 + np.exp(-(0.25 - diff + (0.2 if subset == 'Direct' else -0.15))))
                wall = max(8.0, rng.lognormal(3.6, 0.45))
                rsec = 0.0
                mtok = int(max(3000, rng.normal(14800, 3200)))
                rtok = 0
                revents = 0
                spass = 0
                ndcg = base_ndcg
                t_calls = {'search': int(rng.integers(5, 13)), 'bash': int(rng.integers(12, 26)), 'read': int(rng.integers(4, 11)), 'rerank': 0}
            elif m == 'auto_rerank':
                p = 1 / (1 + np.exp(-(0.40 - diff + (0.1 if subset == 'Bridge' else -0.05))))
                wall = max(10.0, rng.lognormal(3.75, 0.42))
                rsec = round(float(max(0.8, rng.normal(4.8, 1.4))), 2)
                mtok = int(max(3000, rng.normal(12600, 2900)))
                rtok = int(max(1200, rng.normal(6400, 1800)))
                revents = int(rng.integers(4, 9))
                spass = revents * 50
                ndcg = float(np.clip(base_ndcg + rng.normal(0.04, 0.06), 0.05, 0.99))
                t_calls = {'search': int(rng.integers(5, 11)), 'bash': int(rng.integers(8, 18)), 'read': int(rng.integers(4, 10)), 'rerank': revents}
            else:
                p = 1 / (1 + np.exp(-(0.72 - diff + (0.35 if subset == 'Bridge' else 0.05))))
                wall = max(7.0, rng.lognormal(3.38, 0.38))
                rsec = round(float(max(0.0, rng.normal(1.7, 0.8))), 2)
                mtok = int(max(2500, rng.normal(10400, 2400)))
                rtok = int(max(0, rng.normal(2400, 1100)))
                revents = int(rng.integers(0, 5))
                spass = revents * 40
                ndcg = float(np.clip(base_ndcg + rng.normal(0.09, 0.06), 0.05, 0.99))
                t_calls = {'search': int(rng.integers(4, 10)), 'bash': int(rng.integers(6, 14)), 'read': int(rng.integers(3, 9)), 'rerank': revents}

            timeout = wall > 220.0
            status = 'timeout' if timeout else 'complete'
            score = 0 if timeout else int(rng.random() < p)
            obs_rows.append({
                'benchmark': 'DemoQA', 'question_id': qid, 'subset': subset, 'method': m,
                'score': score, 'status': status,
                'wall_seconds': round(min(wall, 240.0), 2),
                'rerank_seconds': rsec,
                'main_input_tokens': mtok,
                'reranker_input_tokens': rtok,
                'rerank_events': revents,
                'scored_passages': spass,
            })
            bounded_rows.append({
                'benchmark': 'DemoQA', 'question_id': qid, 'subset': subset, 'method': m,
                'score': round(ndcg, 4), 'status': 'complete',
                'wall_seconds': round(min(wall, 240.0), 2),
                'rerank_seconds': rsec,
                'main_input_tokens': mtok,
                'reranker_input_tokens': rtok,
                'rerank_events': revents,
                'scored_passages': spass,
            })
            char_mult = {'search': 1200, 'bash': 1950, 'read': 2400, 'rerank': 620}
            for tool, cnt in t_calls.items():
                chars = int(cnt * char_mult[tool] * rng.uniform(0.75, 1.25)) if cnt > 0 else 0
                tool_rows.append({
                    'benchmark': 'DemoQA', 'question_id': qid, 'method': m,
                    'tool': tool, 'calls': cnt, 'returned_chars': chars,
                })

    write_csv(
        'observations.csv',
        ['benchmark', 'question_id', 'subset', 'method', 'score', 'status',
         'wall_seconds', 'rerank_seconds', 'main_input_tokens', 'reranker_input_tokens',
         'rerank_events', 'scored_passages'],
        obs_rows,
    )
    write_csv(
        'observations_bounded.csv',
        ['benchmark', 'question_id', 'subset', 'method', 'score', 'status',
         'wall_seconds', 'rerank_seconds', 'main_input_tokens', 'reranker_input_tokens',
         'rerank_events', 'scored_passages'],
        bounded_rows,
    )
    write_csv(
        'tool_calls.csv',
        ['benchmark', 'question_id', 'method', 'tool', 'calls', 'returned_chars'],
        tool_rows,
    )

    # 2. budget_runs.csv (F06)
    budget_rows = []
    budgets = [10, 20, 40, 60, 100]
    base_curve = {'baseline': [0.34, 0.45, 0.54, 0.58, 0.60],
                  'auto_rerank': [0.38, 0.50, 0.59, 0.62, 0.63],
                  'agent_rerank': [0.42, 0.56, 0.66, 0.70, 0.72]}
    for b_idx, bval in enumerate(budgets):
        for i in range(1, 101):
            qid = f'q{i:03d}'
            latent = rng.random()
            for m in methods:
                p = base_curve[m][b_idx]
                score = int(latent < p)
                budget_rows.append({
                    'benchmark': 'DemoQA', 'question_id': qid, 'method': m,
                    'budget_value': bval, 'score': score, 'status': 'complete',
                })
    write_csv('budget_runs.csv', ['benchmark', 'question_id', 'method', 'budget_value', 'score', 'status'], budget_rows)

    # 3. rank_transitions.csv (F07)
    rank_rows = []
    before_choices = [1, 3, 8, 35, 220]
    for i in range(1, 121):
        qid = f'q{i:03d}'
        for d in range(1, 4):
            doc_id = f'doc_{i:03d}_{d}'
            rb = int(rng.choice(before_choices, p=[0.08, 0.18, 0.22, 0.36, 0.16]))
            if rb == 1:
                ra = int(rng.choice([1, 2, 3], p=[0.84, 0.11, 0.05]))
            elif rb <= 5:
                ra = int(rng.choice([1, 3, 7, 15], p=[0.52, 0.28, 0.13, 0.07]))
            elif rb <= 10:
                ra = int(rng.choice([1, 3, 8, 20, 120], p=[0.24, 0.38, 0.20, 0.14, 0.04]))
            elif rb <= 100:
                ra = int(rng.choice([1, 4, 8, 25, 140], p=[0.10, 0.24, 0.22, 0.34, 0.10]))
            else:
                ra = 'outside' if rng.random() < 0.22 else int(rng.choice([8, 45, 180], p=[0.12, 0.38, 0.50]))
            rank_rows.append({
                'benchmark': 'DemoQA', 'question_id': qid, 'method': 'agent_rerank',
                'doc_id': doc_id, 'rank_before': rb, 'rank_after': ra, 'is_relevant': 1,
            })
    write_csv('rank_transitions.csv',
              ['benchmark', 'question_id', 'method', 'doc_id', 'rank_before', 'rank_after', 'is_relevant'],
              rank_rows)

    # 4. trajectories.csv (F09)
    traj_rows = [
        # Baseline: 14 turns, late evidence, wrong
        ('case_042', 'baseline', 1, 'search', 'none', 'initial query'),
        ('case_042', 'baseline', 2, 'bash', 'none', 'broad rg'),
        ('case_042', 'baseline', 3, 'bash', 'none', 'filter noisy hits'),
        ('case_042', 'baseline', 4, 'read', 'none', 'distractor doc'),
        ('case_042', 'baseline', 5, 'search', 'none', 'reformulate'),
        ('case_042', 'baseline', 6, 'bash', 'none', 'rg entity'),
        ('case_042', 'baseline', 7, 'read', 'none', 'partial clue'),
        ('case_042', 'baseline', 8, 'search', 'none', 'second hop'),
        ('case_042', 'baseline', 9, 'bash', 'none', 'scan workspace'),
        ('case_042', 'baseline', 10, 'read', 'first_evidence', 'answer clue found'),
        ('case_042', 'baseline', 11, 'bash', 'none', 'verify dates'),
        ('case_042', 'baseline', 12, 'answer', 'final_wrong', 'wrong entity'),
        # Auto rerank: 9 turns, frequent rerank, correct
        ('case_042', 'auto_rerank', 1, 'search', 'none', 'initial query'),
        ('case_042', 'auto_rerank', 2, 'rerank', 'none', 'auto rerank #1'),
        ('case_042', 'auto_rerank', 3, 'read', 'none', 'top snippet'),
        ('case_042', 'auto_rerank', 4, 'search', 'none', 'second hop'),
        ('case_042', 'auto_rerank', 5, 'rerank', 'rerank_hit', 'auto rerank #2'),
        ('case_042', 'auto_rerank', 6, 'read', 'first_evidence', 'answer clue found'),
        ('case_042', 'auto_rerank', 7, 'rerank', 'none', 'auto rerank #3'),
        ('case_042', 'auto_rerank', 8, 'read', 'none', 'verify'),
        ('case_042', 'auto_rerank', 9, 'answer', 'final_correct', 'verified'),
        # Agent rerank: 6 turns, 1 targeted rerank, correct
        ('case_042', 'agent_rerank', 1, 'search', 'none', 'initial query'),
        ('case_042', 'agent_rerank', 2, 'bash', 'none', 'narrow workspace'),
        ('case_042', 'agent_rerank', 3, 'rerank', 'rerank_hit', 'targeted rerank'),
        ('case_042', 'agent_rerank', 4, 'read', 'first_evidence', 'answer clue found'),
        ('case_042', 'agent_rerank', 5, 'read', 'none', 'cross-check'),
        ('case_042', 'agent_rerank', 6, 'answer', 'final_correct', 'verified'),
    ]
    write_csv(
        'trajectories.csv',
        ['case_id', 'method', 'turn', 'tool', 'event_flag', 'note'],
        [dict(zip(['case_id', 'method', 'turn', 'tool', 'event_flag', 'note'], r)) for r in traj_rows],
    )
    print(f'Generated synthetic demo datasets in {DEMO_DIR}')


if __name__ == '__main__':
    main()
