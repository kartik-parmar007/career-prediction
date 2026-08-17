/**
 * Storage Manager: Centralized localStorage session persistence.
 * Zero database / zero server-side user data persistence.
 */

const STORAGE_KEY = 'ai_career_advisor_session';

const defaultSession = {
  assessmentAnswers: null,
  careerResults: null,
  selectedCareerId: null,
  selectedCareerTitle: null,
  skillTestResults: {},
  activeRoadmap: null,
  chatHistory: [],
  lastUpdated: null
};

class SessionStore {
  static getSession() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { ...defaultSession };
      return { ...defaultSession, ...JSON.parse(raw) };
    } catch (e) {
      console.error('[Storage Error] Failed to read session:', e);
      return { ...defaultSession };
    }
  }

  static saveSession(updatedState) {
    try {
      const current = this.getSession();
      const next = { ...current, ...updatedState, lastUpdated: new Date().toISOString() };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      window.dispatchEvent(new CustomEvent('sessionUpdated', { detail: next }));
      return next;
    } catch (e) {
      console.error('[Storage Error] Failed to save session:', e);
    }
  }

  static saveAssessmentAnswers(answers) {
    return this.saveSession({ assessmentAnswers: answers });
  }

  static saveCareerResults(results) {
    const topMatch = results.top_recommendations && results.top_recommendations[0];
    const update = { careerResults: results };
    if (topMatch && !this.getSession().selectedCareerId) {
      update.selectedCareerId = topMatch.career_id;
      update.selectedCareerTitle = topMatch.title;
    }
    return this.saveSession(update);
  }

  static setSelectedCareer(careerId, careerTitle) {
    return this.saveSession({
      selectedCareerId: careerId,
      selectedCareerTitle: careerTitle
    });
  }

  static saveSkillTestResult(testId, testResult) {
    const session = this.getSession();
    const tests = { ...session.skillTestResults, [testId]: testResult };
    return this.saveSession({ skillTestResults: tests });
  }

  static getSkillTestResult(testId) {
    const session = this.getSession();
    return session.skillTestResults[testId] || null;
  }

  static getLatestSkillTestResult() {
    const session = this.getSession();
    const selectedId = session.selectedCareerId;
    if (selectedId && session.skillTestResults[selectedId]) {
      return session.skillTestResults[selectedId];
    }
    const testKeys = Object.keys(session.skillTestResults);
    if (testKeys.length > 0) {
      return session.skillTestResults[testKeys[testKeys.length - 1]];
    }
    return null;
  }

  static saveRoadmap(roadmap) {
    return this.saveSession({ activeRoadmap: roadmap });
  }

  static getChatHistory() {
    return this.getSession().chatHistory || [];
  }

  static appendChatMessage(role, content) {
    const history = this.getChatHistory();
    history.push({ role, content, timestamp: new Date().toISOString() });
    return this.saveSession({ chatHistory: history });
  }

  static clearChatHistory() {
    return this.saveSession({ chatHistory: [] });
  }

  static clearSession() {
    localStorage.removeItem(STORAGE_KEY);
    window.dispatchEvent(new CustomEvent('sessionUpdated', { detail: { ...defaultSession } }));
  }

  static getAdvisorContext() {
    const s = this.getSession();
    const latestTest = this.getLatestSkillTestResult();
    const topCareer = s.careerResults && s.careerResults.top_recommendations && s.careerResults.top_recommendations[0];

    return {
      selected_career_id: s.selectedCareerId || (topCareer ? topCareer.career_id : 'fullstack'),
      selected_career_title: s.selectedCareerTitle || (topCareer ? topCareer.title : 'Full Stack Developer'),
      compatibility_pct: topCareer ? topCareer.compatibility : 85,
      readiness_pct: latestTest ? latestTest.technical_readiness : (s.selectedCareerId ? 70 : 65),
      current_level: latestTest ? latestTest.current_level : 'Beginner+',
      weak_topics: latestTest ? latestTest.weak_areas : ['Core Architecture', 'State Management'],
      strong_topics: latestTest ? latestTest.strong_areas : ['Fundamentals', 'Syntax'],
      weekly_hours: s.assessmentAnswers && s.assessmentAnswers.learning_time_commitment ? s.assessmentAnswers.learning_time_commitment : '10 hours/week'
    };
  }
}

window.SessionStore = SessionStore;
