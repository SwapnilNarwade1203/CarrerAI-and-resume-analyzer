/* ══════════════════════════════════════════════════
   AI RESUME ANALYZER – MAIN JAVASCRIPT
═══════════════════════════════════════════════════ */

(function() {
  // ── Theme Management ───────────────────────────
  const html = document.documentElement;
  const THEME_KEY = 'ra_theme';

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }

  function toggleTheme() {
    const current = html.getAttribute('data-theme') || 'dark';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  }

  // Load saved theme
  const savedTheme = localStorage.getItem(THEME_KEY) || 'dark';
  applyTheme(savedTheme);

  // Attach theme buttons
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#themeToggle, #themeToggleMobile').forEach(btn => {
      btn.addEventListener('click', toggleTheme);
    });

    // ── Mobile Sidebar ─────────────────────────
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('mobileMenuBtn');
    if (menuBtn && sidebar) {
      menuBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
      // Close on outside click
      document.addEventListener('click', e => {
        if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      });
    }

    // ── Auto-dismiss alerts ────────────────────
    document.querySelectorAll('.alert').forEach(alert => {
      setTimeout(() => {
        if (alert && alert.parentElement) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateX(20px)';
          alert.style.transition = 'all 0.5s';
          setTimeout(() => alert.remove(), 500);
        }
      }, 4000);
    });

    // ── Active nav auto-highlight ──────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
      if (link.getAttribute('href') && currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/') {
        link.classList.add('active');
      }
    });

    // ── Skill level circle animation ───────────
    document.querySelectorAll('.skill-level-circle').forEach(el => {
      const text = el.querySelector('span');
      if (text) {
        const pct = parseInt(text.textContent) || 0;
        el.style.background = `conic-gradient(var(--primary) ${pct}%, var(--bg-card-light) 0%)`;
      }
    });

    // ── Score ring animation ───────────────────
    document.querySelectorAll('.score-ring-lg, .score-ring-xl').forEach(el => {
      const scoreEl = el.querySelector('[data-score]') || el.querySelector('.score-val-xl, .score-val-lg');
      if (scoreEl) {
        const pct = parseInt(scoreEl.textContent) || 0;
        el.style.background = `conic-gradient(var(--primary) ${pct * 3.6}deg, rgba(255,255,255,0.06) 0deg)`;
      }
    });

    // ── Interview question expand icon ─────────
    document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(btn => {
      btn.addEventListener('click', function() {
        const icon = this.querySelector('.collapse-icon');
        if (icon) icon.style.transform = this.classList.contains('collapsed') ? 'rotate(0)' : 'rotate(180deg)';
      });
    });

    // ── Animate progress bars ──────────────────
    const observer = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.width = e.target.getAttribute('data-width') || e.target.style.width;
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.2 });
    document.querySelectorAll('.progress-bar').forEach(bar => observer.observe(bar));

    // ── Tooltip init (Bootstrap) ───────────────
    const tooltipEls = document.querySelectorAll('[title]');
    tooltipEls.forEach(el => {
      if (typeof bootstrap !== 'undefined') {
        new bootstrap.Tooltip(el, { trigger: 'hover', delay: { show: 400, hide: 100 } });
      }
    });

    // ── Smooth scroll ──────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
      });
    });

    // ── Print button helpers ───────────────────
    document.querySelectorAll('[data-print]').forEach(btn => {
      btn.addEventListener('click', () => window.print());
    });
  });
})();
