"""Compile existing charts into one offline HTML; do not redraw any figure."""
from pathlib import Path
import base64
import hashlib
import html
import io
import json
import sys
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.catalog_support import load_catalog, source_inventory
from scripts.figure_code_support import attach_code_sections
from scripts.readme_notes import FIGURE_NOTES

OUTPUT = ROOT / 'dist/图表汇总_2026-11-16.html'
GITHUB = ROOT / 'github_references/2026-11-15'
TEMPLATES = ROOT / 'rerank_templates/2026-11-16'
H = html.escape


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect():
    catalog, inventory = load_catalog(), source_inventory()
    figures = []
    refs = {x['template']: x for x in json.loads((TEMPLATES / 'sources.json').read_text())}
    template_text = {
        'forest': ('T01', '子集收益森林图', '同题比较不同方法在各 benchmark 与题型上的质量差值，保留负收益、配对样本量和 95% bootstrap 区间。',
                   '需要逐题 score 和稳定 question_id。All 与子集重叠；区间不含多重比较校正。'),
        'raincloud': ('T02', '分面耗时雨云图', '按题型观察端到端耗时、token 等资源分布，显示逐题点、四分位数与长尾。',
                      '需要实际逐题资源数据。保留零值与已记录的未完成题；不能由总账均摊出分布。'),
        'pareto': ('T03', '质量—开销 Pareto 图', '在同一批题目上比较平均质量与平均成本，突出观测均值中的非支配配置。',
                   '质量、成本和各方法必须使用同一题集。非支配标记不是统计显著胜出的证明。'),
    }
    for name, (code, title, purpose, limits) in template_text.items():
        figures.append(dict(id=f'template-{name}', code=code, category='templates', title=title,
            badge='合成数据 · 可运行模板', origin='synthetic', image=TEMPLATES / f'figures/{name}.png',
            purpose=purpose, limits=limits, source_label=f'图型参考：{refs[name]["repo"]}',
            source_url=refs[name]['image_url'], script=f'rerank_templates/2026-11-16/plot_{name}.py',
            source_code_url=refs[name]['source_url'], data=['rerank_templates/2026-11-16/data/demo/observations.csv'],
            extra='默认示例为 120 题 × 3 方法的合成数据。完整代码、数据格式说明和示例在本文件内嵌的模板包中。'))
    for category, entries in [('selected', catalog['selected']), ('supplement', catalog['supplement'])]:
        for i, entry in enumerate(entries, 1):
            raw = {**inventory[entry['id']], **entry}
            is_paper = raw['origin'] == 'paper'
            location = ''
            if is_paper:
                location = f'{raw["paper_version"]} · {raw["source_locator"]} · PDF p. {raw["source_pdf_page"]}'
            figures.append(dict(id=f'gallery-{raw["id"]}', code=f'{"M" if category == "selected" else "S"}{i:02d}',
                original_id=raw['id'], category=category, title=raw['title'],
                badge='论文公开数据重绘' if is_paper else '合成数据模板', origin=raw['origin'], image=ROOT / raw['image'],
                purpose=raw.get('purpose') or raw.get('fit') or raw.get('usage', ''),
                limits=raw.get('condition') or raw.get('note') or '', source_label=raw['source_label'],
                source_url=raw['source_url'], source_locator=location, script=raw['script'], data=raw['data'],
                extra=('补充收录原因：' + raw['reason']) if category == 'supplement' else raw.get('section', '')))
    for raw in json.loads((GITHUB / 'manifest.json').read_text())['figures']:
        figures.append(dict(id=f'github-{raw["id"]}', code=raw['id'], category='github', title=raw['title'],
            badge='GitHub 上游原始示例', origin='github', image=GITHUB / raw['preview_local'],
            purpose=raw['use'], limits=raw['limits'], source_label=raw['repo'], source_url=raw['image_url'],
            source_code_url=raw['source_url'], source_locator=f'固定 commit：{raw["commit"]}',
            author=raw['author'], license=raw['license'], license_url=raw['license_url'],
            license_note=raw['license_note'], license_text=(GITHUB / raw['license_local']).read_text(),
            data_requirement=raw['data'], extra=raw['adapt'],
            transformation='原 PDF 栅格预览，内容未改动。' if raw['transformation'] != 'none' else '保留原图，未重绘。'))
    if len(figures) != 34 or len({f['id'] for f in figures}) != 34:
        raise ValueError('Expected all 34 figures exactly once.')
    for item in figures:
        if not item['image'].is_file():
            raise FileNotFoundError(item['image'])
        item['sha256'] = sha(item['image'])
        with Image.open(item['image']) as im:
            item['width'], item['height'] = im.size
    if len({item['sha256'] for item in figures}) != len(figures):
        raise ValueError('Duplicate image files would be embedded.')
    return figures


