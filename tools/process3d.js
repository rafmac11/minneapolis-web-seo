/* 3D process pipeline: isometric platforms per step, a lead orb travelling through them,
   synced with the step list. One canvas per .proc3d element. */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ICONS = {
    phone: 'M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z',
    form: 'M7 3h7l4 4v14H7z M14 3v4h4 M10 12h5 M10 16h5',
    message: 'M4 5h16v11H10l-5 4v-4H4z M8.5 10.5h.01 M12 10.5h.01 M15.5 10.5h.01',
    pin: 'M12 21s-6-6.2-6-11a6 6 0 0 1 12 0c0 4.8-6 11-6 11z M12 7.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 1 0 0-5z',
    calendar: 'M4 6h16v14H4z M4 10h16 M8 3v5 M16 3v5 M9 15l2 2 4-4',
    star: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z',
    repeat: 'M17 2l3 3-3 3 M4 11V9a4 4 0 0 1 4-4h12 M7 22l-3-3 3-3 M20 13v2a4 4 0 0 1-4 4H4',
    chart: 'M4 20h16 M7 16v-5 M12 16V7 M17 16v-8',
    search: 'M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 1 0 0-13z M15.5 15.5L20 20',
    check: 'M5 12.5l4.5 4.5L19 7',
    target: 'M12 3a9 9 0 1 0 0 18 9 9 0 1 0 0-18z M12 7.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 1 0 0-9z M12 11a1 1 0 1 0 0 2 1 1 0 1 0 0-2z',
    tool: 'M14.5 6.5a4 4 0 0 0 5 5l-8 8a2.1 2.1 0 0 1-3-3l8-8a4 4 0 0 0-2-2z',
    bolt: 'M13 2L4 14h7l-1 8 9-12h-7z',
    rocket: 'M12 2c3 2.5 4.5 6 4.5 10l-2 3h-5l-2-3c0-4 1.5-7.5 4.5-10z M12 8.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 1 0 0-3z M9.5 15l-2.5 4 3-1 M14.5 15l2.5 4-3-1 M12 18v4',
    shield: 'M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6z M8.5 12l2.5 2.5 4.5-4.5',
    layout: 'M4 4h16v16H4z M4 9h16 M10 9v11',
    pen: 'M4 20l4-1 11-11-3-3L5 16z M14 6l3 3',
    code: 'M8 7l-5 5 5 5 M16 7l5 5-5 5 M13.5 5l-3 14',
    users: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 1 0 0 7z M2.5 20c.5-3.5 3.2-5.5 6.5-5.5s6 2 6.5 5.5 M16 4.5a3.5 3.5 0 0 1 0 6.5 M18 14.8c2 .7 3.2 2.5 3.5 5.2',
    trend: 'M3 17l6-6 4 4 8-8 M15 7h6v6'
  };
  var paths = {};
  function icon(k) { return paths[k] || (paths[k] = new Path2D(ICONS[k] || ICONS.check)); }

  function setup(box) {
    var canvas = box.querySelector('canvas');
    var ctx = canvas.getContext('2d');
    var keys = (canvas.getAttribute('data-icons') || '').split(',').filter(Boolean);
    var n = keys.length; if (!n) return;
    var list = box.closest('.steps-sec') && box.closest('.steps-sec').querySelectorAll('.steps > li');
    list = list ? Array.prototype.slice.call(list) : [];

    // world layout: cascading zigzag staircase
    var slabs = [];
    for (var i = 0; i < n; i++) slabs.push({ x: (i % 2) * 2.1, y: i * 1.55, z: (n - 1 - i) * 0.62 });
    var W = 1.5, Dp = 1.5, T = 0.3;

    var dpr, cw, ch, scale, ox, oy, theta = 0, elev = 1, tmx = 0, tmy = 0, mx = 0, my = 0;
    function iso(x, y, z) {
      var c = Math.cos(theta), s = Math.sin(theta);
      var xr = x * c - y * s, yr = x * s + y * c;
      return [ox + (xr - yr) * 0.866 * scale, oy + ((xr + yr) * 0.5 * elev - z) * scale];
    }
    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      var r = canvas.getBoundingClientRect(); cw = r.width; ch = r.height;
      canvas.width = Math.round(cw * dpr); canvas.height = Math.round(ch * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      // fit bounds at rest pose
      theta = 0; elev = 1; scale = 1; ox = 0; oy = 0;
      var minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
      slabs.forEach(function (sb) {
        [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(function (d) {
          [sb.z + 1.35, sb.z - T - 0.9].forEach(function (zz) {
            var p = iso(sb.x + d[0] * W / 2, sb.y + d[1] * Dp / 2, zz);
            minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]); minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]);
          });
        });
      });
      scale = Math.min(cw * 0.84 / (maxX - minX), ch * 0.9 / (maxY - minY));
      ox = cw / 2 - (minX + maxX) / 2 * scale; oy = ch / 2 - (minY + maxY) / 2 * scale;
    }

    var DWELL = 1500, TRAVEL = 750, STAGE = DWELL + TRAVEL, start = performance.now(), forced = -1, forcedAt = 0;
    function stageAt(now) {
      var t = now - start, k = Math.floor(t / STAGE) % (n + 1); // extra beat at the end before looping
      return { i: Math.min(k, n - 1), f: (t % STAGE), loopEnd: k === n };
    }

    function poly(pts, fill, stroke) {
      ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
      for (var j = 1; j < pts.length; j++) ctx.lineTo(pts[j][0], pts[j][1]);
      ctx.closePath(); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1; ctx.stroke(); }
    }

    function drawSlab(sb, z, state, glow) {
      var hx = W / 2, hy = Dp / 2;
      var a = iso(sb.x - hx, sb.y - hy, z), b = iso(sb.x + hx, sb.y - hy, z), c = iso(sb.x + hx, sb.y + hy, z), d = iso(sb.x - hx, sb.y + hy, z);
      var b2 = iso(sb.x + hx, sb.y - hy, z - T), c2 = iso(sb.x + hx, sb.y + hy, z - T), d2 = iso(sb.x - hx, sb.y + hy, z - T);
      // soft shadow on the floor
      var sh = iso(sb.x + 0.25, sb.y + 0.25, -0.9);
      var sg = ctx.createRadialGradient(sh[0], sh[1], 0, sh[0], sh[1], scale * 1.1);
      sg.addColorStop(0, 'rgba(0,10,25,' + (0.35 + glow * 0.15) + ')'); sg.addColorStop(1, 'rgba(0,10,25,0)');
      ctx.fillStyle = sg; ctx.beginPath(); ctx.ellipse(sh[0], sh[1], scale * 1.2, scale * 0.6, 0, 0, 7); ctx.fill();
      var active = state === 2, done = state === 1;
      poly([b, c, c2, b2], active ? '#C25E00' : done ? '#1B5A92' : '#0A2848');
      poly([d, c, c2, d2], active ? '#8A4300' : done ? '#123F6B' : '#071E38');
      var tg = ctx.createLinearGradient(a[0], a[1], c[0], c[1]);
      if (active) { tg.addColorStop(0, '#FFC06A'); tg.addColorStop(1, '#FF8900'); }
      else if (done) { tg.addColorStop(0, '#4A97DB'); tg.addColorStop(1, '#2468A6'); }
      else { tg.addColorStop(0, '#1C4C7D'); tg.addColorStop(1, '#0F3660'); }
      poly([a, b, c, d], tg, active ? 'rgba(255,230,190,.9)' : done ? 'rgba(200,230,255,.7)' : 'rgba(150,200,255,.35)');
      // inner inset line on top face
      var k = 0.72, ia = iso(sb.x - hx * k, sb.y - hy * k, z), ib = iso(sb.x + hx * k, sb.y - hy * k, z), ic = iso(sb.x + hx * k, sb.y + hy * k, z), id = iso(sb.x - hx * k, sb.y + hy * k, z);
      poly([ia, ib, ic, id], null, active ? 'rgba(255,255,255,.55)' : 'rgba(150,200,255,.18)');
      if (glow > 0) { // halo
        var cc = iso(sb.x, sb.y, z), hg = ctx.createRadialGradient(cc[0], cc[1], 0, cc[0], cc[1], scale * 1.6);
        hg.addColorStop(0, 'rgba(255,150,40,' + (0.35 * glow) + ')'); hg.addColorStop(1, 'rgba(255,150,40,0)');
        ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(cc[0], cc[1], scale * 1.6, 0, 7); ctx.fill();
      }
    }

    function drawCard(sb, z, key, state, num, now) {
      var base = iso(sb.x, sb.y, z), top = iso(sb.x, sb.y, z + 0.95);
      var active = state === 2, s = Math.max(30, scale * 0.62) * (active ? 1.12 : 1);
      // light beam
      var bg = ctx.createLinearGradient(base[0], base[1], top[0], top[1]);
      bg.addColorStop(0, active ? 'rgba(255,170,60,.55)' : 'rgba(140,200,255,.25)'); bg.addColorStop(1, 'rgba(140,200,255,0)');
      ctx.fillStyle = bg; ctx.beginPath();
      ctx.moveTo(base[0] - s * 0.32, base[1]); ctx.lineTo(top[0] - s * 0.5, top[1]); ctx.lineTo(top[0] + s * 0.5, top[1]); ctx.lineTo(base[0] + s * 0.32, base[1]); ctx.closePath(); ctx.fill();
      var bob = reduce ? 0 : Math.sin(now / 700 + num) * 3;
      var x = top[0] - s / 2, y = top[1] - s / 2 + bob;
      ctx.save();
      ctx.shadowColor = active ? 'rgba(255,137,0,.8)' : 'rgba(80,160,255,.35)'; ctx.shadowBlur = active ? 24 : 12;
      ctx.fillStyle = active ? '#FF8900' : 'rgba(12,44,78,.92)';
      rr(x, y, s, s, s * 0.24); ctx.fill();
      ctx.restore();
      ctx.strokeStyle = active ? 'rgba(255,255,255,.85)' : 'rgba(150,205,255,.55)'; ctx.lineWidth = 1.2; rr(x, y, s, s, s * 0.24); ctx.stroke();
      ctx.save(); ctx.translate(x + s * 0.2, y + s * 0.2); ctx.scale(s * 0.6 / 24, s * 0.6 / 24);
      ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.strokeStyle = active ? '#001A33' : '#BFE0FF'; ctx.stroke(icon(key));
      ctx.restore();
      if (state === 1) { // completed tick
        ctx.fillStyle = '#1E9E4F'; ctx.beginPath(); ctx.arc(x + s - 2, y + 2, s * 0.17, 0, 7); ctx.fill();
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.6; ctx.beginPath();
        ctx.moveTo(x + s - 2 - s * 0.08, y + 2); ctx.lineTo(x + s - 2 - s * 0.02, y + 2 + s * 0.06); ctx.lineTo(x + s - 2 + s * 0.09, y + 2 - s * 0.06); ctx.stroke();
      }
      // step number
      ctx.font = '780 ' + Math.round(Math.max(13, s * 0.36)) + 'px "Bricolage Grotesque", system-ui, sans-serif';
      ctx.fillStyle = active ? '#FFB04D' : state === 1 ? 'rgba(191,224,255,.85)' : 'rgba(191,224,255,.5)';
      ctx.fillText(String(num).padStart(2, '0'), x + s + 8, y + s * 0.42);
    }
    function rr(x, y, w, h, r) {
      ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
    }

    function floor(now) {
      var minx = -1.4, maxx = 3.6, miny = -1.4, maxy = (n - 1) * 1.55 + 1.4;
      for (var gx = minx; gx <= maxx; gx += 0.5) for (var gy = miny; gy <= maxy; gy += 0.5) {
        var p = iso(gx, gy, -0.9);
        ctx.fillStyle = 'rgba(120,180,240,0.16)'; ctx.fillRect(p[0] - 0.8, p[1] - 0.8, 1.6, 1.6);
      }
    }

    function frame(now) {
      // pose: gentle sway + pointer parallax
      mx += (tmx - mx) * 0.06; my += (tmy - my) * 0.06;
      theta = (reduce ? 0 : 0.07 * Math.sin(now / 3200)) + mx * 0.22;
      elev = 1 + my * 0.12;
      ctx.clearRect(0, 0, cw, ch);
      floor(now);

      var st = reduce ? { i: forced >= 0 ? forced : n - 1, f: DWELL, loopEnd: false } : stageAt(now);
      if (forced >= 0 && !reduce) { st = { i: forced, f: Math.min(now - forcedAt, DWELL), loopEnd: false }; if (now - forcedAt > DWELL) { start = now - forced * STAGE - DWELL; forced = -1; } }
      var cur = st.loopEnd ? -1 : st.i, travelling = !st.loopEnd && st.f > DWELL && st.i < n - 1, tp = travelling ? (st.f - DWELL) / TRAVEL : 0;
      if (st.loopEnd) cur = -2;

      for (var i = 0; i < n; i++) {
        var sb = slabs[i], z = sb.z + (reduce ? 0 : Math.sin(now / 900 + i * 1.3) * 0.04);
        var state = cur === -2 ? 1 : i < cur ? 1 : i === cur ? 2 : 0;
        if (reduce && forced < 0) state = i === n - 1 ? 2 : 1;
        var glow = state === 2 ? (0.7 + 0.3 * Math.sin(now / 250)) : 0;
        drawSlab(sb, z, state, glow);
        if (i < n - 1) { // connector tube
          var nb = slabs[i + 1], p0 = iso(sb.x, sb.y, z + 0.02), p1 = iso(nb.x, nb.y, nb.z + 0.02);
          ctx.save(); ctx.lineCap = 'round';
          ctx.strokeStyle = 'rgba(140,200,255,.18)'; ctx.lineWidth = 7; ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); ctx.stroke();
          ctx.setLineDash([4, 9]); ctx.lineDashOffset = reduce ? 0 : -now / 40;
          ctx.strokeStyle = i < cur || cur === -2 ? 'rgba(255,170,70,.9)' : 'rgba(170,215,255,.55)'; ctx.lineWidth = 2;
          ctx.beginPath(); ctx.moveTo(p0[0], p0[1]); ctx.lineTo(p1[0], p1[1]); ctx.stroke();
          ctx.restore();
        }
      }
      // cards drawn last so they float above everything
      for (var j = 0; j < n; j++) {
        var sj = slabs[j], zj = sj.z + (reduce ? 0 : Math.sin(now / 900 + j * 1.3) * 0.04);
        var stj = cur === -2 ? 1 : j < cur ? 1 : j === cur ? 2 : 0;
        if (reduce && forced < 0) stj = j === n - 1 ? 2 : 1;
        drawCard(sj, zj, keys[j], stj, j + 1, now);
      }
      // orb
      if (!reduce && cur >= 0) {
        var a = slabs[cur], b = slabs[Math.min(cur + 1, n - 1)], e = tp < 0.5 ? 2 * tp * tp : 1 - Math.pow(-2 * tp + 2, 2) / 2;
        var ox_ = a.x + (b.x - a.x) * e, oy_ = a.y + (b.y - a.y) * e, oz = a.z + (b.z - a.z) * e + 0.18 + Math.sin(Math.PI * e) * 0.9;
        var p = iso(ox_, oy_, oz), r = Math.max(7, scale * 0.16);
        var og = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], r * 3);
        og.addColorStop(0, 'rgba(255,255,255,1)'); og.addColorStop(0.25, 'rgba(255,200,120,.95)'); og.addColorStop(1, 'rgba(255,137,0,0)');
        ctx.fillStyle = og; ctx.beginPath(); ctx.arc(p[0], p[1], r * 3, 0, 7); ctx.fill();
      }
      // sync list
      for (var q = 0; q < list.length; q++) list[q].classList.toggle('is-active', q === cur || (reduce && forced < 0 && false));
    }

    var running = false, visible = false;
    function loop(now) { if (!visible) { running = false; return; } frame(now); requestAnimationFrame(loop); }
    function kick() { if (!running && visible) { running = true; requestAnimationFrame(loop); } }
    size();
    if (window.ResizeObserver) new ResizeObserver(function () { size(); frame(performance.now()); }).observe(canvas);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) { if (!running) start = performance.now() - 200; kick(); } }, { threshold: 0.15 }).observe(canvas);
    else { visible = true; kick(); }
    box.addEventListener('pointermove', function (e) { var r = canvas.getBoundingClientRect(); tmx = ((e.clientX - r.left) / r.width - 0.5) * 2; tmy = ((e.clientY - r.top) / r.height - 0.5) * 2; kick(); });
    box.addEventListener('pointerleave', function () { tmx = 0; tmy = 0; });
    list.forEach(function (li, idx) {
      var jump = function () { forced = idx; forcedAt = performance.now(); if (reduce) frame(performance.now()); kick(); };
      li.addEventListener('mouseenter', jump); li.addEventListener('click', jump);
    });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { frame(performance.now()); });
    frame(performance.now());
  }
  Array.prototype.forEach.call(document.querySelectorAll('.proc3d'), setup);
})();
