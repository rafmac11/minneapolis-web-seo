#!/usr/bin/env python3
"""Rebuild the seo4web.pro static site from the exported content with a new design,
fixed SEO metadata/schema and contextual interlinking.
Usage: python3 -I build.py <src_dir> <out_dir>
"""
import sys, os, re, json, shutil, html, datetime, copy
from bs4 import BeautifulSoup, NavigableString, Tag

SRC, OUT = sys.argv[1], sys.argv[2]
ORIGIN = "https://seo4web.pro"
BRAND = "Website Design & SEO Solutions"
PHONE_DISPLAY = "(612) 230-0815"
PHONE_TEL = "+16122300815"
PHONE_LD = "+1-612-230-0815"
EMAIL = "info@seo4web.pro"
STREET, CITY, REGION, ZIP = "530 N 3rd St", "Minneapolis", "MN", "55401"
TODAY = datetime.date.today().isoformat()
FONTS = "/home/claude/tools/node_modules/@fontsource-variable"
import hashlib
def _hash(*names):
    h = hashlib.sha1()
    for n in names:
        h.update(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), n), "rb").read())
    return h.hexdigest()[:10]
# content-based cache busting: any change to a file gives it a new URL
CSS_V = _hash("site.css")
JS_V = _hash("site.js")
GLOBE_V = _hash("globe.js", "globe-points.js")
PROC_V = _hash("process3d.js")
FORM_V = _hash("lead-form.css", "lead-form.js")
PROC_TAG = f'\n<script src="/assets/process3d.js?v={PROC_V}" defer></script>'

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("leadgen_content", os.path.join(os.path.dirname(os.path.abspath(__file__)), "leadgen_content.py"))
LG = _ilu.module_from_spec(_spec); _spec.loader.exec_module(LG)
_spec2 = _ilu.spec_from_file_location("entities", os.path.join(os.path.dirname(os.path.abspath(__file__)), "entities.py"))
ENT = _ilu.module_from_spec(_spec2); _spec2.loader.exec_module(ENT)

# ---------------------------------------------------------------- site map
NAV = [
    ("Web Design", [("minneapolis-web-design-companies", "Web Design"),
                    ("web-developers-minneapolis", "Web Development"),
                    ("wordpress-design-minneapolis", "WordPress Design"),
                    ("design-agency-minneapolis", "Design Agency"),
                    ("graphic-design-firm-minneapolis", "Graphic Design")]),
    ("SEO", [("", "SEO Services"),
             ("minneapolis-seo-consultant", "SEO Consulting"),
             ("local-seo-minneapolis", "Local SEO")]),
    ("Marketing", [("digital-marketing-minneapolis-mn", "Digital Marketing"),
                   ("marketing-minneapolis", "Marketing Services"),
                   ("online-marketing-minneapolis", "Online Marketing"),
                   ("minneapolis-marketing-firms", "Marketing Firm"),
                   ("minneapolis-ppc-management", "PPC Management"),
                   ("social-media-marketing-minneapolis", "Social Media Marketing")]),
    ("Lead Generation", [(p["slug"], p["nav"]) for p in LG.PAGES]),
    ("Creative", [("advertising-companies-minneapolis", "Advertising"),
                          ("creative-agencies-minneapolis", "Creative Agency"),
                          ("branding-agency-minneapolis", "Branding")]),
]
CLUSTER = {}
SHORT = {}
for group, items in NAV:
    for slug, label in items:
        CLUSTER[slug] = group
        SHORT[slug] = label
SERVICES = [s for g, items in NAV for s, _ in items if s]

# Contextual anchor phrases -> target page. Longer / more specific phrases first.
LINK_PHRASES = [  # (regex, target) — earlier entries win ties
    (r"local SEO|Google Business Profile|local search(?: results)?|map results", "local-seo-minneapolis"),
    (r"SEO consultants?|SEO consulting|SEO audits?|technical SEO|keyword research", "minneapolis-seo-consultant"),
    (r"search engine optimization|organic search(?: visibility)?|organic visibility", ""),
    (r"pay-per-click|paid search|Google Ads|PPC(?: campaigns?| management)?|paid (?:advertising|campaigns?|media)", "minneapolis-ppc-management"),
    (r"social media(?: marketing)?", "social-media-marketing-minneapolis"),
    (r"digital marketing|digital (?:channels|campaigns?)|conversion tracking", "digital-marketing-minneapolis-mn"),
    (r"online marketing|online (?:presence|visibility|channels|campaigns?|advertising|audiences?|customers|search|reputation|growth|leads|marketplace|sales|research)|business online", "online-marketing-minneapolis"),
    (r"marketing (?:firms?|compan(?:y|ies)|agency|agencies|partners?|teams?)|agency relationship|full-service", "minneapolis-marketing-firms"),
    (r"marketing (?:strategy|strategies|plans?|services|programs?|campaigns?|priorities|support|planning|program|tasks)", "marketing-minneapolis"),
    (r"WordPress", "wordpress-design-minneapolis"),
    (r"web(?:site)? development|web developers?|content management systems?|responsive (?:design|layouts?|websites?)|(?:web|website|WordPress|front-end) developers?", "web-developers-minneapolis"),
    (r"website design|web design|website redesigns?|website designers?|landing pages?|page structure|site structure|site navigation", "minneapolis-web-design-companies"),
    (r"design agenc(?:y|ies)|visual design|user experience|redesigns?", "design-agency-minneapolis"),
    (r"graphic design(?:ers?)?|logo design|visual assets|marketing materials|marketing collateral|visual systems?", "graphic-design-firm-minneapolis"),
    (r"creative (?:agenc(?:y|ies)|direction|work|teams?|concepts?|production|campaigns?|strategy|assets)", "creative-agencies-minneapolis"),
    (r"brand strategy|brand identity|branding|visual identity|brand (?:positioning|voice|standards|guidelines|messaging|consistency|recognition)", "branding-agency-minneapolis"),
    (r"advertising(?: campaigns?)?", "advertising-companies-minneapolis"),
    (r"(?:contractor |home service )?lead generation", LG.HUB),
    (r"landscap(?:ing|ers?)(?: compan(?:y|ies)| projects?| work)?", "landscaping-lead-generation"),
    (r"(?:irrigation|sprinkler)(?: systems?| compan(?:y|ies)| work)?", "irrigation-lead-generation"),
    (r"snow (?:removal|plowing)(?: compan(?:y|ies)| contracts?)?", "snow-removal-lead-generation"),
    (r"concrete (?:contractors?|work|projects?)", "concrete-contractor-lead-generation"),
    (r"towing(?: compan(?:y|ies))?|tow trucks?", "towing-lead-generation"),
    (r"home service contractors?|contractors", LG.HUB),
]
MAX_CONTEXT_LINKS = 6
MAX_INBOUND = 6

# ---------------------------------------------------------------- helpers
def url(slug):
    return "/" if not slug else f"/{slug}/"

def absu(slug):
    return ORIGIN + url(slug)

def fix_brand(s):
    return re.sub(r"website design &(amp;)? SEO Solutions", lambda m: "Website Design &" + (m.group(1) or "") + " SEO Solutions", s)

def norm_href(h):
    if h.startswith(("tel:", "mailto:", "http", "#")):
        return h
    h = re.sub(r"^(\.\./)+", "", h)
    if h in ("index.html", ""):
        return "/"
    m = re.match(r"([\w-]+)/index\.html$", h)
    return f"/{m.group(1)}/" if m else "/" + h

def norm_src(s):
    return "/" + re.sub(r"^(\.\./)+", "", s)

def esc(s):
    return html.escape(s, quote=True)

def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""

ALLOWED = {"a", "strong", "em", "b", "i", "br", "code"}
def inner(el):
    """Clean inner HTML of a paragraph-like element."""
    el = copy.copy(el)
    for t in el.find_all(True):
        if t.name not in ALLOWED:
            t.unwrap(); continue
        attrs = {}
        if t.name == "a" and t.get("href"):
            attrs["href"] = norm_href(t["href"])
        t.attrs = attrs
    out = "".join(str(c) for c in el.contents)
    out = re.sub(r"\s+", " ", out).strip()
    # tidy up lowercase "seo" in legacy anchor text
    out = re.sub(r"\bseo\b", "SEO", out)
    out = out.replace("a SEO", "an SEO").replace("Minneapolis homeowners rely on", "Minneapolis businesses rely on")
    return fix_brand(out)

