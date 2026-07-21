const state = {
  sessionId: window.localStorage.getItem("startframe_session_id"),
  session: null,
  sources: [],
  coverage: null,
  knowledgeMap: null,
  fullRoute: [],
  selectedSourceId: null,
  selectedSource: null,
  selectedChunkIndex: 0,
  deleteTarget: null,
  sessionDeleteTarget: null,
  sessionDeleteTrigger: null,
  sourceReturn: null,
  sourceReturnTrigger: null,
  pollTimer: null,
  focusTimer: null,
  saveTimers: {},
  drafts: {},
  focus: null,
  tutor: null,
  activity: null,
  feedback: null,
  evidence: null,
  agent: null,
  search: null,
  activityReturnTrigger: null,
  tutorReturnTrigger: null,
  conflict: null,
  runtimeMode: "demo",
  sessions: [],
};

const views = {
  home: document.querySelector("#home-view"),
  sources: document.querySelector("#source-view"),
  coverage: document.querySelector("#coverage-view"),
  path: document.querySelector("#path-view"),
  focus: document.querySelector("#focus-view"),
  tutor: document.querySelector("#tutor-view"),
  activity: document.querySelector("#activity-view"),
  feedback: document.querySelector("#feedback-view"),
  evidence: document.querySelector("#evidence-ready-view"),
  agent: document.querySelector("#agent-view"),
  search: document.querySelector("#search-view"),
  summary: document.querySelector("#summary-view"),
};

const runtimeStatus = document.querySelector("#runtime-status");
const startButtons = document.querySelectorAll("#start-session, #empty-start");
const libraryLink = document.querySelector("#library-link");
const openSettingsPanelButton = document.querySelector("#open-settings-panel");
const closeSettingsPanelButton = document.querySelector("#close-settings-panel");
const settingsDialog = document.querySelector("#settings-dialog");
const openHelpPanelButton = document.querySelector("#open-help-panel");
const closeHelpPanelButton = document.querySelector("#close-help-panel");
const helpDialog = document.querySelector("#help-dialog");
const sourceTitle = document.querySelector("#sources-title");
const backHomeButton = document.querySelector("#back-home");
const saveForLaterButton = document.querySelector("#save-for-later");
const recentEmpty = document.querySelector("#recent-empty");
const recentList = document.querySelector("#recent-list");
const recentMessage = document.querySelector("#recent-message");
const sessionSearch = document.querySelector("#session-search");
const sessionFilter = document.querySelector("#session-filter");
const recentEmptyTitle = document.querySelector("#recent-empty-title");
const recentEmptyCopy = document.querySelector("#recent-empty-copy");
const emptyStartButton = document.querySelector("#empty-start");
const exportJsonButton = document.querySelector("#export-json");
const exportMarkdownButton = document.querySelector("#export-markdown");
const openAiActivityButton = document.querySelector("#open-ai-activity");
const openDeleteWorkspaceButton = document.querySelector("#open-delete-workspace");
const dataControlMessage = document.querySelector("#data-control-message");
const preferenceLargeText = document.querySelector("#preference-large-text");
const preferenceReducedMotion = document.querySelector("#preference-reduced-motion");
const preferenceShowTimer = document.querySelector("#preference-show-timer");
const preferenceSearchSuggestions = document.querySelector("#preference-search-suggestions");
const uploadPanel = document.querySelector("#upload-panel");
const sourceInventory = document.querySelector("#source-inventory");
const learningReady = document.querySelector("#learning-ready");
const sourceCount = document.querySelector("#source-count");
const sourceEmpty = document.querySelector("#source-empty");
const sourceList = document.querySelector("#source-list");
const uploadMessage = document.querySelector("#upload-message");
const connectionBanner = document.querySelector("#connection-banner");
const chooseFilesButton = document.querySelector("#choose-files");
const fileInput = document.querySelector("#file-input");
const dropZone = document.querySelector("#drop-zone");
const dropZoneTitle = document.querySelector("#drop-zone-title");
const dropZoneCopy = document.querySelector("#drop-zone-copy");
const reviewCoverageButton = document.querySelector("#review-coverage");
const coverageNote = document.querySelector("#coverage-note");
const loadDemoButton = document.querySelector("#load-demo-materials");
const demoMaterialNote = document.querySelector("#demo-material-note");

const pasteDialog = document.querySelector("#paste-dialog");
const pasteForm = document.querySelector("#paste-form");
const openPasteButton = document.querySelector("#open-paste");
const cancelPasteButton = document.querySelector("#cancel-paste");
const pasteTitleInput = document.querySelector("#paste-title-input");
const pasteText = document.querySelector("#paste-text");
const pasteError = document.querySelector("#paste-error");
const submitPasteButton = document.querySelector("#submit-paste");
const deleteDialog = document.querySelector("#delete-dialog");
const deleteFilename = document.querySelector("#delete-filename");
const cancelDeleteButton = document.querySelector("#cancel-delete");
const confirmDeleteButton = document.querySelector("#confirm-delete");


const coverageTitle = document.querySelector("#coverage-title");
const coverageMessage = document.querySelector("#coverage-message");
const coveredList = document.querySelector("#covered-list");
const gapList = document.querySelector("#gap-list");
const coveredCount = document.querySelector("#covered-count");
const coverageSourceOriginHeading = document.querySelector("#coverage-source-origin-heading");
const uploadedPolicyText = document.querySelector("#uploaded-policy-text");
const aiPolicyText = document.querySelector("#ai-policy-text");
const gapCount = document.querySelector("#gap-count");
const coverageGenerationLabel = document.querySelector("#coverage-generation-label");
const regenerateCoverageButton = document.querySelector("#regenerate-coverage");
const generateMapButton = document.querySelector("#generate-map");
const backToSourcesFromCoverageButton = document.querySelector("#back-to-sources-from-coverage");

const pathTitle = document.querySelector("#path-title");
const pathMessage = document.querySelector("#path-message");
const mapCount = document.querySelector("#map-count");
const conceptMap = document.querySelector("#concept-map");
const pathConceptPreview = document.querySelector("#path-concept-preview");
const pathGenerationLabel = document.querySelector("#path-generation-label");
const confirmPathButton = document.querySelector("#confirm-path");
const backToCoverageButton = document.querySelector("#back-to-coverage");

const focusTitle = document.querySelector("#focus-title");
const focusBreadcrumb = document.querySelector("#focus-breadcrumb");
const focusRole = document.querySelector("#focus-role");
const focusDefinition = document.querySelector("#focus-definition");
const focusKeyPoints = document.querySelector("#focus-key-points");
const focusExample = document.querySelector("#focus-example");
const focusSources = document.querySelector("#focus-sources");
const focusRoute = document.querySelector("#focus-route");
const focusMapPreview = document.querySelector("#focus-map-preview");
const focusProgressCount = document.querySelector("#focus-progress-count");
const activeConceptCount = document.querySelector("#active-concept-count");
const focusNote = document.querySelector("#focus-note");
const focusNoteStatus = document.querySelector("#focus-note-status");
const focusSaveStatus = document.querySelector("#focus-save-status");
const saveFocusNoteButton = document.querySelector("#save-focus-note");
const openTutorButton = document.querySelector("#open-tutor");
const pauseSessionButton = document.querySelector("#pause-session");
const reviewFullMapButton = document.querySelector("#review-full-map");
const mobileSessionNav = document.querySelector(".mobile-session-nav");
const pauseDialog = document.querySelector("#pause-dialog");
const pauseLibraryButton = document.querySelector("#pause-library");
const resumeSessionButton = document.querySelector("#resume-session");
const conflictDialog = document.querySelector("#conflict-dialog");
const conflictLocal = document.querySelector("#conflict-local");
const conflictServer = document.querySelector("#conflict-server");
const keepLocalDraftButton = document.querySelector("#keep-local-draft");
const keepServerDraftButton = document.querySelector("#keep-server-draft");
const summaryRestartAction = document.querySelector("#summary-restart-action");
const summaryConcept = document.querySelector("#summary-concept");
const summaryNote = document.querySelector("#summary-note");
const summaryCompleted = document.querySelector("#summary-completed");
const summaryReview = document.querySelector("#summary-review");
const summaryStats = document.querySelector("#summary-stats");
const summaryLibraryButton = document.querySelector("#summary-library");
const summaryExportButton = document.querySelector("#summary-export");
const summaryResumeButton = document.querySelector("#summary-resume");

const sessionDeleteDialog = document.querySelector("#session-delete-dialog");
const sessionDeleteName = document.querySelector("#session-delete-name");
const sessionDeleteMessage = document.querySelector("#session-delete-message");
const cancelSessionDeleteButton = document.querySelector("#cancel-session-delete");
const confirmSessionDeleteButton = document.querySelector("#confirm-session-delete");
const workspaceDeleteDialog = document.querySelector("#workspace-delete-dialog");
const workspaceDeleteMessage = document.querySelector("#workspace-delete-message");
const cancelWorkspaceDeleteButton = document.querySelector("#cancel-workspace-delete");
const confirmWorkspaceDeleteButton = document.querySelector("#confirm-workspace-delete");
const aiActivityDialog = document.querySelector("#ai-activity-dialog");
const aiActivityList = document.querySelector("#ai-activity-list");
const aiActivityMessage = document.querySelector("#ai-activity-message");
const closeAiActivityButton = document.querySelector("#close-ai-activity");

const tutorTitle = document.querySelector("#tutor-title");
const tutorBreadcrumb = document.querySelector("#tutor-breadcrumb");
const tutorSaveStatus = document.querySelector("#tutor-save-status");
const tutorPauseButton = document.querySelector("#tutor-pause");
const closeTutorButton = document.querySelector("#close-tutor");
const tutorEmpty = document.querySelector("#tutor-empty");
const tutorLog = document.querySelector("#tutor-log");
const tutorActions = document.querySelector("#tutor-actions");
const tutorForm = document.querySelector("#tutor-form");
const tutorInput = document.querySelector("#tutor-input");
const tutorDraftStatus = document.querySelector("#tutor-draft-status");
const tutorMessageStatus = document.querySelector("#tutor-message-status");
const sendTutorMessageButton = document.querySelector("#send-tutor-message");
const tutorConcept = document.querySelector("#tutor-concept");
const tutorRole = document.querySelector("#tutor-role");
const tutorPrevious = document.querySelector("#tutor-previous");
const tutorGuidanceLevel = document.querySelector("#tutor-guidance-level");
const tutorContextSources = document.querySelector("#tutor-context-sources");
const guidanceLadder = document.querySelector("#guidance-ladder");
const tutorModeLabel = document.querySelector("#tutor-mode-label");

const startQuizButton = document.querySelector("#start-quiz");
const startRecallButton = document.querySelector("#start-recall");
const activityTitle = document.querySelector("#activity-title");
const activityTypeLabel = document.querySelector("#activity-type-label");
const activityBreadcrumb = document.querySelector("#activity-breadcrumb");
const activityKindChip = document.querySelector("#activity-kind-chip");
const activityOriginLabel = document.querySelector("#activity-origin-label");
const activityPrompt = document.querySelector("#activity-prompt");
const remedialCompletion = document.querySelector("#remedial-completion");
const activityForm = document.querySelector("#activity-form");
const quizOptions = document.querySelector("#quiz-options");
const recallAnswerWrap = document.querySelector("#recall-answer-wrap");
const recallAnswer = document.querySelector("#recall-answer");
const activityAnswerLabel = document.querySelector("#activity-answer-label");
const activityMessage = document.querySelector("#activity-message");
const activitySaveStatus = document.querySelector("#activity-save-status");
const activityDraftStatus = document.querySelector("#activity-draft-status");
const submitActivityButton = document.querySelector("#submit-activity");
const closeActivityButton = document.querySelector("#close-activity");
const activityReturnButton = document.querySelector("#activity-return");
const activityPauseButton = document.querySelector("#activity-pause");
const hintList = document.querySelector("#hint-list");
const revealHintButton = document.querySelector("#reveal-hint");
const mobileActivityConcept = document.querySelector("#mobile-activity-concept");
const mobileActivityHints = document.querySelector("#mobile-activity-hints");
const mobileActivityPause = document.querySelector("#mobile-activity-pause");

const feedbackTitle = document.querySelector("#feedback-title");
const feedbackBreadcrumb = document.querySelector("#feedback-breadcrumb");
const feedbackSaveStatus = document.querySelector("#feedback-save-status");
const feedbackPauseButton = document.querySelector("#feedback-pause");
const feedbackOriginLabel = document.querySelector("#feedback-origin-label");
const feedbackResultMark = document.querySelector("#feedback-result-mark");
const feedbackResultLabel = document.querySelector("#feedback-result-label");
const feedbackSectionsTitle = document.querySelector("#feedback-sections-title");
const quizAnswerReview = document.querySelector("#quiz-answer-review");
const feedbackExplanation = document.querySelector("#feedback-explanation");
const feedbackCorrection = document.querySelector("#feedback-correction");
const feedbackEncouragement = document.querySelector("#feedback-encouragement");
const completeFeedbackButton = document.querySelector("#complete-feedback");
const feedbackMessage = document.querySelector("#feedback-message");
const mobileFeedbackConcept = document.querySelector("#mobile-feedback-concept");
const mobileFeedbackPause = document.querySelector("#mobile-feedback-pause");
const evidenceReadyTitle = document.querySelector("#evidence-ready-title");
const evidenceReadyMessage = document.querySelector("#evidence-ready-message");
const runAgentButton = document.querySelector("#run-agent");

const agentTitle = document.querySelector("#agent-title");
const agentSaveStatus = document.querySelector("#agent-save-status");
const agentPauseButton = document.querySelector("#agent-pause");
const agentEstimate = document.querySelector("#agent-estimate");
const agentActionTitle = document.querySelector("#agent-action-title");
const agentReason = document.querySelector("#agent-reason");
const acceptAgentButton = document.querySelector("#accept-agent");
const agentMessage = document.querySelector("#agent-message");

