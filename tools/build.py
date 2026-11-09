# -*- coding: utf-8 -*-
"""安全帽.cn 官网静态页面生成器。

输出零依赖的纯静态 HTML（内容全部写在 HTML 里，便于百度与 AI 爬虫抓取）。
运行：python tools/build.py

重要约定：
- 所有企业具体信息（企业全称、电话、地址、资质、年限、案例、数据）一律使用 [方括号占位]，
  不编造任何企业资料；行业通用选型知识单独标注为「通用参考」。
- 中文域名「安全帽.cn」出现在页面标题、导航与页脚；canonical/sitemap 使用 punycode。
"""
from pathlib import Path
from datetime import date
import json

ROOT = Path(__file__).resolve().parent.parent
SITE = "安全帽.cn"
PUNY = "xn--15qt0wm7b.cn"
BASE = "https://" + PUNY
MAIL = "mfujun@agent.qq.com"
REPO = "https://github.com/mfujun2025/anquanmao"
TODAY = date.today().isoformat()

# ---------------------------------------------------------------- 图标库
ICON_PATHS = {
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.4 2.1L8 9.8a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.9 2.1Z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/>',
    "location": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "check": '<path d="m20 6-11 11-5-5"/>',
    "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "hardhat": '<path d="M3 17a9 9 0 0 1 18 0"/><path d="M2 17h20v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-2Z"/><path d="M12 8v9"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 21v-4h6v4M8 7h2M14 7h2M8 11h2M14 11h2"/>',
    "bolt": '<path d="m13 2-9 12h7l-1 8 9-12h-7l1-8Z"/>',
    "factory": '<path d="M3 21V9l6 4V9l6 4V5l6 4v12H3Z"/><path d="M7 17h2M13 17h2M19 17h1"/>',
    "certificate": '<circle cx="12" cy="9" r="5"/><path d="m9 13-2 8 5-3 5 3-2-8"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0M16 5a3 3 0 0 1 0 6M17 14a6 6 0 0 1 4 6"/>',
    "document": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6Z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
    "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="2" y="13" width="4" height="6" rx="1"/><rect x="18" y="13" width="4" height="6" rx="1"/><path d="M20 19a4 4 0 0 1-4 4h-2"/>',
    "truck": '<path d="M3 6h11v10H3zM14 9h4l3 3v4h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5 5L3 18l3 3 6.7-6.7a4 4 0 0 0 5-5l-3 3-2.8-2.8 3-3Z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18Z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "alert": '<path d="M12 3 2 20h20L12 3Z"/><path d="M12 9v5M12 17h.01"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2h6v2M9 10h6M9 14h6"/>',
    "layers": '<path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/>',
    "refresh": '<path d="M20 11a8 8 0 1 0-2 6"/><path d="M20 4v7h-7"/>',
    "tag": '<path d="M20 12 12 20 3 11V3h8l9 9Z"/><circle cx="7.5" cy="7.5" r="1.2"/>',
    "ruler": '<path d="m3 15 6-6 6 6-6 6-6-6Z"/><path d="m9 9 12-6 0 6-6 6"/>',
}

SPRITE = '<svg class="sprite" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">' + "".join(
    '<symbol id="i-%s" viewBox="0 0 24 24">%s</symbol>' % (k, v) for k, v in ICON_PATHS.items()
) + "</svg>"


def ico(name, cls="icon"):
    return '<svg class="%s" aria-hidden="true"><use href="#i-%s"></use></svg>' % (cls, name)


# ---------------------------------------------------------------- 产品数据
PRODUCTS = {
    "construction": {
        "name": "建筑施工安全帽",
        "short": "面向房屋建筑、市政工程等一般高处与交叉作业场景的头部防护选型。",
        "img": "helmet-yellow.svg",
        "tags": ["建筑工地", "高处作业", "交叉施工"],
        "features": [
            "按作业风险等级确认所需类别，核对产品标识与执行标准。",
            "关注帽壳材质、帽衬结构与缓冲间距，具体参数以检测报告为准。",
            "确认后箍调节范围与下颏带配置，适配不同佩戴者头围。",
            "建立进场验收、日常检查与到期更换记录，周期以产品说明书为准。",
        ],
        "scenes": [
            ("房屋建筑施工", "主体结构、砌筑与装饰阶段的现场作业人员头部防护。"),
            ("市政与路桥工程", "道路、管网、桥梁等露天及多工种交叉作业环境。"),
            ("安装与检修", "设备安装、管线敷设及临时检修作业现场。"),
        ],
    },
    "electrical": {
        "name": "电力绝缘安全帽",
        "short": "面向带电作业、配电运维等存在电击风险场景的头部防护选型。",
        "img": "helmet-blue.svg",
        "tags": ["带电作业", "配电运维", "绝缘性能"],
        "features": [
            "确认产品是否标注相应的电绝缘性能等级，等级与适用电压范围以产品标识为准。",
            "核对执行标准与检测报告，避免以普通帽替代带电作业用帽。",
            "检查帽壳是否存在划伤、裂纹、变形，绝缘类用品应单独存放与定期检验。",
            "与其他绝缘防护用具配套使用，作业流程遵循单位安全管理制度。",
        ],
        "scenes": [
            ("配电房与变电站运维", "设备巡检、倒闸操作及日常维护作业。"),
            ("电力线路施工", "架空线路、电缆敷设及相关带电或近电作业。"),
            ("工矿企业电气检修", "厂内配电系统、机电设备的停电与近电检修。"),
        ],
    },
    "industrial": {
        "name": "工业防护安全帽",
        "short": "面向制造、矿山、化工等存在坠物与碰撞风险场景的头部防护选型。",
        "img": "helmet-red.svg",
        "tags": ["制造业", "矿山", "化工"],
        "features": [
            "按现场坠物、碰撞、侧向挤压等风险识别所需性能类别。",
            "关注帽壳强度、帽衬缓冲结构与配件兼容性（面屏、耳罩、照明）。",
            "特殊环境需核对耐温、耐腐蚀或阻燃等附加性能，以检测报告为准。",
            "明确清洁、存放与报废规则，受冲击或出现老化迹象应及时更换。",
        ],
        "scenes": [
            ("机械制造与装配", "车间吊装、设备装配与物料搬运区域。"),
            ("矿山与采掘", "井下及露天采掘、支护与运输作业。"),
            ("化工与仓储", "装置区巡检、罐区作业及立体仓库存取作业。"),
        ],
    },
    "lightweight": {
        "name": "轻便透气安全帽",
        "short": "面向长时间佩戴、高温或需频繁移动场景的头部防护选型。",
        "img": "helmet-white.svg",
        "tags": ["长时间佩戴", "高温环境", "巡检"],
        "features": [
            "在满足对应防护类别前提下，关注整帽重量与佩戴舒适性的平衡。",
            "核对通风结构设计是否影响所需防护性能，以产品标识与检测报告为准。",
            "确认头围调节、吸汗衬垫与下颏带的可更换性与清洁方式。",
            "高温环境应结合作业轮换与休息制度，用品检查周期按说明书执行。",
        ],
        "scenes": [
            ("园区与厂区巡检", "长距离、多频次巡查及日常点位检查。"),
            ("高温季节露天作业", "夏季户外施工、物流装卸等连续佩戴场景。"),
            ("物业与设施维护", "机电、暖通、公共设施维修与安装作业。"),
        ],
    },
}

