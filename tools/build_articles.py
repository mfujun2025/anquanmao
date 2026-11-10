# -*- coding: utf-8 -*-
"""安全帽.cn · SEO 长文发布页构建器

用法：python tools/build_articles.py

输入：articles/<slug>.md （含 YAML frontmatter 的 Markdown 交付稿）
输出：blog/<slug>.html   （带完整 SEO meta / JSON-LD / 内链修正的发布页）

设计要点：
1. Meta Title / Description 以研究 Brief §9 的实测版为权威（50-60 / 150-160 中文字符，
   5 篇口径一致），不依赖撰稿人是否改写 frontmatter。
2. 正文里的站内相对链接在 blog/ 子目录下会失效，构建时统一补 ../ 前缀。
3. sitemap.xml 由 tools/build.py 的 extra_files() 自动扫描 blog/*.html 生成，本脚本不重复维护。
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "articles"
BLOG = ROOT / "blog"
BASE = "https://xn--15qt0wm7b.cn"

# ---- Brief §9 实测版 Meta（权威，勿改） ------------------------------------
META = {
    "safety-helmet-buying-guide": {
        "title": "安全帽怎么选？2026采购方必看的GB 2811-2019国标、材质对比、行业场景与到货验收五步全指南｜安全帽选购",
        "desc": "安全帽怎么选才合规又不花冤枉钱？本文面向采购方、工地安全员与个体用户，按查资质、定材质、对场景、看结构、做验收五步拆解GB 2811-2019执行要点，附四材质对照表、八类工况速查表与招标参数模板，并厘清生产许可证新政、2.5年与3.5年报废期限等高频疑问，帮你一次买对、验收不返工，也可按场景直接挑选合规安全帽。",
        "keyword": "安全帽怎么选", "cat": "选购指南", "read": "10 分钟",
    },
    "safety-helmet-lifespan-and-replacement": {
        "title": "安全帽使用期限是多久？塑料帽2.5年、玻璃钢帽3.5年强制报废与日常检查、清洗存放、正确佩戴五步全指南",
        "desc": "安全帽使用期限按材质区分：塑料帽不超过2.5年、玻璃钢帽不超过3.5年，自生产日期起算，受过一次重击即使外观完好也须报废。本文讲清强制报废期限怎么查、班前与季度检查清单、清洗存放四不要，以及查调留系护的正确佩戴五步法，说明安全帽不能替代骑行头盔、不能自行钻孔通风，并附六个高频问答与报废更换台账字段，方便安全员落地执行。",
        "keyword": "安全帽使用期限", "cat": "使用保养", "read": "9 分钟",
    },
    "gb-2811-2019-safety-helmet-standard": {
        "title": "GB 2811-2019安全帽国家标准全解读：12项新旧变化、P/T分类标记、帽壳6项永久标识与2024生产许可证新政",
        "desc": "安全帽国家标准要查哪几样？不少招标文件仍写LA强制或T1到T5分类，与现行规定不符。本文依据国标全文与市场监管总局2024年第25号公告，拆解GB 2811-2019较2007版的12项变化、P/T分类标记与帽壳6项永久标识，厘清2019年取消、2024年9月25日重启生产许可证的时间线，附招标参数模板与到货索证顺序。",
        "keyword": "安全帽国家标准", "cat": "标准法规", "read": "10 分钟",
    },
    "safety-helmet-material-comparison": {
        "title": "安全帽材质怎么选：ABS、HDPE、玻璃钢、PC四种材料抗冲击、耐温、绝缘与成本对照表（附回料识别·2026）",
        "desc": "安全帽材质直接决定防护上限与采购预算，市面批发价从6元到39元相差六倍。本文用一张对照表比较ABS、HDPE、玻璃钢与PC在抗冲击、耐温、绝缘、重量与价位上的表现，讲清GB 2811-2019禁止回料用于受力部件的规定与劣质帽识别特征，并按工地、电力、冶金、冷库给出结论，最后用三年周期算总账，避免只看单价买错帽子。",
        "keyword": "安全帽材质", "cat": "材质对比", "read": "9 分钟",
    },
    "safety-helmet-selection-by-industry": {
        "title": "不同行业安全帽选型指南：建筑、电力、石化、冶金、矿山、市政、冷库八类工况对照表与性能标记映射（2026）",
        "desc": "同样是安全帽，电力要电绝缘、石化要防静电、冶金要阻燃，一张单子买同一种最容易漏项。本文按建筑、电力、石化、冶金焊接、矿山隧道、市政交通、冷库极寒等八类工况，把作业风险映射到GB 2811-2019性能标记、材质与结构配置，附场景选型对照表，并点出跨行业借用、透气款误用于带电作业等五个常见错误，帮多工种项目一次配齐。",
        "keyword": "安全帽选型", "cat": "场景选型", "read": "9 分钟",
    },
}
# Brief §10 发布顺序：篇1 → 篇5 → 篇2 → 篇3 → 篇4
ORDER = [
    "safety-helmet-buying-guide",
    "safety-helmet-lifespan-and-replacement",
    "gb-2811-2019-safety-helmet-standard",
    "safety-helmet-material-comparison",
    "safety-helmet-selection-by-industry",
]

TITLES = {
    "safety-helmet-buying-guide": "安全帽怎么选：五步采购决策指南",
    "safety-helmet-lifespan-and-replacement": "安全帽使用期限与报废更换全指南",
    "gb-2811-2019-safety-helmet-standard": "GB 2811-2019 安全帽国家标准全解读",
    "safety-helmet-material-comparison": "ABS、HDPE 与玻璃钢材质对照",
    "safety-helmet-selection-by-industry": "按行业场景挑选安全帽",
}


# ---- Markdown 子集解析 -----------------------------------------------------
def inline(text):
    s = html.escape(text, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator(line):
    return bool(re.match(r"^\s*\|?[\s:\-\|]+\|[\s:\-\|]+$", line)) and "-" in line


def fix_links(fragment):
    """把正文中的站内相对链接修正为 blog/ 子目录下可用的路径。"""
    def repl(m):
        url = m.group(1)
        if url.startswith(("http://", "https://", "mailto:", "#", "../")):
            return m.group(0)
        if url.startswith("blog/"):
            return 'href="%s"' % url[len("blog/"):]
        if url.startswith(("index.html", "products/", "faq.html", "contact.html", "about.html", "assets/")):
            return 'href="../%s"' % url
        return m.group(0)
    return re.sub(r'href="([^"]+)"', repl, fragment)


def md_to_html(md):
    lines = md.split("\n")
    out, toc = [], []
    i, n = 0, len(lines)
    h2_no = 0
    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 代码围栏
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append('<pre><code class="lang-%s">%s</code></pre>' % (html.escape(lang), html.escape("\n".join(buf))))
            continue

        # 水平线
        if re.match(r"^\s*(---|\*\*\*|___)\s*$", stripped):
            out.append("<hr>"); i += 1; continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.+?)\s*#*\s*$", stripped)
        if m:
            level, text = len(m.group(1)), m.group(2)
            if level == 1:
                i += 1; continue   # H1 由模板输出
            if level == 2:
                h2_no += 1
                hid = "sec-%d" % h2_no
                toc.append((hid, re.sub(r"<[^>]+>", "", inline(text))))
                out.append('<h2 id="%s">%s</h2>' % (hid, inline(text)))
            else:
                out.append("<h%d>%s</h%d>" % (level, inline(text), level))
            i += 1; continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and is_separator(lines[i + 1]):
            header = split_row(stripped)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i])); i += 1
            th = "".join("<th>%s</th>" % inline(c) for c in header)
            tb = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in rows)
            out.append('<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, tb))
            continue

        # 引用
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(buf)))
            continue

        # 列表
        if re.match(r"^\s*([-*+]|\d+[.)])\s+", stripped):
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", stripped))
            items = []
            while i < n and re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[i].strip()):
                items.append(re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", lines[i].strip())); i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(x) for x in items), tag))
            continue

        # 段落（合并软换行）
        buf = [stripped]
        i += 1
        while i < n and lines[i].strip() and not re.match(
                r"^\s*(#{1,4}\s|>|\||```|---|\*\*\*|___|[-*+]\s|\d+[.)]\s)", lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))

    return fix_links("\n".join(out)), toc


def parse_frontmatter(md):
    meta = {}
    if md.startswith("---"):
        end = md.find("\n---", 3)
        if end > 0:
            for line in md[3:end].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            return meta, md[end + 4:].lstrip("\n")
    return meta, md


# ---- 页面模板 --------------------------------------------------------------
TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
<meta name="description" content="@@DESC@@">
<meta name="keywords" content="@@KEYWORD@@,安全帽,安全帽.cn,GB 2811-2019">
<meta name="author" content="安全帽.cn">
<link rel="canonical" href="@@CANONICAL@@">
<meta property="og:type" content="article">
<meta property="og:site_name" content="安全帽.cn">
<meta property="og:title" content="@@TITLE@@">
<meta property="og:description" content="@@DESC@@">
<meta property="og:url" content="@@CANONICAL@@">
<link rel="icon" type="image/svg+xml" href="../assets/img/favicon.svg">
<link rel="stylesheet" href="../assets/css/article.css">
<script type="application/ld+json">@@JSONLD@@</script>
</head>
<body>
<div class="topbar"><div class="container"><span>安全帽.cn · <b>按作业场景选安全帽</b></span><span>依据 GB 2811-2019 等公开标准整理 · 行业通用参考</span></div></div>
<header class="site-head"><div class="container">
<a class="brand" href="../index.html"><span class="brand-mark"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17a9 9 0 0 1 18 0"/><path d="M2 17h20v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-2Z"/><path d="M12 8v9"/></svg></span>安全帽.cn</a>
<nav class="nav"><a href="../index.html">商城首页</a><a href="../products/index.html">产品中心</a><a href="../faq.html">常见问题</a><a href="../contact.html#inquiry">业务咨询</a></nav>
<a class="back-shop" href="../index.html">返回商城 →</a>
</div></header>

<div class="container">
<div class="breadcrumb"><a href="../index.html">首页</a><span>/</span><a href="../index.html#articles">安全帽知识</a><span>/</span>@@CAT@@</div>
<div class="layout">
<main class="article">
<div class="article-meta"><span class="cat">@@CAT@@</span><span>约 @@READ@@</span><span>更新：2026-11-10</span><span>安全帽.cn 编辑部</span></div>
<h1>@@H1@@</h1>
@@BODY@@
<section class="related"><h3>延伸阅读 · 安全帽选型知识库</h3><div class="related-grid">@@RELATED@@</div></section>
<section class="cta-box"><h3>按场景挑合规安全帽</h3><p>看完标准与材质，回到产品中心按建筑施工、电力绝缘、工业防护、轻便透气四类场景核对规格；批量采购可提交作业场景与数量索取集中报价。</p><a href="../products/index.html">浏览产品中心 →</a></section>
<p class="disclaimer">本文依据 GB 2811-2019《头部防护 安全帽》等公开标准与监管信息整理，为行业通用参考，不构成对任何具体产品性能的承诺或认证声明。本站企业主体、资质、检测报告与报价均为占位资料，正式采购请以产品标识、型式检验报告与产品说明书为准。</p>
</main>
<aside class="toc"><h4>本文目录</h4><ol>@@TOC@@</ol>
<div class="toc-cta">需要选型清单或批量报价？<a href="../contact.html#inquiry">提交集采需求</a></div>
</aside>
</div>
</div>
<footer class="site-foot"><div class="container"><span>© 2026 <strong>安全帽.cn</strong> · 行业通用参考，企业资料待填写</span><span><a href="../index.html">商城首页</a> · <a href="../faq.html">常见问题</a> · <a href="../contact.html">联系我们</a></span></div></footer>
<script>
(function(){var links=[].slice.call(document.querySelectorAll('.toc a')),secs=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));}).filter(Boolean);
function mark(){var y=window.scrollY+140,cur=0;secs.forEach(function(s,i){if(s.offsetTop<=y)cur=i;});links.forEach(function(a,i){a.classList.toggle('active',i===cur);});}
window.addEventListener('scroll',mark,{passive:true});mark();})();
</script>
</body>
</html>
"""