const searchTitle = document.querySelector("#search-title");
const searchSaveStatus = document.querySelector("#search-save-status");
const searchPauseButton = document.querySelector("#search-pause");
const searchConfirmationPanel = document.querySelector("#search-confirmation-panel");
const searchConfirmationTitle = document.querySelector("#search-confirmation-title");
const searchGates = document.querySelector("#search-gates");
const searchGapTitle = document.querySelector("#search-gap-title");
const searchGapWhy = document.querySelector("#search-gap-why");
const searchQueryScope = document.querySelector("#search-query-scope");
const searchRequestReason = document.querySelector("#search-request-reason");
const searchMessage = document.querySelector("#search-message");
const declineSearchButton = document.querySelector("#decline-search");
const confirmSearchButton = document.querySelector("#confirm-search");
const searchResultsPanel = document.querySelector("#search-results-panel");
const searchResultsTitle = document.querySelector("#search-results-title");
const searchResultCount = document.querySelector("#search-result-count");
const searchResultList = document.querySelector("#search-result-list");
const ignoreSearchResultsButton = document.querySelector("#ignore-search-results");

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { Accept: "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (response.status === 204) return null;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.user_message || "The request could not be completed.");
    error.body = body;
    throw error;
  }
  return body;
}

function setButtonBusy(button, busy, busyText, readyText) {
  button.disabled = busy;
  button.textContent = busy ? busyText : readyText;
  button.setAttribute("aria-busy", String(busy));
}

function setMessage(target, message, kind = "info") {
  target.textContent = message;
  target.dataset.kind = kind;
  target.hidden = !message;
}

function setUploadMessage(message, kind = "info") {
  setMessage(uploadMessage, message, kind);
}

function showView(name, hash, heading) {
  Object.entries(views).forEach(([viewName, view]) => {
    view.hidden = viewName !== name;
  });
  if (hash) window.location.hash = hash;
  window.scrollTo({ top: 0, behavior: "auto" });
  if (heading) heading.focus({ preventScroll: true });
}

async function checkRuntime() {
  try {
    const health = await api("/api/health");
    state.runtimeMode = health.mode;
    const isDemo = health.mode === "demo";
    runtimeStatus.textContent = "Service ready.";
    loadDemoButton.hidden = !isDemo;
    demoMaterialNote.hidden = !isDemo;
  } catch (error) {
    runtimeStatus.textContent = "Service unavailable. Refresh to retry; page content remains available.";
  }
}

async function getCurrentSession() {
  if (!state.sessionId) return null;
  const body = await api(`/api/sessions/${state.sessionId}`);
  state.session = body.session;
  return state.session;
}

async function beginSession() {
  const buttons = [...startButtons];
  buttons.forEach((button) => setButtonBusy(button, true, "Creating session…", button.textContent));
  try {
    const body = await api("/api/sessions", { method: "POST" });
    state.sessionId = body.session.id;
    state.session = body.session;
    window.localStorage.setItem("startframe_session_id", state.sessionId);
    await showSources();
  } catch (error) {
    runtimeStatus.textContent = `${error.message} Nothing was changed. Try again.`;
  } finally {
    buttons.forEach((button) => {
      const label = button.id === "empty-start" ? "Start your first session" : "Upload material and start learning";
      setButtonBusy(button, false, "", label);
    });
  }
}

async function loadSessions() {
  try {
    const body = await api("/api/sessions");
    state.sessions = body.sessions;
    renderSessions();
  } catch (error) {
    recentEmpty.hidden = false;
    recentList.hidden = true;
  }
}

function renderSessions() {
  const query = sessionSearch.value.trim().toLowerCase();
  const filter = sessionFilter.value;
  const sessions = state.sessions.filter((session) => {
    const matchesQuery = !query || `${session.name} ${session.goal || ""}`.toLowerCase().includes(query);
    const matchesFilter = filter === "all"
      || (filter === "paused" && session.is_paused)
      || (filter === "completed" && session.state === "session_summary")
      || (filter === "active" && !session.is_paused && session.state !== "session_summary");
    return matchesQuery && matchesFilter;
  });
  recentList.replaceChildren();
  recentEmpty.hidden = sessions.length > 0;
  recentList.hidden = sessions.length === 0;
  const total = state.sessions.length;
  document.querySelector("#recent-sessions .status-chip").textContent = sessions.length === total
    ? `${total} ${total === 1 ? "session" : "sessions"}`
    : `${sessions.length} of ${total}`;
  const hasSessions = total > 0;
  recentEmptyTitle.textContent = hasSessions ? "No sessions match these filters" : "No learning sessions yet";
  recentEmptyCopy.textContent = hasSessions
    ? "Change the search text or status filter to see other saved sessions."
    : "After your first upload, resumable concepts, drafts, and next actions will appear here.";
  emptyStartButton.hidden = hasSessions;
  sessions.forEach((session) => {
    const item = element("article", "session-item");
    const details = element("div");
    details.append(element("h3", "", session.name));
    const ready = Number(session.ready_source_count || 0);
    const total = Number(session.source_count || 0);
    details.append(element("p", "", `${ready}/${total} sources ready · ${session.state.replaceAll("_", " ")}`));
    const actions = element("div", "session-actions");
    const resume = element("button", "button button-secondary", resumeLabel(session));
    resume.type = "button";
    resume.addEventListener("click", () => resumeSession(session.id));
    const copyButton = element("button", "button button-quiet", "Copy");
    copyButton.type = "button";
    copyButton.setAttribute("aria-label", `Copy ${session.name} as a new session`);
    copyButton.addEventListener("click", () => copyLearningSession(session, copyButton));
    const deleteButton = element("button", "button button-quiet", "Delete");
    deleteButton.type = "button";
    deleteButton.setAttribute("aria-label", `Delete ${session.name}`);
    deleteButton.addEventListener("click", () => openSessionDelete(session, deleteButton));
    actions.append(resume, copyButton, deleteButton);
    item.append(details, actions);
    recentList.append(item);
  });
}

async function copyLearningSession(session, button) {
  setMessage(recentMessage, `Copying ${session.name} with its source files…`);
  setButtonBusy(button, true, "Copying…", "Copy");
  try {
    const body = await api(`/api/sessions/${session.id}/copy`, { method: "POST" });
    await loadSessions();
    setMessage(recentMessage, `${body.session.name} is ready. It shares immutable file storage but starts with fresh learning progress.`, "success");
  } catch (error) {
    setMessage(recentMessage, `${error.message} The original session is unchanged.`, "error");
    setButtonBusy(button, false, "", "Copy");
  }
}

function openSessionDelete(session, trigger) {
  state.sessionDeleteTarget = session;
  state.sessionDeleteTrigger = trigger;
  sessionDeleteName.textContent = session.name;
  setMessage(sessionDeleteMessage, "");
  setButtonBusy(confirmSessionDeleteButton, false, "", "Delete session permanently");
  sessionDeleteDialog.showModal();
}

function closeSessionDelete() {
  sessionDeleteDialog.close();
  const trigger = state.sessionDeleteTrigger;
  state.sessionDeleteTarget = null;
  state.sessionDeleteTrigger = null;
  if (trigger?.isConnected) trigger.focus({ preventScroll: true });
}

async function confirmSessionDelete() {
  const session = state.sessionDeleteTarget;
  if (!session) return;
  setButtonBusy(confirmSessionDeleteButton, true, "Deleting permanently…", "Delete session permanently");
  cancelSessionDeleteButton.disabled = true;
  try {
    const body = await api(`/api/sessions/${session.id}`, { method: "DELETE" });
    if (state.sessionId === session.id) {
      state.sessionId = null;
      state.session = null;
      window.localStorage.removeItem("startframe_session_id");
    }
    sessionDeleteDialog.close();
    state.sessionDeleteTarget = null;
    state.sessionDeleteTrigger = null;
    await loadSessions();
    setMessage(
      recentMessage,
      body.file_cleanup_complete
        ? body.removed_unreferenced_blobs
          ? `${body.deleted_session_name} was permanently deleted with ${body.removed_unreferenced_blobs} unshared source ${body.removed_unreferenced_blobs === 1 ? "file" : "files"}.`
          : `${body.deleted_session_name} was permanently deleted. Source files still used by another session were preserved.`
        : `${body.deleted_session_name} was deleted, but one stored file could not be cleaned up. Contact the deployment owner.`,
      body.file_cleanup_complete ? "success" : "error",
    );
  } catch (error) {
    setMessage(sessionDeleteMessage, `${error.message} The session and files remain available.`, "error");
    setButtonBusy(confirmSessionDeleteButton, false, "", "Delete session permanently");
  } finally {
    cancelSessionDeleteButton.disabled = false;
  }
}

function resumeLabel(session) {
  if (session.is_paused) return "Resume paused session";
  if (session.state === "session_summary") return "View session summary";
  if (session.state === "search_confirmation") return "Review search confirmation";
  if (session.state === "search_running") return "View search progress";
  if (session.state === "search_results") return "Review external sources";
  if (session.state === "agent_decision") return "Continue learning";
  if (["practicing", "remedial_practice"].includes(session.state)) return "Resume current practice";
  if (session.state === "feedback_shown") return "Resume saved feedback";
  if (session.state === "evidence_ready") return "Continue learning";
  if (session.state === "learning_concept") return "Resume current concept";
  if (session.state === "start_action") return "Start learning";
  if (session.state === "path_drafting") return "Review learning path";
  if (session.setup_completed) return "Continue with this material";
  return "Continue session";
}

async function resumeSession(sessionId) {
  state.sessionId = sessionId;
  window.localStorage.setItem("startframe_session_id", sessionId);
  try {
    const session = await getCurrentSession();
    if (["practicing", "remedial_practice"].includes(session.state)) {
      await showActivity();
      if (session.is_paused) pauseDialog.showModal();
    } else if (session.state === "feedback_shown") {
      await showFeedback();
      if (session.is_paused) pauseDialog.showModal();
    } else if (session.state === "evidence_ready") {
      await showEvidenceReady();
      if (session.is_paused) pauseDialog.showModal();
    } else if (session.state === "agent_decision") {
      await showAgentDecision();
      if (session.is_paused) pauseDialog.showModal();
    } else if (["search_confirmation", "search_running", "search_results"].includes(session.state)) {
      await showControlledSearch();
      if (session.is_paused) pauseDialog.showModal();
    } else if (session.state === "session_summary") {
      const summary = await api(`/api/sessions/${sessionId}/summary`);
      showFinishedSummary(summary.summary);
    } else if (session.state === "learning_concept") {
      if (session.tutor_open) await showTutor();
      else await showFocus();
      if (session.is_paused) pauseDialog.showModal();
    } else if (session.state === "start_action") {
      await startFirstConcept();
    } else if (session.state === "path_drafting") {
      try {
        await showPath();
      } catch (error) {
        await showCoverage();
      }
    } else if (session.setup_completed) {
      await showSources();
    } else {
      await showSources();
    }
  } catch (error) {
    state.sessionId = null;
    state.session = null;
    window.localStorage.removeItem("startframe_session_id");
    await showHome();
  }
}

async function showSources(returnTo = null) {
  if (!state.sessionId) {
    await beginSession();
    return;
  }
  state.sourceReturn = returnTo;
  backHomeButton.textContent = returnTo === "coverage"
    ? "← Back to coverage"
    : returnTo === "path"
      ? "← Back to learning map"
      : returnTo === "focus"
        ? "← Back to current concept"
        : returnTo === "tutor"
          ? "← Back to Tutor"
        : returnTo === "activity"
          ? "← Back to practice"
        : returnTo === "feedback"
          ? "← Back to feedback"
      : "← Back to library";
  showView("sources", `sources/${state.sessionId}`, sourceTitle);
  await Promise.all([loadSources(), getCurrentSession()]);
}

async function showHome(event) {
  if (event) event.preventDefault();
  window.clearTimeout(state.pollTimer);
  window.clearInterval(state.focusTimer);
  showView("home", "library", document.querySelector("#hero-title"));
  await loadSessions();
}

function openSettingsPanel() {
  setMessage(dataControlMessage, "");
  settingsDialog.showModal();
}

function closeSettingsPanel() {
  settingsDialog.close();
  openSettingsPanelButton.focus({ preventScroll: true });
}

function openHelpPanel() {
  helpDialog.showModal();
}

function closeHelpPanel() {
  helpDialog.close();
  openHelpPanelButton.focus({ preventScroll: true });
}

function savedPreference(name) {
  return window.localStorage.getItem(`startframe_preference_${name}`) === "true";
}

function loadPreferences() {
  preferenceLargeText.checked = savedPreference("large_text");
  preferenceReducedMotion.checked = savedPreference("reduced_motion");
  preferenceShowTimer.checked = savedPreference("show_timer");
  preferenceSearchSuggestions.checked = savedPreference("search_suggestions");
  document.documentElement.classList.toggle("large-interface-text", preferenceLargeText.checked);
  document.documentElement.classList.toggle("reduce-interface-motion", preferenceReducedMotion.checked);
}

function savePreferences() {
  const values = {
    large_text: preferenceLargeText.checked,
    reduced_motion: preferenceReducedMotion.checked,
    show_timer: preferenceShowTimer.checked,
    search_suggestions: preferenceSearchSuggestions.checked,
  };
  Object.entries(values).forEach(([name, value]) => {
    window.localStorage.setItem(`startframe_preference_${name}`, String(value));
  });
  loadPreferences();
  setMessage(dataControlMessage, "Preferences were saved on this device.", "success");
}

function downloadWorkspaceExport(format) {
  const label = format === "markdown" ? "Markdown summary" : "JSON record";
  setMessage(dataControlMessage, `Preparing the ${label}. Your saved data will not be changed.`);
  const link = document.createElement("a");
  link.href = `/api/export?format=${format}`;
  link.download = format === "markdown" ? "startframe-learning-record.md" : "startframe-learning-record.json";
  document.body.append(link);
  link.click();
  link.remove();
  setMessage(dataControlMessage, `${label} download started.`, "success");
}

