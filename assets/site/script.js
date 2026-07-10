const header = document.querySelector(".site-header");
const hero = document.querySelector(".hero");
const heroPhotos = [...document.querySelectorAll(".hero-photo")];
const heroContent = document.querySelector(".hero-content");
const heroTitle = document.querySelector("#hero-title");
const toast = document.querySelector(".cart-toast");

const slides = [
  {
    accent: "Smart Care",
    rest: "For Pet Homes",
    tone: "maple",
  },
  {
    accent: "Fresh Water",
    rest: "For Quiet Sips",
    tone: "ice",
  },
  {
    accent: "Shared Corners",
    rest: "For Calm Routines",
    tone: "pine",
  },
  {
    accent: "Cleaner Days",
    rest: "For Indoor Cats",
    tone: "mint",
  },
  {
    accent: "Sunny Hydration",
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

window.addEventListener("scroll", setHeaderState, { passive: true });
setHeaderState();

document.querySelectorAll(".product-tile").forEach((tile) => {
  tile.addEventListener("mouseenter", () => {
    showToast("Open the shop to browse this product.");
  });
});

showSlide(0, { syncText: false });
startHeroRotation();

if (hero) {
  window.addEventListener(
    "load",
    () => {
      hero.classList.add("is-loaded");
    },
    { once: true },
  );
}
