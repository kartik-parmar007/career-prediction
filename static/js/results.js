/**
 * Results Visualization Module (Clean White / Light Theme)
 * Handles Chart.js charts and UI rendering for both Career and Skill Test Results.
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('career-results-view')) {
    initCareerResultsPage();
  }
  if (document.getElementById('skill-results-view')) {
    initSkillResultsPage();
  }
});

// ==========================================
// 1. Career Results Page Initialization
// ==========================================
function initCareerResultsPage() {
  const session = window.SessionStore.getSession();
  const careerResults = session.careerResults;

  const container = document.getElementById('top-careers-container');
  if (!container) return;

  if (!careerResults || !careerResults.top_recommendations || careerResults.top_recommendations.length === 0) {
    container.innerHTML = `
      <div class="col-span-full glass-card p-6 sm:p-8 text-center text-slate-700">
        <i class="fa-solid fa-clipboard-question text-3xl sm:text-4xl text-indigo-600 mb-3"></i>
        <h3 class="text-lg sm:text-xl font-bold text-slate-900 mb-2">No Career Assessment Found</h3>
        <p class="text-xs sm:text-sm text-slate-500 mb-5">Take our 15-question AI assessment to discover your top IT career matches.</p>
        <a href="/career-test" class="gradient-btn px-5 py-2.5 rounded-xl text-xs sm:text-sm inline-block">Start Career Assessment</a>
      </div>
    `;
    return;
  }

  const recs = careerResults.top_recommendations;

  let cardsHtml = '';
  const medals = ['🥇 Top Match', '🥈 2nd Match', '🥉 3rd Match'];
  const medalColors = ['bg-amber-50 border-amber-300 text-amber-800',
                       'bg-slate-100 border-slate-300 text-slate-700',
                       'bg-amber-50 border-amber-200 text-amber-900'];

  recs.forEach((rec, idx) => {
    const isPrimary = (idx === 0);
    const medalLabel = medals[idx] || `Rank #${idx + 1}`;
    const medalStyle = medalColors[idx] || 'border-indigo-200 text-indigo-700 bg-indigo-50';

    cardsHtml += `
      <div class="glass-card p-5 sm:p-7 flex flex-col justify-between relative overflow-hidden transition-all duration-300 ${isPrimary ? 'border-indigo-400 ring-2 ring-indigo-500/20 shadow-md' : 'hover:border-indigo-200'}">
        ${isPrimary ? `<div class="absolute top-0 right-0 bg-indigo-600 text-white text-[10px] sm:text-[11px] font-bold px-3 py-0.5 rounded-bl-xl uppercase tracking-wider shadow-sm">Top Match</div>` : ''}

        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${medalStyle}">${medalLabel}</span>
            <span class="badge-pill badge-cyan text-[10px]">${rec.difficulty}</span>
          </div>

          <div class="flex items-center gap-3 mb-3">
            <div class="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-xl text-indigo-600 shrink-0">
              <i class="${rec.icon || 'fa-solid fa-code'}"></i>
            </div>
            <div>
              <h3 class="text-lg sm:text-xl font-bold text-slate-900">${rec.title}</h3>
              <div class="text-xs sm:text-sm font-semibold text-emerald-600 flex items-center gap-1 mt-0.5">
                <i class="fa-solid fa-chart-line text-[11px]"></i> ${rec.compatibility}% Compatibility Match
              </div>
            </div>
          </div>

          <p class="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">${rec.description}</p>

          <div class="mb-4 p-3 rounded-xl bg-indigo-50/60 border border-indigo-100">
            <h4 class="text-[11px] font-bold uppercase tracking-wider text-indigo-800 mb-1 flex items-center gap-1">
              <i class="fa-solid fa-sparkles text-[10px]"></i> Why It Matches
            </h4>
            <p class="text-xs text-slate-700 leading-relaxed">${rec.why_matches}</p>
          </div>

          <div class="mb-4">
            <h4 class="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">Core Skills</h4>
            <div class="flex flex-wrap gap-1">
              ${(rec.key_skills || []).map(skill => `<span class="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-slate-700 text-[11px] font-medium">${skill}</span>`).join('')}
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 mb-4 text-xs text-slate-500">
            <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
              <span class="block text-slate-400 text-[10px] mb-0.5">Salary Range</span>
              <span class="font-semibold text-slate-800 text-xs">${rec.salary_range}</span>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
              <span class="block text-slate-400 text-[10px] mb-0.5">Typical Role</span>
              <span class="font-semibold text-slate-800 text-xs truncate block">${(rec.typical_roles && rec.typical_roles[0]) || 'Specialist'}</span>
            </div>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 flex flex-col gap-2">
          <a href="/skill-test?test_id=${rec.career_id}" onclick="selectTargetCareer('${rec.career_id}', '${rec.title}')" class="gradient-btn w-full py-2.5 rounded-xl text-center text-xs font-semibold flex items-center justify-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-vial"></i> Take Skill Test (10 MCQs)
          </a>
        </div>
      </div>
    `;
  });

  container.innerHTML = cardsHtml;
  renderCareerRadarChart(careerResults.all_compatibilities || {});
}

function selectTargetCareer(careerId, careerTitle) {
  window.SessionStore.setSelectedCareer(careerId, careerTitle);
}

function renderCareerRadarChart(compatibilities) {
  const chartCanvas = document.getElementById('career-radar-chart');
  if (!chartCanvas || !window.Chart) return;

  const labels = [
    'Frontend', 'Backend', 'Full Stack', 'Mobile', 
    'Data Analyst', 'Data Science', 'AI/ML', 'Cloud/DevOps', 
    'Security', 'QA', 'UI/UX', 'Data Eng'
  ];

  const keys = [
    'frontend', 'backend', 'fullstack', 'mobile',
    'data_analyst', 'data_scientist', 'ai_ml', 'devops_cloud',
    'cybersecurity', 'qa_automation', 'ui_ux', 'data_engineer'
  ];

  const scores = keys.map(k => compatibilities[k] || 50);

  new Chart(chartCanvas, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Compatibility %',
        data: scores,
        backgroundColor: 'rgba(99, 102, 241, 0.16)',
        borderColor: '#4f46e5',
        borderWidth: 2.5,
        pointBackgroundColor: '#06b6d4',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: '#4f46e5',
        pointHoverBorderColor: '#ffffff',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(203, 213, 225, 0.7)' },
          grid: { color: 'rgba(226, 232, 240, 0.9)' },
          pointLabels: {
            color: '#334155',
            font: { size: 10, family: 'Inter', weight: '600' }
          },
          ticks: {
            display: false,
            backdropColor: 'transparent',
            min: 30,
            max: 100
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// ==========================================
// 2. Skill Results Page Initialization
// ==========================================
function initSkillResultsPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const testId = urlParams.get('test_id') || 'fullstack';

  const resultData = window.SessionStore.getSkillTestResult(testId);
  const container = document.getElementById('skill-results-view');
  if (!container) return;

  if (!resultData) {
    container.innerHTML = `
      <div class="glass-card p-6 sm:p-8 text-center text-slate-700">
        <i class="fa-solid fa-chart-pie text-3xl sm:text-4xl text-rose-500 mb-3"></i>
        <h3 class="text-lg sm:text-xl font-bold text-slate-900 mb-2">No Test Result Found</h3>
        <p class="text-xs sm:text-sm text-slate-500 mb-5">Select a skill test from our catalog to assess your technical readiness.</p>
        <a href="/skill-tests" class="gradient-btn px-5 py-2.5 rounded-xl text-xs sm:text-sm inline-block">Explore Skill Tests</a>
      </div>
    `;
    return;
  }

  // Populate Header Stats
  const titleEl = document.getElementById('result-test-title');
  const scorePctEl = document.getElementById('result-score-pct');
  const correctCountEl = document.getElementById('result-correct-count');
  const levelBadgeEl = document.getElementById('result-level-badge');

  if (titleEl) titleEl.innerText = resultData.title;
  if (scorePctEl) scorePctEl.innerText = `${resultData.technical_readiness}%`;
  if (correctCountEl) correctCountEl.innerText = `${resultData.correct_count} / 10 Correct`;
  if (levelBadgeEl) levelBadgeEl.innerText = resultData.current_level;

  // Populate Strengths & Weaknesses
  const strengthsContainer = document.getElementById('strong-areas-list');
  const weaknessesContainer = document.getElementById('weak-areas-list');

  if (strengthsContainer) {
    if (resultData.strong_areas && resultData.strong_areas.length > 0) {
      strengthsContainer.innerHTML = resultData.strong_areas.map(area => `
        <li class="flex items-center gap-2 text-xs sm:text-sm text-emerald-700 font-medium py-0.5">
          <i class="fa-solid fa-circle-check text-emerald-600 text-xs"></i> ${area}
        </li>
      `).join('');
    } else {
      strengthsContainer.innerHTML = `<li class="text-xs text-slate-500 italic">Continue practicing to solidify mastery areas.</li>`;
    }
  }

  if (weaknessesContainer) {
    if (resultData.weak_areas && resultData.weak_areas.length > 0) {
      weaknessesContainer.innerHTML = resultData.weak_areas.map(area => `
        <li class="flex items-center gap-2 text-xs sm:text-sm text-amber-800 font-medium py-0.5">
          <i class="fa-solid fa-triangle-exclamation text-amber-600 text-xs"></i> ${area}
        </li>
      `).join('');
    } else {
      weaknessesContainer.innerHTML = `<li class="text-xs text-emerald-700 font-medium">✓ Excellent! No critical gaps detected.</li>`;
    }
  }

  // Render Horizontal Bar Chart for Topic Breakdown
  renderTopicBreakdownChart(resultData.topic_breakdown || {});

  // Render Question Review
  renderQuestionReviewAccordion(resultData.question_reviews || []);
}

function renderTopicBreakdownChart(topics) {
  const canvas = document.getElementById('topic-breakdown-chart');
  if (!canvas || !window.Chart) return;

  const labels = Object.keys(topics);
  const dataValues = labels.map(l => topics[l].percentage);
  const backgroundColors = dataValues.map(v => v >= 70 ? 'rgba(16, 185, 129, 0.85)' : 'rgba(245, 158, 11, 0.85)');

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Proficiency %',
        data: dataValues,
        backgroundColor: backgroundColors,
        borderRadius: 6,
        barThickness: 14
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          min: 0,
          max: 100,
          grid: { color: 'rgba(226, 232, 240, 0.8)' },
          ticks: { color: '#64748b', font: { family: 'Inter', size: 10 }, callback: v => `${v}%` }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#1e293b', font: { family: 'Inter', size: 11, weight: '600' } }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderQuestionReviewAccordion(reviews) {
  const container = document.getElementById('question-review-list');
  if (!container) return;

  let html = '';
  reviews.forEach((r, idx) => {
    const isCorrect = r.is_correct;
    const badgeClass = isCorrect ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : 'text-rose-700 bg-rose-50 border-rose-200';
    const statusIcon = isCorrect ? 'fa-solid fa-check' : 'fa-solid fa-xmark';

    html += `
      <div class="glass-card p-4 sm:p-5 border border-slate-200 rounded-xl mb-3 shadow-sm">
        <div class="flex items-start justify-between gap-2 mb-2">
          <span class="text-[11px] sm:text-xs font-semibold text-slate-500">Q${idx + 1} • <span class="text-indigo-600 font-bold">${r.topic}</span></span>
          <span class="px-2 py-0.5 rounded-full text-[10px] sm:text-xs font-bold border ${badgeClass} flex items-center gap-1 shrink-0">
            <i class="${statusIcon}"></i> ${isCorrect ? 'Correct' : 'Incorrect'}
          </span>
        </div>

        <h4 class="text-xs sm:text-sm md:text-base font-semibold text-slate-900 mb-3 leading-relaxed">${r.question}</h4>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs mb-3">
          <div class="p-2.5 rounded-lg ${isCorrect ? 'bg-emerald-50 border border-emerald-200 text-emerald-900' : 'bg-rose-50 border border-rose-200 text-rose-900'}">
            <span class="font-bold block text-[10px] uppercase mb-0.5">Your Answer</span>
            <span class="leading-snug">${r.user_selected >= 0 ? r.options[r.user_selected] : 'None selected'}</span>
          </div>
          <div class="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900">
            <span class="font-bold block text-[10px] uppercase mb-0.5">Correct Answer</span>
            <span class="leading-snug">${r.options[r.correct_answer]}</span>
          </div>
        </div>

        <div class="text-xs text-slate-700 p-2.5 sm:p-3 rounded-lg bg-slate-50 border border-slate-200 leading-relaxed">
          <strong class="text-indigo-700 block mb-0.5 text-[11px] uppercase tracking-wider font-semibold">Explanation</strong>
          ${r.explanation}
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

window.selectTargetCareer = selectTargetCareer;
