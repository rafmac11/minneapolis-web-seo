"""Content for the contractor lead generation pages (hub + one page per trade)."""

HUB = "contractor-lead-generation"

def steps(*items):
    return [{"n": f"0{i + 1}", "h": h, "p": p} for i, (h, p) in enumerate(items)]

PAGES = [
# ------------------------------------------------------------------ hub
{
 "slug": HUB, "nav": "Home Service Contractors", "long": "Contractor Lead Generation",
 "blurb": "Websites, local search, ads and automated follow-up that turn searches into booked jobs for home service contractors.",
 "title": "Contractor Lead Generation for Home Service Businesses",
 "desc": "Lead generation for landscapers, irrigation, snow removal, concrete and towing companies: websites, local SEO, ads and automated follow-up that books jobs.",
 "kicker": "Lead generation for home service contractors",
 "h1": "Lead Generation for Home Service Contractors",
 "lead": "We build the whole system that brings you work: a website that sells the job, <strong>local search and ads</strong> that put you in front of homeowners, and automation that answers every lead before your competitor does.",
 "chips": ["Booked jobs, not clicks", "Every lead answered", "Minnesota based, nationwide"],
 "alerts": [
   {"src": "Google call", "job": "Tow needed, car won't start", "where": "Bloomington, MN", "note": "Missed call, text reply sent"},
   {"src": "Website form", "job": "Patio and retaining wall quote", "where": "Plymouth, MN", "note": "Added to CRM, estimate booked"},
   {"src": "Local Services Ad", "job": "Seasonal snow plowing contract", "where": "Eden Prairie, MN", "note": "Routed to sales"}],
 "sections": [
  {"type": "prose", "h2": "Built for Contractors Who Run Their Business From the Truck",
   "paras": [
     "Most home service contractors do not lose work because they are bad at the job. They lose it because a homeowner searched, found three companies, and hired the first one that answered. When you are on a job site, behind a plow or under a vehicle, that is hard to win by hand.",
     "Our lead generation work for contractors covers both halves of the problem. First we make sure the right homeowners and property managers find you: a fast website with a page for every service, a complete Google Business Profile, local SEO for the towns you serve and, when it makes sense, paid search and Local Services Ads.",
     "Then our SaaS developers connect what happens next. Calls, forms and messages are captured in one place, missed calls get an instant text back, leads are routed to the right person, and follow-ups and review requests go out automatically. You see which channels produce booked jobs, not just traffic."]},
  {"type": "cards", "h2": "Trades We Build Lead Systems For", "kicker": "Each trade buys, books and pays differently",
   "intro": "Seasonality, urgency and job size change how a lead should be found and handled. These are the trades we have built dedicated playbooks for.",
   "items": [
     {"h": "Landscaping and Lawn Care", "href": "/landscaping-lead-generation/", "p": "Design-build, hardscape and maintenance leads, with seasonal campaigns timed to spring cleanups and fall work."},
     {"h": "Irrigation and Sprinkler Companies", "href": "/irrigation-lead-generation/", "p": "Installs, repairs, spring startups and fall winterizations, plus reminders that turn one-time customers into yearly service."},
     {"h": "Snow Removal and Plowing", "href": "/snow-removal-lead-generation/", "p": "Seasonal contracts sold before the first storm, and storm-day calls captured when every competitor is busy."},
     {"h": "Concrete Contractors", "href": "/concrete-contractor-lead-generation/", "p": "Driveway, patio, foundation and decorative concrete leads, qualified by project size and timeline before you drive out."},
     {"h": "Towing Companies", "href": "/towing-lead-generation/", "p": "Phone-first visibility for urgent searches and a system that makes sure no emergency call goes unanswered."},
     {"h": "Other Home Service Trades", "href": "", "p": "Fencing, tree care, gutters, pressure washing and similar trades follow the same pattern. Ask us about yours."}]},
  {"type": "cards", "h2": "What the Lead System Includes", "kicker": "Found, answered, followed up, measured",
   "intro": "",
   "items": [
     {"h": "Contractor Website and Landing Pages", "href": "/minneapolis-web-design-companies/", "p": "A mobile-first site with a page for each service and service area, project photos, reviews and a quote form that asks the right questions."},
     {"h": "Local SEO and Google Business Profile", "href": "/local-seo-minneapolis/", "p": "Map visibility, categories, service areas, photos and review flow for the towns where you want work."},
     {"h": "Paid Search and Local Services Ads", "href": "/minneapolis-ppc-management/", "p": "Google Ads and Local Services Ads where your trade and market are eligible, scheduled around when you can take the work."},
     {"h": "Missed-Call Text Back and Instant Replies", "href": "", "p": "Every missed call and form gets an immediate text so the homeowner knows you are on it, even when you are on a job."},
     {"h": "CRM Routing and Automated Follow-Up", "href": "/web-developers-minneapolis/", "p": "Leads land in your CRM or field service software, go to the right person, and get follow-ups until they book or say no."},
     {"h": "Call Tracking, Reviews and Reporting", "href": "", "p": "See cost per booked job by channel, and send review requests automatically after the work is done."}]},
  {"type": "steps", "h2": "How Contractor Lead Generation Works", "kicker": "From first search to booked job",
   "intro": "We set up the system once, then keep tuning it around the jobs you actually want.",
   "items": steps(
     ("Define the jobs worth chasing", "We agree on the services, job sizes, towns and seasons you want more of, and the ones you would rather turn down."),
     ("Fix how you get found", "Website pages, Google Business Profile, local SEO and, if needed, ad campaigns are built around those jobs and areas."),
     ("Connect every lead to a response", "Calls, forms, texts and ad leads flow into one place with instant replies, routing and follow-up sequences."),
     ("Book, review and repeat", "Booked jobs trigger review requests, and past customers get reminders for seasonal or repeat work."),
     ("Report on booked jobs", "Monthly reporting shows leads, booked jobs and cost per job by channel, so budget goes where it pays."))},
  {"type": "band", "text": "Missing calls while you are on a job? We can usually set up missed-call text back first, before anything else."},
  {"type": "prose", "h2": "Based in Minnesota, Working With Contractors Nationwide",
   "paras": [
     "We are based in the North Loop of Minneapolis, so we know what a Minnesota season does to a contractor's calendar: the spring rush, the short concrete and irrigation windows, and the snow contracts that need to be signed before November.",
     "The same lead system works anywhere. We set up contractors across the United States with local search, ads and automation tuned to their own markets and seasons."]},
  {"type": "faq", "h2": "Contractor Lead Generation FAQs", "kicker": "Common questions from contractors",
   "items": [
     {"q": "Do I need a new website to start?", "a": "Not always. If your current site loads fast, works on phones and has a page for each service, we can build on it. If it is slow or hard to update, a new contractor site is usually the fastest way to improve lead quality."},
     {"q": "How quickly will I see leads?", "a": "Paid search and Local Services Ads can start producing calls soon after launch. Local SEO and Google Business Profile improvements build over several months. Most contractors use both: ads for steady volume now and organic search for lower cost over time."},
     {"q": "Can you connect to the CRM or field service software I already use?", "a": "In most cases, yes. Our developers connect common CRMs and field service tools, and can build custom integrations when a standard connection does not exist."},
     {"q": "Do you only work with contractors in Minnesota?", "a": "No. We are based in Minneapolis and work with home service contractors nationwide."},
     {"q": "What does contractor lead generation cost?", "a": "It depends on your trade, the size of your service area and whether paid ads are included. Call us and we will give you a clear scope and price after looking at your current setup."}]},
  {"type": "final", "h2": "Get More Booked Jobs From the Leads You Already Pay For",
   "paras": ["Tell us your trade, your service area and how leads reach you today. We will show you where jobs are slipping through and what we would fix first."]},
 ]},
# ------------------------------------------------------------------ landscaping
{
 "slug": "landscaping-lead-generation", "nav": "Landscaping", "long": "Landscaping Lead Generation",
 "blurb": "Design-build, hardscape and maintenance leads for landscapers, timed to the season and filtered by job size.",
 "title": "Lead Generation for Landscapers and Lawn Care Companies",
 "desc": "Landscaping lead generation for the jobs you want: design-build, hardscape and maintenance leads from search, maps and ads, followed up automatically.",
 "kicker": "Landscaping lead generation",
 "h1": "Lead Generation for Landscaping Companies",
 "lead": "Fill your schedule with the jobs you actually want: <strong>design-build, hardscape and maintenance contracts</strong>, found through search and maps and followed up automatically while your crews are working.",
 "chips": ["Seasonal campaigns", "Bigger projects", "Maintenance contracts"],
 "alerts": [
   {"src": "Website form", "job": "Paver patio and fire pit design", "where": "Minnetonka, MN", "note": "Budget and photos attached"},
   {"src": "Google Business Profile", "job": "Spring cleanup and mulch", "where": "Edina, MN", "note": "Text reply sent automatically"},
   {"src": "Google Ads", "job": "Weekly lawn maintenance", "where": "Wayzata, MN", "note": "Added to route list"}]},
 ]
