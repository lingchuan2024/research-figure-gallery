"""Generate one representative per chart type with multiple uses and source links."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.catalog_support import ROOT,load_catalog,source_inventory
from scripts.readme_notes import FIGURE_NOTES
from scripts.family_support import load_families

def source_line(item):
    if item['origin']=='paper':
        return f"来源：[{item['source_label']}]({item['source_url']})，{item['paper_version']}，{item['source_locator']}。"
    return f"图型参考：[{item['reference'].rstrip('/').split('/')[-1]}]({item['reference']})。"

def index_entries():
    """Read source inventories; generated dist reports are not prerequisites."""
    catalog,inventory=load_catalog(),source_inventory()
    template=Path('rerank_templates/2026-11-16')
    github=Path('github_references/2026-11-15')
    template_refs={r['template']:r for r in json.loads((ROOT/template/'sources.json').read_text())}
    entries=[]
    for number,(name,title) in enumerate([('forest','子集收益森林图'),('raincloud','分面耗时雨云图'),('pareto','质量—开销 Pareto 图')],1):
        entries.append(dict(code=f'T{number:02d}',category='templates',title=title,origin='合成模板',
            image=str(template/f'figures/{name}.png'),script=str(template/f'plot_{name}.py'),helper=str(template/'common.py'),
            inputs=[('逐题 CSV',str(template/'data/demo/observations.csv')),('配置',str(template/'config.json'))],status='本地可运行',
            reference=f"图型参考：[{template_refs[name]['repo']}]({template_refs[name]['image_url']})；本库独立实现，默认数据为合成示例。"))
    template_v2=Path('rerank_templates/2026-11-21')
    t2_specs=[
        ('T04','results_table','实测主结果表模板','observations.csv'),
        ('T05','paired','实测逐题配对比较模板','observations.csv'),
        ('T06','budget_curve','实测预算趋势曲线模板','budget_runs.csv'),
        ('T07','rank_transition','实测排名迁移热图模板','rank_transitions.csv'),
        ('T08','tool_composition','实测工具与文本组成模板','tool_calls.csv'),
        ('T09','trajectory','实测工具轨迹时间线模板','trajectories.csv'),
    ]
    for code,name,title,csv_name in t2_specs:
        entries.append(dict(code=code,category='templates',title=title,origin='合成模板',
            image=str(template_v2/f'figures/{name}.png'),script=str(template_v2/f'plot_{name}.py'),helper=str(template_v2/'common.py'),
            inputs=[('示例 CSV',str(template_v2/'data/demo'/csv_name)),('配置',str(template_v2/'config.json'))],status='本地可运行',
            reference='本库独立实现的实测数据契约模板（2026-11-21）；默认数据为合成示例，附带 `config.measured.example.json`。'))
    agentic_exp=Path('rerank_expansion/2026-11-21')
    a_specs=[
        ('A01','A01_iter_query_ablation','ITER 查询输入消融',['iter_query_ablation.csv'],'ITER','https://arxiv.org/abs/2608.27912','2608.27912v2','Table 3, p. 15'),
        ('A02','A02_iter_cross_agent','ITER 跨 Backbone 迁移与 V/S 转化',['iter_cross_agent.csv'],'ITER','https://arxiv.org/abs/2608.27912','2608.27912v2','Table 2, p. 14'),
        ('A03','A03_rarg_coarse_to_fine','RARG 粗到细相关性引导前沿',['rarg_main_bcplus.csv'],'RARG','https://arxiv.org/abs/2607.24223','2607.24223v2','Table 1, p. 7'),
        ('A04','A04_rarg_scope_heatmap','RARG 检索域排名命中热图',['rarg_scope_rank_heatmap.csv'],'RARG','https://arxiv.org/abs/2607.24223','2607.24223v2','Figure 3, p. 9'),
        ('A05','A05_indexact_context_tradeoff','IndexAct 上下文权衡与观察策略消融',['indexact_bcplus_main.csv','indexact_observation_ablation.csv'],'IndexAct','https://arxiv.org/abs/2610.07960','2610.07960v1','Tables 1-2, pp. 7-8'),
        ('A06','A06_rise_scaling_and_topk','RISE 10 倍扩容与 Top-K 消融',['rise_scaling_100k_1m.csv','rise_topk_ablation.csv'],'RISE','https://arxiv.org/abs/2606.06880','2606.06880v1','Tables 2-3, pp. 7-8'),
    ]
    for code,stem,title,csvs,src_lbl,src_url,ver,loc in a_specs:
        entries.append(dict(code=code,category='agentic_expansion',title=title,origin='论文数值重绘',
            image=str(agentic_exp/f'figures/{stem}.png'),script=str(agentic_exp/f'code/{stem}.py'),helper=str(agentic_exp/'plotlib.py'),
            inputs=[(c,str(agentic_exp/'data'/c)) for c in csvs],status='本地可运行',
            reference=f'来源：[{src_lbl}]({src_url})，{ver}，{loc}。'))
    for category,prefix in [('selected','M'),('supplement','S')]:
        for number,item in enumerate(catalog[category],1):
            raw={**inventory[item['id']],**item};script=Path(raw['script'])
            helper=script.parent.parent/'plotlib.py' if raw['origin']=='paper' else Path('gallerylib/__init__.py')
            entries.append(dict(code=f'{prefix}{number:02d}',category=category,title=raw['title'],image=raw['image'],
                script=raw['script'],helper=str(helper),origin='论文数值重绘' if raw['origin']=='paper' else '合成模板',
                inputs=[(Path(p).name,p) for p in raw['data']],status='本地可运行',reference=source_line(raw)))
    code_meta={}
    for name in ['effectiveness.json','efficiency.json']:
        for meta in json.loads((ROOT/github/'code_sections'/name).read_text()):
            if meta['id'] in code_meta:raise ValueError('Duplicate upstream code metadata: '+meta['id'])
            code_meta[meta['id']]={**meta,'metadata_file':str(github/'code_sections'/name)}
    for raw in json.loads((ROOT/github/'manifest.json').read_text())['figures']:
        if raw['id']=='G07':continue
        meta=code_meta[raw['id']]
        inputs=[('数据与环境',meta['metadata_file'])]
        inputs.extend((Path(s['local_file']).name,str(github/s['local_file'])) for s in meta.get('support_files',[]))
        entries.append(dict(code=raw['id'],category='github',title=raw['title'],origin='上游原图',
            image=str(github/raw['preview_local']),script=str(github/meta['code_file']),
            source=str(github/raw['source_local']),license=str(github/raw['license_local']),inputs=inputs,status='上游参考 · 未完整执行',
            reference=f"上游原图：[{raw['repo']}]({raw['image_url']})；许可：{raw['license']}。{raw['license_note']}"))
    if len(entries)!=45 or len({e['code'] for e in entries})!=45:raise ValueError('Expected 45 distinct figure index entries.')
    return entries



def write_index(entries, families):
    by_code={entry['code']:entry for entry in entries}
    def link(label,path):return f'[{label}](../{path})'
    text=f'''# 图型、代码与来源索引

[返回一图多用途图库](../README.md)

按 **{len(families)} 种图型**统一整理。每类在首页只显示一张代表图，下面的实现用于不同实验目的；不再按网站、论文或模板来源分组。

同类代码的指标、字段和统计方法可能不同。选择与实验目的相符的实现，不要仅改标题就套用原数值。执行状态与许可证逐项注明；所有示例均不属于我们的实测结果。

'''
    for family in families:
        text+=f'<a id="{family["id"].lower()}"></a>\n\n## {family["id"]} · {family["title"]}\n\n'
        text+=f'[代表图与多用途说明](../README.md#{family["id"].lower()})\n\n'
        for number,code in enumerate(family['members'],1):
            entry=by_code[code]
            marker=' · 当前代表图' if code==family['representative'] else ''
            text+=f'<a id="variant-{code.lower()}"></a>\n\n### {family["id"]}.{number} · {entry["title"]}{marker}\n\n'
            text+=link('主代码',entry['script'])
            if entry.get('helper'):text+=' · '+link('公共函数',entry['helper'])
            if entry.get('source'):text+=' · '+link('原始快照',entry['source'])+' · '+link('许可全文',entry['license'])
            text+='\n\n输入：'+' · '.join(link(label,path) for label,path in entry['inputs'])+'。\n\n'
            text+='适用用途：'+'；'.join(use['purpose'] for use in family['uses'] if code in use['source_codes'])+'。\n\n'
            text+=f"执行状态：{entry['status']}。{FIGURE_NOTES[code]['caution']}\n\n{entry['reference']}\n\n"
    text+='''## 复现与许可

完整构建保留每种用途所需的代码、数据和来源证据。运行报告在 `dist/figure_code_execution.json`，汇总文件为 `dist/图表汇总_2026-11-16.html`；其中可直接下载对应运行包。

本地实现的主脚本、公共函数和输入数据必须一起使用。未完整执行的参考源码需按其环境说明安装依赖。根目录 MIT 许可仅覆盖本库自主实现，原始素材按各自的许可使用。
'''
    (ROOT/'docs/FIGURE_INDEX.md').write_text(text,encoding='utf-8')


def write_entrypoint(entries, families):
    by_code={entry['code']:entry for entry in entries}
    text=f'''# Rerank 科研绘图：一图多用途

将相似画法合并为 **{len(families)} 种图型**，每类只保留一张代表图，在下方列出多个实验用途、论文位置和对应代码。出处统一放在每图的说明与[代码来源索引](docs/FIGURE_INDEX.md)中。

图中的数值来自合成示例或公开材料，均不是我们的实测结果。使用时选择对应用途的代码与数据格式；同一画法不意味着不同指标或分母可以混用。

[下载离线图册与完整代码包](https://github.com/lingchuan2024/research-figure-gallery/releases/latest) · [安装与构建](#quick-start) · [全部代码、输入与来源](docs/FIGURE_INDEX.md) · [逐题数据格式](rerank_templates/2026-11-16/DATA_FORMAT.md) · [目录说明](docs/STRUCTURE.md)

<a id="figure-catalog"></a>

## 按图型选择

| 图型 | 可回答的问题 |
| --- | --- |
'''
    for family in families:
        purposes='；'.join(use['purpose'] for use in family['uses'])
        text+=f"| [{family['id']} · {family['title']}](#{family['id'].lower()}) | {purposes} |\n"
    text+='\n'
    for family in families:
        entry=by_code[family['representative']]
        text+=f'''<a id="{family['id'].lower()}"></a>

## {family['id']} · {family['title']}

![{family['id']} {family['title']}：代表图]({entry['image']})

**这张图怎么看：** {FIGURE_NOTES[entry['code']]['reading']}

**可以用于：**

'''
        for use in family['uses']:
            code_links=' · '.join(f"[{by_code[c]['title']}](docs/FIGURE_INDEX.md#variant-{c.lower()})" for c in use['source_codes'])
            placement=use['placement'].rstrip(' \t\r\n。.;；')
            data=use['data'].rstrip(' \t\r\n。.;；')
            text+=f"- **{use['purpose']}** 建议位置：{placement}；需要：{data}。实现参考：{code_links}。\n\n"
        text+=f'''**使用边界：** {family['caution']}

<details>
<summary>代表图代码、数据与运行方法</summary>

[主代码]({entry['script']})'''
        if entry.get('helper'):text+=f" · [公共函数]({entry['helper']})"
        if entry.get('source'):text+=f" · [原始快照]({entry['source']}) · [许可全文]({entry['license']})"
        text+='\n\n输入：'+' · '.join(f'[{label}]({path})' for label,path in entry['inputs'])+'。\n\n'
        text+=f"执行状态：{entry['status']}。\n\n"
        if entry.get('helper'):
            text+=f"安装依赖后，在仓库根目录执行：\n\n```bash\npython {entry['script']} --output-dir dist/{family['id'].lower()} --formats png svg\n```\n\n"
        else:
            text+='运行环境与数据要求见上述“数据与环境”链接。参考源码尚未在本项目完整执行。\n\n'
        text+=f"[本图型的全部用途实现、数据与来源](docs/FIGURE_INDEX.md#{family['id'].lower()})\n\n</details>\n\n示例类型：{entry['origin']}。{entry['reference']}\n\n[返回图型目录](#figure-catalog)\n\n"
    text+='''<a id="quick-start"></a>

## 安装与构建

在仓库根目录使用 Python 3.10+：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/build_gallery.py --keep-existing-images
```

打开 `dist/图表汇总_2026-11-16.html`，可离线查看同一套一图多用途图库，并下载每种用途对应的代码和数据。完整发布包为 `dist/research-figure-gallery.zip`。也可从仓库 Actions 的成功构建中下载 Artifacts。

逐题输入见[数据格式（F03–F05）](rerank_templates/2026-11-16/DATA_FORMAT.md)与[扩展模板数据格式（F01/F02/F06–F09）](rerank_templates/2026-11-21/DATA_FORMAT.md)；2026 Agentic Rerank 文献重绘说明见[研究笔记](rerank_expansion/2026-11-21/RESEARCH_NOTES.md)；旧示例字段见[数据说明](data/README.md)。代码入口、执行状态与引用信息均在[统一索引](docs/FIGURE_INDEX.md)中。

图型与用途由 [figure_families.json](docs/catalog/figure_families.json) 统一维护，README、离线汇总和总览图由它生成。历史图片与来源证据用于代码溯源，不再作为多个独立图型重复展示。

自编代码采用 [MIT 许可](LICENSE)。来源图片、论文材料和原始源码保留各自许可，详见[来源说明](docs/REFERENCES.md)。

## 推荐外部科研图例仓库

- [faridrashidi/cnsplots](https://github.com/faridrashidi/cnsplots)（[示例图库](https://cnsplots.farid.one)）：面向 *Cell / Nature / Science* 风格的 Python 统计与机器学习绘图库，提供丰富的成品图例与配套代码（带显著性检验的箱线/小提琴/散点/柱状图、热图、ROC、混淆矩阵、多面板组合等），支持物理尺寸控制与 Illustrator 可编辑 SVG/PDF 导出。
- [ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers)：收录 *Nature Machine Intelligence*、ICML、NeurIPS、ECCV 等真实顶会/顶刊论文中的 Matplotlib 配图脚本与成品图（定量对比、组成拆解、趋势曲线、雷达图、后训练对比等），并附带科研绘图规范文档，适合 AI/ML 论文直接参考版式与配色。
'''
    (ROOT/'README.md').write_text(text,encoding='utf-8')


def write_documents():
    entries=index_entries()
    families=load_families({entry['code'] for entry in entries})
    (ROOT/'docs').mkdir(exist_ok=True)
    write_index(entries,families)
    write_entrypoint(entries,families)


if __name__=='__main__':write_documents()