# 规格表：行业通用参考值（依据 GB 2811-2019 等公开标准与监管信息整理），
# 不是本企业产品参数，也不代表任何具体型号已通过认证。
SPEC_BASE = [
    ("产品型号", "本页为分类展示页，非具体型号；型号清单请提交咨询索取"),
    ("执行标准", "通用参考：GB 2811-2019《头部防护 安全帽》（2020-07-01 实施），以帽壳内侧永久标识为准"),
    ("帽壳材质", "通用参考：ABS、HDPE（PE）等常见塑料材质，以产品标识为准"),
    ("帽衬结构", "通用参考：由帽壳、帽衬与下颏带等组成，帽衬与帽壳之间需保留缓冲间距"),
    ("下颏带 / 后箍", "通用参考：下颏带应系紧，后箍或旋钮式调节用于适配头围；配置以产品实物为准"),
    ("头围调节范围", "通用参考：市面常见标注约 52–64 cm，采购前按佩戴人员头围核对"),
    ("整帽重量", "通用参考：普通型常见约 300–430 g；重量过轻可能意味着壁厚不足，以产品标识为准"),
    ("可选颜色", "通用参考：黄、红、蓝、白为常见作业区分色，具体色号以企业色卡为准"),
    ("参考价格", "以报价单为准；请提交咨询说明场景与数量后索取"),
    ("使用与更换周期", "通用参考：塑料 / 纸胶帽自制造完成起不超过 2.5 年，玻璃钢 / 橡胶帽不超过 3.5 年；受冲击、开裂或老化应立即更换"),
    ("配套附件", "通用参考：面屏、耳罩、照明等，需确认与原帽兼容且不影响防护性能"),
    ("检测报告与资质", "待企业填写：型式检验报告、生产许可证编号与标志（自 2024-09-25 起纳入许可证管理）"),
]

# 各分类在通用值之上的差异项
SPEC_BY_SLUG = {
    "construction": {
        "帽壳材质": "通用参考：ABS 或 HDPE 帽壳，韧性与抗冲击性较均衡；以产品标识为准",
        "配套附件": "通用参考：可配下颏带、吸汗衬垫；高处作业优先确认帽衬缓冲与标识完整",
    },
    "electrical": {
        "帽壳材质": "通用参考：需选用标注电绝缘性能的产品，避免以普通帽替代；等级以产品标识与检测报告为准",
        "帽衬结构": "通用参考：电绝缘类用品避免金属件穿透帽壳，具体结构以产品标识为准",
        "配套附件": "通用参考：与绝缘手套、绝缘靴等用具配套；附件不得破坏绝缘完整性",
        "使用与更换周期": "通用参考：除参照 2.5 年 / 3.5 年材质期限外，绝缘类用品应按单位制度定期检验，出现划伤、变形即停用",
    },
    "industrial": {
        "帽壳材质": "通用参考：ABS 或玻璃钢（FRP）；高温、焊接等环境需核对耐高温或阻燃标记",
        "帽衬结构": "通用参考：关注侧向刚性与帽壳强度，矿山、隧道等场景避免侧面挤压风险",
        "配套附件": "通用参考：面屏、耳罩、照明等较常用，需确认接口兼容与安装后防护性能",
    },
    "lightweight": {
        "帽壳材质": "通用参考：ABS 或 HDPE；带通风孔的结构需确认不影响所需防护性能",
        "整帽重量": "通用参考：以「满足对应防护类别」为前提比较整帽重量，不宜单纯追求轻；以产品标识为准",
        "配套附件": "通用参考：可更换吸汗衬垫、下颏带较常见，注意清洁方式与配件供应",
    },
}


# 卡片上的一句话选型重点（通用参考，非产品性能承诺）
FOCUS = {
    "construction": "帽壳材质、缓冲间距与下颏带配置",
    "electrical": "电绝缘性能标记与型式检验报告",
    "industrial": "帽壳强度、侧向刚性与附件兼容",
    "lightweight": "整帽重量、通风结构与头围适配",
}


def spec_rows_for(slug):
    rows = dict(SPEC_BASE)
    rows.update(SPEC_BY_SLUG.get(slug, {}))
    return list(rows.items())


# 安全帽选型常识（公开标准与监管信息，供品牌页展示，不涉及企业资料）
KNOWLEDGE = [
    ("document", "先看标准与永久标识",
     "现行强制性国家标准为 GB 2811-2019《头部防护 安全帽》，2020 年 7 月 1 日起实施。选购时核对帽壳内侧的永久标识：制造日期、标准编号、生产许可证编号与标志。自 2024 年 9 月 25 日起，安全帽纳入工业产品生产许可证管理。"),
    ("shield", "按风险与材质选类别",
     "通用参考：ABS、HDPE 常见于建筑与一般工业场景，玻璃钢多用于高温、矿山等环境；带电作业须核对电绝缘性能标记。冲击吸收、耐穿刺是基本技术性能，具体等级以产品标识和型式检验报告为准。"),
    ("clock", "到期、受损即更换",
     "通用参考：塑料 / 纸胶帽自制造完成起使用不超过 2.5 年，玻璃钢 / 橡胶帽不超过 3.5 年；遭受过一次明显冲击、帽壳开裂变形、帽衬松脱或标识模糊，应立即停用更换。佩戴时系紧下颏带并保持帽衬缓冲间距。"),
]

# 上线前需补齐的企业资料（集中清单，便于一次性替换）
PENDING_DOCS = [
    ("企业全称", "全站顶部品牌区、页脚版权行", "营业执照上的完整名称"),
    ("咨询热线", "顶部信息栏、页脚、联系我们", "可接通的业务电话，去掉 400-XXX-XXXX 示例格式"),
    ("办公地址 / 地图", "页脚、联系我们", "省市区及详细地址，确认后嵌入地图"),
    ("营业时间", "页脚、联系我们", "工作日与具体时段"),
    ("ICP 备案号", "页脚", "域名备案通过后填写，未备案不可上线"),
    ("产品型号与正式参数", "产品中心、4 个分类详情", "替换通用参考表，附产品标识与检测数据"),
    ("资质证书 / 检测报告", "首页企业实力、品牌介绍", "证书名称、编号、有效期与可核验出处"),
    ("客户案例", "首页案例区", "按背景—需求—方案—效果—评价填写，可脱敏"),
    ("参考价格与商务条款", "产品中心、常见问题", "报价周期、起订量、交付与开票条款"),
    ("企业简介 / 发展历程 / 实景", "品牌介绍", "200–300 字简介、时间轴节点、办公与产线照片"),
]

FAQ_ITEMS = [
    ("安全帽主要分为哪些类别？",
     "本站按作业场景把展示内容分为建筑施工、电力绝缘、工业防护、轻便透气四类，便于按场景浏览。分类仅为站内导航口径；产品的正式类别、性能标记与适用范围，以产品标识、执行标准和型式检验报告为准。现行强制性国家标准为 GB 2811-2019《头部防护 安全帽》。"),
    ("选型时需要重点核对哪些信息？",
     "通用参考：先识别作业风险（坠物、碰撞、电击、侧向挤压、高温等），再核对帽壳内侧永久标识中的标准编号、制造日期与生产许可证编号；其次看帽壳材质、帽衬缓冲结构、头围调节范围、是否需要电绝缘等附加性能，以及能否与面屏、耳罩等附件配套。自 2024 年 9 月 25 日起，安全帽纳入工业产品生产许可证管理，采购时可一并核对证照与型式检验报告。"),
    ("安全帽有使用期限吗？",
     "有。通用参考：按 GB 2811-2019 及相关监管提示，塑料 / 纸胶材质自制造完成之日起使用不超过 2.5 年，玻璃钢 / 橡胶材质不超过 3.5 年。此外，遭受过明显冲击、帽壳开裂变形、帽衬松脱或标识模糊时，不论是否到期都应立即更换。具体周期以产品说明书和所在单位的安全管理制度为准。"),
    ("如何获取产品资料与报价？",
     "可在「产品中心」浏览分类、特点、规格参数通用参考与应用场景，再通过页面中的咨询表单或邮件提交需求。报价资料由企业在核实作业场景与数量后提供，本站不预设任何价格与报价周期。"),
    ("是否支持批量采购与标识定制？",
     "请在咨询表单中说明采购数量、使用场景、颜色与标识需求，并注明是否需要面屏、耳罩等附件。起订量、交付周期、定制范围与开票信息均由企业确认后书面回复，本页不预设任何商务条款。"),
    ("提交咨询表单后，我的信息会如何处理？",
     "本站为纯静态实现，表单内容不会上传到服务器。填写并校验通过后，由你选择「用邮件客户端发送」或「复制咨询内容」，再通过邮件发送至 %s。站点后续接入表单服务或企业微信后，可改为在线收单。" % MAIL),
]

