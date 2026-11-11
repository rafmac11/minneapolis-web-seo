/* 404 globe: dotted 3D Earth on canvas with a Minneapolis pin and a flight arc to "the missing page". */
(function () {
  var canvas = document.getElementById('nf-globe');
  if (!canvas || !window.GLOBE_LAND) return;
  var ctx = canvas.getContext('2d');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var MODE = canvas.getAttribute('data-mode') || '404';
  var D = Math.PI / 180;

  // land dots -> unit vectors
  var src = window.GLOBE_LAND, N = src.length / 2;
  var px = new Float32Array(N), py = new Float32Array(N), pz = new Float32Array(N);
  for (var i = 0; i < N; i++) {
    var la = src[2 * i] / 10 * D, lo = src[2 * i + 1] / 10 * D;
    px[i] = Math.cos(la) * Math.sin(lo); py[i] = Math.sin(la); pz[i] = Math.cos(la) * Math.cos(lo);
  }
  function vec(lat, lon) { lat *= D; lon *= D; return [Math.cos(lat) * Math.sin(lon), Math.sin(lat), Math.cos(lat) * Math.cos(lon)]; }

  var MSP = vec(44.98, -93.27);
  var DESTS = [[-33.9, 18.4], [35.7, 139.7], [-41.3, 174.8], [64.1, -21.9], [-22.9, -43.2], [51.5, -0.1], [1.35, 103.8], [-34.6, -58.4], [21.3, -157.9], [60.2, 24.9], [-8.4, 115.2], [30.0, 31.2]];
  var dest = vec.apply(null, DESTS[Math.floor(Math.random() * DESTS.length)]);

  var HOME_ROT = 93.27 * D + (MODE === 'thanks' ? 0.12 : -0.3), HOME_TILT = MODE === 'thanks' ? 0.55 : 0.32;
  var rot = HOME_ROT, tilt = HOME_TILT, vr = reduce ? 0 : 0.0016, vt = 0;
  var W, H, R, cx, cy, dpr;
  function size() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    var r = canvas.getBoundingClientRect();
    W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    R = Math.min(W, H) * 0.4; cx = W / 2; cy = H / 2;
  }

  // rotate world vector by current view
  var cr, sr, ct, st;
  function view() { cr = Math.cos(rot); sr = Math.sin(rot); ct = Math.cos(tilt); st = Math.sin(tilt); }
  function proj(x, y, z, out) {
    var x1 = x * cr + z * sr, z1 = -x * sr + z * cr;
    var y2 = y * ct - z1 * st, z2 = y * st + z1 * ct;
    out[0] = cx + x1 * R; out[1] = cy - y2 * R; out[2] = z2; out[3] = x1; out[4] = y2;
    return out;
  }
  var P = [0, 0, 0, 0, 0];

  function slerp(a, b, t) {
    var d = Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
    var w = Math.acos(d), s = Math.sin(w) || 1;
    var k1 = Math.sin((1 - t) * w) / s, k2 = Math.sin(t * w) / s;
    return [a[0] * k1 + b[0] * k2, a[1] * k1 + b[1] * k2, a[2] * k1 + b[2] * k2];
  }

  var t0 = performance.now(), cycle = 5200;
  function draw(now) {
    view();
    ctx.clearRect(0, 0, W, H);

    // atmosphere glow
    var g = ctx.createRadialGradient(cx, cy, R * 0.9, cx, cy, R * 1.45);
    g.addColorStop(0, 'rgba(90,160,255,0.28)'); g.addColorStop(0.45, 'rgba(60,120,230,0.10)'); g.addColorStop(1, 'rgba(0,26,51,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R * 1.45, 0, 7); ctx.fill();

    // ocean sphere with rim light
    var s = ctx.createRadialGradient(cx - R * 0.35, cy - R * 0.4, R * 0.1, cx, cy, R);
    s.addColorStop(0, '#0d3a66'); s.addColorStop(0.75, '#062644'); s.addColorStop(1, '#03182e');
    ctx.fillStyle = s; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(140,190,255,0.35)'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.stroke();

    // land dots: far side shows faintly through the globe, near side bright toward the viewer
    var ds = Math.max(1.6, R / 135);
    for (var i = 0; i < N; i++) {
      proj(px[i], py[i], pz[i], P);
      if (P[2] <= 0) {
        ctx.fillStyle = 'rgba(120,170,230,0.07)';
        ctx.fillRect(P[0] - 0.7, P[1] - 0.7, 1.4, 1.4);
        continue;
      }
      var a = 0.4 + 0.6 * P[2];
      ctx.fillStyle = 'rgba(190,224,255,' + a.toFixed(3) + ')';
      var r = ds * (0.55 + 0.55 * P[2]);
      ctx.beginPath(); ctx.arc(P[0], P[1], r / 2, 0, 6.2832); ctx.fill();
    }
    // specular highlight
    var hl = ctx.createRadialGradient(cx - R * 0.45, cy - R * 0.5, 0, cx - R * 0.45, cy - R * 0.5, R * 0.9);
    hl.addColorStop(0, 'rgba(255,255,255,0.10)'); hl.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = hl; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.fill();

    if (MODE === 'thanks') { drawThanks(now); return; }
    // flight arc Minneapolis -> missing page
    var ph = reduce ? 0.62 : ((now - t0) % cycle) / cycle;
    var grow = Math.min(1, ph / 0.55), fade = ph > 0.85 ? 1 - (ph - 0.85) / 0.15 : 1;
    var steps = 64, last = null;
    for (var k = 0; k <= steps * grow; k++) {
      var t = k / steps, v = slerp(MSP, dest, t), h = 1 + 0.28 * Math.sin(Math.PI * t);
      proj(v[0] * h, v[1] * h, v[2] * h, P);
      var vis = P[2] > 0 || (P[3] * P[3] + P[4] * P[4]) > 1;
      if (last && vis && last[2]) {
        ctx.strokeStyle = 'rgba(255,' + Math.round(137 + 118 * t) + ',' + Math.round(0 + 200 * t) + ',' + (0.9 * fade).toFixed(3) + ')';
        ctx.lineWidth = 2.2; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(last[0], last[1]); ctx.lineTo(P[0], P[1]); ctx.stroke();
      }
      last = [P[0], P[1], vis];
    }
    // comet head
    if (grow < 1 && last && last[2]) {
      var hg = ctx.createRadialGradient(last[0], last[1], 0, last[0], last[1], 10);
      hg.addColorStop(0, 'rgba(255,255,255,0.95)'); hg.addColorStop(1, 'rgba(255,200,120,0)');
      ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(last[0], last[1], 10, 0, 7); ctx.fill();
    }

    // destination marker
    proj(dest[0], dest[1], dest[2], P);
    if (grow >= 1 && P[2] > 0) {
      ctx.globalAlpha = fade;
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(P[0], P[1], 3.5, 0, 7); ctx.fill();
      ctx.font = '700 13px "Bricolage Grotesque", system-ui, sans-serif';
      var label = '404 is here', tw = ctx.measureText(label).width;
      ctx.fillStyle = 'rgba(255,255,255,0.95)';
      var lx0 = P[0] + 10 + tw + 16 > W - 4 ? P[0] - 10 - tw - 16 : P[0] + 10;
      roundRect(lx0, P[1] - 26, tw + 16, 22, 6); ctx.fill();
      ctx.fillStyle = '#001A33'; ctx.fillText(label, lx0 + 8, P[1] - 10);
      ctx.globalAlpha = 1;
    }

    // Minneapolis pin with pulse
    proj(MSP[0], MSP[1], MSP[2], P);
    if (P[2] > 0) {
      var pulse = reduce ? 0.5 : ((now % 1800) / 1800);
      ctx.strokeStyle = 'rgba(255,137,0,' + (0.8 * (1 - pulse)).toFixed(3) + ')';
      ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(P[0], P[1], 4 + pulse * 16, 0, 7); ctx.stroke();
      ctx.fillStyle = '#FF8900'; ctx.beginPath(); ctx.arc(P[0], P[1], 4.5, 0, 7); ctx.fill();
      ctx.font = '600 12px "Bricolage Grotesque", system-ui, sans-serif';
      ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.fillText('Minneapolis', P[0] + 9, P[1] + 16);
    }
  }
  function arc(a, b, grow, alpha, warmToCool) {
    var steps = 64, last = null;
    for (var k = 0; k <= steps * grow; k++) {
      var t = k / steps, v = slerp(a, b, t), h = 1 + 0.26 * Math.sin(Math.PI * t);
      proj(v[0] * h, v[1] * h, v[2] * h, P);
      var vis = P[2] > 0 || (P[3] * P[3] + P[4] * P[4]) > 1;
      if (last && vis && last[2]) {
        var q = warmToCool ? t : 1 - t; // q=1 is the white end
        ctx.strokeStyle = 'rgba(255,' + Math.round(137 + 118 * q) + ',' + Math.round(200 * q) + ',' + (0.9 * alpha).toFixed(3) + ')';
        ctx.lineWidth = 2.2; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(last[0], last[1]); ctx.lineTo(P[0], P[1]); ctx.stroke();
      }
      last = [P[0], P[1], vis];
    }
    return last;
  }
  function head(pt) {
    if (!pt || !pt[2]) return;
    var hg = ctx.createRadialGradient(pt[0], pt[1], 0, pt[0], pt[1], 10);
    hg.addColorStop(0, 'rgba(255,255,255,0.95)'); hg.addColorStop(1, 'rgba(255,200,120,0)');
    ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(pt[0], pt[1], 10, 0, 7); ctx.fill();
  }
  // thank-you mode: requests fly in from around the world and land in Minneapolis
  var SOURCES = [[40.7, -74.0], [34.05, -118.25], [29.76, -95.37], [47.6, -122.3], [25.76, -80.19], [41.88, -87.63], [39.74, -104.99], [33.45, -112.07], [43.65, -79.38], [51.5, -0.1], [19.43, -99.13], [32.78, -96.8]];
  var srcVecs = SOURCES.map(function (c) { return vec(c[0], c[1]); });
  var TCYCLE = 7000, STAGGER = 520, FLY = 1500, landed = -1e9;
  function drawThanks(now) {
    var tt = reduce ? 4000 : now % TCYCLE, lastLand = -1e9;
    for (var i = 0; i < srcVecs.length; i++) {
      var st0 = i * STAGGER, e = tt - st0;
      if (e < 0) continue;
      var grow = Math.min(1, e / FLY), alpha = e > FLY ? Math.max(0, 1 - (e - FLY) / 1400) : 1;
      if (reduce) { grow = 1; alpha = 0.7; }
      if (alpha <= 0) continue;
      // source dot
      proj(srcVecs[i][0], srcVecs[i][1], srcVecs[i][2], P);
      if (P[2] > 0) { ctx.fillStyle = 'rgba(255,255,255,' + (0.8 * alpha).toFixed(3) + ')'; ctx.beginPath(); ctx.arc(P[0], P[1], 2.4, 0, 7); ctx.fill(); }
      var end = arc(srcVecs[i], MSP, grow, alpha, false);
      if (grow < 1) head(end); else lastLand = Math.max(lastLand, st0 + FLY);
    }
    var since = tt - lastLand;
    proj(MSP[0], MSP[1], MSP[2], P);
    if (P[2] > 0) {
      if (!reduce && since >= 0 && since < 700) { // landing burst
        var k = since / 700;
        ctx.strokeStyle = 'rgba(255,200,120,' + (0.9 * (1 - k)).toFixed(3) + ')'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(P[0], P[1], 6 + k * 34, 0, 7); ctx.stroke();
      }
      var glow = ctx.createRadialGradient(P[0], P[1], 0, P[0], P[1], 26);
      glow.addColorStop(0, 'rgba(255,137,0,0.55)'); glow.addColorStop(1, 'rgba(255,137,0,0)');
      ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(P[0], P[1], 26, 0, 7); ctx.fill();
      ctx.fillStyle = '#FF8900'; ctx.beginPath(); ctx.arc(P[0], P[1], 5.5, 0, 7); ctx.fill();
      ctx.font = '700 13px "Bricolage Grotesque", system-ui, sans-serif';
      var label = 'Request received', tw = ctx.measureText(label).width;
      var bw = tw + 34, bx = P[0] + 12 + bw > W - 4 ? P[0] - 12 - bw : P[0] + 12;
      ctx.fillStyle = 'rgba(255,255,255,0.96)'; roundRect(bx, P[1] - 30, bw, 24, 7); ctx.fill();
      ctx.fillStyle = '#1E9E4F'; ctx.beginPath(); ctx.arc(bx + 12, P[1] - 18, 4.5, 0, 7); ctx.fill();
      ctx.fillStyle = '#001A33'; ctx.fillText(label, bx + 22, P[1] - 13);
    }
  }
  function roundRect(x, y, w, h, r) {
    ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }

  // drag to spin, with inertia
  var dragging = false, lx = 0, ly = 0;
  canvas.addEventListener('pointerdown', function (e) { dragging = true; lx = e.clientX; ly = e.clientY; canvas.setPointerCapture(e.pointerId); canvas.classList.add('grabbing'); });
  canvas.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    var dx = e.clientX - lx, dy = e.clientY - ly; lx = e.clientX; ly = e.clientY;
    rot += dx * 0.006; tilt = Math.max(-0.9, Math.min(0.9, tilt + dy * 0.004));
    vr = dx * 0.0006; vt = dy * 0.0003;
    if (reduce) draw(performance.now());
  });
  function end() { dragging = false; canvas.classList.remove('grabbing'); }
  canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);

  var cycleStart = t0;
  function loop(now) {
    if (!dragging) {
      rot += vr; tilt = Math.max(-0.9, Math.min(0.9, tilt + vt));
      if (MODE === 'thanks') { // keep Minneapolis in view: gentle sway, ease back home after a drag
        vr *= 0.94; vt *= 0.94;
        rot += (HOME_ROT + 0.22 * Math.sin(now / 3800) - rot) * 0.015;
        tilt += (HOME_TILT - tilt) * 0.015;
      } else { vr += (0.0016 - vr) * 0.02; vt *= 0.94; }
    }
    if (now - cycleStart > cycle) { // new destination each flight
      cycleStart = now; t0 = now;
      dest = vec.apply(null, DESTS[Math.floor(Math.random() * DESTS.length)]);
    }
    draw(now);
    requestAnimationFrame(loop);
  }
  size();
  if (window.ResizeObserver) new ResizeObserver(function () { size(); if (reduce) draw(performance.now()); }).observe(canvas);
  if (reduce) { draw(performance.now()); } else { requestAnimationFrame(loop); }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (reduce) draw(performance.now()); });
})();
