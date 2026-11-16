"""Build a separate, source-backed reference document without redrawing figures."""
from pathlib import Path
import base64
import hashlib
import html
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent
DOC = 'GitHub科研绘图参考'
H = html.escape

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_digest(path):
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def collect():
    # One canonical source manifest; downloaded candidates were consolidated.
    items = json.loads((ROOT / 'manifest.json').read_text())['figures']
    for item in items:
        for field in ['original_local', 'preview_local', 'source_local', 'license_local']:
            assert (ROOT / item[field]).is_file(), item[field]
        assert digest(ROOT / item['original_local']) == item['original_sha256'], item['id']
        assert blob_digest(ROOT / item['original_local']) == item['image_blob_sha'], item['id']
        if 'source_blob_sha' in item:
            assert blob_digest(ROOT / item['source_local']) == item['source_blob_sha'], item['id']
        with Image.open(ROOT / item['preview_local']) as image:
            item['preview_dimensions'] = list(image.size)
        item['preview_sha256'] = digest(ROOT / item['preview_local'])
        item['source_sha256'] = digest(ROOT / item['source_local'])
        item['license_sha256'] = digest(ROOT / item['license_local'])
        item['original_upstream_image'] = True
        item['our_redraw'] = False
        item['code_execution'] = 'Source inspected; not executed.'
    assert len({item['original_sha256'] for item in items}) == len(items)
    return items


def markdown(items):
    out = [f'# GitHub 科研绘图参考：面向 Rerank 实验\n',
           '整理日期：2026-11-15。来自 **8 个 GitHub 仓库的 8 张原始示例图**，用于选图、代码借鉴与实验设计。所有图片与代码均固定到 commit，并保留本地原文件。',
           '**这些图中的数值是上游教程、测试或演示数据，不是我们的实验结果，也不是 rerank 论文数值。** 图片未重画；G08 保留原 PDF，另有栅格化预览。源码已核对对应关系，尚未在本项目中执行。',
           f'[打开离线图文版](../../dist/{DOC}.html) · [来源清单与 SHA256](manifest.json) · [返回现有图库](../../README.md)\n',
           '## 优先选择\n',
           '当前 rerank 正文优先考虑 **G02 森林图**（哪些子集受益）、**G04 雨云图**（耗时长尾）和 **G06 Pareto 图**（质量—实测开销）。G01 适合同题配对分析；G05、G07 用于诊断与证据互补性；G03、G08 适合统计补充和多面板排版。',
           '这里的优先级是针对当前实验用途的编辑判断，不代表仓库质量排名。\n',
           ]
    table = ['| 编号 | 要回答的问题 | 图型 | 建议位置 |', '| --- | --- | --- | --- |']
    for item in items:
        table.append(f'| [{item["id"]}](#{item["id"].lower()}) | {item["question"]} | {item["title"]} | {item["placement"]} |')
    out.append('\n'.join(table))
    for item in items:
        out.extend(['', f'<a id="{item["id"].lower()}"></a>', f'## {item["id"]} · {item["title"]}\n',
                    f'![{item["title"]}：上游原始示例]({item["preview_local"]})\n',
                    f'原作者 / 项目：{item["author"]}。来源：[{item["repo"]}]({item["repo_url"]})。',
                    f'**用于回答：**{item["question"]} {item["use"]}',
                    f'**需要的数据：**{item["data"]}', f'**迁移建议：**{item["adapt"]}',
                    f'**使用边界：**{item["limits"]}',
                    f'[GitHub 原图]({item["image_url"]}) · [对应源码]({item["source_url"]}) · [本地原图]({item["original_local"]}) · [本地源码]({item["source_local"]})',
                    f'源码对应：{item["source_locator"]}',
                    f'许可：**{item["license"]}**。[上游声明]({item["license_url"]}) · [本地许可全文]({item["license_local"]})。{item["license_note"]}',
                    f'固定版本：`{item["commit"]}`。'])
        if item['id'] == 'G08':
            out.append('书籍图像采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)；代码采用 BSD-2-Clause。预览仅由原 PDF 栅格化，内容未改动。')
    out.extend(['', '## 检索、筛选与保存方式\n',
        '从 GitHub 仓库检索科研绘图与 scientific visualization 示例，进一步查找配对估计图、森林图、临界差异图、雨云图、注释热图、Pareto、UpSet 和多面板布局。只收录仓库内实际存在的图片或 PDF，并检查对应代码及许可证；不以仓库截图或自行重画代替原图。',
        '例如 ARPeeketi/Template_Scientifc_Figures 的 filled_area_plot 示例经检查后未入选：大图例、重叠填充和装饰标记使信息过密。此处只保留适合当前研究问题的 8 个互补示例。',
        '图片通过 Git blob SHA 与固定版本核对，另记录 SHA256。下载的原图各保留一份；HTML 内嵌图片以便离线阅读，Markdown 引用同一份原文件。来源目录中的 README / Notebook / RST 是上游源码快照，并非新增图库文档。',
        '现有论文重绘和合成模板仍在主图库，当前共 23 张（15 主图、8 补充）；这 8 张 GitHub 参考单独计数。去重详情见 [删除记录](../../curation/2026-11-15-dedup/README.md)。',
        '可通过 `python github_references/2026-11-15/build_document.py` 重新生成本文件与 dist/ 中的离线 HTML，过程只校验和排版，不执行上游绘图源码。\n'])
    (ROOT / f'{DOC}.md').write_text('\n\n'.join(out), encoding='utf-8')


