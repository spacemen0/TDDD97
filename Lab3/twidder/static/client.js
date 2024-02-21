const server_url = "http://127.0.0.1:5000";
const socket_url = "ws://127.0.0.1:5000/sock";
let socket;
window.onload = function () {
  if (localStorage.getItem("token")) {
    loadProfile();
    startWebsocket();
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
  loadUserInfo();
  loadWall();
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
function clearOldPasswordValidity(event) {
  let password = document.getElementById("oldPassword");
  password.setCustomValidity("");
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
  let modal = document.getElementById("message-box");
  let messageText = document.getElementById("message-text");

  messageText.textContent = message;
  modal.style.display = "block";
}

function closeMessageBox() {
  let modal = document.getElementById("message-box");
  modal.style.display = "none";
}

function ForceSignOut() {
  localStorage.removeItem("token");
  console.log("ForceSignOut");
  loadWelcome();
  if (socket.readyState == 1) socket.close();
}

function startWebsocket() {
  if (!localStorage.getItem("token")) return;
  socket = new WebSocket(socket_url);
  socket.addEventListener("message", (ev) => {
    if (ev.data === "Log Out") ForceSignOut();
  });
  socket.onopen = (event) => {
    if (socket.readyState == 1)
      socket.send(localStorage.getItem("token"));
  };
};

function profileCallback(response, token, load = false) {
  if (response.success) {
    showMessageBox(response.message);
    if (token !== "") localStorage.setItem("token", token);
    if (load) { loadProfile(); startWebsocket(); };
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
  let xhr = new XMLHttpRequest();
  xhr.open("POST", server_url + "/sign_up", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      const authorizationHeader = xhr.getResponseHeader("Authorization");
      let token = "";
      token = authorizationHeader;
      profileCallback(responseData, token);
    }
  };
  let requestBody = JSON.stringify(dataObject);
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
    username: email,
    password: password,
  };

  let xhr = new XMLHttpRequest();
  xhr.open("POST", server_url + "/sign_in", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      let token = "";
      token = responseData.data;
      profileCallback(responseData, token, true);
    }
  };
  let requestBody = JSON.stringify(dataObject);
  xhr.send(requestBody);
}

function showTab(tabId) {
  let tabs = document.getElementsByClassName("tabs");
  for (let i = 0; i < tabs.length; i++) {
    tabs[i].classList.remove("active-tab");
  }

  document.getElementById(tabId).classList.add("active-tab");
}

function validateOldPassword() {
  let password = document.getElementById("oldPassword");
  if (password.value.length < 8) {
    password.setCustomValidity("Password must be at least 8 characters long");
    password.reportValidity();
    return false;
  } else {
    password.setCustomValidity("");
  }
  return true;
}

function changePassword(event) {
  event.preventDefault();
  if (!validateOldPassword() || !validateRegister()) {
    return false;
  }
  let token = localStorage.getItem("token");
  let oldPassword = document.getElementById("oldPassword").value;
  let newPassword = document.getElementById("password").value;

  let changeResult = serverstub.changePassword(token, oldPassword, newPassword);
  displayMessage(changeResult.message, "change");
}

function signOutCallback(response) {
  if (response.success) {
    showMessageBox(response.message);
    localStorage.removeItem("token");
    loadWelcome();
  } else {
    let errorMessage = response.message;
    showMessageBox(errorMessage);
  }
}
function signOut(event) {
  event.preventDefault();

  let xhr = new XMLHttpRequest();
  xhr.open("DELETE", server_url + "/sign_out", true);
  let token = localStorage.getItem("token");
  xhr.setRequestHeader("Authorization", token);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      signOutCallback(responseData);
    }
  };
  xhr.send();
}


