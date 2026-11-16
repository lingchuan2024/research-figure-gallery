"""Generate the illustrated README, curated gallery, and complete code index."""
from pathlib import Path
import json
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.catalog_support import ROOT,load_catalog,source_inventory,selected_entries
from scripts.readme_notes import FIGURE_NOTES

def source_line(item):
    if item['origin']=='paper':
        return f"来源：[{item['source_label']}]({item['source_url']})，{item['paper_version']}，{item['source_locator']}。"
    return f"图型参考：[{item['reference'].rstrip('/').split('/')[-1]}]({item['reference']})。"

def write_gallery_and_supplement():
    items=selected_entries();catalog=load_catalog();inventory=source_inventory();sections=list(dict.fromkeys(i['section']for i in items))
    paper_count=sum(i['origin']=='paper'for i in items);template_count=len(items)-paper_count
    text=f'''# 精选图表：完整说明

[返回仓库首页](README.md) · [全部 34 图与代码](docs/FIGURE_INDEX.md) · [补充索引](SUPPLEMENT.md)

面向 search / rerank / 自主工具调用实验，按论文要回答的问题精选 {len(items)} 张图。每张图附预览、可运行代码、输入数据和来源。

**文献数据重绘**（{paper_count} 张）使用来源论文的公开数值；**合成数据模板**（{template_count} 张）仅用于展示画法。全部脚本由本仓库实现，图中数值均不属于我们的实验结果。

完整构建生成 `dist/图表汇总_2026-11-16.html`，内嵌 34 张图及每图代码包，可离线阅读和下载。26 个本地实现包由构建流程独立执行验证；8 个上游代码参考包未在本项目完整执行。

[补充索引与筛选理由](SUPPLEMENT.md) · [Deep Research 论文分析](paper_expansion/2026-11-01/RESEARCH_NOTES.md) · [Rerank 论文与实验契合分析](rerank_expansion/2026-11-15/RESEARCH_NOTES.md)

**独立参考文档：**[GitHub 科研绘图原图与代码](github_references/2026-11-15/GitHub科研绘图参考.md)。另收录 8 个仓库的 8 张原始示例，按 rerank 的实验问题说明用途，不计入本图库的 23 张图。构建后的独立 HTML 位于 `dist/GitHub科研绘图参考.html`。最新[去重记录](curation/2026-11-15-dedup/README.md)列出删除项与保留理由。

**可运行的 Rerank 实验模板：**[使用指南与三图预览](rerank_templates/2026-11-16/README.md) · [逐题 CSV 格式与真实日志映射](rerank_templates/2026-11-16/DATA_FORMAT.md)。将森林图、雨云图和 Pareto 图做成独立脚本；一份 CSV + JSON 配置即可输出 PNG/SVG/PDF、绘图数值和样本筛选记录。

## 按论文用途选图

| 论文用途 | 图号 |
| --- | --- |
'''
    for section in sections:
        numbers='、'.join(f"{i['number']:02d}"for i in items if i['section']==section)
        text+=f"| {section.split('、',1)[-1]} | {numbers} |\n"
    text+='\n实验比较应统一问题集、模型和停止条件。这里的“100 字符”指 search 与 rerank **返回给模型的长度预算**；主模型输入、检索暴露文本、reranker 开销需分别统计。以下是选图和迁移条件，不预设方法优劣。\n\n'
    for section in sections:
        text+=f'## {section}\n\n'
        for item in (i for i in items if i['section']==section):
            badge='文献数据重绘'if item['origin']=='paper'else'合成数据模板'
            text+=f"### {item['number']:02d} · {item['title']}\n\n![{item['title']}（{badge}）]({item['image']})\n\n"
            data_links='、'.join(f"[{Path(p).name}]({p})"for p in item['data'])
            text+=f"**{badge}** · [代码]({item['script']}) · {data_links} · [SVG]({item['vector']})\n\n"
            text+=item['purpose']+'\n\n'+source_line(item)+'\n\n'
    text+='''## 运行与替换数据

Python 3.10+。图片和 CSV 已存入仓库；更新目录与校验时保留已有图片：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/build_gallery.py --keep-existing-images
```

单图脚本均支持 `--data-dir`、`--output-dir` 和 `--formats`。建议输出到单独目录：

```bash
# 模板示例
python examples/08_query_paired_comparison/plot.py --data-dir data/demo --output-dir dist/query-pairs
# 文献数值重绘
python paper_expansion/2026-11-01/code/N02_failure_hierarchy.py --output-dir dist/failure-hierarchy --formats png svg
# 本轮 Rerank 文献图重建与目录验证
python rerank_expansion/2026-11-15/build.py
```

模板字段定义见 [数据说明](data/README.md)；文献数值的原表、页码与文件校验信息见 [Deep Research 来源审计](paper_expansion/2026-11-01/data_provenance.json)和 [Rerank 来源审计](rerank_expansion/2026-11-15/data_provenance.json)。接入真实实验时重新核验指标、分母、配对关系和脚注。

```bash
python -m unittest discover -s tests -v
python scripts/package_release.py
```

## 目录与维护

- [catalog.json](catalog.json)：主图库的顺序、分类与补充条目；本文由它与来源清单统一生成。
- `examples/`、`paper_expansion/2026-11-01/code/`、`rerank_expansion/2026-11-15/code/`：实际绘图脚本；`gallery.json` 和各文献 `manifest.json` 保存源文件映射。
- [SUPPLEMENT.md](SUPPLEMENT.md)：未进入主图库的图及理由，图片与代码保留。
- `dist/verification.json`：完整构建生成的文件摘要、代码与目录检查记录；不验证实验结论。

本仓库自编代码采用 [MIT 许可](LICENSE)。文献重绘保留论文署名与出处；独立 GitHub 参考目录中的原图和源码保留各自的上游许可证。参考项目的完整说明见 [REFERENCES.md](REFERENCES.md)。
'''
    # The detailed document moved one directory deeper; keep every local link valid.
    text=re.sub(r'(?<=\]\()([^)]*)(?=\))',lambda m:m[0] if m[0].startswith(('https:','http:','#')) else '../'+m[0],text)
    (ROOT/'docs').mkdir(exist_ok=True)
    (ROOT/'docs/GALLERY.md').write_text(text,encoding='utf-8')
    supplement=f'''# 补充索引与筛选理由

[返回仓库首页](README.md) · [全部 34 图与代码](docs/FIGURE_INDEX.md) · [精选图文](docs/GALLERY.md)

主图库按实验契合度、可读性和信息互补性，从 {len(inventory)} 张中精选 {len(items)} 张。以下 {len(catalog['supplement'])} 张适合后续专项实验或附录，当前不重复展示大图。全部图片、代码及数据保留，随时可复用。

| 图表 | 暂不进入主图库的原因 | 文件 |
| --- | --- | --- |
'''
    for item in catalog['supplement']:
        raw=inventory[item['id']]
        supplement+=f"| {item['title']} | {item['reason']} | [图片]({raw['image']}) · [代码]({raw['script']}) · [数据]({raw['data'][0]}) |\n"
    supplement+=f'\n筛选针对图的表达与当前实验用途，没有按结果方向筛样本或改变数值。主图库的 {len(items)} 张按统一用途组织，数据来源类型在每图旁注明；不同论文分数不能合并排名。\n'
    (ROOT/'SUPPLEMENT.md').write_text(supplement,encoding='utf-8')

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
        meta=code_meta[raw['id']]
        inputs=[('数据与环境',meta['metadata_file'])]
        inputs.extend((Path(s['local_file']).name,str(github/s['local_file'])) for s in meta.get('support_files',[]))
        entries.append(dict(code=raw['id'],category='github',title=raw['title'],origin='上游原图',
            image=str(github/raw['preview_local']),script=str(github/meta['code_file']),
            source=str(github/raw['source_local']),license=str(github/raw['license_local']),inputs=inputs,status='上游参考 · 未完整执行',
            reference=f"上游原图：[{raw['repo']}]({raw['image_url']})；许可：{raw['license']}。{raw['license_note']}"))
    if len(entries)!=34 or len({e['code'] for e in entries})!=34:raise ValueError('Expected 34 distinct figure index entries.')
    return entries