NAV = [
    ("index.html", "首页", "home"),
    ("products/index.html", "产品中心", "products"),
    ("about.html", "品牌介绍", "about"),
    ("faq.html", "常见问题", "faq"),
    ("contact.html", "联系我们", "contact"),
]


# ---------------------------------------------------------------- 公共片段
def head_meta(title, desc, rel, path, ld):
    canonical = BASE + "/" + path.lstrip("/")
    if path != "index.html":
        canonical = BASE + "/" + path
    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="keywords" content="安全帽,安全帽.cn,安全帽分类,安全帽规格,安全帽选型,头部防护,业务咨询">
<meta name="author" content="%s">
<link rel="canonical" href="%s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<link rel="icon" type="image/svg+xml" href="%sassets/img/favicon.svg">
<link rel="stylesheet" href="%sassets/css/style.css">
<script>document.documentElement.classList.add('js');</script>
<script type="application/ld+json">%s</script>
</head>
<body>
<a class="skip-link" href="#main">跳到主要内容</a>
%s
""" % (title, desc, SITE, canonical, SITE, title, desc, canonical, rel, rel,
       json.dumps(ld, ensure_ascii=False), SPRITE)


def topbar(rel):
    return """<header class="topbar">
<div class="container topbar-inner">
<div class="brand-lockup">
<span class="brand-mark">%s</span>
<div class="brand-name"><a href="%sindex.html">%s</a><small>[企业全称待填写] · 安全帽产品展示与业务咨询</small></div>
</div>
<div class="topbar-contact">
<div class="top-phone"><span class="label">业务咨询热线（占位）</span><span class="num">[400-XXX-XXXX]</span></div>
<a class="top-mail" href="mailto:%s">%s%s</a>
</div>
</div>
</header>
""" % (ico("hardhat", "icon"), rel, SITE, MAIL, ico("mail", "icon icon-sm"), MAIL)


def navbar(rel, active):
    items = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        if key == "products":
            subs = "".join(
                '<li><a href="%sproducts/%s.html">%s</a></li>' % (rel, slug, d["name"])
                for slug, d in PRODUCTS.items())
            items.append(
                '<li class="dropdown"><a href="%sproducts/index.html"%s>%s %s</a>'
                '<ul class="dropdown-menu">%s<li><a href="%sproducts/index.html">查看全部分类 %s</a></li></ul></li>'
                % (rel, cur, label, ico("chevron", "icon icon-sm"), subs, rel, ico("arrow", "icon icon-sm")))
        else:
            items.append('<li><a href="%s%s"%s>%s</a></li>' % (rel, href, cur, label))
    items.append('<li class="nav-domain-item"><a href="%sindex.html">本站域名 %s</a></li>' % (rel, SITE))
    return """<div class="navbar">
<div class="container navbar-inner">
<button class="nav-toggle" type="button" aria-controls="nav-links" aria-expanded="false" aria-label="打开或关闭主导航">
%s<span class="nav-toggle-text">打开菜单</span></button>
<nav aria-label="主导航"><ul class="nav-links" id="nav-links">%s</ul></nav>
<span class="nav-domain">本站域名 <strong>%s</strong></span>
</div>
</div>
""" % (ico("menu", "icon"), "".join(items), SITE)


def cta_band(rel):
    return """<section class="cta-band" aria-labelledby="cta-title">
<div class="container cta-inner">
<div><h2 id="cta-title">需要选型建议或产品资料？</h2><p>提交咨询表单，或通过邮件说明作业场景与数量，企业信息核实后回复。</p></div>
<div class="btn-row"><a class="btn btn-primary" href="%scontact.html#inquiry">提交业务咨询 %s</a><a class="btn btn-ghost-light" href="%sproducts/index.html">浏览产品分类</a></div>
</div>
</section>
""" % (rel, ico("arrow"), rel)


def trust_strip():
    data = [
        ("shield", "分类清晰 · 按场景选型"),
        ("document", "规格与场景 · 结构完整"),
        ("check", "通用参考 · 依据公开标准"),
        ("headset", "咨询入口 · 每页可达"),
    ]
    cells = "".join('<div class="trust-item">%s<span>%s</span></div>' % (ico(k), t) for k, t in data)
    return '<section class="trust-strip" aria-label="站点服务说明"><div class="container"><div class="grid grid-4">%s</div></div></section>' % cells


def footer(rel):
    nav_links = "".join('<li><a href="%s%s">%s</a></li>' % (rel, h, l) for h, l, _ in NAV)
    prod_links = "".join('<li><a href="%sproducts/%s.html">%s</a></li>' % (rel, s, d["name"]) for s, d in PRODUCTS.items())
    return """<footer class="site-footer">
<div class="container">
<div class="footer-grid">
<div class="footer-brand">
<div class="brand-name"><a href="%sindex.html">%s</a><small>安全帽产品展示与业务咨询官网</small></div>
<p>本站企业主体信息仍为占位内容，正式上线前请替换为真实资料。行业选型内容依据 GB 2811-2019 等公开标准整理，仅作通用参考。</p>
<a class="footer-domain" href="%sindex.html">%s</a>
</div>
<div><h3>快速导航</h3><ul class="footer-list">%s</ul></div>
<div><h3>产品分类</h3><ul class="footer-list">%s</ul></div>
<div><h3>联系方式（占位）</h3>
<ul class="footer-list">
<li>咨询热线：[400-XXX-XXXX]</li>
<li>联系邮箱：<a href="mailto:%s">%s</a></li>
<li>办公地址：[省市区及详细地址待填写]</li>
<li>营业时间：[工作日及时间待填写]</li>
<li>备案号：[ICP 备案号待填写]</li>
</ul></div>
</div>
<div class="footer-bottom">
<span>&copy; <span data-year>%s</span> <strong>%s</strong> · [企业全称待填写] 版权所有</span>
<span>域名 <strong>%s</strong>（punycode：%s） · <a href="%s">项目仓库</a></span>
</div>
</div>
</footer>
<a class="floating-consult" href="%scontact.html#inquiry">%s 业务咨询</a>
<script src="%sassets/js/main.js"></script>
</body>
</html>
""" % (rel, SITE, rel, SITE, nav_links, prod_links, MAIL, MAIL,
       str(date.today().year), SITE, SITE, PUNY, REPO, rel, ico("headset"), rel)


def breadcrumb(rel, crumbs):
    lis = "".join('<li><a href="%s%s">%s</a></li>' % (rel, h, t) for h, t in crumbs[:-1])
    lis += "<li aria-current=\"page\">%s</li>" % crumbs[-1][1]
    return '<nav class="breadcrumb" aria-label="面包屑"><div class="container"><ol>%s</ol></div></nav>' % lis


def section_head(eyebrow, title, desc, center=False):
    return '<div class="section-head%s"><span class="eyebrow">%s</span><h2>%s</h2><p>%s</p></div>' % (
        " center" if center else "", eyebrow, title, desc)


def page(rel, path, title, desc, active, body, ld_extra=None):
    ld = [
        {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": SITE,
         "inLanguage": "zh-CN", "description": "安全帽产品分类、特点、规格与应用场景展示及业务咨询"},
        {"@type": "Organization", "@id": BASE + "/#org", "name": SITE, "url": BASE + "/",
         "email": MAIL, "description": "安全帽产品展示与业务咨询站点，行业选型内容依据公开标准整理，企业主体资料待填写"}
    ]
    if ld_extra:
        ld += ld_extra
    graph = {"@context": "https://schema.org", "@graph": ld}
    html = head_meta(title, desc, rel, path, graph) + topbar(rel) + navbar(rel, active)
    html += '<main id="main">' + body + "</main>"
    html += cta_band(rel) + trust_strip() + footer(rel)
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return path


def product_card(rel, slug, compact=False):
    d = PRODUCTS[slug]
    tags = "".join('<span class="tag">%s</span>' % t for t in d["tags"])
    return """<article class="card product-card">
