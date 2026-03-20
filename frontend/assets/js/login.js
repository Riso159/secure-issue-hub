const loginForm = document.getElementById("loginForm");
const errorBox = document.getElementById("errorBox");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  errorBox.classList.add("d-none");
  errorBox.textContent = "";

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    await login(email, password);
    window.location.href = "./pages/dashboard.html";
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.remove("d-none");
  }
});