def link(url, label):
    return f'<a href="{H(url)}" target="_blank" rel="noopener noreferrer">{H(label)} ↗</a>'


def family_figures(sources):
    """Create presentation-only copies; source IDs/categories keep their contracts."""
    from scripts.family_support import load_families

    by_code = {source['code']: source for source in sources}
    families = load_families(set(by_code))
    display = []
    for family in families:
        representative = by_code[family['representative']]
        item = dict(representative)
        item.update(
            code=family['id'], title=family['title'], category='figures',
            source_code=representative['code'], source_title=representative['title'],
            source_category=representative['category'], family=family,
            reading=FIGURE_NOTES[representative['code']]['reading'],
            variants=[by_code[code] for code in family['members'] if code != family['representative']],
        )
        display.append(item)
    return display


def uses_table(item):
    rows = []
    labels = {code: f"{item['code']}.{number}" for number, code in enumerate(item['family']['members'], 1)}
    for use in item['family']['uses']:
        codes = ' · '.join(f'<a href="#code-{H(code)}">{H(labels[code])}</a>' for code in use['source_codes'])
        rows.append(f'<tr><td>{H(use["purpose"])}</td><td>{H(use["placement"])}</td>'
                    f'<td>{H(use["data"])}</td><td>{codes}</td></tr>')
    return ('<section class="uses"><h4>同一图型可以回答什么问题</h4><div class="table-scroll">'
            '<table><thead><tr><th>用途</th><th>建议论文位置</th><th>所需数据</th><th>对应代码</th></tr></thead>'
            '<tbody>' + ''.join(rows) + '</tbody></table></div></section>')


def variant_sections(item):
    """Show source variants as text and archive links, never as extra previews."""
    if not item['variants']:
        return ''
    rows = []
    for variant in item['variants']:
        code = variant['code_section']
        label = f"{item['code']}.{item['family']['members'].index(variant['code']) + 1}"
        source = link(variant['source_url'], variant['source_label'])
        if variant.get('source_code_url'):
            source += ' · ' + link(variant['source_code_url'], '上游对应代码')
        license_text = (H(variant['license']) + ' · ' + link(variant['license_url'], '许可声明')) if variant.get('license') else '本库代码：MIT；论文数据保留原出处。'
        if variant.get('license_note'):
            license_text += '。' + H(variant['license_note'])
        if variant['code'] == 'G08':
            license_text += ' · ' + link('https://creativecommons.org/licenses/by-nc-sa/4.0/', '原图 CC BY-NC-SA 4.0')
        attribution = f'<br>作者 / 项目：{H(variant["author"])}' if variant.get('author') else ''
        note = FIGURE_NOTES[variant['code']]['caution']
        rows.append(f'''<div class="variant" id="code-{H(variant['code'])}" data-source-id="{H(variant['id'])}">
<p><b>{H(label)} · {H(variant['title'])}</b> <span class="code-status {code['kind']}">{H(code['status'])}</span></p>
<p>示例类型：{H(variant['badge'])}<br>代码：<code>{H(code['main_path'])}</code><br>来源：{source}{attribution}<br>许可：{license_text}</p>
<p>{H(note)}</p><button type="button" class="download-variant-bundle" data-bundle-id="{H(variant['id'])}">下载此用途的代码与数据包</button>
</div>''')
    return (f'<details class="variants"><summary>相关用途的代码与来源 · {len(rows)} 份变体</summary>'
            + ''.join(rows) + '</details>')


