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

OUTPUT = ROOT / 'dist/图表汇总_2026-11-16.html'
GITHUB = ROOT / 'github_references/2026-11-15'
TEMPLATES = ROOT / 'rerank_templates/2026-11-16'
H = html.escape
CATEGORIES = {
    'templates': ('01', '可运行的 Rerank 模板', '最新三张模板：共享逐题 CSV 与 JSON 配置，可导出 PNG、SVG、PDF 和实际绘图数值。'),
    'selected': ('02', '精选图库', '按当前研究问题筛选的 15 张图，保留原有说明和来源。'),
    'supplement': ('03', '补充图库', '8 张专项与附录参考，保留各自的适用范围和暂未进入主图库的理由。'),
    'github': ('04', 'GitHub 原图参考', '8 个仓库中的原始示例，均有固定版本来源与对应代码。'),
}


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
    return f'''<section class="code-section" aria-label="{H(item['title'])}的代码">
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
        if item['code'] == 'G08':
            detail.append('<p>' + link('https://creativecommons.org/licenses/by-nc-sa/4.0/', 'CC BY-NC-SA 4.0') + '。Nicolas P. Rougier 原 PDF 的栅格预览，内容未改动。</p>')
        detail.append(f'<details class="license"><summary>许可全文</summary><pre>{H(item["license_text"])}</pre></details>')
    detail.append(f'<p>原始标识：<code>{H(item.get("original_id", item["code"]))}</code><br>图片 SHA256：<code>{item["sha256"]}</code></p>')
    limits = f'<p class="limits"><b>使用边界</b>　{H(item["limits"])}</p>' if item['limits'] else ''
    requirements = f'<p><b>需要数据</b>　{H(item["data_requirement"])}</p>' if item.get('data_requirement') else ''
    extra = f'<p class="extra">{H(item["extra"])}</p>' if item.get('extra') else ''
    search = ' '.join([item['code'], item['title'], item['purpose'], item['source_label'], item.get('original_id', '')])
    return f'''<article class="figure-card" id="{item['id']}" data-category="{item['category']}" data-search="{H(search)}">
