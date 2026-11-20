#!/usr/bin/env python3
"""Apply the SEO fixes in seo_overrides.py to a built site (default: ../public).

Usage: python3 -I tools/seo_fix.py public

Idempotent: a second run changes nothing. build.py runs it at the end of a rebuild, so a
fresh build gets the same fixes. Edits are targeted string edits (no HTML re-serialisation),
so unchanged parts of each page stay byte-identical.
"""
import datetime, glob, hashlib, html, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seo_overrides as O

ORIGIN = "https://seo4web.pro"
root = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "public")).rstrip("/")
TODAY = datetime.date.today().isoformat()
LD_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)

def slug_of(path):
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    return "" if rel == "index.html" else rel[:-len("/index.html")] if rel.endswith("/index.html") else None

def replace_text(doc, old, new):
    """Replace a title/description everywhere: escaped in HTML, raw inside JSON-LD."""
    if not old or old == new:
        return doc
    parts, last = [], 0
    for m in LD_RE.finditer(doc):
        parts.append(doc[last:m.start()].replace(html.escape(old, quote=False), html.escape(new, quote=False)))
        parts.append(m.group(1) + m.group(2).replace(json.dumps(old, ensure_ascii=False)[1:-1],
                                                      json.dumps(new, ensure_ascii=False)[1:-1]) + m.group(3))
        last = m.end()
    parts.append(doc[last:].replace(html.escape(old, quote=False), html.escape(new, quote=False)))
    return "".join(parts)

def edit_ld(doc, fn):
    def sub(m):
        raw = m.group(2)
        data = json.loads(raw)
        compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        if compact != raw:          # keep any hand-formatted block untouched
            return m.group(0)
        fn(data)
        return m.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + m.group(3)
    return LD_RE.sub(sub, doc)

def scope_band(slug):
    cluster = next(c for c in O.CLUSTERS.values() if slug in c)
    focus = O.FOCUS[slug]
    items = "".join(f'<li><a href="{"/" + s + "/" if s else "/"}">{html.escape(O.LABEL[s])}</a> <span>{html.escape(O.FOCUS[s])}</span></li>'
                    for s in cluster if s != slug)
    return ('<section class="scope" aria-labelledby="scope-h"><div class="wrap scope-grid">'
            f'<div class="scope-this"><p class="scope-k" id="scope-h">What this page covers</p><p>{html.escape(focus[0].upper() + focus[1:])}.</p></div>'
            f'<div class="scope-more"><p class="scope-k">Looking for something else?</p><ul>{items}</ul></div>'
            '</div></section>\n')

SCOPE_RE = re.compile(r'<section class="scope".*?</section>\n?', re.S)

SCOPE_CSS = """
/* "What this page covers" band (seo_fix.py): tells overlapping service pages apart */
.scope{padding:3rem 0 2.25rem;border-bottom:1px solid var(--rule)}
.scope-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);gap:1.25rem 3rem;align-items:start}
.scope-k{font:650 .78rem/1.2 var(--display);letter-spacing:.08em;text-transform:uppercase;color:var(--orange-ink);margin:0 0 .5rem}
.scope-this p:last-child{font:550 1.2rem/1.45 var(--display);color:var(--navy);margin:0}
.scope-more ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.55rem 1.75rem;font-size:.95rem;line-height:1.4}
.scope-more a{font:600 .98rem/1.3 var(--display)}
.scope-more span{display:block;color:var(--steel)}
@media (max-width:900px){.scope-grid{grid-template-columns:1fr}}
"""

def ensure_css():
    css_src = os.path.join(HERE, "site.css")
    css = open(css_src, encoding="utf-8").read()
    if "/* \"What this page covers\" band" not in css:
        open(css_src, "w", encoding="utf-8").write(css.rstrip("\n") + "\n" + SCOPE_CSS)
    shutil.copy(css_src, os.path.join(root, "site.css"))
    return hashlib.sha1(open(css_src, "rb").read()).hexdigest()[:10]