PAGES[1]["sections"] = [
  {"type": "prose", "h2": "Not Every Landscaping Lead Is Worth the Drive",
   "paras": [
     "A landscaping company can get plenty of calls and still have a bad season. Small one-off mowing requests from the far edge of your service area eat up estimate time, while the patio, retaining wall and planting projects that make the year go to whoever responded first.",
     "Our landscaping lead generation is built around the work you want more of. Service pages, ads and your Google Business Profile focus on design-build, hardscape and maintenance contracts in the towns where your crews already run, and the quote form asks for project type, rough budget and photos so you can prioritize before you call back.",
     "Timing matters as much as targeting. Homeowners start planning spring projects in late winter, cleanups spike when the snow melts, and fall cleanups and next-year planning follow. Campaigns and follow-ups are scheduled around that calendar instead of running flat all year."]},
  {"type": "cards", "h2": "Where Landscaping Leads Come From", "kicker": "Channels tuned for landscapers", "intro": "",
   "items": [
     {"h": "Service and Project Pages", "href": "/minneapolis-web-design-companies/", "p": "Dedicated pages for patios, retaining walls, planting, sod, lighting and maintenance, each with photos of your real work."},
     {"h": "Google Business Profile and Maps", "href": "/local-seo-minneapolis/", "p": "Categories, service areas, project photos and a steady review flow so you show up when homeowners search nearby."},
     {"h": "Seasonal Google Ads", "href": "/minneapolis-ppc-management/", "p": "Ads that push design-build in late winter, cleanups in spring and fall, and pause when your schedule is full."},
     {"h": "Project Gallery and Reviews", "href": "", "p": "Before-and-after galleries and reviews that mention the project type help homeowners trust you with larger jobs."},
     {"h": "Maintenance Contract Offers", "href": "", "p": "Landing pages and follow-ups that turn one-time cleanup customers into recurring maintenance accounts."},
     {"h": "Past Customer Reactivation", "href": "", "p": "Automatic reminders to last year's customers before spring and fall, when they are most likely to book again."}]},
  {"type": "steps", "h2": "How a Landscaping Lead Gets Handled", "kicker": "While your crews keep working", "intro": "",
   "items": steps(
     ("Homeowner requests a quote", "The form captures the project type, address, rough budget and photos, so you know what the job is before you call."),
     ("Instant reply and qualification", "An automatic text confirms the request and offers estimate times. Leads outside your area or below your minimum are flagged."),
     ("Estimate booked and reminded", "The estimate lands on your calendar with reminders, and quotes that are not accepted get polite follow-ups."),
     ("Job done, review requested", "After the work, the customer gets a review request and is added to seasonal reminders for next year."))},
  {"type": "faq", "h2": "Landscaping Lead Generation FAQs", "kicker": "Questions from landscapers",
   "items": [
     {"q": "Can you focus on hardscape and design-build instead of mowing?", "a": "Yes. Pages, ads and Google Business Profile services are built around the work you want, and the quote form screens out jobs below your minimum."},
     {"q": "What happens in the off season?", "a": "Late winter is when many homeowners plan spring projects, so that is when design-build campaigns usually start. If you also offer snow removal, we can switch messaging and budget to it for winter."},
     {"q": "Do you write the content for my service pages?", "a": "Yes. We write each page from your services, process and project photos, so it reads like your company rather than a template."},
     {"q": "Will this work if I serve several suburbs?", "a": "Yes. We set up service-area pages and targeting for the towns your crews cover, and keep ads out of areas you do not want to drive to."}]},
  {"type": "final", "h2": "Book More of the Landscaping Jobs You Want",
   "paras": ["Tell us which projects you want more of and where your crews work. We will show you how to get them in front of the right homeowners this season."]},
]
PAGES.append({
 "slug": "irrigation-lead-generation", "nav": "Irrigation and Sprinklers", "long": "Irrigation and Sprinkler Lead Generation",
 "blurb": "Installs, repairs, spring startups and fall winterization leads, plus reminders that turn customers into yearly service.",
 "title": "Irrigation and Sprinkler Company Lead Generation",
 "desc": "Lead generation for irrigation and sprinkler companies: installs, repairs, startups and winterizations from search and maps, plus automated reminders.",
 "kicker": "Irrigation and sprinkler lead generation",
 "h1": "Lead Generation for Irrigation and Sprinkler Companies",
 "lead": "Get found for <strong>new installs, repairs, spring startups and fall winterizations</strong>, and let automated reminders bring last year's customers back before the rush.",
 "chips": ["Install and repair leads", "Startup and blowout season", "Repeat service"],
 "alerts": [
   {"src": "Google call", "job": "Broken sprinkler head, zone leaking", "where": "Maple Grove, MN", "note": "Missed call, text reply sent"},
   {"src": "Website form", "job": "New irrigation system, front and back yard", "where": "Woodbury, MN", "note": "Estimate booked"},
   {"src": "Reminder campaign", "job": "Fall winterization, returning customer", "where": "Roseville, MN", "note": "Booked online"}],
 "sections": [
  {"type": "prose", "h2": "Two Busy Seasons and a Lot of Repeat Work",
   "paras": [
     "Irrigation work comes in waves. Spring startups and repairs pile up as soon as the ground thaws, installs fill late spring and summer, and in colder states fall winterizations and blowouts all need to happen before the first hard freeze. Between those peaks, the phone can go quiet.",
     "Irrigation lead generation works best when it treats those waves differently. New install campaigns target homeowners and builders with larger projects. Repair and startup searches need fast, phone-first visibility in maps. And winterization is mostly repeat business, which is cheaper to win from your own customer list than from ads.",
     "We build the website pages, Google Business Profile, local SEO and ads for the first two, and the automation for the third: reminders, online booking and follow-ups that fill your startup and blowout routes before the season starts."]},
  {"type": "cards", "h2": "Where Irrigation Leads Come From", "kicker": "Channels tuned for sprinkler companies", "intro": "",
   "items": [
     {"h": "Install and Repair Pages", "href": "/minneapolis-web-design-companies/", "p": "Separate pages for new systems, repairs, startups, winterizations, smart controllers and drip irrigation."},
     {"h": "Maps Visibility for Urgent Repairs", "href": "/local-seo-minneapolis/", "p": "A complete Google Business Profile and local SEO so leaking-zone and broken-head searches find you first."},
     {"h": "Seasonal Search Ads", "href": "/minneapolis-ppc-management/", "p": "Ads scheduled for startup and winterization season, and install campaigns when you have crew capacity."},
     {"h": "Service Reminders and Online Booking", "href": "", "p": "Automatic spring and fall reminders to past customers with a simple way to pick a date."},
     {"h": "Backflow and Inspection Notices", "href": "", "p": "Where your local rules require backflow testing, reminders bring customers back on schedule."},
     {"h": "Builder and Property Manager Outreach", "href": "", "p": "Landing pages and follow-ups for commercial properties and new construction installs."}]},
  {"type": "steps", "h2": "How an Irrigation Lead Gets Handled", "kicker": "Fast for repairs, organized for routes", "intro": "",
   "items": steps(
     ("Customer calls or books", "Repair calls, install requests and online bookings all land in one place, tagged by job type."),
     ("Instant reply", "Missed calls get a text back, and booking confirmations go out right away with the next available window."),
     ("Routed by area and season", "Startups and winterizations are grouped by area so routes stay tight, and installs go to estimating."),
     ("Remembered for next season", "Every customer is added to spring and fall reminders, so repeat work books itself."))},
  {"type": "faq", "h2": "Irrigation Lead Generation FAQs", "kicker": "Questions from sprinkler companies",
   "items": [
     {"q": "Can you help us sell more new installs, not just repairs?", "a": "Yes. Install campaigns use separate pages, ads and qualification questions about property size and timeline, so estimating time goes to real projects."},
     {"q": "How do automated reminders work?", "a": "Before spring startup and fall winterization season, past customers get a text or email with a link to book. Replies and bookings land in your schedule or CRM."},
     {"q": "Do you work with irrigation companies outside Minnesota?", "a": "Yes. We work nationwide and adjust campaigns and reminders to your local seasons."},
     {"q": "We also do landscape lighting. Can that be included?", "a": "Yes. Related services get their own pages and can share the same lead system and reminders."}]},
  {"type": "final", "h2": "Fill Your Startup and Winterization Routes Early",
   "paras": ["Tell us how many customers you serve today and which work you want more of. We will show you what the lead system would look like for your company."]},
 ]})
