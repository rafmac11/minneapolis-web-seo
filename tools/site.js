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
})();