def main():
    css_v = ensure_css()
    renames = []          # (old, new) for llms.txt and okf/*.md
    changed = set()
    for path in sorted(glob.glob(root + "/**/*.html", recursive=True)):
        slug = slug_of(path)
        doc = orig = open(path, encoding="utf-8").read()
        # 1 · titles and descriptions, every copy in sync
        old_t = html.unescape(re.search(r"<title>(.*?)</title>", doc, re.S).group(1))
        m = re.search(r'<meta name="description" content="([^"]*)"', doc)
        old_d = html.unescape(m.group(1)) if m else None
        if slug in O.TITLES and O.TITLES[slug] != old_t:
            doc = replace_text(doc, old_t, O.TITLES[slug]); renames.append((old_t, O.TITLES[slug]))
        if slug in O.DESCS and old_d and O.DESCS[slug] != old_d:
            doc = replace_text(doc, old_d, O.DESCS[slug]); renames.append((old_d, O.DESCS[slug]))
        # 2 · keep e-mail links away from Cloudflare e-mail obfuscation (it rewrites them to
        #     /cdn-cgi/l/email-protection, which crawlers report as a 404)
        doc = re.sub(r'(?<!<!--email_off-->)(<a\b[^>]*href="mailto:[^"]*"[^>]*>.*?</a>)(?!<!--/email_off-->)',
                     r"<!--email_off-->\1<!--/email_off-->", doc, flags=re.S)
        # 3 · decorative images: short alt + aria-hidden
        def fix_img(m):
            tag = m.group(0)
            src = re.search(r'\ssrc="([^"]*)"', tag)
            if not src or src.group(1) not in O.DECORATIVE_ALT or not re.search(r'\salt=""', tag):
                return tag
            tag = tag.replace(' alt=""', f' alt="{html.escape(O.DECORATIVE_ALT[src.group(1)])}"', 1)
            if "aria-hidden" not in tag:
                tag = tag.replace("<img ", '<img aria-hidden="true" ', 1)
            return tag
        doc = re.sub(r"<img\b[^>]*>", fix_img, doc)
        # 4 · structured data: one distinct main entity per page
        def ld(data):
            for n in data.get("@graph", []):
                t = n.get("@type")
                if t == "Service" and n.get("serviceType") == "Lead generation":
                    n["serviceType"] = n["name"]          # e.g. "Lead Generation for Towing Companies"
                if t in ("WebPage", "ContactPage") and slug in O.ABOUT_BUSINESS:
                    n["about"] = {"@id": ORIGIN + "/#business"}
        doc = edit_ld(doc, ld)
        # 5 · "What this page covers" band after the hero on clustered service pages
        if slug in O.SCOPE_PAGES:
            doc = SCOPE_RE.sub("", doc)
            i = doc.find('<section class="hero">')
            j = doc.find("</section>", i) + len("</section>\n")
            doc = doc[:j] + scope_band(slug) + doc[j:]
        # 6 · stylesheet cache-busting
        doc = re.sub(r"/site\.css\?v=[0-9a-f]+", f"/site.css?v={css_v}", doc)
        if doc != orig:
            if slug is not None:
                def bump(data):
                    for n in data.get("@graph", []):
                        if "dateModified" in n:
                            n["dateModified"] = TODAY
                doc = edit_ld(doc, bump)
                changed.add(slug)
            open(path, "w", encoding="utf-8").write(doc)
    # 7 · plain-text copies (llms.txt, okf/*.md)
    for f in [root + "/llms.txt"] + glob.glob(root + "/okf/*.md"):
        t = o = open(f, encoding="utf-8").read()
        for old, new in renames:
            t = t.replace(old, new)
        if t != o:
            open(f, "w", encoding="utf-8").write(t)
    # 8 · sitemap lastmod for pages that changed
    sm_path = root + "/sitemap.xml"
    sm = open(sm_path).read()
    for s in changed:
        loc = re.escape(ORIGIN + ("/" + s + "/" if s else "/"))
        sm = re.sub(rf"(<loc>{loc}</loc><lastmod>)[^<]*(</lastmod>)", rf"\g<1>{TODAY}\g<2>", sm)
    open(sm_path, "w").write(sm)
    print(f"seo_fix: {len(changed)} pages updated, {len(renames)} title/description rewrites, site.css v={css_v}")

if __name__ == "__main__":
    main()