def code_section(item):
    code = item['code_section']
    helpers = []
    for helper in code['helpers']:
        helpers.append(f'<details class="helper-code"><summary>公共函数：{H(helper["path"])}</summary><pre class="source-code"><code>{H(helper["text"])}</code></pre></details>')
    inputs = []
    for data in code['inputs']:
        fields = ' · '.join(H(name) if name else '（原始行号列）' for name in data['columns'])
        inputs.append(f'<div class="input-preview"><p><b>{H(Path(data["path"]).name)}</b> · {data["row_count"]} 行</p><p class="fields">字段：{fields}</p><pre><code>{H(data["preview"])}</code></pre></div>')
    label = '下载独立运行包' if code['kind'] == 'local' else '下载上游源码参考包'
    source_code = item.get('source_code', item['code'])
    return f'''<section class="code-section" id="code-{H(source_code)}" aria-label="{H(item['title'])}的代码">
<div class="code-heading"><h4>代码部分</h4><span class="code-status {code['kind']}">{H(code['status'])}</span></div>
<p class="code-file">{H(code['filename'])} · {H(code['language'])} · {len(code['text'].splitlines())} 行</p>
<div class="code-actions"><button type="button" class="copy-code">复制代码</button><button type="button" class="download-code">下载代码文件</button><button type="button" class="download-code-bundle">{label}</button><span class="copy-status" aria-live="polite"></span></div>
<pre class="source-code main-code" data-filename="{H(code['filename'])}" data-sha256="{code['code_sha256']}"><code>{H(code['text'])}</code></pre>
<p class="code-notes">{H(code['notes'])}</p>{''.join(helpers)}
<details class="run-details"><summary>运行方式、依赖与输入数据</summary><p><b>依赖：</b>{H('；'.join(code['dependencies']))}</p><pre class="run-command"><code>{H(code['command'])}</code></pre><p><b>数据格式：</b>{H(code['input_format'])}</p>{''.join(inputs)}</details>
</section>'''


def card(item):
    image_data = base64.b64encode(item['image'].read_bytes()).decode()
    sources = link(item['source_url'], item['source_label'])
    if item.get('source_code_url'):
        sources += ' · ' + link(item['source_code_url'], '上游对应代码')
    detail = []
    if item.get('source_locator'):
        detail.append(f'<p>{H(item["source_locator"])}</p>')
    if item.get('script'):
        detail.append(f'<p>仓库绘图脚本：<code>{H(item["script"])}</code></p>')
    if item.get('data'):
        detail.append('<p>仓库输入数据：' + '、'.join(f'<code>{H(p)}</code>' for p in item['data']) + '</p>')
    if item.get('license'):
        detail.append(f'<p>作者 / 项目：{H(item["author"])}<br>许可：{H(item["license"])}。{H(item["license_note"])}</p>')
        detail.append('<p>' + link(item['license_url'], '上游许可声明') + '</p>')
        if item.get('source_code', item['code']) == 'G08':
            detail.append('<p>' + link('https://creativecommons.org/licenses/by-nc-sa/4.0/', 'CC BY-NC-SA 4.0') + '。Nicolas P. Rougier 原 PDF 的栅格预览，内容未改动。</p>')
        detail.append(f'<details class="license"><summary>许可全文</summary><pre>{H(item["license_text"])}</pre></details>')
    detail.append(f'<p>代表来源：<code>{H(item["source_code"])}</code> · {H(item["source_title"])}<br>原始标识：<code>{H(item.get("original_id", item["source_code"]))}</code><br>图片 SHA256：<code>{item["sha256"]}</code></p>')
    limits = f'<p class="limits"><b>使用边界</b>　{H(item["family"]["caution"])}</p>'
    search_parts = [item['code'], item['title'], item['reading'], item['source_label'], item['source_code']]
    for use in item['family']['uses']:
        search_parts.extend([use['purpose'], use['placement'], use['data'], *use['source_codes']])
    for variant in item['variants']:
        search_parts.extend([variant['code'], variant['title'], variant['source_label']])
    search = ' '.join(search_parts)
    return f'''<article class="figure-card" id="{item['id']}" data-category="{item['category']}" data-search="{H(search)}">
<header class="card-header"><span class="number">{item['code']}</span><div><span class="badge {item['origin']}">{H(item['badge'])}</span><h3>{H(item['title'])}</h3></div></header>
<figure><button class="zoom-image" type="button" aria-label="放大 {H(item['title'])}"><img loading="lazy" src="data:image/png;base64,{image_data}" width="{item['width']}" height="{item['height']}" alt="{H(item['title'])} · {H(item['badge'])}"></button><figcaption>{H(item.get('transformation', '保留当前成图，未重新计算或改动画面。'))} <span>{item['width']} × {item['height']} px</span></figcaption></figure>
<div class="card-body"><p class="example-source">示例：{H(item['source_title'])}</p><p class="purpose"><b>这张示例怎么看</b>　{H(item['reading'])}</p>{uses_table(item)}{limits}<p class="sources">代表图来源：{sources}</p><div class="actions"><button type="button" class="view-full">放大查看</button><button type="button" class="download-image">下载代表图 PNG</button><a href="#top">返回顶部 ↑</a></div>{code_section(item)}{variant_sections(item)}<details class="provenance"><summary>代表图来源定位与文件信息</summary>{''.join(detail)}</details></div></article>'''


