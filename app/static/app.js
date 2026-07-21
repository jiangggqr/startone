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
  runtimeMode: "demo",
};

const views = {
  home: document.querySelector("#home-view"),
  sources: document.querySelector("#source-view"),
  setup: document.querySelector("#setup-view"),
  coverage: document.querySelector("#coverage-view"),
  path: document.querySelector("#path-view"),
  start: document.querySelector("#start-action-view"),
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
const saveStartAnswerButton = document.querySelector("#save-start-answer");
const startSaveLaterButton = document.querySelector("#start-save-later");
const startBackMapButton = document.querySelector("#start-back-map");

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
    if (session.state === "start_action") {
      await showStartAction();
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
      : "← Back to library";
  showView("sources", `sources/${state.sessionId}`, sourceTitle);
  await Promise.all([loadSources(), getCurrentSession()]);
}

async function showHome(event) {
  if (event) event.preventDefault();
  window.clearTimeout(state.pollTimer);
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
  const returnTo = window.location.hash.startsWith("#path/") ? "path" : "coverage";
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
  const body = existing || await api(`/api/sessions/${state.sessionId}/path`);
  state.knowledgeMap = body;
  const action = body.knowledge_map.start_action;
  startPageTitle.textContent = action.title;
  startPageInstruction.textContent = action.instruction;
  startPageCondition.textContent = action.completion_condition;
  startDuration.textContent = `About ${action.estimated_seconds} seconds`;
  startAnswer.value = window.localStorage.getItem(startDraftKey()) || "";
  setMessage(startMessage, startAnswer.value ? "Your unfinished answer was restored from this device." : "");
  showView("start", `start/${state.sessionId}`, startPageTitle);
}

function saveStartDraft() {
  window.localStorage.setItem(startDraftKey(), startAnswer.value);
}

function saveStartPoint() {
  const answer = startAnswer.value.trim();
  if (!answer) {
    setMessage(startMessage, "Write one checkable sentence before saving this starting point.", "error");
    startAnswer.focus();
    return;
  }
  saveStartDraft();
  setMessage(startMessage, "Starting point saved on this device. It will carry into the focus session.", "success");
  saveStartAnswerButton.textContent = "Starting point saved";
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
startSaveLaterButton.addEventListener("click", showHome);
startBackMapButton.addEventListener("click", showPath);

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
});
window.addEventListener("online", () => {
  connectionBanner.hidden = true;
  setUploadMessage("Connection restored. You can upload or retry now.", "success");
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
    else if (hash.startsWith("#sources/")) await showSources();
  } catch (error) {
    await showSources();
    setUploadMessage(`${error.message} Your sources are still available.`, "error");
  }
}

initialize();
