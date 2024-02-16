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
  reloadWall();
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
  var modal = document.getElementById("message-box");
  var messageText = document.getElementById("message-text");

  messageText.textContent = message;
  modal.style.display = "block";
}

function closeMessageBox() {
  var modal = document.getElementById("message-box");
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
  var tabs = document.getElementsByClassName("tabs");
  for (var i = 0; i < tabs.length; i++) {
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
  var token = JSON.parse(localStorage.getItem("token"));
  var oldPassword = document.getElementById("oldPassword").value;
  var newPassword = document.getElementById("password").value;

  var changeResult = serverstub.changePassword(token, oldPassword, newPassword);
  displayMessage(changeResult.message, "change");
}

function signOut(event) {
  event.preventDefault();
  var token = JSON.parse(localStorage.getItem("token"));
  var signOutResult = serverstub.signOut(token);
  localStorage.setItem("token", "");
  console.log(token);
  if (signOutResult.success) {
    loadWelcome();
  } else {
    displayMessage(signOutResult.message, "change");
  }
}

function displayMessage(message, method) {
  var messageElement = document.getElementById(method + "-message");
  messageElement.textContent = message;
}

function loadUserInfo() {
  var token = JSON.parse(localStorage.getItem("token"));
  var userInfo = serverstub.getUserDataByToken(token);
  if (userInfo.success) {
    var user = userInfo.data;
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
  var token = JSON.parse(localStorage.getItem("token"));
  var wallInfo = serverstub.getUserMessagesByToken(token);
  if (wallInfo.success) {
    var wall = wallInfo.data;
    var wallList = document.getElementById("wall");
    wallList.innerHTML = "";
    wall.forEach(function (message) {
      wallList.innerHTML +=
        "<li><p>" + message.writer + ": " + message.content + "</p></li>";
    });
  }
}

function postMessage() {
  var message = document.getElementById("post-message").value.trim();
  if (message !== "") {
    var token = JSON.parse(localStorage.getItem("token"));
    var postResult = serverstub.postMessage(token, message);
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

function reloadWall() {
  loadWall();
}

function browseUser() {
  var userEmail = document.getElementById("searching-email").value;
  var token = JSON.parse(localStorage.getItem("token"));
  var userData = serverstub.getUserDataByEmail(token, userEmail);

  if (userData.success) {
    displayUser(userData.data);
  } else {
    document.getElementById("search-feedback").textContent = userData.message;
    clearBrowseData();
  }
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
  var token = JSON.parse(localStorage.getItem("token"));
  var searchResult = serverstub.getUserMessagesByEmail(token, user.email);
  if (searchResult.success) {
    var messages = searchResult.data;
    var wallHTML = "<h3>Wall Messages:</h3><ul>";
    messages.forEach(function (message) {
      wallHTML += "<li><p>" + message.writer + ": " + message.content + "</p></li>";
    });
    wallHTML += "</ul>";
    document.getElementById("search-feedback").innerHTML += wallHTML;

    var postMessageForm = `
        <h3>Post a Message:</h3>
        <textarea id="post-message" rows="4" cols="20"></textarea><br>
        <button onclick="postOthersMessage()">Post</button>
    `;
    document.getElementById("search-feedback").innerHTML += postMessageForm;
  } else {
    document.getElementById("search-feedback").innerHTML +=
      "<p>No messages found on this user's wall.</p>";
  }
}

function postOthersMessage() {
  var token = JSON.parse(localStorage.getItem("token"));
  var message = document.getElementById("post-message").value.trim();
  if (message !== "") {
    var email = document.getElementById("searching-email").value;
    var posted = serverstub.postMessage(token, message, email);

    if (posted.success) {
    } else {
      showMessageBox(postResult.message);
    }
  } else {
    showMessageBox("Please enter a message.");
  }
}