def img_data(img):
    d = {"src": norm_src(img["src"]), "alt": fix_brand(img.get("alt", "")),
         "w": img.get("width"), "h": img.get("height"), "srcset": ""}
    if "field-presence" in d["src"]:  # shared photo: original alt texts described other scenes
        d["alt"] = "Website Design & SEO Solutions branded service van at a client's home in a Minneapolis neighborhood"
    if img.get("srcset"):
        parts = []
        for p in img["srcset"].split(","):
            u, wd = p.strip().rsplit(" ", 1)
            parts.append(f"{norm_src(u)} {wd}")
        d["srcset"] = ", ".join(parts)
    return d

def render_img(d, sizes, eager=False, cls=""):
    a = [f'src="{esc(d["src"])}"', f'alt="{esc(d["alt"])}"']
    if d["srcset"]:
        a.append(f'srcset="{esc(d["srcset"])}" sizes="{sizes}"')
    if d["w"]:
        a.append(f'width="{d["w"]}" height="{d["h"]}"')
    a.append('fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"')
    if cls:
        a.append(f'class="{cls}"')
    return "<img " + " ".join(a) + ">"

# ---------------------------------------------------------------- extraction
def kicker_for(h2):
    sp = h2.find_previous_sibling("span")
    return text(sp) if sp else ""

def intro_for(h2):
    p = h2.find_next_sibling("p")
    return inner(p) if p else ""

def paras_in(sec, exclude=()):
    out = []
    for p in sec.find_all("p"):
        if any(p.find_parent(x) for x in ("article", "details", "figure")):
            continue
        if p in exclude:
            continue
        out.append(p)
    return out

def extract_section(sec, is_last):
    h1, h2 = sec.find("h1"), sec.find("h2")
    imgs = sec.find_all("img")
    if h1:
        tc = h1.parent
        kick = h1.find_previous_sibling()
        ps = [p for p in tc.find_all("p") if not p.find_parent("figure")]
        lead = max(ps, key=lambda p: len(text(p))) if ps else None
        chips_el = tc.find(attrs={"aria-label": True}, recursive=True)
        chips = [text(s) for s in chips_el.find_all("span")] if chips_el and chips_el.name == "div" else []
        return {"type": "hero", "kicker": text(kick) if kick and kick.name == "div" else "",
                "h1": fix_brand(text(h1)), "lead": inner(lead) if lead else "", "chips": chips,
                "img": img_data(imgs[0]) if imgs else None}
    if not h2:
        a = sec.find("a")
        return {"type": "band", "text": inner(sec.find("p")), "href": norm_href(a["href"]) if a else "",
                "cta": text(a) if a else ""}
    base = {"kicker": kicker_for(h2), "h2": fix_brand(text(h2)), "intro": intro_for(h2)}
    if sec.find("details"):
        items = []
        for d in sec.find_all("details"):
            items.append({"q": text(d.summary), "a": inner(d.find("p"))})
        return {**base, "type": "faq", "items": items}
    steps = [s for s in sec.find_all("span") if re.fullmatch(r"\s*0\d\s*", s.get_text())]
    if steps:
        items = []
        for s in steps:
            box = s.parent
            items.append({"n": text(s), "h": text(box.find("h3")), "p": inner(box.find("p"))})
        return {**base, "type": "steps", "items": items}
    if sec.find("article"):
        items = []
        for ar in sec.find_all("article"):
            a = ar.find("a")
            items.append({"h": text(ar.find("h3")), "p": inner(ar.find("p")),
                          "href": norm_href(a["href"]) if a else ""})
        return {**base, "type": "cards", "items": items}
    if sec.find("h3"):
        items = [{"h": text(h3), "p": inner(h3.find_next_sibling("p")), "href": ""} for h3 in sec.find_all("h3")]
        return {**base, "type": "areas", "items": items}
    if len(imgs) >= 2:
        return {**base, "type": "gallery", "imgs": [img_data(i) for i in imgs]}
    intro_p = h2.find_next_sibling("p")
    ps = [inner(p) for p in paras_in(sec, exclude=[intro_p] if intro_p else []) if text(p)]
    if is_last:
        return {**base, "type": "final", "paras": ps}
    if imgs:
        return {**base, "type": "media", "paras": ps, "img": img_data(imgs[0])}
    return {**base, "type": "prose", "paras": ps}

def extract_page(slug):
    path = os.path.join(SRC, slug, "index.html") if slug else os.path.join(SRC, "index.html")
    s = BeautifulSoup(open(path, encoding="utf-8").read(), "lxml")
    page = {"slug": slug, "title": fix_brand(s.title.string.strip()),
            "desc": fix_brand(s.find("meta", attrs={"name": "description"})["content"].strip())}
    secs = s.main.find_all("section", recursive=False)
    page["sections"] = [extract_section(x, i == len(secs) - 1) for i, x in enumerate(secs)]
    page["main_soup"] = s.main
    return page

# ---------------------------------------------------------------- extra images
EXTRA = "/assets/1094/extra/"
def extra_img(name, w, h, alt):
    return {"src": f"{EXTRA}{name}.webp", "alt": alt, "w": str(w), "h": str(h),
            "srcset": ", ".join([f"{EXTRA}{name}-w{x}.webp {x}w" for x in (400, 800, 1200)] + [f"{EXTRA}{name}.webp {w}w"])}

EXTRA_IMAGES = {
    "minneapolis-ppc-management": {
        "Paid Search Managed Around Business Results": extra_img("minneapolis-ppc-ad-campaigns", 1600, 1066,
            "Person tapping a smartphone surrounded by floating icons for video, display, audience and search ads"),
        "How Our PPC Management Process Works": extra_img("minneapolis-ppc-optimization-dashboard", 1600, 1065,
            "Hands on a laptop keyboard with campaign performance charts and percentage gauges overlaid on the screen"),
        "Better Decisions Start With Reliable Conversion Data": extra_img("minneapolis-ppc-reporting", 1600, 1066,
            "Printed campaign reports with bar, line and pie charts under a magnifying glass, next to a pen and data table"),
        "How Budget Is Controlled": extra_img("minneapolis-ppc-budget-setup", 1600, 900,
            "Marketer checking a cost report on a laptop against a printed spreadsheet while reviewing a campaign budget"),
    },
}
FINAL_BG = {"": "/assets/1094/extra/minneapolis-skyline.webp"}

def apply_extra_images(page):
    cfg = EXTRA_IMAGES.get(page["slug"], {})
    for sec in page["sections"]:
        img = cfg.get(sec.get("h2"))
        if not img:
            continue
        if sec["type"] == "prose":
            sec["type"] = "media"
        sec["img"] = img
    for sec in page["sections"]:
        if sec["type"] == "final" and page["slug"] in FINAL_BG:
            sec["bg"] = FINAL_BG[page["slug"]]

# ---------------------------------------------------------------- interlinking
def _slots(page):
    """Yield (container, key) slots whose HTML may receive one contextual link."""
    for sec in page["sections"]:
        if sec["type"] in ("prose", "media"):
            for i in range(len(sec["paras"])):
                yield (sec["paras"], i)
        elif sec["type"] in ("faq",):
            for it in sec["items"]:
                yield (it, "a")
        elif sec["type"] in ("cards", "areas"):
            for it in sec["items"]:
                if not it["href"]:
                    yield (it, "p")

def _candidates(page, used, slot_html):
    frag = BeautifulSoup(f"<div>{slot_html}</div>", "html.parser").div
    out = []
    for prio, (phrase, target) in enumerate(LINK_PHRASES):
        href = url(target)
        if target == page["slug"] or href in used:
            continue
        for node in frag.find_all(string=True):
            if node.find_parent("a"):
                continue
            m = re.search(r"(?<![\w-])(?:" + phrase + r")(?![\w-])", str(node), re.I)
            if m:
                if re.match(r"\s*(?:&|&amp;)\s*SEO Solutions", str(node)[m.end():]):
                    continue  # never link the brand name
                out.append((prio, target, m.group(0)))
                break
    return out

def _apply(slot_html, phrase_text, href):
    frag = BeautifulSoup(f"<div>{slot_html}</div>", "html.parser").div
    for node in frag.find_all(string=True):
        if node.find_parent("a"):
            continue
        s = str(node); i = s.find(phrase_text)
        if i >= 0:
            node.replace_with(BeautifulSoup(esc(s[:i]) + f'<a href="{href}">{esc(phrase_text)}</a>' + esc(s[i + len(phrase_text):]), "html.parser"))
            return "".join(str(c) for c in frag.contents)
    return slot_html

