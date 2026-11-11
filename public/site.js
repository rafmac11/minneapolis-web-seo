(function () {
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.menu-toggle');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  var groups = Array.prototype.slice.call(document.querySelectorAll('.nav details'));
  var desktop = window.matchMedia('(min-width: 1241px) and (hover: hover)');
  function closeAll(except) {
    groups.forEach(function (d) { if (d !== except) d.removeAttribute('open'); });
  }
  groups.forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open && desktop.matches) closeAll(d); });
    var t;
    d.parentElement.addEventListener('mouseenter', function () {
      if (!desktop.matches) return; clearTimeout(t); closeAll(d); d.setAttribute('open', '');
    });
    d.parentElement.addEventListener('mouseleave', function () {
      if (!desktop.matches) return; t = setTimeout(function () { d.removeAttribute('open'); }, 180);
    });
  });
  document.addEventListener('click', function (e) {
    if (desktop.matches && !e.target.closest('.nav')) closeAll(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAll(null);
      if (nav && nav.classList.contains('open')) { nav.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); toggle.focus(); }
    }
  });

  // header shadow on scroll
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }
  // scroll reveal (class js-anim is set early in <head> unless reduced motion is on)
  window.__revealReady = true;
  var root = document.documentElement;
  if (!root.classList.contains('js-anim')) return;
  var sel = '.sec .sec-head, .sec .prose, .cards > li, .steps > li, .rel > li, .media-fig, .steps-fig, .gallery figure, .faq details, .band-in, .final-in, .contact-cards > *, .contact-side, .svc-list li';
  var els = Array.prototype.slice.call(document.querySelectorAll(sel));
  els.forEach(function (el) {
    el.setAttribute('data-reveal', '');
    var sibs = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
    if (el.matches('.cards > li, .steps > li, .rel > li, .gallery figure, .faq details, .contact-cards > *, .svc-list li')) {
      el.style.setProperty('--d', (sibs % 6) * 70 + 'ms');
    }
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  els.forEach(function (el) { io.observe(el); });
})();