def html_document(items):
    nav = ''.join(f'<a href="#{x["id"]}"><b>{x["id"]}</b>{H(x["question"])}</a>' for x in items)
    cards = []
    for x in items:
        encoded = base64.b64encode((ROOT / x['preview_local']).read_bytes()).decode()
        width, height = x['preview_dimensions']
        body = ''.join(f'<div><dt>{label}</dt><dd>{H(x[field])}</dd></div>' for label, field in
                       [('用于回答', 'use'), ('需要的数据', 'data'), ('迁移建议', 'adapt'), ('使用边界', 'limits')])
        license_text = H((ROOT / x['license_local']).read_text())
        caption = 'GitHub 仓库原图 · 未重画' if x['transformation'] == 'none' else 'GitHub 原 PDF 的栅格预览 · 内容未改动'
        license_extra = '<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0 条款</a> · ' if x['id'] == 'G08' else ''
        cards.append(f'''<article id="{x['id']}">
<header class="card-header"><div class="number">{x['id']}</div><div><span class="placement">{H(x['placement'])}</span><h2>{H(x['title'])}</h2><p>{H(x['question'])}</p></div></header>
<figure><img src="data:image/png;base64,{encoded}" width="{width}" height="{height}" alt="{H(x['title'])}，上游原始演示图"><figcaption>{caption} · {width} × {height} px</figcaption></figure>
<div class="card-body"><dl>{body}</dl><p class="attribution">原作者 / 项目：{H(x['author'])}<br>仓库：<a href="{H(x['repo_url'])}">{H(x['repo'])}</a></p>
<div class="source-links"><a href="{H(x['image_url'])}">GitHub 原图 ↗</a><a href="{H(x['source_url'])}">对应源码 ↗</a><a href="{H(x['license_url'])}">许可声明 ↗</a></div>
<details><summary>来源定位、固定版本与许可</summary><p>{H(x['source_locator'])}</p><p>固定 commit：<code>{x['commit']}</code><br>原图 SHA256：<code>{x['original_sha256']}</code></p><p>{H(x['license'])}。{H(x['license_note'])}</p><p>{license_extra}源码已检查，未执行。图片来源与处理方式：{H(x['transformation'])}。</p><pre>{license_text}</pre></details></div></article>''')
    css = '''
:root{--ink:#152f33;--muted:#586b6e;--accent:#006b68;--line:#d8e2df;--paper:#fff;--bg:#f2f5f2}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.75}a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:3px}main{max-width:1080px;margin:auto;padding:52px 32px}h1{font-size:42px;letter-spacing:-1px;line-height:1.25;margin:14px 0 20px}h2{font-size:26px;line-height:1.35;margin:7px 0}p{margin:10px 0}.eyebrow{font-size:13px;font-weight:700;letter-spacing:2px;color:var(--accent)}.intro{max-width:830px;font-size:17px}.metrics{display:flex;gap:12px;margin:26px 0}.metrics span{background:#e2eeea;padding:7px 16px;border-radius:4px}.notice{background:#fff;border-left:4px solid var(--accent);padding:16px 22px;color:var(--muted);font-size:15px}.recommend{margin:26px 0}nav{display:grid;grid-template-columns:1fr 1fr;gap:8px 20px;padding:20px 0 30px}nav a{display:flex;gap:14px;padding:11px 0;border-bottom:1px solid var(--line);text-decoration:none;font-size:15px}nav b{font-variant-numeric:tabular-nums}article{margin:20px 0 36px;background:var(--paper);border:1px solid var(--line);border-radius:9px;overflow:hidden;scroll-margin-top:22px}.card-header{display:flex;gap:22px;padding:30px 34px 18px}.number{font-size:24px;color:var(--accent);font-weight:700;min-width:48px}.placement{font-size:12px;letter-spacing:1px;color:var(--muted)}.card-header p{color:var(--muted);margin:7px 0;font-size:16px}figure{margin:8px 34px 20px;padding:24px 16px 12px;border:1px solid #e7ece9;background:white;text-align:center}figure img{max-width:100%;height:auto;max-height:670px;object-fit:contain;display:block;margin:auto}figcaption{font-size:12px;color:var(--muted);margin-top:16px}.card-body{padding:0 34px 28px}dl{margin:0}dl>div{display:grid;grid-template-columns:94px 1fr;border-top:1px solid #edf0ed;padding:11px 0;gap:10px}dt{font-weight:650;color:var(--accent);font-size:14px}dd{margin:0;font-size:15px}.attribution{font-size:13px;color:var(--muted);margin:18px 0 12px}.source-links{display:flex;gap:12px;flex-wrap:wrap}.source-links a{border:1px solid var(--line);padding:5px 12px;border-radius:4px;text-decoration:none;font-size:13px}details{font-size:13px;color:var(--muted);border-top:1px solid var(--line);margin-top:20px;padding-top:12px}summary{cursor:pointer;font-weight:600}code{overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.55;font-size:11px;background:#f5f7f5;padding:16px;max-height:300px;overflow:auto}footer{border-top:1px solid var(--line);padding:22px 0 0;font-size:14px;color:var(--muted)}
@media(max-width:700px){main{padding:28px 16px}h1{font-size:30px}nav{grid-template-columns:1fr;gap:0}.card-header{padding:22px 18px 10px;gap:12px}.number{font-size:20px;min-width:42px}h2{font-size:22px}figure{margin:8px 16px 18px;padding:12px 6px}.card-body{padding:0 18px 22px}dl>div{grid-template-columns:1fr;gap:4px}.metrics{gap:7px;flex-wrap:wrap}.metrics span{font-size:13px;padding:5px 10px}}
@media print{body{background:#fff}main{padding:0;max-width:none}nav{display:none}article{break-before:page;border:0;margin:0;padding:0}figure{break-inside:avoid}.card-header{padding-top:0}figure img{max-height:420px}details{display:none}a{color:inherit}.card-body{padding-bottom:10px}.notice{font-size:13px}footer{break-before:page}}
'''
    result = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GitHub 科研绘图参考 · Rerank</title><style>{css}</style></head><body><main>