CSS = '''
:root{--ink:#18353b;--muted:#5b7075;--teal:#006d67;--line:#dae4e0;--bg:#f1f5f2;--white:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.75}a{color:var(--teal);text-underline-offset:3px}button,input{font:inherit}button,a{touch-action:manipulation}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #e1ad47;outline-offset:3px}main{max-width:1160px;margin:auto;padding:42px 30px 60px}h1{font-size:44px;line-height:1.25;letter-spacing:-1px;margin:12px 0 18px}h2{font-size:26px;line-height:1.4;margin:0}h3{font-size:24px;line-height:1.4;margin:8px 0 0}.eyebrow{font-size:12px;letter-spacing:2px;color:var(--teal);font-weight:700}.lead{font-size:17px;max-width:900px}.counts{display:flex;flex-wrap:wrap;gap:10px;margin:25px 0}.counts span{background:#e0ece6;padding:7px 14px;border-radius:4px}.notice{background:#fff;border-left:4px solid var(--teal);padding:16px 20px;font-size:14px;color:var(--muted)}.bundle{display:flex;align-items:center;flex-wrap:wrap;gap:16px;margin:22px 0}.bundle button{background:var(--teal);color:#fff;border:0;padding:11px 18px;border-radius:5px;font-weight:650}.bundle small{color:var(--muted)}.toolbar{position:sticky;top:0;z-index:8;background:#f1f5f2f2;backdrop-filter:blur(10px);padding:14px 0;border-bottom:1px solid var(--line)}.searchline{display:flex;gap:12px;align-items:center}.searchline input{padding:10px 13px;border:1px solid #b8cbc4;border-radius:5px;background:#fff;min-width:0;flex:1}.searchline button{border:1px solid var(--line);background:white;padding:10px 16px;border-radius:5px}.filter-buttons{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.filter-buttons button{border:1px solid #c4d5cd;border-radius:30px;background:#fff;padding:6px 14px;color:var(--ink);font-size:14px}.filter-buttons button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:#fff}.count-line{margin:9px 0 0;color:var(--muted);font-size:13px}.toc{margin:22px 0;background:#fff;border:1px solid var(--line);padding:16px 22px;border-radius:6px}.toc summary{cursor:pointer;font-weight:650}.toc-links{display:grid;grid-template-columns:1fr 1fr;gap:5px 20px;margin-top:15px}.toc-links a{font-size:14px;text-decoration:none;padding:4px 0}.toc-links b{display:inline-block;min-width:40px}.section-header{margin:38px 0 18px;padding-bottom:12px;border-bottom:1px solid var(--line)}.section-header .section-number{font-size:13px;letter-spacing:2px;color:var(--teal);font-weight:700}.section-header p{font-size:14px;color:var(--muted);margin:8px 0 0}.figure-card{margin:20px 0 30px;background:white;border:1px solid var(--line);border-radius:9px;overflow:hidden;scroll-margin-top:188px}.card-header{display:flex;gap:22px;padding:25px 30px 14px}.number{color:var(--teal);font-size:22px;min-width:44px;font-weight:700}.badge{font-size:12px;padding:4px 8px;border-radius:4px;background:#edf3f1;color:var(--muted)}.badge.paper{background:#e7edf8;color:#355b87}.badge.synthetic{background:#fbefdb;color:#855923}.badge.github{background:#edf0f3;color:#465763}figure{margin:10px 28px 18px;padding:14px 10px 9px;border:1px solid #e8ede9;text-align:center}.zoom-image{padding:0;border:0;background:transparent;display:block;width:100%;cursor:zoom-in}.zoom-image img{display:block;max-width:100%;height:auto;max-height:730px;object-fit:contain;margin:auto}.zoom-image img:hover{opacity:.96}figcaption{font-size:12px;color:var(--muted);margin-top:12px}figcaption span{margin-left:8px}.card-body{padding:0 30px 24px;font-size:15px}.purpose{font-size:16px;margin:10px 0}.limits{background:#f6f8f6;padding:10px 13px;border-radius:4px}.extra{font-size:13px;color:var(--muted)}.sources{font-size:13px;overflow-wrap:anywhere}.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0}.actions button{border:1px solid #ccdcd4;background:#fff;padding:6px 11px;border-radius:4px;color:var(--teal);font-size:13px}.actions a{font-size:13px;margin-left:auto}.provenance{border-top:1px solid var(--line);padding-top:11px;font-size:13px;color:var(--muted)}summary{cursor:pointer}code{font-size:12px;overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:11px;padding:15px;background:#f6f8f6;max-height:280px;overflow:auto}.license{margin-top:10px}footer{margin-top:35px;border-top:1px solid var(--line);padding-top:20px;color:var(--muted);font-size:13px}.empty{padding:40px;text-align:center;color:var(--muted)}[hidden]{display:none!important}dialog{border:0;border-radius:8px;padding:16px;max-width:96vw;width:max-content;max-height:95vh;overflow:auto;background:white}dialog::backdrop{background:#102329d9}.dialog-head{display:flex;justify-content:space-between;align-items:center;gap:20px;position:sticky;top:-16px;background:#fff;padding:8px 0 15px}dialog button{border:1px solid #b8cbc4;padding:6px 12px;border-radius:4px;background:white}dialog img{display:block;max-width:min(2000px,90vw);height:auto}dialog p{margin:0;font-size:14px}.noscript{background:#fff3d4;padding:12px 18px}
@media(max-width:700px){main{padding:25px 15px}h1{font-size:32px}h2{font-size:23px}h3{font-size:21px}.lead{font-size:15px}.counts{gap:6px}.counts span{font-size:13px;padding:6px 10px}.toolbar{padding:10px 0}.filter-buttons{gap:6px}.filter-buttons button{font-size:12px;padding:5px 10px}.card-header{padding:20px 17px 10px;gap:12px}.number{min-width:37px;font-size:20px}figure{margin:8px 13px 16px;padding:8px 5px}.card-body{padding:0 17px 20px}.toc-links{grid-template-columns:1fr}.toc{padding:12px 16px}.figure-card{scroll-margin-top:215px}.actions a{margin-left:0}figcaption span{display:block;margin:0}.notice{font-size:13px}.purpose{font-size:15px}}
@media print{body{background:white}main{max-width:none;padding:0}h1{font-size:28px}.toolbar,.toc,.bundle,.actions,dialog,.provenance,button.zoom-image::after{display:none!important}.figure-card{break-before:page;border:0;overflow:visible;margin:0}.card-header{padding:10px 0}.card-body{padding:0;font-size:11px}figure{margin:5px 0 12px;padding:5px;break-inside:avoid}.zoom-image img{max-height:155mm;max-width:100%}.purpose{font-size:12px}.limits,.extra,.sources,figcaption{font-size:10px}.section-header{break-before:page;margin-top:15px}.figure-card[hidden],.figure-section[hidden]{display:none!important}footer{break-before:page}}
'''

