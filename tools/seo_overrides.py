"""SEO data applied to the built site by seo_fix.py.

TITLES / DESCS: replacement <title> and meta description per page slug ("" = homepage).
They replace the old value everywhere it appears (title, og:/twitter: tags, JSON-LD,
search-preview card, llms.txt and okf/*.md), so every copy stays in sync.
Limits: title <= 580px in Arial 20px, description <= 920px in Arial 13px, whole sentences only.

FOCUS: one-line scope of each page in an overlapping cluster. Each clustered page gets a
"What this page covers" band after the hero that states its own focus and links its
siblings with theirs, so visitors and search engines can tell the pages apart.
"""

TITLES = {
    "marketing-minneapolis": "Marketing Minneapolis | Strategy, Planning & Measurement",
    "online-marketing-minneapolis": "Online Marketing Minneapolis | SEO, Content & Paid Media",
    "digital-marketing-minneapolis-mn": "Digital Marketing Minneapolis MN | Services, Process & Cost",
    "minneapolis-marketing-firms": "Minneapolis Marketing Firm | Full-Service Programs",
    "advertising-companies-minneapolis": "Advertising Companies in Minneapolis | Campaigns & Creative",
    "creative-agencies-minneapolis": "Creative Agencies Minneapolis | Brand, Campaign & Content",
    "branding-agency-minneapolis": "Branding Agency Minneapolis | Positioning & Identity",
}

DESCS = {
    "minneapolis-ppc-management": "Minneapolis PPC management that reaches qualified prospects, cuts wasted spend and improves ROI, with budget control and reliable conversion data.",
    "marketing-minneapolis": "Marketing strategy for Minneapolis businesses: what the plan should cover, how it is managed, and how each activity is measured against business results.",
    "online-marketing-minneapolis": "Online marketing for Minneapolis businesses that coordinates search, content and paid media, with reporting that shows what drives inquiries.",
    "digital-marketing-minneapolis-mn": "Digital marketing services for Minneapolis, MN businesses: what is included, how the process works, typical monthly costs and how to choose an agency.",
    "minneapolis-marketing-firms": "A full-service Minneapolis marketing firm that coordinates strategy, search, content and campaigns, plus how to compare firms and proposals.",
    "advertising-companies-minneapolis": "Advertising for Minneapolis businesses that aligns campaign strategy, creative and measurement, plus the questions to ask before you hire an ad agency.",
    "creative-agencies-minneapolis": "Creative agency work for Minneapolis businesses: brand, campaign and content production scoped around clear goals, from brief to launch.",
    "graphic-design-firm-minneapolis": "Our graphic design firm in Minneapolis creates logos, visual identities and marketing graphics, with the process, typical costs and timelines explained.",
    "branding-agency-minneapolis": "Our Minneapolis branding agency builds brand positioning, identity systems and guidelines, and helps you choose between a refresh and a full rebrand.",
}

# cluster -> ordered slugs; FOCUS[slug] completes "This page covers ..."
CLUSTERS = {
    "Marketing": ["marketing-minneapolis", "online-marketing-minneapolis", "digital-marketing-minneapolis-mn",
                  "minneapolis-marketing-firms", "advertising-companies-minneapolis",
                  "social-media-marketing-minneapolis", "minneapolis-ppc-management"],
    "Design": ["minneapolis-web-design-companies", "web-developers-minneapolis", "wordpress-design-minneapolis",
               "design-agency-minneapolis", "graphic-design-firm-minneapolis", "creative-agencies-minneapolis",
               "branding-agency-minneapolis"],
    "SEO": ["", "minneapolis-seo-consultant", "local-seo-minneapolis"],
}
# pages that show the band (the homepage already lists every service in its cards section)
SCOPE_PAGES = [s for c in CLUSTERS.values() for s in c if s]

LABEL = {
    "": "SEO services",
    "marketing-minneapolis": "Marketing strategy",
    "online-marketing-minneapolis": "Online marketing",
    "digital-marketing-minneapolis-mn": "Digital marketing services",
    "minneapolis-marketing-firms": "Full-service marketing firm",
    "advertising-companies-minneapolis": "Advertising",
    "social-media-marketing-minneapolis": "Social media marketing",
    "minneapolis-ppc-management": "PPC management",
    "minneapolis-web-design-companies": "Web design",
    "web-developers-minneapolis": "Web development",
    "wordpress-design-minneapolis": "WordPress design",
    "design-agency-minneapolis": "Design agency",
    "graphic-design-firm-minneapolis": "Graphic design",
    "creative-agencies-minneapolis": "Creative agency",
    "branding-agency-minneapolis": "Branding",
    "minneapolis-seo-consultant": "SEO consulting",
    "local-seo-minneapolis": "Local SEO",
}

FOCUS = {
    "": "technical, content and local search priorities for organic growth",
    "marketing-minneapolis": "marketing strategy and planning, and how results are measured",
    "online-marketing-minneapolis": "how search, content and paid media work together, and useful reporting",
    "digital-marketing-minneapolis-mn": "our digital marketing services, process and typical costs",
    "minneapolis-marketing-firms": "what a full-service firm coordinates and how to compare firms",
    "advertising-companies-minneapolis": "advertising campaigns: strategy, creative and measurement",
    "social-media-marketing-minneapolis": "organic and paid social media campaigns",
    "minneapolis-ppc-management": "Google Ads and paid search management, budgets and conversion data",
    "minneapolis-web-design-companies": "custom website design projects, costs and choosing a designer",
    "web-developers-minneapolis": "website builds, integrations, performance and testing",
    "wordpress-design-minneapolis": "WordPress websites your team can update and maintain",
    "design-agency-minneapolis": "strategy-led design for websites built to convert",
    "graphic-design-firm-minneapolis": "logos, visual identity and marketing graphics",
    "creative-agencies-minneapolis": "creative campaigns and content, from brief to launch",
    "branding-agency-minneapolis": "brand positioning, identity systems and rebrands",
    "minneapolis-seo-consultant": "SEO consulting: audits, strategy and advice for your team",
    "local-seo-minneapolis": "Google Business Profile, map results and local rankings",
}

# decorative images: short alt + aria-hidden (SEO tools flag alt="" as missing)
DECORATIVE_ALT = {
    "/assets/1094/extra/minneapolis-skyline.webp": "Minneapolis skyline",
    "/assets/1094/favicon-32.png": "Website Design & SEO Solutions icon",
}

# pages that are not about a service: WebPage.about points at the business instead of a topic
ABOUT_BUSINESS = ["contact", "privacy-policy", "terms-of-use"]
