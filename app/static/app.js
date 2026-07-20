const state = {
  sessionId: window.localStorage.getItem("startframe_session_id"),
  sources: [],
  selectedSourceId: null,
  selectedSource: null,
  selectedChunkIndex: 0,
  deleteTarget: null,
  pollTimer: null,
};

const modeBadge = document.querySelector("#mode-badge");
const runtimeStatus = document.querySelector("#runtime-status");
const homeView = document.querySelector("#home-view");
const sourceView = document.querySelector("#source-view");
const sourceTitle = document.querySelector("#sources-title");
const startButtons = document.querySelectorAll("#start-session, #empty-start");
const libraryLink = document.querySelector("#library-link");
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

function setUploadMessage(message, kind = "info") {
  uploadMessage.textContent = message;
  uploadMessage.dataset.kind = kind;
  uploadMessage.hidden = !message;
}

function setButtonBusy(button, busy, busyText, readyText) {
  button.disabled = busy;
  button.textContent = busy ? busyText : readyText;
  button.setAttribute("aria-busy", String(busy));
}

async function checkRuntime() {
  try {
    const health = await api("/api/health");
    const isDemo = health.mode === "demo";
    modeBadge.textContent = isDemo ? "Demo mode" : "Live model mode";
    modeBadge.dataset.mode = health.mode;
    runtimeStatus.textContent = `Service healthy · ${isDemo ? "Demo" : "Live model"} mode · Database schema ${health.schema_version}`;
  } catch (error) {
    modeBadge.textContent = "Service offline";
    modeBadge.dataset.mode = "offline";
    runtimeStatus.textContent = "Could not reach the service. Refresh to retry; page content remains available.";
  }
}

async function beginSession() {
  const buttons = [...startButtons];
  buttons.forEach((button) => setButtonBusy(button, true, "Creating session…", button.dataset.readyText || button.textContent));
  try {
    const body = await api("/api/sessions", { method: "POST" });
    state.sessionId = body.session.id;
    window.localStorage.setItem("startframe_session_id", state.sessionId);
    await showSources();
  } catch (error) {
    runtimeStatus.textContent = `${error.message} Nothing was changed. Try again.`;
  } finally {
    buttons.forEach((button) => {
      const readyText = button.id === "empty-start" ? "Start your first session" : "Upload material and start a session";
      setButtonBusy(button, false, "", readyText);
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
    const resume = element("button", "button button-secondary", "Continue adding sources");
    resume.type = "button";
    resume.addEventListener("click", async () => {
      state.sessionId = session.id;
      window.localStorage.setItem("startframe_session_id", state.sessionId);
      await showSources();
    });
    item.append(copy, resume);
    recentList.append(item);
  });
}

async function showSources() {
  if (!state.sessionId) {
    await beginSession();
    return;
  }
  homeView.hidden = true;
  sourceView.hidden = false;
  window.location.hash = `sources/${state.sessionId}`;
  sourceTitle.focus();
  await loadSources();
}

async function showHome(event) {
  if (event) event.preventDefault();
  window.clearTimeout(state.pollTimer);
  homeView.hidden = false;
  sourceView.hidden = true;
  window.location.hash = "library";
  document.querySelector("#hero-title").focus({ preventScroll: true });
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

async function selectSource(sourceId) {
  try {
    const body = await api(`/api/sources/${sourceId}`);
    state.selectedSourceId = sourceId;
    state.selectedSource = body.source;
    state.selectedChunkIndex = 0;
    renderPreview();
  } catch (error) {
    setUploadMessage(`${error.message} Select another source or retry this one.`, "error");
  }
}

function chunkLocation(source, chunk) {
  if (source.media_kind === "pdf") {
    return `Page ${chunk.page_number} · excerpt ${chunk.page_chunk_index}`;
  }
  if (source.media_kind === "pasted") {
    return `Paragraph ${chunk.paragraph_number} · characters ${chunk.start_char}–${chunk.end_char}`;
  }
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

startButtons.forEach((button) => button.addEventListener("click", beginSession));
libraryLink.addEventListener("click", showHome);
backHomeButton.addEventListener("click", showHome);
saveForLaterButton.addEventListener("click", showHome);
chooseFilesButton.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => uploadFiles(fileInput.files));
openPasteButton.addEventListener("click", () => pasteDialog.showModal());
cancelPasteButton.addEventListener("click", () => pasteDialog.close());
pasteForm.addEventListener("submit", submitPastedSource);
cancelDeleteButton.addEventListener("click", () => deleteDialog.close());
confirmDeleteButton.addEventListener("click", deleteSelectedSource);

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
  if (window.location.hash.startsWith("#sources/") && state.sessionId) {
    await showSources();
  }
}

initialize();
