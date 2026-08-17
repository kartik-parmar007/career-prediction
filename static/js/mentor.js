/**
 * AI Career Mentor Chatbot Script (Clean White Theme)
 * Real-time conversation interface with session context awareness and mobile-optimized display.
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('mentor-chat-container')) {
    initMentorChat();
  }
});

function initMentorChat() {
  renderMentorContextSidebar();
  renderChatHistory();

  const form = document.getElementById('mentor-chat-form');
  const input = document.getElementById('mentor-chat-input');

  if (form && input) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      await sendMentorMessage(text);
    });
  }
}

function renderMentorContextSidebar() {
  const context = window.SessionStore.getAdvisorContext();

  const careerEl = document.getElementById('mentor-target-career');
  const compatEl = document.getElementById('mentor-compat-score');
  const readinessEl = document.getElementById('mentor-readiness-score');
  const weakEl = document.getElementById('mentor-weak-topics');

  if (careerEl) careerEl.innerText = context.selected_career_title || 'General IT Engineering';
  if (compatEl) compatEl.innerText = `${context.compatibility_pct}%`;
  if (readinessEl) readinessEl.innerText = `${context.readiness_pct}%`;

  if (weakEl) {
    if (context.weak_topics && context.weak_topics.length > 0) {
      weakEl.innerHTML = context.weak_topics.map(t => `<span class="px-2 py-0.5 rounded-md bg-amber-50 border border-amber-200 text-amber-800 text-[10px] sm:text-[11px] font-medium">${t}</span>`).join(' ');
    } else {
      weakEl.innerHTML = `<span class="text-xs text-emerald-600 font-medium">✓ Foundations Verified</span>`;
    }
  }
}

function renderChatHistory() {
  const messagesContainer = document.getElementById('mentor-messages-list');
  if (!messagesContainer) return;

  const history = window.SessionStore.getChatHistory();

  if (history.length === 0) {
    const context = window.SessionStore.getAdvisorContext();
    const career = context.selected_career_title || 'IT Software Engineer';

    messagesContainer.innerHTML = `
      <div class="chat-bubble-ai p-3.5 sm:p-5 max-w-[90%] sm:max-w-[85%] self-start animate-fade-in bg-white border border-slate-200 shadow-sm">
        <div class="flex items-center gap-2 mb-1.5 sm:mb-2">
          <div class="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-indigo-600 flex items-center justify-center text-white text-[10px] sm:text-xs">
            <i class="fa-solid fa-robot"></i>
          </div>
          <span class="text-xs font-bold text-indigo-700">AI Career Mentor</span>
        </div>
        <p class="text-xs sm:text-sm text-slate-800 leading-relaxed mb-2">
          Hello! I have reviewed your target career path (<strong>${career}</strong>), 
          compatibility match (<strong>${context.compatibility_pct}%</strong>), and technical score (<strong>${context.readiness_pct}%</strong>).
        </p>
        <p class="text-[11px] sm:text-xs text-slate-500 leading-relaxed">
          How can I assist your learning journey? Select a question or ask anything below!
        </p>
      </div>
    `;
    return;
  }

  let html = '';
  history.forEach(msg => {
    const isUser = msg.role === 'user';
    const formattedContent = formatChatMessage(msg.content);

    if (isUser) {
      html += `
        <div class="chat-bubble-user p-3 sm:p-4 max-w-[90%] sm:max-w-[85%] self-end animate-fade-in">
          <div class="text-xs sm:text-sm font-medium text-white whitespace-pre-wrap leading-relaxed">${escapeHtml(msg.content)}</div>
        </div>
      `;
    } else {
      html += `
        <div class="chat-bubble-ai p-3.5 sm:p-5 max-w-[90%] sm:max-w-[85%] self-start animate-fade-in bg-white border border-slate-200 shadow-sm">
          <div class="flex items-center gap-2 mb-1.5 sm:mb-2">
            <div class="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-indigo-600 flex items-center justify-center text-white text-[10px] sm:text-xs">
              <i class="fa-solid fa-robot"></i>
            </div>
            <span class="text-xs font-bold text-indigo-700">AI Career Mentor</span>
          </div>
          <div class="text-xs sm:text-sm text-slate-800 leading-relaxed space-y-1.5 sm:space-y-2">${formattedContent}</div>
        </div>
      `;
    }
  });

  messagesContainer.innerHTML = html;
  scrollChatToBottom();
}

async function sendMentorMessage(userText) {
  window.SessionStore.appendChatMessage('user', userText);
  renderChatHistory();

  showTypingIndicator();

  const history = window.SessionStore.getChatHistory();
  const context = window.SessionStore.getAdvisorContext();

  try {
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: history,
        session_context: context
      })
    });

    const data = await response.json();
    hideTypingIndicator();

    if (data.status === 'success' && data.message) {
      window.SessionStore.appendChatMessage('assistant', data.message.content);
      renderChatHistory();
    } else {
      throw new Error(data.message || 'Error communicating with AI mentor');
    }
  } catch (err) {
    console.error(err);
    hideTypingIndicator();
    window.SessionStore.appendChatMessage('assistant', `⚠️ Temporary connection issue: ${err.message}. Please try again.`);
    renderChatHistory();
  }
}

function sendPresetPrompt(promptText) {
  sendMentorMessage(promptText);
}

function showTypingIndicator() {
  const container = document.getElementById('mentor-messages-list');
  if (!container) return;

  let typingEl = document.getElementById('mentor-typing-indicator');
  if (!typingEl) {
    typingEl = document.createElement('div');
    typingEl.id = 'mentor-typing-indicator';
    typingEl.className = 'chat-bubble-ai p-2.5 sm:p-3 max-w-[100px] self-start flex items-center gap-1.5 bg-white border border-slate-200 shadow-sm';
    typingEl.innerHTML = `
      <span class="w-1.5 h-1.5 rounded-full bg-indigo-600 animate-bounce"></span>
      <span class="w-1.5 h-1.5 rounded-full bg-indigo-600 animate-bounce [animation-delay:0.2s]"></span>
      <span class="w-1.5 h-1.5 rounded-full bg-indigo-600 animate-bounce [animation-delay:0.4s]"></span>
    `;
    container.appendChild(typingEl);
    scrollChatToBottom();
  }
}

function hideTypingIndicator() {
  const typingEl = document.getElementById('mentor-typing-indicator');
  if (typingEl) typingEl.remove();
}

function clearChat() {
  if (confirm('Clear your conversation history?')) {
    window.SessionStore.clearChatHistory();
    renderChatHistory();
  }
}

function scrollChatToBottom() {
  const container = document.getElementById('mentor-messages-container');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function formatChatMessage(text) {
  if (!text) return '';
  let formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-900 font-bold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-indigo-700 font-medium">$1</em>')
    .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-indigo-700 font-mono text-[11px] sm:text-xs">$1</code>');

  const lines = formatted.split('\n');
  let result = [];
  let inList = false;

  for (let line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
      if (!inList) {
        result.push('<ul class="list-disc pl-4 space-y-1 my-1 marker:text-indigo-600 text-xs sm:text-sm text-slate-700">');
        inList = true;
      }
      result.push(`<li>${trimmed.substring(2)}</li>`);
    } else if (/^\d+\.\s/.test(trimmed)) {
      if (!inList) {
        result.push('<ol class="list-decimal pl-4 space-y-1 my-1 marker:text-indigo-600 text-xs sm:text-sm text-slate-700">');
        inList = true;
      }
      result.push(`<li>${trimmed.replace(/^\d+\.\s/, '')}</li>`);
    } else {
      if (inList) {
        result.push('</ul>');
        inList = false;
      }
      if (trimmed) {
        result.push(`<p class="leading-relaxed mb-1 text-slate-700">${trimmed}</p>`);
      }
    }
  }
  if (inList) result.push('</ul>');

  return result.join('');
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
}

window.sendPresetPrompt = sendPresetPrompt;
window.clearChat = clearChat;