PAGES.append({
 "slug": "snow-removal-lead-generation", "nav": "Snow Removal", "long": "Snow Removal Lead Generation",
 "blurb": "Seasonal plowing contracts sold before the first storm, and storm-day calls captured when competitors are full.",
 "title": "Snow Removal Lead Generation for Plowing Contractors",
 "desc": "Snow removal lead generation: residential and commercial plowing contracts signed before winter, plus storm-day calls captured automatically.",
 "kicker": "Snow removal lead generation",
 "h1": "Lead Generation for Snow Removal Companies",
 "lead": "Sign your <strong>seasonal residential and commercial contracts</strong> before the first storm, then capture the storm-day calls your competitors are too busy to answer.",
 "chips": ["Contracts before winter", "Storm-day calls", "Route density"],
 "alerts": [
   {"src": "Website form", "job": "Seasonal driveway plowing contract", "where": "Apple Valley, MN", "note": "Quote sent automatically"},
   {"src": "Google Ads", "job": "Commercial lot plowing and salting", "where": "Burnsville, MN", "note": "Routed to sales"},
   {"src": "Google call", "job": "Driveway cleared today, 10 in. snow", "where": "Lakeville, MN", "note": "Missed call, text reply sent"}],
 "sections": [
  {"type": "prose", "h2": "Snow Removal Is Sold in the Fall",
   "paras": [
     "Most of a snow removal company's season is decided before it snows. Homeowners and property managers sign seasonal contracts in late summer and fall, and by the first big storm most of them have already chosen a provider. Marketing that starts in December is mostly chasing one-time pushes.",
     "Our snow removal lead generation starts early. From late summer, website pages, ads and your Google Business Profile push seasonal contracts, with clear options for per-push, monthly or seasonal pricing and an easy way to request a quote. Commercial campaigns target property managers, HOAs and businesses that need plowing, salting and sidewalk clearing.",
     "Then, when storms hit, the system switches modes. Storm-day searches get phone-first visibility, missed calls get an instant text, and one-time requests are captured and tagged so you can decide which ones fit your routes once contract customers are cleared."]},
  {"type": "cards", "h2": "Where Snow Removal Leads Come From", "kicker": "Channels tuned for plowing contractors", "intro": "",
   "items": [
     {"h": "Seasonal Contract Pages", "href": "/minneapolis-web-design-companies/", "p": "Residential and commercial pages that explain service levels, triggers, pricing options and what is included."},
     {"h": "Google Business Profile in Winter", "href": "/local-seo-minneapolis/", "p": "Updated services, winter hours and photos so storm-day searches find you in maps."},
     {"h": "Early-Season Ads", "href": "/minneapolis-ppc-management/", "p": "Contract campaigns from late summer through fall, then short storm-day bursts if you have capacity."},
     {"h": "Commercial Property Outreach", "href": "", "p": "Landing pages and follow-ups for property managers, HOAs, churches and retail lots."},
     {"h": "Renewal Reminders", "href": "", "p": "Automatic renewal offers to last season's customers before they start shopping around."},
     {"h": "Route-Aware Lead Filtering", "href": "", "p": "Leads are tagged by address so you can say yes to jobs that fit your routes and decline the rest quickly."}]},
  {"type": "steps", "h2": "How a Snow Removal Lead Gets Handled", "kicker": "Contracts first, storm calls second", "intro": "",
   "items": steps(
     ("Request comes in", "Contract requests, commercial inquiries and storm-day calls are captured from every channel and tagged by type."),
     ("Instant response", "Contract leads get pricing options or a quote request right away. Missed storm calls get a text so the customer does not keep dialing others."),
     ("Checked against your routes", "Each address is matched to your service area, so you can quickly accept jobs that fit and decline those that do not."),
     ("Renewed next season", "Contract customers get renewal offers before next winter, and one-time customers get a seasonal contract offer."))},
  {"type": "faq", "h2": "Snow Removal Lead Generation FAQs", "kicker": "Questions from plowing contractors",
   "items": [
     {"q": "When should snow removal marketing start?", "a": "Late summer or early fall. That is when most homeowners and property managers decide on seasonal contracts, and leads are usually cheaper than in the middle of winter."},
     {"q": "Can you target commercial properties only?", "a": "Yes. Commercial campaigns focus on property managers, HOAs and businesses, with pages and follow-ups that address service levels, insurance and response times."},
     {"q": "What about storm days when we are already full?", "a": "Ads can be paused, and missed calls still get an automatic text. One-time requests are saved so you can follow up once contract work is done."},
     {"q": "We do landscaping in summer. Can the same system handle both?", "a": "Yes. Many of our contractors run landscaping or lawn care in summer and snow removal in winter on one website and lead system, with messaging that switches by season."}]},
  {"type": "final", "h2": "Sign Next Winter's Contracts Before the First Storm",
   "paras": ["Tell us your service area and the mix of residential and commercial work you want. We will plan a contract campaign around your season."]},
 ]})
