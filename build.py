#!/usr/bin/env python3
"""
Skomlin Press static site generator.

Reads data/books.json, data/contributors.json, data/covers.json, data/intros.json
and writes the whole site into out/.

Run:  python3 build.py
"""

import io, os, json, html, shutil, datetime

SITE = "https://www.skomlin.com"
GA_ID = "G-710SD8SG0B"
VERIFY = "OJfXcFtcKyvEjxEm_CK0HJMlh67OT9BcnJcAQPFmtxc"
TRADE_FORM = ("https://ed600acc.sibforms.com/serve/MUIFAKoObqmj29mC9g8958g5c7HArpt-dN8N4mxNYcGP1yBPODT2"
              "_KWJkoSnFzzjppiPGpWaI03mnq9X_mqFnuTcDonTbxmmm4FYHj5UqCTgMPnotarxS4r_GrcITTofSc6DgSG65Ljv7hpAwfwC"
              "299i6_1BVaaFA0b5g-j7PlROYAxpsl7w3hqrlkgE602d-G0fSUl14zTIibhISw==")
READER_FORM = ("https://ed600acc.sibforms.com/serve/MUIFAPIui-LYJQYC8j5i97A4hh5LfBwdReh5On1MIe7CXMI8qS5X969I1iSeKLSjP9"
               "-w7bHR7_4QuVlGZUugWEGrZhEy17553aYqIEhT0UsLE37GNutjnzC5dl5aD1A_yuSMEBbKmcQNjBnzkAnPgrx5M8PyXncLyNU0"
               "ySStQs9vnP62acevZEx-aq5bg008B6A4xOnGNmgEz8-UdA==")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

def load(name):
    with io.open(os.path.join(HERE, "data", name), encoding="utf-8") as f:
        return json.load(f)

BOOKS = load("books.json")
CONTRIBUTORS = load("contributors.json")
COVERS = load("covers.json")
try:
    INTROS = load("intros.json")
except IOError:
    INTROS = {}
try:
    ESSAYS = load("essays.json")   # slug -> {"heading", "source", "html"}; long essays on contributor pages
except IOError:
    ESSAYS = {}

BY_SLUG = {b["slug"]: b for b in BOOKS}
E = lambda s: html.escape(s or "", quote=True)