<a class="product-media" href="%sproducts/%s.html"><img src="%sassets/img/%s" alt="%s产品示意插画" loading="lazy" width="320" height="220"></a>
<div class="product-body">
<h3><a href="%sproducts/%s.html">%s</a></h3>
%s
<p>%s</p>
<div class="product-meta">选型重点：%s · 资料与报价：咨询索取</div>
<a class="product-link" href="%sproducts/%s.html">查看特点、规格与应用场景 %s</a>
</div>
</article>
""" % (rel, slug, rel, d["img"], d["name"], rel, slug, d["name"],
       "" if compact else "<div>" + tags + "</div>", d["short"], FOCUS[slug], rel, slug, ico("arrow", "icon icon-sm"))


def faq_block(items, limit=None):
    shown = items[:limit] if limit else items
    return '<div class="faq-list">' + "".join(
        '<details class="faq-item"%s><summary>%s</summary><div class="faq-answer"><p>%s</p></div></details>' %
        (" open" if i == 0 else "", q, a) for i, (q, a) in enumerate(shown)) + "</div>"


def quick_form(rel):
    return """<form class="js-inquiry-form" data-mode="handoff" novalidate>
<div class="form-grid">
<div class="field"><label for="q-name">姓名 <span class="req">*</span></label><input id="q-name" name="name" type="text" autocomplete="name" data-validate="name" placeholder="例如：张工 / 李经理" required><span class="field-error">请填写至少 2 个字的称呼</span></div>
<div class="field"><label for="q-phone">联系电话 <span class="req">*</span></label><input id="q-phone" name="phone" type="tel" autocomplete="tel" data-validate="phone" placeholder="例如：138 0000 0000" required><span class="field-error">请填写有效的联系电话</span></div>
<div class="field full"><label for="q-message">需求描述 <span class="req">*</span></label><textarea id="q-message" name="message" data-validate="message" placeholder="例如：房建施工场景，预计 200 顶，需要检测报告与报价单（至少 10 个字）" required></textarea><span class="field-error">请至少填写 10 个字，便于我们理解需求</span></div>
</div>
<div class="form-actions"><button class="btn btn-primary" type="submit">下一步：完善并提交咨询 %s</button><span class="hint" style="color:var(--muted);font-size:13px">纯静态站点，信息不会上传服务器</span></div>
<div class="form-notice"></div>
</form>
""" % ico("arrow", "icon icon-sm")


def full_form(rel):
    opts = "".join('<option value="%s">%s</option>' % (d["name"], d["name"]) for d in PRODUCTS.values())
    return """<form class="js-inquiry-form" data-mode="mailto" novalidate>
<div class="form-grid">
<div class="field"><label for="c-name">姓名 <span class="req">*</span></label><input id="c-name" name="name" type="text" autocomplete="name" data-validate="name" placeholder="请填写真实姓名" required><span class="field-error">请填写至少 2 个字的姓名</span></div>
<div class="field"><label for="c-company">单位名称</label><input id="c-company" name="company" type="text" autocomplete="organization" placeholder="例如：单位名称（选填）"><span class="hint">选填</span></div>
<div class="field"><label for="c-phone">联系电话 <span class="req">*</span></label><input id="c-phone" name="phone" type="tel" autocomplete="tel" data-validate="phone" placeholder="例如：138 0000 0000" required><span class="field-error">请填写有效的联系电话（数字、空格或 +-() 均可）</span></div>
<div class="field"><label for="c-email">电子邮箱</label><input id="c-email" name="email" type="email" autocomplete="email" data-validate="email" placeholder="name@example.com（选填）"><span class="field-error">邮箱格式不正确，请检查</span></div>
<div class="field full"><label for="c-category">咨询类别 <span class="req">*</span></label><select id="c-category" name="category" data-validate="required" required><option value="">请选择咨询类别</option>%s<option value="批量采购与定制">批量采购与定制</option><option value="资料与报价索取">资料与报价索取</option><option value="其他业务咨询">其他业务咨询</option></select><span class="field-error">请选择咨询类别</span></div>
<div class="field full"><label for="c-message">需求描述 <span class="req">*</span></label><textarea id="c-message" name="message" data-validate="message" placeholder="例如：电力巡检，预计 100 顶，需要电绝缘性能标记与型式检验报告（至少 10 个字）" required></textarea><span class="hint">请勿填写与业务无关的敏感信息；至少 10 个字。</span><span class="field-error">请至少填写 10 个字</span></div>
<div class="field full"><label class="checkbox-field"><input type="checkbox" name="agree" data-validate="checked" required><span>我已阅读并同意：本表单为纯静态演示，内容不会上传服务器，需由我自行选择邮件发送或复制后另发。</span></label><span class="field-error">请勾选后再提交</span></div>
</div>
<div class="form-actions"><button class="btn btn-primary" type="submit">校验并生成咨询内容 %s</button><a class="btn btn-outline" href="mailto:%s">直接发送邮件</a></div>
<div class="form-notice"></div>
</form>
""" % (opts, ico("arrow", "icon icon-sm"), MAIL)


def trust_answers(rel):
    return """<div class="grid grid-3" style="margin-top:36px">
<div class="card"><div class="card-ico">%s</div><h3>你是做什么的</h3><p>本站点围绕安全帽产品分类、特点、规格与应用场景做展示，并提供业务咨询入口。企业主体资料为占位内容，待正式上线前填写。</p></div>
<div class="card"><div class="card-ico">%s</div><h3>凭什么信你</h3><p>资质证书、检测报告、客户案例等信任资料均以占位形式列出，不虚构任何信息；实际材料请向企业索取并核对。</p></div>
<div class="card"><div class="card-ico">%s</div><h3>怎么联系你</h3><p>可通过<a href="%scontact.html#inquiry">咨询表单</a>、邮箱 <a href="mailto:%s">%s</a> 联系；电话与地址为占位，待填写。</p></div>
</div>
""" % (ico("layers", "icon-lg"), ico("certificate", "icon-lg"), ico("headset", "icon-lg"), rel, MAIL, MAIL)


# ---------------------------------------------------------------- 首页
def home(R):
    b = []
    b.append("""<section class="hero">