def interlink(pages, inbound):
    """Round-robin: each round, every page adds one link to the least-linked target it can reach.
    One inserted link per paragraph, one link per target per page, self-links skipped."""
    state = {}
    for p in pages:
        used = set()
        for c, k in _slots(p):
            used.update(re.findall(r'href="([^"]+)"', c[k]))
        state[p["slug"]] = {"used": used, "n": 0, "done": set()}
    progress = True
    while progress:
        progress = False
        for p in pages:
            st = state[p["slug"]]
            if st["n"] >= MAX_CONTEXT_LINKS:
                continue
            best = None
            for idx, (c, k) in enumerate(_slots(p)):
                if idx in st["done"] or "<a " in c[k]:
                    continue
                for prio, target, txt in _candidates(p, st["used"], c[k]):
                    if len(inbound.get(target, ())) >= MAX_INBOUND:
                        continue
                    key = (len(inbound.get(target, ())), prio, idx)
                    if best is None or key < best[0]:
                        best = (key, c, k, idx, target, txt)
            if not best:
                continue
            _, c, k, idx, target, txt = best
            c[k] = _apply(c[k], txt, url(target))
            st["used"].add(url(target)); st["done"].add(idx); st["n"] += 1
            inbound.setdefault(target, set()).add(p["slug"])
            progress = True

RELATED = {}
def plan_related(inbound):
    """4 related links per service page: 2 from the same cluster, 2 from others,
    always preferring pages with the fewest inbound links so far."""
    load = {t: len(inbound.get(t, ())) for t in SERVICES}
    for slug in SERVICES:
        pool_same = sorted([t for t in SERVICES if CLUSTER[t] == CLUSTER[slug] and t != slug],
                           key=lambda t: (load[t], SERVICES.index(t)))
        pool_other = sorted([t for t in SERVICES if CLUSTER[t] != CLUSTER[slug] and t not in inbound_from(inbound, slug)],
                            key=lambda t: (load[t], SERVICES.index(t)))
        if slug in LG.LEADGEN_SLUGS and slug != LG.HUB:
            pool_same = [LG.HUB] + [t for t in pool_same if t != LG.HUB]
        pick = pool_same[:2]
        pick += [t for t in pool_other if t not in pick][:4 - len(pick)]
        for t in pick:
            load[t] += 1
        RELATED[slug] = pick
    return load

def inbound_from(inbound, slug):
    """targets this page already links to contextually"""
    return {t for t, srcs in inbound.items() if slug in srcs}

def related_for(slug):
    return RELATED.get(slug, [])

# ---------------------------------------------------------------- rendering
ICON_PHONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" fill="currentColor"/></svg>'
CARET = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'