PAGES.append({
 "slug": "concrete-contractor-lead-generation", "nav": "Concrete Contractors", "long": "Concrete Contractor Lead Generation",
 "blurb": "Driveway, patio, foundation and decorative concrete leads qualified by project size and timeline.",
 "title": "Concrete Contractor Lead Generation and Marketing",
 "desc": "Concrete contractor lead generation: driveway, patio, foundation and decorative leads from search and maps, qualified by project size before you quote.",
 "kicker": "Concrete contractor lead generation",
 "h1": "Lead Generation for Concrete Contractors",
 "lead": "Win more <strong>driveway, patio, foundation and decorative concrete projects</strong> with leads that arrive with photos, measurements and a timeline, so you quote the right jobs first.",
 "chips": ["Higher-value projects", "Qualified estimates", "Pour-season planning"],
 "alerts": [
   {"src": "Website form", "job": "Driveway replacement, 24 x 40 ft", "where": "Shakopee, MN", "note": "Photos attached, estimate booked"},
   {"src": "Google Business Profile", "job": "Stamped concrete patio", "where": "Chanhassen, MN", "note": "Text reply sent automatically"},
   {"src": "Google Ads", "job": "Sunken sidewalk repair", "where": "Richfield, MN", "note": "Added to repair list"}],
 "sections": [
  {"type": "prose", "h2": "Concrete Leads Need Qualifying Before You Drive Out",
   "paras": [
     "Concrete jobs are high value and slow to close. A homeowner may collect three or four bids, wait for financing or plan around the season, and many requests are too small or too far away to be worth an in-person estimate. Every unqualified site visit costs a crew lead half a morning.",
     "Our concrete contractor lead generation puts qualification up front. Each service has its own page, from driveways and patios to foundations, steps, stamped and decorative work, and repair or leveling. The quote form asks for project type, approximate size, photos and timeline, and leads outside your area or minimum are flagged before anyone gets in a truck.",
     "Because people compare bids, follow-up is where many concrete jobs are won. Automated check-ins after the estimate, project galleries that show finished work, and reviews that mention specific project types help homeowners choose you over the lower bid."]},
  {"type": "cards", "h2": "Where Concrete Leads Come From", "kicker": "Channels tuned for concrete contractors", "intro": "",
   "items": [
     {"h": "Project-Type Pages", "href": "/minneapolis-web-design-companies/", "p": "Pages for driveways, patios, foundations, steps, stamped and decorative concrete, and repair, each with real project photos."},
     {"h": "Local SEO and Maps", "href": "/local-seo-minneapolis/", "p": "Google Business Profile, service areas and reviews so you show up for concrete searches in the towns you serve."},
     {"h": "Paid Search for Big Projects", "href": "/minneapolis-ppc-management/", "p": "Ads focused on driveway replacement, patios and decorative work, kept away from low-value repair searches unless you want them."},
     {"h": "Photo-Based Quote Requests", "href": "", "p": "Forms that collect photos, measurements and timeline so you can give rough pricing or skip a site visit."},
     {"h": "Estimate Follow-Up", "href": "", "p": "Automatic follow-ups after you send a bid, so homeowners comparing quotes hear from you again."},
     {"h": "Builder and Commercial Leads", "href": "", "p": "Landing pages and outreach for builders and property owners who need flatwork, foundations or repairs."}]},
  {"type": "steps", "h2": "How a Concrete Lead Gets Handled", "kicker": "Qualified before the estimate", "intro": "",
   "items": steps(
     ("Homeowner submits a project", "The form captures project type, size, photos, address and timeline."),
     ("Instant reply and screening", "An automatic text confirms the request. Jobs outside your area or below your minimum are flagged for a quick decline or referral."),
     ("Estimate booked and followed up", "Qualified projects get an estimate time, and bids that are not accepted get follow-ups over the next few weeks."),
     ("Finished work becomes marketing", "Completed jobs trigger review requests, and project photos go into your gallery and Google Business Profile."))},
  {"type": "faq", "h2": "Concrete Lead Generation FAQs", "kicker": "Questions from concrete contractors",
   "items": [
     {"q": "Can we avoid small repair jobs?", "a": "Yes. Ads and pages can focus on larger projects, and the quote form flags jobs below your minimum so you can decline or refer them quickly."},
     {"q": "How do you handle the off season?", "a": "In colder climates, winter is when many homeowners plan spring and summer projects. Campaigns shift to booking estimates and collecting deposits for the next pour season."},
     {"q": "Do you work with commercial concrete contractors?", "a": "Yes. Commercial work gets separate pages and outreach for builders, property managers and general contractors."},
     {"q": "Can you show our past projects on the website?", "a": "Yes. We build project galleries from your photos, organized by project type, and use them on service pages and your Google Business Profile."}]},
  {"type": "final", "h2": "Quote Fewer Jobs and Win More of Them",
   "paras": ["Tell us the projects you want and the areas you cover. We will show you how qualified concrete leads would reach your crew."]},
 ]})
