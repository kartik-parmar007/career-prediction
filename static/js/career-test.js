/**
 * Career Assessment Stepper (15 Questions)
 * One-question-at-a-time transition, progress calculation, and ML analysis modal.
 */

let careerQuestions = [];
let currentQuestionIndex = 0;
let userAnswers = {};

document.addEventListener('DOMContentLoaded', async () => {
  await loadCareerQuestions();
});

async function loadCareerQuestions() {
  const container = document.getElementById('career-quiz-container');
  if (!container) return;

  try {
    const response = await fetch('/api/career-questions');
    const data = await response.json();
    if (data.status === 'success' && data.questions) {
      careerQuestions = data.questions;

      // Restore previously saved answers if any
      const session = window.SessionStore.getSession();
      if (session.assessmentAnswers) {
        userAnswers = { ...session.assessmentAnswers };
      }

      renderCurrentQuestion();
    } else {
      throw new Error(data.message || 'Failed to load questions');
    }
  } catch (err) {
    console.error(err);
    container.innerHTML = `
      <div class="glass-card p-6 sm:p-8 text-center text-rose-300">
        <i class="fa-solid fa-triangle-exclamation text-2xl sm:text-3xl mb-2 sm:mb-3"></i>
        <h3 class="text-lg sm:text-xl font-bold mb-2">Unable to Load Assessment</h3>
        <p class="text-xs sm:text-sm text-slate-400 mb-4">${err.message}</p>
        <button onclick="location.reload()" class="gradient-btn px-5 py-2 rounded-xl text-xs sm:text-sm">Retry</button>
      </div>
    `;
  }
}

function renderCurrentQuestion() {
  const container = document.getElementById('career-quiz-container');
  if (!container || careerQuestions.length === 0) return;

  const total = careerQuestions.length; // 15 questions
  const q = careerQuestions[currentQuestionIndex];
  const progressPct = Math.round(((currentQuestionIndex + 1) / total) * 100);

  // Update Header Progress Bar
  const progressText = document.getElementById('quiz-progress-text');
  const progressFill = document.getElementById('quiz-progress-fill');
  const progressPctLabel = document.getElementById('quiz-progress-pct');

  if (progressText) progressText.innerText = `${currentQuestionIndex + 1} of ${total}`;
  if (progressFill) progressFill.style.width = `${progressPct}%`;
  if (progressPctLabel) progressPctLabel.innerText = `${progressPct}%`;

  const selectedVal = userAnswers[q.feature_key];

  let optionsHtml = '';
  q.options.forEach((opt) => {
    const isSelected = (selectedVal !== undefined && selectedVal === opt.value);
    const selectedClass = isSelected ? 'selected' : '';

    optionsHtml += `
      <div class="mcq-option ${selectedClass}" onclick="selectAnswer('${q.feature_key}', '${opt.value}')">
        <div class="mcq-radio-indicator"></div>
        <div class="flex-1">
          <div class="font-semibold text-slate-100 text-xs sm:text-sm md:text-base">${opt.label}</div>
          ${opt.description ? `<div class="text-[11px] sm:text-xs text-slate-400 mt-0.5 leading-relaxed">${opt.description}</div>` : ''}
        </div>
      </div>
    `;
  });

  const isFirst = currentQuestionIndex === 0;
  const isLast = currentQuestionIndex === total - 1;
  const hasAnswer = selectedVal !== undefined;

  container.innerHTML = `
    <div class="animate-fade-in flex flex-col justify-between h-full">
      <div>
        <div class="mb-4 sm:mb-6">
          <span class="badge-pill badge-indigo mb-1.5">Question ${currentQuestionIndex + 1}</span>
          <h2 class="text-base sm:text-xl md:text-2xl font-bold text-slate-100 mt-1 leading-snug">${q.question}</h2>
          ${q.subtitle ? `<p class="text-xs sm:text-sm text-slate-400 mt-1">${q.subtitle}</p>` : ''}
        </div>

        <div class="flex flex-col gap-2.5 sm:gap-3 mb-6">
          ${optionsHtml}
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-slate-800 gap-2">
        <button 
          onclick="prevQuestion()" 
          class="px-4 sm:px-5 py-2.5 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs sm:text-sm font-medium transition ${isFirst ? 'opacity-30 pointer-events-none' : ''}">
          <i class="fa-solid fa-arrow-left mr-1.5"></i> Previous
        </button>

        ${isLast ? `
          <button 
            onclick="submitAssessment()" 
            class="gradient-btn px-5 sm:px-7 py-2.5 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-1.5 ${!hasAnswer ? 'opacity-50 cursor-not-allowed' : ''}">
            <i class="fa-solid fa-sparkles"></i> View Results
          </button>
        ` : `
          <button 
            onclick="nextQuestion()" 
            class="gradient-btn px-5 sm:px-6 py-2.5 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-1.5 ${!hasAnswer ? 'opacity-50 cursor-not-allowed' : ''}">
            Next <i class="fa-solid fa-arrow-right ml-1"></i>
          </button>
        `}
      </div>
    </div>
  `;
}

function selectAnswer(featureKey, value) {
  const parsedVal = isNaN(Number(value)) ? value : Number(value);
  userAnswers[featureKey] = parsedVal;
  window.SessionStore.saveAssessmentAnswers(userAnswers);
  renderCurrentQuestion();
}

function nextQuestion() {
  const q = careerQuestions[currentQuestionIndex];
  if (userAnswers[q.feature_key] === undefined) {
    window.showToast('Please select an option before proceeding', 'error');
    return;
  }
  if (currentQuestionIndex < careerQuestions.length - 1) {
    currentQuestionIndex++;
    renderCurrentQuestion();
  }
}

function prevQuestion() {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    renderCurrentQuestion();
  }
}

async function submitAssessment() {
  const q = careerQuestions[currentQuestionIndex];
  if (userAnswers[q.feature_key] === undefined) {
    window.showToast('Please select an option before submitting', 'error');
    return;
  }

  showAnalysisModal();

  try {
    const response = await fetch('/api/career/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: userAnswers })
    });

    const data = await response.json();
    if (data.status === 'success') {
      window.SessionStore.saveCareerResults(data);

      await animateAnalysisSteps();

      setTimeout(() => {
        window.location.href = '/career-result';
      }, 350);
    } else {
      throw new Error(data.message || 'Analysis failed');
    }
  } catch (err) {
    console.error(err);
    hideAnalysisModal();
    window.showToast(`Error: ${err.message}`, 'error');
  }
}

function showAnalysisModal() {
  const modal = document.getElementById('analysis-loading-modal');
  if (modal) modal.classList.remove('hidden');
}

function hideAnalysisModal() {
  const modal = document.getElementById('analysis-loading-modal');
  if (modal) modal.classList.add('hidden');
}

async function animateAnalysisSteps() {
  const steps = [
    'step-processing-interests',
    'step-analyzing-preferences',
    'step-comparing-paths',
    'step-generating-recs'
  ];

  for (let i = 0; i < steps.length; i++) {
    const el = document.getElementById(steps[i]);
    if (el) {
      el.classList.remove('loading-step-pending');
      el.classList.add('loading-step-done');
      const icon = el.querySelector('.loading-step-icon');
      if (icon) icon.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i>';
    }
    await new Promise(r => setTimeout(r, 350));
  }
}

window.selectAnswer = selectAnswer;
window.nextQuestion = nextQuestion;
window.prevQuestion = prevQuestion;
window.submitAssessment = submitAssessment;
