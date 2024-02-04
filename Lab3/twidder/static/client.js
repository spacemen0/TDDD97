const server_url = "http://127.0.0.1:8000";
const socket_url = "ws://127.0.0.1:8000/sock";
let socket;
window.onload = function () {
  if (localStorage.getItem("token")) {
    loadProfile();
  } else {
    loadWelcome();
  }
};

function loadWelcome() {
  let main = document.getElementById("main");
  let welcome = document.getElementById("welcome");
  main.innerHTML = welcome.innerHTML;
}

function loadProfile() {
  let main = document.getElementById("main");
  let profile = document.getElementById("profile");
  main.innerHTML = profile.innerHTML;
}
function clearLoginValidity() {
  let password = document.getElementById("password-login");
  password.setCustomValidity("");
}
function clearRegisterValidity() {
  let password = document.getElementById("password");
  let repeatPassword = document.getElementById("repeat-psw");
  password.setCustomValidity("");
  repeatPassword.setCustomValidity("");
}

function validateRegister() {
  let password = document.getElementById("password");
  let repeatPassword = document.getElementById("repeat-psw");

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

function showMessageBox(message) {
  var modal = document.getElementById("message-box");
  var messageText = document.getElementById("message-text");

  messageText.textContent = message;
  modal.style.display = "block";
}

function closeMessageBox() {
  var modal = document.getElementById("message-box");
  modal.style.display = "none";
}

function ManuallyLogOut() {
  localStorage.removeItem("token");
  loadWelcome();
}

function startWebsocket() {
  socket = new WebSocket(socket_url);
  socket.addEventListener("message", (ev) => {
    if (ev.data === "Log Out") ManuallyLogOut();
  });
  socket.send(localStorage.getItem("token"));
}

function profileCallback(response, token) {
  if (response.success) {
    console.log(response.message);
    if (token !== "") localStorage.setItem("token", token);
    loadProfile();
    startWebsocket();
  } else {
    let errorMessage = response.message;
    showMessageBox(errorMessage);
  }
}

function register(event) {
  event.preventDefault();
  if (!validateRegister()) {
    return false;
  }

  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;
  let firstName = document.getElementById("first-name").value;
  let familyName = document.getElementById("family-name").value;
  let gender = document.getElementById("gender").value;
  let city = document.getElementById("city").value;
  let country = document.getElementById("country").value;

  let dataObject = {
    email: email,
    password: password,
    firstname: firstName,
    familyname: familyName,
    gender: gender,
    city: city,
    country: country,
  };

  var xhr = new XMLHttpRequest();
  xhr.open("POST", server_url + "/sign_up", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      var responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      const authorizationHeader = xhr.getResponseHeader("Authorization");
      let token = "";
      if (authorizationHeader && authorizationHeader.startsWith("Bearer ")) {
        token = authorizationHeader.slice(7);
      }
      profileCallback(responseData, token);
    }
  };
  var requestBody = JSON.stringify(dataObject);
  xhr.send(requestBody);
}

function validateLogin() {
  let password = document.getElementById("password-login");
  if (password.value.length < 8) {
    password.setCustomValidity("Password must be at least 8 characters long");
    password.reportValidity();
    return false;
  } else {
    password.setCustomValidity("");
  }
  return true;
}
function login(event) {
  event.preventDefault();
  if (!validateLogin()) {
    return false;
  }

  let email = document.getElementById("email-login").value;
  let password = document.getElementById("password-login").value;
  let dataObject = {
    email: email,
    password: password,
  };

  var xhr = new XMLHttpRequest();
  xhr.open("POST", server_url + "/sign_in", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      var responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      const authorizationHeader = xhr.getResponseHeader("Authorization");
      let token = "";
      if (authorizationHeader && authorizationHeader.startsWith("Bearer ")) {
        token = authorizationHeader.slice(7);
      }
      profileCallback(responseData, token);
    }
  };
  var requestBody = JSON.stringify(dataObject);
  xhr.send(requestBody);
}

function showTab(tabId) {
  var tabs = document.getElementsByClassName("tabs");
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].classList.remove("active-tab");
  }

  document.getElementById(tabId).classList.add("active-tab");
}
