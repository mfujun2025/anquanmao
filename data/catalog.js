/* =========================================================================
 * 安全帽.cn · 商品数据层（本地实现）
 * -------------------------------------------------------------------------
 * 本次交付时云服务未开通，故商品/分类/轮播/促销数据以本地结构化数据提供。
 * 数据访问统一走 assets/js/shop.js 里的 CatalogService，页面不直接读本文件。
 *
 * 接入云端数据库时只需两步：
 *   1) 把下面 4 张集合导入云端数据库（categories / products / banners / promotions）；
 *   2) 把 CatalogService 的 MODE 从 'local' 改为 'cloud'，并实现 fetchCloud()。
 * 页面渲染、筛选、购物车代码无需改动。
 *
 * image        = 当前实际展示用的本地静态资源（仓库内 assets/img/）
 * imagePath    = 预留的云端存储对象键；开通云存储后，商品图上传至该路径，
 *                运行时通过签名 URL 加载，image 作为兜底图保留。
 * ========================================================================= */
window.CATALOG = {
  site: {
    name: '安全帽.cn',
    domain: 'xn--15qt0wm7b.cn',
    slogan: '按作业场景选安全帽，合规·现货·可集采',
    standard: 'GB 2811-2019《头部防护 安全帽》',
    notice: '本站商品参数与价格为演示数据，企业主体、资质与报价以正式资料为准。'
  },

  /* ---------- 轮播图 ---------- */
  banners: [
    {
      id: 'b1',
      eyebrow: '开工季 · 头部防护专场',
      title: '合规安全帽，整单直降 15%',
      desc: '按建筑施工、电力绝缘、工业防护、轻便透气四类场景选型，帽壳标识、执行标准与型式检验资料随货可查。',
      cta: '查看热门商品',
      href: '#hot',
      theme: 'gold',
      art: 'assets/img/hero-scene.svg',
      badge: '限时 · 11.10—11.30'
    },
    {
      id: 'b2',
      eyebrow: '电力作业 · 绝缘系列',
      title: '近电作业，先看电绝缘性能标记',
      desc: '带电作业与配电运维场景专用款式，选型时核对电绝缘性能标记、执行标准与检测报告，不拿普通帽替代。',
      cta: '了解电力绝缘安全帽',
      href: 'products/electrical.html',
      theme: 'blue',
      art: 'assets/img/helmet-blue.svg',
      badge: '新品上架'
    },
    {
      id: 'b3',
      eyebrow: '企业集采 · 专属通道',
      title: '批量采购，一顶也按项目配齐',
      desc: '支持按工地/产线分批配货，提供规格对照、标识核对清单与集中报价，采购前先把风险场景列清楚。',
      cta: '提交集采需求',
      href: 'contact.html#inquiry',
      theme: 'ink',
      art: 'assets/img/helmet-red.svg',
      badge: '50 顶起 · 专属报价'
    }
  ],

  /* ---------- 商品分类 ---------- */
  categories: [
    {
      id: 'construction',
      name: '建筑施工安全帽',
      short: '建筑工地',
      desc: '房屋建筑、市政工程等高处坠物与交叉作业场景',
      icon: 'building',
      color: 'yellow',
      href: 'products/construction.html',
      count: 3
    },
    {
      id: 'electrical',
      name: '电力绝缘安全帽',
      short: '带电作业',
      desc: '带电作业、配电运维等存在电击风险的场景',
      icon: 'bolt',
      color: 'blue',
      href: 'products/electrical.html',
      count: 2
    },
    {
      id: 'industrial',
      name: '工业防护安全帽',
      short: '矿山化工',
      desc: '制造、矿山、化工等坠物碰撞与侧向挤压场景',
      icon: 'factory',
      color: 'red',
      href: 'products/industrial.html',
      count: 2
    },
    {
      id: 'lightweight',
      name: '轻便透气安全帽',
      short: '长时间佩戴',
      desc: '长时间佩戴、高温环境与高频巡检场景',
      icon: 'refresh',
      color: 'white',
      href: 'products/lightweight.html',
      count: 1
    }
  ],

  /* ---------- 商品（演示数据） ---------- */
  products: [
    {
      id: 'p01', name: 'V-Pro 建筑施工安全帽（黄色）', category: 'construction',
      price: 49, originalPrice: 69, sales: 2841, rating: 4.9, stock: 860,
      tags: ['GB 2811-2019', 'ABS 帽壳', '旋钮式调节'],
      badge: '热销 TOP1', image: 'assets/img/helmet-yellow.svg',
      imagePath: 'shared/products/v-pro-construction-yellow.webp',
      desc: '通用建筑施工场景，帽衬缓冲结构与下颏带配置齐全，适合多工种交叉作业。',
      hot: true
    },
    {
      id: 'p02', name: '绝缘型电力安全帽（蓝色 · 20kV 级）', category: 'electrical',
      price: 129, originalPrice: 168, sales: 1263, rating: 4.8, stock: 320,
      tags: ['电绝缘性能', '型式检验', '配电运维'],
      badge: '电力专供', image: 'assets/img/helmet-blue.svg',
      imagePath: 'shared/products/insulated-electrical-blue.webp',
      desc: '面向近电作业场景，采购时须核对电绝缘性能标记与对应检测报告。',
      hot: true
    },
    {
      id: 'p03', name: '高强度工业防砸安全帽（红色）', category: 'industrial',
      price: 79, originalPrice: 99, sales: 1987, rating: 4.9, stock: 540,
      tags: ['侧向刚性', '附件兼容', '矿山化工'],
      badge: '工厂直供', image: 'assets/img/helmet-red.svg',
      imagePath: 'shared/products/industrial-impact-red.webp',
      desc: '针对坠物、碰撞与侧向挤压风险，可配面屏、耳罩等附件。',
      hot: true
    },
    {
      id: 'p04', name: '超轻透气安全帽（白色）', category: 'lightweight',
      price: 59, originalPrice: 79, sales: 1562, rating: 4.8, stock: 720,
      tags: ['整帽轻量化', '通风结构', '头围适配'],
      badge: '夏季推荐', image: 'assets/img/helmet-white.svg',
      imagePath: 'shared/products/lightweight-vent-white.webp',
      desc: '长时间佩戴与高温巡检场景，重点看整帽重量与通风结构。',
      hot: true
    },
    {
      id: 'p05', name: '反光条工地安全帽（黄色）', category: 'construction',
      price: 69, originalPrice: 89, sales: 934, rating: 4.7, stock: 410,
      tags: ['高可视', '夜间作业', '反光标识'],
      badge: '夜间施工', image: 'assets/img/helmet-yellow.svg',
      imagePath: 'shared/products/reflective-construction-yellow.webp',
      desc: '增加高可视反光条，适合夜间或低照度环境下的工地通行区域。',
      hot: true
    },
    {
      id: 'p06', name: '矿用加厚防砸安全帽（红色）', category: 'industrial',
      price: 99, originalPrice: 129, sales: 688, rating: 4.8, stock: 260,
      tags: ['加厚帽壳', '矿用场景', '耐冲击'],
      badge: '集采优选', image: 'assets/img/helmet-red.svg',
      imagePath: 'shared/products/mining-heavy-red.webp',
      desc: '帽壳加厚设计，面向矿山与装置检修等高强度作业环境。',
      hot: true
    },
    {
      id: 'p07', name: '可配面屏电力安全帽（蓝色）', category: 'electrical',
      price: 149, originalPrice: 189, sales: 512, rating: 4.9, stock: 180,
      tags: ['面屏支架', '电弧防护', '模块化'],
      badge: '组合套装', image: 'assets/img/helmet-blue.svg',
      imagePath: 'shared/products/face-shield-electrical-blue.webp',
      desc: '预留面屏与耳罩接口，可按作业票要求组合防护附件。',
      hot: true
    },
    {
      id: 'p08', name: '四季通用轻便安全帽（白色）', category: 'lightweight',
      price: 89, originalPrice: 109, sales: 1105, rating: 4.7, stock: 630,
      tags: ['四季内衬', '可拆洗', '巡检常用'],
      badge: '复购率高', image: 'assets/img/helmet-white.svg',
      imagePath: 'shared/products/all-season-white.webp',
      desc: '可拆洗内衬与四季适配结构，适合巡检与频繁移动岗位。',
      hot: true
    }
  ],

  /* ---------- 促销活动 ---------- */
  promotions: [
    {
      id: 'pr1', type: 'flash', eyebrow: '限时秒杀', title: '开工季爆款 8.5 折',
      desc: 'V-Pro 建筑施工安全帽等 4 款热销型号，活动价限量供应，售完即恢复原价。',
      meta: '每日 10:00 补货', cta: '去抢购', href: '#hot', accent: 'red'
    },
    {
      id: 'pr2', type: 'coupon', eyebrow: '满减券', title: '满 500 减 60 · 满 1500 减 220',
      desc: '全站商品可用，适用于工地班组补货与多品类混搭采购，结算时自动抵扣。',
      meta: '领取后 30 天有效', cta: '领券', href: '#hot', accent: 'gold'
    },
    {
      id: 'pr3', type: 'bundle', eyebrow: '组合套餐', title: '安全帽 + 面屏 + 耳罩 套装价',
      desc: '按作业风险一次配齐头部防护，避免不同品牌附件不兼容带来的装配问题。',
      meta: '套餐立省 15%', cta: '看套餐', href: 'products/industrial.html', accent: 'blue'
    },
    {
      id: 'pr4', type: 'b2b', eyebrow: '企业集采', title: '50 顶起 · 专属报价与分批配货',
      desc: '提交作业场景、数量与交付节奏，提供规格对照表、标识核对清单与集中报价。',
      meta: '支持分批交付', cta: '提交需求', href: 'contact.html#inquiry', accent: 'ink'
    }
  ],

  /* ---------- 知识文章（5 篇 SEO 长文站内入口，slug 与发布顺序依据研究 Brief §9 / §10） ---------- */
  articles: [
    { slug: 'safety-helmet-buying-guide', title: '安全帽怎么选：五步采购决策指南（国标·材质·场景·验收）', cat: '选购指南', read: '10 分钟', href: 'blog/safety-helmet-buying-guide.html' },
    { slug: 'safety-helmet-lifespan-and-replacement', title: '安全帽使用期限是多久？报废更换与日常检查全指南', cat: '使用保养', read: '9 分钟', href: 'blog/safety-helmet-lifespan-and-replacement.html' },
    { slug: 'gb-2811-2019-safety-helmet-standard', title: 'GB 2811-2019 安全帽国家标准全解读：12 项变化与永久标识', cat: '标准法规', read: '10 分钟', href: 'blog/gb-2811-2019-safety-helmet-standard.html' },
    { slug: 'safety-helmet-material-comparison', title: '安全帽材质怎么选：ABS / HDPE / 玻璃钢 / PC 对照', cat: '材质对比', read: '9 分钟', href: 'blog/safety-helmet-material-comparison.html' },
    { slug: 'safety-helmet-selection-by-industry', title: '不同行业安全帽选型：八类工况对照与性能标记映射', cat: '场景选型', read: '9 分钟', href: 'blog/safety-helmet-selection-by-industry.html' }
  ]
};
