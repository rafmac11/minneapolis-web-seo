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

// WebMCP tools for in-browser AI agents (https://webmachinelearning.github.io/webmcp/).
// Read-only lookups plus request_quote, which only opens the callback form; it never submits anything.
(function () {
  var mc = document.modelContext || navigator.modelContext;
  if (!mc || typeof mc.registerTool !== 'function') return;
  var dataUrl = '/site-data.json';
  var cache = null;
  function load() {
    if (!cache) cache = fetch(dataUrl, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error('Could not load ' + dataUrl);
      return r.json();
    }).catch(function (e) { cache = null; throw e; });
    return cache;
  }
  function norm(s) { return String(s || '').toLowerCase(); }
  function register(tool) {
    try {
      var p = mc.registerTool(tool);
      if (p && typeof p.catch === 'function') p.catch(function () {});
    } catch (e) { /* tool unavailable in this browser: skip */ }
  }

  register({
    name: 'search_services',
    description: 'Search the services offered by Website Design & SEO Solutions (Minneapolis, MN): website design, SEO, marketing, creative and contractor lead generation. Returns matching services with their page URL and a short description.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Keywords to match, for example "wordpress", "google ads" or "snow removal". Leave empty to list everything.' },
        category: { type: 'string', enum: ['Web Design', 'SEO', 'Marketing', 'Lead Generation', 'Creative'], description: 'Limit results to one service category.' },
        limit: { type: 'integer', minimum: 1, maximum: 25, description: 'Maximum number of results (default 10).' }
      }
    },
    annotations: { readOnlyHint: true },
    execute: function (input) {
      input = input || {};
      return load().then(function (d) {
        var words = norm(input.query).split(/\s+/).filter(Boolean);
        var cat = norm(input.category);
        var out = d.services.filter(function (s) {
          if (cat && norm(s.category) !== cat) return false;
          var hay = norm([s.name, s.category, s.title, s.description, s.keywords].join(' '));
          return words.every(function (w) { return hay.indexOf(w) !== -1; });
        }).slice(0, Math.max(1, Math.min(25, input.limit || 10))).map(function (s) {
          return { name: s.name, category: s.category, url: s.url, description: s.description };
        });
        return { count: out.length, services: out };
      });
    }
  });

  register({
    name: 'get_business_info',
    description: 'Get contact details, office address, opening hours, service areas, the list of services and the pricing policy of Website Design & SEO Solutions.',
    inputSchema: { type: 'object', properties: {} },
    annotations: { readOnlyHint: true },
    execute: function () {
      return load().then(function (d) {
        var b = JSON.parse(JSON.stringify(d.business));
        b.services = d.services.map(function (s) { return { name: s.name, category: s.category, url: s.url }; });
        return b;
      });
    }
  });

  register({
    name: 'request_quote',
    description: 'Open the free-callback request form so the visitor can fill it in and send it themselves. This tool does not submit anything. Optionally pass the service the visitor is interested in.',
    inputSchema: {
      type: 'object',
      properties: {
        service: { type: 'string', description: 'Optional service name or keyword, for example "local SEO".' }
      }
    },
    annotations: { readOnlyHint: false },
    execute: function (input) {
      input = input || {};
      return load().catch(function () { return { services: [] }; }).then(function (d) {
        var q = norm(input.service), match = null;
        if (q) d.services.some(function (s) {
          if (norm(s.name + ' ' + s.title + ' ' + s.keywords).indexOf(q) !== -1) { match = s; return true; }
          return false;
        });
        var form = document.getElementById('form');
        if (form && /^\/contact\/?$/.test(location.pathname)) {
          form.scrollIntoView({ behavior: 'smooth', block: 'start' });
          var field = form.querySelector('input, select, textarea, iframe');
          if (field) { try { field.focus({ preventScroll: true }); } catch (e) {} }
          return { opened: true, url: location.origin + '/contact/#form', service: match ? match.name : (input.service || null),
                   note: 'The callback form is open. The visitor fills it in and sends it; nothing was submitted.' };
        }
        var url = '/contact/' + (match ? '?service=' + encodeURIComponent(match.slug) : '') + '#form';
        setTimeout(function () { location.href = url; }, 60);
        return { opened: true, url: location.origin + url, service: match ? match.name : (input.service || null),
                 note: 'Opening the contact page with the callback form. The visitor fills it in and sends it; nothing was submitted.' };
      });
    }
  });
})();
