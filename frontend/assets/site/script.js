const heroSlides = Array.from(document.querySelectorAll(".hero-bg"));
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (heroSlides.length > 1 && !reduceMotion) {
  let activeIndex = 0;

  window.setInterval(() => {
    if (document.hidden) {
      return;
    }

    heroSlides[activeIndex].classList.remove("is-active");
    activeIndex = (activeIndex + 1) % heroSlides.length;
    heroSlides[activeIndex].classList.add("is-active");
  }, 6500);
}
