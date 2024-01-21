window.onload = function () {
  // let main = document.getElementById("main");
  // let welcome = document.getElementById("welcome");
  // main.innerHTML = welcome.innerHTML;
};
// var validationTimer;

// function startValidation() {
//   clearTimeout(validationTimer);

//   validationTimer = setTimeout(function () {
//     validateData();
//   }, 1000);
// }
function clearValidity() {
  let password = document.getElementById("password");
  let repeatPassword = document.getElementById("repeat-psw");
  password.setCustomValidity("");
  repeatPassword.setCustomValidity("");
}

function validateData() {
  let password = document.getElementById("password");
  let repeatPassword = document.getElementById("repeat-psw");
  password.setCustomValidity("");

  if (password.value.length < 8) {
    password.setCustomValidity("Password must be at least 8 characters long");
    console.log("Password must be at least 8 characters long");
    password.reportValidity();
    return false;
  } else {
    password.setCustomValidity("");
    console.log("Password is valid");
  }

  if (password.value !== repeatPassword.value) {
    repeatPassword.setCustomValidity("Passwords do not match");
    console.log("Passwords do not match");
    repeatPassword.reportValidity();
    return false;
  } else {
    repeatPassword.setCustomValidity("");
  }
}

function register(event) {
  event.preventDefault();
  if (!validateData()) {
    return false;
  }
  let form = document.getElementById("register-form");
  form.submit();
  return true;
}
