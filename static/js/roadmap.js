/**
 * AI Personalized Roadmap Manager
 * Connects to /api/ai/roadmap, renders multi-phase learning cards, and tracks task completion.
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (document.getElementById('roadmap-view-container')) {
    await initRoadmap();
  }
});

async function initRoadmap() {
  const container = document.getElementById('roadmap-view-container');
  const loadingOverlay = document.getElementById('roadmap-loading-overlay');
  if (!container) return;

  const session = window.SessionStore.getSession();
  const context = window.SessionStore.getAdvisorContext();

  if (session.activeRoadmap) {
    renderRoadmapData(session.activeRoadmap);
    return;
  }

  if (loadingOverlay) loadingOverlay.classList.remove('hidden');

  try {
    const payload = {
      career_id: context.selected_career_id,
      career_title: context.selected_career_title,
      compatibility_pct: context.compatibility_pct,
      readiness_pct: context.readiness_pct,
      weak_topics: context.weak_topics,
      strong_topics: context.strong_topics,
      weekly_hours: context.weekly_hours
    };

    const response = await fetch('/api/ai/roadmap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (data.status === 'success' && data.roadmap) {
      window.SessionStore.saveRoadmap(data.roadmap);
      renderRoadmapData(data.roadmap);
    } else {
      throw new Error(data.message || 'Failed to generate roadmap');
    }
  } catch (err) {
    console.error(err);
    container.innerHTML = `
      <div class="glass-card p-6 sm:p-8 text-center text-rose-300">
        <i class="fa-solid fa-triangle-exclamation text-2xl sm:text-3xl mb-2 sm:mb-3"></i>
        <h3 class="text-lg sm:text-xl font-bold mb-2">Roadmap Generation Error</h3>
        <p class="text-xs sm:text-sm text-slate-400 mb-4">${err.message}</p>
        <button onclick="location.reload()" class="gradient-btn px-5 py-2 rounded-xl text-xs sm:text-sm">Retry</button>
      </div>
    `;
  } finally {
    if (loadingOverlay) loadingOverlay.classList.add('hidden');
  }
}

function renderRoadmapData(roadmap) {
  const container = document.getElementById('roadmap-phases-timeline');
  const summaryEl = document.getElementById('roadmap-custom-summary');
  const careerTitleEl = document.getElementById('roadmap-career-title');
  const durationBadgeEl = document.getElementById('roadmap-total-duration');
  const sourceBadgeEl = document.getElementById('roadmap-source-badge');

  if (careerTitleEl) careerTitleEl.innerText = roadmap.career_title || 'IT Career';
  if (summaryEl) summaryEl.innerText = roadmap.custom_summary || '';
  if (durationBadgeEl) durationBadgeEl.innerText = roadmap.total_estimated_months || '5 - 6 Months';

  if (sourceBadgeEl) {
    if (roadmap.generated_by === 'live_ai') {
      sourceBadgeEl.innerHTML = `<i class="fa-solid fa-sparkles text-cyan-400"></i> AI Generated`;
    } else {
      sourceBadgeEl.innerHTML = `<i class="fa-solid fa-microchip text-indigo-400"></i> AI Engine`;
    }
  }

  if (!container || !roadmap.phases) return;

  let phasesHtml = '';
  roadmap.phases.forEach((p, idx) => {
    const phaseNum = p.phase || (idx + 1);
    const focusTag = p.focus_tag || (phaseNum === 1 ? 'Priority Gap' : 'Core Mastery');
    const isPriority = focusTag.toLowerCase().includes('priority') || focusTag.toLowerCase().includes('gap');

    phasesHtml += `
      <div class="glass-card p-5 sm:p-7 relative overflow-hidden transition-all duration-300 hover:border-indigo-500/50">
        <div class="flex flex-wrap items-center justify-between gap-2.5 mb-3.5">
          <div class="flex items-center gap-2.5">
            <span class="w-8 h-8 rounded-xl bg-indigo-950/90 border border-indigo-500/40 text-indigo-300 font-bold flex items-center justify-center text-xs sm:text-sm shadow-sm">
              0${phaseNum}
            </span>
            <h3 class="text-base sm:text-lg font-bold text-slate-100">${p.title}</h3>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${isPriority ? 'bg-amber-950/50 border-amber-500/40 text-amber-300' : 'bg-indigo-950/40 border-indigo-500/30 text-indigo-300'}">
              ${focusTag}
            </span>
            <span class="badge-pill badge-cyan text-[10px]">${p.duration}</span>
          </div>
        </div>

        <div class="mb-4">
          <h4 class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">Core Skills</h4>
          <div class="flex flex-wrap gap-1 mb-2.5">
            ${(p.skills || []).map(s => `<span class="px-2 py-0.5 rounded-md bg-slate-800/80 border border-slate-700 text-slate-200 text-[11px] font-medium">${s}</span>`).join('')}
          </div>
          <ul class="text-xs text-slate-300 space-y-1 pl-4 list-disc marker:text-indigo-400">
            ${(p.topics || []).map(t => `<li>${t}</li>`).join('')}
          </ul>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2 pt-3 border-t border-slate-800">
          <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <h5 class="text-[11px] font-bold text-indigo-300 uppercase tracking-wider mb-2 flex items-center gap-1">
              <i class="fa-solid fa-list-check text-[10px]"></i> Practice Tasks
            </h5>
            <ul class="text-xs text-slate-300 space-y-1.5">
              ${(p.practice_tasks || []).map((task, tIdx) => `
                <li class="flex items-start gap-2">
                  <input type="checkbox" id="task-${phaseNum}-${tIdx}" class="mt-0.5 w-3.5 h-3.5 rounded text-indigo-600 focus:ring-0 bg-slate-800 border-slate-700 cursor-pointer" onchange="toggleTaskCheck('task-${phaseNum}-${tIdx}')">
                  <label for="task-${phaseNum}-${tIdx}" class="leading-snug cursor-pointer select-none">${task}</label>
                </li>
              `).join('')}
            </ul>
          </div>

          <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <h5 class="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-1.5 flex items-center gap-1">
              <i class="fa-solid fa-folder-open text-[10px]"></i> Milestone Capstone
            </h5>
            <p class="text-xs text-slate-200 font-semibold mb-1">${p.project}</p>
            <p class="text-xs text-slate-400 leading-relaxed"><strong class="text-slate-300">Milestone:</strong> ${p.milestone}</p>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = phasesHtml;
  restoreTaskCheckboxes();
}

function toggleTaskCheck(taskId) {
  const checkbox = document.getElementById(taskId);
  if (!checkbox) return;
  const checks = JSON.parse(localStorage.getItem('roadmap_task_checks') || '{}');
  checks[taskId] = checkbox.checked;
  localStorage.setItem('roadmap_task_checks', JSON.stringify(checks));
}

function restoreTaskCheckboxes() {
  const checks = JSON.parse(localStorage.getItem('roadmap_task_checks') || '{}');
  Object.keys(checks).forEach(id => {
    const el = document.getElementById(id);
    if (el) el.checked = checks[id];
  });
}

function regenerateRoadmap() {
  if (confirm('Regenerate your AI roadmap with latest assessment results?')) {
    window.SessionStore.saveRoadmap(null);
    initRoadmap();
  }
}

window.toggleTaskCheck = toggleTaskCheck;
window.regenerateRoadmap = regenerateRoadmap;