PAGES.append({
 "slug": "towing-lead-generation", "nav": "Towing Companies", "long": "Towing Company Lead Generation",
 "blurb": "Phone-first visibility for urgent towing searches and a system that makes sure no emergency call is missed.",
 "title": "Towing Company Lead Generation and Marketing",
 "desc": "Towing lead generation: show up first for urgent tow truck searches, answer every call with missed-call text back, and track which calls become paid tows.",
 "kicker": "Towing lead generation",
 "h1": "Lead Generation for Towing Companies",
 "lead": "Show up first when a driver searches for a tow truck, and make sure <strong>every urgent call gets answered</strong>, even when every truck is already out.",
 "chips": ["Phone-first visibility", "No missed calls", "Private-pay calls"],
 "alerts": [
   {"src": "Google call", "job": "Tow needed, I-494 shoulder", "where": "Bloomington, MN", "note": "Answered, truck dispatched"},
   {"src": "Google call", "job": "Lockout in parking ramp", "where": "Downtown Minneapolis", "note": "Missed call, text reply sent"},
   {"src": "Website form", "job": "Junk car pickup, no title issues", "where": "Brooklyn Park, MN", "note": "Quote sent automatically"}],
 "sections": [
  {"type": "prose", "h2": "Towing Customers Call the First Company That Answers",
   "paras": [
     "Almost nobody plans a tow. A driver is stuck on a shoulder or in a parking lot, searches on their phone, and calls the first company that looks close and available. If that call rings out, they hang up and call the next one. For a towing company, visibility and answering speed are the whole game.",
     "Our towing lead generation is phone-first. Your Google Business Profile, local SEO and mobile site are built so you appear close to where drivers search, with a large tap-to-call button and clear service details: towing, roadside assistance, lockouts, jump starts, accident recovery, heavy-duty and junk car removal, whichever you offer.",
     "Then we protect every call. Call tracking shows which channels produce tows, missed calls get an instant text asking for location and vehicle details, and ads are scheduled around your dispatch capacity so you are not paying for calls you cannot take."]},
  {"type": "cards", "h2": "Where Towing Leads Come From", "kicker": "Channels tuned for towing companies", "intro": "",
   "items": [
     {"h": "Google Business Profile and Maps", "href": "/local-seo-minneapolis/", "p": "Accurate categories, hours, service area and photos of your trucks, so you show up in map results near the driver."},
     {"h": "Mobile Site With Tap-to-Call", "href": "/minneapolis-web-design-companies/", "p": "A fast mobile site where calling you takes one tap, with pages for each service and area you cover."},
     {"h": "Call-Focused Search Ads", "href": "/minneapolis-ppc-management/", "p": "Ads built for phone calls, scheduled around your dispatch capacity and focused on areas your trucks can reach quickly."},
     {"h": "Missed-Call Text Back", "href": "", "p": "Every missed call gets a text asking for location and vehicle details, so the driver waits for you instead of calling someone else."},
     {"h": "Call Tracking and Recording", "href": "", "p": "See which channels produce paid tows and review calls to improve how dispatch handles them."},
     {"h": "Reviews After Every Job", "href": "", "p": "Automatic review requests after each tow build the ratings drivers check before they call."}]},
  {"type": "steps", "h2": "How a Towing Lead Gets Handled", "kicker": "Every call answered", "intro": "",
   "items": steps(
     ("Driver searches and calls", "Map results, your mobile site and call ads all route to a tracked number for your dispatch."),
     ("Answered or texted instantly", "If dispatch is busy, the caller gets an immediate text asking for location, vehicle and situation."),
     ("Dispatched and logged", "Job details are captured for dispatch and logged by source, so you know which channels bring paying tows."),
     ("Review requested", "After the job, the customer gets a review request, which helps your next map ranking."))},
  {"type": "faq", "h2": "Towing Lead Generation FAQs", "kicker": "Questions from towing companies",
   "items": [
     {"q": "Do you handle 24/7 towing companies?", "a": "Yes. Ads, hours and automation are set up around when you actually dispatch, including overnight and weekend coverage."},
     {"q": "Can you help us get more private-pay calls?", "a": "Yes. Search visibility and call ads bring drivers directly to you, and call tracking shows how many of those calls become paid tows."},
     {"q": "We cover several cities. How is that handled?", "a": "We set up service-area pages and Google Business Profile service areas for the cities you cover, and keep ads focused on places your trucks can reach quickly."},
     {"q": "Can you track which calls turn into jobs?", "a": "Yes. Calls are tracked by source, and dispatch can mark outcomes so reporting shows cost per paid tow, not just cost per call."}]},
  {"type": "final", "h2": "Answer Every Tow Call and Win More of Them",
   "paras": ["Tell us your service area, your hours and how calls are answered today. We will show you where calls are slipping away and how to catch them."]},
 ]})

LEADGEN_SLUGS = [p["slug"] for p in PAGES]
