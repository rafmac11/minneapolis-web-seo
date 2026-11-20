# seo4web.pro — Website Design & SEO Solutions

Static website for Website Design & SEO Solutions, Minneapolis, MN.

## Layout

- `public/`: the live site. Deploy this folder as is.
- `tools/`: the build script that produced `public/` from the original site export, plus the stylesheet, script and checks.

## Deploy on Cloudflare Pages

1. In Cloudflare, go to **Workers & Pages → Create → Pages → Connect to Git** and pick this repository.
2. Set **Framework preset** to *None*, leave **Build command** empty and set **Build output directory** to `public`.
3. After the first deploy, add `seo4web.pro` (and `www.seo4web.pro`) under **Custom domains**.

Cloudflare reads `public/_headers` for security and caching headers and `public/_redirects` for redirects. `public/404.html` is used for missing pages.

## Editing

For small text changes, edit the HTML in `public/` directly.

To regenerate the whole site from the original export:

```bash
cd tools
npm install          # downloads the Bricolage Grotesque and Source Serif 4 fonts
pip install beautifulsoup4 lxml
python3 -I build.py /path/to/original-export ../public
python3 -I audit.py ../public   # checks titles, descriptions, canonicals, schema, links and images
```

## SEO fixes and audit

The original export is not in this repository, so `public/` is the source of truth. SEO changes are data in
`tools/seo_overrides.py` (titles, descriptions, the "What this page covers" bands, decorative image alt text) and are
applied by `tools/seo_fix.py`, which is safe to re-run and which `build.py` also runs after a rebuild:

```bash
python3 -I tools/seo_fix.py public      # apply tools/seo_overrides.py to the site
python3 -I tools/site_audit.py public   # full audit; exits 1 if any error is found
```

`site_audit.py` measures titles (≤580px, Arial 20px) and descriptions (≤920px, Arial 13px) in pixels and checks clean
Cloudflare Pages URLs in canonicals, og:url, JSON-LD, the sitemap, internal links and redirects, plus H1s, lang,
viewport, JSON-LD validity, broken links, missing assets, orphan pages, sitemap coverage, image alt text and sizes,
Cloudflare e-mail obfuscation and the share of each page's text that is unique to it.

`build.py` holds the navigation, the contextual-link phrase map (`LINK_PHRASES`) and the structured-data settings (phone, address, hours).
