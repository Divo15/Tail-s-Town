(() => {
  const section = document.querySelector("[data-litter-animation]");
  if (!section) return;

  const canvas = section.querySelector("[data-litter-canvas]");
  const stories = [...section.querySelectorAll("[data-litter-story]")];
  const context = canvas?.getContext("2d", { alpha: false, desynchronized: true });
  const frameCount = Number(section.dataset.frameCount || 300);
  const availableFrameCount = Number(section.dataset.availableFrameCount || frameCount);
  const sourceFrameCount = Number(section.dataset.sourceFrameCount || frameCount);
  const desktopTemplate = section.dataset.desktopFrameTemplate;
  const mobileTemplate = section.dataset.mobileFrameTemplate;
  const desktopFinalFrame = section.dataset.desktopFinalFrame;
  const mobileFinalFrame = section.dataset.mobileFinalFrame;
  const mobileQuery = window.matchMedia("(max-width: 720px)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  if (!canvas || !context || !desktopTemplate || !mobileTemplate || !frameCount) return;

  const EXPLODE_END = 0.72;
  const REASSEMBLE_START = 0.78;
  const REASSEMBLE_END = REASSEMBLE_START + EXPLODE_END;
  const TIMELINE_END = REASSEMBLE_END;
  const FINAL_FRAME_START = 2;
  const PRELOAD_AHEAD = 24;
  const PRELOAD_BEHIND = 8;
  const MAX_CACHED_FRAMES = 42;
  const MAX_PARALLEL_LOADS = 6;
  const STORY_STARTS = [0, 0.16, 0.42, 0.66, REASSEMBLE_START];
  const LOOP_DURATION = 11000;

  const records = new Map();
  const queued = new Set();
  let queue = [];
  let activeLoads = 0;
  let animationFrame = 0;
  let targetProgress = 0;
  let displayProgress = 0;
  let targetFrame = 1;
  let lastDrawnFrame = 0;
  let activeStory = 0;
  let lastTick = performance.now();
  let disposed = false;
  let fullyActivated = false;
  let isPlaying = false;
  let loopStartedAt = 0;
  let prefetchStarted = false;
  let prefetchCursor = 1;
  const prefetchController = new AbortController();

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const sourceFrameForAvailable = (availableFrame) => {
    if (availableFrameCount === 75 && sourceFrameCount === 300) {
      return availableFrame <= 37 ? 1 + (availableFrame - 1) * 4 : 152 + (availableFrame - 38) * 4;
    }

    return Math.round(
      1 + ((availableFrame - 1) / Math.max(1, availableFrameCount - 1)) * (sourceFrameCount - 1),
    );
  };

  const frameUrl = (frame) => {
    if (frame <= FINAL_FRAME_START) {
      const finalFrame = mobileQuery.matches ? mobileFinalFrame : desktopFinalFrame;
      if (finalFrame) return finalFrame;
    }

    const template = mobileQuery.matches ? mobileTemplate : desktopTemplate;
    const availableFrame = Math.round(
      1 + ((frame - 1) / Math.max(1, frameCount - 1)) * (availableFrameCount - 1),
    );
    const sourceFrame = sourceFrameForAvailable(availableFrame);
    return template.replace("__FRAME__", String(sourceFrame).padStart(3, "0"));
  };

  const frameForProgress = (progress) => {
    const clamped = clamp(progress, 0, TIMELINE_END);
    if (clamped <= EXPLODE_END) {
      return Math.round(1 + (clamped / EXPLODE_END) * (frameCount - 1));
    }
    if (clamped < REASSEMBLE_START) return frameCount;
    if (clamped >= REASSEMBLE_END) return 1;

    const closing = (clamped - REASSEMBLE_START) / (REASSEMBLE_END - REASSEMBLE_START);
    const easedClosing = closing * closing * (3 - 2 * closing);
    return Math.round(frameCount - easedClosing * (frameCount - 1));
  };

  const storyForProgress = (progress) => {
    let nextStory = 0;
    for (let index = 1; index < STORY_STARTS.length; index += 1) {
      if (progress >= STORY_STARTS[index]) nextStory = index;
    }
    return nextStory;
  };

  const setStory = (index) => {
    if (index === activeStory && stories[index]?.classList.contains("is-active")) return;
    activeStory = index;
    section.dataset.activeStory = String(index);
    stories.forEach((story, storyIndex) => {
      const isActive = storyIndex === index;
      story.classList.toggle("is-active", isActive);
      story.setAttribute("aria-hidden", String(!isActive));
    });
  };

  const resizeCanvas = () => {
    const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const pixelWidth = Math.max(1, Math.round(width * ratio));
    const pixelHeight = Math.max(1, Math.round(height * ratio));

    if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
      canvas.width = pixelWidth;
      canvas.height = pixelHeight;
    }

    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    return { width, height };
  };

  const draw = (record, frame) => {
    const { width, height } = resizeCanvas();
    const image = record.image;
    const imageRatio = image.naturalWidth / image.naturalHeight;
    const canvasRatio = width / height;
    const scale = imageRatio > canvasRatio ? width / image.naturalWidth : height / image.naturalHeight;
    const drawWidth = image.naturalWidth * scale;
    const drawHeight = image.naturalHeight * scale;

    context.fillStyle = "#050505";
    context.fillRect(0, 0, width, height);
    context.drawImage(image, (width - drawWidth) / 2, (height - drawHeight) / 2, drawWidth, drawHeight);
    record.touched = performance.now();
    lastDrawnFrame = frame;
    section.classList.add("is-ready");
  };

  const trimCache = () => {
    if (records.size <= MAX_CACHED_FRAMES) return;
    const removable = [...records.entries()]
      .filter(
        ([frame, record]) =>
          record.status === "ready" && frame !== 1 && Math.abs(frame - targetFrame) > PRELOAD_BEHIND,
      )
      .sort(([, first], [, second]) => first.touched - second.touched);

    while (records.size > MAX_CACHED_FRAMES && removable.length) {
      const oldest = removable.shift();
      if (oldest) records.delete(oldest[0]);
    }
  };

  function scheduleRender() {
    if (!animationFrame && !disposed) animationFrame = window.requestAnimationFrame(render);
  }

  const finishLoad = (frame, record) => {
    if (disposed || record.status === "ready") return;
    record.status = "ready";
    record.touched = performance.now();
    activeLoads -= 1;
    trimCache();
    pumpQueue();
    scheduleRender();
  };

  function pumpQueue() {
    while (activeLoads < MAX_PARALLEL_LOADS && queue.length && !disposed) {
      const next = queue.shift();
      queued.delete(next.frame);
      if (records.has(next.frame)) continue;

      const image = new Image();
      const record = { image, status: "loading", touched: performance.now() };
      records.set(next.frame, record);
      activeLoads += 1;
      image.decoding = "async";
      image.fetchPriority = next.urgent ? "high" : "auto";
      image.onload = () => {
        image.decode().catch(() => undefined).finally(() => finishLoad(next.frame, record));
      };
      image.onerror = () => {
        records.delete(next.frame);
        activeLoads -= 1;
        pumpQueue();
      };
      image.src = frameUrl(next.frame);
    }
  }

  const queueFrame = (frame, urgent = false) => {
    if (frame < 1 || frame > frameCount || records.has(frame)) return;
    if (queued.has(frame)) {
      if (urgent) {
        const index = queue.findIndex((item) => item.frame === frame);
        if (index >= 0) {
          const [item] = queue.splice(index, 1);
          queue.unshift({ ...item, urgent: true });
        }
      }
      return;
    }

    queued.add(frame);
    const item = { frame, urgent };
    if (urgent) queue.unshift(item);
    else queue.push(item);
    pumpQueue();
  };

  const primeFrames = (frame, direction) => {
    queueFrame(frame, true);
    for (let offset = 1; offset <= PRELOAD_AHEAD; offset += 1) {
      queueFrame(frame + offset * direction, offset <= 4);
    }
    for (let offset = 1; offset <= PRELOAD_BEHIND; offset += 1) {
      queueFrame(frame - offset * direction);
    }
  };

  const drawBestAvailable = (frame) => {
    const exact = records.get(frame);
    if (exact?.status === "ready") {
      if (frame !== lastDrawnFrame) draw(exact, frame);
      return;
    }

    if (!lastDrawnFrame) {
      const first = records.get(1);
      if (first?.status === "ready") draw(first, 1);
      return;
    }

    const direction = frame >= lastDrawnFrame ? -1 : 1;
    for (let candidate = frame; candidate !== lastDrawnFrame; candidate += direction) {
      const record = records.get(candidate);
      if (record?.status === "ready") {
        draw(record, candidate);
        return;
      }
    }
  };

  const updateActiveState = () => {
    const rect = section.getBoundingClientRect();
    const isActive = rect.top <= window.innerHeight && rect.bottom >= 0;
    document.body.classList.toggle("is-litter-animation-active", isActive);
    return isActive;
  };

  function render(time) {
    animationFrame = 0;
    const elapsed = Math.min(64, Math.max(1, time - lastTick));
    lastTick = time;

    if (reducedMotion.matches || !isPlaying) {
      displayProgress = 0;
    } else {
      const loopElapsed = (time - loopStartedAt) % LOOP_DURATION;
      displayProgress = (loopElapsed / LOOP_DURATION) * TIMELINE_END;
    }

    const nextFrame = reducedMotion.matches || !isPlaying ? 1 : frameForProgress(displayProgress);
    if (nextFrame !== targetFrame) {
      const direction = Math.sign(nextFrame - targetFrame) || 1;
      targetFrame = nextFrame;
      primeFrames(targetFrame, direction);
    }

    drawBestAvailable(targetFrame);
    setStory(reducedMotion.matches ? 0 : storyForProgress(displayProgress));

    if (isPlaying && !reducedMotion.matches) {
      scheduleRender();
    }
  }

  const startLoop = () => {
    if (reducedMotion.matches) return;
    if (!isPlaying) {
      loopStartedAt = performance.now() - (displayProgress / TIMELINE_END) * LOOP_DURATION;
      isPlaying = true;
    }
    updateActiveState();
    scheduleRender();
  };

  const stopLoop = () => {
    isPlaying = false;
    updateActiveState();
  };

  const updateTarget = () => {
    if (updateActiveState()) startLoop();
    else stopLoop();
  };

  const handleResize = () => {
    resizeCanvas();
    const current = records.get(lastDrawnFrame);
    if (current?.status === "ready") draw(current, lastDrawnFrame);
    updateTarget();
  };

  const prefetchWorker = async () => {
    while (!disposed && prefetchCursor <= frameCount) {
      const frame = prefetchCursor;
      prefetchCursor += 1;
      try {
        const response = await fetch(frameUrl(frame), {
          cache: "force-cache",
          signal: prefetchController.signal,
        });
        if (response.ok) await response.arrayBuffer();
      } catch {
        if (prefetchController.signal.aborted) return;
      }
    }
  };

  const startPrefetch = () => {
    if (prefetchStarted || reducedMotion.matches) return;
    prefetchStarted = true;
    window.setTimeout(() => {
      void Promise.all(Array.from({ length: 2 }, () => prefetchWorker()));
    }, 650);
  };

  const proximityObserver = new IntersectionObserver(
    (entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      fullyActivated = true;
      targetProgress = 0;
      targetFrame = 1;
      primeFrames(targetFrame, 1);
      startPrefetch();
      if (updateActiveState()) startLoop();
      else scheduleRender();
      proximityObserver.disconnect();
    },
    { rootMargin: "0px", threshold: 0 },
  );

  activeStory = -1;
  setStory(0);
  queueFrame(1, true);
  resizeCanvas();
  proximityObserver.observe(section);
  window.addEventListener("scroll", updateTarget, { passive: true });
  window.addEventListener("resize", handleResize);

  window.addEventListener(
    "pagehide",
    () => {
      disposed = true;
      prefetchController.abort();
      window.cancelAnimationFrame(animationFrame);
      proximityObserver.disconnect();
      queue = [];
      queued.clear();
      records.forEach(({ image }) => {
        image.onload = null;
        image.onerror = null;
      });
      records.clear();
      document.body.classList.remove("is-litter-animation-active");
    },
    { once: true },
  );
})();