def write_index(entries):
    def link(label,path):return f'[{label}](../{path})'
    text='''# 34 图与全部代码索引

[返回仓库首页](../README.md) · [15 图完整说明](GALLERY.md) · [补充理由](../SUPPLEMENT.md)

本页覆盖 **34 张图：26 个本地可运行实现、8 个上游代码参考**。编号与离线 HTML 一致。点击图名查看规范预览；每行列出主代码及运行所需的公共函数、数据或环境说明。

完整构建会生成并独立执行 26 个本地代码包。8 个上游参考包保留提取代码、原始快照和许可证，未在本项目完整执行，不保证在当前依赖下复现原图。不要把上游图片当作本地重跑结果。

构建后打开 `dist/图表汇总_2026-11-16.html`，可离线阅读和下载逐图代码包；`dist/research-figure-gallery.zip` 是完整发布包。构建产物不会纳入 Git，需在本地生成或从 GitHub Actions 下载。运行状态与环境见 `dist/figure_code_execution.json`。

'''
    for category,title in [('templates','可运行的 Rerank 模板 · 3 张'),('selected','精选图库 · 15 张'),('supplement','补充图库 · 8 张'),('github','GitHub 原图参考 · 8 张')]:
        text+=f'## {title}\n\n| 编号 | 图表 / 数据类型 | 代码 | 输入与说明 | 状态 |\n| --- | --- | --- | --- | --- |\n'
        for e in (item for item in entries if item['category']==category):
            code=link('主代码',e['script'])
            if e.get('helper'):code+=' · '+link('公共函数',e['helper'])
            if e.get('source'):code+=' · '+link('原始快照',e['source'])+' · '+link('许可',e['license'])
            inputs=' · '.join(link(label,path) for label,path in e['inputs'])
            title_link=link(e['title'].replace('|','\\|'),e['image'])
            text+=f"| {e['code']} | {title_link}<br>{e['origin']} | {code} | {inputs} | {e['status']} |\n"
        text+='\n'
    text+='''## 使用边界

- T01–T03 共享逐题 CSV 与 JSON 配置；见[字段契约](../rerank_templates/2026-11-16/DATA_FORMAT.md)。
- M/S 中的论文数值来自公开表格，不能据此补造逐题分布；合成数据仅展示画法。
- G03 原图显示模拟数据的平均百分位秩；G08 图像与代码许可不同，详见[上游参考文档](../github_references/2026-11-15/GitHub科研绘图参考.md)。
- 上游源码快照与许可证是来源材料，不能作为缓存删除。索引由 `catalog.json`、来源 manifest 和 `code_sections` 元数据生成。
'''
    (ROOT/'docs/FIGURE_INDEX.md').write_text(text,encoding='utf-8')