<div class="container hero-inner">
<div>
<span class="eyebrow" style="color:var(--accent)">头部防护 · 产品展示与业务咨询</span>
<h1>安全帽产品分类、规格与<br><em>应用场景，一页看清</em></h1>
<p class="hero-lead">%s 是面向安全帽产品展示与业务咨询的简体中文官网。按作业场景浏览分类，查看特点、规格参数与应用场景，再通过咨询表单提交需求。</p>
<p class="hero-domain">%s 本站域名：%s</p>
<div class="btn-row"><a class="btn btn-primary" href="products/index.html">浏览产品中心 %s</a><a class="btn btn-outline" href="contact.html#inquiry">获取选型与报价咨询</a></div>
<div class="note" style="margin-top:26px">说明：本站企业名称、电话、地址、资质与案例仍为占位内容，未编造任何企业资料；产品规格表已按公开标准填写行业通用参考值，并非本企业产品参数或性能承诺。</div>
</div>
<figure class="hero-art"><img src="assets/img/hero-scene.svg" alt="工地建筑剪影与黄色安全帽组成的示意插画" width="640" height="460"><figcaption>安全帽主题示意插画（非实物照片）</figcaption></figure>
</div>
</section>
""" % (SITE, ico("globe"), SITE, ico("arrow")))

    stats = [("4", "安全帽产品分类"), ("12", "规格参数核对项"), ("12", "常见作业场景"), ("6", "选型常见问题")]
    b.append('<section class="section" style="padding:38px 0"><div class="container"><div class="stats">' +
             "".join('<div class="stat"><span class="value">%s</span><span class="label">%s</span></div>' % (v, l) for v, l in stats) +
             '</div><p class="note">以上为本站内容规模统计，非企业业绩数据；本站不使用无法核实的宣传数字。</p></div></section>')

    b.append('<section class="section section-soft"><div class="container">' +
             section_head("产品中心", "按作业场景浏览安全帽分类", "四类场景各自给出特点、规格参数通用参考与应用场景，先选场景再看详情，最后提交咨询。") +
             '<div class="grid grid-4">' + "".join(product_card("", s) for s in PRODUCTS) + "</div>" +
             '<div style="text-align:center;margin-top:30px"><a class="btn btn-outline" href="products/index.html">查看全部分类与规格对照表 ' + ico("arrow", "icon icon-sm") + "</a></div></div></section>")

    steps = [
        ("layers", "第一步 · 选场景", "在「产品中心」按建筑施工、电力绝缘、工业防护、轻便透气四类定位。"),
        ("ruler", "第二步 · 看规格", "打开分类详情，查看特点、12 项规格通用参考与应用场景清单。"),
        ("clipboard", "第三步 · 提需求", "通过咨询表单或邮件说明场景与数量，索取资料与报价。"),
    ]
    b.append('<section class="section"><div class="container">' +
             section_head("浏览路径", "从浏览到咨询，三步走完", "每个页面都保留产品入口、信任说明与咨询入口，不会出现看完无处可去的页面。", True) +
             '<div class="grid grid-3">' + "".join(
                 '<div class="card"><div class="card-ico">%s</div><h3>%s</h3><p>%s</p></div>' % (ico(k), t, d) for k, t, d in steps
             ) + "</div></div></section>")

    strength = [
        ("certificate", "资质与证书", "待企业补充：证书名称、编号与有效期"),
        ("factory", "生产与供应", "待企业补充：产能、产线与供货范围"),
        ("document", "检测与报告", "待企业补充：检测机构与报告编号"),
        ("users", "团队与服务", "待企业补充：团队规模与服务范围"),
    ]
    b.append('<section class="section section-soft"><div class="container">' +
             section_head("企业实力", "信任资料，逐项待补", "以下板块结构已就位，具体信息均由企业填写后替换，不预先编写无法核实的内容。") +
             '<div class="grid grid-4">' + "".join(
                 '<div class="card"><div class="card-ico accent">%s</div><h3>%s</h3><p><span class="placeholder">%s</span></p></div>' % (ico(k), t, v)
                 for k, t, v in strength) + "</div></div></section>")

    scene_cases = [
        ("房屋建筑主体施工", "高处坠物、多工种交叉作业", "建筑施工安全帽", "construction"),
        ("配电房与变电运维", "近电作业、电击风险", "电力绝缘安全帽", "electrical"),
        ("矿山与化工装置检修", "坠物、碰撞、侧向挤压", "工业防护安全帽", "industrial"),
    ]
    b.append('<section class="section"><div class="container">' +
             section_head("场景化选型参考", "按作业风险反查产品分类", "以下为行业通用场景说明，不含客户名称、项目时间或效果数据；正式客户案例由企业按「背景—需求—方案—效果—评价」补充。") +
             '<div class="grid grid-3">' + "".join(
                 '<div class="card"><span class="tag">通用场景</span><h3>%s</h3><p style="color:var(--muted);font-size:14px">主要风险：%s</p><p>建议对照「%s」分类，核对执行标准、性能标记与型式检验报告。</p><a class="product-link" href="products/%s.html">查看该分类规格与场景 %s</a></div>'
                 % (t, risk, cat, slug, ico("arrow", "icon icon-sm"))
                 for t, risk, cat, slug in scene_cases) + "</div></div></section>")

    b.append('<section class="section section-soft"><div class="container">' +
             section_head("常见问题", "选型前常问的几件事", "以下为通用选型参考，不构成对具体产品性能的承诺；完整问答见「常见问题」页。", True) +
             faq_block(FAQ_ITEMS, 3) +
             '<div style="text-align:center;margin-top:26px"><a class="btn btn-outline" href="faq.html">查看全部常见问题 ' + ico("arrow", "icon icon-sm") + "</a></div></div></section>")

    b.append('<section class="section section-ink" id="quick"><div class="container"><div class="grid grid-2" style="align-items:center;gap:46px">' +
             '<div><span class="eyebrow">快速咨询</span><h2>先留下需求，再补充细节</h2><p style="font-size:16px">填写三项信息后跳转到「联系我们」的完整表单，已填内容自动带入。本站为纯静态实现，信息不会上传服务器。</p>' + trust_answers("") + "</div>" +
             '<div class="card" style="box-shadow:none"><h3 style="margin-bottom:18px">快速咨询表单</h3>' + quick_form("") + "</div>" +
             "</div></div></section>")
    return "".join(b)


# ---------------------------------------------------------------- 产品中心
def products_index(R):
    b = [breadcrumb(R, [("index.html", "首页"), ("products/index.html", "产品中心")])]
    b.append('<section class="section"><div class="container">' +
             '<span class="eyebrow">产品中心 · %s</span><h1>安全帽产品分类</h1>' % SITE +
             '<p style="font-size:17px;color:var(--muted);max-width:820px">按作业场景划分四类，覆盖分类、特点、规格参数通用参考与应用场景。企业型号、检测数据与参考价格仍为占位内容，正式资料由企业填写后替换。</p>' +
             '<div class="category-strip">' +
             ('<a href="%sproducts/index.html" aria-current="page">全部分类（4）</a>' % R) +
             "".join('<a href="%sproducts/%s.html">%s</a>' % (R, s, d["name"]) for s, d in PRODUCTS.items()) +
             '<a href="%scontact.html#inquiry">不确定怎么选？提交咨询 %s</a>' % (R, ico("arrow", "icon icon-sm")) +
             "</div>" +
             '<div class="grid grid-4">' + "".join(product_card(R, s) for s in PRODUCTS) + "</div>" +
             '<div class="pagination" aria-label="分类列表分页"><span class="disabled">上一页</span><span class="current">1</span><span class="disabled">下一页</span><span style="border:0">共 1 页 / 4 个分类；扩品后按每页 12 个自动分页</span></div>' +
             "</div></section>")

    rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>GB 2811-2019（通用参考）</td><td>咨询索取报价单</td></tr>" %
        (d["name"], " / ".join(d["tags"]), d["features"][0]) for d in PRODUCTS.values())
    b.append('<section class="section section-soft"><div class="container">' +
             section_head("规格与分类对照", "四类安全帽关键选型对照", "下表按分类列出选型首要关注点与现行执行标准；具体型号、材质、重量、检测报告与价格需向企业索取，以产品标识与检测报告为准。") +
             '<div class="table-wrap"><table><caption>分类与关键选型对照表 · 行业通用参考</caption><thead><tr><th>分类</th><th>适用场景标签</th><th>选型首要关注点（通用参考）</th><th>执行标准</th><th>参考价格</th></tr></thead><tbody>' + rows + "</tbody></table></div>" +
             '<div class="note">通用参考：现行强制性国家标准为 GB 2811-2019《头部防护 安全帽》，2020 年 7 月 1 日起实施。本表仅作选型字段提示，不代表任何具体产品已通过认证或已列入本站产品目录。</div>' +
             "</div></section>")

    scene_cards = "".join(
        '<div class="card"><h3>%s</h3><p style="color:var(--muted);font-size:14px">%s</p><ul style="margin:12px 0 0;font-size:14px">%s</ul><a class="product-link" href="%s.html">查看应用场景与规格 %s</a></div>' %
        (d["name"], d["short"], "".join("<li>%s</li>" % t for t, _ in d["scenes"]), s, ico("arrow", "icon icon-sm"))
        for s, d in PRODUCTS.items())
    b.append('<section class="section"><div class="container">' +
             section_head("应用场景速查", "按作业环境反查产品分类", "先确定作业环境与风险类型，再进入对应分类查看完整规格与特点。") +
             '<div class="grid grid-2">' + scene_cards + "</div></div></section>")
    return "".join(b)


# ---------------------------------------------------------------- 产品详情
def product_detail(R, slug):
    d = PRODUCTS[slug]
    b = [breadcrumb(R, [("index.html", "首页"), ("products/index.html", "产品中心"), ("products/%s.html" % slug, d["name"])])]
    b.append("""<section class="section"><div class="container">
