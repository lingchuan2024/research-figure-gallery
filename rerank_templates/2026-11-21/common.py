"""Standalone CSV contracts, paired statistics, and portable provenance for F01/F02/F06/F07/F08/F09 templates."""
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

INK = '#243746'
MUTED = '#5C707B'
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
CONDITIONS = (
    'question_set',
    'generator_model',
    'retrieval_policy',
    'hardware',
    'concurrency',
    'stopping_rule',
    'run_selection',
)
DEFAULT_RANK_BINS = (
    ('1', 1, 1),
    ('2-5', 2, 5),
    ('6-10', 6, 10),
    ('11-100', 11, 100),
    ('101+', 101, math.inf),
)
DEFAULT_TOOL_COLORS = {
    'search': '#4C78A8',
    'bash': '#9FAAB5',
    'read': '#63ACA6',
    'rerank': '#E09A42',
    'answer': '#2E6F5E',
}


def setup(dpi=240):
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 9.5,
        'axes.titlesize': 11.5,
        'axes.titleweight': 'bold',
        'axes.labelsize': 9.5,
        'xtick.labelsize': 8.5,
        'ytick.labelsize': 8.5,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.edgecolor': '#98A5AB',
        'axes.labelcolor': INK,
        'text.color': INK,
        'xtick.color': INK,
        'ytick.color': INK,
        'axes.axisbelow': True,
        'grid.color': '#E5EAED',
        'grid.linewidth': 0.75,
        'legend.frameon': False,
        'savefig.dpi': dpi,
        'svg.fonttype': 'none',
        'svg.hashsalt': 'rerank-templates-20261121',
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
    })


def base_parser(stem, default_csv):
    parser = argparse.ArgumentParser(description=f'Render {stem} from validated CSV observations.')
    parser.add_argument('--data', type=Path, default=HERE / 'data/demo' / default_csv)
    parser.add_argument('--config', type=Path, default=HERE / 'config.json')
    parser.add_argument('--output-dir', type=Path, default=HERE / 'figures')
    parser.add_argument('--formats', nargs='+', choices=['png', 'svg', 'pdf'], default=['png', 'svg', 'pdf'])
    parser.add_argument('--bootstrap', type=int, default=3000)
    parser.add_argument('--seed', type=int, default=20261121)
    return parser


def finalize_args(parser, default_csv, argv=None):
    args = parser.parse_args(argv)
    if args.bootstrap < 200:
        parser.error('--bootstrap must be at least 200; default is 3000.')
    if args.seed < 0:
        parser.error('--seed must be nonnegative.')
    default_data = (HERE / 'data/demo' / default_csv).resolve()
    default_cfg = (HERE / 'config.json').resolve()
    custom = args.data.resolve() != default_data or args.config.resolve() != default_cfg
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
        if not isinstance(method, dict) or any(
            not isinstance(method.get(k), str) or not method[k].strip() for k in ('id', 'label', 'color')
        ):
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
            raise ValueError(f'score.{key} is required.')
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


def load_config(path: Path):
    return validate_config(json.loads(path.read_text(encoding='utf-8')))


def read_csv_rows(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f'{path.name}: CSV requires a unique header row.')
        rows = list(reader)
    if not rows:
        raise ValueError(f'{path.name}: input CSV has no rows.')
    return rows


def validate_observations(records, config):
    allowed = {m['id'] for m in config['methods']}
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
            if row['score'] not in {0.0, 1.0}:
                raise ValueError('Binary score must be exactly 0 or 1.')
            if row['status'] != 'complete' and row['score'] != 0.0:
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
            raise ValueError(f'Duplicate question/method key {key}.')
        seen.add(key)
        sets.setdefault((row['benchmark'], row['method']), set()).add(row['question_id'])
        qkey = key[:2]
        if qkey in subsets and subsets[qkey] != row['subset']:
            raise ValueError(f'Inconsistent subset for paired question {qkey}.')
        subsets[qkey] = row['subset']
        converted.append(row)
    for benchmark in sorted({r['benchmark'] for r in converted}):
        ref = sets.get((benchmark, config['baseline']), set())
        if not ref:
            raise ValueError(f'No baseline observations in {benchmark}.')
        for method in sorted(allowed):
            obs = sets.get((benchmark, method), set())
            if obs != ref:
                raise ValueError(
                    f'Pairing mismatch in {benchmark}/{method}: missing={sorted(ref - obs)[:6]}, extra={sorted(obs - ref)[:6]}. No automatic inner join.'
                )
    return sorted(converted, key=lambda r: (r['benchmark'], r['question_id'], r['method']))


