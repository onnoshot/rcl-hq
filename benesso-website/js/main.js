/* ═══════════════════════════════════════════════════════════
   BENESSO COFFEE — Main JS
   ═══════════════════════════════════════════════════════════ */

'use strict';

/* ─── STICKY HEADER ──────────────────────────────────────── */
const header = document.getElementById('site-header');
const onScroll = () => {
  header.classList.toggle('scrolled', window.scrollY > 20);
};
window.addEventListener('scroll', onScroll, { passive: true });

/* ─── HAMBURGER / MOBILE NAV ─────────────────────────────── */
const hamburger = document.getElementById('hamburgerBtn');
const navMenu   = document.getElementById('navMenu');

hamburger.addEventListener('click', () => {
  const isOpen = navMenu.classList.toggle('open');
  hamburger.classList.toggle('open', isOpen);
  hamburger.setAttribute('aria-expanded', String(isOpen));
  document.body.style.overflow = isOpen ? 'hidden' : '';
});

// Dropdown toggles on mobile
navMenu.querySelectorAll('.has-dropdown').forEach(item => {
  item.addEventListener('click', e => {
    if (window.innerWidth > 768) return;
    e.preventDefault();
    item.classList.toggle('dropdown-open');
  });
});

// Close nav on link click
navMenu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    if (window.innerWidth > 768) return;
    navMenu.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  });
});

// Close on outside click
document.addEventListener('click', e => {
  if (!header.contains(e.target) && navMenu.classList.contains('open')) {
    navMenu.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
});

/* ─── SCROLL REVEAL ──────────────────────────────────────── */
const revealEls = document.querySelectorAll(
  '.product-card, .blog-card, .workshop-card, .classic-card, .about-pillars li, .trust-item, .wholesale-card, .insta-cell'
);

revealEls.forEach(el => el.classList.add('reveal'));

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Stagger delay for grid children
        const siblings = Array.from(entry.target.parentElement.children);
        const idx = siblings.indexOf(entry.target);
        entry.target.style.transitionDelay = `${Math.min(idx * 80, 400)}ms`;
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
);

revealEls.forEach(el => revealObserver.observe(el));

/* ─── BACK TO TOP ────────────────────────────────────────── */
const backToTop = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
  const show = window.scrollY > 400;
  backToTop.hidden = !show;
}, { passive: true });

backToTop.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

/* ─── FOOTER YEAR ────────────────────────────────────────── */
const yearEl = document.getElementById('footer-year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* ─── CART BADGE (stub — wire to real cart in Shopify) ──── */
let cartCount = 0;
document.querySelectorAll('.btn-add-mini, .quick-add').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    cartCount++;
    document.querySelectorAll('.cart-badge').forEach(b => {
      b.textContent = cartCount;
    });
    // Micro-animation
    btn.style.transform = 'scale(1.3)';
    setTimeout(() => { btn.style.transform = ''; }, 200);

    // Update aria-label on cart button
    const cartBtn = document.querySelector('.nav-cart-btn');
    if (cartBtn) cartBtn.setAttribute('aria-label', `Sepet (${cartCount} ürün)`);
  });
});

/* ─── CONTACT FORM ───────────────────────────────────────── */
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = contactForm.querySelector('[type="submit"]');
    const original = btn.textContent;
    btn.textContent = 'Gönderildi ✓';
    btn.disabled = true;
    btn.style.background = '#2D7A3A';
    setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
      btn.style.background = '';
      contactForm.reset();
    }, 3000);
  });
}

/* ─── NEWSLETTER FORM ────────────────────────────────────── */
const newsletterForm = document.querySelector('.newsletter-form');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = newsletterForm.querySelector('[type="submit"]');
    const original = btn.textContent;
    btn.textContent = 'Abone Olundunuz ✓';
    btn.disabled = true;
    setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
      newsletterForm.reset();
    }, 3000);
  });
}

/* ─── SMOOTH ANCHOR SCROLL (offset for sticky header) ───── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const targetId = this.getAttribute('href');
    if (targetId === '#') return;
    const target = document.querySelector(targetId);
    if (!target) return;
    e.preventDefault();
    const headerHeight = header.offsetHeight;
    const targetTop = target.getBoundingClientRect().top + window.scrollY - headerHeight - 16;
    window.scrollTo({ top: targetTop, behavior: 'smooth' });
  });
});