<div class="grid grid-2" style="gap:46px;align-items:center">
<div class="product-media" style="border:1px solid var(--line);border-radius:var(--radius)"><img src="%sassets/img/%s" alt="%s产品示意插画" width="320" height="220"></div>
<div><span class="eyebrow">产品分类 · %s</span><h1>%s</h1>
<p style="font-size:17px;color:var(--muted)">%s</p>
<div>%s</div>
<p class="note">本页为分类展示页，非具体型号详情页。下表规格值为行业通用参考，型号、检测数据、价格与报告仍需向企业索取。</p>
<div class="btn-row" style="margin-top:22px"><a class="btn btn-primary" href="%scontact.html#inquiry">咨询该分类产品 %s</a><a class="btn btn-outline" href="%sproducts/index.html">返回产品中心</a></div>
</div></div></div></section>
""" % (R, d["img"], d["name"], SITE, d["name"], d["short"],
       "".join('<span class="tag tag-accent">%s</span>' % t for t in d["tags"]), R, ico("arrow", "icon icon-sm"), R))

    b.append('<section class="section section-soft"><div class="container">' +
             section_head("产品特点", "%s · 选型关注点" % d["name"], "以下为通用选型参考，描述的是核对要点，不代表任何具体产品的性能承诺。") +
             '<div class="card" style="max-width:900px"><ul class="feature-list">' +
             "".join('<li>%s<span>%s</span></li>' % (ico("check"), f) for f in d["features"]) +
             "</ul></div></div></section>")

    spec_rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (k, v) for k, v in spec_rows_for(slug))
    b.append('<section class="section"><div class="container">' +
             section_head("规格参数", "规格参数表（行业通用参考）", "依据公开标准与监管信息整理的通用核对项，不是本企业产品参数；正式规格表、检测报告与报价单请提交咨询索取。") +
             '<div class="table-wrap"><table><caption>%s · 规格参数通用参考表</caption><thead><tr><th>参数项</th><th>参数值（行业通用参考）</th></tr></thead><tbody>%s</tbody></table></div>' % (d["name"], spec_rows) +
             '<div class="note">表中数值与标准信息均为行业通用参考：GB 2811-2019 为现行强制性国家标准，更换期限参考公开监管提示，头围与重量为市面常见标注。以上不构成对任何具体产品的认证声明或性能承诺。</div>' +
             "</div></section>")

    scenes = "".join(
        '<div class="scene-item">%s<div><h4>%s</h4><p>%s</p></div></div>' % (ico("location"), t, desc)
        for t, desc in d["scenes"])
    b.append('<section class="section section-soft"><div class="container">' +
             section_head("应用场景", "%s · 常见作业场景" % d["name"], "场景描述为行业通用说明，未涉及任何具体客户或项目。") +
             '<div class="scene-grid">' + scenes + "</div>" +
             '<div class="grid grid-2" style="margin-top:26px"><div class="card"><h3>使用前需确认</h3><ul style="margin:0"><li>作业风险评估与所需防护类别</li><li>产品标识、执行标准与检测报告</li><li>头围适配与附件兼容性</li><li>检查、维护与更换制度</li></ul></div>' +
             '<div class="card"><h3>索取完整资料</h3><p>需要型号清单、检测报告、报价单或样品说明，请提交咨询表单，注明场景与预计数量。</p><a class="btn btn-primary btn-sm" href="%scontact.html#inquiry">提交咨询 %s</a></div></div>' % (R, ico("arrow", "icon icon-sm")) +
             "</div></section>")

    related = [s for s in PRODUCTS if s != slug][:3]
    b.append('<section class="section"><div class="container">' +
             section_head("相关分类推荐", "同类场景的其他选择", "按作业场景关联推荐，方便对照选型。") +
             '<div class="grid grid-3">' + "".join(product_card(R, s, compact=True) for s in related) + "</div>" +
             "</div></section>")

    crumbs = [{"@type": "ListItem", "position": 1, "name": "首页", "item": BASE + "/index.html"},
              {"@type": "ListItem", "position": 2, "name": "产品中心", "item": BASE + "/products/index.html"},
              {"@type": "ListItem", "position": 3, "name": d["name"], "item": BASE + "/products/" + slug + ".html"}]
    ld = [
        {"@type": "BreadcrumbList", "itemListElement": crumbs},
        {"@type": "Product", "name": d["name"], "description": d["short"],
         "category": "安全帽 / " + d["name"], "image": BASE + "/assets/img/" + d["img"],
         "url": BASE + "/products/" + slug + ".html", "inLanguage": "zh-CN",
         "additionalProperty": [{"@type": "PropertyValue", "name": "规格参数", "value": "行业通用参考，具体参数以产品标识与检测报告为准"}]}
    ]
    return "".join(b), ld


# ---------------------------------------------------------------- 品牌介绍
def about(R):
    b = [breadcrumb(R, [("index.html", "首页"), ("about.html", "品牌介绍")])]
    b.append("""<section class="section"><div class="container">
