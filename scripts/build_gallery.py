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
    usage_index='| 用途 | 示例 | 内容 |\n| --- | --- | --- |\n'
    for category in categories:
        group=[i for i in items if i['category']==category]
        usage_index+='| '+category.split(' · ',1)[-1]+' | '+'、'.join(i['id'].split('_')[0]for i in group)+' | '+'；'.join(i['title']for i in group)+' |\n'
    text=f'''# Research Figure Gallery · 论文图表模板库

按**论文中要说明什么**查找图，再打开图旁边的本地 Python 源码。当前保留 {len(items)} 张精选示例，均由本仓库代码生成，附有数据和运行命令。

本轮按视觉质量从 19 张中删去 9 张，优先保留层级清楚、配色克制、缩小后仍容易比较的例子。具体保留与删除理由见 [视觉筛选记录](CURATION.md)。沿用原编号，方便与此前版本对照。

**所有定量数值都是合成演示数据，不是当前实验结果。** 本库是自主实现的绘图模板，不声称复现参考论文的原始数值或原图代码。图形布局与图型的参考链接见各例及 [REFERENCES.md](REFERENCES.md)。代码采用 MIT 许可；参考项目与论文各自保留原许可。

![全部示例速览](assets/overview.png)

速览生成代码：[scripts/contact_sheet.py](scripts/contact_sheet.py)。完整大图、代码、数据按用途列在下方。

## 开始使用

Python 3.10+；只需 Matplotlib、NumPy 和 Pillow，不依赖 TeX、联网服务或专门绘图库。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python scripts/build_gallery.py
```

`requirements-lock.txt` 固定本次验证所用的三个直接依赖版本；`requirements.txt` 给出兼容范围，不是完整的传递依赖锁。演示 CSV 已提交，构建无需重新生成。

```bash
# 可选：用固定种子重新生成演示数据（会覆盖 data/demo 中的 CSV）
python scripts/generate_demo_data.py --seed 20261101 --questions 100
# 只重新出指定的图
python scripts/build_gallery.py --only 02_token_raincloud 17_ablation_forest
# 单图，换成自己的 CSV，并导出 PNG、SVG、PDF
python examples/08_query_paired_comparison/plot.py --data-dir /path/to/my_csv --output-dir /path/to/figures --formats png svg pdf
# 数据、统计边界与源码映射检查
python -m unittest discover -s tests -v
# 打包源码、数据与图片
python scripts/package_release.py
```

每张图的默认输入是 `data/demo/`，默认输出是 `assets/`。真实数据放到其他目录，并通过 `--data-dir` 指定；字段定义见 [data/README.md](data/README.md)。每个脚本包含具体绘图逻辑，共享样式及统计函数位于 [gallerylib/__init__.py](gallerylib/__init__.py)。若要替换为真实结果，请同时改掉 `save()` 的合成数据脚注，保留准确的数据来源和统计说明。

## 用途索引

{usage_index}

视觉上优先选用 **02 雨云图、04 横向占比图、08 哑铃图、17 消融森林图、19 主结果表**。针对当前 search / rerank 实验，主文还可选 12 效果—成本，按篇幅补 07 证据排名和 16 案例图。不要为了使用某种图而补造指标。

控制变量说明：这里将“100 字符”理解为 **search 与 rerank 返回给模型的内容长度统一**，并非 reranker 的输入长度。具体分词、截断与字符计数规则仍需在真实实验中记录。

'''
    for category in categories:
        text+=f"## {category}\n\n"
        for item in items:
            code=item['script'];identifier=item['id'];number=identifier.split('_')[0]
            text+=f"### {number} · {item['title']}\n\n{item['usage']}\n\n![{item['title']}——合成演示数据]({item['image']})\n\n"
            text+=f"**代码：[`{code}`]({code})** · [SVG 矢量图]({item['vector']})\n\n"
            text+='数据：'+('、'.join(f"[{Path(p).name}]({p})"for p in item['data'])if item['data']else'不读取数据，由代码定义流程节点。')+'\n\n'
            text+=f"```bash\npython {code}\n```\n\n{item['note']} [图型／布局参考]({item['reference']})。\n\n"
    text+='''## 文件结构与复现检查

```text
examples/*/plot.py                       # 每张保留示例对应一份实际绘图脚本
gallerylib/__init__.py                    # 共享样式、配对与统计函数
data/demo/*.csv                          # 9 张合成演示表
data/README.md                           # 字段、单位、统计口径
assets/*.png, *.svg                       # 精选图片及速览
gallery.json                             # 图片—源码—输入数据映射
CURATION.md                              # 本轮视觉筛选及删除理由
scripts/build_gallery.py                 # 运行测试、出图、生成 README 和校验记录
scripts/contact_sheet.py                 # 生成缩略图速览
scripts/package_release.py               # 打包交付
tests/test_contracts.py                   # 有意义的数据与统计契约检查
verification.json                        # 最近一次构建的版本、测试数、SHA-256
```

构建脚本会运行测试、检查每张 PNG/SVG 是否存在、检查 PNG 是否有可见内容，并记录源码、CSV 和图片摘要。图面排版仍需人工检查；本次已对速览和重点图进行检查。SVG 保留文字与矢量元素，投稿前按期刊尺寸、字体及分辨率调整。

当前目录是独立的本地 Git 仓库，可直接用 `git log` 查看提交记录。尚未配置远端。发布时可将整个目录推送到自己的 GitHub 仓库，README 中使用的相对图片和代码链接可直接工作。
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
