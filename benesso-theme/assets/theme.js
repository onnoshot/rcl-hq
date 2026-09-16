/* =========================================================================
   BENESSO — interaction & animation engine
   ========================================================================= */
(function () {
  'use strict';
  var reduce = document.documentElement.classList.contains('reduce-motion');

  /* ---------- Scroll reveal ---------- */
  function initReveal() {
    var els = document.querySelectorAll('.reveal,.reveal-scale,.reveal-left,.reveal-right,[data-stagger]');
    if (reduce || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Count-up stats ---------- */
  function initCounters() {
    var nums = document.querySelectorAll('[data-count-to]');
    if (!nums.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target, target = parseFloat(el.dataset.countTo),
            suffix = el.dataset.countSuffix || '', dur = 1400, t0 = null;
        if (reduce) { el.textContent = target + suffix; io.unobserve(el); return; }
        function step(ts) {
          if (!t0) t0 = ts;
          var p = Math.min((ts - t0) / dur, 1), eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased).toLocaleString('tr-TR') + suffix;
          if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
        io.unobserve(el);
      });
    }, { threshold: 0.5 });
    nums.forEach(function (n) { io.observe(n); });
  }

  /* ---------- Header scroll behaviour ---------- */
  function initHeader() {
    var header = document.querySelector('.site-header');
    if (!header) return;
    var last = 0;
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      header.classList.toggle('is-scrolled', y > 24);
      if (!reduce) header.classList.toggle('is-hidden', y > last && y > 240);
      last = y;
    }, { passive: true });
  }

  /* ---------- Mobile nav ---------- */
  function initNav() {
    var toggle = document.querySelector('.nav-toggle'), nav = document.querySelector('.nav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { nav.classList.remove('is-open'); document.body.style.overflow = ''; });
    });
  }

  /* ---------- Magnetic buttons ---------- */
  function initMagnetic() {
    if (reduce || matchMedia('(pointer:coarse)').matches) return;
    document.querySelectorAll('[data-magnetic]').forEach(function (el) {
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.25;
        var y = (e.clientY - r.top - r.height / 2) * 0.4;
        el.style.transform = 'translate(' + x + 'px,' + y + 'px)';
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------- 3D tilt cards ---------- */
  function initTilt() {
    if (reduce || matchMedia('(pointer:coarse)').matches) return;
    document.querySelectorAll('[data-tilt]').forEach(function (el) {
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = 'perspective(900px) rotateY(' + (px * 8) + 'deg) rotateX(' + (-py * 8) + 'deg)';
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------- Parallax on scroll ---------- */
  function initParallax() {
    if (reduce) return;
    var els = document.querySelectorAll('[data-parallax]');
    if (!els.length) return;
    var ticking = false;
    function update() {
      var vh = window.innerHeight;
      els.forEach(function (el) {
        var r = el.getBoundingClientRect();
        var speed = parseFloat(el.dataset.parallax) || 0.15;
        var offset = (r.top + r.height / 2 - vh / 2) * -speed;
        el.style.transform = 'translateY(' + offset + 'px)';
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  }

  /* ---------- Cupping bars fill on view ---------- */
  function initCupping() {
    var bars = document.querySelectorAll('.cup-bar__fill[data-level]');
    if (!bars.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.style.width = (parseFloat(e.target.dataset.level) * 20) + '%'; io.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    bars.forEach(function (b) { io.observe(b); });
  }

  /* ---------- Product option pills ---------- */
  function initOptionPills() {
    document.querySelectorAll('.opt-pills').forEach(function (group) {
      group.addEventListener('change', function (e) {
        if (e.target.type !== 'radio') return;
        group.querySelectorAll('.opt-pill').forEach(function (p) { p.classList.remove('is-checked'); });
        e.target.closest('.opt-pill').classList.add('is-checked');
      });
    });
  }

  /* ---------- PDP gallery ---------- */
  function initGallery() {
    var main = document.querySelector('[data-pdp-main]');
    if (!main) return;
    document.querySelectorAll('[data-pdp-thumb]').forEach(function (t) {
      t.addEventListener('click', function () {
        main.src = t.dataset.full || t.querySelector('img').src;
        document.querySelectorAll('[data-pdp-thumb]').forEach(function (x) { x.classList.remove('is-active'); });
        t.classList.add('is-active');
      });
    });
  }

  /* ---------- AJAX Cart ---------- */
  var Cart = {
    drawer: null,
    open: function () { if (this.drawer) this.drawer.classList.add('is-open'); document.body.style.overflow = 'hidden'; },
    close: function () { if (this.drawer) this.drawer.classList.remove('is-open'); document.body.style.overflow = ''; },
    refresh: function () {
      fetch('/cart.js').then(function (r) { return r.json(); }).then(function (c) { Cart.render(c); });
    },
    render: function (c) {
      document.querySelectorAll('[data-cart-count]').forEach(function (el) {
        el.textContent = c.item_count; el.dataset.count = c.item_count;
      });
      var body = document.querySelector('[data-cart-items]');
      var foot = document.querySelector('[data-cart-total]');
      if (foot) foot.textContent = Cart.money(c.total_price);
      if (!body) return;
      if (!c.items.length) { body.innerHTML = '<p class="muted center" style="padding:3rem 0">Sepetin boş. Bir kahve seç ✦</p>'; return; }
      body.innerHTML = c.items.map(function (i) {
        return '<div class="cart-line"><img src="' + (i.image ? i.image.replace(/(\.[a-z]+)(\?.*)?$/i, '_120x$1') : '') + '" alt="" loading="lazy">' +
          '<div><div style="font-weight:600">' + i.product_title + '</div>' +
          '<div class="muted" style="font-size:.8rem">' + (i.variant_title || '') + '</div>' +
          '<div style="margin-top:.4rem" class="qty"><button data-line-dn="' + i.key + '">−</button><span style="padding:0 .6rem;font-family:var(--font-mono)">' + i.quantity + '</span><button data-line-up="' + i.key + '">+</button></div></div>' +
          '<div style="font-family:var(--font-mono);font-weight:700">' + Cart.money(i.final_line_price) + '</div></div>';
      }).join('');
    },
    money: function (cents) { return (cents / 100).toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + ' ₺'; },
    add: function (form) {
      var btn = form.querySelector('[type=submit]');
      if (btn) { btn.classList.add('is-loading'); btn.disabled = true; }
      fetch('/cart/add.js', { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function () { Cart.refresh(); Cart.open(); })
        .catch(function () { form.submit(); })
        .finally(function () { if (btn) { btn.classList.remove('is-loading'); btn.disabled = false; } });
    },
    change: function (key, qty) {
      fetch('/cart/change.js', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify({ id: key, quantity: qty }) })
        .then(function (r) { return r.json(); }).then(function (c) { Cart.render(c); });
    }
  };

  function initCart() {
    Cart.drawer = document.querySelector('.cart-drawer');
    document.addEventListener('click', function (e) {
      if (e.target.closest('[data-cart-open]')) { e.preventDefault(); Cart.refresh(); Cart.open(); }
      if (e.target.closest('[data-cart-close]') || e.target.classList.contains('cart-drawer__overlay')) Cart.close();
      var up = e.target.closest('[data-line-up]'), dn = e.target.closest('[data-line-dn]');
      if (up) { var key = up.dataset.lineUp; var qs = up.previousElementSibling; Cart.change(key, parseInt(qs.textContent) + 1); }
      if (dn) { var k2 = dn.dataset.lineDn; var q2 = dn.nextElementSibling; Cart.change(k2, Math.max(0, parseInt(q2.textContent) - 1)); }
    });
    document.querySelectorAll('form[action$="/cart/add"]').forEach(function (form) {
      form.addEventListener('submit', function (e) { e.preventDefault(); Cart.add(form); });
    });
    Cart.refresh();
  }

  /* ---------- Init ---------- */
  function ready(fn) { document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn); }
  ready(function () {
    initReveal(); initCounters(); initHeader(); initNav(); initMagnetic(); initTilt();
    initParallax(); initCupping(); initOptionPills(); initGallery(); initCart();
  });
})();
