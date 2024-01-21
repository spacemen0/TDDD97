window.onload = function () {
  let main = document.getElementById("main");
  let welcome = document.getElementById("welcome");
  main.innerHTML = welcome.innerHTML;
};
function clearValidity() {
  let password = document.getElementById("password");
  let repeatPassword = document.getElementById("repeat-psw");
  password.setCustomValidity("");
  repeatPassword.setCustomValidity("");
}

function validateLogin() {
  let password = document.getElementById("password-login");
  password.setCustomValidity("");
  if (password.value.length < 8) {
    password.setCustomValidity("Password must be at least 8 characters long");
    password.reportValidity();
    return false;
  } else {
    password.setCustomValidity("");
  }
  return true;
}

function validateRegister() {
  let password = document.getElementById("password");
  let repeatPassword = document.getElementById("repeat-psw");
  password.setCustomValidity("");

  if (password.value.length < 8) {
    password.setCustomValidity("Password must be at least 8 characters long");
    password.reportValidity();
    return false;
  } else {
    password.setCustomValidity("");
  }

  if (password.value !== repeatPassword.value) {
    repeatPassword.setCustomValidity("Passwords do not match");
    repeatPassword.reportValidity();
    return false;
  } else {
    repeatPassword.setCustomValidity("");
  }
  return true;
}

function register(event) {
  event.preventDefault();
  if (!validateRegister()) {
    return false;
  }
  let form = document.getElementById("register-form");
  form.reset();
  return true;
}

function login(event) {
  event.preventDefault();
  if (!validateLogin()) {
    return false;
  }
  let form = document.getElementById("login-form");
  form.reset();
  return true;
}