def write(relpath, text):
    path = os.path.join(OUT, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(text)

# ---------------------------------------------------------------- seal

def logo(kind="eagle", cls="brand-mark"):
    """The Skomlin mark. kind: eagle (bird only) or lockup (bird over SKOMLIN)."""
    alt = "Skomlin Press" if kind == "lockup" else "The Skomlin eagle"
    return ('<img class="%s" src="/assets/logo-%s.svg" alt="%s" width="%s" height="%s">'
            % (cls, kind, alt, "616" if kind == "eagle" else "799",
               "851" if kind == "eagle" else "911"))


# ---------------------------------------------------------------- shell

NAV = [("/catalogue/", "Catalogue", "catalogue"),
       ("/contributors/", "Translators &amp; Authors", "contributors"),
       ("/trade/", "For Booksellers", "trade"),
       ("/about/", "About", "about"),
       ("/news/", "News", "news")]

def head(title, desc, canonical, image=None, image_alt=None, og_type="website", extra=""):
    img = image or (SITE + "/social-card.png")
    alt = image_alt or "The Skomlin Press wordmark in cream on a crimson ground"
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(canonical)s">
<meta name="google-site-verification" content="%(verify)s" />
<meta name="theme-color" content="#8B1A1A">
<meta property="og:type" content="%(og_type)s">
<meta property="og:site_name" content="Skomlin Press">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="%(img)s">
<meta property="og:image:alt" content="%(alt)s">
<meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(img)s">
<script async src="https://www.googletagmanager.com/gtag/js?id=%(ga)s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%(ga)s');
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&display=swap" rel="stylesheet">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css">
%(extra)s</head>
<body>
""" % dict(title=E(title), desc=E(desc), canonical=canonical, verify=VERIFY,
           og_type=og_type, img=img, alt=E(alt), ga=GA_ID, extra=extra)

def header(active=None):
    links = "".join(
        '      <a href="%s"%s>%s</a>\n' % (href, ' class="active"' if key == active else "", label)
        for href, label, key in NAV)
    return """<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="/">
      %s
      <div>
        <span class="brand-word">Skomlin</span>
        <span class="brand-sub">Press &amp; Catalogue</span>
      </div>
    </a>
    <button class="nav-toggle" id="navToggle" aria-label="Menu" aria-expanded="false">&#9776;</button>
    <nav class="main-nav" id="mainNav">
%s    </nav>
  </div>
</header>

<main>
""" % (logo("eagle"), links)

FOOTER = """</main>

<iframe name="skomlin-sink" title="Form submission target" aria-hidden="true" tabindex="-1" style="display:none; width:0; height:0; border:0;"></iframe>

<footer class="colophon">
  <div class="wrap">
    %(lockup)s
    <div class="cl">Set in EB Garamond. World literature in translation, printed on demand.</div>
    <div style="width:100%%; max-width:480px; margin-top:4px;">
      <div class="eyebrow" style="margin-bottom:10px;">New titles &amp; reading notes</div>
      <form class="signup-form" data-ctx="reader" method="POST" target="skomlin-sink" action="%(reader)s" onsubmit="return handleSignup(event)" style="display:flex; gap:8px; flex-wrap:wrap; justify-content:center;">
        <label class="visually-hidden" for="sf-email-reader">Email address</label>
        <input type="email" id="sf-email-reader" name="EMAIL" required placeholder="your@email.com" style="padding:10px 12px; border:1px solid var(--rule); border-radius:2px; font-family:inherit; font-size:0.95rem; background:var(--white); color:var(--slate); flex:1; min-width:180px;">
        <input class="hp-field" type="text" name="email_address_check" value="" tabindex="-1" autocomplete="off" aria-hidden="true">
        <input type="hidden" name="locale" value="en">
        <button type="submit" class="btn btn-primary" style="border:none; padding:10px 22px; white-space:nowrap;">Subscribe</button>
      </form>
      <div class="confirm" id="confirm-reader">
        <div class="tick">&#10003;</div>
        <div style="color:var(--slate-light); font-size:0.92rem;">Almost there. Check your email and click the confirmation link.</div>
      </div>
    </div>
    <div class="clinks">
      <a href="/catalogue/">Catalogue</a>
      <a href="/contributors/">Contributors</a>
      <a href="/trade/">Trade</a>
      <a href="/about/">About</a>
      <a href="/news/">News</a>
    </div>
  </div>
</footer>
<script src="/assets/site.js"></script>
</body>
</html>
"""

def footer():
    return FOOTER % dict(lockup=logo("lockup", "colophon-mark"), reader=READER_FORM)

def page(title, desc, canonical, body, active=None, image=None, image_alt=None,
         og_type="website", extra=""):
    return head(title, desc, canonical, image, image_alt, og_type, extra) + header(active) + body + footer()

# ---------------------------------------------------------------- pieces

def display_name(name):
    return " ".join(p.strip() for p in reversed(name.split(","))).strip()

def primary_authors(book):
    a = [c for c in book["contributors"] if (c.get("role") or "").lower() == "author"]
    a = a or book["contributors"][:1]
    return ", ".join(display_name(c["name"]) for c in a)

def cover_img(book, lazy=True):
    src = COVERS.get(book["slug"])
    if src:
        return ('<div class="cover-real"><img src="%s" alt="Front cover of %s" %s></div>'
                % (src, E(book["title"]), 'loading="lazy"' if lazy else ""))
    return ('<div class="cover cv-1"><div class="cover-title">%s</div><div class="cover-rule"></div>'
            '<div class="cover-author">%s</div><div class="cover-imprint">Skomlin</div></div>'
            % (E(book["title"]), E(primary_authors(book))))

def book_card(book):
    blurb = book.get("short_description") or ""
    return """      <a class="book-card" href="/books/%s/">
        %s
        <div class="meta">
          <div class="t">%s</div>
          <div class="a">%s</div>
        </div>
        <p class="card-blurb">%s</p>
      </a>
""" % (book["slug"], cover_img(book), E(book["title"]), E(primary_authors(book)), E(blurb))

def price_row(book):
    row = []
    for key, label, sym in (("us_list", "USD", "$"), ("uk_list", "GBP", "£"),
                            ("eur_list", "EUR", "€"), ("aus_list", "AUD", "A$")):
        if book.get(key):
            row.append("<b>%s</b>&nbsp;%s%.2f" % (label, sym, float(book[key])))
    return "&ensp;·&ensp;".join(row)

def facts(book):
    items = []
    if book.get("format"):
        items.append("<span><b>Format</b> %s</span>" % E(book["format"]))
    if book.get("page_count"):
        items.append("<span><b>Pages</b> %s</span>" % E(str(book["page_count"])))
    pr = price_row(book)
    if pr:
        items.append('<span class="price-row">%s</span>' % pr)
    if book.get("bisac"):
        items.append("<span><b>Category</b> %s</span>" % E(book["bisac"]))
    return "".join(items)

def jsonld_book(book):
    authors = [display_name(c["name"]) for c in book["contributors"]
               if (c.get("role") or "").lower() == "author"]
    translators = [display_name(c["name"]) for c in book["contributors"]
                   if (c.get("role") or "").lower() == "translator"]
    offers = []
    for key, cur in (("us_list", "USD"), ("uk_list", "GBP"),
                     ("eur_list", "EUR"), ("aus_list", "AUD")):
        if book.get(key):
            offers.append({"@type": "Offer", "price": "%.2f" % float(book[key]),
                           "priceCurrency": cur,
                           "availability": "https://schema.org/InStock",
                           "url": "%s/books/%s/" % (SITE, book["slug"])})
    data = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": book["title"],
        "url": "%s/books/%s/" % (SITE, book["slug"]),
        "isbn": book["isbn"],
        "bookFormat": "https://schema.org/Paperback",
        "inLanguage": "en",
        "publisher": {"@type": "Organization", "name": "Skomlin Press", "url": SITE + "/"},
    }
    if authors:
        data["author"] = [{"@type": "Person", "name": n} for n in authors]
    if translators:
        data["translator"] = [{"@type": "Person", "name": n} for n in translators]
    if book.get("page_count"):
        data["numberOfPages"] = int(book["page_count"])
    if book.get("short_description"):
        data["description"] = book["short_description"]
    if COVERS.get(book["slug"]):
        data["image"] = SITE + COVERS[book["slug"]]
    if offers:
        data["offers"] = offers
    crumbs = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Catalogue", "item": SITE + "/catalogue/"},
            {"@type": "ListItem", "position": 2, "name": book["title"],
             "item": "%s/books/%s/" % (SITE, book["slug"])}]}
    return ('<script type="application/ld+json">%s</script>\n<script type="application/ld+json">%s</script>\n'
            % (json.dumps(data, ensure_ascii=False), json.dumps(crumbs, ensure_ascii=False)))

def signup_form(ctx, heading=True):
    return """<form class="signup-form" data-ctx="%(ctx)s" method="POST" target="skomlin-sink" action="%(action)s" onsubmit="return handleSignup(event)">
      <div class="field">
        <label for="sf-store-%(ctx)s">Bookshop Name</label>
        <input type="text" id="sf-store-%(ctx)s" name="STORE" required placeholder="e.g. Shakespeare and Company">
      </div>
      <div class="field">
        <label for="sf-name-%(ctx)s">Contact Name</label>
        <input type="text" id="sf-name-%(ctx)s" name="FIRSTNAME" required placeholder="Your name">
      </div>
      <div class="field">
        <label for="sf-email-%(ctx)s">Email</label>
        <input type="email" id="sf-email-%(ctx)s" name="EMAIL" required placeholder="you@bookshop.com">
      </div>
      <div class="field">
        <label for="sf-city-%(ctx)s">City / Country</label>
        <input type="text" id="sf-city-%(ctx)s" name="CITY" placeholder="e.g. Paris, France">
      </div>
      <input class="hp-field" type="text" name="email_address_check" value="" tabindex="-1" autocomplete="off" aria-hidden="true">
      <input type="hidden" name="locale" value="en">
      <button type="submit" class="btn btn-primary" style="width:100%%; border:none;">Join the Trade List</button>
      <div class="form-note">We'll only use this to share new titles, stockist terms, and sell-sheets. No spam, unsubscribe any time.</div>
    </form>
    <div class="confirm" id="confirm-%(ctx)s">
      <div class="tick">&#10003;</div>
      <div class="small-caps" style="color:var(--crimson);">One more step</div>
      <div style="color:var(--slate-light); font-size:0.92rem; margin-top:6px;">Check your email and click the confirmation link to join the list.</div>
    </div>""" % dict(ctx=ctx, action=TRADE_FORM)

# ---------------------------------------------------------------- pages

DESC_HOME = ("Skomlin Press publishes classic and contemporary literature in translation: novels and "
             "novellas from Poland, Switzerland, Russia, France and beyond, in English editions built "
             "to be read again.")

def build_home():
    featured = BOOKS[:6]
    body = """<section class="hero">
  %s
  <div class="eyebrow">World Literature in Translation</div>
  <h1>Books built to be read again.</h1>
  <p class="lede">Skomlin Press publishes classic and contemporary literature from Poland, Switzerland, Russia, France and beyond, brought into English by translators who treat the work as their own.</p>
  <div class="btn-row">
    <a class="btn btn-primary" href="/catalogue/">Browse the Catalogue</a>
    <a class="btn btn-outline" href="/trade/">For Booksellers</a>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="block-head">
      <div class="eyebrow">Recently Added</div>
      <h2>From the Shelf</h2>
    </div>
    <div class="shelf">
%s    </div>
    <div style="text-align:center; margin-top:40px;">
      <a class="btn btn-outline" href="/catalogue/">View Full Catalogue (%d Titles)</a>
    </div>
  </div>
</section>

<section class="trade-band">
  <div class="wrap">
    <div>
      <div class="eyebrow" style="color:var(--cream); opacity:.85;">For Independent Booksellers</div>
      <h2>Stock the Catalogue</h2>
      <p>Skomlin Press distributes through Ingram / Lightning Source International, publisher ID 6060282. Order any title by ISBN through iPage, by EDI, or by calling 1-800-937-8000. Sign up to receive sell sheets and new title announcements.</p>
      <div style="margin-top:22px;"><a class="btn" style="border-color:var(--cream); color:var(--cream);" href="/trade/">Ordering Information</a></div>
    </div>
    <div class="form-card">%s</div>
  </div>
</section>
""" % (logo("eagle", "hero-mark"), "".join(book_card(b) for b in featured), len(BOOKS), signup_form("home"))

    ld = ('<script type="application/ld+json">%s</script>\n' % json.dumps({
        "@context": "https://schema.org", "@type": "Organization",
        "name": "Skomlin Press", "url": SITE + "/",
        "logo": SITE + "/social-card.png",
        "description": DESC_HOME}, ensure_ascii=False))

    write("index.html", page("Skomlin Press, World Literature in Translation", DESC_HOME,
                             SITE + "/", body, active=None, extra=ld))

def build_catalogue():
    roles = sorted({c["role"] for b in BOOKS for c in b["contributors"] if c.get("role")})
    series = sorted({b["series"] for b in BOOKS if b.get("series")})
    body = """<section class="block" style="padding-top:36px;">
  <div class="wrap">
    <div class="block-head" style="margin-bottom:0;">
      <div class="eyebrow">The Full List</div>
      <h1>Catalogue</h1>
    </div>
    <div class="cat-controls">
      <div class="field search">
        <label for="catSearch">Search</label>
        <input type="text" id="catSearch" placeholder="Title, author, translator, or theme&hellip;">
      </div>
      <div class="field">
        <label for="catRole">Contributor Role</label>
        <select id="catRole"><option value="">All roles</option>%s</select>
      </div>
      <div class="field">
        <label for="catSeries">Series</label>
        <select id="catSeries"><option value="">All series</option>%s</select>
      </div>
    </div>
    <div class="cat-count" id="catCount">%d titles</div>
    <div class="shelf" id="catGrid">
%s    </div>
    <div class="empty-state hidden" id="catEmpty">
      <div class="es-title">No titles match</div>
      <div>Try clearing a filter or searching a different term.</div>
    </div>
  </div>
</section>
""" % ("".join('<option value="%s">%s</option>' % (E(r), E(r)) for r in roles),
       "".join('<option value="%s">%s</option>' % (E(s), E(s)) for s in series),
       len(BOOKS),
       "".join(catalogue_card(b) for b in BOOKS))

    ld = ('<script type="application/ld+json">%s</script>\n' % json.dumps({
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": "Skomlin Press Catalogue", "url": SITE + "/catalogue/",
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(BOOKS),
                       "itemListElement": [
                           {"@type": "ListItem", "position": i + 1, "name": b["title"],
                            "url": "%s/books/%s/" % (SITE, b["slug"])}
                           for i, b in enumerate(BOOKS)]}}, ensure_ascii=False))

    desc = ("All %d titles from Skomlin Press: literary fiction, novellas and classics in translation "
            "from Poland, Switzerland, Russia, France and beyond, with prices in four currencies." % len(BOOKS))
    write("catalogue/index.html", page("Catalogue | Skomlin Press", desc,
                                       SITE + "/catalogue/", body, active="catalogue",
                                       extra=ld + '<script src="/assets/catalogue.js" defer></script>\n'))

def catalogue_card(book):
    haystack = " ".join(filter(None, [
        book["title"], book.get("keywords") or "", book.get("short_description") or "",
        " ".join(c["name"] for c in book["contributors"])])).lower()
    roles = "|".join(sorted({c["role"] for c in book["contributors"] if c.get("role")}))
    return """      <a class="book-card" href="/books/%s/" data-roles="%s" data-series="%s" data-search="%s">
        %s
        <div class="meta">
          <div class="t">%s</div>
          <div class="a">%s</div>
        </div>
        <p class="card-blurb">%s</p>
      </a>
""" % (book["slug"], E(roles), E(book.get("series") or ""), E(haystack), cover_img(book),
       E(book["title"]), E(primary_authors(book)), E(book.get("short_description") or ""))

def build_book(book):
    slug = book["slug"]
    byline = " &middot; ".join(
        '<a href="/people/%s/">%s <span style="opacity:.6">(%s)</span></a>' % (c["slug"], E(display_name(c["name"])), E(c["role"]))
        if c.get("role") else '<a href="/people/%s/">%s</a>' % (c["slug"], E(display_name(c["name"])))
        for c in book["contributors"])

    contribs = "".join("""            <div class="contrib-card">
              <div><span class="cn"><a href="/people/%s/">%s</a></span>%s</div>
              %s
            </div>
""" % (c["slug"], E(display_name(c["name"])),
       '<span class="cr">%s</span>' % E(c["role"]) if c.get("role") else "",
       '<div class="cb">%s</div>' % E(c["bio"]) if c.get("bio") else "")
        for c in book["contributors"])

    body = """<div class="detail">
  <div class="wrap">
    <a class="back-link" href="/catalogue/">&larr; Back to Catalogue</a>
    <div class="detail-grid">
      <div class="detail-cover">%(cover)s</div>
      <div>
        <div class="detail-imprint">%(imprint)s Press%(series)s</div>
        <h1>%(title)s</h1>
        <div class="by-line">%(byline)s</div>
        <p class="isbn-line"><span class="small-caps">ISBN</span> <strong>%(isbn)s</strong></p>
        <div class="facts">%(facts)s</div>
        <div class="full-desc">%(desc)s</div>
        %(reviews)s
        <div class="order-note">
          <div class="small-caps" style="color:var(--crimson);">To order</div>
          <p>Available to the trade through Ingram / Lightning Source International. Order by ISBN <strong>%(isbn)s</strong> through iPage, by EDI, or by calling 1-800-937-8000. Skomlin Press publisher ID is 6060282. <a href="/trade/">Full ordering information</a>.</p>
        </div>
        <div class="contrib-block">
          <h2>Contributors</h2>
%(contribs)s        </div>
      </div>
    </div>
  </div>
</div>
""" % dict(cover=cover_img(book, lazy=False), imprint=E(book.get("imprint") or "Skomlin"),
           series=' &middot; ' + E(book["series"]) if book.get("series") else "",
           title=E(book["title"]), byline=byline, isbn=E(book["isbn"]),
           facts=facts(book),
           desc=book.get("full_description") or ("<p>%s</p>" % E(book.get("short_description") or "")),
           reviews='<blockquote class="review-quote">%s</blockquote>' % book["review_quotes"] if book.get("review_quotes") else "",
           contribs=contribs)

    desc = (book.get("short_description") or book["title"])[:300]
    img = SITE + COVERS[slug] if COVERS.get(slug) else None
    title = "%s | Skomlin Press" % book["title"]
    write("books/%s/index.html" % slug,
          page(title, desc, "%s/books/%s/" % (SITE, slug), body, active="catalogue",
               image=img, image_alt="Front cover of %s" % book["title"],
               og_type="book", extra=jsonld_book(book)))

def build_contributors_index():
    keys = sorted(CONTRIBUTORS, key=lambda k: CONTRIBUTORS[k]["name"].lower())
    cards = "".join("""      <a class="contrib-tile" href="/people/%s/">
        <div class="ct-name">%s</div>
        <div class="ct-roles small-caps">%s</div>
        <div class="ct-count">%d title%s</div>
      </a>
""" % (k, E(display_name(CONTRIBUTORS[k]["name"])), E(" / ".join(CONTRIBUTORS[k]["roles"])),
       len(CONTRIBUTORS[k]["books"]), "s" if len(CONTRIBUTORS[k]["books"]) != 1 else "")
        for k in keys)
    body = """<section class="block" style="padding-top:36px;">
  <div class="wrap">
    <div class="block-head">
      <div class="eyebrow">Authors, Translators &amp; Introducers</div>
      <h1>Contributors</h1>
    </div>
    <p class="section-lede">The %d writers, translators, editors and introducers behind the Skomlin list, from Constance Garnett and C. K. Scott Moncrieff to the translators working on the press today.</p>
    <div class="contrib-grid">
%s    </div>
  </div>
</section>
""" % (len(CONTRIBUTORS), cards)
    desc = ("The %d authors, translators and introducers behind the Skomlin Press list, with a page "
            "for each and the titles they worked on." % len(CONTRIBUTORS))
    write("contributors/index.html", page("Translators & Authors | Skomlin Press", desc,
                                          SITE + "/contributors/", body, active="contributors"))

def build_person(slug, c):
    books = [BY_SLUG[b["slug"]] for b in c["books"] if b["slug"] in BY_SLUG]
    name = display_name(c["name"])
    intro = INTROS.get(slug)
    intro_html = '<p class="person-intro">%s</p>' % E(intro) if intro else ""
    bio_html = ('<div class="contrib-bio"><p>%s</p></div>' % E(c["bio"])) if c.get("bio") else ""
    essay = ESSAYS.get(slug)
    if essay:
        bio_html += ('<div class="contrib-bio person-essay"><h2>%s</h2>%s%s</div>'
                     % (E(essay.get("heading") or "About the author"),
                        ('<p class="essay-source">%s</p>' % E(essay["source"])) if essay.get("source") else "",
                        essay["html"]))
    body = """<div class="contrib-header">
  <div class="eyebrow">%(roles)s</div>
  <h1>%(name)s</h1>
  %(intro)s
  %(bio)s
</div>
<section class="block">
  <div class="wrap">
    <div class="block-head"><h2>%(count)s at Skomlin</h2></div>
    <div class="shelf">
%(grid)s    </div>
  </div>
</section>
""" % dict(roles=E(" / ".join(c["roles"])), name=E(name), intro=intro_html, bio=bio_html,
           count="Title" if len(books) == 1 else "Titles",
           grid="".join(book_card(b) for b in books))

    titles = ", ".join(b["title"] for b in books)
    desc = (intro or c.get("bio") or "%s at Skomlin Press." % name)
    desc = (desc[:230].rsplit(" ", 1)[0] + " Titles: " + titles)[:300]
    ld = ('<script type="application/ld+json">%s</script>\n' % json.dumps({
        "@context": "https://schema.org", "@type": "Person", "name": name,
        "url": "%s/people/%s/" % (SITE, slug),
        "description": (c.get("bio") or intro or "")[:500],
        "jobTitle": ", ".join(c["roles"])}, ensure_ascii=False))
    write("people/%s/index.html" % slug,
          page("%s | Skomlin Press" % name, desc, "%s/people/%s/" % (SITE, slug),
               body, active="contributors", og_type="profile", extra=ld))

def build_trade():
    body = """<section class="hero" style="padding-bottom:20px;">
  <div class="eyebrow">For Independent Booksellers</div>
  <h1>Ordering Skomlin Press</h1>
  <p class="lede">Skomlin Press distributes through Ingram / Lightning Source International. All titles are available to order by ISBN through Ingram&rsquo;s standard channels.</p>
</section>
<section class="block">
  <div class="wrap trade-grid">
    <div>
      <h2 style="font-style:italic; color:var(--crimson); font-size:1.5rem;">How to order</h2>
      <div style="margin-top:18px; display:flex; flex-direction:column; gap:22px;">
        <div>
          <div class="small-caps" style="color:var(--crimson);">Ingram iPage</div>
          <div style="color:var(--slate-light); margin-top:4px;">Search by ISBN or publisher ID at <a href="https://www.ingramcontent.com" target="_blank" rel="noopener" style="color:var(--crimson);">ingramcontent.com</a>. Our publisher ID is <strong>6060282</strong>.</div>
        </div>
        <div>
          <div class="small-caps" style="color:var(--crimson);">EDI</div>
          <div style="color:var(--slate-light); margin-top:4px;">Standard EDI ordering is supported through Ingram.</div>
        </div>
        <div>
          <div class="small-caps" style="color:var(--crimson);">By Phone</div>
          <div style="color:var(--slate-light); margin-top:4px;">Call Ingram customer service at <strong>1-800-937-8000</strong> and quote the ISBN or publisher ID.</div>
        </div>
        <div>
          <div class="small-caps" style="color:var(--crimson);">Sell Sheets</div>
          <div style="color:var(--slate-light); margin-top:4px;">One-page sell sheets with hook, comparable titles, and hand-selling notes are available on request. Sign up below and we&rsquo;ll send them to you.</div>
        </div>
      </div>
    </div>
    <div class="form-card">%s</div>
  </div>
</section>
""" % signup_form("trade")
    desc = ("How independent booksellers order Skomlin Press titles: through Ingram and Lightning Source "
            "International by ISBN, on iPage, by EDI or by phone. Publisher ID 6060282.")
    write("trade/index.html", page("Ordering & Trade | Skomlin Press", desc,
                                   SITE + "/trade/", body, active="trade"))

def build_about():
    body = """<section class="hero" style="padding-bottom:10px;">
  <div class="eyebrow">The Press</div>
  <h1>About Skomlin Press</h1>
</section>
<section class="block">
  <div class="about-copy">
    <p>Skomlin Press publishes classic and contemporary literature in translation, novels and novellas from Poland, Switzerland, Russia, France and beyond, brought into English by translators who treat the work as their own rather than a service rendered.</p>
    <p>The list favours books that reward rereading over books built for a single sitting: forgotten classics restored to print, and newer work chosen with the same standard.</p>
    <h2>What We Value</h2>
    <div class="values-row">
      <div class="value-chip"><div class="vt">Permanence</div></div>
      <div class="value-chip"><div class="vt">Rigour</div></div>
      <div class="value-chip"><div class="vt">Craft</div></div>
      <div class="value-chip"><div class="vt">Restraint</div></div>
      <div class="value-chip"><div class="vt">Heritage</div></div>
    </div>
    <h2>The Catalogue</h2>
    <p>%d titles are currently in print, spanning literary fiction, novellas and a long-running commitment to Charles-Ferdinand Ramuz, six of whose novels appear in English from Skomlin. Browse the <a href="/catalogue/">full catalogue</a> or read about the <a href="/contributors/">translators and authors</a> behind it.</p>
    <h2>Getting in Touch</h2>
    <p>Booksellers will find ordering details on the <a href="/trade/">trade page</a>. Announcements of new titles appear on the <a href="/news/">news page</a> and go first to the mailing list below.</p>
  </div>
</section>
""" % len(BOOKS)
    desc = ("Skomlin Press is a small literary imprint publishing classic and contemporary European "
            "literature in English translation, with %d titles in print." % len(BOOKS))
    write("about/index.html", page("About | Skomlin Press", desc, SITE + "/about/", body, active="about"))

def build_news():
    try:
        entries = load("news.json")
    except IOError:
        entries = []
    if entries:
        items = "".join("""    <article class="news-item">
      <time datetime="%s">%s</time>
      <h2>%s</h2>
      %s
    </article>
""" % (e["date"], e.get("display_date") or e["date"], E(e["title"]), e["body"]) for e in entries)
    else:
        items = '    <p class="section-lede">Announcements will appear here. New titles go first to the mailing list below.</p>\n'
    body = """<section class="hero" style="padding-bottom:10px;">
  <div class="eyebrow">Announcements</div>
  <h1>News</h1>
</section>
<section class="block">
  <div class="news-wrap">
%s  </div>
</section>
""" % items
    desc = "New titles, reissues and announcements from Skomlin Press."
    write("news/index.html", page("News | Skomlin Press", desc, SITE + "/news/", body, active="news"))

# ---------------------------------------------------------------- assets

def build_assets():
    with io.open(os.path.join(HERE, "site.css.orig"), encoding="utf-8") as f:
        css = f.read()
    css += """

/* ===== static build additions ===== */
.visually-hidden{position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap;}
.hp-field{position:absolute; left:-9999px; top:-9999px; width:1px; height:1px; opacity:0; pointer-events:none;}
a.brand{text-decoration:none;}
a.book-card{display:block; color:inherit; text-decoration:none;}
.block-head h1{
  font-style:italic; font-weight:500; color:var(--crimson);
  font-size:1.9rem; margin:10px 0 0;
}
.card-blurb{
  font-size:0.86rem; line-height:1.5; color:var(--slate-light);
  margin:8px 2px 0; text-align:left;
  display:-webkit-box; -webkit-line-clamp:5; -webkit-box-orient:vertical; overflow:hidden;
}
.isbn-line{
  margin:0 0 6px; font-size:0.95rem; color:var(--slate);
}
.isbn-line .small-caps{color:var(--crimson); letter-spacing:0.1em; margin-right:4px;}
.order-note{
  margin:30px 0 0; padding:18px 22px; background:var(--cream-deep);
  border-left:3px solid var(--crimson);
}
.order-note p{margin:6px 0 0; font-size:0.95rem; line-height:1.6;}
.order-note a{color:var(--crimson); border-bottom:1px solid transparent;}
.order-note a:hover{border-color:var(--crimson);}
.section-lede{
  max-width:640px; margin:0 auto 32px; text-align:center;
  color:var(--slate-light); font-size:1.05rem; line-height:1.7;
}
.person-intro{
  max-width:640px; margin:18px auto 0; font-size:1.12rem; line-height:1.75;
  text-align:left; color:var(--slate);
}
.contrib-grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:20px;}
.contrib-tile{
  display:block; padding:18px; background:var(--white); border:1px solid var(--rule);
  text-decoration:none; color:inherit; transition:border-color .15s, transform .15s;
}
.contrib-tile:hover{border-color:var(--crimson); transform:translateY(-2px);}
.ct-name{font-weight:600; font-size:1.05rem; color:var(--slate);}
.ct-roles{color:var(--crimson); font-size:0.8rem; margin-top:4px;}
.ct-count{font-size:0.85rem; color:var(--slate-light); margin-top:6px;}
.trade-grid{display:grid; grid-template-columns:1.1fr 1fr; gap:50px; align-items:flex-start;}
@media (max-width:800px){.trade-grid{grid-template-columns:1fr;}}
.detail h2{font-variant:small-caps; letter-spacing:0.08em; color:var(--crimson); font-size:1.05rem; margin-bottom:16px;}
.person-essay{margin-top:40px; padding-top:28px; border-top:1px solid var(--rule);}
.person-essay h2{font-variant:small-caps; letter-spacing:0.08em; color:var(--crimson); font-size:1.05rem; font-weight:600; margin:0 0 4px;}
.person-essay .essay-source{font-size:0.9rem; color:var(--slate-light); font-style:italic; margin:0 0 18px;}
.person-essay p{margin:0 0 1.1em;}
.news-wrap{max-width:680px; margin:0 auto;}
.news-item{padding:0 0 30px; margin-bottom:30px; border-bottom:1px solid var(--rule);}
.news-item:last-child{border-bottom:none;}
.news-item time{
  font-variant:small-caps; letter-spacing:0.1em; font-size:0.82rem; color:var(--crimson);
}
.news-item h2{font-style:italic; font-weight:500; color:var(--crimson); font-size:1.4rem; margin:6px 0 12px;}
.news-item p{margin:0 0 1em; line-height:1.75;}
blockquote.review-quote{margin:30px 0;}
.contrib-header h1{margin-bottom:4px;}
.brand-mark{height:46px; width:auto; display:block; flex-shrink:0;}
.hero-mark{height:112px; width:auto; display:block; margin:0 auto 24px;}
.colophon-mark{height:84px; width:auto; display:block; margin:0 auto;}
@media (max-width:600px){
  .brand-mark{height:38px;}
  .hero-mark{height:88px;}
  .colophon-mark{height:70px;}
}
@media (max-width:820px){
  nav.main-nav{visibility:hidden;}
  nav.main-nav.open{visibility:visible;}
}
"""
    write("assets/site.css", css)

    write("assets/site.js", """/* Skomlin Press, shared behaviour */
