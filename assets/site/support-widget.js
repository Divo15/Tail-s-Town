(function () {
  "use strict";

  var launcher = document.querySelector(".support-launcher");
  if (!launcher) return;

  function updateLauncherVisibility() {
    var pageBottom = document.documentElement.scrollHeight;
    var viewportBottom = window.scrollY + window.innerHeight;
    launcher.hidden = viewportBottom < pageBottom - 24;
  }

  window.addEventListener("scroll", updateLauncherVisibility, { passive: true });
  window.addEventListener("resize", updateLauncherVisibility);
  window.addEventListener("load", updateLauncherVisibility);
  updateLauncherVisibility();
}());