<div class="grid grid-2" style="gap:46px;align-items:center">
<div><span class="eyebrow">品牌介绍 · %s</span><h1>关于本站与企业主体</h1>
<p style="font-size:17px;color:var(--muted)">%s 定位为安全帽产品展示与业务咨询官网。本页所有企业具体信息均使用占位内容，待企业核对后填写，不预先编写无法核实的介绍、资质或业绩。</p>
<div class="btn-row"><a class="btn btn-primary" href="products/index.html">浏览产品 %s</a><a class="btn btn-outline" href="contact.html#inquiry">联系业务咨询</a></div></div>
<div class="card"><h3>企业简介（占位）</h3><p><span class="placeholder">[请在此填写 200–300 字企业简介：成立时间、主营业务、服务行业、经营理念等，均以真实信息为准]</span></p>
<div class="note">填写提示：介绍写「客户能得到什么」，少用无法核实的形容词；涉及绝对化用语或满额承诺类表述，请按《广告法》替换为可核对的事实与数字。</div></div>
</div></div></section>
""" % (SITE, SITE, ico("arrow", "icon icon-sm")))

    timeline = [
        ("节点 1", "待企业补充：成立时间与经营主体信息"),
        ("节点 2", "待企业补充：产品线或业务拓展事项"),
        ("节点 3", "待企业补充：资质、体系或重要合作"),
        ("节点 4", "待企业补充：近期发展事项"),
    ]
    b.append('<section class="section section-soft"><div class="container"><div class="grid grid-2" style="gap:46px">' +
             '<div>' + section_head("发展历程", "发展时间轴（占位）", "按真实时间填写关键节点，每个节点配可核对的事实，不使用模糊夸大表述。") +
             '<ul class="timeline">' + "".join('<li><span class="year">%s</span><br>%s</li>' % (y, e) for y, e in timeline) + "</ul></div>" +
             '<div>' + section_head("团队与实力", "实力资料清单（占位）", "以下项目建议逐项补齐真实材料与图片。") +
             '<div class="grid grid-2">' + "".join(
                 '<div class="card"><div class="card-ico">%s</div><h3>%s</h3><p><span class="placeholder">%s</span></p></div>' % (ico(k), t, v)
                 for k, t, v in [
                     ("certificate", "资质证书", "待企业补充：证书名称与编号"),
                     ("factory", "生产与仓储", "待企业补充：场地、产线与实景照片"),
                     ("users", "团队构成", "待企业补充：团队规模与岗位"),
                     ("document", "检测报告", "待企业补充：报告名称与编号"),
                 ]) + "</div></div></div></div></section>")

    flow = [
        "提交需求：说明作业场景、预计数量与需要索取的资料",
        "需求核实：核对作业风险与选型方向，确认是否需要电绝缘等附加性能",
        "资料提供：型号清单、规格参数、型式检验报告与报价说明",
        "样品与确认：确认颜色、标识、下颏带与面屏等附件需求",
        "商务确认：价格、交付周期与开票条款由企业书面确认",
        "后续服务：使用说明、日常检查与到期更换提醒",
    ]
    b.append('<section class="section"><div class="container"><div class="grid grid-2" style="gap:46px">' +
             '<div>' + section_head("服务流程", "从咨询到交付的步骤", "流程为通用框架，具体时限、条款与责任均由企业填写后确认。") +
             '<ol class="flow-steps">' + "".join("<li>%s</li>" % s for s in flow) + "</ol></div>" +
             '<div>' + section_head("企业文化与实景", "待补充的展示位", "以下为内容占位框，正式资料到位后替换为实景照片与说明文字。") +
             '<div class="map-placeholder" style="min-height:150px;margin-bottom:16px">%s<div>企业实景照片位（待补充）<br><span style="font-size:13px">建议：办公区 / 生产区 / 仓储区，各配一句说明</span></div></div>' % ico("location") +
             '<div class="card"><h3>企业文化</h3><p><span class="placeholder">待企业补充：使命、价值观与服务理念</span></p></div></div>' +
             "</div></div></section>")

    b.append('<section class="section"><div class="container">' +
             section_head("安全帽选型常识", "依据公开标准整理的三条通用参考", "以下依据 GB 2811-2019 等公开标准与监管信息整理，供选型时核对，不代表企业资质或任何具体产品的性能承诺。", True) +
             '<div class="grid grid-3">' + "".join(
                 '<div class="card"><div class="card-ico accent">%s</div><h3>%s</h3><p>%s</p></div>' % (ico(k), t, d)
                 for k, t, d in KNOWLEDGE) + "</div></div></section>")

    doc_rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (item, place, req)
                       for item, place, req in PENDING_DOCS)
    b.append('<section class="section"><div class="container">' +
             section_head("上线前资料清单", "仍需企业填写的占位项", "行业通用内容已按公开标准填写；下表为企业主体资料，须以真实、可核验的信息替换后方可对外上线。") +
             '<div class="table-wrap"><table><caption>待补齐的企业资料清单</caption><thead><tr><th>资料项</th><th>主要出现位置</th><th>填写要求</th></tr></thead><tbody>' + doc_rows + "</tbody></table></div>" +
             "</div></section>")

    b.append('<section class="section section-soft"><div class="container">' +
             section_head("独立信任说明", "这一页也能独立回答三个问题", "无论从搜索还是外链进入本页，都能看清业务、信任依据与联系方式。", True) +
             trust_answers(R) + "</div></section>")
    return "".join(b)


# ---------------------------------------------------------------- 联系我们
def contact(R):
    b = [breadcrumb(R, [("index.html", "首页"), ("contact.html", "联系我们")])]
    b.append('<section class="section" id="inquiry"><div class="container">' +
             '<span class="eyebrow">联系我们 · %s</span><h1>业务咨询与联系方式</h1>' % SITE +
             '<p style="font-size:17px;color:var(--muted);max-width:820px">请通过下方表单说明作业场景与需求；企业电话、地址、营业时间等为占位内容，上线前请替换为真实信息。邮箱为本站指定的联系邮箱。</p>' +
             '<div class="contact-grid" style="margin-top:38px">' +
             '<div><h2 style="font-size:22px;margin-bottom:18px">联系方式</h2><ul class="contact-list">' +
             "".join('<li>%s<div><span class="k">%s</span><span class="v">%s</span></div></li>' % (ico(k), t, v) for k, t, v in [
                 ("phone", "咨询热线（占位）", '<span class="placeholder">[400-XXX-XXXX]</span>'),
                 ("mail", "联系邮箱", '<a href="mailto:%s">%s</a>' % (MAIL, MAIL)),
                 ("location", "办公地址（占位）", '<span class="placeholder">[省市区及详细地址待填写]</span>'),
                 ("clock", "营业时间（占位）", '<span class="placeholder">[工作日及时间待填写]</span>'),
                 ("globe", "官方网站", '<a href="index.html">%s</a>' % SITE),
             ]) + "</ul>" +
             '<div class="map-placeholder">%s<div>地图位置待企业确认后嵌入<br><span style="font-size:13px">企业确认地址后嵌入地图；当前不展示任何虚构位置</span></div></div>' % ico("location") +
             '<div class="card" style="margin-top:20px"><h3>分支机构与其他渠道</h3><p><span class="placeholder">待企业补充：分支机构、企业微信、传真等渠道</span></p></div>' +
             '<div class="card" style="margin-top:16px"><h3>响应说明</h3><p><span class="placeholder">待企业补充：首次响应时限、报价周期与资料寄送方式</span></p><p style="font-size:13px;color:var(--muted);margin:0">本页不预设任何服务承诺或时效数字。</p></div>' +
             "</div>" +
             '<div><h2 style="font-size:22px;margin-bottom:18px">业务咨询表单</h2>' +
             '<div class="card" style="box-shadow:none">' + full_form(R) + "</div>" +
             '<div class="note"><strong>表单说明：</strong>本站为纯静态实现，未接入后端收单服务。填写并校验通过后，可选择「用邮件客户端发送」或「复制咨询内容」自行发送；表单内容不会上传到服务器，也不会写入 Cookie。接入表单服务或企业微信后即可改为在线收单。</div>' +
             "</div></div></div></section>")

    b.append('<section class="section section-soft"><div class="container">' +
             section_head("咨询前可先准备", "提供这些信息，沟通更高效", "以下为通用准备清单，不涉及任何企业数据。", True) +
             '<div class="grid grid-4">' + "".join(
                 '<div class="card"><div class="card-ico accent">%s</div><h3>%s</h3><p>%s</p></div>' % (ico(k), t, d) for k, t, d in [
                     ("building", "作业场景", "室内 / 露天、是否存在电击、坠物、高温等风险。"),
                     ("ruler", "规格要求", "头围范围、颜色、是否需要面屏或耳罩等附件。"),
                     ("layers", "数量与批次", "预计采购数量、分批安排与期望交付时间。"),
                     ("document", "所需资料", "型号清单、检测报告、报价单或样品说明。"),
                 ]) + "</div></div></section>")

    b.append('<section class="section"><div class="container">' + trust_answers(R) + "</div></section>")
    ld = [{"@type": "ContactPage", "name": "联系我们 - " + SITE, "url": BASE + "/contact.html",
           "inLanguage": "zh-CN", "description": "安全帽产品业务咨询表单与联系方式占位页面"},
          {"@type": "ContactPoint", "contactType": "sales", "email": MAIL,
           "url": BASE + "/contact.html", "availableLanguage": ["zh-CN"]}]
    return "".join(b), ld


# ---------------------------------------------------------------- FAQ
def faq(R):
    b = [breadcrumb(R, [("index.html", "首页"), ("faq.html", "常见问题")])]
    b.append('<section class="section"><div class="container">' +
             '<span class="eyebrow">常见问题 · %s</span><h1>选型与咨询常见问题</h1>' % SITE +
             '<p style="font-size:17px;color:var(--muted);max-width:820px">以下问答分为通用选型参考与站点使用说明两部分，不涉及具体企业承诺；商务条款、价格与周期均为占位内容。</p>' +
             '<div style="margin-top:34px">' + faq_block(FAQ_ITEMS) + "</div>" +
             '<div class="card" style="max-width:860px;margin:26px auto 0"><h3>没找到答案？</h3><p>可直接提交咨询表单，或通过邮件说明问题，我们会在核实后回复，具体响应时限由企业确认后补充。</p><div class="btn-row"><a class="btn btn-primary btn-sm" href="%scontact.html#inquiry">提交咨询 %s</a><a class="btn btn-outline btn-sm" href="products/index.html">返回产品中心</a></div></div>' % (R, ico("arrow", "icon icon-sm")) +
             "</div></section>")
    ld = [{"@type": "FAQPage", "name": "常见问题 - " + SITE, "inLanguage": "zh-CN",
           "mainEntity": [{"@type": "Question", "name": q,
                           "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_ITEMS]}]
    return "".join(b), ld


# ---------------------------------------------------------------- 404
def notfound(R):
    b = """<section class="section"><div class="container" style="max-width:720px;text-align:center;padding:40px 0">