CSS += '''
.code-section{border-top:1px solid var(--line);margin:22px 0;padding-top:18px}.code-heading{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.code-heading h4{margin:0;font-size:18px}.code-status{font-size:12px;padding:3px 8px;border-radius:4px;background:#e4f0e9;color:#23644c}.code-status.upstream{background:#fff1d7;color:#86601d}.code-file,.code-notes{font-size:12px;color:var(--muted);overflow-wrap:anywhere}.code-actions{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}.code-actions button{border:1px solid #c3d5cc;background:#fff;color:var(--teal);border-radius:4px;padding:6px 11px;font-size:13px}.copy-status{font-size:12px;color:var(--teal);align-self:center}.source-code{background:#152e35;color:#e4eee9;border-radius:5px;padding:16px 18px;white-space:pre;overflow:auto;max-height:360px;tab-size:4}.source-code code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;overflow-wrap:normal}.helper-code,.run-details{margin:12px 0;padding:10px 0;border-top:1px solid #e6ede8;font-size:13px}.run-command{font-size:12px;white-space:pre-wrap;max-height:none}.input-preview{border:1px solid var(--line);border-radius:4px;margin:12px 0;padding:10px 12px}.input-preview p{margin:4px 0}.input-preview pre{white-space:pre;max-height:150px;overflow:auto}.fields{font-size:12px;overflow-wrap:anywhere}.bundle .secondary{background:white;color:var(--teal);border:1px solid #c3d5cc}
@media(max-width:700px){.source-code{padding:12px;max-height:300px}.source-code code{font-size:11px}.code-actions button{font-size:12px;padding:6px 9px}.code-heading h4{font-size:17px}.code-status{font-size:11px}.code-actions{gap:6px}}
@media print{.code-actions{display:none}.source-code{max-height:none;white-space:pre-wrap;overflow:visible;background:#f4f7f5;color:#18353b}.source-code code{font-size:8px}.code-section{break-before:auto}.code-notes,.code-file{font-size:9px}}
'''