def validate_budget_runs(records, config):
    allowed = {m['id'] for m in config['methods']}
    converted, seen, sets = [], set(), {}
    for line, raw in enumerate(records, 2):
        if None in raw:
            raise ValueError(f'CSV line {line}: extra values beyond the header.')
        row = dict(raw)
        for key in ('benchmark', 'question_id', 'method', 'status'):
            if row.get(key) is None or not str(row[key]).strip():
                raise ValueError(f'CSV line {line}: missing {key}.')
            row[key] = str(row[key]).strip()
        if row['method'] not in allowed:
            raise ValueError(f'Unknown method {row["method"]}.')
        if row['status'] not in {'complete', 'timeout', 'no_final', 'error'}:
            raise ValueError(f'Unsupported status {row["status"]}.')
        try:
            row['budget_value'] = float(row['budget_value'])
            row['score'] = float(row['score'])
        except (TypeError, ValueError) as exc:
            raise ValueError(f'CSV line {line}: budget_value and score must be numeric.') from exc
        if not math.isfinite(row['budget_value']) or row['budget_value'] <= 0:
            raise ValueError(f'CSV line {line}: budget_value must be finite and positive.')
        if not math.isfinite(row['score']) or not 0 <= row['score'] <= 1:
            raise ValueError(f'CSV line {line}: score must be finite and within [0,1].')
        if config['score']['kind'] == 'binary' and row['score'] not in {0.0, 1.0}:
            raise ValueError(f'CSV line {line}: binary score must be 0 or 1.')
        key = (row['benchmark'], row['budget_value'], row['question_id'], row['method'])
        if key in seen:
            raise ValueError(f'Duplicate budget run key {key}.')
        seen.add(key)
        sets.setdefault((row['benchmark'], row['budget_value'], row['method']), set()).add(row['question_id'])
        converted.append(row)
    for benchmark in sorted({r['benchmark'] for r in converted}):
        budgets = sorted({r['budget_value'] for r in converted if r['benchmark'] == benchmark})
        for bval in budgets:
            ref = sets.get((benchmark, bval, config['baseline']), set())
            if not ref:
                raise ValueError(f'No baseline rows for {benchmark} at budget={bval}.')
            for method in sorted(allowed):
                obs = sets.get((benchmark, bval, method), set())
                if obs != ref:
                    raise ValueError(f'Pairing mismatch in {benchmark} budget={bval} method={method}.')
    return converted


def validate_rank_transitions(records, config):
    allowed = {m['id'] for m in config['methods']}
    converted, seen = [], set()
    for line, raw in enumerate(records, 2):
        if None in raw:
            raise ValueError(f'CSV line {line}: extra values beyond header.')
        row = dict(raw)
        for key in ('benchmark', 'question_id', 'method', 'doc_id', 'rank_before', 'rank_after'):
            if row.get(key) is None or not str(row[key]).strip():
                raise ValueError(f'CSV line {line}: missing {key}.')
            row[key] = str(row[key]).strip()
        if row['method'] not in allowed:
            raise ValueError(f'Unknown method {row["method"]}.')
        for rkey in ('rank_before', 'rank_after'):
            if row[rkey].casefold() == 'outside':
                row[rkey] = None
            else:
                try:
                    val = int(row[rkey])
                except ValueError as exc:
                    raise ValueError(f'CSV line {line}: {rkey} must be positive integer or "outside".') from exc
                if val < 1:
                    raise ValueError(f'CSV line {line}: {rkey} must be >= 1.')
                row[rkey] = val
        rel = str(row.get('is_relevant', '1')).strip().lower()
        if rel not in {'0', '1', 'true', 'false'}:
            raise ValueError(f'CSV line {line}: is_relevant must be 0/1 or true/false.')
        row['is_relevant'] = rel in {'1', 'true'}
        key = (row['benchmark'], row['question_id'], row['method'], row['doc_id'])
        if key in seen:
            raise ValueError(f'Duplicate rank transition key {key}.')
        seen.add(key)
        converted.append(row)
    return converted


def validate_tool_calls(records, config):
    allowed = {m['id'] for m in config['methods']}
    converted, seen, qsets = [], set(), {}
    for line, raw in enumerate(records, 2):
        if None in raw:
            raise ValueError(f'CSV line {line}: extra values beyond header.')
        row = dict(raw)
        for key in ('benchmark', 'question_id', 'method', 'tool'):
            if row.get(key) is None or not str(row[key]).strip():
                raise ValueError(f'CSV line {line}: missing {key}.')
            row[key] = str(row[key]).strip()
        if row['method'] not in allowed:
            raise ValueError(f'Unknown method {row["method"]}.')
        for nkey in ('calls', 'returned_chars'):
            try:
                val = float(row[nkey])
            except (TypeError, ValueError) as exc:
                raise ValueError(f'CSV line {line}: {nkey} must be numeric.') from exc
            if not math.isfinite(val) or val < 0 or val != int(val):
                raise ValueError(f'CSV line {line}: {nkey} must be a nonnegative integer.')
            row[nkey] = int(val)
        key = (row['benchmark'], row['question_id'], row['method'], row['tool'])
        if key in seen:
            raise ValueError(f'Duplicate tool call key {key}.')
        seen.add(key)
        qsets.setdefault((row['benchmark'], row['method']), set()).add(row['question_id'])
        converted.append(row)
    for benchmark in sorted({r['benchmark'] for r in converted}):
        ref = qsets.get((benchmark, config['baseline']), set())
        if not ref:
            raise ValueError(f'No baseline tool rows in {benchmark}.')
        for method in sorted(allowed):
            obs = qsets.get((benchmark, method), set())
            if obs != ref:
                raise ValueError(f'Tool-call question pairing mismatch in {benchmark}/{method}.')
    return converted


