const issuesList = document.getElementById("issuesList");
const issueForm = document.getElementById("issueForm");
const logoutBtn = document.getElementById("logoutBtn");
const errorBox = document.getElementById("errorBox");

const params = new URLSearchParams(window.location.search);
const workspaceId = params.get("id");

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("d-none");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("d-none");
}

function renderIssues(items) {
  issuesList.innerHTML = "";

  if (!items.length) {
    issuesList.innerHTML = `<div class="col-12"><div class="alert alert-secondary">Zatiaľ tu nie sú žiadne issues.</div></div>`;
    return;
  }

  items.forEach((issue) => {items.forEach((issue) => {
  const col = document.createElement("div");
  col.className = "col-md-6";

  col.innerHTML = `
    <a href="./issue.html?id=${issue.id}" class="text-decoration-none text-dark">
      <div class="card h-100 shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h2 class="h5">${issue.title}</h2>
            <span class="badge bg-dark">${issue.severity}</span>
          </div>
          <p class="text-muted small mb-2">Status: ${issue.status}</p>
          <p class="mb-0">${issue.description || ""}</p>
        </div>
      </div>
    </a>
  `;

  issuesList.appendChild(col);
});
});
}

async function loadPage() {
  if (!workspaceId) {
    showError("Chýba workspace id v URL.");
    return;
  }

  try {
    clearError();
    await authMe();
    const items = await getIssues(workspaceId);
    renderIssues(items);
  } catch (err) {
    if (err.message === "Neprihlásený používateľ") {
      window.location.href = "../index.html";
      return;
    }
    showError(err.message);
  }
}

issueForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    clearError();

    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const severity = document.getElementById("severity").value;

    await createIssue(workspaceId, title, description, severity);

    issueForm.reset();
    document.getElementById("severity").value = "MEDIUM";

    const items = await getIssues(workspaceId);
    renderIssues(items);
  } catch (err) {
    showError(err.message);
  }
});

logoutBtn.addEventListener("click", async () => {
  await logout();
  window.location.href = "../index.html";
});

loadPage();