"""Write the whole README and supplement from one editorial catalog."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.catalog_support import ROOT,load_catalog,source_inventory,selected_entries

def source_line(item):
    if item['origin']=='paper':
        return f"来源：[{item['source_label']}]({item['source_url']})，{item['paper_version']}，{item['source_locator']}。"
    return f"图型参考：[{item['reference'].rstrip('/').split('/')[-1]}]({item['reference']})。"

def write_documents():
    items=selected_entries();catalog=load_catalog();inventory=source_inventory();sections=list(dict.fromkeys(i['section']for i in items))
    paper_count=sum(i['origin']=='paper'for i in items);template_count=len(items)-paper_count
    text=f'''# Agentic Search 图表参考库

面向 search / rerank / 自主工具调用实验，按论文要回答的问题精选 {len(items)} 张图。每张图附预览、可运行代码、输入数据和来源。

**文献数据重绘**（{paper_count} 张）使用来源论文的公开数值；**合成数据模板**（{template_count} 张）仅用于展示画法。全部脚本由本仓库实现，图中数值均不属于我们的实验结果。

[精选总览](docs/gallery_overview.png)（[生成代码](scripts/build_curated_overview.py)） · [补充索引与筛选理由](SUPPLEMENT.md) · [论文与实验契合分析](paper_expansion/2026-11-01/RESEARCH_NOTES.md)

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
python examples/08_query_paired_comparison/plot.py --data-dir data/demo --output-dir output/figures
# 文献数值重绘
python paper_expansion/2026-11-01/code/N02_failure_hierarchy.py --output-dir output/figures --formats png svg
```

模板字段定义见 [数据说明](data/README.md)；文献数值的原表、页码与文件校验信息见 [来源审计](paper_expansion/2026-11-01/data_provenance.json)。接入真实实验时重新核验指标、分母、配对关系和脚注。

```bash
python -m unittest discover -s tests -v
python scripts/package_release.py
```

## 目录与维护

- [catalog.json](catalog.json)：主图库的顺序、分类与补充条目，README 由它统一生成。
- `examples/`、`paper_expansion/2026-11-01/code/`：实际绘图脚本；`gallery.json` 和文献 `manifest.json` 保存源文件映射。
- [SUPPLEMENT.md](SUPPLEMENT.md)：未进入主图库的图及理由，图片与代码保留。
- [verification.json](verification.json)：文件摘要、代码与目录检查记录；不验证实验结论。

代码采用 [MIT 许可](LICENSE)。文献重绘保留论文署名与出处，参考项目的完整说明见 [REFERENCES.md](REFERENCES.md)。
'''
    (ROOT/'README.md').write_text(text,encoding='utf-8')
    supplement='''# 补充索引与筛选理由

主图库按实验契合度、可读性和信息互补性，从18张中保留12张。以下6张适合后续专项实验或附录，当前不重复展示大图。全部图片、代码及数据保持原文件，随时可复用。

| 图表 | 暂不进入主图库的原因 | 文件 |
| --- | --- | --- |
'''
    for item in catalog['supplement']:
        raw=inventory[item['id']]
        supplement+=f"| {item['title']} | {item['reason']} | [图片]({raw['image']}) · [代码]({raw['script']}) · [数据]({raw['data'][0]}) |\n"
    supplement+='\n筛选针对图的表达与当前实验用途，没有按结果方向筛样本或改变数值。主图库的12张按统一用途组织，数据来源类型在每图旁注明；不同论文分数不能合并排名。\n'
    (ROOT/'SUPPLEMENT.md').write_text(supplement,encoding='utf-8')

if __name__=='__main__':write_documents()
