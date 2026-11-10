/* 安全帽.cn · 电商首页运行时
 * 数据层 CatalogService 统一收口：当前 MODE='local'（云服务未开通），
 * 接入云端数据库时改为 'cloud' 并实现 fetchCloud()，页面渲染代码无需改动。 */
(function () {
  'use strict';

  /* ---------------------------------------------------------------------
   * 0. 工具
   * ------------------------------------------------------------------- */
  var $ = function (s, root) { return (root || document).querySelector(s); };
  var $$ = function (s, root) { return Array.prototype.slice.call((root || document).querySelectorAll(s)); };
  var esc = function (v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };
  var yuan = function (n) { return '¥' + Number(n).toFixed(0); };
  var icon = function (id, cls) {
    return '<svg ' + (cls ? 'class="' + cls + '" ' : '') + 'aria-hidden="true"><use href="#' + id + '"></use></svg>';
  };
  var toastTimer;
  function toast(msg) {
    var el = $('#toast');
    if (!el) return;
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, 2600);
  }
  function store(key, val) {
    try {
      if (val === undefined) return JSON.parse(localStorage.getItem(key) || 'null');
      localStorage.setItem(key, JSON.stringify(val));
      return val;
    } catch (e) { return null; }
  }

  /* ---------------------------------------------------------------------
   * 1. 数据层
   * ------------------------------------------------------------------- */
  var CatalogService = {
    MODE: 'local',           // 'local' | 'cloud'
    _cache: null,

    // 云端实现骨架：开通云服务后，用官方 SDK 的 cloud.database.from(...) 替换本方法，
    // 并把 createWorkBuddyCloud 的 endpoint / publishableKey 取自 publicConfig。
    fetchCloud: function () {
      return Promise.reject(new Error('云服务尚未开通：请在 WorkBuddy 中启用云服务后实现 fetchCloud()。'));
    },

    get: function () {
      if (this._cache) return Promise.resolve(this._cache);
      var self = this;
      var raw = (this.MODE === 'cloud') ? this.fetchCloud() : Promise.resolve(window.CATALOG);
      return Promise.resolve(raw).then(function (data) {
        if (!data || !data.products) throw new Error('商品数据未加载');
        self._cache = data;
        return data;
      });
    },

    products: function (category, keyword) {
      return this.get().then(function (d) {
        return d.products.filter(function (p) {
          var okCat = !category || category === 'all' || p.category === category;
          var okKey = !keyword;
          if (!okKey) {
            var hay = [p.name, p.desc, p.category].concat(p.tags || []).join(' ').toLowerCase();
            okKey = hay.indexOf(String(keyword).toLowerCase()) !== -1;
          }
          return okCat && okKey;
        });
      });
    }
  };
  window.CatalogService = CatalogService;

  /* ---------------------------------------------------------------------
   * 2. 轮播图
   * ------------------------------------------------------------------- */
  var Carousel = {
    idx: 0, timer: null, total: 0,
    init: function (banners) {
      var host = $('#slides');
      if (!host || !banners.length) return;
      this.total = banners.length;
      this.themes = banners.map(function (b) { return b.theme; });
      host.innerHTML = banners.map(function (b, i) {
        return '<article class="slide ' + esc(b.theme) + (i === 0 ? ' active' : '') + '" role="tabpanel" aria-label="第 ' + (i + 1) + ' 张：' + esc(b.title) + '">' +
          '<div class="slide-copy">' +
            (b.badge ? '<span class="slide-badge">' + esc(b.badge) + '</span>' : '') +
            '<span class="slide-eyebrow">' + esc(b.eyebrow) + '</span>' +
            '<h2>' + esc(b.title) + '</h2><p>' + esc(b.desc) + '</p>' +
            '<a class="btn ' + (b.theme === 'ink' ? 'btn-gold' : 'btn-dark') + '" href="' + esc(b.href) + '">' + esc(b.cta) + icon('i-arrow') + '</a>' +
          '</div>' +
          '<div class="slide-art"><img src="' + esc(b.art) + '" alt="' + esc(b.title) + ' 主题示意插画" loading="' + (i === 0 ? 'eager' : 'lazy') + '"></div>' +
        '</article>';
      }).join('');

      $('#slide-dots').innerHTML = banners.map(function (b, i) {
        return '<button type="button" role="tab" aria-label="切换到第 ' + (i + 1) + ' 张" aria-selected="' + (i === 0) + '" class="' + (i === 0 ? 'active' : '') + '" data-i="' + i + '"></button>';
      }).join('');

      var self = this;
      $$('#slide-dots button').forEach(function (btn) {
        btn.addEventListener('click', function () { self.go(parseInt(btn.dataset.i, 10)); self.play(); });
      });
      $('#slide-prev').addEventListener('click', function () { self.go(self.idx - 1); self.play(); });
      $('#slide-next').addEventListener('click', function () { self.go(self.idx + 1); self.play(); });
      var box = $('#carousel');
      box.addEventListener('mouseenter', function () { self.stop(); });
      box.addEventListener('mouseleave', function () { self.play(); });
      document.addEventListener('visibilitychange', function () { document.hidden ? self.stop() : self.play(); });
      this.go(0);
      this.play();
    },
    go: function (i) {
      this.idx = (i + this.total) % this.total;
      $$('#slides .slide').forEach(function (el, n) { el.classList.toggle('active', n === i); });
      $$('#slide-dots button').forEach(function (el, n) {
        el.classList.toggle('active', n === i);
        el.setAttribute('aria-selected', n === i ? 'true' : 'false');
      });
      var box = $('#carousel');
      if (box) box.setAttribute('data-theme', (this.themes && this.themes[i]) || 'gold');
      var c = $('#slide-count');
      if (c) c.textContent = String(i + 1).padStart(2, '0') + ' / ' + String(this.total).padStart(2, '0');
    },
    play: function () {
      var self = this;
      this.stop();
      if (this.total < 2) return;
      this.timer = setInterval(function () { self.go(self.idx + 1); }, 5200);
    },
    stop: function () { clearInterval(this.timer); this.timer = null; }
  };

  /* ---------------------------------------------------------------------
   * 3. 渲染各区块
   * ------------------------------------------------------------------- */
  function renderCategories(list) {
    var colorMap = { yellow: '', blue: 'c-blue', red: 'c-red', white: 'c-white' };
    $('#category-grid').innerHTML = list.map(function (c) {
      return '<a class="cat-card ' + (colorMap[c.color] || '') + '" href="' + esc(c.href) + '">' +
        '<span class="cat-ico">' + icon(c.icon) + '</span>' +
        '<h3>' + esc(c.name) + '</h3><p>' + esc(c.desc) + '</p>' +
        '<div class="cat-foot"><b>' + esc(c.short) + '</b><span>' + c.count + ' 款在售 ' + icon('i-arrow') + '</span></div>' +
      '</a>';
    }).join('');
  }

  function renderFilters(list) {
    var tabs = [{ id: 'all', name: '全部商品' }].concat(list.map(function (c) { return { id: c.id, name: c.short }; }));
    $('#filter-tabs').innerHTML = tabs.map(function (t, i) {
      return '<button type="button" role="tab" data-cat="' + esc(t.id) + '" aria-selected="' + (i === 0) + '" class="' + (i === 0 ? 'active' : '') + '">' + esc(t.name) + '</button>';
    }).join('');
    $$('#filter-tabs button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        $$('#filter-tabs button').forEach(function (b) {
          b.classList.remove('active'); b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active'); btn.setAttribute('aria-selected', 'true');
        $('#search-input').value = '';
        loadProducts(btn.dataset.cat, '');
      });
    });
  }

  function productCard(p) {
    var badgeCls = p.category === 'electrical' ? 'blue' : (p.category === 'lightweight' ? 'gold' : '');
    var catName = (window.CATALOG.categories.find(function (c) { return c.id === p.category; }) || {}).short || '安全帽';
    return '<article class="product-card" data-id="' + esc(p.id) + '">' +
      '<div class="product-media"><img src="' + esc(p.image) + '" alt="' + esc(p.name) + ' 产品示意插画" loading="lazy" width="320" height="220">' +
        (p.badge ? '<span class="product-badge ' + badgeCls + '">' + esc(p.badge) + '</span>' : '') + '</div>' +
      '<div class="product-body">' +
        '<span class="product-cat">' + esc(catName) + ' · ' + esc(p.id.toUpperCase()) + '</span>' +
        '<h3>' + esc(p.name) + '</h3>' +
        '<div class="product-tags">' + (p.tags || []).map(function (t) { return '<span>' + esc(t) + '</span>'; }).join('') + '</div>' +
        '<div class="price-row"><span class="price"><small>¥</small>' + Number(p.price).toFixed(0) + '</span>' +
          '<span class="price-old">' + yuan(p.originalPrice) + '</span>' +
          '<span class="price-sales">已售 ' + Number(p.sales).toLocaleString('zh-CN') + '</span></div>' +
        '<div class="product-actions">' +
          '<button class="btn btn-cart" type="button" data-add="' + esc(p.id) + '">加入购物车</button>' +
          '<a class="btn btn-detail" href="' + esc((window.CATALOG.categories.find(function (c) { return c.id === p.category; }) || {}).href || 'products/index.html') + '">查看详情</a>' +
        '</div>' +
      '</div></article>';
  }

  function loadProducts(category, keyword) {
    return CatalogService.products(category, keyword).then(function (rows) {
      var grid = $('#product-grid');
      grid.innerHTML = rows.length
        ? rows.map(productCard).join('')
        : '<div class="product-empty">没有匹配的商品，试试搜索「电力」「建筑」或切换到全部分类。</div>';
      $$('[data-add]', grid).forEach(function (btn) {
        btn.addEventListener('click', function () { Cart.add(btn.dataset.add); });
      });
    }).catch(function (err) {
      $('#product-grid').innerHTML = '<div class="product-empty">商品数据加载失败：' + esc(err.message) + '</div>';
    });
  }

  function renderPromotions(list) {
    $('#promo-grid').innerHTML = list.map(function (pr) {
      var extra = pr.type === 'flash' ? '<div class="countdown" id="countdown"><span>距本场结束</span><b id="cd-h">00</b>:<b id="cd-m">00</b>:<b id="cd-s">00</b></div>' : '';
      return '<article class="promo-card ' + esc(pr.accent) + '">' +
        '<span class="promo-eyebrow">' + esc(pr.eyebrow) + '</span>' +
        '<h3>' + esc(pr.title) + '</h3>' +
        '<p>' + esc(pr.desc) + '</p>' + extra +
        '<span class="promo-meta">' + esc(pr.meta) + '</span>' +
        '<a class="promo-link" href="' + esc(pr.href) + '">' + esc(pr.cta) + ' ' + icon('i-arrow') + '</a>' +
      '</article>';
    }).join('');
    startCountdown();
  }

  function startCountdown() {
    var h = $('#cd-h'), m = $('#cd-m'), s = $('#cd-s');
    if (!h) return;
    function tick() {
      var now = new Date();
      var end = new Date(now); end.setHours(23, 59, 59, 999);
      var left = Math.max(0, Math.floor((end - now) / 1000));
      h.textContent = String(Math.floor(left / 3600)).padStart(2, '0');
      m.textContent = String(Math.floor(left % 3600 / 60)).padStart(2, '0');
      s.textContent = String(left % 60).padStart(2, '0');
    }
    tick(); setInterval(tick, 1000);
  }

  function renderArticles(list) {
    $('#article-grid').innerHTML = list.map(function (a) {
      return '<a class="article-card" href="' + esc(a.href) + '">' +
        '<span class="article-cat">' + esc(a.cat) + '</span>' +
        '<h3>' + esc(a.title) + '</h3>' +
        '<div class="article-foot"><span>约 ' + esc(a.read) + '</span><b>阅读全文 →</b></div>' +
      '</a>';
    }).join('');
  }

  /* ---------------------------------------------------------------------
   * 4. 购物车（本地演示）
   * ------------------------------------------------------------------- */
  var Cart = {
    KEY: 'aqm_cart_v1',
    items: function () { return store(this.KEY) || []; },
    save: function (arr) { store(this.KEY, arr); this.render(); },
    add: function (id) {
      var arr = this.items();
      var hit = arr.find(function (x) { return x.id === id; });
      if (hit) hit.qty += 1;
      else arr.push({ id: id, qty: 1 });
      this.save(arr);
      var p = window.CATALOG.products.find(function (x) { return x.id === id; });
      toast('已加入购物车：' + (p ? p.name : id));
    },
    count: function () { return this.items().reduce(function (n, x) { return n + x.qty; }, 0); },
    render: function () {
      var arr = this.items();
      var badge = $('#cart-count');
      if (badge) badge.textContent = this.count();
      var body = $('#cart-body'), total = 0;
      if (!body) return;
      if (!arr.length) {
        body.innerHTML = '<div class="cart-empty">购物车还是空的<br>去「热门商品」挑几顶安全帽吧</div>';
      } else {
        body.innerHTML = arr.map(function (line) {
          var p = window.CATALOG.products.find(function (x) { return x.id === line.id; });
          if (!p) return '';
          total += p.price * line.qty;
          return '<div class="cart-line" data-line="' + esc(p.id) + '">' +
            '<img src="' + esc(p.image) + '" alt="" loading="lazy">' +
            '<div><strong>' + esc(p.name) + '</strong><small>' + yuan(p.price) + ' × ' + line.qty + '</small></div>' +
            '<button class="icon-btn" type="button" data-minus="' + esc(p.id) + '" aria-label="减少数量" style="height:30px;padding:0 9px">−</button>' +
            '<button class="icon-btn" type="button" data-plus="' + esc(p.id) + '" aria-label="增加数量" style="height:30px;padding:0 9px">+</button>' +
            '<button class="icon-btn" type="button" data-del="' + esc(p.id) + '" aria-label="移除" style="height:30px;padding:0 9px">×</button>' +
          '</div>';
        }).join('');
        $$('[data-plus]', body).forEach(function (b) { b.onclick = function () { Cart.add(b.dataset.plus); }; });
        $$('[data-minus]', body).forEach(function (b) {
          b.onclick = function () {
            var a = Cart.items(), hit = a.find(function (x) { return x.id === b.dataset.minus; });
            if (hit) { hit.qty -= 1; if (hit.qty <= 0) a.splice(a.indexOf(hit), 1); }
            Cart.save(a);
          };
        });
        $$('[data-del]', body).forEach(function (b) {
          b.onclick = function () { Cart.save(Cart.items().filter(function (x) { return x.id !== b.dataset.del; })); };
        });
      }
      var t = $('#cart-total'); if (t) t.textContent = yuan(total);
    },
    open: function () { $('#cart-drawer').classList.add('open'); },
    close: function () { $('#cart-drawer').classList.remove('open'); }
  };

  /* ---------------------------------------------------------------------
   * 5. 登录（本地演示会话，非真实账号体系）
   * ------------------------------------------------------------------- */
  var Auth = {
    KEY: 'aqm_session_v1',
    tab: 'phone',
    current: function () { return store(this.KEY); },
    open: function () {
      var o = $('#login-overlay');
      o.classList.add('open');
      this.refresh();
      setTimeout(function () { var el = $('#login-identity'); if (el && !Auth.current()) el.focus(); }, 60);
    },
    close: function () { $('#login-overlay').classList.remove('open'); },
    refresh: function () {
      var user = this.current();
      $('#login-form').style.display = user ? 'none' : '';
      $('#signed-in-panel').style.display = user ? '' : 'none';
      if (user) $('#signed-in-name').textContent = user.name;
      $('#user-chip').classList.toggle('on', !!user);
      if (user) {
        $('#user-name').textContent = user.name;
        $('#user-avatar').textContent = user.name.slice(0, 1).toUpperCase();
        $('#login-label').textContent = '我的账号';
      } else {
        $('#login-label').textContent = '登录 / 注册';
      }
    },
    signIn: function (identity, tab) {
      var name = tab === 'phone' ? identity.slice(0, 3) + '****' + identity.slice(-4) : identity.split('@')[0];
      store(this.KEY, { name: name, via: tab, at: Date.now() });
      this.refresh(); this.close();
      toast('登录成功（演示会话，仅存本机）');
    },
    signOut: function () {
      try { localStorage.removeItem(this.KEY); } catch (e) {}
      this.refresh(); this.close();
      toast('已退出登录');
    }
  };

  function initAuthUI() {
    var msg = $('#login-msg');
    var codeSent = false, countdown = 0, cdTimer;

    $$('.tabs button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        Auth.tab = btn.dataset.tab;
        $$('.tabs button').forEach(function (b) {
          b.classList.toggle('active', b === btn);
          b.setAttribute('aria-selected', b === btn ? 'true' : 'false');
        });
        var isPhone = Auth.tab === 'phone';
        $('#field-identity label').textContent = isPhone ? '手机号' : '邮箱';
        var input = $('#login-identity');
        input.type = isPhone ? 'tel' : 'email';
        input.placeholder = isPhone ? '请输入 11 位手机号' : '请输入邮箱地址';
        input.value = '';
        $('#login-code').value = '';
        msg.textContent = ''; msg.classList.remove('ok');
      });
    });

    $('#send-code').addEventListener('click', function () {
      var v = $('#login-identity').value.trim();
      var valid = Auth.tab === 'phone' ? /^1\d{10}$/.test(v) : /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
      if (!valid) {
        msg.textContent = Auth.tab === 'phone' ? '请输入正确的 11 位手机号' : '请输入正确的邮箱地址';
        msg.classList.remove('ok'); return;
      }
      codeSent = true;
      msg.textContent = '演示验证码已生成，输入任意 6 位数字即可登录';
      msg.classList.add('ok');
      countdown = 60;
      var btn = this;
      btn.disabled = true;
      btn.textContent = countdown + 's 后重发';
      clearInterval(cdTimer);
      cdTimer = setInterval(function () {
        countdown -= 1;
        if (countdown <= 0) { clearInterval(cdTimer); btn.disabled = false; btn.textContent = '重新获取'; }
        else btn.textContent = countdown + 's 后重发';
      }, 1000);
    });

    $('#login-identity').addEventListener('input', function () { msg.textContent = ''; });

    $('#login-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var identity = $('#login-identity').value.trim();
      var code = $('#login-code').value.trim();
      var valid = Auth.tab === 'phone' ? /^1\d{10}$/.test(identity) : /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identity);
      if (!valid) { msg.textContent = '请先填写正确的' + (Auth.tab === 'phone' ? '手机号' : '邮箱'); msg.classList.remove('ok'); return; }
      if (!codeSent) { msg.textContent = '请先点击「获取验证码」'; msg.classList.remove('ok'); return; }
      if (!/^\d{6}$/.test(code)) { msg.textContent = '请输入 6 位数字验证码'; msg.classList.remove('ok'); return; }
      Auth.signIn(identity, Auth.tab);
    });

    $('#login-btn').addEventListener('click', function () { Auth.open(); });
    $('#login-close').addEventListener('click', function () { Auth.close(); });
    $('#logout-btn').addEventListener('click', function () { Auth.signOut(); });
    $('#login-overlay').addEventListener('click', function (e) { if (e.target === this) Auth.close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { Auth.close(); Cart.close(); }
    });
    Auth.refresh();
  }

  /* ---------------------------------------------------------------------
   * 6. 其他交互
   * ------------------------------------------------------------------- */
  function initMisc() {
    $('#year').textContent = new Date().getFullYear();
    $('#cart-btn').addEventListener('click', function () { Cart.render(); Cart.open(); });
    $('#cart-close').addEventListener('click', function () { Cart.close(); });
    $('#cart-checkout').addEventListener('click', function () {
      var arr = Cart.items();
      if (!arr.length) { toast('购物车为空，先挑几顶安全帽吧'); return; }
      var lines = arr.map(function (x) {
        var p = window.CATALOG.products.find(function (y) { return y.id === x.id; });
        return p ? p.name + ' × ' + x.qty + '（' + yuan(p.price * x.qty) + '）' : '';
      }).filter(Boolean);
      var text = '安全帽.cn 集采需求清单（演示）\n' + lines.join('\n');
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { toast('清单已复制到剪贴板（演示环境不提交）'); },
          function () { toast('清单已生成（演示环境不提交）'); });
      } else { toast('清单已生成（演示环境不提交）'); }
    });

    $('#search-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var q = $('#search-input').value.trim();
      $$('#filter-tabs button').forEach(function (b) {
        b.classList.toggle('active', b.dataset.cat === 'all');
        b.setAttribute('aria-selected', b.dataset.cat === 'all' ? 'true' : 'false');
      });
      loadProducts('all', q).then(function () {
        $('#hot').scrollIntoView({ behavior: 'smooth', block: 'start' });
        toast(q ? '搜索「' + q + '」的结果' : '已展示全部商品');
      });
    });

    var top = $('#back-top');
    window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 520); }, { passive: true });
    top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ---------------------------------------------------------------------
   * 7. 启动
   * ------------------------------------------------------------------- */
  CatalogService.get().then(function (d) {
    Carousel.init(d.banners || []);
    renderCategories(d.categories || []);
    renderFilters(d.categories || []);
    renderPromotions(d.promotions || []);
    renderArticles(d.articles || []);
    loadProducts('all', '');
    Cart.render();
    initAuthUI();
    initMisc();
  }).catch(function (err) {
    ['#category-grid', '#product-grid', '#promo-grid', '#article-grid'].forEach(function (sel) {
      var el = $(sel);
      if (el) el.innerHTML = '<div class="product-empty">数据加载失败：' + esc(err.message) + '</div>';
    });
  });
})();
