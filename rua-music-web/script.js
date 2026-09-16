(() => {
  "use strict";

  // Hero video: skip on data-saver connections, fall back to the poster still.
  const heroVideo = document.getElementById("heroVideo");
  const saveData = navigator.connection && navigator.connection.saveData;
  if (heroVideo && !saveData) {
    const source = heroVideo.querySelector("source[data-src]");
    if (source) {
      source.src = source.dataset.src;
      heroVideo.load();
      heroVideo.play().catch(() => {});
    }
  }

  const audio = document.getElementById("bgAudio");
  const soundToggle = document.getElementById("soundToggle");
  const soundTxt = soundToggle.querySelector(".txt");

  function syncSoundUI() {
    const on = !audio.paused && !audio.muted;
    soundToggle.setAttribute("aria-pressed", String(on));
    soundToggle.setAttribute("aria-label", on ? "Sesi kapat" : "Sesi aç");
    soundTxt.textContent = on ? "SESLİ" : "SESSİZ";
  }

  audio.addEventListener("play", syncSoundUI);
  audio.addEventListener("pause", syncSoundUI);
  audio.addEventListener("volumechange", syncSoundUI);

  // Try to start with sound immediately; browsers that block unmuted
  // autoplay will reject the promise, so retry on the user's first
  // interaction with the page (click, key, touch, or scroll) — but never
  // steal a click that landed on the toggle itself, otherwise that same
  // click both starts playback (via this fallback) and immediately mutes
  // it again (via the toggle's own handler reading the just-changed state).
  audio.muted = false;
  audio.play().catch(() => {
    syncSoundUI();
    const resume = (e) => {
      if (soundToggle.contains(e.target)) return;
      audio.play().catch(() => {});
    };
    ["pointerdown", "keydown", "touchstart", "wheel"].forEach((evt) =>
      window.addEventListener(evt, resume, { once: true, passive: true })
    );
  });

  soundToggle.addEventListener("click", () => {
    if (audio.muted || audio.paused) {
      audio.muted = false;
      audio.play().catch(() => {});
    } else {
      audio.muted = true;
    }
    syncSoundUI();
  });

  const track = document.getElementById("transportTrack");
  const fill = document.getElementById("transportFill");
  const timeEl = document.getElementById("transportTime");

  const sections = [
    { id: "hero", label: "Giriş" },
    { id: "about", label: "Hakkında" },
    { id: "tour", label: "Turne" },
    { id: "music", label: "Müzik" },
    { id: "style", label: "Stil" },
    { id: "gallery", label: "Galeri" },
    { id: "social", label: "Sosyal" },
    { id: "venues", label: "Mekanlar" },
    { id: "booking", label: "Booking" },
  ].map((s) => ({ ...s, el: document.getElementById(s.id) })).filter((s) => s.el);

  const cues = [];

  function layoutCues() {
    const doc = document.documentElement;
    const scrollable = Math.max(doc.scrollHeight - window.innerHeight, 1);
    sections.forEach((s) => {
      const pct = Math.min((s.el.offsetTop / scrollable) * 100, 100);
      if (s.btn) {
        s.btn.style.left = pct + "%";
      } else {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "transport__cue";
        btn.style.left = pct + "%";
        btn.setAttribute("aria-label", "Bölüme git: " + s.label);
        const label = document.createElement("span");
        label.className = "label";
        label.textContent = s.label;
        label.setAttribute("aria-hidden", "true");
        btn.appendChild(label);
        btn.addEventListener("click", () => {
          s.el.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "start" });
        });
        track.appendChild(btn);
        s.btn = btn;
        cues.push(s);
      }
    });
  }

  function prefersReducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  const SET_LENGTH_SECONDS = 225; // stylised progress readout, not a real track duration

  function formatTime(totalSeconds) {
    const m = Math.floor(totalSeconds / 60);
    const s = Math.floor(totalSeconds % 60);
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  let ticking = false;

  function updateProgress() {
    const doc = document.documentElement;
    const scrollable = Math.max(doc.scrollHeight - window.innerHeight, 1);
    const progress = Math.min(Math.max(window.scrollY / scrollable, 0), 1);

    fill.style.width = (progress * 100) + "%";
    timeEl.textContent = formatTime(progress * SET_LENGTH_SECONDS);

    let activeIndex = 0;
    sections.forEach((s, i) => {
      if (window.scrollY + window.innerHeight * 0.4 >= s.el.offsetTop) activeIndex = i;
    });
    sections.forEach((s, i) => {
      if (s.btn) s.btn.classList.toggle("is-active", i === activeIndex);
    });

    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(updateProgress);
      ticking = true;
    }
  }

  window.addEventListener("resize", () => {
    layoutCues();
    updateProgress();
  });

  window.addEventListener("scroll", onScroll, { passive: true });

  layoutCues();
  updateProgress();
})();
