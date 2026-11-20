#!/usr/bin/env python3
"""AI-agent readiness for the built site (default: ../public).

Usage: python3 -I tools/agent_ready.py public

Generates, from the site's own pages and structured data:
  /site-data.json            business facts + service list read by the WebMCP tools in site.js
  /llms.txt                  llmstxt.org summary
  /.well-known/ard.json      Agentic Resource Discovery manifest (ARD v0.91)
and patches every page with the credit banner comment, <link rel="ard">, the footer
"Website design by" credit link, robots.txt Agentmap, and the site.js /
site.css cache-busting versions. Running it twice changes nothing. build.py runs it last.
"""
import glob, hashlib, html, json, os, re, shutil, sys
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
root = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "public")).rstrip("/")
ORIGIN = "https://seo4web.pro"
DOMAIN = "seo4web.pro"
SHORT = "SEO4WEB"
ARD_URL = f"{ORIGIN}/.well-known/ard.json"
CREDIT = ("webleadsnow.com", "https://webleadsnow.com/")
TOOLS = ["search_services", "get_business_info", "request_quote"]
# Pricing as the site states it (contact page "A clear plan and price", "Free consultation, no obligation")
PRICING = ("Priced by project scope. After a free, no-obligation consultation and a short call you get a "
           "recommendation of what to do first and what it costs.")
# Target phrases + city (ARD representativeQueries)
QUERIES = ["website design company in Minneapolis", "SEO services in Minneapolis",
           "local SEO agency in Minneapolis", "PPC management in Minneapolis",
           "lead generation for home service contractors in Minneapolis"]

def page(slug):
    p = os.path.join(root, slug, "index.html") if slug else os.path.join(root, "index.html")
    return BeautifulSoup(open(p, encoding="utf-8").read(), "lxml")

def url(slug): return f"{ORIGIN}/{slug}/" if slug else f"{ORIGIN}/"

def graph(s):
    return json.loads(s.find("script", type="application/ld+json").string)["@graph"]

# ------------------------------------------------------------------ data from the site
def collect():
    home = page("")
    biz = next(n for n in graph(home) if n.get("@id") == ORIGIN + "/#business")
    a = biz["address"]
    address = f'{a["streetAddress"]}, {a["addressLocality"]}, {a["addressRegion"]} {a["postalCode"]}'
    days = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}
    hours = [f'{days[o["dayOfWeek"][0]]}–{days[o["dayOfWeek"][-1]]} {o["opens"]}–{o["closes"]}' for o in biz["openingHoursSpecification"]]
    phone_display = home.select_one('a[href^="tel:"] span').get_text(strip=True).replace("Call ", "")
    business = {
        "name": biz["name"], "url": url(""), "description": biz["description"],
        "address": address, "telephone": phone_display, "email": biz["email"],
        "hours": hours + ["Sat–Sun closed"],
        "areaServed": [x["name"] for x in biz["areaServed"]],
        "pricingPolicy": PRICING,
        "contactPage": url("contact") + "#form",
    }
    # categories from the footer service columns; display names from the contact page service list
    cat = {}
    for col in home.select("footer .fcol"):
        for a_ in col.select("a"):
            cat[a_["href"].strip("/")] = col.select_one(".fhead").get_text(strip=True)
    names = {a_["href"].strip("/"): a_.get_text(strip=True) for a_ in page("contact").select(".svc-list a")}
    services = []
    for slug, category in cat.items():
        s = page(slug)
        g = graph(s)
        wp = next(n for n in g if n.get("@type") == "WebPage")
        kw = [wp["about"]["name"]] + [m["name"] for m in wp.get("mentions", [])] + [li.get_text(strip=True) for li in s.select(".hero .chips li")]
        services.append({
            "slug": slug, "name": names.get(slug) or ("SEO Services" if not slug else slug),
            "category": category, "url": url(slug), "title": s.title.string.strip(),
            "description": s.find("meta", attrs={"name": "description"})["content"],
            "keywords": "; ".join(dict.fromkeys(kw)),
        })
    return business, services, biz

