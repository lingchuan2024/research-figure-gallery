"""Attach inspectable source, data previews and portable per-figure code bundles."""
from pathlib import Path
import csv
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GITHUB = ROOT / 'github_references/2026-11-15'
DIST = ROOT / 'dist/figure_code'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive_bytes(files, prefix):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for name, value in sorted(files.items()):
            path = Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError(f'Unsafe bundle path: {name}')
            entry = zipfile.ZipInfo(str(Path(prefix) / path), date_time=(2026, 11, 16, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, value if isinstance(value, bytes) else value.encode('utf-8'))
    return stream.getvalue()


def preview_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    result = io.StringIO()
    writer = csv.DictWriter(result, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows[:3])
    return {'path': str(path.relative_to(ROOT)), 'columns': fields, 'row_count': len(rows),
            'preview': result.getvalue(), 'sha256': digest(path.read_bytes())}


def local_section(item):
    script = ROOT / item['script']
    files = {item['script']: script.read_bytes(), 'requirements-lock.txt': (ROOT / 'requirements-lock.txt').read_bytes(),
             'LICENSE': (ROOT / 'LICENSE').read_bytes()}
    source = script.read_text(encoding='utf-8')
    data = [preview_csv(ROOT / name) for name in item['data']]
    for name in item['data']:
        files[name] = (ROOT / name).read_bytes()
    if item['category'] == 'templates':
        helper = script.parent / 'common.py'
        for name in ['config.json', 'config.measured.example.json', 'DATA_FORMAT.md']:
            path = script.parent / name
            files[str(path.relative_to(ROOT))] = path.read_bytes()
        input_note = '逐题 CSV；同一 benchmark 下按 question_id 与 method 严格配对。默认示例为合成数据。字段定义见包内 DATA_FORMAT.md；配置与数据通过 --config / --data 替换。'
    elif script.parts[-3] == 'examples':
        helper = ROOT / 'gallerylib/__init__.py'
        files['data/README.md'] = (ROOT / 'data/README.md').read_bytes()
        input_note = '合成示例 CSV，字段与粒度见包内 data/README.md。方法集合与颜色在 gallerylib 中定义；真实数据使用 --data-dir 指向同名 CSV 所在目录。'
    else:
        helper = script.parent.parent / 'plotlib.py'
        input_note = 'CSV 保存来源论文的公开汇总数值，通常一行对应表格中的一个实验条件；不是逐题观测。保持字段、单位、方法名与脚本一致，使用 --data-dir 替换数据目录。'
    helper_rel = str(helper.relative_to(ROOT))
    files[helper_rel] = helper.read_bytes()
    entry = item['script']
    runner = f'''"""Run the bundled figure without requiring the parent repository."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
if __name__ == '__main__':
    subprocess.run([sys.executable, str(ROOT / {entry!r}), '--output-dir', str(ROOT / 'output'), *sys.argv[1:]], cwd=ROOT, check=True)
'''
    files['run.py'] = runner
    fields_text = '\n\n'.join(f'### {Path(d["path"]).name}\n\n{d["row_count"]} 行。字段：' + '、'.join(f'`{c}`' for c in d['columns']) + '\n\n```csv\n' + d['preview'] + '```' for d in data)
    files['INPUT_FORMAT.md'] = f'# {item["title"]}：输入数据\n\n{input_note}\n\n{fields_text}\n\n{item.get("limits", "")}\n'
    files['README.md'] = f'''# {item['code']} · {item['title']}

本包包含对应图的完整主脚本、公共函数、实际输入 CSV、依赖与许可。代码与既有实现一致，未改绘图逻辑。

## 运行

在解压后的本包根目录，Python 3.10+：

```bash
python -m pip install -r requirements-lock.txt
python run.py --formats png svg
```

输出在本包 `output/`。`run.py` 将参数传给主脚本；查看选项：`python run.py --help`。R01–R06 只支持 PNG/SVG，其余实现的具体格式以 `--help` 为准。

## 文件

- 主脚本：`{entry}`
- 公共函数：`{helper_rel}`
- 输入格式：`INPUT_FORMAT.md`
- 输入文件：{', '.join('`' + d['path'] + '`' for d in data)}

{input_note}

数据类型：{item['badge']}。{item['purpose']}

使用边界：{item.get('limits', '')}

来源：[{item['source_label']}]({item['source_url']})。{item.get('source_locator', '')}

本包主脚本是本库实现；文献图是公开数值重绘，演示数据不是我们的实验结果。
'''
    return {'language': 'python', 'kind': 'local', 'text': source, 'filename': script.name,
        'main_path': item['script'], 'code_sha256': digest(script.read_bytes()),
        'helpers': [{'path': helper_rel, 'text': helper.read_text(), 'sha256': digest(helper.read_bytes())}],
        'dependencies': ['matplotlib==3.10.8', 'numpy==2.1.2', 'Pillow==11.0.0'],
        'input_format': input_note, 'inputs': data,
        'command': 'python -m pip install -r requirements-lock.txt\npython run.py --formats png svg',
        'status': '本地实现 · 独立运行包', 'execution_status': 'local_bundle_prepared',
        'notes': '下载运行包包含公共函数和数据；单独复制主脚本时需要保留对应目录结构。',
        'files': files}


def upstream_sections():
    result = {}
    for name in ['effectiveness.json', 'efficiency.json']:
        for entry in json.loads((GITHUB / 'code_sections' / name).read_text()):
            if entry['id'] in result:
                raise ValueError('Duplicate upstream code entry')
            result[entry['id']] = entry
    if set(result) != {f'G{i:02d}' for i in range(1, 9)}:
        raise ValueError('All eight GitHub figures require a code section.')
    return result


def github_section(item, meta, reference):
    code_path = GITHUB / meta['code_file']
    source_path = GITHUB / reference['source_local']
    if meta.get('code_sha256') and digest(code_path.read_bytes()) != meta['code_sha256']:
        raise ValueError(f'Changed extracted code: {meta["id"]}')
    if digest(source_path.read_bytes()) != reference['source_sha256']:
        raise ValueError(f'Changed upstream snapshot: {meta["id"]}')
    code_archive_path = meta.get('code_archive_path', meta['code_file'])
    working = meta.get('working_directory', '.')
    files = {code_archive_path: code_path.read_bytes(),
             'upstream/' + source_path.name: source_path.read_bytes(),
             'UPSTREAM_LICENSE.txt': (GITHUB / reference['license_local']).read_bytes(),
             'PROVENANCE.json': json.dumps(meta, ensure_ascii=False, indent=2) + '\n'}
    support_inputs = []
    for support in meta.get('support_files', []):
        path = GITHUB / support['local_file']
        if support.get('sha256') and digest(path.read_bytes()) != support['sha256']:
            raise ValueError(f'Changed support data: {path}')
        files[support['archive_path']] = path.read_bytes()
        if path.suffix == '.csv':
            support_inputs.append(preview_csv(path))
    for directory in meta.get('create_directories', []):
        files[str(Path(directory) / '.keep')] = ''
    extraction = meta.get('extraction', meta.get('provenance', ''))
    notes = meta.get('notes', '')
    instructions = meta['run_instructions']
    dep_text = '\n'.join('- ' + dep for dep in meta['dependencies'])
    files['DEPENDENCIES.md'] = f'# 上游依赖\n\n{dep_text}\n\n{instructions}\n\n未在当前环境安装或运行上游依赖；原图仍使用固定 commit 的仓库原件。\n'
    files['README.md'] = f'''# {item['code']} · {item['title']}：上游代码参考

对应代码：`{code_archive_path}`。原始源码快照在 `upstream/`。代码提取自图的固定版本来源，保留原作者许可证；必要的导入、出图开关或路径适配在代码和下文说明。

**执行状态：上游示例，未在本项目运行；不能将原图称为本地重跑结果。**

## 环境与输入

{dep_text}

{meta['input_format']}

## 运行说明

{instructions}

建议工作目录：`{working}`。具体入口见上述说明，Python/R 依赖与上游版本保持一致。

## 来源与提取

[{reference['repo']}]({reference['source_url']})，commit `{reference['commit']}`。

{extraction}

{notes}

许可：{reference['license']}。{reference['license_note']}

{reference['license_url']}
'''
    return {'language': meta['language'], 'kind': 'upstream', 'text': code_path.read_text(),
            'filename': code_path.name, 'main_path': str(code_path.relative_to(ROOT)),
            'code_sha256': digest(code_path.read_bytes()), 'helpers': [],
            'dependencies': meta['dependencies'], 'input_format': meta['input_format'], 'inputs': support_inputs,
            'command': instructions, 'status': '上游对应示例 · 未在本项目执行',
            'execution_status': 'upstream_not_executed',
            'notes': str(extraction) + '\n' + str(notes), 'files': files}


def attach_code_sections(figures):
    DIST.mkdir(parents=True, exist_ok=True)
    upstream = upstream_sections()
    refs = {r['id']: r for r in json.loads((GITHUB / 'manifest.json').read_text())['figures']}
    receipt_path = ROOT / 'dist/figure_code_execution.json'
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    previous = {entry['id']: entry for entry in receipt.get('entries', [])}
    index = []
    all_files = {}
    for item in figures:
        code = github_section(item, upstream[item['code']], refs[item['code']]) if item['category'] == 'github' else local_section(item)
        prefix = item['id']
        archive = archive_bytes(code.pop('files'), prefix)
        target = DIST / f'{item["id"]}.zip'
        target.write_bytes(archive)
        code['bundle_sha256'] = digest(archive)
        code['bundle_bytes'] = archive
        code['bundle_filename'] = target.name
        code['bundle_path'] = str(target.relative_to(ROOT))
        old = previous.get(item['id'], {})
        if code['kind'] == 'local' and old.get('status') == 'passed' and old.get('bundle_sha256') == code['bundle_sha256']:
            code['status'] = '已独立运行验证 · PNG / SVG'
            code['execution_status'] = 'local_bundle_executed'
        item['code_section'] = code
        all_files[target.name] = archive
        index.append({'id': item['id'], 'code': item['code'], 'title': item['title'], 'kind': code['kind'],
            'main_path': code['main_path'], 'code_sha256': code['code_sha256'],
            'bundle_path': code['bundle_path'], 'bundle_sha256': code['bundle_sha256'],
            'execution_status': code['execution_status'], 'language': code['language']})
    all_files['index.json'] = json.dumps(index, ensure_ascii=False, indent=2) + '\n'
    all_files['README.md'] = '# 34 张图表的代码与数据\n\n每张图各有一个 ZIP。T/M/S 开头的页面编号对应26个本地实现包，含运行入口、公共函数、CSV与依赖；G01–G08对应上游源码参考包，未在本项目执行。请先阅读每包README。\n\n按 index.json 的 title/id 查找对应压缩包。原图和论文数值来源见汇总HTML。\n'
    combined = archive_bytes(all_files, 'all-figure-code')
    (DIST / 'all-figure-code.zip').write_bytes(combined)
    manifest = {'figures': len(index), 'local_bundles': sum(i['kind'] == 'local' for i in index),
                'upstream_source_bundles': sum(i['kind'] == 'upstream' for i in index),
                'all_bundle': 'dist/figure_code/all-figure-code.zip', 'all_bundle_sha256': digest(combined), 'entries': index}
    (ROOT / 'dist/figure_code_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest, combined
