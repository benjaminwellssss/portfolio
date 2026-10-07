(function () {
  document.querySelectorAll('.stat-card b').forEach(function (b) { b.setAttribute('data-text', b.textContent); });
  document.querySelectorAll('.pagehead h1, .hero h2, .services h2, .process h2, .cta h2, .row h3').forEach(function (h) {
    if (h.children.length) return; h.classList.add('fx'); h.setAttribute('data-text', h.textContent);
  });
})();

(function () {
  var vids = [].slice.call(document.querySelectorAll('.dp-main video'));
  if (!vids.length) return;
  function start(v) { if (!v.src && v.dataset.src) v.src = v.dataset.src; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) start(e.target); else e.target.pause(); }); }, { threshold: 0.5 });
    vids.forEach(function (v) { io.observe(v); });
  } else { vids.forEach(start); }
  document.querySelectorAll('[data-play]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      var v = a.closest('.dp').querySelector('.dp-main video');
      if (v) { v.scrollIntoView({ behavior: 'smooth', block: 'center' }); start(v); }
    });
  });
})();
