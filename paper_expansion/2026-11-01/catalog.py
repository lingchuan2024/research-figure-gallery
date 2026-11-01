"""Render new reference entries once each, with links relative to the repository."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]

def root_section():
    figures=json.loads((HERE/'manifest.json').read_text());papers={p['id']:p for p in json.loads((HERE/'papers.json').read_text())}
    prefix=str(HERE.relative_to(REPO))
    text=f'''\n## 新增 · Deep Research 文献真实数据图

本轮核查 8 篇已有资料索引之外的论文，从其中 6 篇新增 {len(figures)} 张图。**新增图均由论文表格或图上明确打印的真实数值重绘；不是我们的实验结果，也不是作者原出图脚本。** 每图附 CSV、出处页码和本地绘图代码，未猜测未公开的逐题数据或误差区间。

[论文内容与实验契合分析]({prefix}/RESEARCH_NOTES.md) · [审美筛选记录]({prefix}/AESTHETIC_REVIEW.md) · [数据来源审计]({prefix}/data_provenance.json) · [新图速览]({prefix}/new_figures_overview.png)（[速览代码]({prefix}/contact_sheet.py)）

'''
    for category in sorted({f['category']for f in figures}):
        text+=f'### {category}\n\n'
        for f in (f for f in figures if f['category']==category):
            p=papers[f['paper']]
            text+=f"**{f['id']} · {f['title']}**\n\n![{f['title']}（论文真实数值重绘）]({prefix}/{f['image']})\n\n"
            text+=f"[绘图代码]({prefix}/{f['script']}) · [CSV]({prefix}/{f['data']}) · [SVG]({prefix}/{f['vector']}) · [论文原表／原图页]({p['pdf']}#page={f['source_pdf_page']})\n\n"
            text+=f"出处：{p['version']}，{f['source_locator']}。契合点：{f['fit']}\n\n{f['condition']}\n\n"
    text+=f'''新增图可单独复现，不改写原有图片：

```bash
python {prefix}/build.py
```

原始论文下载与 SHA-256 校验：`python {prefix}/fetch_sources.py`。作者仓库已按固定提交检查，本轮未定位到这些图对应的作者出图脚本；上面的“绘图代码”均是仓库内的重绘实现。
'''
    return text