(function(){
  var t = document.getElementById('navToggle');
  var n = document.getElementById('mainNav');
  if(t && n){
    t.addEventListener('click', function(){
      var open = n.classList.toggle('open');
      t.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
})();

function handleSignup(e){
  var form = e.target;
  var ctx = form.getAttribute('data-ctx');
  var btn = form.querySelector('button[type="submit"]');
  if(btn){ btn.disabled = true; btn.textContent = 'Submitting\\u2026'; }
  setTimeout(function(){
    form.classList.add('hidden');
    var conf = document.getElementById('confirm-' + ctx);
    if(conf) conf.classList.add('show');
  }, 700);
  return true;
}

/* Old hash addresses keep working: #/book/slug becomes /books/slug/ */
(function(){
  var h = location.hash || '';
  if(h.indexOf('#/') !== 0) return;
  var parts = h.slice(2).split('/').filter(Boolean);
  var map = {catalogue:'/catalogue/', contributors:'/contributors/', trade:'/trade/', about:'/about/'};
  var dest = null;
  if(parts.length === 0) dest = '/';
  else if(parts[0] === 'book' && parts[1]) dest = '/books/' + parts[1] + '/';
  else if(parts[0] === 'contributor' && parts[1]) dest = '/people/' + parts[1] + '/';
  else if(map[parts[0]]) dest = map[parts[0]];
  if(dest && dest !== location.pathname) location.replace(dest);
})();
""")

    write("assets/catalogue.js", """/* Catalogue filtering. Cards are already in the HTML; this only hides and shows them. */
(function(){
  var search = document.getElementById('catSearch');
  var roleSel = document.getElementById('catRole');
  var seriesSel = document.getElementById('catSeries');
  var grid = document.getElementById('catGrid');
  var empty = document.getElementById('catEmpty');
  var count = document.getElementById('catCount');
  if(!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.book-card'));
  var total = cards.length;

  function draw(){
    var q = (search.value || '').trim().toLowerCase();
    var role = roleSel.value;
    var ser = seriesSel.value;
    var shown = 0;
    cards.forEach(function(card){
      var ok = true;
      if(role && (card.getAttribute('data-roles') || '').split('|').indexOf(role) === -1) ok = false;
      if(ok && ser && card.getAttribute('data-series') !== ser) ok = false;
      if(ok && q && (card.getAttribute('data-search') || '').indexOf(q) === -1) ok = false;
      card.classList.toggle('hidden', !ok);
      if(ok) shown++;
    });
    count.textContent = shown === total ? (total + ' titles') : (shown + ' of ' + total + ' titles');
    empty.classList.toggle('hidden', shown !== 0);
  }

  search.addEventListener('input', draw);
  roleSel.addEventListener('change', draw);
  seriesSel.addEventListener('change', draw);
  draw();
})();
""")

def build_meta():
    today = datetime.date.today().isoformat()
    urls = [("/", "1.0", "weekly"), ("/catalogue/", "0.9", "weekly"),
            ("/contributors/", "0.7", "monthly"), ("/trade/", "0.7", "monthly"),
            ("/about/", "0.5", "yearly"), ("/news/", "0.6", "weekly")]
    urls += [("/books/%s/" % b["slug"], "0.8", "monthly") for b in BOOKS]
    urls += [("/people/%s/" % k, "0.5", "monthly") for k in sorted(CONTRIBUTORS)]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri, freq in urls:
        out.append("  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n"
                   "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>"
                   % (SITE, loc, today, freq, pri))
    out.append("</urlset>")
    write("sitemap.xml", "\n".join(out) + "\n")
    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
    write("404.html", page("Page not found | Skomlin Press",
                           "That page does not exist. Browse the Skomlin Press catalogue instead.",
                           SITE + "/404.html",
                           """<section class="hero">
  <div class="eyebrow">404</div>
  <h1>That page has moved, or never was.</h1>
  <p class="lede">Try the <a href="/catalogue/" style="color:var(--crimson);">catalogue</a>, or start again from the <a href="/" style="color:var(--crimson);">front page</a>.</p>
</section>
"""))
    return len(urls)

# ---------------------------------------------------------------- run

def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    build_assets()
    build_home()
    build_catalogue()
    for b in BOOKS:
        build_book(b)
    build_contributors_index()
    for k, c in CONTRIBUTORS.items():
        build_person(k, c)
    build_trade()
    build_about()
    build_news()
    n = build_meta()

    # carry the data and this script into the output so the repo stays self-rebuilding
    shutil.copytree(os.path.join(HERE, "data"), os.path.join(OUT, "data"))
    shutil.copy(os.path.abspath(__file__), os.path.join(OUT, "build.py"))
    shutil.copy(os.path.join(HERE, "site.css.orig"), os.path.join(OUT, "site.css.orig"))
    for f in ("logo-eagle.svg", "logo-lockup.svg"):
        src = os.path.join(HERE, f)
        if not os.path.exists(src):          # in the repo the logos live in assets/
            src = os.path.join(HERE, "assets", f)
        shutil.copy(src, os.path.join(OUT, "assets", f))
    for f in ("favicon.ico", "favicon.svg", "apple-touch-icon.png",
              "icon-512.png", "social-card.png"):
        shutil.copy(os.path.join(HERE, f), os.path.join(OUT, f))

    pages = sum(1 for _, _, fs in os.walk(OUT) for f in fs if f.endswith(".html"))
    print("pages: %d, sitemap urls: %d" % (pages, n))
    print("books %d, contributors %d, covers %d, intros %d"
          % (len(BOOKS), len(CONTRIBUTORS), len(COVERS), len(INTROS)))

if __name__ == "__main__":
    main()
