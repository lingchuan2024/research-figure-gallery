"""Standalone CSV contracts, paired statistics and output for rerank templates."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import os
import textwrap

HERE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(HERE / '.cache' / 'matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(HERE / '.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import is_color_like
import numpy as np

IDENTITY = ('benchmark', 'question_id', 'subset', 'method', 'status')
METRICS = {
    'wall_seconds': ('End-to-end time / question (s)', 's'),
    'rerank_seconds': ('Reranker scoring time / question (s)', 's'),
    'main_input_tokens': ('Main-model input tokens / question', 'tokens'),
    'reranker_input_tokens': ('Reranker input tokens / question', 'tokens'),
    'rerank_events': ('Reranking events / question', 'events'),
    'scored_passages': ('Scored passages / question', 'passages'),
}
INTEGER_METRICS = set(METRICS) - {'wall_seconds', 'rerank_seconds'}
CONDITIONS = ('question_set', 'generator_model', 'retrieval_policy', 'hardware',
              'concurrency', 'stopping_rule', 'run_selection')


def setup():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.titlesize': 12, 'axes.labelsize': 10, 'xtick.labelsize': 9,
        'ytick.labelsize': 9, 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.edgecolor': '#98A5AB', 'axes.labelcolor': '#243746',
        'text.color': '#243746', 'xtick.color': '#243746', 'ytick.color': '#243746',
        'axes.axisbelow': True, 'grid.color': '#E5EAED', 'grid.linewidth': .7,
        'legend.frameon': False, 'savefig.dpi': 180, 'svg.fonttype': 'none',
        'svg.hashsalt': 'rerank-templates-20261116', 'figure.facecolor': 'white'})


def arguments(stem, argv=None):
    parser = argparse.ArgumentParser(description=f'Render {stem} from paired question-level observations.')
    parser.add_argument('--data', type=Path, default=HERE / 'data/demo/observations.csv')
    parser.add_argument('--config', type=Path, default=HERE / 'config.json')
    parser.add_argument('--output-dir', type=Path, default=HERE / 'figures')
    parser.add_argument('--formats', nargs='+', choices=['png', 'svg', 'pdf'], default=['png', 'svg', 'pdf'])
    parser.add_argument('--metric', choices=list(METRICS), default='wall_seconds',
                        help='Cost metric for raincloud and Pareto; forest always uses score.')
    parser.add_argument('--scale', choices=['linear', 'log1p'], default='linear',
                        help='Cost-axis scale for raincloud/Pareto. log1p retains zero and labels original units.')
    parser.add_argument('--missing-cost', choices=['error', 'complete-case'], default='error',
                        help='Fail on missing selected cost, or explicitly remove that question from ALL methods.')
    parser.add_argument('--bootstrap', type=int, default=3000)
    parser.add_argument('--seed', type=int, default=20261116)
    args = parser.parse_args(argv)
    if args.bootstrap < 200:
        parser.error('--bootstrap must be at least 200; default is 3000.')
    if args.seed < 0:
        parser.error('--seed must be nonnegative.')
    custom = args.data.resolve() != (HERE / 'data/demo/observations.csv').resolve() or args.config.resolve() != (HERE / 'config.json').resolve()
    if custom and args.output_dir.resolve() == (HERE / 'figures').resolve():
        parser.error('Custom inputs require a separate --output-dir to preserve the bundled demo.')
    return args


def validate_config(config):
    if not isinstance(config, dict) or config.get('schema_version') != 1:
        raise ValueError('config.schema_version must be 1.')
    if config.get('data_kind') not in {'synthetic', 'measured'}:
        raise ValueError('config.data_kind must be synthetic or measured.')
    if not isinstance(config.get('experiment'), str) or not config['experiment'].strip():
        raise ValueError('config.experiment must describe the comparison.')
    methods = config.get('methods')
    if not isinstance(methods, list) or len(methods) < 2:
        raise ValueError('At least two configured methods are required.')
    ids = []
    for method in methods:
        if not isinstance(method, dict) or any(not isinstance(method.get(k), str) or not method[k].strip() for k in ('id', 'label', 'color')):
            raise ValueError('Each method requires nonempty id, label and color.')
        if not is_color_like(method['color']):
            raise ValueError(f'Invalid method color: {method["color"]}')
        ids.append(method['id'])
    if len(set(ids)) != len(ids) or config.get('baseline') not in ids:
        raise ValueError('Method IDs must be unique and baseline must be a configured ID.')
    score = config.get('score', {})
    if not isinstance(score, dict) or score.get('kind') not in {'binary', 'bounded'}:
        raise ValueError('score.kind must be binary (0/1) or bounded ([0,1]).')
    for key in ('label', 'unit', 'delta_unit'):
        if not isinstance(score.get(key), str) or not score[key].strip():
            raise ValueError(f'score.{key} is required; include metric and cutoff in label.')
    scale = score.get('scale')
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not math.isfinite(scale) or scale <= 0:
        raise ValueError('score.scale must be a finite positive display multiplier.')
    conditions = config.get('conditions', {})
    for key in CONDITIONS:
        if not isinstance(conditions.get(key), str) or not conditions[key].strip():
            raise ValueError(f'conditions.{key} must be recorded explicitly.')
        if config['data_kind'] == 'measured' and conditions[key].startswith('REPLACE_'):
            raise ValueError(f'Fill conditions.{key} before rendering measured data.')
    return config


def validate_rows(records, config):
    validate_config(config)
    if not records:
        raise ValueError('Input CSV has no observations.')
    allowed = {method['id'] for method in config['methods']}
    converted, seen, sets, subsets = [], set(), {}, {}
    for line, raw in enumerate(records, 2):
        if None in raw:
            raise ValueError(f'CSV line {line}: extra values beyond the header.')
        row = dict(raw)
        for key in IDENTITY:
            if row.get(key) is None or not str(row[key]).strip():
                raise ValueError(f'CSV line {line}: missing {key}.')
            row[key] = str(row[key]).strip()
        if row['subset'].casefold() == 'all':
            raise ValueError('subset=All is reserved for the computed all-question summary.')
        if row['method'] not in allowed:
            raise ValueError(f'Unknown method {row["method"]}; update config.methods explicitly.')
        if row['status'] not in {'complete', 'timeout', 'no_final', 'error'}:
            raise ValueError(f'Unsupported status {row["status"]}.')
        try:
            row['score'] = float(row['score'])
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f'CSV line {line}: score must be numeric, not missing.') from exc
        if not math.isfinite(row['score']) or not 0 <= row['score'] <= 1:
            raise ValueError(f'CSV line {line}: score must be finite and within [0,1].')
        if config['score']['kind'] == 'binary':
            if row['score'] not in {0., 1.}:
                raise ValueError('Binary score must be exactly 0 or 1.')
            if row['status'] != 'complete' and row['score'] != 0:
                raise ValueError('For binary final-answer scoring, unsuccessful terminal status requires score=0.')
        for key in METRICS:
            if row.get(key) is None or str(row[key]).strip() == '':
                row[key] = None
                continue
            try:
                value = float(row[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f'CSV line {line}: {key} must be numeric or blank.') from exc
            if not math.isfinite(value) or value < 0:
                raise ValueError(f'CSV line {line}: {key} must be finite and nonnegative.')
            if key in INTEGER_METRICS and value != int(value):
                raise ValueError(f'CSV line {line}: {key} must be an integer count.')
            row[key] = value
        key = (row['benchmark'], row['question_id'], row['method'])
        if key in seen:
            raise ValueError(f'Duplicate question/method key {key}; select one run or aggregate repetitions first.')
        seen.add(key)
        sets.setdefault((row['benchmark'], row['method']), set()).add(row['question_id'])
        question = key[:2]
        if question in subsets and subsets[question] != row['subset']:
            raise ValueError(f'Inconsistent subset for paired question {question}.')
        subsets[question] = row['subset']
        converted.append(row)
    for benchmark in sorted({row['benchmark'] for row in converted}):
        reference = sets.get((benchmark, config['baseline']), set())
        if not reference:
            raise ValueError(f'No baseline observations in {benchmark}.')
        for method in sorted(allowed):
            observed = sets.get((benchmark, method), set())
            if observed != reference:
                raise ValueError(f'Pairing mismatch in {benchmark}/{method}: missing={sorted(reference-observed)[:8]}, extra={sorted(observed-reference)[:8]}. No automatic inner join.')
    return sorted(converted, key=lambda row: (row['benchmark'], row['question_id'], row['method']))


def load_dataset(args):
    config = validate_config(json.loads(args.config.read_text(encoding='utf-8')))
    with args.data.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('CSV requires a unique header row.')
        return validate_rows(list(reader), config), config


def groups(rows, include_all=False):
    output = []
    for benchmark in sorted({row['benchmark'] for row in rows}):
        selected = [row for row in rows if row['benchmark'] == benchmark]
        if include_all:
            output.append((f'{benchmark} / All', selected))
        for subset in sorted({row['subset'] for row in selected}):
            output.append((f'{benchmark} / {subset}', [row for row in selected if row['subset'] == subset]))
    return output


def paired_differences(rows, baseline, method):
    def index(label):
        selected = [row for row in rows if row['method'] == label]
        result = {(row['benchmark'], row['question_id']): row['score'] for row in selected}
        if len(result) != len(selected):
            raise ValueError('Duplicate pairing key.')
        return result
    left, right = index(baseline), index(method)
    if not left or left.keys() != right.keys():
        raise ValueError('Paired differences require matching nonempty question IDs.')
    return np.array([right[key] - left[key] for key in sorted(left)], dtype=float)


def bootstrap_ci(values, draws=3000, seed=20261116):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) == 0 or not np.isfinite(values).all():
        raise ValueError('Bootstrap requires a nonempty finite vector.')
    if not isinstance(draws, (int, np.integer)) or draws < 1:
        raise ValueError('Bootstrap draws must be a positive integer.')
    rng = np.random.default_rng(seed)
    means = np.empty(draws)
    batch_size = max(1, min(128, 1_000_000 // len(values)))
    for start in range(0, draws, batch_size):
        size = min(batch_size, draws - start)
        means[start:start + size] = values[rng.integers(0, len(values), (size, len(values)))].mean(axis=1)
    return tuple(float(x) for x in np.quantile(means, [.025, .975]))


def metric_info(metric):
    if metric not in METRICS:
        raise ValueError(f'Unknown cost metric {metric}.')
    return METRICS[metric]


def select_metric_cohort(rows, metric, policy='error'):
    metric_info(metric)
    if policy not in {'error', 'complete-case'}:
        raise ValueError('Missing-cost policy must be error or complete-case.')
    missing = {}
    for row in rows:
        if row.get(metric) is None:
            missing.setdefault((row['benchmark'], row['question_id']), []).append(row['method'])
    if missing and policy == 'error':
        examples = ', '.join(f'{b}/{q}: {sorted(ms)}' for (b, q), ms in list(sorted(missing.items()))[:5])
        raise ValueError(f'Missing {metric} for {len(missing)} paired questions ({examples}). Record measured values, or explicitly use --missing-cost complete-case; blanks are never zero.')
    kept = [row for row in rows if (row['benchmark'], row['question_id']) not in missing]
    before, after = {}, {}
    for label, source in [('before', rows), ('after', kept)]:
        target = before if label == 'before' else after
        for benchmark in sorted({row['benchmark'] for row in rows}):
            target[benchmark] = len({row['question_id'] for row in source if row['benchmark'] == benchmark})
    if not kept or any(n == 0 for n in after.values()):
        raise ValueError('No complete paired cost cohort remains in at least one benchmark.')
    audit = {'policy': policy, 'metric': metric, 'questions_before': before, 'questions_after': after,
             'excluded_question_count': len(missing),
             'excluded_questions': [{'benchmark': b, 'question_id': q, 'missing_methods': sorted(ms)} for (b, q), ms in sorted(missing.items())]}
    return kept, audit


def pareto_mask(cost, score):
    cost, score = np.asarray(cost, float), np.asarray(score, float)
    if cost.ndim != 1 or cost.shape != score.shape or len(cost) == 0 or not np.isfinite(cost).all() or not np.isfinite(score).all():
        raise ValueError('Pareto requires matching nonempty finite vectors.')
    if np.any(cost < 0):
        raise ValueError('Cost must be nonnegative.')
    return np.array([not np.any((cost <= cost[i]) & (score >= score[i]) & ((cost < cost[i]) | (score > score[i]))) for i in range(len(cost))])


def portable_input_reference(data_path, config_path):
    """Identify input bytes without recording the machine's absolute directory."""
    data = Path(data_path).resolve()
    for label, base in (('config_directory', Path(config_path).resolve().parent),
                        ('template_directory', HERE)):
        try:
            return data.relative_to(base).as_posix(), label
        except ValueError:
            pass
    # Inputs outside both roots remain identifiable by name and input_sha256.
    return data.name, 'filename_only'


