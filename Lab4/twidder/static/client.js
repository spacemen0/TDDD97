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
  showMessageBox("Someone else signed in to your account, you have been signed out")
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

function clearRegisterValidity() {
  let password = document.getElementById("password");
  let repeatPassword = document.getElementById("repeat-psw");
  password.setCustomValidity("");
  repeatPassword.setCustomValidity("");
}

function registerCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "201":
      showMessageBox("Sign up successfully");
      break;
    case "400":
      if (response.message == "Missing fields")
        showMessageBox("Please fill in all fields")
      else if (response.message == "Invalid password")
        showMessageBox("Password must be at least 8 digits")
      else showMessageBox("Incorrect email format")
      break
    case "409":
      showMessageBox("This email address has already be taken")
      break
    default:
      showMessageBox("Internal server error")

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
      registerCallback(responseData, xhr.status);
    }
  };
  let requestBody = JSON.stringify(dataObject);
  xhr.send(requestBody);
}

function clearLoginValidity() {
  let password = document.getElementById("password-login");
  password.setCustomValidity("");
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

function loginCallback(response, status) {
  status = status.toString();
  switch (status) {
    case "200":
      showMessageBox("Log in successfully");
      if (response.data !== "") localStorage.setItem("token", response.data);
      loadProfile(); startWebsocket();
      break;
    case "400":
      showMessageBox("Please fill in all fields");
      break;
    case "401":
      if (response.message == "User not exist")
        showMessageBox("User not exist, you may entered a wrong email");
      else showMessageBox("Incorrect password, please try again");
      break;
    default:
      showMessageBox("Internal server error");
  }
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
      loginCallback(responseData, xhr.status);
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

function clearOldPasswordValidity() {
  let password = document.getElementById("oldPassword");
  password.setCustomValidity("");
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

function changePasswordCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "200":
      showMessageBox("Password changed successfully");
      localStorage.removeItem("token");
      loadWelcome();
      break;
    case "400":
      if (response.message == "Missing fields")
        showMessageBox("Please fill in all fields");
      else showMessageBox("New password must be at least 8 digits")
      break;
    case "401":
      if (response.message == "User not exist")
        showMessageBox("The user associated with your token does not exist");
      else
        showMessageBox("Invalid or missing token");
      break;
    default:
      showMessageBox("Internal server error");
  }
}

function changePassword(event) {
  event.preventDefault();
  if (!validateOldPassword() || !validateRegister()) {
    return false;
  }
  let token = localStorage.getItem("token");
  let oldPassword = document.getElementById("oldPassword").value;
  let newPassword = document.getElementById("password").value;

  let dataObject = {
    oldpassword: oldPassword,
    newpassword: newPassword
  }

  let xhr = new XMLHttpRequest();
  xhr.open("PUT", server_url + "/change_password", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Authorization", token);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      changePasswordCallback(responseData, xhr.status);
    }
  };
  let requestBody = JSON.stringify(dataObject);
  xhr.send(requestBody);
}

function signOutCallback(status) {
  status = status.toString()
  switch (status) {
    case "204":
      showMessageBox("Signed out successfully");
      localStorage.removeItem("token");
      loadWelcome();
      if (socket.readyState == 1) socket.close()
      break;
    case "401":
      showMessageBox("Invalid or missing token");
      break;
    default:
      showMessageBox("Internal server error");
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
      signOutCallback(xhr.status);
    }
  };
  xhr.send();
}

function loadUserCallback(response, status) {

  status = status.toString()
  switch (status) {
    case "200":
      let user = response.data;
      localStorage.setItem("user", JSON.stringify(user));
      document.getElementById("user-info").innerHTML =
        "<strong>First Name:</strong> " +
        user[2] +
        "<br>" +
        "<strong>Last Name:</strong> " +
        user[3] +
        "<br>" +
        "<strong>Email:</strong> " +
        user[1] +
        "<br>" +
        "<strong>Gender:</strong> " +
        user[4] +
        "<br>" +
        "<strong>City:</strong> " +
        user[5] +
        "<br>" +
        "<strong>Country:</strong> " +
        user[6];
      break;
    case "401":
      if (response.message == "User not exist")
        showMessageBox("The user associated with your token does not exist");
      else
        showMessageBox("Invalid or missing token");
      break;
    default:
      showMessageBox("Internal server error");
  }
}

function loadUserInfo() {
  let token = localStorage.getItem("token");
  let xhr = new XMLHttpRequest();
  xhr.open("GET", server_url + "/get_user_data_by_token", true);
  xhr.setRequestHeader("Authorization", token);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      loadUserCallback(responseData, xhr.status);
    }
  };
  xhr.send();
}

function loadWallCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "200":
      let wall = response.data;
      let wallList = document.getElementById("wall");
      wallList.innerHTML = "";
      if (wall != NaN)
        wall.forEach(function (message) {
          wallList.innerHTML +=
            "<li><p>" + message.writer + ": " + message.content + "</p></li>";
        });
      break;
    case "401":
      showMessageBox("Invalid or missing token");
      break;
    default:
      showMessageBox("Internal server error");
  }
}

function loadWall() {
  let token = localStorage.getItem("token");
  let xhr = new XMLHttpRequest();
  xhr.open("GET", server_url + "/get_user_messages_by_token", true);
  xhr.setRequestHeader("Authorization", token);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      loadWallCallback(responseData, xhr.status);
    }
  };
  xhr.send();
}

function postMessageCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "201":
      loadWall();
      document.getElementById("post-message").value = "";
      break;
    case "400":
      if (response.message == "Empty message")
        showMessageBox("You entered an empty message");
      else showMessageBox("You entered an empty email address")
      break;
    case "401":
      if (response.message == "User not exist")
        showMessageBox("The user associated with your token does not exist");
      else
        showMessageBox("Invalid or missing token");
      break;
    default:
      showMessageBox("Internal server error");
  }
}
function postMessage() {
  let message = document.getElementById("post-message").value.trim();
  let email = JSON.parse(localStorage.getItem("user"))[1];
  let dataObject = {
    email: email,
    message, message
  }
  if (message !== "") {
    let token = localStorage.getItem("token");
    let xhr = new XMLHttpRequest();
    xhr.open("POST", server_url + "/post_message", true);
    xhr.setRequestHeader("Authorization", token);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
      if (xhr.readyState == 4) {
        let responseData = JSON.parse(xhr.responseText);
        console.log(responseData);
        postMessageCallback(responseData, xhr.status);
      }
    };
    let requestBody = JSON.stringify(dataObject);
    xhr.send(requestBody);
  } else {
    showMessageBox("Please enter a message.");
  }
}

function userDataCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "200":
      displayUser(response.data);
      break;
    case "401":
      showMessageBox("Invalid or missing token");
      clearBrowseData();
      break;
    case "404":
      showMessageBox("No such user")
      clearBrowseData();
      break
    default:
      showMessageBox("Internal server error");
      clearBrowseData();
  }
}

function browseUser() {
  let userEmail = document.getElementById("searching-email").value;
  let token = localStorage.getItem("token");
  let xhr = new XMLHttpRequest();
  xhr.open("GET", server_url + "/get_user_data_by_email/" + userEmail, true);
  xhr.setRequestHeader("Authorization", token);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      userDataCallback(responseData, xhr.status);
    }
  };
  xhr.send();


}

function clearBrowseData() {
  document.getElementById("search-feedback").innerHTML = "";
  document.getElementsByClassName("wall-wrapper")[0].innerHTML = "";
}

function searchResultCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "200":
      let messages = response.data;

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
      break;
    case "401":
      showMessageBox("Invalid or missing token");
      document.getElementById("search-feedback").innerHTML +=
        "<p>No messages found on this user's wall.</p>";
      break;
    case "404":
      showMessageBox("No such user")
      document.getElementById("search-feedback").innerHTML +=
        "<p>No messages found on this user's wall.</p>";
      break
    default:
      showMessageBox("Internal server error");
      document.getElementById("search-feedback").innerHTML +=
        "<p>No messages found on this user's wall.</p>";
  }
}

function displayUser(user) {
  document.getElementById("search-feedback").innerHTML =
    "<strong>First Name:</strong> " +
    user[2] +
    "<br>" +
    "<strong>Last Name:</strong> " +
    user[3] +
    "<br>" +
    "<strong>Email:</strong> " +
    user[1] +
    "<br>" +
    "<strong>Gender:</strong> " +
    user[4] +
    "<br>" +
    "<strong>City:</strong> " +
    user[5] +
    "<br>" +
    "<strong>Country:</strong> " +
    user[6];
  let token = localStorage.getItem("token");
  let xhr = new XMLHttpRequest();
  xhr.open("GET", server_url + "/get_user_messages_by_email/" + user[1], true);
  xhr.setRequestHeader("Authorization", token);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      searchResultCallback(responseData, xhr.status);
    }
  };
  xhr.send();

}

function postOthersMessageCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "201":
      browseUser();
      break;
    case "400":
      if (response.message == "Empty message")
        showMessageBox("You entered an empty message");
      else showMessageBox("You entered an empty email address")
      break;
    case "401":
      if (response.message == "User not exist")
        showMessageBox("The user associated with your token does not exist");
      else
        showMessageBox("Invalid or missing token");
      break;
    default:
      showMessageBox("Internal server error");
  }
}

function postOthersMessage() {
  let token = localStorage.getItem("token");
  let message = document.getElementById("post-notes").value;
  let sent = false;
  if (message !== "") {
    let email = document.getElementById("searching-email").value;
    let dataObject = {
      email: email,
      message: message
    }
    let xhr = new XMLHttpRequest();
    xhr.open("POST", server_url + "/post_message", true);
    xhr.setRequestHeader("Authorization", token);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
      if (xhr.readyState == 4) {
        let responseData = JSON.parse(xhr.responseText);
        console.log(responseData);
        postOthersMessageCallback(responseData, xhr.status);
      }
    };
    let requestBody = JSON.stringify(dataObject);
    xhr.send(requestBody);
    sent = true;
  } else {
    if (!sent)
      showMessageBox("Please enter a message.");
  }

}

function recoverPasswordCallback(response, status) {
  status = status.toString()
  switch (status) {
    case "200":
      showMessageBox("Password recovery email successfully sent, please check your mailbox")
      break;
    case "404":
      showMessageBox("You entered an wrong email address")
      break;
    default:
      showMessageBox("Internal server error");
  }
}

function recoverPassword() {
  let email = document.getElementById("email-login").value;

  let dataObject = {
    email: email
  };

  let xhr = new XMLHttpRequest();
  xhr.open("POST", server_url + "/send_recover_email", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      let responseData = JSON.parse(xhr.responseText);
      console.log(responseData);
      recoverPasswordCallback(responseData, xhr.status);
    }
  };
  let requestBody = JSON.stringify(dataObject);
  xhr.send(requestBody);
}