def write_entrypoint(entries):
    if set(FIGURE_NOTES)!={entry['code'] for entry in entries}:
        raise ValueError('Every README figure requires its own explanation and placement advice.')
    text='''# Rerank Research Figure Gallery

面向 search、rerank 与自主工具调用实验的科研绘图参考库。本页逐张展示 **34 张图**，说明**怎么看、适合放在论文哪里、需要什么数据，以及对应代码**。

[全部代码索引](docs/FIGURE_INDEX.md) · [精选图与研究问题](docs/GALLERY.md) · [Rerank 模板使用指南](rerank_templates/2026-11-16/README.md) · [安装与构建](#quick-start)

其中 26 个是本地可运行实现；8 个是 GitHub 上游原图与代码参考，**未在本项目完整执行**。每图标明论文数值、合成示例或上游示例；这些数值均不是我们的实测结果。论文位置是根据图所回答的问题给出的建议，最终取决于真实实验设计与结果。

如果先准备 rerank 论文的三张核心实验图，可从 [T01 子集收益](#t01)、[T02 耗时分布](#t02)、[T03 质量与开销](#t03) 开始；是否采用应由可用数据和论文主张决定。

<a id="figure-catalog"></a>

## 图表目录

'''
    categories=[('templates','可运行的 Rerank 模板',3),('selected','精选图库',15),
                ('supplement','补充图库',8),('github','GitHub 原图参考',8)]
    for category,title,count in categories:
        links=' · '.join(f"[{e['code']} {e['title']}](#{e['code'].lower()})" for e in entries if e['category']==category)
        text+=f'**[{title} · {count} 张](#{category})**\n\n{links}\n\n'
    for category,title,count in categories:
        text+=f'<a id="{category}"></a>\n\n## {title} · {count} 张\n\n'
        for entry in (e for e in entries if e['category']==category):
            note=FIGURE_NOTES[entry['code']]
            text+=f'''<a id="{entry['code'].lower()}"></a>

### {entry['code']} · {entry['title']}

**{entry['origin']} · {entry['status']}**

![{entry['code']} {entry['title']}（{entry['origin']}）]({entry['image']})

**这张图怎么看：** {note['reading']}

**适合放在论文哪里：** {note['placement']}

**换成我们的实验需要：** {note['data_requirement']}

**使用边界：** {note['caution']}

<details>
<summary>代码、数据与复现</summary>

[主代码]({entry['script']})'''
            if entry.get('helper'):
                text+=f" · [公共函数]({entry['helper']})"
            if entry.get('source'):
                text+=f" · [上游源码快照]({entry['source']}) · [许可全文]({entry['license']})"
            text+='\n\n输入：'+' · '.join(f'[{label}]({path})' for label,path in entry['inputs'])+'。\n\n'
            if entry['category']=='github':
                text+='上游 Python / R 环境、支持数据与运行说明见上述“数据与环境”链接；本库仅核对与保存参考源码，原图不代表本地重跑结果。\n\n'
            else:
                text+=f"安装下方依赖后，在仓库根目录执行：\n\n```bash\npython {entry['script']} --output-dir dist/{entry['code'].lower()} --formats png svg\n```\n\n"
            text+='</details>\n\n'+entry['reference']+'\n\n[返回图表目录](#figure-catalog)\n\n'
    text+='''<a id="quick-start"></a>

## 快速开始 / Quick start

在仓库根目录，使用 Python 3.10+：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/build_gallery.py --keep-existing-images
```

构建后打开 `dist/图表汇总_2026-11-16.html`：图片、逐图代码与下载包内嵌，可离线使用。完整发布包位于 `dist/research-figure-gallery.zip`。构建产物放在 `dist/`，不提交到 Git；这些文件需先构建生成。

**从 GitHub 下载：** 进入仓库的 **Actions** 页面，选择一次成功的构建，在 **Artifacts** 中下载产物并解压。流程定义见[构建工作流](.github/workflows/build.yml)。完整构建独立执行 26 个本地代码包，8 个上游包检查完整性；报告位于 `dist/`。

## 选择与运行单图

在[34 图索引](docs/FIGURE_INDEX.md)中查看主脚本、公共函数及输入文件。三个新模板共享逐题 CSV 与配置；[数据格式](rerank_templates/2026-11-16/DATA_FORMAT.md)说明如何接入真实日志。单独复制主脚本时，需一并保留公共函数和数据。

```bash
python rerank_templates/2026-11-16/plot_pareto.py --output-dir dist/custom-pareto
```

上游示例的依赖、数据和运行路径见对应代码参考包，不能用原图代替重跑验证。

## 目录与来源

| 内容 | 入口 |
| --- | --- |
| 全部图、代码与输入 | [34 图索引](docs/FIGURE_INDEX.md) |
| 精选说明与补充理由 | [精选图文](docs/GALLERY.md) · [补充索引](SUPPLEMENT.md) |
| 论文数值与出处 | [Deep Research](paper_expansion/2026-11-01/RESEARCH_NOTES.md) · [Rerank](rerank_expansion/2026-11-15/RESEARCH_NOTES.md) |
| GitHub 原图、快照与许可 | [上游参考文档](github_references/2026-11-15/GitHub科研绘图参考.md) |
| 目录维护与去重记录 | [catalog.json](catalog.json) · [筛选说明](CURATION.md) · [去重记录](curation/2026-11-15-dedup/README.md) |

本库自编代码采用 [MIT 许可](LICENSE)。上游原图与源码各自保留原许可，详见[参考来源](REFERENCES.md)；根目录许可证不覆盖这些上游材料。
'''
    (ROOT/'README.md').write_text(text,encoding='utf-8')


def write_documents():
    entries=index_entries()
    write_gallery_and_supplement()
    write_index(entries)
    write_entrypoint(entries)


if __name__=='__main__':write_documents()