async function openAiActivity() {
  aiActivityList.replaceChildren(loadingCard("Loading the workspace AI audit record…"));
  setMessage(aiActivityMessage, "");
  aiActivityDialog.showModal();
  try {
    const body = await api("/api/ai-activity");
    aiActivityList.replaceChildren();
    if (!body.activities.length) {
      aiActivityList.append(emptyCard("No AI operation has run in this workspace yet."));
      return;
    }
    body.activities.forEach((activity) => {
      const item = element("article", "ai-activity-item");
      item.append(
        element("strong", "", activity.operation.replaceAll("_", " ")),
        element("span", "status-chip", activity.status),
        element(
          "p",
          "micro-copy",
          `${activity.session_name} · ${formatAccessedAt(activity.created_at)}`,
        ),
      );
      if (activity.error_code) item.append(element("p", "field-error", `Recoverable error: ${activity.error_code}`));
      aiActivityList.append(item);
    });
  } catch (error) {
    aiActivityList.replaceChildren();
    setMessage(aiActivityMessage, `${error.message} No learning data was changed.`, "error");
  }
}

function closeAiActivity() {
  aiActivityDialog.close();
  if (!settingsDialog.open) settingsDialog.showModal();
  openAiActivityButton.focus({ preventScroll: true });
}

function openWorkspaceDelete() {
  setMessage(workspaceDeleteMessage, "");
  setButtonBusy(confirmWorkspaceDeleteButton, false, "", "Delete everything permanently");
  workspaceDeleteDialog.showModal();
}

function closeWorkspaceDelete() {
  workspaceDeleteDialog.close();
  if (!settingsDialog.open) settingsDialog.showModal();
  openDeleteWorkspaceButton.focus({ preventScroll: true });
}

async function confirmWorkspaceDelete() {
  setButtonBusy(confirmWorkspaceDeleteButton, true, "Deleting everything…", "Delete everything permanently");
  cancelWorkspaceDeleteButton.disabled = true;
  try {
    const body = await api("/api/user-data", { method: "DELETE" });
    Object.keys(window.localStorage)
      .filter((key) => key.startsWith("startframe_"))
      .forEach((key) => window.localStorage.removeItem(key));
    loadPreferences();
    window.clearTimeout(state.pollTimer);
    window.clearInterval(state.focusTimer);
    state.sessionId = null;
    state.session = null;
    state.sources = [];
    state.drafts = {};
    state.focus = null;
    state.tutor = null;
    state.activity = null;
    state.feedback = null;
    state.evidence = null;
    state.agent = null;
    state.search = null;
    workspaceDeleteDialog.close();
    await showHome();
    setMessage(
      dataControlMessage,
      body.file_cleanup_complete
        ? "All workspace learning data and uploaded files were permanently deleted."
        : "All database records were deleted, but one stored file needs deployment-owner cleanup.",
      body.file_cleanup_complete ? "success" : "error",
    );
    settingsDialog.showModal();
  } catch (error) {
    setMessage(workspaceDeleteMessage, `${error.message} Your workspace data remains available.`, "error");
    setButtonBusy(confirmWorkspaceDeleteButton, false, "", "Delete everything permanently");
  } finally {
    cancelWorkspaceDeleteButton.disabled = false;
  }
}

function sourceStatus(source) {
  const labels = {
    pending: "Waiting to parse",
    processing: "Parsing",
    success: "Ready",
    partial_success: "Ready with a warning",
    error: "Needs attention",
    cancelled: "Cancelled",
  };
  return labels[source.parse_status] || source.parse_status;
}

function sourceOriginLabel(origin) {
  if (origin === "ai_supplement") return "AI supplemental explanation";
  if (origin === "external") return "External supplement";
  return "Uploaded material";
}

function sourceOriginClass(origin) {
  if (origin === "ai_supplement") return "origin-badge origin-ai";
  if (origin === "external") return "origin-badge origin-external";
  return "origin-badge";
}

function sourceMetadata(source) {
  const size = source.byte_size >= 1024 * 1024
    ? `${(source.byte_size / (1024 * 1024)).toFixed(1)} MB`
    : `${Math.max(1, Math.round(source.byte_size / 1024))} KB`;
  const locationCount = source.media_kind === "pdf" && source.page_count
    ? `${source.page_count} ${source.page_count === 1 ? "page" : "pages"}`
    : source.line_count
      ? `${source.line_count} lines`
      : "Location pending";
  return `${sourceOriginLabel(source.source_origin)} · ${sourceStatus(source)} · ${locationCount} · ${size}`;
}

async function loadSources() {
  if (!state.sessionId) return;
  try {
    const body = await api(`/api/sessions/${state.sessionId}/sources`);
    state.sources = body.sources;
    renderSources();
    const processing = state.sources.some((source) => ["pending", "processing"].includes(source.parse_status));
    window.clearTimeout(state.pollTimer);
    if (processing) state.pollTimer = window.setTimeout(loadSources, 1200);
  } catch (error) {
    if (error.body?.error_code === "session_not_found") {
      state.sessionId = null;
      state.session = null;
      window.localStorage.removeItem("startframe_session_id");
      await showHome();
      return;
    }
    setUploadMessage(`${error.message} Your current page is unchanged.`, "error");
  }
}

function renderSources() {
  sourceList.replaceChildren();
  const hasSources = state.sources.length > 0;
  sourceInventory.hidden = !hasSources;
  sourceEmpty.hidden = hasSources;
  uploadPanel.classList.toggle("has-sources", hasSources);
  dropZoneTitle.textContent = hasSources ? "Add more material" : "Drop files here";
  dropZoneCopy.textContent = hasSources ? "Drop another file here or choose from this device" : "or choose files from this device";
  sourceCount.textContent = `${state.sources.length} ${state.sources.length === 1 ? "source" : "sources"}`;
  const readySources = state.sources.filter((source) => ["success", "partial_success"].includes(source.parse_status));
  reviewCoverageButton.disabled = readySources.length === 0;
  learningReady.hidden = readySources.length === 0;
  coverageNote.textContent = readySources.length
    ? `${readySources.length} readable ${readySources.length === 1 ? "source is" : "sources are"} ready. StartFrame will identify the core concepts, organize the knowledge framework, and open the first explanation.`
    : "StartFrame will identify the core concepts, organize the knowledge framework, and open the first explanation.";

  state.sources.forEach((source) => {
    const item = element("li", "source-item");
    item.dataset.state = source.parse_status;
    const select = element("div", "source-select");
    const marker = ["success", "partial_success"].includes(source.parse_status) ? "✓ " : source.parse_status === "error" ? "! " : "… ";
    select.append(element("span", "source-name", `${marker}${source.filename}`));
    select.append(element("span", "source-meta", sourceMetadata(source)));
    if (source.error_message) select.append(element("span", "source-error", source.error_message));

    const actions = element("div", "source-actions");
    if (["error", "cancelled"].includes(source.parse_status)) {
      const retry = element("button", "small-button", "Retry");
      retry.type = "button";
      retry.addEventListener("click", () => retrySource(source.id, retry));
      actions.append(retry);
    }
    const remove = element("button", "small-button", "Remove");
    remove.type = "button";
    remove.addEventListener("click", () => openDeleteDialog(source));
    actions.append(remove);
    item.append(select, actions);
    sourceList.append(item);
  });
}

function revealReadyMaterial() {
  if (sourceInventory.hidden) return;
  sourceInventory.scrollIntoView({ behavior: "smooth", block: "start" });
  const heading = sourceInventory.querySelector("h2");
  if (heading) {
    heading.setAttribute("tabindex", "-1");
    heading.focus({ preventScroll: true });
  }
}

async function uploadFiles(fileList) {
  const files = [...fileList];
  if (!files.length) return;
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  setButtonBusy(chooseFilesButton, true, `Uploading ${files.length}…`, "Choose files");
  setUploadMessage(`Uploading and parsing ${files.length} ${files.length === 1 ? "file" : "files"}…`);
  try {
    const body = await api(`/api/sessions/${state.sessionId}/sources`, { method: "POST", body: formData });
    if (body.rejected.length) {
      const rejected = body.rejected.map((item) => `${item.filename}: ${item.user_message}`).join(" ");
      setUploadMessage(`${body.accepted.length} saved. ${body.rejected.length} could not be added. ${rejected}`, "error");
    } else {
      setUploadMessage(`${body.accepted.length} ${body.accepted.length === 1 ? "source" : "sources"} saved and parsed.`, "success");
    }
    await loadSources();
    if (state.sources.some((source) => ["success", "partial_success"].includes(source.parse_status))) revealReadyMaterial();
  } catch (error) {
    const rejected = error.body?.rejected;
    if (Array.isArray(rejected) && rejected.length) {
      const details = rejected.map((item) => `${item.filename}: ${item.user_message}`).join(" ");
      setUploadMessage(`No files were added. ${details} Existing sources are still saved.`, "error");
    } else {
      setUploadMessage(`${error.message} Existing sources are still saved.`, "error");
    }
  } finally {
    fileInput.value = "";
    setButtonBusy(chooseFilesButton, false, "", "Choose files");
  }
}

async function loadSampleMaterials() {
  const idleLabel = "Try sample material";
  setButtonBusy(loadDemoButton, true, "Loading sample material…", idleLabel);
  try {
    const body = await api(`/api/sessions/${state.sessionId}/demo-materials?scenario=standard`, { method: "POST" });
    setUploadMessage(
      body.created_count
        ? "Two sample learning materials were added to this session."
        : "The sample materials are already in this session.",
      "success",
    );
    await loadSources();
    if (state.sources.some((source) => ["success", "partial_success"].includes(source.parse_status))) revealReadyMaterial();
  } catch (error) {
    setUploadMessage(`${error.message} Existing sources are unchanged.`, "error");
  } finally {
    setButtonBusy(loadDemoButton, false, "", idleLabel);
  }
}

async function leaveSourceView() {
  const returnTo = state.sourceReturn;
  const trigger = state.sourceReturnTrigger;
  state.sourceReturn = null;
  state.sourceReturnTrigger = null;
  if (returnTo === "coverage") showView("coverage", `coverage/${state.sessionId}`, coverageTitle);
  else if (returnTo === "path") showView("path", `path/${state.sessionId}`, pathTitle);
  else if (returnTo === "focus") showView("focus", `focus/${state.sessionId}`, focusTitle);
  else if (returnTo === "tutor") showView("tutor", `tutor/${state.sessionId}`, tutorTitle);
  else if (returnTo === "activity") showView("activity", `activity/${state.activity?.activity?.id || ""}`, activityTitle);
  else if (returnTo === "feedback") showView("feedback", `feedback/${state.feedback?.feedback?.id || ""}`, feedbackTitle);
  else await showHome();
  if (trigger?.isConnected) trigger.focus({ preventScroll: true });
}

async function retrySource(sourceId, button) {
  setButtonBusy(button, true, "Retrying…", "Retry");
  try {
    await api(`/api/sources/${sourceId}/retry`, { method: "POST" });
    setUploadMessage("Retry complete. Review the updated source status.", "success");
    await loadSources();
  } catch (error) {
    setUploadMessage(`${error.message} The original upload remains saved.`, "error");
  } finally {
    setButtonBusy(button, false, "", "Retry");
  }
}

function openDeleteDialog(source) {
  state.deleteTarget = source;
  deleteFilename.textContent = source.filename;
  deleteDialog.showModal();
}

async function deleteSelectedSource() {
  if (!state.deleteTarget) return;
  setButtonBusy(confirmDeleteButton, true, "Deleting…", "Delete source");
  try {
    await api(`/api/sources/${state.deleteTarget.id}`, { method: "DELETE" });
    deleteDialog.close();
    setUploadMessage(`${state.deleteTarget.filename} was deleted from this session.`, "success");
    await loadSources();
  } catch (error) {
    deleteDialog.close();
    setUploadMessage(`${error.message} The source is still saved.`, "error");
  } finally {
    state.deleteTarget = null;
    setButtonBusy(confirmDeleteButton, false, "", "Delete source");
  }
}

async function submitPastedSource(event) {
  event.preventDefault();
  pasteError.hidden = true;
  if (!pasteForm.reportValidity()) return;
  setButtonBusy(submitPasteButton, true, "Adding text…", "Add pasted text");
  try {
    const body = await api(`/api/sessions/${state.sessionId}/pasted-sources`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: pasteTitleInput.value.trim(), text: pasteText.value }),
    });
    pasteDialog.close();
    pasteForm.reset();
    setUploadMessage("Pasted text was saved and parsed with paragraph locations.", "success");
    await loadSources();
    revealReadyMaterial();
  } catch (error) {
    pasteError.textContent = `${error.message} Your pasted text remains in this form.`;
    pasteError.hidden = false;
    pasteError.focus();
  } finally {
    setButtonBusy(submitPasteButton, false, "", "Add pasted text");
  }
}

async function prepareLearningPath() {
  window.clearTimeout(state.pollTimer);
  let readyLabel = "Build my learning path";
  let progressStage = "Reading representative sections across your material.";
  const startedAt = Date.now();
  const progressTimer = window.setInterval(() => {
    const elapsed = Math.max(1, Math.round((Date.now() - startedAt) / 1000));
    coverageNote.textContent = `${progressStage} ${elapsed} seconds elapsed. Large PDFs usually take 20–60 seconds.`;
  }, 1000);
  setButtonBusy(reviewCoverageButton, true, "Analyzing source coverage…", readyLabel);
  setUploadMessage("Reading sections across the full material. Your upload is already saved.");
  try {
    const session = await getCurrentSession();

    let path = null;
    try {
      path = await api(`/api/sessions/${state.sessionId}/path`);
    } catch (error) {
      if (error.body?.error_code !== "map_not_generated") throw error;
    }

    if (!path) {
      let coverage = null;
      try {
        coverage = await api(`/api/sessions/${state.sessionId}/coverage`);
      } catch (error) {
        if (error.body?.error_code !== "coverage_not_generated") throw error;
      }

      if (!coverage) {
        const result = await api(`/api/sessions/${state.sessionId}/learning-path`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            version: session.version,
            show_timer: savedPreference("show_timer"),
            search_permission: savedPreference("search_suggestions"),
            stage: "coverage",
          }),
        });
        coverage = result.coverage;
      }
      state.coverage = coverage;
      progressStage = "Source coverage is ready. Organizing the concept route.";
      setButtonBusy(reviewCoverageButton, true, "Building your learning path…", readyLabel);
      setUploadMessage("Source coverage is ready. Building the knowledge framework and first learning action…", "success");
      path = await api(`/api/sessions/${state.sessionId}/path`, { method: "POST" });
    }

    state.knowledgeMap = path;
    state.fullRoute = path.knowledge_map.concepts.map((concept) => concept.concept_key);
    showView("path", `path/${state.sessionId}`, pathTitle);
    renderPath(path);
    confirmPathButton.disabled = false;
    setMessage(pathMessage, "Your knowledge framework is ready. Start with the first explanation when you are ready.", "success");
  } catch (error) {
    readyLabel = "Retry learning path";
    setUploadMessage(error.message, "error");
    coverageNote.textContent = `${error.body?.saved_state || "Your material is still saved."} Retry continues from the last completed stage.`;
  } finally {
    window.clearInterval(progressTimer);
    setButtonBusy(reviewCoverageButton, false, "", readyLabel);
  }
}