def header(slug):
    groups = []
    for g, items in NAV:
        active = slug in [s for s, _ in items] and slug != "" or (g == "SEO" and slug == "")
        links = "".join(f'<li><a href="{url(s)}"{" aria-current=\"page\"" if s == slug else ""}>{esc(l)}</a></li>' for s, l in items)
        groups.append(f'<li class="nav-group"><details{" data-active" if active else ""}><summary>{esc(g)}{CARET}</summary><ul class="nav-menu">{links}</ul></details></li>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="utility"><div class="wrap">
  <p>Based in Minneapolis, serving clients nationwide</p>
  <p>Mon–Fri 8am–6pm, closed weekends</p>
</div></div>
<header class="site-header"><div class="wrap">
  <a class="logo" href="/" aria-label="{BRAND} home"><img src="/assets/1094/logo-display.webp" width="560" height="84" alt="{BRAND}"></a>
  <nav class="nav" id="primary-nav-panel" aria-label="Primary">
    <ul class="nav-list">{"".join(groups)}<li><a class="nav-link" href="/about/"{" aria-current=\"page\"" if slug == "about" else ""}>About</a></li><li><a class="nav-link" href="/contact/"{" aria-current=\"page\"" if slug == "contact" else ""}>Contact</a></li></ul>
  </nav>
  <a class="btn btn-call" href="tel:{PHONE_TEL}">{ICON_PHONE}<span>{PHONE_DISPLAY}</span></a>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav-panel"><span></span><span class="sr">Menu</span></button>
</div></header>'''

def footer():
    cols = []
    for g, items in NAV:
        cols.append(f'<div class="fcol"><p class="fhead">{esc(g)}</p><ul>' +
                    "".join(f'<li><a href="{url(s)}">{esc(l)}</a></li>' for s, l in items) + "</ul></div>")
    year = datetime.date.today().year
    return f'''<footer class="site-footer">
  <div class="wrap footer-top">
    <div class="fbrand">
      <p class="fbig">Get found by the Minneapolis customers already searching for you.</p>
      <a class="btn btn-primary" href="tel:{PHONE_TEL}">{ICON_PHONE}<span>Call {PHONE_DISPLAY}</span></a>
      <address>{BRAND}<br>{STREET}<br>{CITY}, {REGION} {ZIP}<br><a href="mailto:{EMAIL}">{EMAIL}</a></address>
    </div>
    <nav class="fnav" aria-label="Services">{"".join(cols)}</nav>
  </div>
  <div class="wrap footer-base">
    <p>© {year} {BRAND}</p>
    <p><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy-policy/">Privacy Policy</a><a href="/terms-of-use/">Terms of Use</a></p>
  </div>
</footer>'''

def serp_card(page):
    path = " › ".join(["seo4web.pro"] + ([page["slug"]] if page["slug"] else []))
    return f'''<div class="serp" aria-hidden="true">
  <p class="serp-label">Search preview</p>
  <div class="serp-site"><span class="serp-fav"><img src="/assets/1094/favicon-32.png" width="16" height="16" alt=""></span><span><b>{BRAND}</b><br><small>{esc(path)}</small></span></div>
  <p class="serp-title">{esc(page["title"])}</p>
  <p class="serp-desc">{esc(page["desc"])}</p>
</div>'''

def crumbs(page):
    if not page["slug"]:
        return ""
    name = page.get("crumb") or SHORT.get(page["slug"], "")
    mid = f'<li><a href="{url(page["parent"])}">{esc(LONG_NAME[page["parent"]])}</a></li>' if page.get("parent") else ""
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li>{mid}<li aria-current="page">{esc(name)}</li></ol></nav>'

def r_hero(sec, page):
    chips = "".join(f"<li>{esc(c)}</li>" for c in sec["chips"])
    img = render_img(sec["img"], "(max-width: 900px) 100vw, 46vw", eager=True) if sec["img"] else ""
    if sec.get("alerts"):
        cards = "".join(f'''<li class="alert"><p class="alert-src">{esc(a["src"])}</p><p class="alert-job">{esc(a["job"])}</p><p class="alert-meta"><span>{esc(a["where"])}</span><span class="alert-note">{esc(a["note"])}</span></p></li>''' for a in sec["alerts"])
        img = f'<div class="alerts"><p class="alerts-label">Example lead alerts</p><ul>{cards}</ul></div>'
    return f'''<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      {crumbs(page)}
      <p class="hero-kicker">{esc(sec["kicker"])}</p>
      <h1>{esc(sec["h1"])}</h1>
      <p class="lead">{sec["lead"]}</p>
      <div class="actions">
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">{ICON_PHONE}<span>Call {PHONE_DISPLAY}</span></a>
        <a class="btn btn-ghost" href="/contact/">Request a callback</a>
      </div>
      {f'<ul class="chips" aria-label="Focus areas">{chips}</ul>' if chips else ""}
    </div>
    <figure class="hero-media{' hero-alerts' if sec.get('alerts') else ''}">{img}{serp_card(page)}</figure>
  </div>
</section>'''

def head_block(sec, cls=""):
    k = f'<p class="dek">{esc(sec["kicker"])}</p>' if sec.get("kicker") else ""
    i = f'<p class="intro">{sec["intro"]}</p>' if sec.get("intro") else ""
    return f'<div class="sec-head {cls}"><h2>{esc(sec["h2"])}</h2>{k}{i}</div>'

def r_prose(sec, page, alt):
    ps = "".join(f"<p>{p}</p>" for p in sec["paras"])
    return f'<section class="sec prose-sec{alt}"><div class="wrap split">{head_block(sec)}<div class="prose">{ps}</div></div></section>'

def r_media(sec, page, alt, flip):
    ps = "".join(f"<p>{p}</p>" for p in sec["paras"])
    return f'''<section class="sec media-sec{alt}"><div class="wrap media{' flip' if flip else ''}">
  <figure class="media-fig">{render_img(sec["img"], "(max-width: 900px) 100vw, 42vw")}</figure>
  <div>{head_block(sec)}<div class="prose">{ps}</div></div>
</div></section>'''

def r_cards(sec, page, alt):
    items = []
    for it in sec["items"]:
        h = f'<a href="{it["href"]}">{esc(it["h"])}</a>' if it["href"] else esc(it["h"])
        items.append(f'<li class="card{" card-link" if it["href"] else ""}"><h3>{h}</h3><p>{it["p"]}</p></li>')
    many = " cards-many" if len(items) > 8 else ""
    return f'<section class="sec{alt}"><div class="wrap">{head_block(sec, "wide")}<ul class="cards{many}">{"".join(items)}</ul></div></section>'

ICON_RULES = [  # first match wins
    (("review requested", "job done", "finished work"), "star"),
    (("repeat", "remember", "renew", "next season", "ongoing care"), "repeat"),
    (("measur", "report", "baseline", "track"), "chart"),
    (("booked", "estimate", "schedul"), "calendar"),
    (("reply", "response", "answer", "texted"), "message"),
    (("rout", "checked against", "dispatch", "local presence", "local authority", "markets and"), "pin"),
    (("calls", "phone"), "phone"),
    (("request", "submit", "brief", "comes in"), "form"),
    (("team", "friends", "owners", "audience", "training"), "users"),
    (("launch", "publishing", "delivery", "handoff"), "rocket"),
    (("quality", "testing", "validation"), "shield"),
    (("wirefram", "sitemap", "structure", "architecture", "interface", "scope", "content plan"), "layout"),
    (("rank", "grow"), "trend"),
    (("optimi", "refin", "improv"), "bolt"),
    (("design", "creative", "concept", "production", "content development"), "pen"),
    (("develop",), "code"),
    (("priorit", "goal", "define", "strategy", "set priorities"), "target"),
    (("discover", "audit", "research", "review", "map "), "search"),
    (("implement", "fix", "build", "connect"), "tool"),
]
def step_icon(h):
    h = h.lower()
    for words, key in ICON_RULES:
        if any(w in h for w in words):
            return key
    return "check"

def r_steps(sec, page, alt):
    fig = f'<figure class="steps-fig">{render_img(sec["img"], "(max-width: 1020px) 100vw, 36vw")}</figure>' if sec.get("img") else ""
    if not fig:
        keys = ",".join(step_icon(it["h"]) for it in sec["items"])
        fig = f'<div class="proc3d"><canvas data-icons="{keys}" role="img" aria-label="Animated 3D diagram of the {len(sec["items"])} steps: ' + esc("; ".join(it["h"] for it in sec["items"])) + '"></canvas><p class="proc3d-hint" aria-hidden="true"><span class="h-hover">Hover a step to jump to it</span><span class="h-tap">Tap a step to jump to it</span></p></div>'
    items = "".join(f'<li><span class="step-n" aria-hidden="true">{it["n"]}</span><div><h3>{esc(it["h"])}</h3><p>{it["p"]}</p></div></li>' for it in sec["items"])
    return f'<section class="sec steps-sec"><div class="wrap split"><div class="steps-side">{head_block(sec)}{fig}</div><ol class="steps{' timeline' if sec.get('timeline') else ''}">{items}</ol></div></section>'

def r_faq(sec, page, alt):
    items = "".join(f'<details><summary><h3>{esc(it["q"])}</h3><span class="pm" aria-hidden="true"></span></summary><div class="ans"><p>{it["a"]}</p></div></details>' for it in sec["items"])
    return f'<section class="sec faq-sec{alt}" id="faq"><div class="wrap split">{head_block(sec)}<div class="faq">{items}</div></div></section>'

def r_band(sec, page, alt):
    return f'''<section class="band"><div class="wrap band-in">
  <p>{sec["text"]}</p>
  <a class="btn btn-primary" href="tel:{PHONE_TEL}">{ICON_PHONE}<span>Call for a free quote</span></a>
</div></section>'''

def r_gallery(sec, page, alt):
    figs = "".join(f'<figure>{render_img(d, "(max-width: 900px) 100vw, 33vw")}<figcaption>{esc(d["alt"])}</figcaption></figure>' for d in sec["imgs"])
    return f'<section class="sec{alt}"><div class="wrap">{head_block(sec, "wide")}<div class="gallery">{figs}</div></div></section>'

def r_related(page):
    if page["slug"] in ("contact",):
        return ""
    rel = related_for(page["slug"]) if page["slug"] else []
    if not rel:
        return ""
    desc = SERVICE_BLURB
    items = "".join(f'<li><a href="{url(s)}"><span class="rel-cluster">{esc(CLUSTER[s])}</span><span class="rel-name">{esc(LONG_NAME[s])}</span><span class="rel-desc">{esc(desc.get(s, ""))}</span></a></li>' for s in rel)
    return f'''<section class="sec related"><div class="wrap">
  <div class="sec-head wide"><h2>Related services in Minneapolis</h2><p class="dek">Most projects touch more than one of these. Here is where this work usually connects.</p></div>
  <ul class="rel">{items}</ul>
</div></section>'''

def r_final(sec, page, alt):
    ps = "".join(f"<p>{p}</p>" for p in sec["paras"])
    bg = f'<img class="final-bg" src="{sec["bg"]}" alt="" width="395" height="128" loading="lazy" decoding="async">' if sec.get("bg") else ""
    return f'''<section class="final{' has-bg' if bg else ''}">{bg}<div class="wrap final-in">
  <h2>{esc(sec["h2"])}</h2>
  <div>{ps}<div class="actions">
    <a class="btn btn-primary" href="tel:{PHONE_TEL}">{ICON_PHONE}<span>Call {PHONE_DISPLAY}</span></a>
    <a class="btn btn-ghost-light" href="/contact/">Request a callback</a>
  </div></div>
</div></section>'''

def render_sections(page):
    out, alt_toggle, media_n = [], False, 0
    for sec in page["sections"]:
        t = sec["type"]
        alt = " alt" if alt_toggle else ""
        if t == "hero": out.append(r_hero(sec, page)); continue
        if t == "band": out.append(r_band(sec, page, alt)); alt_toggle = False; continue
        if t == "final":
            out.append(r_related(page)); out.append(r_final(sec, page, alt)); continue
        if t == "prose": out.append(r_prose(sec, page, alt))
        elif t == "media": out.append(r_media(sec, page, alt, media_n % 2 == 1)); media_n += 1
        elif t in ("cards", "areas"): out.append(r_cards(sec, page, alt))
        elif t == "steps": out.append(r_steps(sec, page, alt)); alt_toggle = True; continue
        elif t == "faq": out.append(r_faq(sec, page, alt))
        elif t == "gallery": out.append(r_gallery(sec, page, alt))
        alt_toggle = not alt_toggle
    return "\n".join(out)

# ---------------------------------------------------------------- schema
def business_ld(slug=""):
    return {
        "@type": ["ProfessionalService", "LocalBusiness"], "@id": ORIGIN + "/#business",
        "name": BRAND, "url": ORIGIN + "/", "email": EMAIL, "telephone": PHONE_LD,
        "logo": {"@type": "ImageObject", "url": ORIGIN + "/assets/1094/logo.png", "width": 2100, "height": 316},
        "image": ORIGIN + "/assets/1094/brand/search-engine-optimization-minneapolis-workspace.webp",
        "description": "Website design, search engine optimization and digital marketing for Minneapolis businesses.",
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": CITY,
                    "addressRegion": REGION, "postalCode": ZIP, "addressCountry": "US"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "18:00"}],
        "areaServed": [{"@type": "City", "name": "Minneapolis", "sameAs": "https://en.wikipedia.org/wiki/Minneapolis"},
                       {"@type": "AdministrativeArea", "name": "Minneapolis–Saint Paul metropolitan area"},
                       {"@type": "Country", "name": "United States"}],
        "knowsAbout": [ENT.thing(k) for k in ENT.topics_for(slug)],
        "contactPoint": {"@type": "ContactPoint", "telephone": PHONE_LD, "email": EMAIL, "contactType": "sales",
                         "areaServed": "US", "availableLanguage": "English"},
    }

def page_ld(page, kind="WebPage"):
    u = absu(page["slug"])
    graph = [business_ld(page["slug"]),
             {"@type": "WebSite", "@id": ORIGIN + "/#website", "url": ORIGIN + "/", "name": BRAND,
              "inLanguage": "en-US", "publisher": {"@id": ORIGIN + "/#business"}}]
    wp = {"@type": kind, "@id": u + "#webpage", "url": u, "name": page["title"], "description": page["desc"],
          "inLanguage": "en-US", "isPartOf": {"@id": ORIGIN + "/#website"}, "dateModified": TODAY,
          "about": ENT.thing(ENT.topics_for(page["slug"])[0]),
          "mentions": [ENT.thing(k) for k in ENT.topics_for(page["slug"])[1:]],
          "publisher": {"@id": ORIGIN + "/#business"}}
    hero = next((s for s in page.get("sections", []) if s["type"] == "hero" and s.get("img")), None)
    if hero:
        wp["primaryImageOfPage"] = {"@type": "ImageObject", "url": ORIGIN + hero["img"]["src"],
                                    "width": int(hero["img"]["w"]), "height": int(hero["img"]["h"]), "caption": hero["img"]["alt"]}
    if page["slug"]:
        wp["breadcrumb"] = {"@id": u + "#breadcrumb"}
        crumbs_ld = [{"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"}]
        if page.get("parent"):
            crumbs_ld.append({"@type": "ListItem", "position": 2, "name": LONG_NAME[page["parent"]], "item": absu(page["parent"])})
        crumbs_ld.append({"@type": "ListItem", "position": len(crumbs_ld) + 1, "name": page.get("crumb") or SHORT.get(page["slug"], page["title"]), "item": u})
        graph.append({"@type": "BreadcrumbList", "@id": u + "#breadcrumb", "itemListElement": crumbs_ld})
    graph.append(wp)
    if page["slug"] in SERVICES or page["slug"] == "":
        h1 = next(s["h1"] for s in page["sections"] if s["type"] == "hero")
        svc = {"@type": "Service", "@id": u + "#service", "name": h1, "serviceType": LONG_NAME.get(page["slug"], h1),
               "description": page["desc"], "url": u, "provider": {"@id": ORIGIN + "/#business"},
               "areaServed": {"@type": "City", "name": "Minneapolis"}}
        if page["slug"] in LG.LEADGEN_SLUGS:
            svc["serviceType"] = "Lead generation"
            svc["areaServed"] = {"@type": "Country", "name": "United States"}
            svc["audience"] = {"@type": "BusinessAudience", "audienceType": LONG_NAME[page["slug"]].replace(" Lead Generation", "") + " businesses"}
        if page["slug"] == "":
            svc["hasOfferCatalog"] = {"@type": "OfferCatalog", "name": "Website design, SEO and marketing services",
                                      "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": LONG_NAME[s], "url": absu(s)}} for s in SERVICES if s]}
        graph.append(svc)
        wp["mainEntity"] = {"@id": u + "#service"}
    faq = next((s for s in page.get("sections", []) if s["type"] == "faq"), None)
    if faq:
        graph.append({"@type": "FAQPage", "@id": u + "#faq", "isPartOf": {"@id": u + "#webpage"}, "mainEntity": [
            {"@type": "Question", "name": it["q"], "acceptedAnswer": {"@type": "Answer",
             "text": BeautifulSoup(it["a"], "html.parser").get_text()}} for it in faq["items"]]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- document
def document(page, body, ld, og_img=None, robots="index, follow, max-image-preview:large, max-snippet:-1"):
    u = absu(page["slug"])
    og_img = og_img or {"src": "/assets/1094/brand/search-engine-optimization-minneapolis-workspace.webp", "w": "1000", "h": "750",
                        "alt": "Website Design & SEO Solutions team workspace in Minneapolis"}
    preload = ""
    hero = next((s for s in page.get("sections", []) if s["type"] == "hero" and s.get("img")), None)
    if hero and hero["img"]["srcset"]:
        preload = f'<link rel="preload" as="image" href="{hero["img"]["src"]}" imagesrcset="{hero["img"]["srcset"]}" imagesizes="(max-width: 900px) 100vw, 46vw" fetchpriority="high">'
    return f'''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page["title"])}</title>
