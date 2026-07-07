/**
 * main.js — ChronicCare AI Global JavaScript
 * Dark mode, medication tracking, utilities, voice support
 */

/* ================================================================
   DARK MODE MANAGER
   ================================================================ */
const ThemeManager = {
  KEY: 'cc-theme',

  init() {
    const saved = localStorage.getItem(this.KEY) || 'light';
    this.apply(saved);
    this.bindToggles();
  },

  apply(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem(this.KEY, theme);
    const isDark = theme === 'dark';

    // Update all toggle icons
    document.querySelectorAll('[id^="darkIcon"]').forEach(icon => {
      icon.className = isDark ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-fill';
    });
  },

  toggle() {
    const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
    this.apply(current === 'dark' ? 'light' : 'dark');
  },

  bindToggles() {
    ['darkModeToggle', 'darkModeToggleMobile'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('click', () => this.toggle());
    });
  }
};

/* ================================================================
   MEDICATION TRACKING
   ================================================================ */
async function markMedTaken(medId, btn) {
  try {
    btn.disabled = true;
    const res = await fetch(`/patients/medications/${medId}/taken`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'ok') {
      btn.classList.remove('btn-success', 'btn-outline-success');
      btn.classList.add('btn-success');
      btn.innerHTML = '<i class="bi bi-check2-all"></i>';
      showToast(`✓ Medication marked as taken! Adherence: ${data.adherence}%`, 'success');
    }
  } catch(e) {
    btn.disabled = false;
    showToast('Failed to update. Please try again.', 'danger');
  }
}

/* ================================================================
   ALERT MANAGEMENT
   ================================================================ */
async function resolveAlert(patientId, alertId) {
  try {
    const res = await fetch(`/api/alerts/${patientId}/resolve/${alertId}`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'ok') {
      const el = document.getElementById(`alert-${alertId}`);
      if (el) {
        el.style.transition = 'opacity .3s, transform .3s';
        el.style.opacity = '0';
        el.style.transform = 'translateX(20px)';
        setTimeout(() => el.remove(), 300);
      }
    }
  } catch(e) {
    showToast('Failed to resolve alert.', 'danger');
  }
}

/* ================================================================
   AI INSIGHTS LOADER
   ================================================================ */
async function loadInsights(patientId) {
  const btn = document.getElementById('insightsBtn');
  const content = document.getElementById('insightsContent');
  if (!btn || !content) return;

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Analyzing…';
  content.innerHTML = `
    <div class="text-center py-5">
      <div class="spinner-border text-primary mb-3" style="width:2.5rem;height:2.5rem"></div>
      <p class="text-muted">IBM Granite AI is analyzing your health data…</p>
    </div>`;

  try {
    const res = await fetch(`/api/insights/${patientId}`);
    const data = await res.json();
    if (data.insights) {
      content.innerHTML = `<div class="ai-response-body">${formatAIResponse(data.insights)}</div>`;
    } else {
      content.innerHTML = '<p class="text-muted text-center py-3">No insights available. Log more health data.</p>';
    }
  } catch(e) {
    content.innerHTML = '<p class="text-danger text-center py-3"><i class="bi bi-wifi-off me-2"></i>Failed to load insights. Please try again.</p>';
  }

  btn.disabled = false;
  btn.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i>Refresh';
}

/* ================================================================
   AI RESPONSE FORMATTER
   ================================================================ */
function formatAIResponse(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^## (.+)$/gm, '<h5 class="text-primary mt-3 mb-2">$1</h5>')
    .replace(/^# (.+)$/gm, '<h4 class="text-primary mt-3 mb-2">$1</h4>')
    .replace(/^(\d+\..+)$/gm, '<p class="fw-semibold mt-2 mb-1">$1</p>')
    .replace(/^[•\-\*] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>(?:\s*<li>[\s\S]*?<\/li>)*)/g, '<ul class="mb-2">$1</ul>')
    .replace(/\n\n/g, '<br>')
    .replace(/\n(?!<)/g, '<br>');
}

/* ================================================================
   TOAST NOTIFICATIONS
   ================================================================ */
function showToast(message, type = 'info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-bg-${type} border-0 show`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.closest('.toast').remove()"></button>
    </div>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

/* ================================================================
   BMI COLOR CODING
   ================================================================ */
function applyBmiColors() {
  document.querySelectorAll('.bmi-value').forEach(el => {
    const bmi = parseFloat(el.dataset.bmi || el.textContent);
    el.classList.remove('bmi-underweight','bmi-normal','bmi-overweight','bmi-obese');
    if (bmi < 18.5)     el.classList.add('bmi-underweight');
    else if (bmi < 25)  el.classList.add('bmi-normal');
    else if (bmi < 30)  el.classList.add('bmi-overweight');
    else                el.classList.add('bmi-obese');
  });
}

/* ================================================================
   VOICE OUTPUT (Text to Speech)
   ================================================================ */
function speakText(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const clean = text.replace(/<[^>]+>/g, '').replace(/\*\*/g, '');
  const utt = new SpeechSynthesisUtterance(clean);
  utt.lang = 'en-US';
  utt.rate = 0.95;
  window.speechSynthesis.speak(utt);
}

/* ================================================================
   FORM UTILITIES
   ================================================================ */
function confirmDelete(message) {
  return confirm(message || 'Are you sure? This cannot be undone.');
}

// Auto-resize textarea
document.addEventListener('input', function(e) {
  if (e.target.classList.contains('chat-input')) {
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  }
});

/* ================================================================
   INIT
   ================================================================ */
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  applyBmiColors();

  // Animate progress bars
  document.querySelectorAll('.progress-bar[style*="width"]').forEach(bar => {
    const targetWidth = bar.style.width;
    bar.style.width = '0%';
    bar.style.transition = 'width 1s ease-out';
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = targetWidth; }, 100);
    });
  });

  // Initialize Bootstrap tooltips
  document.querySelectorAll('[title]').forEach(el => {
    try { new bootstrap.Tooltip(el, { trigger: 'hover', delay: { show: 300, hide: 0 } }); } catch(e) {}
  });
});