# ------------------------------------------------------------------ generated files
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path) or open(path, encoding="utf-8").read() != text:
        open(path, "w", encoding="utf-8").write(text)

def llms_txt(b, services):
    def line(title, u, desc): return f"- [{title}]({u}): {desc}\n"
    def meta(slug): return page(slug).find("meta", attrs={"name": "description"})["content"]
    groups = {}
    for s in services:
        groups.setdefault("Lead generation programs" if s["category"] == "Lead Generation" else "Services", []).append(s)
    t = f"# {b['name']}\n\n"
    t += (f"> {b['name']} is a Minneapolis, Minnesota agency for website design, web development, search engine "
          f"optimization (SEO), local SEO, PPC, social media, branding and lead generation for home service contractors. "
          f"Office: {b['address']}. Phone {b['telephone']}, email {b['email']}. Serves Minneapolis, the Twin Cities "
          f"metro and clients nationwide.\n\n")
    t += "## Key facts\n\n"
    t += f"- Address: {b['address']}\n- Phone: {b['telephone']}\n- Email: {b['email']}\n"
    t += f"- Hours: {'; '.join(b['hours'])}\n- Service area: {', '.join(b['areaServed'])}\n"
    t += f"- Pricing: {b['pricingPolicy']}\n"
    t += f"- Request a callback: {b['contactPage']}\n\n"
    t += "## Main pages\n\n"
    t += line("Home: SEO services in Minneapolis", url(""), meta(""))
    t += line("About us", url("about"), meta("about"))
    t += line("Contact and free callback", url("contact"), meta("contact"))
    for h in ("Services", "Lead generation programs"):
        t += f"\n## {h}\n\n" + "".join(line(s["name"], s["url"], s["description"]) for s in groups[h] if s["slug"])
    t += "\n## Optional\n\n"
    t += line("Privacy Policy", url("privacy-policy"), meta("privacy-policy"))
    t += line("Terms of Use", url("terms-of-use"), meta("terms-of-use"))
    t += line("XML sitemap", f"{ORIGIN}/sitemap.xml", "Every indexable page with its last-modified date.")
    if os.path.exists(os.path.join(root, "okf", "index.md")):
        t += line("Open Knowledge Format bundle", f"{ORIGIN}/okf/index.md", "Markdown copies of the service pages (OKF v0.2).")
    return t

def ard_json(b, biz, updated):
    entry = {
        "@context": "https://agenticresourcediscovery.org/context/v1",
        "identifier": f"urn:air:{DOMAIN}:website:{SHORT.lower()}",
        "displayName": b["name"],
        "description": (f"Website of {b['name']}, a Minneapolis, MN agency for website design, SEO, local SEO, PPC, "
                        "social media, branding and contractor lead generation. In-page WebMCP tools let a browser "
                        "agent search the services, read business details and open the callback form."),
        "type": "text/html",
        "url": url(""),
        "capabilities": TOOLS,
        "representativeQueries": QUERIES,
        "tags": ["website-design", "seo", "local-seo", "ppc", "digital-marketing", "lead-generation", "minneapolis", "local-business"],
        "updatedAt": updated,
        "metadata": {
            "schemaOrgType": "ProfessionalService",
            "address": b["address"] + ", US",
            "telephone": biz["telephone"],
            "email": b["email"],
            "areaServed": "; ".join(b["areaServed"]),
            "openingHours": "Mo-Fr 08:00-18:00",
            "pricingPolicy": b["pricingPolicy"],
        },
    }
    return json.dumps({"specVersion": "1.0",
                       "host": {"displayName": b["name"], "documentationUrl": f"{ORIGIN}/llms.txt"},
                       "entries": [entry]}, ensure_ascii=False, indent=2) + "\n"