async function createCoverage() {
  showView("coverage", `coverage/${state.sessionId}`, coverageTitle);
  coveredList.replaceChildren(loadingCard("Checking each grounded source section…"));
  gapList.replaceChildren(loadingCard("Naming only specific candidate gaps…"));
  setMessage(coverageMessage, "Reviewing uploaded material. No internet search is available in this step.");
  setButtonBusy(regenerateCoverageButton, true, "Generating coverage…", "Regenerate coverage");
  generateMapButton.disabled = true;
  try {
    const body = await api(`/api/sessions/${state.sessionId}/coverage`, { method: "POST" });
    state.coverage = body;
    renderCoverage(body);
    setMessage(coverageMessage, "Coverage is ready. Every visible claim passed source-reference validation.", "success");
    generateMapButton.disabled = false;
  } catch (error) {
    coveredList.replaceChildren(errorCard(error.message, "Retry coverage generation"));
    gapList.replaceChildren(emptyCard("No candidate gaps are displayed until coverage validates."));
    setMessage(coverageMessage, `${error.message} ${error.body?.saved_state || "Your sources are saved."}`, "error");
    generateMapButton.disabled = true;
  } finally {
    setButtonBusy(regenerateCoverageButton, false, "", "Regenerate coverage");
  }
}

async function showCoverage() {
  showView("coverage", `coverage/${state.sessionId}`, coverageTitle);
  try {
    const body = await api(`/api/sessions/${state.sessionId}/coverage`);
    state.coverage = body;
    renderCoverage(body);
    setMessage(coverageMessage, "Coverage restored from the saved session.", "success");
    generateMapButton.disabled = false;
  } catch (error) {
    if (error.body?.error_code === "coverage_not_generated") {
      await showSources();
      setUploadMessage("Build the learning path first. Your material is ready.");
      return;
    }
    setMessage(coverageMessage, `${error.message} Your sources remain saved.`, "error");
  }
}

function loadingCard(text) {
  const card = element("div", "result-card loading-card");
  card.append(element("span", "loading-mark", "…"), element("p", "", text));
  return card;
}

function emptyCard(text) {
  const card = element("div", "result-card empty-result");
  card.append(element("p", "", text));
  return card;
}

function errorCard(text, actionLabel) {
  const card = element("div", "result-card error-result");
  card.append(element("strong", "", "Result not displayed"), element("p", "", text), element("span", "micro-copy", actionLabel));
  return card;
}

function referenceButton(reference, details) {
  const detail = details.find((item) => item.source_id === reference.source_id && item.chunk_id === reference.chunk_id);
  return element(
    "span",
    "source-reference",
    detail ? `${sourceOriginLabel(detail.source_origin)} · ${detail.filename} · ${detail.location}` : "Verified source location",
  );
}

function renderCoverage(body) {
  const coverage = body.coverage;
  const origins = new Set(body.source_ref_details.map((item) => item.source_origin));
  coverageSourceOriginHeading.textContent = origins.has("uploaded")
    ? "Uploaded material"
    : origins.has("ai_supplement")
      ? "AI supplemental explanation"
      : "Saved learning source";
  uploadedPolicyText.textContent = origins.has("uploaded")
    ? "Primary source for this map and later learning activities."
    : "No uploaded material is available in this session.";
  aiPolicyText.textContent = origins.has("ai_supplement")
    ? "Supplemental explanations stay labeled and never claim uploaded or external provenance."
    : "Must stay labeled and cannot invent source locations.";
  coveredList.replaceChildren();
  gapList.replaceChildren();
  coveredCount.textContent = `${coverage.covered_concepts.length} covered`;
  gapCount.textContent = `${body.source_gaps.length} ${body.source_gaps.length === 1 ? "gap" : "gaps"}`;
  coverage.covered_concepts.forEach((concept) => {
    const card = element("article", "result-card");
    card.append(element("h3", "", concept.title), element("p", "", concept.coverage_summary));
    const refs = element("div", "reference-list");
    concept.source_refs.forEach((reference) => refs.append(referenceButton(reference, body.source_ref_details)));
    card.append(refs);
    coveredList.append(card);
  });
  if (!body.source_gaps.length) {
    gapList.append(emptyCard("No specific source gaps were identified. The Agent still cannot search without later learning evidence."));
  } else {
    body.source_gaps.forEach((gap) => {
      const card = element("article", "result-card gap-card");
      const status = element("span", "candidate-label", "Candidate only");
      card.append(status, element("h3", "", gap.description), element("p", "", gap.why_needed));
      const evidence = element("p", "evidence-line", `Why it was named: ${gap.evidence}`);
      card.append(evidence);
      const refs = element("div", "reference-list");
      gap.current_source_refs.forEach((reference) => refs.append(referenceButton(reference, body.source_ref_details)));
      card.append(refs);
      gapList.append(card);
    });
  }
  coverageGenerationLabel.textContent = "Source references verified · No external search used";
}

async function createMap() {
  showView("path", `path/${state.sessionId}`, pathTitle);
  conceptMap.replaceChildren(loadingCard("Building 2–5 grounded concepts and dependency links…"));
  setMessage(pathMessage, "Organizing the knowledge framework from foundation to application.");
  setButtonBusy(generateMapButton, true, "Generating map…", "Generate the learning map");
  confirmPathButton.disabled = true;
  try {
    const body = await api(`/api/sessions/${state.sessionId}/path`, { method: "POST" });
    state.knowledgeMap = body;
    state.fullRoute = body.knowledge_map.concepts.map((concept) => concept.concept_key);
    renderPath(body);
    setMessage(pathMessage, "Your knowledge framework is ready. Start with the first explanation when you are ready.", "success");
    confirmPathButton.disabled = false;
  } catch (error) {
    conceptMap.replaceChildren(errorCard(error.message, "Return to coverage or retry map generation"));
    setMessage(pathMessage, `${error.message} ${error.body?.saved_state || "Your coverage review is saved."}`, "error");
  } finally {
    setButtonBusy(generateMapButton, false, "", "Generate the learning map");
  }
}

async function showPath() {
  showView("path", `path/${state.sessionId}`, pathTitle);
  const body = await api(`/api/sessions/${state.sessionId}/path`);
  state.knowledgeMap = body;
  state.fullRoute = body.knowledge_map.concepts.map((concept) => concept.concept_key);
  renderPath(body);
  setMessage(pathMessage, body.confirmed ? "This route is confirmed." : "Learning map restored from the saved session.", "success");
}

function renderPath(body) {
  const map = body.knowledge_map;
  const conceptsByKey = new Map(map.concepts.map((concept) => [concept.concept_key, concept]));
  conceptMap.replaceChildren();
  pathConceptPreview.hidden = true;
  pathConceptPreview.replaceChildren();
  mapCount.textContent = `${map.concepts.length} concepts`;
  map.concepts.forEach((concept, index) => {
    const item = element("li", "concept-node");
    item.dataset.inRoute = String(map.recommended_route.includes(concept.concept_key));
    const number = element("span", "concept-number", String(index + 1));
    const button = element("button", "concept-node-button");
    button.type = "button";
    button.setAttribute("aria-expanded", "false");
    button.append(element("strong", "", concept.title), element("span", "", concept.plain_definition));
    button.addEventListener("click", () => {
      conceptMap.querySelectorAll(".concept-node-button").forEach((node) => {
        node.classList.toggle("selected", node === button);
        node.setAttribute("aria-expanded", String(node === button));
      });
      const prerequisiteNames = concept.prerequisite_keys.map((key) => conceptsByKey.get(key)?.title || key);
      renderMapConceptPreview(pathConceptPreview, concept, prerequisiteNames, index + 1, map.concepts.length);
    });
    item.append(number, button);
    conceptMap.append(item);
  });
  conceptMap.querySelector(".concept-node-button")?.click();
  confirmPathButton.dataset.confirmed = String(Boolean(body.confirmed));
  confirmPathButton.textContent = body.confirmed ? "Return to the current concept" : "Start learning the first concept";
  pathGenerationLabel.textContent = "Built from your material · Ready to learn";
}

function renderMapConceptPreview(container, concept, prerequisiteNames, position, total) {
  container.replaceChildren();
  container.hidden = false;
  const heading = element("div", "map-preview-heading");
  heading.append(
    element("span", "status-chip", `${position} of ${total}`),
    element("h3", "", concept.title),
  );
  const relationship = prerequisiteNames.length
    ? `Builds on ${prerequisiteNames.join(", ")}.`
    : "This is the foundation of the framework.";
  container.append(
    heading,
    element("p", "", concept.plain_definition),
    element("p", "map-preview-relationship", concept.role_in_map || relationship),
    element("p", "map-preview-dependency", relationship),
  );
}

async function confirmPath() {
  if (confirmPathButton.dataset.confirmed === "true") {
    await showFocus();
    return;
  }
  setButtonBusy(confirmPathButton, true, "Opening the first explanation…", "Start learning the first concept");
  try {
    await startFirstConcept();
  } catch (error) {
    setMessage(pathMessage, `${error.message} Your map is still saved.`, "error");
  } finally {
    setButtonBusy(confirmPathButton, false, "", "Start learning the first concept");
  }
}

async function startFirstConcept() {
  const session = await getCurrentSession();
  const body = await api(`/api/sessions/${state.sessionId}/learn/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ version: session.version }),
  });
  renderFocus(body);
  showView("focus", `focus/${state.sessionId}`, focusTitle);
}

function focusDraftKey() {
  return `startframe_focus_note_${state.sessionId}`;
}

function draftLocalKey(draftType) {
  if (draftType === "tutor") return `startframe_tutor_draft_${state.sessionId}`;
  if (draftType === "quiz" || draftType === "recall") return `startframe_${draftType}_draft_${state.sessionId}`;
  return focusDraftKey();
}

function queueDraftSave(draftType, content, statusTarget, hintDepth = 0) {
  window.localStorage.setItem(draftLocalKey(draftType), content);
  window.clearTimeout(state.saveTimers[draftType]);
  if (!navigator.onLine) {
    statusTarget.textContent = "Saved on this device · waiting to sync";
    return;
  }
  statusTarget.textContent = "Saving…";
  state.saveTimers[draftType] = window.setTimeout(
    () => saveDraftNow(draftType, content, statusTarget, hintDepth),
    500,
  );
}

async function saveDraftNow(draftType, content, statusTarget, hintDepth = 0) {
  window.clearTimeout(state.saveTimers[draftType]);
  window.localStorage.setItem(draftLocalKey(draftType), content);
  if (!navigator.onLine) {
    statusTarget.textContent = "Saved on this device · waiting to sync";
    return null;
  }
  statusTarget.textContent = "Saving…";
  try {
    const body = await api(`/api/sessions/${state.sessionId}/drafts/${draftType}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content,
        hint_depth: hintDepth,
        version: state.drafts[draftType]?.server_version || 0,
      }),
    });
    state.drafts[draftType] = body.draft;
    window.localStorage.setItem(draftLocalKey(draftType), body.draft.content);
    statusTarget.textContent = "Saved on server";
    focusSaveStatus.textContent = "Saved";
    if (draftType === "tutor") tutorSaveStatus.textContent = "Conversation and draft saved";
    if (draftType === "quiz" || draftType === "recall") activitySaveStatus.textContent = "Saved";
    return body.draft;
  } catch (error) {
    if (error.body?.error_code === "draft_version_conflict") {
      openDraftConflict(draftType, content, statusTarget, error.body.details, hintDepth);
      return null;
    }
    statusTarget.textContent = "Save failed · local copy kept";
    focusSaveStatus.textContent = "Local copy kept";
    if (draftType === "tutor") tutorSaveStatus.textContent = "Local draft kept";
    if (draftType === "quiz" || draftType === "recall") activitySaveStatus.textContent = "Local draft kept";
    return null;
  }
}

function openDraftConflict(draftType, localContent, statusTarget, details, hintDepth = 0) {
  const serverDraft = details?.server_draft;
  state.conflict = {
    draftType,
    localContent,
    statusTarget,
    serverVersion: serverDraft?.server_version || 0,
    hintDepth,
  };
  conflictLocal.value = localContent;
  conflictServer.value = serverDraft?.content || "The server copy is empty.";
  statusTarget.textContent = "Conflict · choose a version";
  conflictDialog.showModal();
}

async function showFocus(existing = null) {
  const body = existing || await api(`/api/sessions/${state.sessionId}/focus`);
  renderFocus(body);
  showView("focus", `focus/${state.sessionId}`, focusTitle);
  if (body.session.is_paused && !pauseDialog.open) pauseDialog.showModal();
}