def save_outputs(fig, args, stem, config, note, summary_rows, audit=None):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    badge = 'SYNTHETIC DEMO - not experimental results' if config['data_kind'] == 'synthetic' else 'USER-SUPPLIED MEASURED DATA'
    footer = badge + '\n' + '\n'.join(textwrap.wrap(note, width=125))
    fig.text(.5, .012, footer, ha='center', va='bottom', fontsize=7.2, color='#5C707B')
    for fmt in args.formats:
        metadata = {'Date': None} if fmt == 'svg' else ({'CreationDate': None, 'ModDate': None} if fmt == 'pdf' else {'Software': 'rerank-templates'})
        fig.savefig(args.output_dir / f'{stem}.{fmt}', bbox_inches='tight', facecolor='white', metadata=metadata)
    plt.close(fig)
    if not summary_rows:
        raise ValueError('No summary statistics were produced.')
    fields = list(dict.fromkeys(key for row in summary_rows for key in row))
    with (args.output_dir / f'{stem}_summary.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary_rows)
    input_csv, input_csv_base = portable_input_reference(args.data, args.config)
    provenance = {'template': stem, 'data_kind': config['data_kind'], 'config': config,
        'input_csv': input_csv, 'input_csv_base': input_csv_base,
        'input_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
        'config_file': args.config.name,
        'config_sha256': hashlib.sha256(args.config.read_bytes()).hexdigest(),
        'cost_metric': args.metric if stem != 'forest' else None,
        'bootstrap_resamples': args.bootstrap if stem in {'forest', 'pareto'} else None, 'seed': args.seed,
        'missing_cost_audit': audit, 'note': note,
        'environment': {'matplotlib': matplotlib.__version__, 'numpy': np.__version__}}
    (args.output_dir / f'{stem}_provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Rendered {stem}: {args.output_dir}')
