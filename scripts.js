function toggleProfile(el) {
  // Strip the 'show' part of the ID
  var profile = el.id.substring(4);
  element = document.getElementById(profile);
  var isExpanded = (element.style.display == 'block') ? true : false;

  if (isExpanded) {
    element.style.display = 'none';
    document.getElementById(el.id).innerHTML = "More info";
  } else {
    element.style.display = 'block';
    document.getElementById(el.id).innerHTML = "Less info";
  }
}

function logout(el) {
  // We log out by removing the user's credentials from the secret form.
  // And then we redirect the user.
  alert('Are you sure you want to log out?');
  var usernameFieldId = "usernameSecret";
  var passwordFieldId = "passwordSecret";
  document.getElementById(usernameFieldId).value = "";
  document.getElementById(passwordFieldId).value = "";

  document.location.reload();
}

function goHome() {
  document.location.reload();
}