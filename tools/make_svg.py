# -*- coding: utf-8 -*-
"""生成站内 SVG 线稿示意图（安全帽分类图、首屏插画、favicon）。

v2 视觉：暖白底 + 墨黑线稿 + 安全橙点缀，工业技术手册风。
全部为原创几何示意插画，非实物照片，不含任何企业资料。
运行：python tools/make_svg.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
IMG.mkdir(parents=True, exist_ok=True)

LINE = "#17191C"
ACCENT = "#FF5A1F"
FILL = "#F8F7F3"

HELMET_BODY = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 220" role="img" aria-labelledby="ht hd">
<title id="ht">__TITLE__</title>
<desc id="hd">安全帽分类线稿示意插画，非实物照片，实际外观以产品实物为准</desc>
<g fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M36 142 C36 70 90 26 160 26 C230 26 284 70 284 142 L284 150 L36 150 Z" fill="__FILL__" stroke="__LINE__" stroke-width="2.4"/>
<path d="M160 26 L160 150 M112 32 C100 70 96 110 96 150 M208 32 C220 70 224 110 224 150" stroke="__LINE__" stroke-width="1.2" opacity=".26"/>
<path d="M126 30 Q160 23 194 30" stroke="__ACCENT__" stroke-width="5"/>
<path d="M22 148 Q160 136 298 148 Q308 150 300 162 Q160 178 20 162 Q12 150 22 148 Z" fill="__ACCENT__" stroke="__LINE__" stroke-width="2.2"/>
<path d="M34 153 Q160 143 286 153" stroke="#FFFFFF" stroke-width="1.4" opacity=".5"/>
<path d="M60 162 Q66 200 160 205 Q254 200 260 162" stroke="__LINE__" stroke-width="1.5" stroke-dasharray="6 7" opacity=".4"/>
__EXTRA__
</g>
<text x="288" y="206" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="__ACCENT__" opacity=".9">__NUM__</text>
</svg>
"""

VARIANTS = {
    "helmet-yellow": {
        "title": "建筑施工安全帽线稿示意图",
        "num": "01",
        "extra": '<rect x="146" y="88" width="28" height="28" stroke="__LINE__" stroke-width="1.6" opacity=".4"/>'
                 '<path d="M153 102 l5 5 l9 -11" stroke="__ACCENT__" stroke-width="2.2"/>',
    },
    "helmet-blue": {
        "title": "电力绝缘安全帽线稿示意图",
        "num": "02",
        "extra": '<path d="M163 80 l-13 22 h10 l-4 18 15 -24 h-10 l6 -16 z" stroke="__ACCENT__" stroke-width="2"/>',
    },
    "helmet-red": {
        "title": "工业防护安全帽线稿示意图",
        "num": "03",
        "extra": '<path d="M36 120 C24 122 20 138 24 152" stroke="__LINE__" stroke-width="1.7"/>'
                 '<rect x="18" y="118" width="12" height="30" rx="3" stroke="__LINE__" stroke-width="1.7"/>'
                 '<path d="M284 120 C296 122 300 138 296 152" stroke="__LINE__" stroke-width="1.7"/>'
                 '<rect x="290" y="118" width="12" height="30" rx="3" stroke="__LINE__" stroke-width="1.7"/>',
    },
    "helmet-white": {
        "title": "轻便透气安全帽线稿示意图",
        "num": "04",
        "extra": '<path d="M118 62 h18 M110 76 h18 M184 62 h18 M192 76 h18" stroke="__LINE__" stroke-width="2" opacity=".5"/>'
                 '<path d="M152 48 h16" stroke="__ACCENT__" stroke-width="2.4"/>',
    },
}


def render(template, title, num, extra):
    return (template.replace("__TITLE__", title)
                    .replace("__NUM__", num)
                    .replace("__EXTRA__", extra)
                    .replace("__FILL__", FILL)
                    .replace("__LINE__", LINE)
                    .replace("__ACCENT__", ACCENT))


for name, v in VARIANTS.items():
    (IMG / (name + ".svg")).write_text(render(HELMET_BODY, v["title"], v["num"], v["extra"]), encoding="utf-8")

