/**
 * Main Global Application Script
 * Manages Navigation, Mobile Menu, Session indicators, and Toast notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarSessionBadge();
  initClearSessionHandler();
  initMobileMenu();

  window.addEventListener('sessionUpdated', () => {
    initNavbarSessionBadge();
  });
});

function initNavbarSessionBadge() {
  const sessionBadge = document.getElementById('navbar-session-status');
  if (!sessionBadge) return;

  const session = window.SessionStore ? window.SessionStore.getSession() : null;
  if (!session) return;

  if (session.selectedCareerTitle) {
    sessionBadge.innerHTML = `
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      <span class="text-xs font-semibold text-indigo-300 max-w-[100px] sm:max-w-[140px] truncate">${session.selectedCareerTitle}</span>
    `;
    sessionBadge.classList.remove('hidden');
    sessionBadge.classList.add('flex');
  } else if (session.assessmentAnswers) {
    sessionBadge.innerHTML = `
      <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
      <span class="text-xs text-slate-300 font-medium">Assessed</span>
    `;
    sessionBadge.classList.remove('hidden');
    sessionBadge.classList.add('flex');
  } else {
    sessionBadge.classList.add('hidden');
    sessionBadge.classList.remove('flex');
  }
}

function initClearSessionHandler() {
  const clearButtons = document.querySelectorAll('[data-action="clear-session"]');
  clearButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (confirm('Reset your assessment session and start fresh?')) {
        if (window.SessionStore) {
          window.SessionStore.clearSession();
          showToast('Session reset successfully', 'success');
          setTimeout(() => {
            window.location.href = '/';
          }, 350);
        }
      }
    });
  });
}

function initMobileMenu() {
  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  const menuIcon = document.getElementById('mobile-menu-icon');

  if (toggleBtn && mobileMenu) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = mobileMenu.classList.contains('hidden');
      if (isHidden) {
        mobileMenu.classList.remove('hidden');
        if (menuIcon) {
          menuIcon.classList.remove('fa-bars');
          menuIcon.classList.add('fa-xmark');
        }
      } else {
        mobileMenu.classList.add('hidden');
        if (menuIcon) {
          menuIcon.classList.remove('fa-xmark');
          menuIcon.classList.add('fa-bars');
        }
      }
    });

    // Close on navigation link click
    const mobileLinks = mobileMenu.querySelectorAll('.mobile-nav-link, a');
    mobileLinks.forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
        if (menuIcon) {
          menuIcon.classList.remove('fa-xmark');
          menuIcon.classList.add('fa-bars');
        }
      });
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!mobileMenu.contains(e.target) && !toggleBtn.contains(e.target)) {
        if (!mobileMenu.classList.contains('hidden')) {
          mobileMenu.classList.add('hidden');
          if (menuIcon) {
            menuIcon.classList.remove('fa-xmark');
            menuIcon.classList.add('fa-bars');
          }
        }
      }
    });
  }
}

// Global Toast Notification Helper
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'fixed bottom-4 right-4 left-4 sm:left-auto sm:max-w-sm z-50 flex flex-col gap-2 pointer-events-none';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const bg = type === 'success' ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-200' :
             type === 'error' ? 'bg-rose-950/90 border-rose-500/50 text-rose-200' :
             'bg-slate-900/90 border-indigo-500/50 text-slate-200';

  const icon = type === 'success' ? 'fa-solid fa-circle-check text-emerald-400' :
               type === 'error' ? 'fa-solid fa-circle-exclamation text-rose-400' :
               'fa-solid fa-circle-info text-indigo-400';

  toast.className = `pointer-events-auto flex items-center gap-2.5 px-4 py-3 rounded-xl border backdrop-blur-md shadow-2xl transition-all duration-300 animate-fade-in text-xs sm:text-sm font-medium ${bg}`;
  toast.innerHTML = `
    <i class="${icon} text-sm"></i>
    <span class="flex-1">${message}</span>
  `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}

window.showToast = showToast;
