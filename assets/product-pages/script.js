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
  const isRollupProductPage = document.body.matches(".detail-feeder, .detail-water");
  const isAtPageBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 8;
  header?.classList.toggle("is-rolled-up", isRollupProductPage && isAtPageBottom);
};

const syncHeaderHeight = () => {
  const headerHeight = Math.round(header?.getBoundingClientRect().height || 0);
  document.documentElement.style.setProperty("--site-header-height", `${headerHeight}px`);
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

let headerScrollFrame;
window.addEventListener(
  "scroll",
  () => {
    if (headerScrollFrame) return;
    headerScrollFrame = window.requestAnimationFrame(() => {
      setHeaderState();
      headerScrollFrame = undefined;
    });
  },
  { passive: true },
);
window.addEventListener("resize", () => {
  syncHeaderHeight();
  setHeaderState();
});
window.addEventListener("load", syncHeaderHeight, { once: true });
setHeaderState();
syncHeaderHeight();

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
  document.querySelector("#products")?.scrollIntoView({ behavior: "smooth" });
});

const hydrateVideo = (video) => {
  if (!video || video.src || !video.dataset.videoSrc) return;
  video.preload = "auto";
  video.src = video.dataset.videoSrc;
  video.load();
};

const playLiveVideo = (video) => {
  hydrateVideo(video);
  video.muted = true;
  video.loop = true;
  video.playsInline = true;
  const playAttempt = video.play();
  playAttempt?.catch(() => video.classList.add("needs-user-start"));
};

if (liveVideos.length) {
  const liveVideoObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const video = entry.target;
        if (entry.isIntersecting) {
          playLiveVideo(video);
        } else if (!video.paused) {
          video.pause();
        }
      });
    },
    { rootMargin: "75% 0px", threshold: 0.01 },
  );

  liveVideos.forEach((video) => liveVideoObserver.observe(video));
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

const frameSequences = [...document.querySelectorAll("[data-frame-sequence]")];
const singleCycleExplodedSections = [
  ...document.querySelectorAll(".detail-feeder .exploded-product, .detail-water .exploded-product"),
];

if (singleCycleExplodedSections.length) {
  const explosionObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const section = entry.target;
        const core = section.querySelector(".explode-core");
        const settleExplosion = () => section.classList.add("is-settled");

        section.classList.add("is-exploding");
        core?.addEventListener("animationend", settleExplosion, { once: true });
        window.setTimeout(settleExplosion, 5000);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.28 },
  );

  singleCycleExplodedSections.forEach((section) => explosionObserver.observe(section));
}

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

const setupFrameSequence = (section) => {
  const video = section.querySelector("[data-frame-video]");
  if (!video) return;

  const frameCount = Number(video.dataset.frameCount || 260);
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const header = document.querySelector(".site-header");
  const pixelsPerFrame = 14;
  let raf = 0;
  let mediaReady = false;

  const updateSequenceMetrics = () => {
    const headerHeight = Math.round(header?.getBoundingClientRect().height || 0);
    const stageHeight = Math.max(1, window.innerHeight - headerHeight);
    const scrollDistance = prefersReduced.matches ? 0 : (frameCount - 1) * pixelsPerFrame;

    section.style.setProperty("--sequence-header-offset", `${headerHeight}px`);
    section.style.setProperty("--sequence-stage-height", `${stageHeight}px`);
    section.style.setProperty("--sequence-scroll-distance", `${scrollDistance}px`);

    return { headerHeight, stageHeight, scrollDistance };
  };

  let metrics = updateSequenceMetrics();

  const progressFromScroll = () => {
    const rect = section.getBoundingClientRect();
    const total = Math.max(1, metrics.scrollDistance);
    return clamp((metrics.headerHeight - rect.top) / total, 0, 1);
  };

  const render = () => {
    raf = 0;
    const progress = prefersReduced.matches ? 0 : progressFromScroll();
    const rect = section.getBoundingClientRect();
    const sequenceIsPinned = !prefersReduced.matches
      && rect.top <= metrics.headerHeight + 1
      && rect.bottom >= window.innerHeight - 1;

    document.body.classList.toggle("is-frame-sequence-active", sequenceIsPinned);
    if (mediaReady && Number.isFinite(video.duration)) {
      const targetTime = progress * Math.max(0, video.duration - 1 / 30);
      if (Math.abs(video.currentTime - targetTime) > 1 / 60) {
        video.currentTime = targetTime;
      }
    }
  };

  const requestRender = () => {
    if (!raf) raf = window.requestAnimationFrame(render);
  };

  const mediaObserver = new IntersectionObserver(
    (entries, observer) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      hydrateVideo(video);
      observer.disconnect();
    },
    { rootMargin: "150% 0px", threshold: 0.01 },
  );

  video.addEventListener("loadedmetadata", () => {
    mediaReady = true;
    video.pause();
    requestRender();
  });
  mediaObserver.observe(section);
  requestRender();

  const handleSequenceResize = () => {
    metrics = updateSequenceMetrics();
    requestRender();
  };

  window.addEventListener("scroll", requestRender, { passive: true });
  window.addEventListener("resize", handleSequenceResize);
  prefersReduced.addEventListener?.("change", handleSequenceResize);
};

frameSequences.forEach(setupFrameSequence);