CSS += '''
.uses h4{font-size:17px;margin:20px 0 10px}.table-scroll{overflow-x:auto}.uses table{width:100%;border-collapse:collapse;font-size:13px}.uses th,.uses td{padding:10px 12px;border:1px solid var(--line);text-align:left;vertical-align:top}.uses th{background:#f1f5f2;white-space:nowrap}.uses td:last-child{min-width:84px}.example-source{font-size:12px;color:var(--muted)}.variants{border-top:1px solid var(--line);margin:18px 0;padding-top:14px}.variants>summary{font-weight:650}.variant{padding:12px 0;border-bottom:1px solid #e6ede8;font-size:13px;scroll-margin-top:160px}.variant p{margin:7px 0;overflow-wrap:anywhere}.variant .code-status{display:inline-block;margin-top:4px}.download-variant-bundle{border:1px solid #c3d5cc;background:white;color:var(--teal);padding:6px 11px;border-radius:4px;font-size:13px}.code-section{scroll-margin-top:160px}
'''

JS = '''
const cards=[...document.querySelectorAll('.figure-card')];
const search=document.getElementById('search');
function applyFilter(){
 const query=search.value.trim().toLocaleLowerCase();let visible=0;
 for(const card of cards){card.hidden=!card.dataset.search.toLocaleLowerCase().includes(query);if(!card.hidden)visible++;document.querySelector(`[data-target="${card.id}"]`).hidden=card.hidden;}
 for(const section of document.querySelectorAll('.figure-section'))section.hidden=![...section.querySelectorAll('.figure-card')].some(card=>!card.hidden);
 document.getElementById('visible-count').textContent=`显示 ${visible} / ${cards.length} 种图型`;
 document.getElementById('empty').hidden=visible!==0;
}
search.addEventListener('input',applyFilter);
document.getElementById('reset').addEventListener('click',()=>{search.value='';applyFilter()});
const dialog=document.getElementById('zoom-dialog'),zoomed=document.getElementById('zoomed-image');
const bundles=JSON.parse(document.getElementById('code-bundles').textContent);
for(const card of cards){
 const img=card.querySelector('img');
 function zoom(){zoomed.src=img.src;zoomed.alt=img.alt;document.getElementById('zoom-title').textContent=img.alt;dialog.showModal()}
 card.querySelector('.zoom-image').addEventListener('click',zoom);card.querySelector('.view-full').addEventListener('click',zoom);
 card.querySelector('.download-image').addEventListener('click',()=>download(img.src,`${card.id}.png`));
 const source=card.querySelector('.main-code code'),main=card.querySelector('.main-code');
 card.querySelector('.download-code').addEventListener('click',()=>downloadBlob(new Blob([source.textContent],{type:'text/plain;charset=utf-8'}),main.dataset.filename));
 card.querySelector('.download-code-bundle').addEventListener('click',()=>downloadArchive(bundles[card.id]));
 card.querySelector('.copy-code').addEventListener('click',async()=>{let copied=false;try{await navigator.clipboard.writeText(source.textContent);copied=true}catch(e){const input=document.createElement('textarea');input.value=source.textContent;input.style.position='fixed';input.style.opacity='0';document.body.appendChild(input);input.select();copied=document.execCommand('copy');input.remove()}card.querySelector('.copy-status').textContent=copied?'已复制完整代码':'请在代码框中选择并复制';});
}
for(const button of document.querySelectorAll('.download-variant-bundle'))button.addEventListener('click',()=>downloadArchive(bundles[button.dataset.bundleId]));
for(const anchor of document.querySelectorAll('.uses a[href^="#code-"]'))anchor.addEventListener('click',()=>{const target=document.querySelector(anchor.getAttribute('href'));if(target){const details=target.closest('details');if(details)details.open=true;}});
document.getElementById('close-zoom').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
function download(url,name){const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove()}
function downloadBlob(blob,name){const url=URL.createObjectURL(blob);download(url,name);setTimeout(()=>URL.revokeObjectURL(url),30000)}
function downloadArchive(payload){const bytes=Uint8Array.from(atob(payload.data),c=>c.charCodeAt(0));downloadBlob(new Blob([bytes],{type:'application/zip'}),payload.filename)}
document.getElementById('download-all-code').addEventListener('click',()=>downloadArchive(bundles.all));
applyFilter();
'''


