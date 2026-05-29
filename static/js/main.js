/* ══════════════════════════════════════════════════
   AI RESUME ANALYZER – MAIN JS
══════════════════════════════════════════════════ */

// Theme is handled inline in base.html for zero-flash.
// This file handles UI enhancements only.

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss alerts after 5s ──────────────────
  document.querySelectorAll('.alert.fade.show').forEach(function (el) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Animate progress bars on load ────────────────
  document.querySelectorAll('.progress-bar[data-width]').forEach(function (bar) {
    const w = bar.getAttribute('data-width');
    setTimeout(function () { bar.style.width = w + '%'; }, 100);
  });

  // ── Bootstrap tooltips ────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  // ── File input label update ───────────────────────
  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener('change', function () {
      const label = document.querySelector('label[for="' + input.id + '"]');
      if (label && input.files.length > 0) {
        label.textContent = input.files[0].name;
      }
    });
  });

  // ── Upload drop zone drag & drop ─────────────────
  const zone = document.querySelector('.upload-zone');
  if (zone) {
    const fileInput = zone.querySelector('input[type="file"]');
    if (fileInput) {
      fileInput.addEventListener('click', function (e) {
        e.stopPropagation();
      });
    }

    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', function () {
      zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      zone.classList.remove('drag-over');
      if (fileInput && e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        fileInput.dispatchEvent(new Event('change'));
      }
    });
    zone.addEventListener('click', function () {
      if (fileInput) {
        fileInput.click();
      }
    });
  }

  // ── Sidebar Mobile Toggle ─────────────────────────
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebarClose = document.getElementById('sidebar-close');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggle && sidebar && sidebarBackdrop) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.add('show');
      sidebarBackdrop.classList.add('show');
      document.body.style.overflow = 'hidden';
    });
  }

  function closeSidebar() {
    if (sidebar && sidebarBackdrop) {
      sidebar.classList.remove('show');
      sidebarBackdrop.classList.remove('show');
      document.body.style.overflow = '';
    }
  }

  if (sidebarClose) {
    sidebarClose.addEventListener('click', closeSidebar);
  }
  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', closeSidebar);
  }

});
