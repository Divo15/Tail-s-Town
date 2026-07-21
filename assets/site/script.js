const header = document.querySelector(".site-header");
const hero = document.querySelector(".hero");
const heroPhotos = [...document.querySelectorAll(".hero-photo")];
const heroContent = document.querySelector(".hero-content");
const heroTitle = document.querySelector("#hero-title");
const toast = document.querySelector(".cart-toast");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const saveData = navigator.connection?.saveData === true;

if (window.location.hash === "#bundles") {
  window.location.replace("/shop/bundles/");
}

const slides = [
  {
    accent: "BreakFast",
    rest: "With Wagging tails",
    tone: "maple",
  },
  {
    accent: "Tiny Sips",
    rest: "Cozy Whiskers",
    tone: "ice",
  },
  {
    accent: "Little Pows",
    rest: "One Corner",
    tone: "pine",
  },
  {
    accent: "Clean Steps",
    rest: "Tidy Litter",
    tone: "mint",
  },
  {
    accent: "Sunny Sips",
    rest: "After Long Walks",
    tone: "sun",
  },
];

let activeSlide = 0;
let slideTimer;
let textTimer;
let leaveTimer;

const IMAGE_FADE_MS = 850;
const TEXT_SWAP_DELAY = 425;
const ROTATION_INTERVAL = 9200;

const hydratePhoto = (photo) => {
  if (!photo || photo.dataset.hydrated === "true") return;

  const source = photo.closest("picture")?.querySelector("source[data-srcset]");
  if (source?.dataset.srcset) {
    source.srcset = source.dataset.srcset;
    delete source.dataset.srcset;
  }

  if (photo.dataset.src) {
    photo.src = photo.dataset.src;
    delete photo.dataset.src;
  }

  photo.dataset.hydrated = "true";
};

const setHeaderState = () => {
  header?.classList.toggle("is-solid", window.scrollY > 24);
};

const updateHeroText = (slide) => {
  if (heroTitle) {
    heroTitle.dataset.tone = slide.tone;
    heroTitle.innerHTML = `<span class="hero-accent">${slide.accent}</span><span>${slide.rest}</span>`;
  }
};

const showSlide = (index, options = {}) => {
  const { syncText = true } = options;
  const previousSlide = activeSlide;
  activeSlide = (index + slides.length) % slides.length;
  const slide = slides[activeSlide];
  hydratePhoto(heroPhotos[activeSlide]);

  if (previousSlide === activeSlide && syncText) {
    return;
  }

  if (hero) {
    hero.dataset.activeSlide = String(activeSlide);
  }

  window.clearTimeout(leaveTimer);

  heroPhotos.forEach((photo, photoIndex) => {
    if (photoIndex === previousSlide && previousSlide !== activeSlide) {
      photo.classList.add("is-leaving");
    } else {
      photo.classList.remove("is-leaving");
    }
    photo.classList.toggle("is-active", photoIndex === activeSlide);
  });

  leaveTimer = window.setTimeout(() => {
    heroPhotos.forEach((photo) => photo.classList.remove("is-leaving"));
  }, IMAGE_FADE_MS);

  window.clearTimeout(textTimer);

  if (!syncText || !heroContent) {
    updateHeroText(slide);
    return;
  }

  heroContent.classList.add("is-text-changing");
  textTimer = window.setTimeout(() => {
    updateHeroText(slide);
    heroContent.classList.remove("is-text-changing");
  }, TEXT_SWAP_DELAY);
};

const startHeroRotation = () => {
  window.clearInterval(slideTimer);
  if (reducedMotion.matches || saveData) return;

  const nextPhoto = heroPhotos[(activeSlide + 1) % heroPhotos.length];
  const prepareNext = () => hydratePhoto(nextPhoto);
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(prepareNext, { timeout: 2500 });
  } else {
    window.setTimeout(prepareNext, 1200);
  }

  slideTimer = window.setInterval(() => {
    showSlide(activeSlide + 1);
  }, ROTATION_INTERVAL);
};

const showToast = (message) => {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("is-visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.classList.remove("is-visible");
  }, 2200);
};

let scrollFrame;
window.addEventListener(
  "scroll",
  () => {
    if (scrollFrame) return;
    scrollFrame = window.requestAnimationFrame(() => {
      setHeaderState();
      scrollFrame = undefined;
    });
  },
  { passive: true },
);
setHeaderState();

if (window.matchMedia("(hover: hover)").matches) {
  document.querySelectorAll(".product-tile").forEach((tile) => {
    tile.addEventListener("mouseenter", () => {
      showToast("Open products to browse this item.");
    });
  });
}

showSlide(0, { syncText: false });
startHeroRotation();

document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    window.clearInterval(slideTimer);
  } else {
    startHeroRotation();
  }
});

if (hero) {
  window.addEventListener(
    "load",
    () => {
      hero.classList.add("is-loaded");
    },
    { once: true },
  );
}
