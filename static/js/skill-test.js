/**
 * Technical Skill Test Engine (10 MCQs)
 * Question pagination, answer tracking, timer, responsive mobile palette, and evaluation submission.
 */

let currentTestId = null;
let testData = null;
let currentQIdx = 0;
let userMcqAnswers = {};
let timerSeconds = 0;
let timerInterval = null;

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  currentTestId = urlParams.get('test_id') || 'fullstack';
  await loadSkillTest(currentTestId);
  startTimer();
});

function startTimer() {
  const timerEl = document.getElementById('test-timer');
  if (!timerEl) return;
  timerInterval = setInterval(() => {
    timerSeconds++;
    const mins = Math.floor(timerSeconds / 60);
    const secs = timerSeconds % 60;
    timerEl.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, 1000);
}

async function loadSkillTest(testId) {
  const container = document.getElementById('skill-quiz-container');
  if (!container) return;

  try {
    const response = await fetch(`/api/skill-tests/${testId}`);
    const data = await response.json();
    if (data.status === 'success' && data.questions) {
      testData = data;
      userMcqAnswers = {};

      const testTitleEl = document.getElementById('test-title');
      const testCategoryEl = document.getElementById('test-category');
      if (testTitleEl) testTitleEl.innerText = data.title;
      if (testCategoryEl) testCategoryEl.innerText = data.category;

      renderMcqQuestion();
      renderQuestionGrid();
    } else {
      throw new Error(data.message || 'Failed to load test');
    }
  } catch (err) {
    console.error(err);
    container.innerHTML = `
      <div class="glass-card p-6 sm:p-8 text-center text-rose-300">
        <i class="fa-solid fa-triangle-exclamation text-2xl sm:text-3xl mb-2 sm:mb-3"></i>
        <h3 class="text-lg sm:text-xl font-bold mb-2">Skill Test Not Found</h3>
        <p class="text-xs sm:text-sm text-slate-400 mb-4">${err.message}</p>
        <a href="/skill-tests" class="gradient-btn px-5 py-2 rounded-xl text-xs sm:text-sm inline-block">Explore All Tests</a>
      </div>
    `;
  }
}

function renderMcqQuestion() {
  const container = document.getElementById('skill-quiz-container');
  if (!container || !testData || !testData.questions) return;

  const total = 10;
  const q = testData.questions[currentQIdx];
  const progressPct = Math.round(((currentQIdx + 1) / total) * 100);

  // Update Progress headers
  const progressText = document.getElementById('mcq-progress-text');
  const progressFill = document.getElementById('mcq-progress-fill');
  const progressCount = document.getElementById('mcq-answered-count');
  const mobileStatus = document.getElementById('mobile-palette-status');

  if (progressText) progressText.innerText = `Question ${currentQIdx + 1} of ${total}`;
  if (progressFill) progressFill.style.width = `${progressPct}%`;
  if (mobileStatus) mobileStatus.innerText = `Q${currentQIdx + 1} of ${total}`;
  
  const answeredCount = Object.keys(userMcqAnswers).length;
  if (progressCount) progressCount.innerText = `${answeredCount} / 10`;

  const selectedIdx = userMcqAnswers[q.id.toString()];

  let optionsHtml = '';
  q.options.forEach((optText, optIdx) => {
    const isSelected = (selectedIdx !== undefined && selectedIdx === optIdx);
    const selectedClass = isSelected ? 'selected' : '';

    optionsHtml += `
      <div class="mcq-option ${selectedClass}" onclick="selectMcqAnswer(${q.id}, ${optIdx})">
        <div class="mcq-radio-indicator"></div>
        <div class="flex-1 text-slate-200 text-xs sm:text-sm md:text-base font-medium leading-snug">
          ${optText}
        </div>
      </div>
    `;
  });

  const isFirst = currentQIdx === 0;
  const isLast = currentQIdx === total - 1;
  const allAnswered = answeredCount === 10;

  container.innerHTML = `
    <div class="animate-fade-in flex flex-col justify-between h-full">
      <div>
        <div class="flex items-center justify-between gap-2 mb-3">
          <span class="badge-pill badge-cyan text-[11px]">${q.topic || 'Core Concept'}</span>
          <span class="text-[11px] text-slate-400 font-medium capitalize">${q.difficulty || 'Medium'}</span>
        </div>

        <h2 class="text-base sm:text-lg md:text-xl font-bold text-slate-100 mb-5 leading-relaxed">
          ${q.question}
        </h2>

        <div class="flex flex-col gap-2.5 sm:gap-3 mb-6">
          ${optionsHtml}
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-slate-800 gap-2">
        <button 
          onclick="prevMcq()" 
          class="px-4 sm:px-5 py-2.5 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs sm:text-sm font-medium transition ${isFirst ? 'opacity-30 pointer-events-none' : ''}">
          <i class="fa-solid fa-arrow-left mr-1.5"></i> Previous
        </button>

        <div class="flex items-center gap-2">
          ${isLast ? `
            <button 
              onclick="submitSkillTest()" 
              class="gradient-btn px-5 sm:px-6 py-2.5 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-1.5 ${!allAnswered ? 'opacity-70' : ''}">
              <i class="fa-solid fa-circle-check"></i> Submit (${answeredCount}/10)
            </button>
          ` : `
            <button 
              onclick="nextMcq()" 
              class="gradient-btn px-5 sm:px-6 py-2.5 rounded-xl text-xs sm:text-sm font-semibold flex items-center gap-1.5">
              Next <i class="fa-solid fa-arrow-right ml-1"></i>
            </button>
          `}
        </div>
      </div>
    </div>
  `;

  renderQuestionGrid();
}

function renderQuestionGrid() {
  const desktopGrid = document.getElementById('question-palette-grid');
  const mobileGrid = document.getElementById('mobile-question-palette');
  if (!testData) return;

  let buttonsHtml = '';
  for (let i = 0; i < 10; i++) {
    const qid = (i + 1).toString();
    const isAnswered = userMcqAnswers[qid] !== undefined;
    const isCurrent = (i === currentQIdx);

    let btnClass = 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-500';
    if (isCurrent) {
      btnClass = 'border-indigo-500 bg-indigo-950/90 text-indigo-200 ring-2 ring-indigo-500/50 font-bold';
    } else if (isAnswered) {
      btnClass = 'bg-emerald-950/70 border-emerald-500/50 text-emerald-300 font-semibold';
    }

    buttonsHtml += `
      <button 
        onclick="jumpToQuestion(${i})" 
        class="w-8 h-8 sm:w-8 sm:h-8 shrink-0 rounded-lg text-xs border transition flex items-center justify-center ${btnClass}">
        ${i + 1}
      </button>
    `;
  }

  if (desktopGrid) desktopGrid.innerHTML = buttonsHtml;
  if (mobileGrid) mobileGrid.innerHTML = buttonsHtml;
}

function selectMcqAnswer(qid, optionIdx) {
  userMcqAnswers[qid.toString()] = optionIdx;
  renderMcqQuestion();
}

function nextMcq() {
  if (currentQIdx < 9) {
    currentQIdx++;
    renderMcqQuestion();
  }
}

function prevMcq() {
  if (currentQIdx > 0) {
    currentQIdx--;
    renderMcqQuestion();
  }
}

function jumpToQuestion(idx) {
  if (idx >= 0 && idx < 10) {
    currentQIdx = idx;
    renderMcqQuestion();
  }
}

async function submitSkillTest() {
  const answeredCount = Object.keys(userMcqAnswers).length;
  if (answeredCount < 10) {
    window.showToast(`Please answer all 10 questions (${answeredCount}/10 completed).`, 'error');
    return;
  }

  if (timerInterval) clearInterval(timerInterval);

  try {
    const response = await fetch('/api/skill-test/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        test_id: currentTestId,
        answers: userMcqAnswers
      })
    });

    const data = await response.json();
    if (data.status === 'success') {
      window.SessionStore.saveSkillTestResult(currentTestId, data);
      window.SessionStore.setSelectedCareer(currentTestId, data.title);

      window.showToast('Test evaluated! Loading report...', 'success');
      setTimeout(() => {
        window.location.href = `/skill-result?test_id=${currentTestId}`;
      }, 350);
    } else {
      throw new Error(data.message || 'Evaluation failed');
    }
  } catch (err) {
    console.error(err);
    window.showToast(`Submission Error: ${err.message}`, 'error');
  }
}

window.selectMcqAnswer = selectMcqAnswer;
window.nextMcq = nextMcq;
window.prevMcq = prevMcq;
window.jumpToQuestion = jumpToQuestion;
window.submitSkillTest = submitSkillTest;