function loadUserInfo() {
  let token = localStorage.getItem("token");
  let userInfo = serverstub.getUserDataByToken(token);
  if (userInfo.success) {
    let user = userInfo.data;
    document.getElementById("user-info").innerHTML =
      "<strong>First Name:</strong> " +
      user.firstname +
      "<br>" +
      "<strong>Last Name:</strong> " +
      user.familyname +
      "<br>" +
      "<strong>Email:</strong> " +
      user.email +
      "<br>" +
      "<strong>Gender:</strong> " +
      user.gender +
      "<br>" +
      "<strong>City:</strong> " +
      user.city +
      "<br>" +
      "<strong>Country:</strong> " +
      user.country;
  }
}

function loadWall() {
  let token = localStorage.getItem("token");
  let wallInfo = serverstub.getUserMessagesByToken(token);
  if (wallInfo.success) {
    let wall = wallInfo.data;
    let wallList = document.getElementById("wall");
    wallList.innerHTML = "";
    wall.forEach(function (message) {
      wallList.innerHTML +=
        "<li><p>" + message.writer + ": " + message.content + "</p></li>";
    });
  }
}

function postMessage() {
  let message = document.getElementById("post-message").value.trim();
  if (message !== "") {
    let token = localStorage.getItem("token");
    let postResult = serverstub.postMessage(token, message);
    if (postResult.success) {
      loadWall();
      document.getElementById("post-message").value = "";
    } else {
      showMessageBox(postResult.message);
    }
  } else {
    showMessageBox("Please enter a message.");
  }
}


function browseUser() {
  let userEmail = document.getElementById("searching-email").value;
  let token = localStorage.getItem("token");
  let userData = serverstub.getUserDataByEmail(token, userEmail);

  if (userData.success) {
    displayUser(userData.data);
  } else {
    showMessageBox(userData.message);
    clearBrowseData();
  }
}

function clearBrowseData() {
  document.getElementById("search-feedback").innerHTML = "";
  document.getElementsByClassName("wall-wrapper")[0].innerHTML = "";
}

function displayUser(user) {
  document.getElementById("search-feedback").innerHTML =
    "<strong>First Name:</strong> " +
    user.firstname +
    "<br>" +
    "<strong>Last Name:</strong> " +
    user.familyname +
    "<br>" +
    "<strong>Email:</strong> " +
    user.email +
    "<br>" +
    "<strong>Gender:</strong> " +
    user.gender +
    "<br>" +
    "<strong>City:</strong> " +
    user.city +
    "<br>" +
    "<strong>Country:</strong> " +
    user.country;
  let token = localStorage.getItem("token");
  let searchResult = serverstub.getUserMessagesByEmail(token, user.email);
  if (searchResult.success) {
    let messages = searchResult.data;

    let postMessageForm = `
    <h3>Post a Message:</h3>
    <textarea id="post-notes" rows="4" cols="20"></textarea><br>
    <button onclick="postOthersMessage()">Post</button>
    <button onclick="reloadPost()">Reload</button>
`;
    document.getElementById("search-feedback").innerHTML += postMessageForm;

    let wallHTML = `<div id="wall-wrapper"><h3>Wall Messages:</h3><ul id="wall">`;
    messages.forEach(function (message) {
      wallHTML +=
        "<li><p>" + message.writer + ": " + message.content + "</p></li>";
    });
    wallHTML += "</ul></div>";
    document.getElementsByClassName("wall-wrapper")[0].innerHTML = "<div id='otherwall'></div>";
    document.getElementById("otherwall").innerHTML = wallHTML;
  } else {
    document.getElementById("search-feedback").innerHTML +=
      "<p>No messages found on this user's wall.</p>";
  }
}

function postOthersMessage() {
  let token = localStorage.getItem("token");
  let message = document.getElementById("post-notes").value;
  if (message !== "") {
    let email = document.getElementById("searching-email").value;
    let posted = serverstub.postMessage(token, message, email);

    if (posted.success) {
      browseUser();
    } else {
      showMessageBox(postResult.message);
    }
  } else {
    showMessageBox("Please enter a message.");
  }
}

