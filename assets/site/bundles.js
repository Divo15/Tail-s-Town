(() => {
  const stage = document.querySelector('.bundle-stage');
  if (!stage) return;

  const slides = [...stage.querySelectorAll('.bundle-slide')];
  const images = slides.map((slide) => slide.querySelector('img'));
  const textGroups = [
    document.querySelector('[data-bundle-info]'),
    document.querySelector('[data-bundle-purchase]'),
    document.querySelector('[data-bundle-text]'),
  ];
  const indexLabel = document.querySelector('[data-bundle-index]');
  const dots = [...document.querySelectorAll('.bundle-progress span')];
  let active = 0;
  let moving = false;
  let pointerStart = null;
  let autoTimer;
  const AUTO_ROTATION_INTERVAL = 4000;

  const preload = () => Promise.all(images.map((image) => {
    if (image.complete && image.naturalWidth) return Promise.resolve();
    return new Promise((resolve) => {
      image.addEventListener('load', resolve, { once: true });
      image.addEventListener('error', resolve, { once: true });
    });
  }));

  const updateText = () => {
    const slide = slides[active];
    const [firstLine, secondLine] = slide.dataset.name.split('|');
    document.querySelector('#bundle-title').innerHTML = `${firstLine}<br>${secondLine}`;
    document.querySelector('[data-stage-number]').textContent = String(active + 1).padStart(2, '0');
    document.querySelector('[data-stage-title]').innerHTML = slide.dataset.stageTitle;
    document.querySelector('[data-stage-products]').textContent = slide.dataset.products;
    document.querySelector('[data-original-price]').textContent = slide.dataset.original;
    document.querySelector('[data-bundle-price]').textContent = slide.dataset.price;
    document.querySelector('[data-bundle-saving]').textContent = slide.dataset.saving;
    document.querySelector('[data-bundle-cta]').href = slide.dataset.href;
    indexLabel.textContent = String(active + 1).padStart(2, '0');
    dots.forEach((dot, index) => dot.classList.toggle('is-active', index === active));
    textGroups.forEach((group) => group.classList.remove('is-changing'));
  };

  const rotate = (direction, manual = true) => {
    if (moving) return;
    moving = true;
    if (manual) clearInterval(autoTimer);
    textGroups.forEach((group) => group.classList.add('is-changing'));
    active = (active + direction + slides.length) % slides.length;

    slides.forEach((slide, index) => {
      const isFront = index === active;
      slide.dataset.position = isFront ? 'front' : (direction > 0 ? 'left' : 'right');
      slide.setAttribute('aria-hidden', isFront ? 'false' : 'true');
    });

    window.setTimeout(updateText, 820);
    window.setTimeout(() => { moving = false; }, 880);
  };

  document.querySelector('[data-bundle-previous]').addEventListener('click', () => rotate(-1));
  document.querySelector('[data-bundle-next]').addEventListener('click', () => rotate(1));
  stage.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); rotate(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); rotate(1); }
  });
  stage.addEventListener('pointerdown', (event) => {
    pointerStart = { x: event.clientX, y: event.clientY };
    stage.setPointerCapture(event.pointerId);
  });
  stage.addEventListener('pointerup', (event) => {
    if (!pointerStart) return;
    const dx = event.clientX - pointerStart.x;
    const dy = event.clientY - pointerStart.y;
    pointerStart = null;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) rotate(dx < 0 ? 1 : -1);
  });
  stage.addEventListener('pointercancel', () => { pointerStart = null; });

  preload().then(() => {
    stage.classList.add('is-ready');
    autoTimer = window.setInterval(() => rotate(1, false), AUTO_ROTATION_INTERVAL);
  });
})();
