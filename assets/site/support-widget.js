(function () {
  "use strict";

  var launcher = document.querySelector(".support-launcher");
  var hero = document.querySelector(".hero");
  var revealOffset = 240;
  if (!launcher) return;

  var canonical = document.querySelector('link[rel="canonical"]');
  var pageUrl = canonical ? canonical.href : window.location.href.split("#")[0];
  pageUrl += (pageUrl.indexOf("?") === -1 ? "?" : "&") + "utm_source=whatsapp&utm_medium=support_widget";
  var message = "Hello,\nI have a question about\n" + pageUrl;
  launcher.href = "https://wa.me/919999554069?text=" + encodeURIComponent(message);

  function updateLauncherVisibility() {
    if (hero) {
      var heroBottom = hero.offsetTop + hero.offsetHeight;
      var revealPoint = Math.max(0, heroBottom - 48);
      launcher.hidden = window.scrollY < revealPoint;
      return;
    }

    var pageBottom = document.documentElement.scrollHeight;
    var viewportBottom = window.scrollY + window.innerHeight;
    launcher.hidden = viewportBottom < pageBottom - revealOffset;
  }

  window.addEventListener("scroll", updateLauncherVisibility, { passive: true });
  window.addEventListener("resize", updateLauncherVisibility);
  window.addEventListener("load", updateLauncherVisibility);
  updateLauncherVisibility();
}());
