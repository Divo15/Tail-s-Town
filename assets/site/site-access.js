(function () {
  "use strict";

  var toggle = document.querySelector("[data-password-toggle]");
  var password = document.querySelector("#site-password");
  if (!toggle || !password) return;

  toggle.addEventListener("click", function () {
    var isVisible = password.type === "text";
    password.type = isVisible ? "password" : "text";
    toggle.setAttribute("aria-pressed", String(!isVisible));
    toggle.setAttribute("aria-label", isVisible ? "Show password" : "Hide password");
    password.focus();
  });
}());
