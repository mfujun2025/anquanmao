# -*- coding: utf-8 -*-
"""站点体检：标签闭合、内部链接、域名体现、结构化数据、违禁词、残留占位符。
运行：python tools/audit.py
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
SELF_CLOSING_OK = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse", "use", "stop"}

issues = []
warnings = []


class Checker(HTMLParser):
    def __init__(self, file):
        super().__init__(convert_charrefs=True)
        self.file = file
        self.stack = []
        self.links = []
        self.scripts = []
        self.in_ld = False
        self.ld_buf = ""
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src"):
            if a.get(k):
                self.links.append(a[k])
        if tag == "script" and a.get("type") == "application/ld+json":
            self.in_ld = True
            self.ld_buf = ""
        if tag == "title":
            self.in_title = True
        if tag not in VOID and tag not in SELF_CLOSING_OK:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src"):
            if a.get(k):
                self.links.append(a[k])

    def handle_endtag(self, tag):
        if tag == "script" and self.in_ld:
            try:
                json.loads(self.ld_buf)
            except Exception as e:
                issues.append("%s: JSON-LD 解析失败 %s" % (self.file, e))
            self.in_ld = False
        if tag == "title":
            self.in_title = False
        if tag in VOID or tag in SELF_CLOSING_OK:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                issues.append("%s: 标签未闭合 </%s>" % (self.file, self.stack.pop()))
            if self.stack:
                self.stack.pop()
        else:
            issues.append("%s: 多余的闭合标签 </%s>" % (self.file, tag))

    def handle_data(self, data):
        if self.in_ld:
            self.ld_buf += data
        if self.in_title:
            self.title += data


pages = sorted([p for p in ROOT.rglob("*.html") if "tools" not in p.parts])
print("检查 %d 个 HTML 页面" % len(pages))

all_local_targets = set()
for p in pages:
    c = Checker(p.relative_to(ROOT).as_posix())
    c.feed(p.read_text(encoding="utf-8"))
    for t in c.stack:
        issues.append("%s: 文档结束时标签未闭合 </%s>" % (c.file, t))

    rel = p.relative_to(ROOT).as_posix()
    text = p.read_text(encoding="utf-8")

    # 新旧模板分组：商城首页与 blog 长文页使用新版前端，旧模板专属结构不再适用
    is_modern = rel == "index.html" or rel.startswith("blog/")

    # 品牌 / 域名体现（所有页面）
    brand_ok = ("安全帽.cn" in c.title or
                'property="og:site_name" content="安全帽.cn"' in text or
                "xn--15qt0wm7b.cn" in text)
    if not brand_ok:
        issues.append("%s: 页面未体现品牌/域名" % rel)

    if not is_modern:
        # 旧模板专属检查：导航 / 页脚域名、独立转化、浮动咨询、信任条、结构类名
        if 'class="nav-domain"' not in text or "安全帽.cn" not in text.split('class="nav-domain"')[1][:160]:
            issues.append("%s: 导航未体现域名" % rel)
        if "footer-bottom" not in text or "安全帽.cn" not in text.split('class="footer-bottom"')[1][:400]:
            issues.append("%s: 页脚未体现域名" % rel)
        if "cta-band" not in text:
            issues.append("%s: 缺少独立转化区" % rel)
        if "floating-consult" not in text:
            issues.append("%s: 缺少浮动咨询入口" % rel)
        if rel != "404.html" and "trust-strip" not in text:
            issues.append("%s: 缺少信任条" % rel)
        for key in ('class="topbar"', 'class="navbar"', 'id="main"', 'class="site-footer"'):
            if key not in text:
                issues.append("%s: 缺少结构 %s" % (rel, key))

    # 所有页面通用：有且仅有一个 H1，且必须有主内容区
    if text.count("<h1") != 1:
        issues.append("%s: H1 数量为 %d（应为 1）" % (rel, text.count("<h1")))
    if 'id="main"' not in text and "<main" not in text:
        issues.append("%s: 缺少主内容区" % rel)

    # 残留占位 / 表情符号
    for bad in ("%s", "%d", "{{", "undefined", "[object Object]", ">None<"):
        if bad in text:
            issues.append("%s: 残留 %s" % (rel, bad))
    if re.search(r"[\U0001F300-\U0001FAFF\uFE0F\u2600-\u27BF]", text):
        issues.append("%s: 检测到 Emoji 字符（应使用 SVG 图标）" % rel)

    # 内部链接
    for href in c.links:
        h = href.strip()
        if h.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:", "//")):
            continue
        path_part = unquote(h.split("#")[0].split("?")[0])
        if not path_part:
            continue
        target = (p.parent / path_part).resolve()
        all_local_targets.add(target)
        if not target.exists():
            issues.append("%s: 链接目标不存在 -> %s" % (rel, h))

# 广告法绝对化用语扫描（序数词「第一步」等不作为宣传用语）
BANNED = ["最好", "最佳", "最强", "最优", "最先进", "最专业", "唯一", "顶级",
          "国家级", "100%", "零风险", "稳赚", "包治", "绝对领先", "行业第一", "首选品牌"]
for p in pages:
    text = p.read_text(encoding="utf-8")
    for w in BANNED:
        if w in text:
            issues.append("%s: 出现绝对化用语「%s」" % (p.relative_to(ROOT).as_posix(), w))

# 附加文件
for f in ("robots.txt", "sitemap.xml", "llms.txt", "CNAME", ".nojekyll",
          "assets/css/style.css", "assets/js/main.js", "assets/img/favicon.svg"):
    if not (ROOT / f).exists():
        issues.append("缺少文件 %s" % f)

try:
    ET.parse(ROOT / "sitemap.xml")
    print("sitemap.xml XML 合法")
except Exception as e:
    issues.append("sitemap.xml 非法: %s" % e)

cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
if cname != "xn--15qt0wm7b.cn":
    issues.append("CNAME 内容异常: %s" % cname)

# SVG 合法性
for svg in sorted((ROOT / "assets/img").glob("*.svg")):
    try:
        ET.parse(svg)
    except Exception as e:
        issues.append("SVG 非法 %s: %s" % (svg.name, e))

# 统计
html_total = sum(p.stat().st_size for p in pages)
print("HTML 合计 %.1f KB，内部链接目标 %d 个" % (html_total / 1024, len(all_local_targets)))
print("本地存在的链接目标 %d 个，缺失 %d 个" %
      (sum(1 for t in all_local_targets if t.exists()), sum(1 for t in all_local_targets if not t.exists())))

if warnings:
    print("\n提示：")
    for w in warnings:
        print("  !", w)

if issues:
    print("\n发现 %d 个问题：" % len(issues))
    for i in issues:
        print("  -", i)
    sys.exit(1)
print("\n体检通过：无结构、链接、域名体现、结构化数据与合规问题。")
