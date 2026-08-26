(function () {
  "use strict";

  var launcher = document.querySelector(".support-launcher");
  var panel = document.querySelector(".support-panel");
  var closeButton = document.querySelector(".support-close");
  var form = document.querySelector("[data-support-form]");
  var status = document.querySelector("[data-support-status]");
  var closeTimer;
  var autoOpenTimer;
  var activeStartedAt;
  var fallbackStorage = {};
  var autoOpenDelay = 15000;
  var autoShownKey = "tailsTownSupportAutoShown";
  var activeTimeKey = "tailsTownSupportActiveMs";
  if (!launcher || !panel || !closeButton || !form || !status) return;

  function readSessionValue(key) {
    try {
      return window.sessionStorage.getItem(key);
    } catch (error) {
      return fallbackStorage[key] || null;
    }
  }

  function writeSessionValue(key, value) {
    try {
      window.sessionStorage.setItem(key, value);
    } catch (error) {
      fallbackStorage[key] = value;
    }
  }

  function getActiveTime() {
    return Math.max(0, Number(readSessionValue(activeTimeKey)) || 0);
  }

  function persistActiveTime() {
    if (typeof activeStartedAt !== "number") return;
    writeSessionValue(activeTimeKey, String(getActiveTime() + (Date.now() - activeStartedAt)));
    activeStartedAt = undefined;
  }

  function markAutoPromptShown() {
    window.clearTimeout(autoOpenTimer);
    persistActiveTime();
    writeSessionValue(autoShownKey, "true");
  }

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
      launcher.focus();
    }
  }

  launcher.addEventListener("click", function () {
    var shouldOpen = launcher.getAttribute("aria-expanded") !== "true";
    if (shouldOpen) markAutoPromptShown();
    setOpen(shouldOpen, shouldOpen);
  });
  closeButton.addEventListener("click", function () { setOpen(false, false); });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden) setOpen(false, false);
  });

  function openAutomaticPrompt() {
    if (readSessionValue(autoShownKey) === "true") return;
    markAutoPromptShown();
    setOpen(true, false);
  }

  function scheduleAutomaticPrompt() {
    window.clearTimeout(autoOpenTimer);
    if (readSessionValue(autoShownKey) === "true" || document.visibilityState !== "visible") return;

    activeStartedAt = Date.now();
    var remainingTime = Math.max(0, autoOpenDelay - getActiveTime());
    autoOpenTimer = window.setTimeout(openAutomaticPrompt, remainingTime);
  }

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") {
      scheduleAutomaticPrompt();
    } else {
      window.clearTimeout(autoOpenTimer);
      persistActiveTime();
    }
  });
  window.addEventListener("pagehide", persistActiveTime);
  scheduleAutomaticPrompt();

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    status.className = "support-form-status is-preview";
    status.textContent = "Preview ready. Email delivery will be connected next.";
  });
}());
