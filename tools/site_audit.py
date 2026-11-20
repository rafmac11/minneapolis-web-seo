#!/usr/bin/env python3
"""Full SEO audit of the static site in public/ as Cloudflare Pages serves it.

Usage: python3 -I tools/site_audit.py public [--json report.json]

Exit code 0 = no errors (warnings/info may remain), 1 = errors found.
Checks: clean canonicals / og:url / JSON-LD URLs / sitemap / internal links / redirects,
title and description pixel widths (Arial 20px / 13px), uniqueness, mid-word cut-offs,
og:/twitter: copies in sync, one H1, html lang, viewport, JSON-LD validity, broken links and
missing assets, orphan pages, sitemap coverage, image alt / decorative handling / dimensions,
Cloudflare e-mail obfuscation (creates /cdn-cgi/l/email-protection links that 404 for crawlers),
duplicate main entities (cannibalisation) and the share of each page's main text that is unique.
"""
import glob, json, os, re, sys, collections
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Comment
from PIL import ImageFont

ORIGIN = "https://seo4web.pro"
TITLE_PX, DESC_PX = 580, 920
UNIQUE_MIN = 0.10          # share of main text that must be unique to the page
SHINGLE = 6

def _font(size):
    for p in ("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):  # metric-compatible with Arial
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("No Arial-compatible font found (install fonts-liberation)")
F20, F13 = _font(20), _font(13)
def px(text, font): return round(font.getlength(text))

root = sys.argv[1].rstrip("/")
want_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
issues = []  # (severity, page, check, message)
def add(sev, page, check, msg): issues.append((sev, page, check, msg))

def served(path):
    """URL path Cloudflare Pages serves a file at."""
    rel = "/" + os.path.relpath(path, root).replace(os.sep, "/")
    if rel.endswith("/index.html"): return rel[:-10]
    if rel.endswith(".html"): return rel[:-5]
    return rel

def resolve(urlpath):
    """File that serves a URL path, or None."""
    p = urlpath.split("#")[0].split("?")[0]
    if p.endswith("/"):
        f = root + p + "index.html"
        return f if os.path.exists(f) else None
    for cand in (root + p, root + p + ".html", root + p + "/index.html"):
        if os.path.isfile(cand): return cand
    return None

def clean_path_problem(p):
    p = p.split("#")[0].split("?")[0]
    if p.endswith(".html"): return "ends in .html (Pages redirects it)"
    if p.endswith("/index"): return "ends in /index"
    f = resolve(p)
    if f and f.endswith("index.html") and p != "/" and not p.endswith("/"):
        return "missing trailing slash (Pages redirects it)"
    return None

files = sorted(glob.glob(root + "/**/*.html", recursive=True))
pages = {}
for f in files:
    s = BeautifulSoup(open(f, encoding="utf-8").read(), "lxml")
    pages[served(f)] = (f, s)

def meta(s, **kw):
    m = s.find("meta", attrs=kw)
    return m.get("content") if m else None

indexable = {}
titles, descs, inbound = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(set)
entities = collections.defaultdict(list)
for url, (f, s) in pages.items():
    robots = (meta(s, name="robots") or "").lower()
    is404 = url == "/404"
    noindex = "noindex" in robots
    if not noindex and not is404: indexable[url] = s
    # --- head basics
    if not (s.html and s.html.get("lang")): add("error", url, "lang", "missing <html lang>")
    if not meta(s, name="viewport"): add("error", url, "viewport", "missing viewport meta")
    t = s.title.string.strip() if s.title and s.title.string else ""
    d = (meta(s, name="description") or "").strip()
    if not t: add("error", url, "title", "missing title")
    if not d: add("error", url, "description", "missing meta description")
    if not noindex and not is404:
        titles[t].append(url); descs[d].append(url)
    tw, dw = px(t, F20), px(d, F13)
    if tw > TITLE_PX: add("error", url, "title-width", f"title {tw}px > {TITLE_PX}px: {t!r}")
    if dw > DESC_PX: add("error", url, "desc-width", f"description {dw}px > {DESC_PX}px: {d!r}")
    if d and not re.search(r"[.!?]$", d): add("error", url, "desc-cutoff", f"description does not end in a full sentence: …{d[-40:]!r}")
    if d.endswith(("…", "...")): add("error", url, "desc-cutoff", "description ends in an ellipsis")
    for k, v, want in (("property", "og:title", t), ("name", "twitter:title", t),
                       ("property", "og:description", d), ("name", "twitter:description", d)):
        got = meta(s, **{k: v})
        if got is not None and got.strip() != want: add("error", url, "social-sync", f"{v} differs from page value")
        if got is None and not is404 and not noindex: add("warning", url, "social-sync", f"{v} missing")
    # --- canonical / og:url
    can = s.find("link", rel="canonical")
    expect = ORIGIN + (url if url.endswith("/") else url)
    if not is404:
        if not can: add("error", url, "canonical", "missing canonical")
        elif can["href"] != expect: add("error", url, "canonical", f"canonical {can['href']} != served URL {expect}")
        ogu = meta(s, property="og:url")
        if ogu and ogu != expect: add("error", url, "og:url", f"og:url {ogu} != {expect}")
    # --- H1
    h1s = s.find_all("h1")
    if len(h1s) != 1: add("error", url, "h1", f"{len(h1s)} <h1> elements")
    # --- JSON-LD
    for sc in s.find_all("script", type="application/ld+json"):
        try: ld = json.loads(sc.string)
        except Exception as e: add("error", url, "json-ld", f"invalid JSON-LD: {e}"); continue
        def walk(o, key=""):
            if isinstance(o, dict):
                for k, v in o.items(): yield from walk(v, k)
            elif isinstance(o, list):
                for v in o: yield from walk(v, key)
            elif isinstance(o, str) and key in ("url", "@id", "item") and o.startswith(ORIGIN):
                yield o
        for u in walk(ld):
            p = urlparse(u).path or "/"
            prob = clean_path_problem(p)
            if prob: add("error", url, "json-ld-url", f"{u}: {prob}")
            elif not resolve(p) and not p.startswith("/assets"): add("error", url, "json-ld-url", f"{u}: no such page")
        g = ld.get("@graph", [ld]) if isinstance(ld, dict) else ld
        for n in g:
            if n.get("@type") in ("WebPage", "AboutPage", "ContactPage") and isinstance(n.get("about"), dict) and n["about"].get("name") and not noindex and not is404:
                entities[("about", n["about"].get("name"))].append(url)
            if n.get("@type") == "Service":
                entities[("serviceType", n.get("serviceType") or "(none)")].append(url)
    # --- links
    for a in s.find_all("a", href=True):
        h = a["href"].strip()
        if h.startswith(ORIGIN): h = h[len(ORIGIN):] or "/"
        if "cdn-cgi" in h: add("error", url, "broken-link", f"link to {h}")
        if not h.startswith("/") or h.startswith("//"): continue
        p = h.split("#")[0]
        if not p: continue
        tgt = resolve(p)
        if not tgt: add("error", url, "broken-link", f"broken internal link {h}"); continue
        prob = clean_path_problem(p)
        if prob: add("error", url, "link-not-clean", f"{h}: {prob}")
        if tgt != f: inbound[served(tgt)].add(url)
    # --- Cloudflare e-mail obfuscation: e-mail addresses in body must be inside <!--email_off-->
    body_html = str(s.body) if s.body else ""
    stripped = re.sub(r"<!--email_off-->.*?<!--/email_off-->", "", body_html, flags=re.S)
    stripped = re.sub(r"<script\b.*?</script>|<noscript\b.*?</noscript>|<textarea\b.*?</textarea>", "", stripped, flags=re.S)
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", re.sub(r"<[^>]+>", lambda m: " ".join(re.findall(r'href="(mailto:[^"]*)"', m.group(0))), stripped)):
        add("error", url, "email-obfuscation", "e-mail address outside <!--email_off--> → Cloudflare rewrites it to /cdn-cgi/l/email-protection (404 for crawlers)")
    # --- assets
    refs = [(t.name, t.get("src")) for t in s.find_all(["img", "script", "source"]) if t.get("src")]
    refs += [(t.name, t.get("href")) for t in s.find_all("link") if t.get("href") and t.get("rel") and set(t["rel"]) & {"stylesheet", "icon", "apple-touch-icon", "preload", "alternate"}]
    for t in s.find_all(["img", "source", "link"]):
        for attr in ("srcset", "imagesrcset"):
            for part in (t.get(attr) or "").split(","):
                if part.strip(): refs.append((t.name, part.strip().split(" ")[0]))
    for tag, r in refs:
        if r.startswith(ORIGIN): r = r[len(ORIGIN):]
        if r.startswith("/") and not r.startswith("//") and not os.path.isfile(root + r.split("?")[0]):
            add("error", url, "missing-asset", f"{tag} {r}")
    for m in s.find_all("meta", property=re.compile("^og:image$")) + s.find_all("meta", attrs={"name": "twitter:image"}):
        p = urlparse(m["content"]).path
        if not os.path.isfile(root + p): add("error", url, "missing-asset", f"{m.get('property') or m.get('name')} {p}")
    # --- images
    for im in s.find_all("img"):
        alt = im.get("alt")
        if alt is None: add("error", url, "img-alt", f"no alt: {im.get('src')}")
        elif not alt.strip():
            hidden = im.get("aria-hidden") == "true" or im.find_parent(attrs={"aria-hidden": "true"}) is not None
            add("error" if not hidden else "warning", url, "img-alt",
                f"empty alt (SEO tools report it as missing; decorative images need aria-hidden=\"true\" plus a short alt): {im.get('src')}")
        if not (im.get("width") and im.get("height")): add("error", url, "img-size", f"no width/height: {im.get('src')}")

# --- duplicates
for t, us in titles.items():
    if len(us) > 1: add("error", ",".join(us), "dup-title", t)
for d, us in descs.items():
    if len(us) > 1: add("error", ",".join(us), "dup-desc", d[:60])
for (kind, name), us in entities.items():
    if len(us) > 1:  # a shared broad topic (about) is normal; a shared main entity (Service) competes
        add("warning" if kind == "serviceType" else "info", ",".join(us), "cannibalisation", f"{len(us)} pages share {kind} \"{name}\"")
# --- orphans
for u in indexable:
    if u != "/" and not (inbound[u] - {u}): add("error", u, "orphan", "no internal links from other pages")
# --- sitemap
sm = open(root + "/sitemap.xml").read()
locs = re.findall(r"<loc>([^<]*)</loc>", sm)
page_locs = [l for l in locs if not re.search(r"\.(webp|png|jpe?g|gif|svg)$", l)]
for l in page_locs:
    p = urlparse(l).path or "/"
    if not resolve(p): add("error", "sitemap", "sitemap", f"{l} does not exist")
    prob = clean_path_problem(p)
    if prob: add("error", "sitemap", "sitemap", f"{l}: {prob}")
    if p in pages and p not in indexable: add("error", "sitemap", "sitemap", f"{l} is noindex")
in_sm = {urlparse(l).path or "/" for l in page_locs}
for u in indexable:
    if u not in in_sm: add("error", u, "sitemap", "indexable page missing from sitemap")
for l in re.findall(r"<image:loc>([^<]*)</image:loc>", sm):
    if not os.path.isfile(root + urlparse(l).path): add("error", "sitemap", "sitemap", f"image {l} missing")
# --- redirects
if os.path.exists(root + "/_redirects"):
    for line in open(root + "/_redirects"):
        parts = line.split()
        if len(parts) >= 2 and not line.startswith("#"):
            tgt = parts[1]
            if tgt.startswith("/"):
                if not resolve(tgt): add("error", "_redirects", "redirect", f"{parts[0]} → {tgt} does not exist")
                prob = clean_path_problem(tgt)
                if prob: add("error", "_redirects", "redirect", f"{parts[0]} → {tgt}: {prob}")
# --- unique text share
def main_text(s):
    m = s.main or s.body
    m = BeautifulSoup(str(m), "lxml")
    for x in m.select("section.related, section.final, section.band, section.scope, nav, .serp, .crumbs, script"):
        x.decompose()
    return re.findall(r"[a-z0-9']+", m.get_text(" ").lower())
sh = {}
for u, s in indexable.items():
    w = main_text(s)
    sh[u] = [" ".join(w[i:i + SHINGLE]) for i in range(max(0, len(w) - SHINGLE + 1))]
count = collections.Counter()
for u, L in sh.items():
    for x in set(L): count[x] += 1
uniq = {}
for u, L in sh.items():
    if L:
        uniq[u] = sum(1 for x in L if count[x] == 1) / len(L)
        if uniq[u] < UNIQUE_MIN: add("error", u, "near-duplicate", f"only {uniq[u]:.0%} of main text unique")
# pairwise similarity (for information)
sets = {u: set(L) for u, L in sh.items()}
pairs = []
us = sorted(sets)
for i, a in enumerate(us):
    for b in us[i + 1:]:
        if sets[a] and sets[b]:
            j = len(sets[a] & sets[b]) / len(sets[a] | sets[b])
            if j > 0.05: pairs.append((round(j, 3), a, b))

# --- report
order = {"error": 0, "warning": 1, "info": 2}
issues.sort(key=lambda x: (order[x[0]], x[2], x[1]))
n_err = sum(1 for i in issues if i[0] == "error"); n_warn = sum(1 for i in issues if i[0] == "warning")
print(f"{len(files)} HTML files, {len(indexable)} indexable · {n_err} errors, {n_warn} warnings")
by = collections.Counter((i[0], i[2]) for i in issues)
for (sev, chk), n in sorted(by.items(), key=lambda x: (order[x[0][0]], x[0][1])): print(f"  {sev:7} {chk:20} {n}")
print()
for sev, page, chk, msg in issues: print(f"[{sev}] {chk} {page}: {msg}")
print("\nUnique main-text share (6-word shingles):")
for u in sorted(uniq, key=uniq.get): print(f"  {uniq[u]:6.1%}  {u}")
if pairs:
    print("\nMost similar page pairs (Jaccard of shingles):")
    for j, a, b in sorted(pairs, reverse=True)[:10]: print(f"  {j:.3f}  {a}  {b}")
if want_json:
    json.dump({"issues": issues, "unique": uniq, "pairs": pairs}, open(want_json, "w"), indent=1)
sys.exit(1 if n_err else 0)
