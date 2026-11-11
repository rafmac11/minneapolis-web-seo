import glob, json, os, re, sys
from bs4 import BeautifulSoup
root = sys.argv[1]; files = sorted(glob.glob(root + "/**/*.html", recursive=True))
titles, descs, problems, links = {}, {}, [], set()
for f in files:
    rel = "/" + os.path.relpath(f, root).replace("index.html", "")
    s = BeautifulSoup(open(f).read(), "lxml")
    t = s.title.string; d = s.find("meta", attrs={"name": "description"})["content"]
    titles.setdefault(t, []).append(rel); descs.setdefault(d, []).append(rel)
    if len(s.find_all("h1")) != 1: problems.append(f"{rel}: {len(s.find_all('h1'))} h1")
    if not (30 <= len(t) <= 60): problems.append(f"{rel}: title {len(t)} chars")
    if not (70 <= len(d) <= 160): problems.append(f"{rel}: desc {len(d)} chars")
    can = s.find("link", rel="canonical")
    if rel != "/404.html" and can["href"] != "https://seo4web.pro" + rel: problems.append(f"{rel}: canonical {can['href']}")
    for sc in s.find_all("script", type="application/ld+json"): json.loads(sc.string)
    for im in s.find_all("img"):
        if im.get("alt") is None: problems.append(f"{rel}: img no alt {im['src']}")
        if not os.path.exists(root + im["src"].split("?")[0]): problems.append(f"{rel}: missing img {im['src']}")
        for part in (im.get("srcset") or "").split(","):
            if part.strip() and not os.path.exists(root + part.strip().split(" ")[0]): problems.append(f"{rel}: missing srcset {part}")
    for a in s.find_all("a", href=True):
        h = a["href"]
        if h.startswith("/"):
            links.add(h)
            p = root + h.split("#")[0] + ("index.html" if h.endswith("/") else "")
            if not os.path.exists(p): problems.append(f"{rel}: broken link {h}")
for k, v in list(titles.items()) + list(descs.items()):
    if len(v) > 1: problems.append(f"duplicate: {k[:50]} on {v}")
sm = open(root + "/sitemap.xml").read()
for u in re.findall(r"<loc>https://seo4web.pro([^<]*)</loc>", sm):
    if not os.path.exists(root + u + ("index.html" if u.endswith("/") else "")): problems.append(f"sitemap broken {u}")
print(len(files), "html files;", len(problems), "problems"); print("\n".join(problems))
