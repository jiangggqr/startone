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
  sourceReturn: null,
  sourceReturnTrigger: null,
  pollTimer: null,
  focusTimer: null,
  saveTimers: {},
  drafts: {},
  focus: null,
  tutor: null,
  tutorReturnTrigger: null,
  conflict: null,
  runtimeMode: "demo",
};

const views = {
  home: document.querySelector("#home-view"),
  sources: document.querySelector("#source-view"),
  setup: document.querySelector("#setup-view"),
  coverage: document.querySelector("#coverage-view"),
  path: document.querySelector("#path-view"),
  start: document.querySelector("#start-action-view"),
  focus: document.querySelector("#focus-view"),
  tutor: document.querySelector("#tutor-view"),
  summary: document.querySelector("#summary-view"),
};

const modeBadge = document.querySelector("#mode-badge");
const runtimeStatus = document.querySelector("#runtime-status");
const startButtons = document.querySelectorAll("#start-session, #empty-start");
const libraryLink = document.querySelector("#library-link");
const sourceTitle = document.querySelector("#sources-title");
const backHomeButton = document.querySelector("#back-home");
const saveForLaterButton = document.querySelector("#save-for-later");
const recentEmpty = document.querySelector("#recent-empty");
const recentList = document.querySelector("#recent-list");
const sourceCount = document.querySelector("#source-count");
const sourceEmpty = document.querySelector("#source-empty");
const sourceList = document.querySelector("#source-list");
const uploadMessage = document.querySelector("#upload-message");
const connectionBanner = document.querySelector("#connection-banner");
const chooseFilesButton = document.querySelector("#choose-files");
const fileInput = document.querySelector("#file-input");
const dropZone = document.querySelector("#drop-zone");
const previewEmpty = document.querySelector("#preview-empty");
const previewContent = document.querySelector("#preview-content");
const previewFilename = document.querySelector("#preview-filename");
const previewLocation = document.querySelector("#preview-location");
const previewText = document.querySelector("#preview-text");
const chunkNavigation = document.querySelector("#chunk-navigation");
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

const setupForm = document.querySelector("#setup-form");
const setupTitle = document.querySelector("#setup-title");
const setupMessage = document.querySelector("#setup-message");
const setupSaveStatus = document.querySelector("#setup-save-status");
const generateCoverageButton = document.querySelector("#generate-coverage");
const backToSourcesButton = document.querySelector("#back-to-sources");

const coverageTitle = document.querySelector("#coverage-title");
const coverageMessage = document.querySelector("#coverage-message");
const coveredList = document.querySelector("#covered-list");
const gapList = document.querySelector("#gap-list");
const coveredCount = document.querySelector("#covered-count");
const gapCount = document.querySelector("#gap-count");
const coverageGenerationLabel = document.querySelector("#coverage-generation-label");
const regenerateCoverageButton = document.querySelector("#regenerate-coverage");
const generateMapButton = document.querySelector("#generate-map");
const backToSetupButton = document.querySelector("#back-to-setup");

const pathTitle = document.querySelector("#path-title");
const pathMessage = document.querySelector("#path-message");
const mapCount = document.querySelector("#map-count");
const conceptMap = document.querySelector("#concept-map");
const routeList = document.querySelector("#route-list");
const routeTotal = document.querySelector("#route-total");
const pathGenerationLabel = document.querySelector("#path-generation-label");
const startActionHeading = document.querySelector("#start-action-heading");
const startActionInstruction = document.querySelector("#start-action-instruction");
const startActionCondition = document.querySelector("#start-action-condition");
const startActionReason = document.querySelector("#start-action-reason");
const shortenRouteButton = document.querySelector("#shorten-route");
const restoreRouteButton = document.querySelector("#restore-route");
const confirmPathButton = document.querySelector("#confirm-path");
const backToCoverageButton = document.querySelector("#back-to-coverage");

const startPageTitle = document.querySelector("#start-page-title");
const startPageInstruction = document.querySelector("#start-page-instruction");
const startPageCondition = document.querySelector("#start-page-condition");
const startDuration = document.querySelector("#start-duration");
const startAnswer = document.querySelector("#start-answer");
const startMessage = document.querySelector("#start-message");
const startSaveStatus = document.querySelector("#start-save-status");
const saveStartAnswerButton = document.querySelector("#save-start-answer");
const startSaveLaterButton = document.querySelector("#start-save-later");
const startBackMapButton = document.querySelector("#start-back-map");