<span class="eyebrow">404</span><h1>页面没有找到</h1>
<p style="font-size:17px;color:var(--muted)">你访问的地址不存在或已调整。可以从下面的入口继续浏览 %s。</p>
<div class="btn-row" style="justify-content:center;margin-top:26px"><a class="btn btn-primary" href="%sindex.html">返回首页</a><a class="btn btn-outline" href="%sproducts/index.html">浏览产品中心</a><a class="btn btn-outline" href="%scontact.html#inquiry">业务咨询</a></div>
<div class="note" style="text-align:left;margin-top:34px">常用入口：首页、产品中心、品牌介绍、常见问题、联系我们。站点地图见 <a href="sitemap.xml">sitemap.xml</a>。</div>
</div></section>""" % (SITE, R, R, R)
    return b


# ---------------------------------------------------------------- 附加文件
def extra_files():
    robots = """User-agent: *
Allow: /
Disallow: /assets/js/
Disallow: /tools/
Disallow: /api/
Disallow: /admin/

User-agent: Baiduspider
Allow: /
User-agent: GPTBot
Allow: /
User-agent: Claude-Web
Allow: /
User-agent: Anthropic-AI
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Bytespider
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Applebot
Allow: /

Sitemap: %s/sitemap.xml
""" % BASE
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")

    urls = ["index.html", "products/index.html"] + ["products/%s.html" % s for s in PRODUCTS] + \
           ["about.html", "contact.html", "faq.html", "404.html"]
    entries = []
    for u in urls:
        loc = BASE + "/" + u
        pr = "1.0" if u == "index.html" else ("0.8" if "products/" in u else "0.6")
        entries.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>%s</priority>\n  </url>" % (loc, TODAY, pr))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    (ROOT / "CNAME").write_text(PUNY + "\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")

    llms = """# 安全帽.cn

> 简体中文安全帽产品展示与业务咨询官网。站点为纯静态实现，内容以 HTML 正文输出，便于搜索引擎与 AI 助手读取。

## 站点信息

- 域名：安全帽.cn（punycode：%s）
- 规范地址：%s
- 联系邮箱：%s
- 项目仓库：%s
- 语言：简体中文（zh-CN）

## 重要说明

本站企业主体信息（企业全称、电话、地址、资质证书、检测报告、客户案例、年限与数据）均为占位内容，尚未填写真实资料；产品型号、检测数据与参考价格同样待企业填写。规格参数表、选型常识与问答已依据 GB 2811-2019《头部防护 安全帽》等公开标准与监管信息填写行业通用参考值，不构成对任何具体产品性能的承诺或认证声明。

## 行业通用参考（依据公开标准）

- 现行标准：GB 2811-2019《头部防护 安全帽》，2020-07-01 实施，替代 GB 2811-2007
- 更换周期：塑料 / 纸胶帽自制造完成起不超过 2.5 年，玻璃钢 / 橡胶帽不超过 3.5 年；受冲击或开裂应立即更换
- 采购核对：帽壳内侧永久标识（制造日期、标准编号、生产许可证编号）；自 2024-09-25 起纳入工业产品生产许可证管理
- 常见材质：ABS、HDPE、玻璃钢；带电作业须核对电绝缘性能标记；普通型整帽重量常见约 300–430 g
- 以上数值为行业通用参考，具体以产品标识、型式检验报告与产品说明书为准

## 产品体系

%s

## 服务与咨询

- 浏览路径：产品中心分类 → 分类详情（特点 / 规格 / 应用场景）→ 咨询表单
- 咨询表单：纯静态实现，校验通过后由访客自行选择邮件发送或复制内容，信息不上传服务器
- 响应时限、报价周期、商务条款：由企业核实需求后书面回复，本站不预设

## 页面索引

%s

## 机器可读文件

- sitemap：%s/sitemap.xml
- robots：%s/robots.txt
""" % (PUNY, BASE, MAIL, REPO,
       "\n".join("- [%s](%s/products/%s.html)：%s" % (d["name"], BASE, s, d["short"]) for s, d in PRODUCTS.items()),
       "\n".join("- [%s](%s/%s)" % (dict((h, l) for h, l, _ in NAV).get(u, "页面"), BASE, u) for u in
                 ["index.html", "products/index.html", "about.html", "faq.html", "contact.html"]),
       BASE, BASE)
    (ROOT / "llms.txt").write_text(llms, encoding="utf-8")


# ---------------------------------------------------------------- 生成
def main():
    generated = []
    generated.append(page("", "index.html",
                          "安全帽.cn | 安全帽产品展示与业务咨询官网",
                          "安全帽.cn 提供安全帽产品分类、特点、规格参数行业通用参考与应用场景展示，以及业务咨询入口。按作业场景选型，依据 GB 2811-2019 等公开标准整理。",
                          "home", home("")))
    generated.append(page("../", "products/index.html",
                          "产品中心 - 安全帽分类、特点、规格与应用场景 | 安全帽.cn",
                          "安全帽.cn 产品中心：建筑施工、电力绝缘、工业防护、轻便透气四类安全帽的分类、选型关注点、规格参数通用参考与应用场景速查。",
                          "products", products_index("../")))
    for slug, d in PRODUCTS.items():
        body, ld = product_detail("../", slug)
        generated.append(page("../", "products/%s.html" % slug,
                              "%s - 特点、规格与应用场景 | 安全帽.cn" % d["name"],
                              "%s：%s 安全帽.cn 提供该分类的选型关注点、12 项规格参数通用参考与常见应用场景，并可提交业务咨询。" % (d["name"], d["short"]),
                              "products", body, ld))
    generated.append(page("", "about.html",
                          "品牌介绍 | 安全帽.cn",
                          "安全帽.cn 品牌介绍页：企业简介、发展历程、团队与实力、服务流程，另有依据公开标准整理的安全帽选型常识与上线前资料清单；企业主体信息均为占位内容。",
                          "about", about("")))
    body, ld = contact("")
    generated.append(page("", "contact.html",
                          "联系我们 - 业务咨询表单与联系方式 | 安全帽.cn",
                          "联系安全帽.cn：提交业务咨询表单，查看联系方式占位。表单为纯静态实现，支持校验、邮件发送与内容复制。",
                          "contact", body, ld))
    body, ld = faq("")
    generated.append(page("", "faq.html",
                          "常见问题 - 安全帽选型与咨询 | 安全帽.cn",
                          "安全帽.cn 常见问题：安全帽分类、选型核对要点、使用与更换周期、资料与报价索取、表单信息处理等通用参考问答。",
                          "faq", body, ld))
    generated.append(page("", "404.html",
                          "页面未找到 | 安全帽.cn",
                          "安全帽.cn 404 页面，提供返回首页、产品中心与业务咨询的入口。",
                          "", notfound("")))
    extra_files()
    print("已生成 %d 个 HTML 页面：" % len(generated))
    for p in generated:
        print("  -", p)
    print("附加文件：robots.txt / sitemap.xml / llms.txt / CNAME / .nojekyll")


if __name__ == "__main__":
    main()