<meta name="description" content="{esc(page["desc"])}">
<meta name="robots" content="{robots}">
<meta name="google-site-verification" content="V68KdejA4_YvFmyL5CZc01YLUrvWZTie88NH_oMRZtE">
<link rel="canonical" href="{u}">
<meta name="theme-color" content="#002B53">
<meta name="format-detection" content="telephone=no">
<meta name="geo.region" content="US-MN"><meta name="geo.placename" content="Minneapolis">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(page["title"])}">
<meta property="og:description" content="{esc(page["desc"])}">
<meta property="og:url" content="{u}">
<meta property="og:image" content="{ORIGIN}{og_img["src"]}">
<meta property="og:image:width" content="{og_img["w"]}"><meta property="og:image:height" content="{og_img["h"]}">
<meta property="og:image:alt" content="{esc(og_img["alt"])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page["title"])}">
<meta name="twitter:description" content="{esc(page["desc"])}">
<meta name="twitter:image" content="{ORIGIN}{og_img["src"]}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/1094/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/1094/favicon-180.png">
<link rel="alternate" type="text/markdown" href="/llms.txt" title="LLM-friendly site guide">
<link rel="preload" href="/fonts/bricolage-grotesque-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/source-serif-4-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="/site.css?v={CSS_V}">
<script>(function(d){{try{{if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&'IntersectionObserver' in window){{d.classList.add('js-anim');setTimeout(function(){{if(!window.__revealReady)d.classList.remove('js-anim')}},2500)}}}}catch(e){{}}}})(document.documentElement)</script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
{header(page["slug"])}
<main id="main">
{body}
</main>
{footer()}
<script src="/site.js?v={JS_V}" defer></script>{PROC_TAG if 'class="proc3d"' in body else ''}
</body>
</html>
'''

# ---------------------------------------------------------------- simple pages
def contact_page():
    page = {"slug": "contact", "crumb": "Contact", "title": "Contact Website Design & SEO Solutions | Minneapolis",
            "desc": f"Request a free callback or call {PHONE_DISPLAY} to talk about website design, SEO or lead generation for your business. Minneapolis office, clients nationwide.",
            "sections": []}
    svc = "".join(f'<li><a href="{url(s)}">{esc(LONG_NAME[s])}</a></li>' for s in SERVICES)
    body = f'''<section class="ct">
  <canvas id="nf-globe" class="ct-planet" data-mode="contact" data-layout="horizon" data-interactive="false" aria-hidden="true"></canvas>
  <div class="wrap ct-grid">
    <div class="ct-copy">
      {crumbs(page)}
      <p class="ty-badge ct-badge"><span class="ct-dot" aria-hidden="true"></span>Free consultation, no obligation</p>
      <h1>Tell us about your business. We'll show you what to fix first.</h1>
      <p class="lead">Send a few details and someone from our Minneapolis team will get back to you with an honest view of your website, your search visibility and where your leads are slipping away.</p>
      <ul class="ct-methods">
        <li><a href="tel:{PHONE_TEL}"><span class="ct-ic">{ICON_PHONE}</span><span><span class="ct-l">Call</span><span class="ct-v">{PHONE_DISPLAY}</span></span></a></li>
        <li><a href="mailto:{EMAIL}"><span class="ct-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6.5A1.5 1.5 0 0 1 4.5 5h15A1.5 1.5 0 0 1 21 6.5v11a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5zm2 .9v.3l7 4.6 7-4.6v-.3zm14 2.6-6.45 4.24a1 1 0 0 1-1.1 0L5 10v7h14z" fill="currentColor"/></svg></span><span><span class="ct-l">Email</span><span class="ct-v">{EMAIL}</span></span></a></li>
        <li><a href="https://www.google.com/maps/search/?api=1&amp;query=530+N+3rd+St+Minneapolis+MN+55401" target="_blank" rel="noopener"><span class="ct-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 1 7 7c0 5.2-7 13-7 13S5 14.2 5 9a7 7 0 0 1 7-7zm0 4.5A2.5 2.5 0 1 0 12 11.5 2.5 2.5 0 0 0 12 6.5z" fill="currentColor"/></svg></span><span><span class="ct-l">Visit</span><span class="ct-v">{STREET}, {CITY}, {REGION} {ZIP}</span></span></a></li>
      </ul>
      <dl class="ct-hours"><div><dt>Monday–Friday</dt><dd>8am–6pm</dd></div><div><dt>Saturday–Sunday</dt><dd>Closed</dd></div></dl>
    </div>
    <div class="ct-card" id="form">
      <h2>Request a free callback</h2>
      <p class="ct-card-sub">It takes about a minute. We reply during business hours.</p>
      <div class="crm-wrap">
        <form id="lead-form" class="lead-form" action="https://crm.webleadsnow.com/api/quote/?form_key=bf71a7aa-af51-400d-98fc-b164d372927d" method="post" novalidate>
          <div class="lf-row">
            <label><span>Name</span><input name="name" type="text" autocomplete="name" required></label>
            <label><span>Phone</span><input name="phone" type="tel" autocomplete="tel" required></label>
          </div>
          <div class="lf-row">
            <label><span>Email</span><input name="email" type="email" autocomplete="email" required></label>
            <label><span>Company <span class="lf-opt">(optional)</span></span><input name="company" type="text" autocomplete="organization"></label>
          </div>
          <div class="lf-row">
            <label><span>Website <span class="lf-opt">(optional)</span></span><input name="website" type="text" inputmode="url" placeholder="yourbusiness.com"></label>
            <label><span>What do you need?</span><select name="service" required><option value="">Choose one</option><option>Website design</option><option>Web development</option><option>SEO</option><option>Local SEO</option><option>PPC management</option><option>Social media marketing</option><option>Lead generation</option><option>Branding / graphic design</option><option>Something else</option></select></label>
          </div>
          <label><span>Anything else? <span class="lf-opt">(optional)</span></span><textarea name="message" rows="4"></textarea></label>
          <div class="lf-hp" aria-hidden="true"><label><span>Leave blank</span><input name="website_url" type="text" tabindex="-1" autocomplete="off"></label></div>
          <button type="submit" class="btn btn-primary">Request my free callback</button>
          <p class="lf-status" role="status" aria-live="polite"></p>
        </form>
        <noscript><p class="form-fallback">Please enable JavaScript to send the form, or call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p></noscript>
      </div>
      <p class="ct-privacy">We only use your details to reply to your request. See our <a href="/privacy-policy/">Privacy Policy</a>.</p>
    </div>
  </div>