const focusTitle = document.querySelector("#focus-title");
const focusBreadcrumb = document.querySelector("#focus-breadcrumb");
const focusRole = document.querySelector("#focus-role");
const focusDefinition = document.querySelector("#focus-definition");
const focusSources = document.querySelector("#focus-sources");
const focusRoute = document.querySelector("#focus-route");
const focusProgressCount = document.querySelector("#focus-progress-count");
const activeConceptCount = document.querySelector("#active-concept-count");
const focusProgressBar = document.querySelector("#focus-progress-bar");
const focusProgressCopy = document.querySelector("#focus-progress-copy");
const startingPoint = document.querySelector("#starting-point");
const elapsedTime = document.querySelector("#elapsed-time");
const remainingTime = document.querySelector("#remaining-time");
const timerContent = document.querySelector("#timer-content");
const hideTimer = document.querySelector("#hide-timer");
const focusNote = document.querySelector("#focus-note");
const focusNoteStatus = document.querySelector("#focus-note-status");
const focusSaveStatus = document.querySelector("#focus-save-status");
const saveFocusNoteButton = document.querySelector("#save-focus-note");
const openTutorButton = document.querySelector("#open-tutor");
const pauseSessionButton = document.querySelector("#pause-session");
const saveExitButton = document.querySelector("#save-exit");
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
const summaryLibraryButton = document.querySelector("#summary-library");
const summaryResumeButton = document.querySelector("#summary-resume");

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
    modeBadge.textContent = isDemo ? "Demo mode" : "Live GPT-5.6 mode";
    modeBadge.dataset.mode = health.mode;
    runtimeStatus.textContent = `Service healthy · ${isDemo ? "Demo" : "Live GPT-5.6"} mode · Database schema ${health.schema_version}`;
    loadDemoButton.hidden = !isDemo;
    demoMaterialNote.hidden = !isDemo;
  } catch (error) {
    modeBadge.textContent = "Service offline";
    modeBadge.dataset.mode = "offline";
    runtimeStatus.textContent = "Could not reach the service. Refresh to retry; page content remains available.";
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
      const label = button.id === "empty-start" ? "Start your first session" : "Upload material and start a session";
      setButtonBusy(button, false, "", label);
    });
  }
}

async function loadSessions() {
  try {
    const body = await api("/api/sessions");
    renderSessions(body.sessions);
  } catch (error) {
    recentEmpty.hidden = false;
    recentList.hidden = true;
  }
}

function renderSessions(sessions) {
  recentList.replaceChildren();
  recentEmpty.hidden = sessions.length > 0;
  recentList.hidden = sessions.length === 0;
  document.querySelector("#recent-sessions .status-chip").textContent = `${sessions.length} ${sessions.length === 1 ? "session" : "sessions"}`;
  sessions.forEach((session) => {
    const item = element("article", "session-item");
    const copy = element("div");
    copy.append(element("h3", "", session.name));
    const ready = Number(session.ready_source_count || 0);
    const total = Number(session.source_count || 0);
    copy.append(element("p", "", `${ready}/${total} sources ready · ${session.state.replaceAll("_", " ")}`));
    const resume = element("button", "button button-secondary", resumeLabel(session));
    resume.type = "button";
    resume.addEventListener("click", () => resumeSession(session.id));
    item.append(copy, resume);
    recentList.append(item);
  });
}

function resumeLabel(session) {
  if (session.is_paused) return "Resume paused session";
  if (session.state === "learning_concept") return "Resume current concept";
  if (session.state === "start_action") return "Open start action";
  if (session.state === "path_drafting") return "Review learning path";
  if (session.setup_completed) return "Review source coverage";
  return "Continue session";
}

