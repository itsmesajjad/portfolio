# Sajjad — Portfolio

A one-page, premium portfolio for **Md. Sajjad Hossain Chowdhury** — graphic & motion designer,
3D modeler and video editor in Dhaka, Bangladesh.

Monochrome, editorial, fully responsive, with a live window into the Behance profile.

---

## Run it

```bash
python server.py
```

That starts a zero-dependency Python server at <http://127.0.0.1:8000> and opens your browser.

Options:

```bash
python server.py --port 5500      # different port
python server.py --no-open        # don't launch a browser
python server.py --host 0.0.0.0   # expose on your LAN (phone/tablet testing)
```

You can also just double-click `index.html`. Everything works offline except the
live Behance stats, which gracefully fall back to the last snapshot.

---

## Files

```
.
├── index.html          ← the whole site (HTML + CSS + JS inline)
├── server.py           ← dev server + /api/profile (live Behance data)
├── assets/
│   ├── cover.webp      ← borderless hero cutout
│   ├── about.webp      ← About portrait
│   ├── profile.jpg     ← small avatar used in the Behance mirror
│   └── work-01…06.webp ← project covers
└── README.md
```

---

## Make it yours

**1. Contact details** — inside `index.html`, find `CONFIG` near the top of the
`<script>` block:

```js
var CONFIG = {
  email: 'sajjad.jhc@gmail.com',
  whatsapp: '8801685455482', // country code, digits only
  linkedin: 'https://www.linkedin.com/in/i-am-sajjad',
  behance: 'https://www.behance.net/sajjadhossain31'
};
```

- The WhatsApp button becomes a real `wa.me` link and displays `+8801685455482`.
- The email updates the about list, the mobile menu note and the Gmail button.

**2. Imagery** — `assets/cover.webp` is the borderless hero cutout and
`assets/about.webp` is the About portrait. Both are grayscale-treated in CSS, sit
without a frame in the hero, and reveal with a scale/blur pop as they enter view.
Replace either file with an optimised WebP at the same aspect ratio.

**3. Experience copy** — edit the five `.exp-item` blocks in the Experience
section. The list starts with the current Senior Graphic Designer role at ESG
Institute Bangladesh, followed by Spade Digital, Adexy Communication, CSR Window
and independent work.

**4. Projects** — the "02 — My Works" section holds six `.shot` cards linking to
real Behance galleries. Swap the `href`, cover image and title/category labels, or
add more cards (the grid is 3-up on desktop, 2-up on mobile). The header pairs the
Behance button with a Pinterest follow link; both live in `.sec-actions`.

**5. Software proficiency** — the five `.software-item` entries below the Behance
mirror crawl continuously, each with an inline Simple Icons glyph from the
`.software-sprite` symbol set. To change the list, edit the items in all three
`.software-group` blocks (they must stay identical for the seamless loop) and add
or swap a `<symbol>` if the icon changes.

**6. Live stats** — `server.py` scrapes the public profile once every 10 minutes
and exposes:

```
GET /api/profile
```

The page reads it and updates the views / appreciations / follower counts plus the
"Synced live" timestamp. Behance sends `X-Frame-Options: SAMEORIGIN`, so a true
iframe embed is blocked by the browser — the showcase is a live-data mirror of the
profile instead, with every card and CTA opening the real page.

---

## Design notes

- **Palette:** only shades of gray (near-black `#0a0a0a` → warm off-white `#f2f2ee`),
  with a soft green "available" dot as the single signal colour.
- **Type:** Instrument Serif (display), Manrope (body), JetBrains Mono (labels).
- **Motion:** preloader counter, masked headline reveal, pop-up text and image
  reveals that replay when a navigation link is clicked, count-ups, magnetic
  buttons, custom cursor, hero cover float and parallax, hover sweeps, plus two
  continuous crawls: the discipline marquee and the software strip. With
  `prefers-reduced-motion`, reveals become plain opacity fades and the pointer,
  float and parallax effects stop; both crawls keep running as requested.
- **Light / dark:** toggle in the header, remembered in `localStorage`.
- **Responsive:**
  - Laptop ≥ 1200 px — two-column hero, sticky About portrait, 3-up project preview.
  - Tablet 721–1200 px — stacked hero, 2-up/4-up adaptations, condensed experience rows.
  - Mobile ≤ 720 px — full-width actions, 2-up preview grid, three About stats,
    single-column contact, full-screen menu.

---

## Accessibility

Skip link, visible focus rings, semantic headings, labelled controls, `aria` states on
the menu and theme toggle, alt text on imagery, and reduced-motion support.

All artwork © Md. Sajjad Hossain Chowdhury.
