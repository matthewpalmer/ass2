function toggleProfile(el) {
  // Strip the 'show' part of the ID
  var profile = el.id.substring(4);
  element = document.getElementById(profile);
  var isExpanded = (element.style.display == 'block') ? true : false;

  if (isExpanded) {
    element.style.display = 'none';
    document.getElementById(el.id).innerHTML = "Show more";
  } else {
    element.style.display = 'block';
    document.getElementById(el.id).innerHTML = "Show less";
  }
}