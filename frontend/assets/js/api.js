const API_BASE = "http://127.0.0.1:8000";

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    throw new Error("Neprihlásený používateľ");
  }

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? data.detail
        : "Request failed";
    throw new Error(detail);
  }

  return data;
}

async function getCsrfToken() {
  const data = await apiFetch("/auth/csrf", {
    method: "GET",
    headers: {},
  });
  return data.csrf;
}

async function authMe() {
  return apiFetch("/auth/me", {
    method: "GET",
    headers: {},
  });
}

async function login(email, password) {
  return apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

async function logout() {
  const csrf = await getCsrfToken();
  return apiFetch("/auth/logout", {
    method: "POST",
    headers: {
      "X-CSRF-Token": csrf,
    },
  });
}

async function getWorkspaces() {
  return apiFetch("/workspaces", {
    method: "GET",
    headers: {},
  });
}

async function createWorkspace(name) {
  const csrf = await getCsrfToken();
  return apiFetch("/workspaces", {
    method: "POST",
    headers: {
      "X-CSRF-Token": csrf,
    },
    body: JSON.stringify({ name }),
  });
}

async function getIssues(workspaceId) {
  return apiFetch(`/workspaces/${workspaceId}/issues`, {
    method: "GET",
    headers: {},
  });
}

async function createIssue(workspaceId, title, description, severity) {
  const csrf = await getCsrfToken();
  return apiFetch(`/workspaces/${workspaceId}/issues`, {
    method: "POST",
    headers: {
      "X-CSRF-Token": csrf,
    },
    body: JSON.stringify({ title, description, severity }),
  });
}
async function getIssue(issueId) {
  return apiFetch(`/issues/${issueId}`, {
    method: "GET",
    headers: {},
  });
}

async function getComments(issueId) {
  return apiFetch(`/issues/${issueId}/comments`, {
    method: "GET",
    headers: {},
  });
}

async function createComment(issueId, content) {
  const csrf = await getCsrfToken();
  return apiFetch(`/issues/${issueId}/comments`, {
    method: "POST",
    headers: {
      "X-CSRF-Token": csrf,
    },
    body: JSON.stringify({ content }),
  });
}

async function updateIssue(issueId, payload) {
  const csrf = await getCsrfToken();
  return apiFetch(`/issues/${issueId}`, {
    method: "PATCH",
    headers: {
      "X-CSRF-Token": csrf,
    },
    body: JSON.stringify(payload),
  });
}