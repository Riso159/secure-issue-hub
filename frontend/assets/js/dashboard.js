const workspaceList = document.getElementById("workspaceList");
const workspaceForm = document.getElementById("workspaceForm");
const workspaceNameInput = document.getElementById("workspaceName");
const logoutBtn = document.getElementById("logoutBtn");
const errorBox = document.getElementById("errorBox");

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("d-none");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("d-none");
}

function renderWorkspaces(items) {
  workspaceList.innerHTML = "";

  if (!items.length) {
    workspaceList.innerHTML = `<div class="list-group-item">Zatiaľ nemáš žiadny workspace.</div>`;
    return;
  }

  items.forEach((ws) => {
    const a = document.createElement("a");
    a.href = `./workspace.html?id=${ws.id}`;
    a.className = "list-group-item list-group-item-action";
    a.innerHTML = `
      <div class="d-flex justify-content-between align-items-center">
        <strong>${ws.name}</strong>
        <span class="badge bg-secondary">owner: ${ws.owner_id}</span>
      </div>
    `;
    workspaceList.appendChild(a);
  });
}

async function loadPage() {
  try {
    clearError();
    await authMe();
    const items = await getWorkspaces();
    renderWorkspaces(items);
  } catch (err) {
    window.location.href = "../index.html";
  }
}

workspaceForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    clearError();
    await createWorkspace(workspaceNameInput.value.trim());
    workspaceNameInput.value = "";
    const items = await getWorkspaces();
    renderWorkspaces(items);
  } catch (err) {
    showError(err.message);
  }
});

logoutBtn.addEventListener("click", async () => {
  await logout();
  window.location.href = "../index.html";
});

loadPage();