def validate_trajectories(records, config):
    allowed = {m['id'] for m in config['methods']}
    valid_flags = {'none', 'first_evidence', 'rerank_hit', 'final_correct', 'final_wrong'}
    converted, seen = [], set()
    for line, raw in enumerate(records, 2):
        if None in raw:
            raise ValueError(f'CSV line {line}: extra values beyond header.')
        row = dict(raw)
        for key in ('case_id', 'method', 'tool'):
            if row.get(key) is None or not str(row[key]).strip():
                raise ValueError(f'CSV line {line}: missing {key}.')
            row[key] = str(row[key]).strip()
        if row['method'] not in allowed:
            raise ValueError(f'Unknown method {row["method"]}.')
        try:
            row['turn'] = int(row['turn'])
        except (TypeError, ValueError) as exc:
            raise ValueError(f'CSV line {line}: turn must be a positive integer.') from exc
        if row['turn'] < 1:
            raise ValueError(f'CSV line {line}: turn must be >= 1.')
        flag = str(row.get('event_flag', 'none') or 'none').strip()
        if flag not in valid_flags:
            raise ValueError(f'CSV line {line}: unsupported event_flag {flag}.')
        row['event_flag'] = flag
        row['note'] = str(row.get('note', '') or '').strip()
        key = (row['case_id'], row['method'], row['turn'])
        if key in seen:
            raise ValueError(f'Duplicate trajectory turn key {key}.')
        seen.add(key)
        converted.append(row)
    return sorted(converted, key=lambda r: (r['case_id'], r['method'], r['turn']))


def wilson_interval(successes, total, z=1.959963984540054):
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError('Require 0 <= successes <= total and total > 0.')
    p = successes / total
    den = 1.0 + z * z / total
    mid = (p + z * z / (2.0 * total)) / den
    half = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / den
    return max(0.0, mid - half), min(1.0, mid + half)


def bootstrap_ci(values, draws=3000, seed=20261121):
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or len(arr) == 0 or not np.isfinite(arr).all():
        raise ValueError('Bootstrap requires a nonempty finite vector.')
    rng = np.random.default_rng(seed)
    means = np.empty(draws)
    batch = max(1, min(128, 1_000_000 // len(arr)))
    for start in range(0, draws, batch):
        size = min(batch, draws - start)
        means[start:start + size] = arr[rng.integers(0, len(arr), (size, len(arr)))].mean(axis=1)
    return tuple(float(x) for x in np.quantile(means, [0.025, 0.975]))


def normalize_rows(matrix):
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2 or np.any(arr < 0):
        raise ValueError('Expected a nonnegative 2D count matrix.')
    denom = arr.sum(axis=1, keepdims=True)
    return np.divide(arr, denom, out=np.full_like(arr, np.nan), where=denom > 0)


def portable_input_reference(data_path, config_path):
    data = Path(data_path).resolve()
    for label, base in (('config_directory', Path(config_path).resolve().parent), ('template_directory', HERE)):
        try:
            return data.relative_to(base).as_posix(), label
        except ValueError:
            pass
    return data.name, 'filename_only'


def save_outputs(fig, args, stem, config, note, summary_rows, extra_provenance=None):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    badge = 'SYNTHETIC DEMO - not experimental results' if config['data_kind'] == 'synthetic' else 'USER-SUPPLIED MEASURED DATA'
    footer = badge + '\n' + '\n'.join(textwrap.wrap(note, width=128))
    fig.text(0.5, 0.012, footer, ha='center', va='bottom', fontsize=7.2, color=MUTED)
    for fmt in args.formats:
        if fmt == 'svg':
            metadata = {'Date': None}
        elif fmt == 'pdf':
            metadata = {'CreationDate': None, 'ModDate': None}
        else:
            metadata = {'Software': 'rerank-templates-20261121'}
        fig.savefig(args.output_dir / f'{stem}.{fmt}', bbox_inches='tight', facecolor='white', metadata=metadata)
    plt.close(fig)

    if not summary_rows:
        raise ValueError('No summary statistics were produced.')
    fields = list(dict.fromkeys(k for row in summary_rows for k in row))
    with (args.output_dir / f'{stem}_summary.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary_rows)

    input_csv, input_csv_base = portable_input_reference(args.data, args.config)
    provenance = {
        'template': stem,
        'data_kind': config['data_kind'],
        'config': config,
        'input_csv': input_csv,
        'input_csv_base': input_csv_base,
        'input_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
        'config_file': args.config.name,
        'config_sha256': hashlib.sha256(args.config.read_bytes()).hexdigest(),
        'bootstrap_resamples': args.bootstrap,
        'seed': args.seed,
        'note': note,
        'environment': {'matplotlib': matplotlib.__version__, 'numpy': np.__version__},
    }
    if extra_provenance:
        provenance.update(extra_provenance)
    (args.output_dir / f'{stem}_provenance.json').write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    print(f'Rendered {stem}: {args.output_dir}')
