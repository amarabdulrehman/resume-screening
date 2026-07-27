/**
 * main.js — RecruitAI Client-side Enhancements
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Sidebar toggle (mobile) ─────────────────────────
  const toggle  = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Auto-dismiss flash alerts after 5 seconds ───────
  document.querySelectorAll('.alert-custom').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getInstance(el) || new bootstrap.Alert(el);
      bsAlert.close();
    }, 5000);
  });

  // ── Animate score bars on visible ───────────────────
  const barObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.width = entry.target.dataset.width || entry.target.style.width;
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.score-bar, .mini-bar, .breakdown-bar').forEach(el => {
    const w = el.style.width;
    el.style.width = '0';
    el.dataset.width = w;
    barObserver.observe(el);
  });

  // ── Table row click navigation ───────────────────────
  document.querySelectorAll('tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => window.location.href = row.dataset.href);
  });

  // ── Confirm dialog on danger forms ──────────────────
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });

});