async function resumeSession(sessionId) {
  state.sessionId = sessionId;
  window.localStorage.setItem("startframe_session_id", sessionId);
  try {
    const session = await getCurrentSession();
    if (session.state === "learning_concept") {
      if (session.tutor_open) await showTutor();
      else await showFocus();
      if (session.is_paused) pauseDialog.showModal();
    } else if (session.state === "start_action") {
      await showStartAction();
      if (session.is_paused) pauseDialog.showModal();
    } else if (session.state === "path_drafting") {
      try {
        await showPath();
      } catch (error) {
        await showCoverage();
      }
    } else if (session.setup_completed) {
      await showCoverage();
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

function sourceMetadata(source) {
  const size = source.byte_size >= 1024 * 1024
    ? `${(source.byte_size / (1024 * 1024)).toFixed(1)} MB`
    : `${Math.max(1, Math.round(source.byte_size / 1024))} KB`;
  const locationCount = source.media_kind === "pdf" && source.page_count
    ? `${source.page_count} ${source.page_count === 1 ? "page" : "pages"}`
    : source.line_count
      ? `${source.line_count} lines`
      : "Location pending";
  return `${sourceStatus(source)} · ${locationCount} · ${size}`;
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
  sourceEmpty.hidden = state.sources.length > 0;
  sourceCount.textContent = `${state.sources.length} ${state.sources.length === 1 ? "source" : "sources"}`;
  const readySources = state.sources.filter((source) => ["success", "partial_success"].includes(source.parse_status));
  reviewCoverageButton.disabled = readySources.length === 0;
  coverageNote.textContent = readySources.length
    ? `${readySources.length} readable ${readySources.length === 1 ? "source is" : "sources are"} ready. Continue when you are satisfied with the material.`
    : "Add at least one readable source to continue.";

  state.sources.forEach((source) => {
    const item = element("li", "source-item");
    item.dataset.state = source.parse_status;
    const select = element("button", "source-select");
    select.type = "button";
    const marker = ["success", "partial_success"].includes(source.parse_status) ? "✓ " : source.parse_status === "error" ? "! " : "… ";
    select.append(element("span", "source-name", `${marker}${source.filename}`));
    select.append(element("span", "source-meta", sourceMetadata(source)));
    if (source.error_message) select.append(element("span", "source-error", source.error_message));
    select.disabled = !["success", "partial_success"].includes(source.parse_status);
    if (!select.disabled) select.addEventListener("click", () => selectSource(source.id));

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
    const firstReady = state.sources.find((source) => ["success", "partial_success"].includes(source.parse_status));
    if (firstReady) await selectSource(firstReady.id);
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

async function loadDemoMaterials() {
  setButtonBusy(loadDemoButton, true, "Loading Demo materials…", "Load the two Demo materials");
  try {
    const body = await api(`/api/sessions/${state.sessionId}/demo-materials`, { method: "POST" });
    setUploadMessage(
      body.created_count
        ? "Two clearly labeled Demo materials were copied into this private session."
        : "The two Demo materials are already in this session.",
      "success",
    );
    await loadSources();
    const firstReady = state.sources.find((source) => ["success", "partial_success"].includes(source.parse_status));
    if (firstReady) await selectSource(firstReady.id);
  } catch (error) {
    setUploadMessage(`${error.message} Existing sources are unchanged.`, "error");
  } finally {
    setButtonBusy(loadDemoButton, false, "", "Load the two Demo materials");
  }
}

async function selectSource(sourceId, chunkId = null) {
  try {
    const body = await api(`/api/sources/${sourceId}`);
    state.selectedSourceId = sourceId;
    state.selectedSource = body.source;
    state.selectedChunkIndex = chunkId
      ? Math.max(0, body.source.chunks.findIndex((chunk) => chunk.id === chunkId))
      : 0;
    renderPreview();
  } catch (error) {
    setUploadMessage(`${error.message} Select another source or retry this one.`, "error");
  }
}

function chunkLocation(source, chunk) {
  if (source.media_kind === "pdf") return `Page ${chunk.page_number} · excerpt ${chunk.page_chunk_index}`;
  if (source.media_kind === "pasted") return `Paragraph ${chunk.paragraph_number} · characters ${chunk.start_char}–${chunk.end_char}`;
  const heading = chunk.heading_path || "Document";
  return `${heading} · lines ${chunk.start_line}–${chunk.end_line}`;
}

function renderPreview() {
  const source = state.selectedSource;
  if (!source || !source.chunks?.length) {
    previewEmpty.hidden = false;
    previewContent.hidden = true;
    return;
  }
  const chunk = source.chunks[state.selectedChunkIndex];
  previewEmpty.hidden = true;
  previewContent.hidden = false;
  previewFilename.textContent = source.filename;
  previewLocation.textContent = chunkLocation(source, chunk);
  previewText.textContent = chunk.text;
  chunkNavigation.replaceChildren();
  source.chunks.forEach((item, index) => {
    const button = element("button", "small-button", String(index + 1));
    button.type = "button";
    button.setAttribute("aria-label", `Show ${chunkLocation(source, item)}`);
    button.setAttribute("aria-current", String(index === state.selectedChunkIndex));
    button.addEventListener("click", () => {
      state.selectedChunkIndex = index;
      renderPreview();
    });
    chunkNavigation.append(button);
  });
}

async function openSourceReference(reference, trigger) {
  const returnTo = window.location.hash.startsWith("#tutor/")
    ? "tutor"
    : window.location.hash.startsWith("#focus/")
    ? "focus"
    : window.location.hash.startsWith("#path/")
      ? "path"
      : "coverage";
  state.sourceReturnTrigger = trigger;
  await showSources(returnTo);
  await selectSource(reference.source_id, reference.chunk_id);
  document.querySelector("#preview-title").focus({ preventScroll: true });
  document.querySelector("#preview-title").scrollIntoView({ block: "start" });
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
    if (state.selectedSourceId === state.deleteTarget.id) {
      state.selectedSourceId = null;
      state.selectedSource = null;
      renderPreview();
    }
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
    await selectSource(body.source.id);
  } catch (error) {
    pasteError.textContent = `${error.message} Your pasted text remains in this form.`;
    pasteError.hidden = false;
    pasteError.focus();
  } finally {
    setButtonBusy(submitPasteButton, false, "", "Add pasted text");
  }
}

function setupDraftKey() {
  return `startframe_setup_${state.sessionId}`;
}

function startDraftKey() {
  return `startframe_start_answer_${state.sessionId}`;
}

function setupValues() {
  const data = new FormData(setupForm);
  return {
    goal: String(data.get("goal") || "").trim(),
    prior_knowledge: String(data.get("prior_knowledge") || "").trim(),
    available_minutes: Number(data.get("available_minutes")),
    energy_level: String(data.get("energy_level")),
    current_question: String(data.get("current_question") || "").trim() || null,
    support_preferences: data.getAll("support").map(String),
    show_timer: data.get("show_timer") === "on",
    search_permission: data.get("search_permission") === "on",
  };
}

function fillSetup(values) {
  if (!values) return;
  setupForm.elements.goal.value = values.goal || "";
  setupForm.elements.prior_knowledge.value = values.prior_knowledge || "";
  setupForm.elements.available_minutes.value = String(values.available_minutes || 25);
  setupForm.elements.energy_level.value = values.energy_level || "medium";
  setupForm.elements.current_question.value = values.current_question || "";
  const supports = new Set(values.support_preferences || []);
  setupForm.querySelectorAll('input[name="support"]').forEach((input) => {
    input.checked = supports.has(input.value);
  });
  setupForm.elements.show_timer.checked = Boolean(values.show_timer);
  setupForm.elements.search_permission.checked = Boolean(values.search_permission);
}

async function showSetup() {
  window.clearTimeout(state.pollTimer);
  const session = await getCurrentSession();
  const localDraft = JSON.parse(window.localStorage.getItem(setupDraftKey()) || "null");
  const serverValues = session.setup_completed ? session : null;
  fillSetup(localDraft || serverValues || {
    goal: "Understand self-attention and explain its basic flow",
    prior_knowledge: "Basic machine learning, but no detailed Transformer knowledge",
    available_minutes: 25,
    energy_level: "medium",
    current_question: "How do relevance scores become a new token representation?",
    support_preferences: ["direct_explanation", "define_terms", "short_steps"],
    show_timer: false,
    search_permission: false,
  });
  setMessage(setupMessage, "");
  showView("setup", `setup/${state.sessionId}`, setupTitle);
}

function saveSetupDraft() {
  window.localStorage.setItem(setupDraftKey(), JSON.stringify(setupValues()));
  setupSaveStatus.textContent = "Draft saved on this device.";
}

async function saveSetup() {
  const values = setupValues();
  const body = await api(`/api/sessions/${state.sessionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...values, version: state.session.version }),
  });
  state.session = body.session;
  window.localStorage.removeItem(setupDraftKey());
  setupSaveStatus.textContent = "Saved to this session.";
  return body.session;
}

async function submitSetup(event) {
  event.preventDefault();
  if (!setupForm.reportValidity()) return;
  setMessage(setupMessage, "");
  setButtonBusy(generateCoverageButton, true, "Saving setup…", "Save setup and review source coverage");
  try {
    await saveSetup();
    await createCoverage();
  } catch (error) {
    const saved = error.body?.saved_state || "Your form values remain on this device.";
    setMessage(setupMessage, `${error.message} ${saved}`, "error");
    setupMessage.focus();
  } finally {
    setButtonBusy(generateCoverageButton, false, "", "Save setup and review source coverage");
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
      await showSetup();
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
  const button = element("button", "source-reference");
  button.type = "button";
  button.textContent = detail ? `${detail.filename} · ${detail.location}` : "Open verified source location";
  button.addEventListener("click", () => openSourceReference(reference, button));
  return button;
}

function renderCoverage(body) {
  const coverage = body.coverage;
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
  const generation = body.generation;
  coverageGenerationLabel.textContent = generation.mode === "demo"
    ? "Deterministic Demo fixture · No model call · No internet search"
    : `${generation.model} Structured Output · Source references validated · No internet search`;
}

async function createMap() {
  showView("path", `path/${state.sessionId}`, pathTitle);
  conceptMap.replaceChildren(loadingCard("Building 2–5 grounded concepts and dependency links…"));
  routeList.replaceChildren();
  setMessage(pathMessage, "Generating one route and one 60–120 second start action.");
  setButtonBusy(generateMapButton, true, "Generating map…", "Generate the learning map");
  confirmPathButton.disabled = true;
  try {
    const body = await api(`/api/sessions/${state.sessionId}/path`, { method: "POST" });
    state.knowledgeMap = body;
    state.fullRoute = body.knowledge_map.concepts.map((concept) => concept.concept_key);
    renderPath(body);
    setMessage(pathMessage, "The map is ready. Review or shorten the route before confirming it.", "success");
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
  routeList.replaceChildren();
  mapCount.textContent = `${map.concepts.length} concepts`;
  map.concepts.forEach((concept, index) => {
    const item = element("li", "concept-node");
    item.dataset.inRoute = String(map.recommended_route.includes(concept.concept_key));
    const number = element("span", "concept-number", String(index + 1));
    const copy = element("div");
    copy.append(element("h3", "", concept.title), element("p", "", concept.plain_definition));
    if (concept.prerequisite_keys.length) {
      const names = concept.prerequisite_keys.map((key) => conceptsByKey.get(key)?.title || key).join(", ");
      copy.append(element("p", "prerequisite-line", `Builds on: ${names}`));
    } else {
      copy.append(element("p", "prerequisite-line", "Starting foundation"));
    }
    const refs = element("div", "reference-list");
    concept.source_refs.forEach((reference) => refs.append(referenceButton(reference, body.source_ref_details)));
    copy.append(refs);
    item.append(number, copy);
    conceptMap.append(item);
  });
  let minutes = 0;
  map.recommended_route.forEach((key) => {
    const concept = conceptsByKey.get(key);
    if (!concept) return;
    minutes += concept.estimated_minutes;
    const item = element("li", "route-item");
    item.append(element("strong", "", concept.title), element("span", "", `${concept.estimated_minutes} min`));
    routeList.append(item);
  });
  routeTotal.textContent = `${map.recommended_route.length} concepts · about ${minutes} minutes before the closing summary`;
  shortenRouteButton.disabled = map.recommended_route.length <= 2;
  restoreRouteButton.disabled = map.recommended_route.length === state.fullRoute.length;
  startActionHeading.textContent = map.start_action.title;
  startActionInstruction.textContent = map.start_action.instruction;
  startActionCondition.textContent = map.start_action.completion_condition;
  startActionReason.textContent = `${map.start_action.why_this_first} · About ${map.start_action.estimated_seconds} seconds.`;
  pathGenerationLabel.textContent = body.generation.mode === "demo"
    ? "Deterministic Demo fixture · Source references validated · No internet search"
    : `${body.generation.model} Structured Output · Source references validated · No internet search`;
}

async function adjustRoute(route) {
  setButtonBusy(shortenRouteButton, true, "Updating route…", "Shorten by one concept");
  try {
    const body = await api(`/api/sessions/${state.sessionId}/path`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ route_concept_keys: route }),
    });
    state.knowledgeMap = body;
    renderPath(body);
    setMessage(pathMessage, "The session route was updated. The full dependency map is still visible.", "success");
  } catch (error) {
    setMessage(pathMessage, `${error.message} The previous route is unchanged.`, "error");
  } finally {
    setButtonBusy(shortenRouteButton, false, "", "Shorten by one concept");
  }
}

async function confirmPath() {
  setButtonBusy(confirmPathButton, true, "Confirming route…", "Confirm this route and show the start action");
  try {
    const body = await api(`/api/sessions/${state.sessionId}/path/confirm`, { method: "POST" });
    state.knowledgeMap = body;
    await showStartAction(body);
  } catch (error) {
    setMessage(pathMessage, `${error.message} Your map is still saved.`, "error");
  } finally {
    setButtonBusy(confirmPathButton, false, "", "Confirm this route and show the start action");
  }
}

async function showStartAction(existing = null) {
  const [body, draftsBody] = await Promise.all([
    existing ? Promise.resolve(existing) : api(`/api/sessions/${state.sessionId}/path`),
    api(`/api/sessions/${state.sessionId}/drafts`),
    getCurrentSession(),
  ]);
  state.knowledgeMap = body;
  state.drafts = Object.fromEntries(draftsBody.drafts.map((draft) => [draft.draft_type, draft]));
  const action = body.knowledge_map.start_action;
  startPageTitle.textContent = action.title;
  startPageInstruction.textContent = action.instruction;
  startPageCondition.textContent = action.completion_condition;
  startDuration.textContent = `About ${action.estimated_seconds} seconds`;
  const serverDraft = state.drafts.start_action?.content || "";
  const localDraft = window.localStorage.getItem(startDraftKey());
  startAnswer.value = localDraft === null ? serverDraft : localDraft;
  startSaveStatus.textContent = serverDraft && startAnswer.value === serverDraft
    ? "Saved on server"
    : startAnswer.value
      ? "Saved on this device · waiting to sync"
      : "Not saved yet";
  setMessage(startMessage, startAnswer.value ? "Your unfinished answer was restored." : "");
  showView("start", `start/${state.sessionId}`, startPageTitle);
}

function saveStartDraft() {
  window.localStorage.setItem(startDraftKey(), startAnswer.value);
  queueDraftSave("start_action", startAnswer.value, startSaveStatus);
}

async function saveStartPoint() {
  const answer = startAnswer.value.trim();
  if (!answer) {
    setMessage(startMessage, "Write one checkable sentence before entering the first concept.", "error");
    startAnswer.focus();
    return;
  }
  setButtonBusy(saveStartAnswerButton, true, "Saving starting point…", "Complete and enter focus mode");
  try {
    const draft = await saveDraftNow("start_action", startAnswer.value, startSaveStatus);
    if (!draft) return;
    const body = await api(`/api/sessions/${state.sessionId}/start-action/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: state.session.version }),
    });
    state.session = body.session;
    renderFocus(body);
    showView("focus", `focus/${state.sessionId}`, focusTitle);
  } catch (error) {
    setMessage(startMessage, `${error.message} Your starting-point draft is still saved.`, "error");
  } finally {
    setButtonBusy(saveStartAnswerButton, false, "", "Complete and enter focus mode");
  }
}

function focusDraftKey() {
  return `startframe_focus_note_${state.sessionId}`;
}

function draftLocalKey(draftType) {
  if (draftType === "start_action") return startDraftKey();
  if (draftType === "tutor") return `startframe_tutor_draft_${state.sessionId}`;
  return focusDraftKey();
}

function queueDraftSave(draftType, content, statusTarget) {
  window.localStorage.setItem(draftLocalKey(draftType), content);
  window.clearTimeout(state.saveTimers[draftType]);
  if (!navigator.onLine) {
    statusTarget.textContent = "Saved on this device · waiting to sync";
    return;
  }
  statusTarget.textContent = "Saving…";
  state.saveTimers[draftType] = window.setTimeout(
    () => saveDraftNow(draftType, content, statusTarget),
    500,
  );
}

async function saveDraftNow(draftType, content, statusTarget) {
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
        hint_depth: 0,
        version: state.drafts[draftType]?.server_version || 0,
      }),
    });
    state.drafts[draftType] = body.draft;
    window.localStorage.setItem(draftLocalKey(draftType), body.draft.content);
    statusTarget.textContent = "Saved on server";
    focusSaveStatus.textContent = "Saved";
    if (draftType === "tutor") tutorSaveStatus.textContent = "Conversation and draft saved";
    return body.draft;
  } catch (error) {
    if (error.body?.error_code === "draft_version_conflict") {
      openDraftConflict(draftType, content, statusTarget, error.body.details);
      return null;
    }
    statusTarget.textContent = "Save failed · local copy kept";
    focusSaveStatus.textContent = "Local copy kept";
    if (draftType === "tutor") tutorSaveStatus.textContent = "Local draft kept";
    return null;
  }
}