def build():
    sources = collect()
    # Packaging and verification still cover every source. Families only choose
    # which original preview and main script appear on the presentation surface.
    code_manifest, combined_code = attach_code_sections(sources)
    figures = family_figures(sources)
    archive = TEMPLATES / 'dist/rerank-plot-templates.zip'
    # Always refresh the attachment after verification; incremental builds must
    # never retain stale code, data-format documentation or provenance.
    import subprocess
    subprocess.run([sys.executable, str(TEMPLATES / 'package.py')], check=True)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('Template attachment ZIP is corrupt.')
        for name, expected in json.loads((TEMPLATES / 'verification.json').read_text())['sha256'].items():
            if hashlib.sha256(bundle.read('rerank-plot-templates/' + name)).hexdigest() != expected:
                raise ValueError(f'Stale template attachment: {name}; run template package.py.')
    toc = ''.join(f'<a data-target="{f["id"]}" href="#{f["id"]}"><b>{f["code"]}</b>{H(f["title"])}</a>' for f in figures)
    sections = ['<section class="figure-section" data-section="figures">'
                + ''.join(card(item) for item in figures) + '</section>']
    code_payloads = {item['id']: {'filename': item['code_section']['bundle_filename'], 'data': base64.b64encode(item['code_section']['bundle_bytes']).decode()} for item in sources}
    code_payloads['all'] = {'filename': 'all-figure-code.zip', 'data': base64.b64encode(combined_code).decode()}
    code_payload = json.dumps(code_payloads)
    result = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rerank 科研绘图参考 · {len(figures)} 种图型</title><style>{CSS}</style></head><body><main id="top">
