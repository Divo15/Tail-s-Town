(function () {
  "use strict";

  var launcher = document.querySelector(".support-launcher");
  var panel = document.querySelector(".support-panel");
  var closeButton = document.querySelector(".support-close");
  var form = document.querySelector("[data-support-form]");
  var status = document.querySelector("[data-support-status]");
  var closeTimer;
  if (!launcher || !panel || !closeButton || !form || !status) return;

  function setOpen(open) {
    window.clearTimeout(closeTimer);
    if (open) panel.hidden = false;
    launcher.setAttribute("aria-expanded", String(open));
    if (open) {
      window.requestAnimationFrame(function () { panel.classList.add("is-open"); });
      window.setTimeout(function () { document.getElementById("support-name").focus(); }, 40);
    } else {
      panel.classList.remove("is-open");
      closeTimer = window.setTimeout(function () { panel.hidden = true; }, 180);
      launcher.focus();
    }
  }

  launcher.addEventListener("click", function () {
    setOpen(launcher.getAttribute("aria-expanded") !== "true");
  });
  closeButton.addEventListener("click", function () { setOpen(false); });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden) setOpen(false);
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    status.className = "support-form-status is-preview";
    status.textContent = "Preview ready. Email delivery will be connected next.";
  });
}());