function renderFocus(body) {
  state.focus = body;
  state.session = body.session;
  if (body.drafts.start_action) state.drafts.start_action = body.drafts.start_action;
  if (body.drafts.focus_note) state.drafts.focus_note = body.drafts.focus_note;
  const concept = body.active_concept;
  focusTitle.textContent = concept.title;
  focusBreadcrumb.textContent = `${state.session.name} › ${concept.title}`;
  focusRole.textContent = concept.role_in_map;
  focusDefinition.textContent = concept.plain_definition;
  focusKeyPoints.replaceChildren();
  (concept.key_points || []).forEach((point) => focusKeyPoints.append(element("li", "", point)));
  focusExample.textContent = concept.concrete_example;
  activeConceptCount.textContent = `Current concept ${body.progress.current} of ${body.progress.total}`;
  focusProgressCount.textContent = `${body.progress.current} of ${body.progress.total}`;
  focusRoute.replaceChildren();
  focusMapPreview.hidden = true;
  focusMapPreview.replaceChildren();
  const routeByKey = new Map(body.route.map((item) => [item.concept_key, item]));
  body.route.forEach((item, index) => {
    const row = element("li", "focus-route-item");
    row.dataset.status = item.is_active ? "active" : item.status;
    const marker = item.status === "completed" ? "✓" : String(index + 1);
    const button = element("button", "focus-route-button");
    button.type = "button";
    button.setAttribute("aria-expanded", "false");
    button.append(element("span", "route-marker", marker), element("span", "route-title", item.title));
    if (item.is_active) button.append(element("span", "route-current", "Current"));
    button.addEventListener("click", () => {
      focusRoute.querySelectorAll(".focus-route-button").forEach((node) => {
        node.classList.toggle("selected", node === button);
        node.setAttribute("aria-expanded", String(node === button));
      });
      const prerequisites = (item.prerequisite_keys || []).map((key) => routeByKey.get(key)?.title || key);
      renderMapConceptPreview(focusMapPreview, item, prerequisites, index + 1, body.route.length);
    });
    row.append(button);
    focusRoute.append(row);
  });
  focusRoute.querySelector(".focus-route-item[data-status='active'] .focus-route-button")?.click();

  focusSources.replaceChildren();
  concept.source_refs.forEach((reference) => {
    const detail = concept.source_ref_details.find(
      (item) => item.source_id === reference.source_id && item.chunk_id === reference.chunk_id,
    );
    const detailOrigin = detail?.source_origin || body.source_policy.primary_origin;
    const disclosure = element("details", "inline-source");
    const summary = element(
      "summary",
      "",
      detail ? `${sourceOriginLabel(detailOrigin)} · ${detail.filename} · ${detail.location}` : sourceOriginLabel(detailOrigin),
    );
    const excerpt = element("p", "source-excerpt", detail?.excerpt || "The verified source location is saved with this concept.");
    disclosure.append(summary, excerpt);
    focusSources.append(disclosure);
  });
  (body.external_supplements || []).forEach((source) => {
    const row = element("div", "focus-source-row");
    const origin = element("span", "origin-badge origin-external", "External supplement");
    const link = element("a", "source-reference", `${source.title} · ${source.publisher}`);
    link.href = source.canonical_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", `Open external source: ${source.title}`);
    row.append(origin, link);
    focusSources.append(row);
  });
  const serverNote = body.drafts.focus_note?.content || "";
  const localNote = window.localStorage.getItem(focusDraftKey());
  focusNote.value = localNote === null ? serverNote : localNote;
  focusNoteStatus.textContent = serverNote && focusNote.value === serverNote
    ? "Saved on server"
    : focusNote.value
      ? "Saved on this device · waiting to sync"
      : "Not saved yet";
  focusSaveStatus.textContent = body.session.last_saved_at ? "Saved" : "Ready to save";

  selectMobilePanel("learn");
}

async function openTutor(trigger) {
  state.tutorReturnTrigger = trigger || state.tutorReturnTrigger || openTutorButton;
  if (state.session?.tutor_open) {
    await showTutor();
    return;
  }
  if (trigger) setButtonBusy(trigger, true, "Opening Tutor…", trigger.textContent);
  try {
    const body = await api(`/api/sessions/${state.sessionId}/tutor/open`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: state.session.version }),
    });
    await showTutor(body);
  } catch (error) {
    focusNoteStatus.textContent = `${error.message} Your current concept remains saved.`;
  } finally {
    if (trigger) {
      const label = trigger.dataset.focusPanel === "tutor" ? "Tutor" : "Open Tutor for this concept";
      setButtonBusy(trigger, false, "", label);
    }
  }
}

async function showTutor(existing = null) {
  const [body, draftsBody] = await Promise.all([
    existing ? Promise.resolve(existing) : api(`/api/sessions/${state.sessionId}/tutor/messages`),
    api(`/api/sessions/${state.sessionId}/drafts`),
  ]);
  state.tutor = body;
  state.session = body.session;
  draftsBody.drafts.forEach((draft) => { state.drafts[draft.draft_type] = draft; });
  renderTutor(body);
  showView("tutor", `tutor/${state.sessionId}`, tutorTitle);
}

function renderTutor(body) {
  const context = body.context;
  const concept = context.concept;
  tutorTitle.textContent = `${concept.title} Tutor`;
  tutorBreadcrumb.textContent = `${state.session.name} › ${concept.title}`;
  tutorConcept.textContent = concept.title;
  tutorRole.textContent = concept.role_in_map;
  tutorPrevious.textContent = context.previous_concept_title || "This is the first route concept.";
  const level = body.thread.last_guidance_level || 1;
  tutorGuidanceLevel.textContent = `${level} · ${body.guidance_ladder[level - 1]}`;
  tutorSaveStatus.textContent = "Conversation saved";
  const tutorPrimaryOrigin = concept.source_ref_details.some((item) => item.source_origin === "uploaded")
    ? "uploaded"
    : "ai_supplement";
  tutorModeLabel.textContent = sourceOriginLabel(tutorPrimaryOrigin);

  tutorContextSources.replaceChildren();
  concept.source_refs.forEach((reference) => {
    const row = element("div", "focus-source-row");
    const detail = concept.source_ref_details.find(
      (item) => item.source_id === reference.source_id && item.chunk_id === reference.chunk_id,
    );
    const detailOrigin = detail?.source_origin || tutorPrimaryOrigin;
    row.append(element("span", sourceOriginClass(detailOrigin), sourceOriginLabel(detailOrigin)));
    row.append(referenceButton(reference, concept.source_ref_details));
    tutorContextSources.append(row);
  });

  guidanceLadder.replaceChildren();
  body.guidance_ladder.forEach((item, index) => {
    const entry = element("li", index + 1 === level ? "current-guidance" : "", `${index + 1}. ${item}`);
    if (index + 1 === level) entry.append(element("strong", "", " · current"));
    guidanceLadder.append(entry);
  });

  tutorActions.replaceChildren();
  body.quick_actions.forEach((action) => {
    const button = element("button", "tutor-action", action.label);
    button.type = "button";
    button.addEventListener("click", () => sendTutorTurn(action.label, action.id));
    tutorActions.append(button);
  });

  tutorLog.replaceChildren();
  body.messages.forEach((message) => tutorLog.append(renderTutorMessage(message)));
  tutorEmpty.hidden = body.messages.length > 0;
  if (body.messages.length) tutorLog.lastElementChild?.scrollIntoView({ block: "nearest" });

  const serverDraft = state.drafts.tutor?.content || "";
  const localDraft = window.localStorage.getItem(draftLocalKey("tutor"));
  tutorInput.value = localDraft === null ? serverDraft : localDraft;
  tutorDraftStatus.textContent = serverDraft && tutorInput.value === serverDraft
    ? "Draft saved on server"
    : tutorInput.value
      ? "Draft saved on this device · waiting to sync"
      : "No unsent draft";
  tutorMessageStatus.textContent = body.messages.length
    ? "Continue with a support action or answer the latest checking question."
    : "No message has been sent yet.";
}

function renderTutorMessage(message) {
  const article = element("article", `tutor-message tutor-message-${message.role}`);
  const header = element("div", "tutor-message-header");
  header.append(element("strong", "", message.role === "tutor" ? "Tutor" : "You"));
  if (message.role === "tutor") {
    const originLabel = message.source_origin === "ai_supplement"
      ? "AI supplemental explanation"
      : "Based on uploaded material";
    const badge = element("span", `origin-badge ${message.source_origin === "ai_supplement" ? "origin-ai" : ""}`, originLabel);
    header.append(badge);
  }
  article.append(header, element("p", "tutor-message-copy", message.message));
  if (message.checking_question) {
    const check = element("div", "tutor-checking-question");
    check.append(element("strong", "", "Checking question"), element("p", "", message.checking_question));
    article.append(check);
  }
  if (message.source_refs?.length) {
    const refs = element("div", "reference-list");
    message.source_refs.forEach((reference) => refs.append(referenceButton(reference, message.source_ref_details)));
    article.append(refs);
  }
  if (message.confusion_signal || message.prerequisite_gap_signal) {
    const signal = element("div", "tutor-signal");
    signal.append(element("strong", "", "Factual Tutor signal"));
    if (message.confusion_signal) signal.append(element("p", "", message.confusion_signal));
    if (message.prerequisite_gap_signal) signal.append(element("p", "", message.prerequisite_gap_signal));
    signal.append(element("span", "micro-copy", "This is an observation, not an Agent decision or search request."));
    article.append(signal);
  }
  return article;
}