<header><span class="eyebrow">RERANK RESEARCH · FIGURE TYPES + CODE</span><h1>按图型选择科研图表</h1><p class="lead">每种图型只展示一个代表图，再说明它能回答哪些研究问题、适合放在论文哪里，以及需要什么数据。同类实现保留为代码变体，便于复用。</p><div class="counts"><span><b>{len(figures)}</b> 种图型</span><span>一图多用途</span><span>代码可下载</span></div></header>
<div class="notice">代表图已内嵌，可离线浏览、放大和下载。每张示例保留真实的数据类型、出处与执行状态；论文数值、合成演示和上游示例都不是我们的实测结果。用途与论文位置是建议，须以实际实验设计为准。</div>
<div class="bundle"><button id="download-all-code" type="button">下载全部图型的代码与数据</button><small>完整代码包 {len(combined_code) / 1024 / 1024:.2f} MiB · 含各用途变体、公共函数、输入说明与许可；上游代码参考会单独注明未完整执行。</small></div>
<noscript><p class="noscript">浏览器禁用了 JavaScript，代表图与说明仍可阅读；启用后可搜索、放大和下载内嵌文件。</p></noscript>
<div class="toolbar"><div class="searchline"><input id="search" type="search" aria-label="搜索图型或用途" placeholder="搜索图型、用途或代码，例如：雨云、召回、RankRAG"><button id="reset" type="button">重置</button></div><p class="count-line" id="visible-count" aria-live="polite">显示 {len(figures)} / {len(figures)} 种图型</p></div>
<details class="toc"><summary>展开全部图型目录</summary><div class="toc-links">{toc}</div></details><p class="empty" id="empty" hidden>没有匹配的图型或用途，请尝试其他关键词。</p>
{''.join(sections)}
<footer><p>每类只展示一个代表图，其余相关实现以代码与来源保留，原始图片、数据和源码没有因展示去重而删除。各用途的下载包保留必要公共函数、输入数据、运行说明和许可证。</p><p>执行状态逐项标明：本地独立运行验证不等于科学结论验证；上游参考未在本项目完整执行，API、依赖版本和随机状态可能影响重跑结果。原图与源码许可可能不同，应遵循各项保留的许可说明。</p><p>代表图片、主代码和所有用途代码包已内嵌，无外部图片、字体或脚本依赖；来源链接需要联网。复制主脚本时请一并保留公共函数和数据，直接运行建议下载完整包。浏览器打印会包含当前搜索结果中的代表图与主代码。</p></footer>
</main><dialog id="zoom-dialog" aria-labelledby="zoom-title"><div class="dialog-head"><p id="zoom-title"></p><button id="close-zoom" type="button">关闭 ✕</button></div><img id="zoomed-image" alt=""></dialog>
<script id="code-bundles" type="application/json">{code_payload}</script><script>{JS}</script></body></html>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8')
    manifest = {'date': '2026-11-16', 'html': OUTPUT.name, 'figures': len(figures),
        'source_figures': len(sources), 'code_sections': len(figures),
        'code_packages': len(code_manifest['entries']),
        'organization': 'One representative preview per figure family; source variants have text and code downloads only.',
        'image_integrity': 'Representative PNG bytes embedded unchanged; all source images retained and traceable.',
        'template_attachment_sha256': sha(archive),
        'all_code_attachment_sha256': code_manifest['all_bundle_sha256'],
        'entries': [{'id': f['id'], 'code': f['code'], 'title': f['title'],
                     'representative': f['source_code'], 'members': f['family']['members'],
                     'category': f['category'], 'source_category': f['source_category'], 'origin': f['origin'],
                     'image': str(f['image'].relative_to(ROOT)), 'sha256': f['sha256'],
                     'code_sha256': f['code_section']['code_sha256'],
                     'code_bundle_sha256': f['code_section']['bundle_sha256']} for f in figures],
        'source_entries': [{'id': f['id'], 'code': f['code'], 'title': f['title'],
                            'category': f['category'], 'origin': f['origin'],
                            'image': str(f['image'].relative_to(ROOT)), 'sha256': f['sha256'],
                            'code_sha256': f['code_section']['code_sha256'],
                            'code_bundle_sha256': f['code_section']['bundle_sha256']} for f in sources]}
    (ROOT / 'dist/all_figures_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'{OUTPUT}: {len(figures)} figure families, {len(sources)} source code packages; {OUTPUT.stat().st_size / 1024 / 1024:.2f} MiB.')


if __name__ == '__main__':
    build()