# 首屏插画：抽取一顶线稿安全帽（不带编号）放大后置于建筑线稿场景中央
inner = (HELMET_BODY.replace('xmlns="http://www.w3.org/2000/svg" ', "")
         .replace('viewBox="0 0 320 220" role="img" aria-labelledby="ht hd"', "")
         .replace('<title id="ht">__TITLE__</title>', "")
         .replace('<desc id="hd">安全帽分类线稿示意插画，非实物照片，实际外观以产品实物为准</desc>', "")
         .replace('<text x="288" y="206" text-anchor="end" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="__ACCENT__" opacity=".9">__NUM__</text>', "")
         .replace("<svg", "<g").replace("</svg>", "</g>"))
inner = render(inner, "", "", "")

GRID = "\n".join(
    ['<path d="M%d 0V460" stroke="#EDEAE3" stroke-width="1"/>' % x for x in range(40, 640, 40)] +
    ['<path d="M0 %dH640" stroke="#EDEAE3" stroke-width="1"/>' % y for y in range(40, 460, 40)]
)

BUILDINGS = """<g fill="none" stroke="#D6D2C8" stroke-width="1.6" stroke-linejoin="round">
<path d="M24 426V288h88v138 M112 426V236h68v190 M180 426V314h106v112 M424 426V272h74v154 M498 426V228h64v198 M562 426V306h56v120"/>
<path d="M24 426H620"/>
<path d="M40 310h16v18H40z M70 310h16v18H70z M100 310h0 M40 344h16v18H40z M70 344h16v18H70z"/>
<path d="M128 258h14v18h-14z M152 258h14v18h-14z M128 292h14v18h-14z M152 292h14v18h-14z"/>
<path d="M198 334h18v18h-18z M228 334h18v18h-18z M258 334h18v18h-18z"/>
<path d="M440 294h16v18h-16z M468 294h16v18h-16z M440 328h16v18h-16z M468 328h16v18h-16z"/>
<path d="M514 250h14v18h-14z M538 250h14v18h-14z M514 284h14v18h-14z M538 284h14v18h-14z"/>
</g>
<g fill="none" stroke="#B9B5AC" stroke-width="2" stroke-linecap="round">
<path d="M392 226V78 M392 78H566 M424 78V108 M392 94H486 M566 78V120"/>
<path d="M486 94V120"/>
</g>
"""

HERO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 460" role="img" aria-labelledby="sh sd">
<title id="sh">安全防护主题线稿插画</title>
<desc id="sd">建筑工地线稿与一顶安全帽线稿组成的原创示意插画，用于首页首屏视觉，非实物照片</desc>
<rect width="640" height="460" fill="#FFFFFF"/>
%s
<circle cx="320" cy="226" r="172" fill="#FFF1E9"/>
<circle cx="320" cy="226" r="172" fill="none" stroke="#F7D6C4" stroke-width="1.5"/>
%s
<g transform="translate(80 62) scale(1.5)">
%s
</g>
<rect x="0" y="0" width="8" height="88" fill="#FF5A1F"/>
<rect x="40" y="26" width="88" height="5" fill="#17191C"/>
<rect x="40" y="38" width="52" height="3" fill="#D6D2C8"/>
<rect x="540" y="426" width="68" height="5" fill="#FF5A1F"/>
</svg>
""" % (GRID, BUILDINGS, inner)
(IMG / "hero-scene.svg").write_text(HERO, encoding="utf-8")

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#17191C"/>
<path d="M12 40 C12 24 21 15 32 15 C43 15 52 24 52 40 L52 43 L12 43 Z" fill="none" stroke="#FF5A1F" stroke-width="2.4" stroke-linejoin="round"/>
<path d="M8 43 Q32 39 56 43 Q58 44 56 48 Q32 53 8 48 Q6 44 8 43 Z" fill="#FF5A1F"/>
<path d="M32 15 V43" stroke="#FF5A1F" stroke-width="1.5" opacity=".55"/>
<path d="M20 46 Q22 56 32 57 Q42 56 44 46" fill="none" stroke="#FF5A1F" stroke-width="1.4" stroke-dasharray="3 3" opacity=".7"/>
</svg>
"""
(IMG / "favicon.svg").write_text(FAVICON, encoding="utf-8")

print("v2 线稿 SVG 已生成：", ", ".join(sorted(p.name for p in IMG.glob("*.svg"))))
