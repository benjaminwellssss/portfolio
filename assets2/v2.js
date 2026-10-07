(function () {
  document.querySelectorAll('.stat-card b').forEach(function (b) { b.setAttribute('data-text', b.textContent); });
  document.querySelectorAll('.pagehead h1, .hero h2, .services h2, .process h2, .cta h2, .row h3').forEach(function (h) {
    if (h.children.length) return; h.classList.add('fx'); h.setAttribute('data-text', h.textContent);
  });
})();