</section>
<section class="sec">
  <div class="wrap">
    <div class="sec-head wide"><h2>What Happens After You Send It</h2><p class="dek">Three short steps, no pressure.</p></div>
    <ol class="ty-steps">
      <li><span class="ty-n">1</span><h3>We review your request</h3><p>We look at your website, your services and the area you serve before we reach out, so the first conversation is useful.</p></li>
      <li><span class="ty-n">2</span><h3>A short call</h3><p>We ask what is working, what is not and which jobs or customers you want more of.</p></li>
      <li><span class="ty-n">3</span><h3>A clear plan and price</h3><p>You get an honest recommendation of what to do first, what it costs and how you will see whether it worked.</p></li>
    </ol>
  </div>
</section>
<section class="sec alt"><div class="wrap">
  <div class="sec-head wide"><h2>Services We Can Talk Through</h2><p class="dek">Based in Minneapolis, Minnesota, working with businesses nationwide.</p></div>
  <ul class="svc-list">{svc}</ul>
</div></section>
<link rel="stylesheet" href="/assets/lead-form.css?v={FORM_V}">
<script src="/assets/lead-form.js?v={FORM_V}" defer></script>
<script src="/assets/globe/globe-points.js?v={GLOBE_V}" defer></script>
<script src="/assets/globe/globe.js?v={GLOBE_V}" defer></script>'''
    return page, body

def legal_page(slug):
    s = BeautifulSoup(open(os.path.join(SRC, slug, "index.html"), encoding="utf-8").read(), "lxml")
    m = s.main
    h1 = fix_brand(text(m.find("h1")))
    parts = []
    for el in m.find_all(["h2", "h3", "p", "ul", "ol", "address"]):
        if el.find_parent(["ul", "ol"]) and el.name in ("p",):
            continue
        if el.name in ("ul", "ol"):
            if el.find_parent(["ul", "ol"]): continue
            parts.append(f"<{el.name}>" + "".join(f"<li>{inner(li)}</li>" for li in el.find_all("li", recursive=False)) + f"</{el.name}>")
        elif el.name in ("h2", "h3"):
            parts.append(f"<{el.name}>{esc(fix_brand(text(el)))}</{el.name}>")
        else:
            if el.find_parent("address") : continue
            t = inner(el)
            if t: parts.append(f"<p>{t}</p>")
    names = {"privacy-policy": ("Privacy Policy", "How Website Design & SEO Solutions handles information you share when you visit this website, call or email us."),
             "terms-of-use": ("Terms of Use", "The terms that apply when you use the Website Design & SEO Solutions website in Minneapolis, Minnesota.")}
    crumb, desc = names[slug]
    page = {"slug": slug, "crumb": crumb, "title": f"{crumb} | {BRAND}", "desc": desc, "sections": []}
    body = f'''<section class="hero hero-plain"><div class="wrap">{crumbs(page)}<h1>{esc(h1)}</h1></div></section>
<section class="sec"><div class="wrap"><div class="prose doc">{"".join(parts)}</div></div></section>'''
    return page, body

def notfound_page():
    page = {"slug": "404", "title": f"Page not found | {BRAND}", "desc": "This page does not exist.", "sections": []}
    popular = ["", "minneapolis-web-design-companies", "local-seo-minneapolis", "minneapolis-ppc-management", LG.HUB, "about"]
    names = {**LONG_NAME, "about": "About Us"}
    links = "".join(f'<li><a href="{url(s)}">{esc(names[s])}</a></li>' for s in popular)
    svc = "".join(f'<li><a href="{url(s)}">{esc(LONG_NAME[s])}</a></li>' for s in SERVICES)
    body = f'''<section class="nf">
  <div class="wrap nf-grid">
    <div class="nf-copy">
      <p class="nf-code" aria-hidden="true">404</p>
      <h1>This page drifted off the map</h1>
      <p class="lead">The link may be old or mistyped. Everything else is right where you left it, starting from our office in Minneapolis.</p>
      <div class="actions">
        <a class="btn btn-primary" href="/">Back to the homepage</a>
        <a class="btn btn-ghost-light" href="tel:{PHONE_TEL}">{ICON_PHONE}<span>Call {PHONE_DISPLAY}</span></a>
      </div>
      <p class="nf-pop-label">Popular pages</p>
      <ul class="nf-pop">{links}</ul>
    </div>
    <div class="nf-stage">
      <canvas id="nf-globe" role="img" aria-label="A rotating globe with a flight path from Minneapolis to the place this page wandered off to">A globe showing a flight path from Minneapolis.</canvas>
      <p class="nf-hint" aria-hidden="true">Drag to spin the globe</p>
    </div>
  </div>
</section>
<section class="sec"><div class="wrap">
  <div class="sec-head wide"><h2>All Services</h2><p class="dek">Pick up where you meant to go.</p></div>
  <ul class="svc-list">{svc}</ul>
