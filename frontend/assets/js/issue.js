const errorBox = document.getElementById("errorBox");
const logoutBtn = document.getElementById("logoutBtn");
const saveStatusBtn = document.getElementById("saveStatusBtn");
const statusSelect = document.getElementById("statusSelect");
const commentForm = document.getElementById("commentForm");
const commentsList = document.getElementById("commentsList");

const issueTitle = document.getElementById("issueTitle");
const issueMeta = document.getElementById("issueMeta");
const issueSeverity = document.getElementById("issueSeverity");
const issueDescription = document.getElementById("issueDescription");
const backLink = document.getElementById("backLink");

const params = new URLSearchParams(window.location.search);
const issueId = params.get("id");

let currentIssue = null;

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("d-none");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("d-none");
}

function renderIssue(issue) {
  currentIssue = issue;

  issueTitle.textContent = issue.title;
  issueMeta.textContent = `Issue #${issue.id} • Workspace ${issue.workspace_id} • Autor ${issue.created_by_id}`;
  issueSeverity.textContent = issue.severity;
  issueDescription.textContent = issue.description || "Bez popisu";
  statusSelect.value = issue.status;
  backLink.href = `./workspace.html?id=${issue.workspace_id}`;
}

function renderComments(items) {
  commentsList.innerHTML = "";

  if (!items.length) {
    commentsList.innerHTML = `<div class="alert alert-secondary mb-0">Zatiaľ tu nie sú žiadne komentáre.</div>`;
    return;
  }

  items.forEach((comment) => {
    const div = document.createElement("div");
    div.className = "border rounded p-3 bg-white";

    div.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong>User ${comment.author_id}</strong>
        <span class="text-muted small">${new Date(comment.created_at).toLocaleString()}</span>
      </div>
      <div>${comment.content}</div>
    `;

    commentsList.appendChild(div);
  });
}

async function loadPage() {
  if (!issueId) {
    showError("Chýba issue id v URL.");
    return;
  }

  try {
    clearError();
    await authMe();

    const issue = await getIssue(issueId);
    renderIssue(issue);

    const comments = await getComments(issueId);
    renderComments(comments);
  } catch (err) {
    if (err.message === "Neprihlásený používateľ") {
      window.location.href = "../index.html";
      return;
    }
    showError(err.message);
  }
}

saveStatusBtn.addEventListener("click", async () => {
  try {
    clearError();
    await updateIssue(issueId, { status: statusSelect.value });

    const issue = await getIssue(issueId);
    renderIssue(issue);
  } catch (err) {
    showError(err.message);
  }
});

commentForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    clearError();

    const content = document.getElementById("commentContent").value.trim();
    await createComment(issueId, content);

    commentForm.reset();

    const comments = await getComments(issueId);
    renderComments(comments);
  } catch (err) {
    showError(err.message);
  }
});

logoutBtn.addEventListener("click", async () => {
  await logout();
  window.location.href = "../index.html";
});

loadPage();