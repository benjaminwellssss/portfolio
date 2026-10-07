# Build Log: Redesign "v2"

## Build 1: test-page build (2026-10-07)

Final state of the redesign while it lived on unlisted test pages (`/home2/`, `/design2/`, `/gallery2/`,
`/about2/`, `/resume2/`, `/dev2/`, `/case2/<post>/`, shared files in `/assets2/`). Git tag: `v2-test-final`
(commit `b1d8520`). Rollback point for the original site: tag `pre-redesign`.

### Pages
- **Home**: hero with logo-cut buttons (Design / Dev / About, Download Resume at the bottom of the stack), stats row,
  services, featured work, closing band. Client-logo carousel under the hero band.
- **Design**: full-width Michigan map with job pins (glow + job name on hover, click opens that post), endless
  scrolling gallery strip underneath, then the case-study cards.
- **Gallery**: every photo with tag filter chips.
- **About / Resume**: restyled to match.
- **Dev**: Steam-store-style project pages: main video or image, a thumbnail row that includes the video
  (click to swap, arrows and slider), text panel locked to the video height with Read more / Show less.
- **Case studies**: one page per post (7 posts), white image backgrounds.

### Design system
- Night ("stealth") theme, greys, pure-white cards and email buttons, bright red (`#E5171F`) accent.
- Logo-cut shapes: rectangles with the top-right and bottom-left corners rounded, used for buttons, cards and tabs.
- Headings and stat numbers: hover "extrude" (face lifts up-left, dark-red layers fill in behind, bright red face
  always on top) plus a quick white sheen sweep.
- Title Case headings everywhere (buttons excluded).
- Carousels and strips always animate, even when the OS asks for reduced motion.

### How it is built
The pages are generated from the site content (`content/posts.json`, `content/gallery.json`) and the original
single-page site by a generator kept outside the repo; a publish script copies the output in. The generated pages
are not meant to be edited by hand.

### Commits since the pre-redesign tag
- `c5a38a3` New design: night theme, logo-cut buttons and cards, services/featured work/closing band on home, full-width map with endless gallery strip, white case-study image backgrounds, heading hover effect
- `c26967f` Map: scale proportionally to fill the panel width (no stretch, no crop)
- `2856ab7` Home sections as full-width bands; map box shorter and cropped at native scale; map heading aligned
- `f51748e` Remove the client logo carousel: restore the home page to how it was before it was added (favicon fix kept)
- `4a1ef35` Add unlisted test pages for the new design: /home2/ /design2/ /gallery2/ /about2/ /resume2/ /dev2/ /case2/<post>/ (existing pages untouched)
- `697f586` Test pages: Design & Signage map at half size (same proportions)
- `71d7b29` Test pages: map zoomed in 1.75x inside the same frame, cropped to it
- `5603c5e` Test pages: map covers the whole panel proportionally (cropped to the frame), heading overlaid
- `a630568` Test pages: version the stylesheet and script links so browsers always load the latest
- `4180921` Test pages: map pins glow on hover, show the job name, and link to that post's page
- `632557c` Test pages: dev page laid out like a store page (main video, text under it, auto-scrolling image strip)
- `da347d4` Test pages: dev strip is half height and sits directly under each main video or image
- `6b0d9a8` Test pages: dev page as Steam-style viewer (main media + thumbnail row with the video, click to swap, arrows and slider, text panel on the right)
- `b0f118d` Test pages: dev text panel locked to the video height with a Read more / Show less toggle
- `7a4aeac` Test pages: remove the Home link and the redundant small label above page titles
- `b1d8520` Test pages: extrude effect keeps the bright red face on top (sheen overlay no longer carries the dark shadow layers)

(The list includes the earlier redesign attempt on the real pages and its revert, kept for history.)