</div></section>
<script src="/assets/globe/globe-points.js?v={GLOBE_V}" defer></script>
<script src="/assets/globe/globe.js?v={GLOBE_V}" defer></script>'''
    return page, body

def about_page():
    team = {"src": "/assets/1094/brand/search-engine-optimization-minneapolis-team.webp", "w": "900", "h": "675",
            "alt": "Website Design & SEO Solutions team reviewing a client website together in the Minneapolis office",
            "srcset": "/assets/1094/brand/search-engine-optimization-minneapolis-team-w400.webp 400w, /assets/1094/brand/search-engine-optimization-minneapolis-team-w600.webp 600w, /assets/1094/brand/search-engine-optimization-minneapolis-team-w800.webp 800w, /assets/1094/brand/search-engine-optimization-minneapolis-team.webp 900w"}
    work = {"src": "/assets/1094/brand/search-engine-optimization-minneapolis-workspace.webp", "w": "1000", "h": "750",
            "alt": "Website Design & SEO Solutions workspace in the North Loop, Minneapolis",
            "srcset": "/assets/1094/brand/search-engine-optimization-minneapolis-workspace-w400.webp 400w, /assets/1094/brand/search-engine-optimization-minneapolis-workspace-w600.webp 600w, /assets/1094/brand/search-engine-optimization-minneapolis-workspace-w800.webp 800w, /assets/1094/brand/search-engine-optimization-minneapolis-workspace.webp 1000w"}
    sections = [
        {"type": "hero", "kicker": "About Website Design & SEO Solutions",
         "h1": "We learned SEO to grow our own business first",
         "lead": "Twelve years ago we needed more customers for a business we already ran. Learning how websites and search engines work changed that business, and it became the work we now do for other owners.",
         "chips": ["Business owners first", "12 years in SEO", "Minnesota based, clients nationwide"], "img": team},
        {"type": "steps", "timeline": True, "kicker": "From one business to many", "h2": "How We Got Here",
         "intro": "We did not start as an agency. We started as a business that needed the phone to ring.",
         "items": [
            {"n": "12 years ago", "h": "Our own business needed to grow",
             "p": "We ran a business that depended on new customers finding us. Buying leads was expensive and unpredictable, so we started learning how websites and search engines actually work."},
            {"n": "Then", "h": "We found a way to rank",
             "p": "Testing on our own site showed us what moved rankings and what did not: solid technical foundations, a useful page for every service, and consistent local signals. Calls started coming from search instead of ads."},
            {"n": "Next", "h": "Friends and other owners asked for help",
             "p": "Other business owners noticed and asked us to do the same for them. We started with friends and local businesses, and treated every site as if our own revenue depended on it."},
            {"n": "Today", "h": "A team of designers and SaaS developers",
             "p": "We now have web designers and SaaS developers who build websites, run SEO and automate the whole lead acquisition process, from the first search to the follow-up."}]},
        {"type": "media", "kicker": "", "intro": "", "img": work, "h2": "Business Owners Before We Were an Agency",
         "paras": ["That background shapes how we work. We judge a website by the calls, forms and booked jobs it brings in, not by the number of reports it produces. When we recommend something, it is what we would do with our own budget.",
                   "It also means we explain things plainly. You should know what we are changing, why it matters for your business, and how you will see whether it worked.",
                   "Every project starts the way ours did: find out how your customers search, build the pages and <a href=\"/\">search engine optimization</a> that answer them, and make sure no lead gets lost on the way to you."]},
        {"type": "cards", "kicker": "Design, search and automation under one roof", "h2": "What Our Team Does Today", "intro": "",
         "items": [
            {"h": "Website Design", "href": "/minneapolis-web-design-companies/", "p": "Fast, clear websites built around the services you sell and the areas you serve, designed to turn visits into calls and inquiries."},
            {"h": "Search Engine Optimization", "href": "/", "p": "Technical fixes, service pages and content priorities that help the right customers find you when they search."},
            {"h": "Local SEO", "href": "/local-seo-minneapolis/", "p": "Google Business Profile, map visibility and local signals for businesses that depend on nearby customers."},
            {"h": "Web Development and Custom Tools", "href": "/web-developers-minneapolis/", "p": "Our SaaS developers build the integrations and custom features a standard website template cannot handle."},
            {"h": "Lead Acquisition Automation", "href": "/contractor-lead-generation/", "p": "Forms, calls, ads and your CRM connected so every new lead is captured, routed to the right person and followed up automatically."},
            {"h": "PPC Management", "href": "/minneapolis-ppc-management/", "p": "Paid search for when you need leads sooner, measured against the same conversions as your organic traffic."}]},
        {"type": "prose", "kicker": "", "intro": "", "h2": "Based in Minnesota, Working With Clients Nationwide",
         "paras": ["Our office is at 530 N 3rd St in the North Loop of Minneapolis, and we know the Twin Cities market well. Most of our work happens online, so we also design websites and run search campaigns for businesses across the United States.",
                   "Whether you serve one neighborhood or several states, the approach is the same: learn how your customers search, give them pages that answer their questions, and connect every inquiry to a fast follow-up."]},
        {"type": "final", "kicker": "", "intro": "", "h2": "Let's Talk About Growing Your Business",
         "paras": ["Tell us what you sell, where you sell it and what is not working today. We will give you a straight answer about what we would do first.", ], "bg": "/assets/1094/extra/minneapolis-skyline.webp"},
    ]
    return {"slug": "about", "crumb": "About", "kind": "AboutPage",
            "title": "About Us | Website Design & SEO Solutions, Minneapolis",
            "desc": "A Minnesota team that learned SEO growing its own business 12 years ago. Today our web designers and SaaS developers help businesses nationwide grow.",
            "sections": sections}

def thankyou_page():
    page = {"slug": "thank-you", "crumb": "Thank you", "title": f"Thank You | {BRAND}",
            "desc": "Thanks for contacting Website Design & SEO Solutions. Your request has reached our Minneapolis team.", "sections": []}
    explore = [("about", "About Us", "How we went from growing our own business to helping others grow theirs."),
               (LG.HUB, "Contractor Lead Generation", LG.PAGES[0]["blurb"]),
               ("local-seo-minneapolis", "Local SEO", SERVICE_BLURB.get("local-seo-minneapolis", "")),
               ("minneapolis-web-design-companies", "Website Design", SERVICE_BLURB.get("minneapolis-web-design-companies", ""))]
    rel = "".join(f'<li><a href="{url(s_)}"><span class="rel-name">{esc(n)}</span><span class="rel-desc">{esc(d)}</span></a></li>' for s_, n, d in explore)
    body = f'''<section class="nf ty">
  <div class="wrap nf-grid">
    <div class="nf-copy">
      <p class="ty-badge"><span class="ty-check" aria-hidden="true"></span>Request received</p>
      <h1>Thank you. Your request is on its way to our team.</h1>
      <p class="lead">We have your details. Someone from our Minneapolis office will call or email you back during business hours, <strong>Monday to Friday 8am–6pm</strong>. Requests sent on the weekend are answered the next business day.</p>
      <div class="actions">
        <a class="btn btn-primary" href="/">Back to the homepage</a>
        <a class="btn btn-ghost-light" href="tel:{PHONE_TEL}">{ICON_PHONE}<span>Need us sooner? {PHONE_DISPLAY}</span></a>
      </div>
    </div>
    <div class="nf-stage">
      <canvas id="nf-globe" data-mode="thanks" role="img" aria-label="A globe with requests from cities around the world arriving at our Minneapolis office">Requests arriving at our Minneapolis office.</canvas>
      <p class="nf-hint" aria-hidden="true">Drag to spin the globe</p>
    </div>
  </div>
</section>
<section class="sec">
  <div class="wrap">
    <div class="sec-head wide"><h2>What Happens Next</h2><p class="dek">Three short steps, no pressure.</p></div>
    <ol class="ty-steps">
      <li><span class="ty-n">1</span><h3>We review your request</h3><p>We look at your website, your services and the area you serve before we reach out, so the first conversation is useful.</p></li>
      <li><span class="ty-n">2</span><h3>A short call</h3><p>We ask what is working, what is not and which jobs or customers you want more of. Bring any reports or numbers you already have.</p></li>
      <li><span class="ty-n">3</span><h3>A clear plan and price</h3><p>You get an honest recommendation of what to do first, what it costs and how you will see whether it worked.</p></li>
    </ol>
  </div>
</section>
<section class="sec alt">
  <div class="wrap">
    <div class="sec-head wide"><h2>While You Wait</h2><p class="dek">A few pages worth a look before we talk.</p></div>
    <ul class="rel">{rel}</ul>
  </div>