async function sendTutorTurn(message, quickAction = null) {
  const cleaned = String(message || "").trim();
  if (!cleaned) {
    tutorMessageStatus.textContent = "Write a question or choose one support action.";
    tutorInput.focus();
    return;
  }
  if (!quickAction) {
    const saved = await saveDraftNow("tutor", tutorInput.value, tutorDraftStatus);
    if (!saved) return;
  }
  setButtonBusy(sendTutorMessageButton, true, "Tutor is thinking…", "Send to Tutor");
  tutorActions.querySelectorAll("button").forEach((button) => { button.disabled = true; });
  tutorMessageStatus.textContent = "Tutor is preparing a source-grounded response. Your unsent text remains saved.";
  try {
    const body = await api(`/api/sessions/${state.sessionId}/tutor/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: cleaned,
        quick_action: quickAction,
        thread_version: state.tutor.thread.version,
      }),
    });
    state.tutor = body;
    state.session = body.session;
    renderTutor(body);
    if (!quickAction) {
      tutorInput.value = "";
      await saveDraftNow("tutor", "", tutorDraftStatus);
    }
    tutorMessageStatus.textContent = "Tutor response saved. No internet search was available or performed.";
  } catch (error) {
    tutorMessageStatus.textContent = `${error.message} Your unsent text is still saved; retry when ready.`;
    if (error.body?.error_code === "tutor_version_conflict") {
      await showTutor();
      tutorMessageStatus.textContent = "The newer conversation was restored. Your unsent text is still here; send it again when ready.";
    }
  } finally {
    setButtonBusy(sendTutorMessageButton, false, "", "Send to Tutor");
    tutorActions.querySelectorAll("button").forEach((button) => { button.disabled = false; });
  }
}

async function closeTutor() {
  setButtonBusy(closeTutorButton, true, "Closing Tutor…", "Close Tutor");
  try {
    if (tutorInput.value || state.drafts.tutor) {
      const saved = await saveDraftNow("tutor", tutorInput.value, tutorDraftStatus);
      if (!saved) return;
    }
    const focusBody = await api(`/api/sessions/${state.sessionId}/tutor/close`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ thread_version: state.tutor.thread.version }),
    });
    state.focus = focusBody;
    state.session = focusBody.session;
    renderFocus(focusBody);
    showView("focus", `focus/${state.sessionId}`, focusTitle);
    const trigger = state.tutorReturnTrigger;
    state.tutorReturnTrigger = null;
    if (trigger?.isConnected) trigger.focus({ preventScroll: true });
  } catch (error) {
    tutorMessageStatus.textContent = `${error.message} The Tutor conversation remains open and saved.`;
  } finally {
    setButtonBusy(closeTutorButton, false, "", "Close Tutor");
  }
}

async function startActivity(type, trigger) {
  state.activityReturnTrigger = trigger;
  const readyLabel = type === "quiz" ? "Multiple choice" : "Free recall";
  const busyLabel = type === "quiz" ? "Preparing Quiz…" : "Preparing free recall…";
  setButtonBusy(trigger, true, busyLabel, readyLabel);
  focusSaveStatus.textContent = "Preparing a grounded practice activity…";
  try {
    const body = await api(`/api/sessions/${state.sessionId}/activities`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, version: state.session.version }),
    });
    window.localStorage.removeItem(draftLocalKey(type));
    state.activity = body;
    state.session = body.session;
    renderActivity(body);
    showView("activity", `activity/${body.activity.id}`, activityTitle);
  } catch (error) {
    focusSaveStatus.textContent = `${error.message} Your concept and notes remain saved; retry when ready.`;
  } finally {
    setButtonBusy(trigger, false, "", readyLabel);
    trigger.innerHTML = type === "quiz"
      ? "<strong>Multiple choice</strong><span>3 questions</span>"
      : "<strong>Free recall</strong><span>1 response</span>";
  }
}

async function showActivity(existing = null) {
  let activityId = existing?.activity?.id || state.activity?.activity?.id || state.session?.active_activity_id;
  if (!activityId) {
    const session = await getCurrentSession();
    activityId = session?.active_activity_id;
  }
  if (!activityId) throw new Error("The active practice could not be restored.");
  const body = existing || await api(`/api/activities/${activityId}`);
  state.activity = body;
  state.session = body.session;
  if (body.draft) state.drafts[body.activity.type] = body.draft;
  renderActivity(body);
  if (body.submission?.feedback_ready && body.submission.feedback_id) {
    await showFeedback(await api(`/api/feedback/${body.submission.feedback_id}`));
    return;
  }
  showView("activity", `activity/${activityId}`, activityTitle);
  if (body.session.is_paused && !pauseDialog.open) pauseDialog.showModal();
}

function currentActivityContent() {
  if (!state.activity) return "";
  if (state.activity.activity.type === "quiz") {
    const answers = {};
    quizOptions.querySelectorAll(".quiz-question").forEach((question) => {
      const selected = question.querySelector("input[type='radio']:checked");
      if (selected) answers[question.dataset.questionId] = selected.value;
    });
    return Object.keys(answers).length ? JSON.stringify(answers) : "";
  }
  return recallAnswer.value;
}

function applyActivityDraftContent(type, content) {
  if (type === "quiz") {
    let answers = {};
    try {
      answers = JSON.parse(content);
    } catch (_error) {
      const firstQuestion = quizOptions.querySelector(".quiz-question");
      if (firstQuestion) answers[firstQuestion.dataset.questionId] = content;
    }
    quizOptions.querySelectorAll(".quiz-question").forEach((question) => {
      question.querySelectorAll("input[type='radio']").forEach((input) => {
        input.checked = input.value === answers[question.dataset.questionId];
      });
    });
  } else if (type === "recall" || type === "remedial") {
    recallAnswer.value = content;
  }
}

function renderActivity(body) {
  state.activity = body;
  state.session = body.session;
  const activity = body.activity;
  const type = activity.type;
  const isQuiz = type === "quiz";
  const isRemedial = type === "remedial";
  const typeName = isQuiz ? "Quiz" : isRemedial ? "Remedial practice" : "Free recall";
  activityTypeLabel.textContent = typeName;
  activityTitle.textContent = typeName;
  activityBreadcrumb.textContent = activity.concept_title;
  activityKindChip.textContent = isQuiz
    ? `${body.quiz.question_count} questions · single select`
    : isRemedial
      ? `One smaller step · round ${activity.remedial_round}`
      : "2–3 sentences · meaning over exact wording";
  activityOriginLabel.textContent = activity.source_origin === "ai_supplement"
    ? "Includes an AI supplemental explanation"
    : activity.source_origin === "external"
      ? "Includes an external supplement"
      : "Based on your material";
  activityPrompt.hidden = isQuiz;
  activityPrompt.textContent = isQuiz ? "" : activity.prompt;
  remedialCompletion.hidden = !isRemedial;
  remedialCompletion.textContent = isRemedial ? `Done when: ${body.remedial.completion_condition}` : "";
  activitySaveStatus.textContent = body.session.last_saved_at ? "Saved" : "Ready to save";

  const serverContent = body.draft?.content || "";
  const localContent = window.localStorage.getItem(draftLocalKey(type));
  const restoredContent = localContent === null ? serverContent : localContent;
  if (body.draft) state.drafts[type] = body.draft;
  quizOptions.replaceChildren();
  quizOptions.hidden = !isQuiz;
  recallAnswerWrap.hidden = isQuiz;
  if (isQuiz) {
    body.quiz.questions.forEach((question, questionIndex) => {
      const fieldset = element("fieldset", "quiz-question");
      fieldset.dataset.questionId = question.id;
      const legend = element("legend");
      legend.append(
        element("span", "quiz-question-number", `Question ${questionIndex + 1} of ${body.quiz.question_count}`),
        element("strong", "", question.question),
      );
      fieldset.append(legend);
      question.options.forEach((option, optionIndex) => {
        const label = element("label", "quiz-option");
        const input = element("input");
        input.type = "radio";
        input.name = `quiz-answer-${question.id}`;
        input.value = option.id;
        input.disabled = activity.status !== "active";
        input.addEventListener("change", () => {
          const content = currentActivityContent();
          queueDraftSave("quiz", content, activityDraftStatus, body.hints.depth);
          updateQuizDraftStatus(body.quiz.question_count);
        });
        label.append(input, element("span", "", `${String.fromCharCode(65 + optionIndex)}. ${option.text}`));
        fieldset.append(label);
      });
      quizOptions.append(fieldset);
    });
    applyActivityDraftContent("quiz", restoredContent);
  } else {
    activityAnswerLabel.textContent = isRemedial ? "Your one-sentence answer" : "Your 2–3 sentence explanation";
    recallAnswer.value = restoredContent;
    recallAnswer.disabled = activity.status !== "active";
    recallAnswer.placeholder = isRemedial
      ? "Answer only this smaller prompt. One sentence is enough."
      : "Explain it in your own words. An incomplete attempt is still useful.";
  }
  if (isQuiz) updateQuizDraftStatus(body.quiz.question_count);
  else {
    activityDraftStatus.textContent = serverContent && restoredContent === serverContent
      ? "Draft saved on server"
      : restoredContent
        ? "Draft saved on this device · waiting to sync"
        : "No answer saved yet";
  }

  hintList.replaceChildren();
  body.hints.revealed.forEach((hint) => {
    const item = element("div", "hint-item");
    item.append(element("strong", "", `Hint ${hint.level}`), element("p", "", hint.text));
    hintList.append(item);
  });
  revealHintButton.disabled = !body.hints.can_reveal_more;
  revealHintButton.hidden = !body.hints.can_reveal_more;
  revealHintButton.textContent = body.hints.can_reveal_more
    ? body.hints.depth ? "Need another hint?" : "Need a hint?"
    : "";

  const submitted = activity.status === "submitted";
  submitActivityButton.disabled = submitted && body.submission?.feedback_ready;
  submitActivityButton.textContent = submitted
    ? body.submission?.feedback_ready ? "Answer submitted" : "Show result"
    : isQuiz ? "Submit 3 answers" : "Submit answer";
  closeActivityButton.textContent = isRemedial ? "Return to feedback" : "Return to concept";
  activityReturnButton.textContent = isRemedial ? "Return to feedback" : "Return to explanation";
  activityMessage.hidden = true;
  if (submitted) {
    activityDraftStatus.textContent = "Answer saved";
    activitySaveStatus.textContent = "Saved";
  }
}

function updateQuizDraftStatus(total) {
  const answered = quizOptions.querySelectorAll(".quiz-question input[type='radio']:checked").length;
  activityDraftStatus.textContent = answered === total
    ? "All answers saved"
    : `${answered} of ${total} answered`;
}

async function revealNextHint() {
  const body = state.activity;
  if (!body) return;
  const type = body.activity.type;
  const content = currentActivityContent();
  if (content || state.drafts[type]) {
    const saved = await saveDraftNow(type, content, activityDraftStatus, body.hints.depth);
    if (!saved) return;
  }
  setButtonBusy(revealHintButton, true, "Revealing one hint…", revealHintButton.textContent);
  try {
    const updated = await api(`/api/activities/${body.activity.id}/hints/next`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: body.activity.version }),
    });
    state.activity = updated;
    if (updated.draft) state.drafts[type] = updated.draft;
    renderActivity(updated);
    const latestHint = hintList.lastElementChild;
    if (latestHint) {
      latestHint.setAttribute("tabindex", "-1");
      latestHint.focus({ preventScroll: true });
    }
  } catch (error) {
    setMessage(activityMessage, `${error.message} Your answer and existing hints remain saved.`, "error");
  } finally {
    if (state.activity) {
      const canReveal = state.activity.hints.can_reveal_more;
      revealHintButton.disabled = !canReveal;
      revealHintButton.hidden = !canReveal;
      revealHintButton.textContent = canReveal
        ? state.activity.hints.depth ? "Need another hint?" : "Need a hint?"
        : "";
    }
  }
}

async function submitCurrentActivity(event) {
  event.preventDefault();
  const body = state.activity;
  if (!body) return;
  if (body.activity.status === "submitted" && body.submission) {
    await prepareFeedback(body.submission.id);
    return;
  }
  if (body.activity.status !== "active") return;
  const type = body.activity.type;
  const content = currentActivityContent().trim();
  const quizComplete = type !== "quiz"
    || quizOptions.querySelectorAll(".quiz-question input[type='radio']:checked").length === body.quiz.question_count;
  if (!content || !quizComplete) {
    setMessage(activityMessage, type === "quiz" ? "Answer all three questions before submitting." : "Write one checkable attempt before submitting.", "error");
    (type === "quiz" ? quizOptions : recallAnswer).focus();
    return;
  }
  const submitLabel = type === "quiz" ? "Submit 3 answers" : "Submit answer";
  setButtonBusy(submitActivityButton, true, "Checking…", submitLabel);
  try {
    const saved = await saveDraftNow(type, content, activityDraftStatus, body.hints.depth);
    if (!saved) return;
    const createdAt = Date.parse(`${body.activity.created_at.replace(" ", "T")}Z`);
    const elapsedSeconds = Number.isFinite(createdAt)
      ? Math.max(0, Math.min(86400, Math.floor((Date.now() - createdAt) / 1000)))
      : 0;
    const submitted = await api(`/api/activities/${body.activity.id}/attempts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: body.activity.version, elapsed_seconds: elapsedSeconds }),
    });
    state.activity = submitted;
    state.session = submitted.session;
    renderActivity(submitted);
    await prepareFeedback(submitted.submission.id);
  } catch (error) {
    setMessage(activityMessage, `${error.message} Your draft and hint depth remain saved; submit again when ready.`, "error");
  } finally {
    if (state.activity?.activity.status === "active") {
      setButtonBusy(submitActivityButton, false, "", submitLabel);
    } else if (state.activity?.activity.status === "submitted" && !state.feedback) {
      setButtonBusy(submitActivityButton, false, "", "Show result");
    }
  }
}

async function prepareFeedback(attemptId) {
  setButtonBusy(submitActivityButton, true, "Checking…", "Show result");
  try {
    const body = await api(`/api/attempts/${attemptId}/feedback`, { method: "POST" });
    state.feedback = body;
    state.session = body.session;
    renderFeedback(body);
    showView("feedback", `feedback/${body.feedback.id}`, feedbackTitle);
  } catch (error) {
    setMessage(activityMessage, `${error.message} Your submitted answer is saved; retry feedback when ready.`, "error");
    setButtonBusy(submitActivityButton, false, "", "Try again");
  }
}

async function showFeedback(existing = null) {
  let body = existing;
  if (!body) {
    const hashId = window.location.hash.startsWith("#feedback/")
      ? window.location.hash.split("/")[1]
      : null;
    if (hashId) body = await api(`/api/feedback/${hashId}`);
    else if (state.feedback?.feedback) body = await api(`/api/feedback/${state.feedback.feedback.id}`);
    else {
      const session = state.session || await getCurrentSession();
      const activity = await api(`/api/activities/${session.active_activity_id}`);
      if (!activity.submission) throw new Error("The submitted answer could not be restored.");
      body = activity.submission.feedback_id
        ? await api(`/api/feedback/${activity.submission.feedback_id}`)
        : await api(`/api/attempts/${activity.submission.id}/feedback`, { method: "POST" });
    }
  }
  state.feedback = body;
  state.session = body.session;
  renderFeedback(body);
  showView("feedback", `feedback/${body.feedback.id}`, feedbackTitle);
  if (body.session.is_paused && !pauseDialog.open) pauseDialog.showModal();
}

function renderFeedback(body) {
  const feedback = body.feedback;
  const evidence = body.evidence;
  const quizResult = feedback.quiz_result;
  const mastered = evidence?.outcome === "mastered";
  const resultTitle = quizResult
    ? `${quizResult.correct_count} of ${quizResult.total_questions} correct`
    : mastered ? "Nice work" : evidence?.outcome === "partial" ? "Good start" : "Let’s clarify this";
  feedbackTitle.textContent = resultTitle;
  feedbackBreadcrumb.textContent = feedback.concept_title;
  feedbackSaveStatus.textContent = "Saved";
  feedbackResultMark.textContent = mastered ? "✓" : "→";
  feedbackResultMark.dataset.result = mastered ? "correct" : "review";
  feedbackResultLabel.textContent = feedback.activity_type === "quiz" ? "Quiz result" : "Practice result";
  feedbackSectionsTitle.textContent = resultTitle;
  feedbackOriginLabel.textContent = feedback.source_origin === "ai_supplement"
    ? "Explanation includes an AI supplement"
    : feedback.source_origin === "external" ? "Explanation includes an external supplement" : "Explanation based on your material";
  quizAnswerReview.hidden = !quizResult;
  quizAnswerReview.replaceChildren();
  feedbackExplanation.hidden = Boolean(quizResult);
  if (quizResult) {
    quizResult.questions.forEach((question) => {
      const review = element("article", "quiz-review-item");
      review.dataset.correct = String(question.is_correct);
      const heading = element("div", "quiz-review-heading");
      heading.append(
        element("span", "quiz-review-mark", question.is_correct ? "✓" : "→"),
        element("strong", "", `Question ${question.question_number}`),
        element("span", "", question.is_correct ? "Correct" : "Review"),
      );
      review.append(heading, element("p", "quiz-review-question", question.question));
      const answer = element("p", "quiz-review-answer");
      answer.append(element("span", "", "Your answer"), document.createTextNode(question.selected_option_text));
      review.append(answer);
      if (!question.is_correct) {
        const correct = element("p", "quiz-review-answer");
        correct.append(element("span", "", "Correct answer"), document.createTextNode(question.correct_option_text));
        review.append(correct);
      }
      review.append(element("p", "quiz-review-why", question.explanation));
      quizAnswerReview.append(review);
    });
  }
  feedbackCorrection.textContent = feedback.compact_correction;
  feedbackEncouragement.textContent = feedback.encouragement;
  feedbackMessage.hidden = true;
  completeFeedbackButton.textContent = "Continue";
  completeFeedbackButton.disabled = false;
}

