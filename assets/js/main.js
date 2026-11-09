/* 安全帽.cn 官网交互脚本 —— 无依赖、可离线运行 */
(function () {
  'use strict';

  /* 移动端导航 */
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');
  if (toggle && links) {
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      links.classList.toggle('is-open', open);
      var label = toggle.querySelector('.nav-toggle-text');
      if (label) label.textContent = open ? '关闭菜单' : '打开菜单';
    };
    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setOpen(false);
    });
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
  }

  /* 页脚年份（真实当前年份，非企业资料） */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* 表单校验与提交 */
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var PHONE = /^[0-9+\-() ]{7,20}$/;

  function mark(field, invalid) {
    var wrap = field.closest('.field') || field.closest('.checkbox-field');
    if (wrap) wrap.classList.toggle('invalid', invalid);
    field.setAttribute('aria-invalid', String(invalid));
    return invalid;
  }

  function validate(form) {
    var firstBad = null;
    form.querySelectorAll('[data-validate]').forEach(function (field) {
      var value = (field.value || '').trim();
      var bad = false;
      switch (field.getAttribute('data-validate')) {
        case 'required': bad = value.length === 0; break;
        case 'name': bad = value.length < 2; break;
        case 'phone': bad = !PHONE.test(value) || value.replace(/\D/g, '').length < 7; break;
        case 'email': bad = value.length > 0 && !EMAIL.test(value); break;
        case 'message': bad = value.length < 10; break;
        case 'checked': bad = !field.checked; break;
      }
      if (mark(field, bad) && !firstBad) firstBad = field;
    });
    return firstBad;
  }

  function collect(form) {
    var data = {};
    form.querySelectorAll('[name]').forEach(function (el) {
      if (el.type === 'checkbox' || el.type === 'submit') return;
      data[el.name] = (el.value || '').trim();
    });
    return data;
  }

  function buildMailBody(d) {
    return [
      '安全帽.cn 官网业务咨询',
      '--------------------------------',
      '姓名：' + (d.name || '未填写'),
      '单位：' + (d.company || '未填写'),
      '联系电话：' + (d.phone || '未填写'),
      '电子邮箱：' + (d.email || '未填写'),
      '咨询类别：' + (d.category || '未填写'),
      '需求描述：',
      d.message || '未填写',
      '--------------------------------',
      '（本内容由官网表单生成，请核对后发送）'
    ].join('\n');
  }

  function notice(form, html, kind) {
    var box = form.querySelector('.form-notice');
    if (!box) return;
    box.innerHTML = html;
    box.className = 'form-notice show ' + (kind || 'ok');
    box.setAttribute('role', 'status');
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function copyText(text, btn) {
    var done = function () {
      var old = btn.textContent;
      btn.textContent = '已复制';
      setTimeout(function () { btn.textContent = old; }, 2200);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(); });
    } else {
      fallback();
    }
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { /* 忽略：用户可手工复制 */ }
      document.body.removeChild(ta);
    }
  }

  var CONSULT_MAIL = 'mfujun@agent.qq.com';

  document.querySelectorAll('.js-inquiry-form').forEach(function (form) {
    var mode = form.getAttribute('data-mode') || 'mailto';

    form.querySelectorAll('[data-validate]').forEach(function (field) {
      field.addEventListener('input', function () { mark(field, false); });
      field.addEventListener('change', function () { mark(field, false); });
    });

    /* 从首页快速咨询带入的内容 */
    if (mode === 'mailto' && window.sessionStorage) {
      try {
        var raw = sessionStorage.getItem('aqm_quick');
        if (raw) {
          var q = JSON.parse(raw);
          Object.keys(q).forEach(function (k) {
            var el = form.querySelector('[name="' + k + '"]');
            if (el && !el.value) el.value = q[k];
          });
          sessionStorage.removeItem('aqm_quick');
          notice(form, '已带入您在首页填写的信息，请补充完整后提交。', 'warn');
        }
      } catch (e) { /* 忽略存储异常 */ }
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = validate(form);
      if (bad) {
        notice(form, '请检查标红的必填项后重新提交。', 'warn');
        bad.focus();
        return;
      }
      var d = collect(form);
      var body = buildMailBody(d);

      if (mode === 'handoff') {
        try { sessionStorage.setItem('aqm_quick', JSON.stringify(d)); } catch (err) { /* 忽略 */ }
        window.location.href = 'contact.html#inquiry';
        return;
      }

      var subject = encodeURIComponent('安全帽.cn 官网咨询 - ' + (d.category || '业务咨询') + ' - ' + (d.name || ''));
      var mailto = 'mailto:' + CONSULT_MAIL + '?subject=' + subject + '&body=' + encodeURIComponent(body);
      notice(form,
        '<strong>信息已填写完整。</strong>本站为纯静态实现，未接入后端收单服务，请选择以下任一方式把需求发给我们：' +
        '<div class="btn-row" style="margin-top:14px">' +
        '<a class="btn btn-primary btn-sm" href="' + mailto + '">用邮件客户端发送</a>' +
        '<button type="button" class="btn btn-outline btn-sm" data-copy>复制咨询内容</button>' +
        '</div>' +
        '<p style="margin:12px 0 0">也可直接发送至 <a href="mailto:' + CONSULT_MAIL + '">' + CONSULT_MAIL + '</a>，或致电页面中的咨询电话（占位，待企业填写）。</p>',
        'ok');
      var copyBtn = form.querySelector('[data-copy]');
      if (copyBtn) copyBtn.addEventListener('click', function () { copyText(body, copyBtn); });
    });
  });
})();
