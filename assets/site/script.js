const header = document.querySelector(".site-header");
const hero = document.querySelector(".hero, .bundle-hero");
const heroPhotos = [...document.querySelectorAll(".hero-photo")];
const heroDots = [...document.querySelectorAll("[data-slide-dot]")];
const heroContent = document.querySelector(".hero-content");
const heroTitle = document.querySelector("#hero-title");
const featureShowcase = document.querySelector("[data-feature-showcase]");
const featureCopy = featureShowcase?.querySelector(".home-feature-copy");
const featureTitle = featureShowcase?.querySelector("#home-feature-title");
const featureTitleAccent = featureShowcase?.querySelector("[data-feature-title-accent]");
const featureTitleRest = featureShowcase?.querySelector("[data-feature-title-rest]");
const featureDescription = featureShowcase?.querySelector(".home-feature-description");
const featureCta = featureShowcase?.querySelector("[data-feature-cta]");
const featureIdNumber = featureShowcase?.querySelector("[data-feature-id-number]");
const featureIdName = featureShowcase?.querySelector("[data-feature-id-name]");
const featureCopyNumber = featureShowcase?.querySelector("[data-feature-copy-number]");
const featureProductMeta = featureShowcase?.querySelector(".home-feature-product-meta");
const featureShots = [...(featureShowcase?.querySelectorAll("[data-feature-shot]") || [])];
const featureControls = [...document.querySelectorAll("[data-feature-product]")];
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

const featureProducts = [
  {
    id: "litter",
    number: "02",
    name: "Smart Litter Box",
    titleAccent: "Cleaner litter,",
    titleRest: "less effort.",
    description: "A calmer, cleaner routine for shared spaces.",
    ctaLabel: "Explore Litter Box",
    ctaHref: "/shop/litter-box/",
  },
  {
    id: "feeder",
    number: "01",
    name: "Smart Feeder",
    titleAccent: "Meals ready,",
    titleRest: "right on time.",
    description: "Quiet portions, ready on schedule.",
    ctaLabel: "Explore Smart Feeder",
    ctaHref: "/shop/smart-feeder/",
  },
  {
    id: "water",
    number: "03",
    name: "Water Fountain",
    titleAccent: "Fresh water,",
    titleRest: "always ready.",
    description: "Filtered flow for everyday hydration.",
    ctaLabel: "Explore Water Fountain",
    ctaHref: "/shop/water-fountain/",
  },
];

let activeSlide = 0;
let activeFeatureIndex = 0;
let slideTimer;
let featureTimer;
let textTimer;
let featureTextTimer;
let leaveTimer;

const IMAGE_FADE_MS = 850;
const TEXT_SWAP_DELAY = 425;
const ROTATION_INTERVAL = 9200;
const FEATURE_ROTATION_INTERVAL = 6400;
const FEATURE_TEXT_SWAP_DELAY = 620;

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
  const isPastHero = Boolean(hero) && hero.getBoundingClientRect().bottom <= 0;
  header?.classList.toggle("is-past-hero", isPastHero);
  header?.toggleAttribute("inert", isPastHero);
};

const updateHeroText = (slide) => {
  if (heroTitle) {
    heroTitle.dataset.tone = slide.tone;
    heroTitle.innerHTML = `<span class="hero-accent">${slide.accent}</span><span>${slide.rest}</span>`;
  }
};

const updateFeatureContent = (product) => {
  if (featureIdNumber) featureIdNumber.textContent = product.number;
  if (featureIdName) featureIdName.textContent = product.name;
  if (featureCopyNumber) featureCopyNumber.textContent = product.number;
  if (featureProductMeta) {
    featureProductMeta.lastChild.textContent = ` ${product.name}`;
  }
  if (featureTitleAccent) featureTitleAccent.textContent = product.titleAccent;
  if (featureTitleRest) featureTitleRest.textContent = product.titleRest;
  if (featureDescription) featureDescription.textContent = product.description;
  if (featureCta) {
    featureCta.textContent = product.ctaLabel;
    featureCta.href = product.ctaHref;
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

  heroDots.forEach((dot, dotIndex) => {
    const isActive = dotIndex === activeSlide;
    dot.classList.toggle("is-active", isActive);
    dot.setAttribute("aria-pressed", isActive ? "true" : "false");
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

const showFeatureProduct = (index, options = {}) => {
  if (!featureShowcase) return;

  const { syncText = true } = options;
  activeFeatureIndex = (index + featureProducts.length) % featureProducts.length;
  const product = featureProducts[activeFeatureIndex];

  featureShowcase.dataset.activeProduct = product.id;
  featureShots.forEach((shot) => {
    shot.classList.toggle("is-active", shot.dataset.featureShot === product.id);
  });
  featureControls.forEach((control) => {
    const isActive = control.dataset.featureProduct === product.id;
    control.setAttribute("aria-pressed", isActive ? "true" : "false");
  });

  window.clearTimeout(featureTextTimer);

  if (!syncText || !featureCopy) {
    updateFeatureContent(product);
    return;
  }

  featureShowcase.classList.add("is-feature-updating");
  featureCopy.classList.add("is-updating");
  featureTextTimer = window.setTimeout(() => {
    updateFeatureContent(product);
    featureShowcase.classList.remove("is-feature-updating");
    featureCopy.classList.remove("is-updating");
  }, FEATURE_TEXT_SWAP_DELAY);
};

const startFeatureRotation = () => {
  window.clearInterval(featureTimer);
  if (!featureShowcase || reducedMotion.matches || saveData) return;

  featureTimer = window.setInterval(() => {
    showFeatureProduct(activeFeatureIndex + 1);
  }, FEATURE_ROTATION_INTERVAL);
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
window.addEventListener("resize", setHeaderState);

heroDots.forEach((dot) => {
  dot.addEventListener("click", () => {
    const index = Number(dot.dataset.slideDot);
    if (Number.isNaN(index)) return;
    showSlide(index);
    startHeroRotation();
  });
});

featureControls.forEach((control) => {
  control.addEventListener("click", () => {
    const nextIndex = featureProducts.findIndex((product) => product.id === control.dataset.featureProduct);
    if (nextIndex === -1) return;
    showFeatureProduct(nextIndex);
    startFeatureRotation();
  });
});

showSlide(0, { syncText: false });
startHeroRotation();
showFeatureProduct(0, { syncText: false });
startFeatureRotation();

document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    window.clearInterval(slideTimer);
    window.clearInterval(featureTimer);
  } else {
    startHeroRotation();
    startFeatureRotation();
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