async function completeFeedbackStep() {
  const body = state.feedback;
  if (!body) return;
  setButtonBusy(completeFeedbackButton, true, "Preparing your next step…", "Continue");
  try {
    const evidenceBody = await api(`/api/feedback/${body.feedback.id}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: body.session.version }),
    });
    await showEvidenceReady(evidenceBody, true);
  } catch (error) {
    setMessage(feedbackMessage, `${error.message} Your answer remains saved.`, "error");
    setButtonBusy(completeFeedbackButton, false, "", "Try again");
  }
}

async function showEvidenceReady(existing = null, continueAutomatically = true) {
  const body = existing || await api(`/api/sessions/${state.sessionId}/evidence`);
  state.evidence = body;
  state.session = body.session;
  renderEvidenceReady(body);
  showView("evidence", `evidence/${state.sessionId}`, evidenceReadyTitle);
  if (body.session.is_paused) {
    if (!pauseDialog.open) pauseDialog.showModal();
    return;
  }
  if (continueAutomatically) await runPlanningAgent();
}

function renderEvidenceReady() {
  evidenceReadyTitle.textContent = "Preparing your next step…";
  runAgentButton.hidden = true;
  setButtonBusy(runAgentButton, false, "", "Try again");
  setMessage(evidenceReadyMessage, "");
}

async function runPlanningAgent() {
  runAgentButton.hidden = true;
  setMessage(evidenceReadyMessage, "");
  try {
    const body = await api(`/api/sessions/${state.sessionId}/agent-decisions`, { method: "POST" });
    await showAgentDecision(body);
  } catch (error) {
    evidenceReadyTitle.textContent = "We couldn’t prepare the next step";
    setMessage(evidenceReadyMessage, `${error.message} Your progress remains saved.`, "error");
    runAgentButton.hidden = false;
    setButtonBusy(runAgentButton, false, "", "Try again");
  }
}

async function showAgentDecision(existing = null) {
  const body = existing || await api(`/api/sessions/${state.sessionId}/agent-decisions/latest`);
  state.agent = body;
  state.session = body.session;
  renderAgentDecision(body);
  showView("agent", `agent/${body.decision.id}`, agentTitle);
  if (body.session.is_paused && !pauseDialog.open) pauseDialog.showModal();
}

function renderAgentDecision(body) {
  const decision = body.decision;
  agentTitle.textContent = "Keep learning";
  agentActionTitle.textContent = decision.action_label;
  agentReason.textContent = decision.reason_for_user;
  agentEstimate.textContent = decision.estimated_minutes
    ? `About ${decision.estimated_minutes} minutes`
    : "Finish for now";
  agentSaveStatus.textContent = "Saved";
  const isProposed = decision.status === "proposed";
  setButtonBusy(acceptAgentButton, false, "", "Continue");
  acceptAgentButton.hidden = !isProposed;
  agentPauseButton.hidden = body.session.state === "session_summary";
  setMessage(agentMessage, "");
  if (!isProposed && body.session.state === "search_confirmation") {
    setMessage(agentMessage, "The Agent requested a search, but no search has run. A separate source-gap confirmation is required next.", "success");
  }
}

async function acceptAgentDecision() {
  const body = state.agent;
  if (!body) return;
  setButtonBusy(acceptAgentButton, true, "Continuing…", "Continue");
  try {
    const result = await api(`/api/agent-decisions/${body.decision.id}/accept`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: body.session.version }),
    });
    await handleAgentExecution(result);
  } catch (error) {
    setMessage(agentMessage, `${error.message} ${error.body?.saved_state || "The decision was not changed."}`, "error");
    setButtonBusy(acceptAgentButton, false, "", "Continue");
  }
}

async function handleAgentExecution(body) {
  state.agent = body;
  state.session = body.execution.session;
  const execution = body.execution;
  if (execution.destination === "focus") {
    await showFocus();
    return;
  }
  if (execution.destination === "activity") {
    await showFocus();
    const trigger = execution.activity_type === "quiz" ? startQuizButton : startRecallButton;
    await startActivity(execution.activity_type, trigger);
    return;
  }
  if (execution.destination === "tutor") {
    await showFocus();
    await openTutor(openTutorButton);
    return;
  }
  if (execution.destination === "search_confirmation") {
    await showControlledSearch();
    return;
  }
  if (execution.destination === "session_summary") {
    const summary = await api(`/api/sessions/${state.sessionId}/summary`);
    showFinishedSummary(summary.summary);
  }
}

async function showControlledSearch(existing = null) {
  const body = existing || await api(`/api/sessions/${state.sessionId}/search-requests/latest`);
  state.search = body;
  state.session = body.session;
  renderControlledSearch(body);
  showView("search", `search/${body.search_request.id}`, searchTitle);
  if (body.session.is_paused && !pauseDialog.open) pauseDialog.showModal();
}

function renderControlledSearch(body) {
  const request = body.search_request;
  const isResults = request.search_status === "completed";
  const isRunning = request.search_status === "running";
  searchTitle.textContent = isResults
    ? `External sources for ${body.concept.title}`
    : `Review the source gap for ${body.concept.title}`;
  searchConfirmationPanel.hidden = isResults;
  searchResultsPanel.hidden = !isResults;
  searchPauseButton.hidden = isRunning;
  searchSaveStatus.textContent = isResults
    ? "Cited results saved"
    : isRunning
      ? "Search running · progress saved"
      : request.confirmation_status === "confirmed"
        ? "Scope confirmed"
        : "No search has run";

  searchGates.replaceChildren();
  const gateLabels = [
    ["session_permission", "Session permission", "Suggestions allowed"],
    ["named_gap_validated", "Named source gap", "Validated from evidence"],
    ["agent_requested_search", "Agent request", "One bounded action"],
    ["user_confirmed_this_scope", "This search", "Separate confirmation"],
  ];
  gateLabels.forEach(([key, label, detail]) => {
    const card = element("div", "search-gate");
    card.append(
      element("strong", "", `${body.gates[key] ? "✓" : "○"} ${label}`),
      element("span", "", body.gates[key] ? detail : key === "user_confirmed_this_scope" ? "Waiting for you" : "Not satisfied"),
    );
    searchGates.append(card);
  });
  searchGapTitle.textContent = body.source_gap.description;
  searchGapWhy.textContent = body.source_gap.why_needed;
  searchQueryScope.textContent = request.query_scope;
  searchRequestReason.textContent = request.reason_for_user;
  searchConfirmationTitle.textContent = isRunning ? "Searching this confirmed scope" : "Search has not run yet";
  setMessage(searchMessage, isRunning ? "The confirmed search is running. Do not close this page until results or a recovery message appears." : "");
  setButtonBusy(confirmSearchButton, false, "", "Confirm scope and search");
  setButtonBusy(declineSearchButton, false, "", "Continue without searching");
  confirmSearchButton.hidden = false;
  declineSearchButton.textContent = isRunning ? "Stop waiting and continue" : "Continue without searching";
  confirmSearchButton.disabled = isRunning;
  declineSearchButton.disabled = false;

  searchResultList.replaceChildren();
  searchResultCount.textContent = `${body.external_sources.length} ${body.external_sources.length === 1 ? "source" : "sources"}`;
  body.external_sources.forEach((source, index) => {
    const card = element("article", "external-result-card");
    card.dataset.recommended = String(index === 0);
    const heading = element("div", "external-result-heading");
    const copy = element("div");
    copy.append(
      element("span", "origin-badge origin-external", "External supplement"),
      element("h3", "", source.title),
      element("p", "micro-copy", `${source.publisher} · accessed ${formatAccessedAt(source.accessed_at)}`),
    );
    const link = element("a", "external-url", source.canonical_url);
    link.href = source.canonical_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    copy.append(link);
    if (index === 0) heading.append(copy, element("span", "status-chip", "Recommended"));
    else heading.append(copy);
    const excerpt = element("div", "citation-excerpt");
    excerpt.append(element("strong", "", "Cited summary"), element("p", "", source.citation_excerpt));
    const reason = element("p", "");
    reason.append(element("strong", "", "Why this result: "), document.createTextNode(source.selection_reason));
    const actions = element("div", "external-result-actions");
    const use = element("button", index === 0 ? "button button-primary" : "button button-secondary", "Use this source");
    use.type = "button";
    use.addEventListener("click", () => useExternalSource(source, use));
    actions.append(use);
    card.append(heading, excerpt, reason, actions);
    searchResultList.append(card);
  });
  setButtonBusy(ignoreSearchResultsButton, false, "", "Ignore results and continue");
}

function formatAccessedAt(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("en", { dateStyle: "medium", timeStyle: "short" });
}

async function confirmAndRunSearch() {
  const body = state.search;
  if (!body) return;
  setMessage(searchMessage, "Confirming this exact scope. No broader search is authorized.");
  setButtonBusy(confirmSearchButton, true, "Confirming scope…", "Confirm scope and search");
  declineSearchButton.disabled = true;
  try {
    const confirmed = await api(`/api/search-requests/${body.search_request.id}/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        confirmed: true,
        session_version: body.session.version,
        request_version: body.search_request.version,
      }),
    });
    state.search = confirmed;
    state.session = confirmed.session;
    renderControlledSearch(confirmed);
    setMessage(searchMessage, "Scope confirmed. Running one controlled web search now.");
    setButtonBusy(confirmSearchButton, true, "Searching cited sources…", "Confirm scope and search");
    declineSearchButton.disabled = true;
    const results = await api(`/api/search-requests/${confirmed.search_request.id}/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_version: confirmed.session.version,
        request_version: confirmed.search_request.version,
      }),
    });
    await showControlledSearch(results);
  } catch (error) {
    setMessage(searchMessage, `${error.message} ${error.body?.saved_state || "Your learning progress remains saved."}`, "error");
    confirmSearchButton.hidden = true;
    declineSearchButton.disabled = false;
    declineSearchButton.textContent = "Continue with uploaded material";
    try {
      state.session = await getCurrentSession();
    } catch (_ignored) {
      // Keep the visible recovery action even if the status refresh also failed.
    }
  }
}

async function declineControlledSearch() {
  const body = state.search;
  if (!body) return;
  if (state.session?.state === "search_running") {
    setButtonBusy(declineSearchButton, true, "Stopping wait…", "Stop waiting and continue");
    try {
      const result = await api(`/api/search-requests/${body.search_request.id}/cancel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_version: body.session.version,
          request_version: body.search_request.version,
        }),
      });
      state.session = result.session;
      await showFocus();
    } catch (error) {
      setMessage(searchMessage, `${error.message} Reload to check the saved search state.`, "error");
      setButtonBusy(declineSearchButton, false, "", "Stop waiting and continue");
    }
    return;
  }
  if (state.session?.state !== "search_confirmation") {
    await showFocus();
    return;
  }
  setButtonBusy(declineSearchButton, true, "Saving your choice…", "Continue without searching");
  try {
    const result = await api(`/api/search-requests/${body.search_request.id}/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        confirmed: false,
        session_version: body.session.version,
        request_version: body.search_request.version,
      }),
    });
    state.session = result.session;
    await showFocus();
  } catch (error) {
    setMessage(searchMessage, `${error.message} No external search was started.`, "error");
    setButtonBusy(declineSearchButton, false, "", "Continue without searching");
  }
}

async function useExternalSource(source, button) {
  setButtonBusy(button, true, "Adding supplement…", "Use this source");
  try {
    const result = await api(`/api/external-sources/${source.id}/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: state.session.version }),
    });
    state.session = result.session;
    await showFocus();
  } catch (error) {
    searchResultsTitle.textContent = `${error.message} The result set remains saved.`;
    setButtonBusy(button, false, "", "Use this source");
  }
}

async function ignoreControlledSearchResults() {
  const body = state.search;
  if (!body) return;
  setButtonBusy(ignoreSearchResultsButton, true, "Saving your choice…", "Ignore results and continue");
  try {
    const result = await api(`/api/search-requests/${body.search_request.id}/ignore`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: body.session.version }),
    });
    state.session = result.session;
    await showFocus();
  } catch (error) {
    setButtonBusy(ignoreSearchResultsButton, false, "", "Ignore results and continue");
    searchResultsTitle.textContent = `${error.message} The cited results remain saved.`;
  }
}

function showFinishedSummary(summary) {
  document.querySelector("#summary-title").textContent = summary.title || "Session complete";
  summaryRestartAction.textContent = summary.restart_action;
  summaryConcept.textContent = summary.current_concept || state.agent?.evidence_summary?.concept_title || "Saved learning session";
  summaryNote.textContent = summary.saved_focus_note || "Your progress and next step are saved. You can stop and return at any time.";
  summaryCompleted.textContent = summary.completed_concepts?.length ? summary.completed_concepts.join(" · ") : "No concept has been marked complete yet.";
  summaryReview.textContent = summary.still_to_review?.length ? summary.still_to_review.join(" · ") : "No remaining route concept.";
  summaryStats.textContent = `${summary.evidence_count || 0} evidence records${summary.latest_outcome ? ` · latest outcome: ${summary.latest_outcome.replaceAll("_", " ")}` : ""} · stopping has no penalty`;
  summaryResumeButton.hidden = true;
  showView("summary", `summary/${state.sessionId}`, document.querySelector("#summary-title"));
}

async function closeCurrentActivity() {
  const body = state.activity;
  if (!body) return;
  const type = body.activity.type;
  setButtonBusy(closeActivityButton, true, "Saving practice…", "Return to concept");
  try {
    if (body.activity.status === "active") {
      const content = currentActivityContent();
      if (content || state.drafts[type]) {
        const saved = await saveDraftNow(type, content, activityDraftStatus, body.hints.depth);
        if (!saved) return;
      }
    }
    const focusBody = await api(`/api/activities/${body.activity.id}/close`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: state.session.version }),
    });
    state.activity = null;
    state.session = focusBody.session;
    if (focusBody.feedback) {
      state.feedback = focusBody;
      renderFeedback(focusBody);
      showView("feedback", `feedback/${focusBody.feedback.id}`, feedbackTitle);
    } else {
      state.focus = focusBody;
      renderFocus(focusBody);
      showView("focus", `focus/${state.sessionId}`, focusTitle);
    }
    const trigger = state.activityReturnTrigger;
    state.activityReturnTrigger = null;
    if (trigger?.isConnected) trigger.focus({ preventScroll: true });
  } catch (error) {
    setMessage(activityMessage, `${error.message} Your practice remains open and saved.`, "error");
  } finally {
    setButtonBusy(closeActivityButton, false, "", "Return to concept");
  }
}

async function saveFocusNoteNow() {
  setButtonBusy(saveFocusNoteButton, true, "Saving note…", "Save this focus note");
  const draft = await saveDraftNow("focus_note", focusNote.value, focusNoteStatus);
  setButtonBusy(saveFocusNoteButton, false, "", "Save this focus note");
  return draft;
}

