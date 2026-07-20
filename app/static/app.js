const modeBadge = document.querySelector("#mode-badge");
const runtimeStatus = document.querySelector("#runtime-status");
const milestoneDialog = document.querySelector("#milestone-dialog");
const closeDialogButton = document.querySelector("#close-dialog");
const startButtons = document.querySelectorAll("#start-session, #empty-start");

function showMilestoneDialog() {
  if (typeof milestoneDialog.showModal === "function") {
    milestoneDialog.showModal();
  } else {
    runtimeStatus.textContent = "The foundation is ready. Material upload opens in the next milestone.";
  }
}

startButtons.forEach((button) => {
  button.addEventListener("click", showMilestoneDialog);
});

closeDialogButton.addEventListener("click", () => milestoneDialog.close());

milestoneDialog.addEventListener("click", (event) => {
  if (event.target === milestoneDialog) {
    milestoneDialog.close();
  }
});

async function checkRuntime() {
  try {
    const response = await fetch("/api/health", {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`health request returned ${response.status}`);
    }
    const health = await response.json();
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

checkRuntime();
