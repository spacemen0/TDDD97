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
    loadProfile();
  } else {
    let errorMessage = signUpResult.message;
    console.log(errorMessage);
    // Display error message to the user
    // document.getElementById("error-message").innerText = errorMessage;
  }
}

function login(event) {
  event.preventDefault();
  if (!validateLogin()) {
    return false;
  }

  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;

  let signInResult = serverstub.signIn(email, password);

  if (signInResult.success) {
    console.log(signInResult.message);
    // Store the token at client-side
    localStorage.setItem("token", signInResult.data);
    // Call the function to decide which view to display
    loadProfile();
  } else {
    let errorMessage = signInResult.message;
    console.log(errorMessage);
    // Display error message to the user
    // document.getElementById("error-message").innerText = errorMessage;
  }
}