async function pauseActiveSession({ showDialog = true } = {}) {
  const isActivityState = ["practicing", "remedial_practice"].includes(state.session?.state);
  const draftType = isActivityState
      ? state.activity?.activity?.type
      : window.location.hash.startsWith("#tutor/")
        ? "tutor"
        : state.session?.state === "learning_concept" ? "focus_note" : null;
  if (draftType) {
    const isActivityDraft = ["quiz", "recall", "remedial"].includes(draftType);
    const input = draftType === "tutor" ? tutorInput : focusNote;
    const status = draftType === "tutor" ? tutorDraftStatus : isActivityDraft ? activityDraftStatus : focusNoteStatus;
    const content = isActivityDraft ? currentActivityContent() : input.value;
    const hintDepth = isActivityDraft ? state.activity?.hints?.depth || 0 : 0;
    if (content || state.drafts[draftType]) {
      const saved = await saveDraftNow(draftType, content, status, hintDepth);
      if (!saved) return null;
    }
  }
  const body = await api(`/api/sessions/${state.sessionId}/pause`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ version: state.session.version }),
  });
  state.session = body.session;
  window.clearInterval(state.focusTimer);
  if (showDialog && !pauseDialog.open) pauseDialog.showModal();
  return body.session;
}

async function resumeActiveSession() {
  setButtonBusy(resumeSessionButton, true, "Resuming…", "Resume session");
  try {
    const body = await api(`/api/sessions/${state.sessionId}/resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: state.session.version }),
    });
    state.session = body.session;
    if (pauseDialog.open) pauseDialog.close();
    if (["practicing", "remedial_practice"].includes(state.session.state)) await showActivity();
    else if (state.session.state === "feedback_shown") await showFeedback();
    else if (state.session.state === "evidence_ready") await showEvidenceReady();
    else if (state.session.state === "agent_decision") await showAgentDecision();
    else if (["search_confirmation", "search_running", "search_results"].includes(state.session.state)) await showControlledSearch();
    else if (state.session.state === "session_summary") {
      const summary = await api(`/api/sessions/${state.sessionId}/summary`);
      showFinishedSummary(summary.summary);
    }
    else if (state.session.state === "learning_concept" && state.session.tutor_open) await showTutor();
    else if (state.session.state === "learning_concept") await showFocus();
    else if (state.session.state === "start_action") await startFirstConcept();
    else await showPath();
  } catch (error) {
    pauseDialog.querySelector("#pause-description").textContent = `${error.message} Your saved work is unchanged.`;
  } finally {
    setButtonBusy(resumeSessionButton, false, "", "Resume session");
  }
}

function showSummary() {
  const focus = state.focus;
  document.querySelector("#summary-title").textContent = "Your exact restart point is ready";
  summaryResumeButton.hidden = false;
  summaryRestartAction.textContent = focus.restart_action;
  summaryConcept.textContent = focus.active_concept.title;
  summaryNote.textContent = focusNote.value.trim() || "No focus note yet. Resume at the concise explanation.";
  const completed = focus.route.filter((concept) => concept.status === "completed").map((concept) => concept.title);
  const remaining = focus.route.filter((concept) => concept.status !== "completed").map((concept) => concept.title);
  summaryCompleted.textContent = completed.length ? completed.join(" · ") : "No concept has been marked complete yet.";
  summaryReview.textContent = remaining.length ? remaining.join(" · ") : "No remaining route concept.";
  summaryStats.textContent = "Checkpoint saved · session paused · stopping has no penalty";
  showView("summary", `summary/${state.sessionId}`, document.querySelector("#summary-title"));
}

function selectMobilePanel(panel) {
  document.querySelectorAll("[data-focus-panel]").forEach((button) => {
    if (button.dataset.focusPanel === panel) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  document.querySelector("#focus-map-panel").dataset.mobileActive = String(panel === "map");
  document.querySelector("#focus-learn-panel").dataset.mobileActive = String(panel === "learn");
}

async function chooseConflictVersion(choice) {
  if (!state.conflict) return;
  const conflict = state.conflict;
  const button = choice === "local" ? keepLocalDraftButton : keepServerDraftButton;
  setButtonBusy(button, true, "Saving choice…", button.textContent);
  try {
    const body = await api(`/api/sessions/${state.sessionId}/draft-conflicts/${conflict.draftType}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        choice,
        local_content: conflict.localContent,
        server_version: conflict.serverVersion,
        hint_depth: conflict.hintDepth || 0,
      }),
    });
    state.drafts[conflict.draftType] = body.draft;
    const target = conflict.draftType === "tutor"
        ? tutorInput
        : ["quiz", "recall", "remedial"].includes(conflict.draftType)
          ? null
          : focusNote;
    if (target) target.value = body.draft.content;
    else applyActivityDraftContent(conflict.draftType, body.draft.content);
    window.localStorage.setItem(draftLocalKey(conflict.draftType), body.draft.content);
    conflict.statusTarget.textContent = "Saved on server";
    state.conflict = null;
    conflictDialog.close();
  } catch (error) {
    conflict.statusTarget.textContent = `${error.message} Both copies remain available.`;
  } finally {
    setButtonBusy(button, false, "", choice === "local" ? "Keep this device version" : "Keep server version");
  }
}

startButtons.forEach((button) => button.addEventListener("click", beginSession));
libraryLink.addEventListener("click", showHome);
openSettingsPanelButton.addEventListener("click", openSettingsPanel);
closeSettingsPanelButton.addEventListener("click", closeSettingsPanel);
settingsDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeSettingsPanel();
});
openHelpPanelButton.addEventListener("click", openHelpPanel);
closeHelpPanelButton.addEventListener("click", closeHelpPanel);
helpDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeHelpPanel();
});
exportJsonButton.addEventListener("click", () => downloadWorkspaceExport("json"));
exportMarkdownButton.addEventListener("click", () => downloadWorkspaceExport("markdown"));
openAiActivityButton.addEventListener("click", () => {
  settingsDialog.close();
  openAiActivity();
});
closeAiActivityButton.addEventListener("click", closeAiActivity);
openDeleteWorkspaceButton.addEventListener("click", () => {
  settingsDialog.close();
  openWorkspaceDelete();
});
cancelWorkspaceDeleteButton.addEventListener("click", closeWorkspaceDelete);
confirmWorkspaceDeleteButton.addEventListener("click", confirmWorkspaceDelete);
cancelSessionDeleteButton.addEventListener("click", closeSessionDelete);
confirmSessionDeleteButton.addEventListener("click", confirmSessionDelete);
backHomeButton.addEventListener("click", leaveSourceView);
saveForLaterButton.addEventListener("click", showHome);
chooseFilesButton.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => uploadFiles(fileInput.files));
loadDemoButton.addEventListener("click", loadSampleMaterials);
reviewCoverageButton.addEventListener("click", prepareLearningPath);
openPasteButton.addEventListener("click", () => pasteDialog.showModal());
cancelPasteButton.addEventListener("click", () => pasteDialog.close());
pasteForm.addEventListener("submit", submitPastedSource);
cancelDeleteButton.addEventListener("click", () => deleteDialog.close());
confirmDeleteButton.addEventListener("click", deleteSelectedSource);
sessionSearch.addEventListener("input", renderSessions);
sessionFilter.addEventListener("change", renderSessions);
[preferenceLargeText, preferenceReducedMotion, preferenceShowTimer, preferenceSearchSuggestions]
  .forEach((control) => control.addEventListener("change", savePreferences));

backToSourcesFromCoverageButton.addEventListener("click", () => showSources());
regenerateCoverageButton.addEventListener("click", createCoverage);
generateMapButton.addEventListener("click", createMap);
backToCoverageButton.addEventListener("click", showCoverage);
confirmPathButton.addEventListener("click", confirmPath);
focusNote.addEventListener("input", () => queueDraftSave("focus_note", focusNote.value, focusNoteStatus));
saveFocusNoteButton.addEventListener("click", saveFocusNoteNow);
openTutorButton.addEventListener("click", () => openTutor(openTutorButton));
startQuizButton.addEventListener("click", () => startActivity("quiz", startQuizButton));
startRecallButton.addEventListener("click", () => startActivity("recall", startRecallButton));
pauseSessionButton.addEventListener("click", () => pauseActiveSession());
resumeSessionButton.addEventListener("click", resumeActiveSession);
pauseLibraryButton.addEventListener("click", async () => {
  pauseDialog.close();
  await showHome();
});
keepLocalDraftButton.addEventListener("click", () => chooseConflictVersion("local"));
keepServerDraftButton.addEventListener("click", () => chooseConflictVersion("server"));
summaryLibraryButton.addEventListener("click", showHome);
summaryExportButton.addEventListener("click", () => downloadWorkspaceExport("markdown"));
summaryResumeButton.addEventListener("click", resumeActiveSession);
reviewFullMapButton.addEventListener("click", showPath);
mobileSessionNav.addEventListener("click", (event) => {
  const button = event.target.closest("[data-focus-panel]");
  if (!button) return;
  if (button.dataset.focusPanel === "tutor") openTutor(button);
  else selectMobilePanel(button.dataset.focusPanel);
});
tutorInput.addEventListener("input", () => queueDraftSave("tutor", tutorInput.value, tutorDraftStatus));
tutorForm.addEventListener("submit", (event) => {
  event.preventDefault();
  sendTutorTurn(tutorInput.value);
});
closeTutorButton.addEventListener("click", closeTutor);
tutorPauseButton.addEventListener("click", () => pauseActiveSession());
recallAnswer.addEventListener("input", () => {
  if (!state.activity || !["recall", "remedial"].includes(state.activity.activity.type)) return;
  const type = state.activity.activity.type;
  queueDraftSave(type, recallAnswer.value, activityDraftStatus, state.activity.hints.depth);
});
activityForm.addEventListener("submit", submitCurrentActivity);
revealHintButton.addEventListener("click", revealNextHint);
closeActivityButton.addEventListener("click", closeCurrentActivity);
activityReturnButton.addEventListener("click", closeCurrentActivity);
activityPauseButton.addEventListener("click", () => pauseActiveSession());
mobileActivityConcept.addEventListener("click", closeCurrentActivity);
mobileActivityHints.addEventListener("click", () => {
  revealHintButton.scrollIntoView({ behavior: "smooth", block: "center" });
  revealHintButton.focus({ preventScroll: true });
});
mobileActivityPause.addEventListener("click", () => pauseActiveSession());
completeFeedbackButton.addEventListener("click", completeFeedbackStep);
feedbackPauseButton.addEventListener("click", () => pauseActiveSession());
mobileFeedbackPause.addEventListener("click", () => pauseActiveSession());
mobileFeedbackConcept.addEventListener("click", () => {
  setMessage(feedbackMessage, "Select Continue to move on.", "info");
});
runAgentButton.addEventListener("click", runPlanningAgent);
agentPauseButton.addEventListener("click", () => pauseActiveSession());
acceptAgentButton.addEventListener("click", acceptAgentDecision);
searchPauseButton.addEventListener("click", () => pauseActiveSession());
declineSearchButton.addEventListener("click", declineControlledSearch);
confirmSearchButton.addEventListener("click", confirmAndRunSearch);
ignoreSearchResultsButton.addEventListener("click", ignoreControlledSearchResults);

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.dataset.dragging = "true";
  });
});
["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.dataset.dragging = "false";
  });
});
dropZone.addEventListener("drop", (event) => uploadFiles(event.dataTransfer.files));

window.addEventListener("offline", () => {
  connectionBanner.hidden = false;
  if (state.session?.state === "learning_concept") {
    if (window.location.hash.startsWith("#tutor/")) tutorDraftStatus.textContent = "Offline · local copy kept";
    else focusNoteStatus.textContent = "Offline · local copy kept";
    focusSaveStatus.textContent = "Offline";
  }
  if (["practicing", "remedial_practice"].includes(state.session?.state)) {
    activityDraftStatus.textContent = "Offline · local copy kept";
    activitySaveStatus.textContent = "Offline";
  }
  if (state.session?.state === "feedback_shown") feedbackSaveStatus.textContent = "Offline · saved feedback remains available";
});
window.addEventListener("online", () => {
  connectionBanner.hidden = true;
  setUploadMessage("Connection restored. You can upload or retry now.", "success");
  if (state.session?.state === "learning_concept" && window.location.hash.startsWith("#tutor/")) {
    saveDraftNow("tutor", tutorInput.value, tutorDraftStatus);
  } else if (state.session?.state === "learning_concept") {
    saveDraftNow("focus_note", focusNote.value, focusNoteStatus);
  } else if (["practicing", "remedial_practice"].includes(state.session?.state) && state.activity) {
    saveDraftNow(
      state.activity.activity.type,
      currentActivityContent(),
      activityDraftStatus,
      state.activity.hints.depth,
    );
  }
});

async function initialize() {
  loadPreferences();
  connectionBanner.hidden = navigator.onLine;
  await Promise.all([checkRuntime(), loadSessions()]);
  if (!state.sessionId) return;
  const hash = window.location.hash;
  try {
    if (hash.startsWith("#coverage/")) await showCoverage();
    else if (hash.startsWith("#path/")) await showPath();
    else if (hash.startsWith("#start/")) await startFirstConcept();
    else if (hash.startsWith("#tutor/")) await showTutor();
    else if (hash.startsWith("#activity/")) await showActivity();
    else if (hash.startsWith("#feedback/")) await showFeedback();
    else if (hash.startsWith("#evidence/")) await showEvidenceReady();
    else if (hash.startsWith("#agent/")) await showAgentDecision();
    else if (hash.startsWith("#search/")) await showControlledSearch();
    else if (hash.startsWith("#focus/")) await showFocus();
    else if (hash.startsWith("#summary/")) {
      const session = await getCurrentSession();
      if (session.state === "session_summary") {
        const summary = await api(`/api/sessions/${state.sessionId}/summary`);
        showFinishedSummary(summary.summary);
      } else {
        await showFocus();
        showSummary();
      }
    }
    else if (hash.startsWith("#sources/")) await showSources();
  } catch (error) {
    await showSources();
    setUploadMessage(`${error.message} Your sources are still available.`, "error");
  }
}

initialize();