function openDraftConflict(draftType, localContent, statusTarget, details) {
  const serverDraft = details?.server_draft;
  state.conflict = {
    draftType,
    localContent,
    statusTarget,
    serverVersion: serverDraft?.server_version || 0,
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
  activeConceptCount.textContent = `Current concept ${body.progress.current} of ${body.progress.total}`;
  focusProgressCount.textContent = `${body.progress.current} of ${body.progress.total}`;
  focusProgressCopy.textContent = `${body.progress.completed} completed · current concept is ${concept.title}`;
  focusProgressBar.style.width = `${Math.max(4, (body.progress.completed / body.progress.total) * 100)}%`;
  startingPoint.textContent = body.drafts.start_action?.content || "No starting point was saved.";

  focusRoute.replaceChildren();
  body.route.forEach((item, index) => {
    const row = element("li", "focus-route-item");
    row.dataset.status = item.is_active ? "active" : item.status;
    const marker = item.status === "completed" ? "✓" : String(index + 1);
    row.append(element("span", "route-marker", marker), element("span", "", item.title));
    if (item.is_active) row.append(element("strong", "", "Current"));
    focusRoute.append(row);
  });

  focusSources.replaceChildren();
  concept.source_refs.forEach((reference) => {
    const button = referenceButton(reference, concept.source_ref_details);
    const origin = element("span", "origin-badge", "Uploaded material");
    const row = element("div", "focus-source-row");
    row.append(origin, button);
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

  const storedTimerPreference = window.localStorage.getItem("startframe_hide_timer");
  hideTimer.checked = storedTimerPreference === null ? !Boolean(body.session.show_timer) : storedTimerPreference === "true";
  timerContent.hidden = hideTimer.checked;
  startFocusClock(body.timer);
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
  tutorModeLabel.textContent = body.generation?.mode === "real"
    ? `${body.generation.model} · uploaded material first`
    : "Uploaded material first";

  tutorContextSources.replaceChildren();
  concept.source_refs.forEach((reference) => {
    const row = element("div", "focus-source-row");
    row.append(element("span", "origin-badge", "Uploaded material"));
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

function startFocusClock(timer) {
  window.clearInterval(state.focusTimer);
  const loadedAt = Date.now();
  const baseElapsed = timer.elapsed_seconds;
  const baseRemaining = timer.remaining_seconds;
  const paint = () => {
    const delta = state.session?.is_paused ? 0 : Math.floor((Date.now() - loadedAt) / 1000);
    elapsedTime.textContent = formatDuration(baseElapsed + delta);
    remainingTime.textContent = formatDuration(Math.max(0, baseRemaining - delta));
  };
  paint();
  state.focusTimer = window.setInterval(paint, 1000);
}

function formatDuration(totalSeconds) {
  const safe = Math.max(0, Number(totalSeconds) || 0);
  const minutes = Math.floor(safe / 60);
  const seconds = Math.floor(safe % 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

async function saveFocusNoteNow() {
  setButtonBusy(saveFocusNoteButton, true, "Saving note…", "Save this focus note");
  const draft = await saveDraftNow("focus_note", focusNote.value, focusNoteStatus);
  setButtonBusy(saveFocusNoteButton, false, "", "Save this focus note");
  return draft;
}

async function pauseActiveSession({ showDialog = true } = {}) {
  const draftType = state.session?.state === "start_action"
    ? "start_action"
    : window.location.hash.startsWith("#tutor/")
      ? "tutor"
      : "focus_note";
  const input = draftType === "start_action" ? startAnswer : draftType === "tutor" ? tutorInput : focusNote;
  const status = draftType === "start_action" ? startSaveStatus : draftType === "tutor" ? tutorDraftStatus : focusNoteStatus;
  if (input.value || state.drafts[draftType]) {
    const saved = await saveDraftNow(draftType, input.value, status);
    if (!saved) return null;
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
    if (state.session.state === "learning_concept" && state.session.tutor_open) await showTutor();
    else if (state.session.state === "learning_concept") await showFocus();
    else await showStartAction();
  } catch (error) {
    pauseDialog.querySelector("#pause-description").textContent = `${error.message} Your saved work is unchanged.`;
  } finally {
    setButtonBusy(resumeSessionButton, false, "", "Resume session");
  }
}

async function saveAndExit() {
  setButtonBusy(saveExitButton, true, "Saving session…", "Save and exit");
  try {
    const draft = await saveFocusNoteNow();
    if (!draft) return;
    const paused = await pauseActiveSession({ showDialog: false });
    if (!paused) return;
    showSummary();
  } catch (error) {
    focusSaveStatus.textContent = `${error.message} Local drafts remain available.`;
  } finally {
    setButtonBusy(saveExitButton, false, "", "Save and exit");
  }
}

function showSummary() {
  const focus = state.focus;
  summaryRestartAction.textContent = focus.restart_action;
  summaryConcept.textContent = focus.active_concept.title;
  summaryNote.textContent = focusNote.value.trim() || "No focus note yet. Resume at the concise explanation.";
  showView("summary", `summary/${state.sessionId}`, document.querySelector("#summary-title"));
}

function selectMobilePanel(panel) {
  document.querySelectorAll("[data-focus-panel]").forEach((button) => {
    if (button.dataset.focusPanel === panel) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  document.querySelector("#focus-map-panel").dataset.mobileActive = String(panel === "map");
  document.querySelector("#focus-learn-panel").dataset.mobileActive = String(panel === "learn");
  document.querySelector("#focus-more-panel").dataset.mobileActive = String(panel === "more");
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
        hint_depth: 0,
      }),
    });
    state.drafts[conflict.draftType] = body.draft;
    const target = conflict.draftType === "start_action"
      ? startAnswer
      : conflict.draftType === "tutor"
        ? tutorInput
        : focusNote;
    target.value = body.draft.content;
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
backHomeButton.addEventListener("click", leaveSourceView);
saveForLaterButton.addEventListener("click", showHome);
chooseFilesButton.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => uploadFiles(fileInput.files));
loadDemoButton.addEventListener("click", loadDemoMaterials);
reviewCoverageButton.addEventListener("click", showSetup);
openPasteButton.addEventListener("click", () => pasteDialog.showModal());
cancelPasteButton.addEventListener("click", () => pasteDialog.close());
pasteForm.addEventListener("submit", submitPastedSource);
cancelDeleteButton.addEventListener("click", () => deleteDialog.close());
confirmDeleteButton.addEventListener("click", deleteSelectedSource);

setupForm.addEventListener("input", saveSetupDraft);
setupForm.addEventListener("change", saveSetupDraft);
setupForm.addEventListener("submit", submitSetup);
backToSourcesButton.addEventListener("click", () => showSources());
backToSetupButton.addEventListener("click", showSetup);
regenerateCoverageButton.addEventListener("click", createCoverage);
generateMapButton.addEventListener("click", createMap);
backToCoverageButton.addEventListener("click", showCoverage);
shortenRouteButton.addEventListener("click", () => {
  const route = state.knowledgeMap.knowledge_map.recommended_route;
  if (route.length > 2) adjustRoute(route.slice(0, -1));
});
restoreRouteButton.addEventListener("click", () => adjustRoute(state.fullRoute));
confirmPathButton.addEventListener("click", confirmPath);
startAnswer.addEventListener("input", saveStartDraft);
saveStartAnswerButton.addEventListener("click", saveStartPoint);
startSaveLaterButton.addEventListener("click", () => pauseActiveSession());
startBackMapButton.addEventListener("click", showPath);
focusNote.addEventListener("input", () => queueDraftSave("focus_note", focusNote.value, focusNoteStatus));
saveFocusNoteButton.addEventListener("click", saveFocusNoteNow);
openTutorButton.addEventListener("click", () => openTutor(openTutorButton));
pauseSessionButton.addEventListener("click", () => pauseActiveSession());
resumeSessionButton.addEventListener("click", resumeActiveSession);
pauseLibraryButton.addEventListener("click", async () => {
  pauseDialog.close();
  await showHome();
});
keepLocalDraftButton.addEventListener("click", () => chooseConflictVersion("local"));
keepServerDraftButton.addEventListener("click", () => chooseConflictVersion("server"));
saveExitButton.addEventListener("click", saveAndExit);
summaryLibraryButton.addEventListener("click", showHome);
summaryResumeButton.addEventListener("click", resumeActiveSession);
reviewFullMapButton.addEventListener("click", () => {
  focusRoute.scrollIntoView({ behavior: "smooth", block: "start" });
  focusProgressCopy.textContent = "The complete confirmed route is shown in this panel.";
});
hideTimer.addEventListener("change", () => {
  timerContent.hidden = hideTimer.checked;
  window.localStorage.setItem("startframe_hide_timer", String(hideTimer.checked));
});
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
  if (state.session?.state === "start_action") startSaveStatus.textContent = "Offline · local copy kept";
  if (state.session?.state === "learning_concept") {
    if (window.location.hash.startsWith("#tutor/")) tutorDraftStatus.textContent = "Offline · local copy kept";
    else focusNoteStatus.textContent = "Offline · local copy kept";
    focusSaveStatus.textContent = "Offline";
  }
});
window.addEventListener("online", () => {
  connectionBanner.hidden = true;
  setUploadMessage("Connection restored. You can upload or retry now.", "success");
  if (state.session?.state === "start_action") saveDraftNow("start_action", startAnswer.value, startSaveStatus);
  if (state.session?.state === "learning_concept" && window.location.hash.startsWith("#tutor/")) {
    saveDraftNow("tutor", tutorInput.value, tutorDraftStatus);
  } else if (state.session?.state === "learning_concept") {
    saveDraftNow("focus_note", focusNote.value, focusNoteStatus);
  }
});

async function initialize() {
  connectionBanner.hidden = navigator.onLine;
  await Promise.all([checkRuntime(), loadSessions()]);
  if (!state.sessionId) return;
  const hash = window.location.hash;
  try {
    if (hash.startsWith("#setup/")) await showSetup();
    else if (hash.startsWith("#coverage/")) await showCoverage();
    else if (hash.startsWith("#path/")) await showPath();
    else if (hash.startsWith("#start/")) await showStartAction();
    else if (hash.startsWith("#tutor/")) await showTutor();
    else if (hash.startsWith("#focus/")) await showFocus();
    else if (hash.startsWith("#summary/")) {
      await showFocus();
      showSummary();
    }
    else if (hash.startsWith("#sources/")) await showSources();
  } catch (error) {
    await showSources();
    setUploadMessage(`${error.message} Your sources are still available.`, "error");
  }
}

initialize();
