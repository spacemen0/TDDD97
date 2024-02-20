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
  console.log(dataObject);
  let signUpResult = serverstub.signUp(dataObject);

  if (signUpResult.success) {
    console.log(signUpResult.message);
    showMessageBox(signUpResult.message);
  } else {
    let errorMessage = signUpResult.message;
    showMessageBox(errorMessage);
  }
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

  let signInResult = serverstub.signIn(email, password);

  if (signInResult.success) {
    console.log(signInResult.message);
    localStorage.setItem("token", JSON.stringify(signInResult.data));
    loadProfile();
  } else {
    let errorMessage = signInResult.message;
    console.log(errorMessage);
    showMessageBox(errorMessage);
  }
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
  let token = JSON.parse(localStorage.getItem("token"));
  let oldPassword = document.getElementById("oldPassword").value;
  let newPassword = document.getElementById("password").value;

  let changeResult = serverstub.changePassword(token, oldPassword, newPassword);
  showMessageBox(changeResult.message);
}

function signOut(event) {
  event.preventDefault();
  let token = JSON.parse(localStorage.getItem("token"));
  let signOutResult = serverstub.signOut(token);
  localStorage.setItem("token", "");
  console.log(token);
  if (signOutResult.success) {
    loadWelcome();
  } else {
    showMessageBox(signOutResult.message);
  }
}


function loadUserInfo() {
  let token = JSON.parse(localStorage.getItem("token"));
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
  let token = JSON.parse(localStorage.getItem("token"));
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
    let token = JSON.parse(localStorage.getItem("token"));
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
  let token = JSON.parse(localStorage.getItem("token"));
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
  let token = JSON.parse(localStorage.getItem("token"));
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
  let token = JSON.parse(localStorage.getItem("token"));
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

