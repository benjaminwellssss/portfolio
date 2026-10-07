(function () {
  document.querySelectorAll('.stat-card b').forEach(function (b) { b.setAttribute('data-text', b.textContent); });
  document.querySelectorAll('.pagehead h1, .hero h2, .services h2, .process h2, .cta h2, .row h3').forEach(function (h) {
    if (h.children.length) return; h.classList.add('fx'); h.setAttribute('data-text', h.textContent);
  });
})();

(function () {
  var bar = document.querySelector('.bar'), btn = document.querySelector('.burger');
  if (!bar || !btn) return;
  var seen = false;
  try { seen = !!localStorage.getItem('menu-seen'); } catch (e) {}
  function set(open) {
    if (open && !seen) { bar.classList.add('first'); seen = true; try { localStorage.setItem('menu-seen', '1'); } catch (e) {} }
    else if (open) bar.classList.remove('first');
    bar.classList.toggle('open', open); btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  btn.addEventListener('click', function (e) { e.stopPropagation(); set(!bar.classList.contains('open')); });
  document.addEventListener('click', function (e) { if (bar.classList.contains('open') && !bar.querySelector('nav').contains(e.target)) set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
  window.addEventListener('resize', function () { if (innerWidth > 700) set(false); });
})();
(function () {
  // main videos play (muted, looping) while they are on screen and pause when they leave; swapped out of the viewer they pause too
  function start(v) { if (!v.src && v.dataset.src) v.src = v.dataset.src; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  var vids = [].slice.call(document.querySelectorAll('.dp-main video'));
  if (vids.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) start(e.target); else e.target.pause(); }); }, { threshold: 0.5 });
    vids.forEach(function (v) { io.observe(v); });
  } else { vids.forEach(start); }

  // lock each project's text panel to the height of the main video; "Read more" opens it to its full length when the text is longer
  document.querySelectorAll('.dp').forEach(function (dp) {
    var main = dp.querySelector('.dp-main'), text = dp.querySelector('.dp-text'), more = dp.querySelector('.dp-more');
    if (!main || !text || !more) return;
    function fit() {
      dp.style.setProperty('--dp-h', main.getBoundingClientRect().height + 'px');
      if (dp.classList.contains('open')) { more.hidden = false; return; }
      var over = text.scrollHeight > text.clientHeight + 2;
      text.classList.toggle('clamped', over); more.hidden = !over;
    }
    more.addEventListener('click', function () {
      var open = dp.classList.toggle('open');
      more.setAttribute('aria-expanded', open ? 'true' : 'false'); more.textContent = open ? 'Show less' : 'Read more';
      if (!open) { fit(); dp.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
    });
    if ('ResizeObserver' in window) new ResizeObserver(fit).observe(main);
    window.addEventListener('resize', fit); window.addEventListener('load', fit); fit();
  });

  // Steam-style viewer: click a thumbnail to show it in the main view; arrows and the slider move the thumbnail row
  document.querySelectorAll('.dp-media').forEach(function (m) {
    var main = m.querySelector('.dp-main'), strip = m.querySelector('.dp-thumbs');
    if (!strip) return;
    var tiles = [].slice.call(strip.querySelectorAll('.dp-tile')), video = main.querySelector('video');
    tiles.forEach(function (t) {
      t.addEventListener('click', function () {
        tiles.forEach(function (x) { x.classList.toggle('on', x === t); });
        var type = t.dataset.type;
        if (type === 'video') { if (video) main.replaceChildren(video); }
        else if (type === 'img') { var i = document.createElement('img'); i.src = t.dataset.src; i.alt = t.dataset.alt || ''; main.replaceChildren(i); }
        else if (type === 'svg') { var d = document.createElement('div'); d.className = 'dp-svgmain'; d.appendChild(t.querySelector('template').content.cloneNode(true)); main.replaceChildren(d); }
      });
    });
    var knob = m.querySelector('.dp-knob'), slider = m.querySelector('.dp-slider');
    function sync() {
      var max = strip.scrollWidth - strip.clientWidth;
      var ctl = m.querySelector('.dp-ctl');
      if (max <= 1) { ctl.classList.add('idle'); knob.style.width = '100%'; knob.style.left = '0'; return; }
      ctl.classList.remove('idle');
      var ratio = strip.clientWidth / strip.scrollWidth, w = Math.max(16, ratio * 100);
      knob.style.width = w + '%'; knob.style.left = (strip.scrollLeft / max) * (100 - w) + '%';
    }
    strip.addEventListener('scroll', sync); window.addEventListener('resize', sync); sync();
    m.querySelectorAll('.dp-arrow').forEach(function (b) {
      b.addEventListener('click', function () { strip.scrollBy({ left: Number(b.dataset.dir) * 3 * 122, behavior: 'smooth' }); });
    });
    var drag = null;
    knob.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, left: strip.scrollLeft }; knob.setPointerCapture(e.pointerId); strip.style.scrollBehavior = 'auto'; });
    knob.addEventListener('pointermove', function (e) {
      if (!drag) return;
      var max = strip.scrollWidth - strip.clientWidth, track = slider.clientWidth - knob.clientWidth;
      strip.scrollLeft = drag.left + ((e.clientX - drag.x) / Math.max(1, track)) * max;
    });
    knob.addEventListener('pointerup', function () { drag = null; strip.style.scrollBehavior = ''; });
  });
})();
