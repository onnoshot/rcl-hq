/* ═══════════════════════════════════════════════
   UniqBee — Main JavaScript
   ═══════════════════════════════════════════════ */

// ── Nav scroll state ──
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

// ── Mobile nav toggle ──
const navToggle = document.getElementById('navToggle');
const navLinks  = document.getElementById('navLinks');
navToggle.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', open);
  // Animate hamburger → X
  const spans = navToggle.querySelectorAll('span');
  if (open) {
    spans[0].style.transform = 'rotate(45deg) translate(4px, 4px)';
    spans[1].style.transform = 'rotate(-45deg) translate(4px, -4px)';
  } else {
    spans[0].style.transform = '';
    spans[1].style.transform = '';
  }
});

// Close nav when a link is clicked
navLinks.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    navToggle.querySelectorAll('span').forEach(s => s.style.transform = '');
  });
});

// ── Scroll-reveal ──
const revealEls = document.querySelectorAll(
  '.service-card, .work-item, .process-step, .testimonial, .about__copy, .section-header'
);
revealEls.forEach(el => el.classList.add('reveal'));

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      // Stagger children within same parent
      const siblings = [...entry.target.parentElement.querySelectorAll('.reveal')];
      const delay = siblings.indexOf(entry.target) * 80;
      setTimeout(() => entry.target.classList.add('visible'), delay);
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

revealEls.forEach(el => revealObserver.observe(el));

// ── Video background: load & play gracefully ──
const heroVideo = document.getElementById('heroVideo');

function setVideoSrc(url) {
  if (!url || !heroVideo) return;
  const src = document.createElement('source');
  src.src = url;
  src.type = 'video/mp4';
  heroVideo.appendChild(src);
  heroVideo.load();
  heroVideo.play().catch(() => {
    // Autoplay blocked — poster image already shown, that's fine
  });
}

// Inline video URL if already resolved at build time
const VIDEO_URL = window.__UNIQBEE_VIDEO_URL__ || null;
if (VIDEO_URL) {
  setVideoSrc(VIDEO_URL);
}

// ── Smooth anchor scroll with nav offset ──
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h') || '72');
    window.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
  });
});

// ── Subtle parallax on hero content ──
const heroContent = document.querySelector('.hero__content');
window.addEventListener('scroll', () => {
  if (!heroContent) return;
  const y = window.scrollY;
  if (y < window.innerHeight) {
    heroContent.style.transform = `translateY(${y * 0.18}px)`;
    heroContent.style.opacity = 1 - (y / (window.innerHeight * 0.7));
  }
}, { passive: true });
