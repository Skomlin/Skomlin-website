# Skomlin Press website

The site is generated. Do not hand-edit the HTML.

## To change the catalogue

Edit the JSON in `data/`:

- `books.json` — titles, ISBNs, descriptions, prices, contributors per book
- `contributors.json` — the contributor index and biographies
- `covers.json` — slug to cover image path
- `intros.json` — the short introductions on contributor pages
- `news.json` — optional, dated announcements for /news/

Then regenerate:

    python3 build.py

Everything lands in `out/`. Upload the contents of `out/` to the repository root.

## What is generated

Home, /catalogue/, /books/<slug>/ (one per title), /contributors/,
/people/<slug>/ (one per contributor), /trade/, /about/, /news/, /404.html,
plus /assets/site.css, /assets/site.js, /assets/catalogue.js, /sitemap.xml and /robots.txt.

`/covers/` and `/social-card.png` are not generated and live in the repository already.

## Notes

- Old hash addresses (`#/book/slug`) redirect to the new pages via `/assets/site.js`. Keep that.
- The `google-site-verification` meta tag is one of two Search Console verifications. Keep it.
- Signup forms post straight to Brevo. There is no API key anywhere, and there must never be one:
  a key committed to a public repository is revoked by Brevo automatically.

## Deliberate oddities, do not "correct" these

- The Leskov title is *Lady Macbeth of the Mzinsk District*. The district is Mtsensk;
  Mzinsk was the translator's choice and is what appears on the printed book. Leave it.
- Walt Ruding's biography no longer mentions the Aubrey Beardsley frontispiece, because
  the Skomlin edition does not reproduce it.
- Ramuz's biography lists his six Skomlin titles on each book page but not on his own
  contributor page, where the introduction and the grid already cover them.
- "Marianna Rychlowska" is a pen name.
