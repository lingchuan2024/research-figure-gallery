"""Render the checked-in examples and regenerate the usage-oriented README."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import hashlib
import json
import platform
import re
import subprocess
from gallerylib import ROOT
import matplotlib
import numpy
import PIL
from PIL import Image

def command(argv):
    result=subprocess.run([sys.executable,*map(str,argv)],cwd=ROOT,text=True,capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {argv}\n{result.stdout}\n{result.stderr}")
    return result

def readme(items):
    categories=list(dict.fromkeys(i['category']for i in items))
    conditions={
        '02_token_raincloud':'统计每题完整轨迹的主模型输入；只能说明这一项用量分布，不能代替含 reranker 开销的总成本。',
        '04_call_vs_output_share':'从实际日志统计显式调用和返回字符；后台自动重排另记，不能按显式调用为零就认定没有开销。',
        '07_rank_transition':'同一候选快照须有真实证据标注及完整前后排名；候选集外和跌出 Top-K 的证据均需保留。',
        '08_query_paired_comparison':'比较同题两种 query 时固定候选集、reranker、片段和返回预算，并用真实相关性标签计算指标。',
        '09_token_outcome_pairs':'按题号配对真实对错与 token；展示相关变化，不能据此单独归因于自主调用。',
        '12_accuracy_cost_frontier':'使用同一评测集和一致的实际成本口径，计入主模型及 reranker；禁止用合成 cost_units 解释真实效率。',
        '14_budget_accuracy':'每个预算下实际运行评测；事后截断完整轨迹不能代替独立预算实验。',
        '16_trajectory_timeline':'替换为可追溯的真实题号、动作和证据事件，并交代案例选择依据；单个案例不能证明整体提升。',
        '17_ablation_forest':'先核验工具实现，再一次只改变 query、snippet、范围或时机中的一项，其他条件固定并按题配对。',
        '19_results_table':'统一问题集、模型、返回字符预算和停止条件，接入真实评测结果；不能将演示排序当作当前实验结论。',
    }
    text=f'''# Research Figure Gallery · 科研图表画法示例

按用途收录 {len(items)} 张图，每张只展示一次，附仓库内绘图代码。

**当前仅为合成数据的画法演示，尚未接入并核验你们的真实实验。** 合成脚本预设了部分方法差异和趋势；出图成功与统计检查通过不能证明实验结论。下文列出的是使用条件，尚不是论文选图建议。

[图型来源](REFERENCES.md) · [数据与字段](data/README.md) · [视觉筛选记录](CURATION.md) · [缩略图速览](assets/overview.png)（[速览代码](scripts/contact_sheet.py)）

## 用途索引

| 用途 | 示例编号 |
| --- | --- |
'''
    for category in categories:
        group=[i for i in items if i['category']==category]
        text+='| '+category.split(' · ',1)[-1]+' | '+'、'.join(i['id'].split('_')[0]for i in group)+' |\n'
    text+='\n'
    for category in categories:
        text+=f"## {category}\n\n"
        for item in (i for i in items if i['category']==category):
            number=item['id'].split('_')[0]
            text+=f"### {number} · {item['title']}\n\n"
            text+=f"![{item['title']}（合成演示数据）]({item['image']})\n\n"
            text+=f"**代码：[{item['script']}]({item['script']})** · [SVG]({item['vector']}) · [图型参考]({item['reference']})\n\n"
            text+=f"适用条件：{conditions[item['id']]}\n\n"
    text+='''## 运行与替换数据

Python 3.10+；默认读取已提交的 `data/demo/`，输出到 `assets/`。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/build_gallery.py
```

只运行某张图，或使用自己的 CSV：

```bash
python examples/02_token_raincloud/plot.py
python examples/02_token_raincloud/plot.py --data-dir /path/to/csv --output-dir /path/to/figures --formats png svg pdf
```

输入文件映射见 [gallery.json](gallery.json)，CSV 字段和统计口径见 [data/README.md](data/README.md)。共享样式与统计函数位于 [gallerylib/__init__.py](gallerylib/__init__.py)。接入真实数据时需同时核验指标定义、对照条件、单位和脚注。

```bash
python -m unittest discover -s tests -v
python scripts/package_release.py
```

[verification.json](verification.json) 记录代码与数据检查、图片校验及 SHA-256，不验证实验是否成立。代码采用 [MIT 许可](LICENSE)；外部参考项目保留各自许可。
'''
    (ROOT/'README.md').write_text(text,encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--only',nargs='+');args=p.parse_args()
    items=json.loads((ROOT/'gallery.json').read_text());known={i['id']for i in items}
    if args.only and not set(args.only)<=known:p.error('Unknown example IDs: '+str(set(args.only)-known))
    for i in items:
        if args.only and i['id']not in args.only:continue
        command([i['script']]);print('Rendered '+i['id'],flush=True)
    for i in items:
        for key in ['image','vector']:
            if not (ROOT/i[key]).is_file():raise FileNotFoundError(i[key])
        with Image.open(ROOT/i['image'])as im:
            rgb=im.convert('RGB');extrema=rgb.getextrema()
            if min(im.size)<300 or all(lo==hi for lo,hi in extrema):raise ValueError('Empty or undersized image: '+i['image'])
    command(['scripts/contact_sheet.py']);readme(items)
    test=command(['-m','unittest','discover','-s','tests','-v']);match=re.search(r'Ran (\d+) tests?',test.stderr);test_count=int(match.group(1))if match else None
    paths=[p for p in ROOT.rglob('*')if p.is_file() and not any(s in {'.git','.cache','__pycache__','dist','.venv'}for s in p.relative_to(ROOT).parts)and p.name!='verification.json']
    verification={'status':'passed','examples':len(items),'unit_tests':test_count,'image_formats':['png','svg'],'python':platform.python_version(),'dependencies':{'matplotlib':matplotlib.__version__,'numpy':numpy.__version__,'Pillow':PIL.__version__},'checks':['unit tests','all manifest code/data links exist','all example PNG/SVG exist','PNG dimensions and nonconstant pixels'],'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(paths)}}
    (ROOT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n');print(f"Verified {len(items)} examples and {test_count} tests; README updated.")

if __name__=='__main__':main()
