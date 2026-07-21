const header = document.querySelector(".site-header");
const hero = document.querySelector(".hero");
const heroPhotos = [...document.querySelectorAll(".hero-photo")];
const heroButtons = [...document.querySelectorAll("[data-slide-target]")];
const heroContent = document.querySelector(".hero-content");
const heroTitle = document.querySelector("#hero-title");
const scrollPet = document.querySelector(".scroll-pet");
const addButtons = [...document.querySelectorAll("[data-product]")];
const liveVideos = [...document.querySelectorAll("[data-live-video]")];
const toast = document.querySelector(".cart-toast");
const signupForm = document.querySelector(".signup-form");

if (window.location.hash === "#bundles") {
  window.location.replace("/shop/bundles/");
}

const slides = [
  {
    accent: "Breakfast",
    rest: "With Wagging Tails",
    tone: "maple",
  },
  {
    accent: "Tiny Sips",
    rest: "Cozy Whiskers",
    tone: "ice",
  },
  {
    accent: "Little Paws",
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
    rest: "After Walkies",
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

  heroButtons.forEach((button, buttonIndex) => {
    button.classList.toggle("is-active", buttonIndex === activeSlide);
  });

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

heroButtons.forEach((button) => {
  button.addEventListener("click", () => {
    showSlide(Number(button.dataset.slideTarget));
    startHeroRotation();
  });
});

addButtons.forEach((button) => {
  button.addEventListener("click", () => {
    showToast(`${button.dataset.product} added to your launch cart.`);
  });
});

signupForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  showToast("You are on the Tail's Town Canada launch list.");
});

scrollPet?.addEventListener("click", () => {
  document.querySelector("#shop")?.scrollIntoView({ behavior: "smooth" });
});

const startLiveVideos = () => {
  liveVideos.forEach((video) => {
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    const playAttempt = video.play();
    if (playAttempt) {
      playAttempt.catch(() => {
        video.classList.add("needs-user-start");
      });
    }
  });
};

if (liveVideos.length) {
  startLiveVideos();
  window.addEventListener("pageshow", startLiveVideos);
  document.addEventListener("click", startLiveVideos);
  document.addEventListener("touchstart", startLiveVideos, { passive: true });
}

if (hero && heroPhotos.length && heroTitle) {
  showSlide(0, { syncText: false });
  startHeroRotation();

  window.addEventListener(
    "load",
    () => {
      hero.classList.add("is-loaded");
    },
    { once: true },
  );
}