</section>
<script>window.dataLayer=window.dataLayer||[];window.dataLayer.push({{event:"thank_you_page_view"}});</script>
<script src="/assets/globe/globe-points.js?v={GLOBE_V}" defer></script>
<script src="/assets/globe/globe.js?v={GLOBE_V}" defer></script>'''
    return page, body

# ---------------------------------------------------------------- main
LONG_NAME = {"": "Search Engine Optimization (SEO)",
             "minneapolis-web-design-companies": "Website Design",
             "web-developers-minneapolis": "Web Development",
             "wordpress-design-minneapolis": "WordPress Design",
             "design-agency-minneapolis": "Design Agency Services",
             "graphic-design-firm-minneapolis": "Graphic Design",
             "minneapolis-seo-consultant": "SEO Consulting",
             "local-seo-minneapolis": "Local SEO",
             "digital-marketing-minneapolis-mn": "Digital Marketing",
             "marketing-minneapolis": "Marketing Services",
             "online-marketing-minneapolis": "Online Marketing",
             "minneapolis-marketing-firms": "Full-Service Marketing Firm",
             "minneapolis-ppc-management": "PPC Management",
             "social-media-marketing-minneapolis": "Social Media Marketing",
             "advertising-companies-minneapolis": "Advertising",
             "creative-agencies-minneapolis": "Creative Agency Services",
             "branding-agency-minneapolis": "Branding",
             **{p["slug"]: p["long"] for p in LG.PAGES}}
SERVICE_BLURB = {}

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    # static assets
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"))
    shutil.copytree(os.path.join(SRC, "okf"), os.path.join(OUT, "okf"))
    shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra-assets"), os.path.join(OUT, "assets/1094/extra"))
    for f in ("favicon.ico",):
        shutil.copy(os.path.join(SRC, f), OUT)
    os.makedirs(os.path.join(OUT, "fonts"))
    shutil.copy(f"{FONTS}/bricolage-grotesque/files/bricolage-grotesque-latin-wght-normal.woff2", f"{OUT}/fonts/bricolage-grotesque-latin-wght.woff2")
    shutil.copy(f"{FONTS}/source-serif-4/files/source-serif-4-latin-wght-normal.woff2", f"{OUT}/fonts/source-serif-4-latin-wght.woff2")
    shutil.copy(f"{FONTS}/source-serif-4/files/source-serif-4-latin-wght-italic.woff2", f"{OUT}/fonts/source-serif-4-latin-wght-italic.woff2")
    here = os.path.dirname(os.path.abspath(__file__))
    shutil.copy(os.path.join(here, "site.css"), OUT)
    shutil.copy(os.path.join(here, "site.js"), OUT)
    os.makedirs(os.path.join(OUT, "assets/globe"), exist_ok=True)
    shutil.copy(os.path.join(here, "globe.js"), os.path.join(OUT, "assets/globe/globe.js"))
    shutil.copy(os.path.join(here, "process3d.js"), os.path.join(OUT, "assets/process3d.js"))
    shutil.copy(os.path.join(here, "lead-form.js"), os.path.join(OUT, "assets/lead-form.js"))
    shutil.copy(os.path.join(here, "lead-form.css"), os.path.join(OUT, "assets/lead-form.css"))
    shutil.copy(os.path.join(here, "globe-points.js"), os.path.join(OUT, "assets/globe/globe-points.js"))

    pages = [extract_page(s) for s in [""] + SERVICES if s not in LG.LEADGEN_SLUGS]
    for p in pages:
        apply_extra_images(p)
    for lp in LG.PAGES:
        hero = {"type": "hero", "kicker": lp["kicker"], "h1": lp["h1"], "lead": lp["lead"], "chips": lp["chips"],
                "img": None, "alerts": lp["alerts"]}
        secs = [hero] + [dict({"kicker": "", "intro": "", "paras": []}, **x) for x in lp["sections"]]
        pages.append({"slug": lp["slug"], "title": lp["title"], "desc": lp["desc"],
                      "crumb": lp["nav"] if lp["slug"] != LG.HUB else "Contractor Lead Generation",
                      "parent": LG.HUB if lp["slug"] != LG.HUB else None, "sections": secs})
    # homepage "About" section links to the new About page
    for sec in pages[0]["sections"]:
        if sec["type"] == "media" and sec["h2"].startswith("About"):
            sec["paras"].append('<a href="/about/">Read how we started and who is on the team</a>.')
    pages.append(about_page())
    # service blurbs from homepage "Related Services" cards
    for sec in pages[0]["sections"]:
        if sec["type"] == "cards":
            for it in sec["items"]:
                if it["href"]:
                    SERVICE_BLURB[it["href"].strip("/")] = BeautifulSoup(it["p"], "html.parser").get_text()
    for lp in LG.PAGES:
        SERVICE_BLURB[lp["slug"]] = lp["blurb"]
    SERVICE_BLURB[""] = "Technical SEO, content priorities, local signals and reporting that ties search visibility to real inquiries."
    # make homepage service cards use clearer names
    for sec in pages[0]["sections"]:
        if sec["type"] == "cards" and any(it["href"] for it in sec["items"]):
            for it in sec["items"]:
                it["h"] = LONG_NAME.get(it["href"].strip("/"), it["h"])
            sec["h2"] = "Website, Search and Marketing Services"
            sec["items"].append({"h": "Contractor Lead Generation", "href": url(LG.HUB), "p": LG.PAGES[0]["blurb"]})

    inbound = {}
    interlink(pages, inbound)
    load = plan_related(inbound)

    report = []
    for p in pages:
        body = render_sections(p)
        hero = next(s for s in p["sections"] if s["type"] == "hero")
        og_ld = page_ld(p, p.get("kind", "WebPage"))
        og = {"src": hero["img"]["src"], "w": hero["img"]["w"], "h": hero["img"]["h"], "alt": hero["img"]["alt"]} if hero.get("img") else \
             {"src": "/assets/1094/brand/search-engine-optimization-minneapolis-field-presence.webp", "w": "900", "h": "675",
              "alt": "Website Design & SEO Solutions branded service van at a client's home"}
        d = os.path.join(OUT, p["slug"]) if p["slug"] else OUT
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(document(p, body, og_ld, og))
        report.append(p)

    extra = [contact_page(), legal_page("privacy-policy"), legal_page("terms-of-use")]
    for p, body in extra:
        kind = "ContactPage" if p["slug"] == "contact" else "WebPage"
        d = os.path.join(OUT, p["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(document(p, body, page_ld(p, kind)))
    p, body = thankyou_page()
    os.makedirs(os.path.join(OUT, "thank-you"), exist_ok=True)
    open(os.path.join(OUT, "thank-you", "index.html"), "w", encoding="utf-8").write(
        document(p, body, json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": p["title"], "url": absu("thank-you")}), robots="noindex, follow"))
    p, body = notfound_page()
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
        document(p, body, json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": p["title"]}), robots="noindex, follow"))

    # sitemap
    urls = [("", "1.0", "weekly")] + [(s, "0.8", "monthly") for s in SERVICES if s] + \
           [("about", "0.6", "yearly"), ("contact", "0.6", "yearly"), ("privacy-policy", "0.2", "yearly"), ("terms-of-use", "0.2", "yearly")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    heroes = {p["slug"]: next(s for s in p["sections"] if s["type"] == "hero").get("img") for p in pages}
    for s, pr, cf in urls:
        img = heroes.get(s)
        im = f'<image:image><image:loc>{ORIGIN}{img["src"]}</image:loc></image:image>' if img else ""
        sm.append(f"  <url><loc>{absu(s)}</loc><lastmod>{TODAY}</lastmod>{im}</url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n\n# Plain-text guide for AI assistants: {ORIGIN}/llms.txt\n")
    # llms.txt + okf: fix brand capitalisation & add contact page
    llms = fix_brand(open(os.path.join(SRC, "llms.txt"), encoding="utf-8").read())
    llms = llms.rstrip() + "\n\n## About\n\n- [About us](https://seo4web.pro/about/): Started 12 years ago by business owners who learned SEO to grow their own business; today a Minnesota team of web designers and SaaS developers serving clients nationwide.\n"
    llms += "\n## Lead generation for home service contractors\n\n" + "".join(f"- [{p['long']}]({ORIGIN}/{p['slug']}/): {p['blurb']}\n" for p in LG.PAGES)
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write(llms)
    for f in os.listdir(os.path.join(OUT, "okf")):
        fp = os.path.join(OUT, "okf", f)
        open(fp, "w", encoding="utf-8").write(fix_brand(open(fp, encoding="utf-8").read()))
    # Cloudflare Pages config
    open(os.path.join(OUT, "_headers"), "w").write("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains

/assets/*
  Cache-Control: public, max-age=31536000, immutable
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *
/site.css
  Cache-Control: public, max-age=31536000, immutable
/site.js
  Cache-Control: public, max-age=31536000, immutable
/*.html
  Cache-Control: public, max-age=0, must-revalidate
/
  Cache-Control: public, max-age=0, must-revalidate
""")
    open(os.path.join(OUT, "_redirects"), "w").write(
        "/home / 301\n/services / 301\n")
    # report
    print("Inbound links per service page (contextual + related block):")
    for s in SERVICES:
        print(f"  {url(s):42} {len(inbound.get(s, [])):2} + {load[s] - len(inbound.get(s, [])):2} = {load[s]}")

if __name__ == "__main__":
    main()
