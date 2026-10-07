(function () {
  document.querySelectorAll('.stat-card b').forEach(function (b) { b.setAttribute('data-text', b.textContent); });
  document.querySelectorAll('.pagehead h1, .hero h2, .services h2, .process h2, .cta h2, .row h3').forEach(function (h) {
    if (h.children.length) return; h.classList.add('fx'); h.setAttribute('data-text', h.textContent);
  });
})();

(function () {
  // main videos play (muted, looping) while they are on screen and pause when they leave; swapped out of the viewer they pause too
  function start(v) { if (!v.src && v.dataset.src) v.src = v.dataset.src; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  var vids = [].slice.call(document.querySelectorAll('.dp-main video'));
  if (vids.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) start(e.target); else e.target.pause(); }); }, { threshold: 0.5 });
    vids.forEach(function (v) { io.observe(v); });
  } else { vids.forEach(start); }

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