def build():
    BLOG.mkdir(parents=True, exist_ok=True)
    built = []
    for slug in ORDER:
        src = ARTICLES / (slug + ".md")
        if not src.exists():
            print("  [跳过] 缺少源稿：%s" % src.name)
            continue
        meta, body_md = parse_frontmatter(src.read_text(encoding="utf-8"))
        m = META[slug]
        body_html, toc = md_to_html(body_md)
        h1 = meta.get("h1") or TITLES[slug]

        # 首段作为导语（若正文以 <p> 开头）
        lede = ""
        pm = re.match(r"\s*(<p>.*?</p>)", body_html, re.S)
        if pm:
            lede = '<div class="lede">%s</div>' % pm.group(1)
            body_html = body_html[pm.end():]

        toc_html = "".join('<li><a href="#%s">%s</a></li>' % (hid, html.escape(t)) for hid, t in toc)
        related = "".join(
            '<a href="%s.html"><small>%s</small>%s</a>' % (s, META[s]["cat"], html.escape(TITLES[s]))
            for s in ORDER if s != slug
        )

        canonical = "%s/blog/%s.html" % (BASE, slug)
        ld = [
            {"@context": "https://schema.org", "@type": "Article",
             "headline": m["title"], "description": m["desc"],
             "inLanguage": "zh-CN", "datePublished": "2026-11-10", "dateModified": "2026-11-10",
             "author": {"@type": "Organization", "name": "安全帽.cn"},
             "publisher": {"@type": "Organization", "name": "安全帽.cn"},
             "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}},
            {"@context": "https://schema.org", "@type": "BreadcrumbList",
             "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "首页", "item": BASE + "/index.html"},
                 {"@type": "ListItem", "position": 2, "name": "安全帽知识", "item": BASE + "/index.html#articles"},
                 {"@type": "ListItem", "position": 3, "name": m["cat"], "item": canonical}]}
        ]

        page = (TEMPLATE
                .replace("@@TITLE@@", html.escape(m["title"], quote=True))
                .replace("@@DESC@@", html.escape(m["desc"], quote=True))
                .replace("@@KEYWORD@@", html.escape(m["keyword"], quote=True))
                .replace("@@CANONICAL@@", canonical)
                .replace("@@JSONLD@@", json.dumps(ld, ensure_ascii=False))
                .replace("@@CAT@@", html.escape(m["cat"]))
                .replace("@@READ@@", m["read"])
                .replace("@@H1@@", html.escape(h1))
                .replace("@@BODY@@", lede + body_html)
                .replace("@@RELATED@@", related)
                .replace("@@TOC@@", toc_html))
        (BLOG / (slug + ".html")).write_text(page, encoding="utf-8")
        built.append(slug)
        print("  [生成] blog/%s.html  H2=%d  表格=%d  内链=%d" % (
            slug, len(toc), body_html.count("<table>"), len(re.findall(r'<a href="\.\./', body_html))))

    print("\n共生成 %d 个发布页。sitemap.xml 请运行 python tools/build.py 自动纳入 blog/*.html。" % len(built))
    return built


if __name__ == "__main__":
    build()