<header><span class="eyebrow">RESEARCH FIGURE REFERENCES · 2026.11.15</span><h1>GitHub 科研绘图参考<br>面向 Rerank 实验</h1><p class="intro">从仓库原图出发，按研究问题选画法。每个示例都有原始图片、对应源码、固定版本与使用边界。</p><div class="metrics"><span><b>8</b> 张原图</span><span><b>8</b> 个仓库</span><span>图片可离线查看</span></div></header>
<div class="notice">图中数值来自上游教程、测试或演示数据，<b>不是我们的实验结果，也不是 rerank 论文数值</b>。图片未重画；G08 保留原 PDF 并提供栅格预览。源码已核对，未在本项目中执行。</div>
<p class="recommend"><b>正文优先：</b>G02 看子集收益，G04 看延迟长尾，G06 看质量与实测开销。其余示例用于配对分析、错误诊断、证据互补性或附录排版；这是针对当前实验用途的选择。</p>
<nav aria-label="按研究问题选图">{nav}</nav>{''.join(cards)}
<footer><p><b>检索与收录规则</b>：通过 GitHub 搜索科研绘图及上述图型，收录仓库内实际存在的 PNG 或 PDF，检查源码与输出对应关系、固定 commit 和许可证。原图均核对 Git blob SHA，并在随附 manifest.json 中保存 SHA256。</p><p>这 8 张图片作为独立参考收录。现有论文重绘与合成模板图库经去重后为 23 张（15 主图、8 补充）。没有用上游演示值补造实验分布或模型结果。</p><p>本 HTML 内嵌全部预览与许可证，可单独保存离线阅读；GitHub 链接需要联网。整理日期：2026-11-15。</p></footer>
</main></body></html>'''
    output = ROOT.parents[1] / 'dist' / f'{DOC}.html'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding='utf-8')


def main():
    items = collect()
    manifest = dict(date='2026-11-15', scope='Separate GitHub original-image references for rerank research',
                    count=len(items), repositories=len({x['repo'] for x in items}),
                    source_status='Original upstream files verified against Git blob hashes; no upstream plotting code executed.',
                    figures=items)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    markdown(items)
    html_document(items)
    print(f'Built {DOC}.md and standalone HTML; {len(items)} unique originals verified.')


if __name__ == '__main__':
    main()