<header class="card-header"><span class="number">{item['code']}</span><div><span class="badge {item['origin']}">{H(item['badge'])}</span><h3>{H(item['title'])}</h3></div></header>
<figure><button class="zoom-image" type="button" aria-label="放大 {H(item['title'])}"><img loading="lazy" src="data:image/png;base64,{image_data}" width="{item['width']}" height="{item['height']}" alt="{H(item['title'])} · {H(item['badge'])}"></button><figcaption>{H(item.get('transformation', '保留当前成图，未重新计算或改动画面。'))} <span>{item['width']} × {item['height']} px</span></figcaption></figure>
<div class="card-body"><p class="purpose">{H(item['purpose'])}</p>{requirements}{limits}{extra}<p class="sources">来源：{sources}</p><div class="actions"><button type="button" class="view-full">放大查看</button><button type="button" class="download-image">下载此图 PNG</button><a href="#top">返回顶部 ↑</a></div>{code_section(item)}<details class="provenance"><summary>来源定位与文件信息</summary>{''.join(detail)}</details></div></article>'''


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

JS = '''
const cards=[...document.querySelectorAll('.figure-card')];
const search=document.getElementById('search');
const filterButtons=[...document.querySelectorAll('[data-filter]')];
let category='all';
function applyFilter(){
 const query=search.value.trim().toLocaleLowerCase();let visible=0;
 for(const card of cards){card.hidden=!((category==='all'||card.dataset.category===category)&&card.dataset.search.toLocaleLowerCase().includes(query));if(!card.hidden)visible++;document.querySelector(`[data-target="${card.id}"]`).hidden=card.hidden;}
 for(const section of document.querySelectorAll('.figure-section'))section.hidden=![...section.querySelectorAll('.figure-card')].some(card=>!card.hidden);
 for(const button of filterButtons)button.setAttribute('aria-pressed',String(button.dataset.filter===category));
 document.getElementById('visible-count').textContent=`显示 ${visible} / ${cards.length} 张图`;
 document.getElementById('empty').hidden=visible!==0;
}
search.addEventListener('input',applyFilter);
for(const button of filterButtons)button.addEventListener('click',()=>{category=button.dataset.filter;applyFilter()});
document.getElementById('reset').addEventListener('click',()=>{category='all';search.value='';applyFilter()});
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
document.getElementById('close-zoom').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
function download(url,name){const a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove()}
function downloadBlob(blob,name){const url=URL.createObjectURL(blob);download(url,name);setTimeout(()=>URL.revokeObjectURL(url),30000)}
function downloadArchive(payload){const bytes=Uint8Array.from(atob(payload.data),c=>c.charCodeAt(0));downloadBlob(new Blob([bytes],{type:'application/zip'}),payload.filename)}
document.getElementById('download-templates').addEventListener('click',()=>downloadArchive(JSON.parse(document.getElementById('template-bundle').textContent)));
document.getElementById('download-all-code').addEventListener('click',()=>downloadArchive(bundles.all));
applyFilter();
'''


def build():
    figures = collect()
    code_manifest, combined_code = attach_code_sections(figures)
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
    sections = []
    for category, (number, title, description) in CATEGORIES.items():
        members = [f for f in figures if f['category'] == category]
        sections.append(f'<section class="figure-section" data-section="{category}"><div class="section-header"><span class="section-number">SECTION {number}</span><h2>{H(title)} <small>· {len(members)}</small></h2><p>{H(description)}</p></div>{"".join(card(f) for f in members)}</section>')
    buttons = [('all', '全部', 34), ('templates', '可运行模板', 3), ('selected', '精选图库', 15), ('supplement', '补充图库', 8), ('github', 'GitHub 原图', 8)]
    filters = ''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(key == "all").lower()}">{label} {count}</button>' for key, label, count in buttons)
    payload = json.dumps({'filename': 'rerank-plot-templates.zip', 'data': base64.b64encode(archive.read_bytes()).decode()})
    code_payloads = {item['id']: {'filename': item['code_section']['bundle_filename'], 'data': base64.b64encode(item['code_section']['bundle_bytes']).decode()} for item in figures}
    code_payloads['all'] = {'filename': 'all-figure-code.zip', 'data': base64.b64encode(combined_code).decode()}
    code_payload = json.dumps(code_payloads)
    result = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rerank 科研图表汇总 · 34 张</title><style>{CSS}</style></head><body><main id="top">
<header><span class="eyebrow">RERANK RESEARCH · FIGURES + CODE · 2026.11.16</span><h1>Rerank 科研图表汇总</h1><p class="lead">34 张图，每张都有可阅读、复制和下载的代码。最新可运行模板在最前，随后是精选图库、补充图库与 GitHub 原图参考。</p><div class="counts"><span><b>34</b> 张图与代码</span><span><b>26</b> 个本地运行包</span><span><b>8</b> 个上游源码参考包</span></div></header>
<div class="notice">所有图片已内嵌，可单独保存、离线浏览、放大和下载。各图明确区分论文公开数据、合成演示和上游示例；当前汇总不含我们的实测实验结果。此前删除的冗余模板和重复总览拼图没有重新收录。</div>
<div class="bundle"><button id="download-all-code" type="button">下载全部 34 张图的代码与数据包</button><button id="download-templates" class="secondary" type="button">下载最新 3 个 Rerank 模板</button><small>全部代码包 {len(combined_code) / 1024 / 1024:.2f} MiB · 每图代码部分附运行说明、依赖和输入格式。8 个上游示例标明未在本项目执行。</small></div>
<noscript><p class="noscript">浏览器禁用了 JavaScript，全部图片仍可阅读；启用后可筛选、放大和下载内嵌文件。</p></noscript>
<div class="toolbar"><div class="searchline"><input id="search" type="search" aria-label="搜索图表" placeholder="搜索图名、用途或来源，例如：雨云、召回、RankRAG"><button id="reset" type="button">重置</button></div><div class="filter-buttons">{filters}</div><p class="count-line" id="visible-count" aria-live="polite">显示 34 / 34 张图</p></div>
<details class="toc"><summary>展开全部图表目录</summary><div class="toc-links">{toc}</div></details><p class="empty" id="empty" hidden>没有匹配的图表。可清空关键词或切换分类。</p>
{''.join(sections)}
<footer><p>汇总日期：2026-11-16。原有图库 23 张（15 精选、8 补充）＋GitHub 原图 8 张＋新模板预览 3 张＝34 张。所有原图保持不变。每图均有完整主脚本或从固定上游版本提取的对应示例，另附数据格式、依赖及说明。</p><p>26 个本地运行包保留主脚本、公共函数和输入 CSV；8 个上游参考包保留摘取代码、原始源码快照和许可，未在本项目执行。上游 API、库版本或随机状态可能影响重跑结果，不能将现有 GitHub 原图当成本地重跑输出。</p><p>此文件内嵌全部图片、代码及 ZIP，无外部图片、字体或脚本依赖；上游来源链接需要联网。复制单个主脚本时应同时保留相应公共函数和数据，直接运行请下载对应完整包。浏览器打印会包含当前筛选图表的代码。</p></footer>
</main><dialog id="zoom-dialog" aria-labelledby="zoom-title"><div class="dialog-head"><p id="zoom-title"></p><button id="close-zoom" type="button">关闭 ✕</button></div><img id="zoomed-image" alt=""></dialog>
<script id="template-bundle" type="application/json">{payload}</script><script id="code-bundles" type="application/json">{code_payload}</script><script>{JS}</script></body></html>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8')
    manifest = {'date': '2026-11-16', 'html': OUTPUT.name, 'figures': len(figures),
        'categories': {key: sum(f['category'] == key for f in figures) for key in CATEGORIES},
        'image_integrity': 'Original PNG bytes embedded unchanged; no overview mosaics or removed figures.',
        'template_attachment_sha256': sha(archive),
        'code_sections': len(code_manifest['entries']), 'all_code_attachment_sha256': code_manifest['all_bundle_sha256'],
        'entries': [{'id': f['id'], 'title': f['title'], 'category': f['category'], 'origin': f['origin'],
                     'image': str(f['image'].relative_to(ROOT)), 'sha256': f['sha256'],
                     'code_sha256': f['code_section']['code_sha256'],
                     'code_bundle_sha256': f['code_section']['bundle_sha256']} for f in figures]}
    (ROOT / 'dist/all_figures_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'{OUTPUT}: {len(figures)} figures, {OUTPUT.stat().st_size / 1024 / 1024:.2f} MiB; all images and template ZIP embedded.')


if __name__ == '__main__':
    build()