def banner():
    import pyfiglet
    art = pyfiglet.figlet_format(SHORT, font="ansi_shadow").rstrip("\n").split("\n")
    art = [l.rstrip() for l in art if l.strip()]
    w = max(len(l) for l in art)
    rule = "=" * w
    c = "\n".join([rule] + art + ["by webleadsnow.com".center(w).rstrip(), rule])
    assert "--" not in c
    return f"<!--\n{c}\n-->"

# ------------------------------------------------------------------ page patches
BANNER_RE = re.compile(r"\n?<!--\n=+\n.*?\n=+\n-->", re.S)
def patch_page(doc, ban, js_v, css_v):
    doc = BANNER_RE.sub("", doc, count=1)
    doc = doc.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + ban, 1)
    if 'rel="ard"' not in doc:
        doc = doc.replace("</head>", f'<link rel="ard" href="{ARD_URL}">\n</head>', 1)
    # footer bottom bar: design credit (underlined: link-in-text-block)
    if CREDIT[1] not in doc:
        doc = re.sub(r"(<div class=\"wrap footer-base\">\s*<p>© [^<]*)</p>",
                     rf'\1<span class="credit"> · Website design by <a href="{CREDIT[1]}" target="_blank" rel="noopener">{CREDIT[0]}</a></span></p>', doc, count=1)
    # header call button: its text is hidden on phones, so give the link an accessible name (axe link-name)
    doc = re.sub(r'<a class="btn btn-call" href="tel:([^"]+)">(?=.*?<span>([^<]+)</span>)',
                 lambda m: f'<a class="btn btn-call" href="tel:{m.group(1)}" aria-label="Call {m.group(2)}">', doc, count=1, flags=re.S)
    doc = re.sub(r"/site\.js\?v=[0-9a-f]+", f"/site.js?v={js_v}", doc)
    doc = re.sub(r"/site\.css\?v=[0-9a-f]+", f"/site.css?v={css_v}", doc)
    return doc

CREDIT_CSS = """
/* footer design credit (agent_ready.py): underlined so it stands out from the text around it, not by colour alone */
.footer-base .credit a{margin:0;text-decoration:underline;text-decoration-color:currentColor;text-decoration-thickness:1px;text-underline-offset:.18em}
"""

def asset(name, extra=""):
    src = os.path.join(HERE, name)
    t = open(src, encoding="utf-8").read()
    if extra and extra.strip().split("\n")[0] not in t:
        open(src, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + extra)
    shutil.copy(src, os.path.join(root, name))
    return hashlib.sha1(open(src, "rb").read()).hexdigest()[:10]

def main():
    css_v = asset("site.css", CREDIT_CSS)
    js_v = asset("site.js")
    b, services, biz = collect()
    write(os.path.join(root, "site-data.json"),
          json.dumps({"business": b, "services": services}, ensure_ascii=False, indent=1) + "\n")
    write(os.path.join(root, "llms.txt"), llms_txt(b, services))
    lastmods = re.findall(r"<lastmod>([^<]+)</lastmod>", open(os.path.join(root, "sitemap.xml")).read())
    write(os.path.join(root, ".well-known", "ard.json"), ard_json(b, biz, max(lastmods) + "T00:00:00Z"))
    ban = banner()
    n = 0
    for f in sorted(glob.glob(root + "/**/*.html", recursive=True)):
        d = open(f, encoding="utf-8").read()
        nd = patch_page(d, ban, js_v, css_v)
        if nd != d:
            open(f, "w", encoding="utf-8").write(nd); n += 1
    rb = os.path.join(root, "robots.txt")
    r = open(rb).read()
    if "Agentmap:" not in r:
        r = r.replace(f"Sitemap: {ORIGIN}/sitemap.xml\n", f"Sitemap: {ORIGIN}/sitemap.xml\nAgentmap: {ARD_URL}\n")
        open(rb, "w").write(r)
    print(f"agent_ready: {n} pages patched, {len(services)} services, site.js v={js_v}, site.css v={css_v}")

if __name__ == "__main__":
    main()
