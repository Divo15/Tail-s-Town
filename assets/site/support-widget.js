(function () {
  "use strict";

  var launcher = document.querySelector(".support-launcher");
  var panel = document.querySelector(".support-panel");
  var closeButton = document.querySelector(".support-close");
  var form = document.querySelector("[data-support-form]");
  var status = document.querySelector("[data-support-status]");
  var revealBoundary = document.querySelector("[data-support-reveal-boundary]");
  var closeTimer;
  if (!launcher || !panel || !closeButton || !form || !status) return;

  function setOpen(open, moveFocus) {
    window.clearTimeout(closeTimer);
    if (open) panel.hidden = false;
    launcher.setAttribute("aria-expanded", String(open));
    if (open) {
      window.requestAnimationFrame(function () { panel.classList.add("is-open"); });
      if (moveFocus) {
        window.setTimeout(function () { document.getElementById("support-name").focus(); }, 40);
      }
    } else {
      panel.classList.remove("is-open");
      closeTimer = window.setTimeout(function () { panel.hidden = true; }, 180);
      if (moveFocus && !launcher.hidden) launcher.focus();
    }
  }

  launcher.addEventListener("click", function () {
    var shouldOpen = launcher.getAttribute("aria-expanded") !== "true";
    setOpen(shouldOpen, shouldOpen);
  });
  closeButton.addEventListener("click", function () { setOpen(false, true); });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden) setOpen(false, true);
  });

  function updateLauncherVisibility() {
    var shouldShow = !revealBoundary || revealBoundary.getBoundingClientRect().bottom <= 0;
    if (!shouldShow && launcher.getAttribute("aria-expanded") === "true") {
      setOpen(false, false);
    }
    launcher.hidden = !shouldShow;
  }

  if (revealBoundary) {
    window.addEventListener("scroll", updateLauncherVisibility, { passive: true });
    window.addEventListener("resize", updateLauncherVisibility);
  }
  updateLauncherVisibility();

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    status.className = "support-form-status is-preview";
    status.textContent = "Preview ready. Email delivery will be connected next.";
  });
}());
