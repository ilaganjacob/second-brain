# Second Brain: spec answers (round 3)

Same as before: write `ok` to accept, or write your own answer after `A:`. Save, then tell me.

---

## Decided

**Product**

- Capture page usable on your phone, plus the desktop dashboard. Lives at `brain.jacobilagan.com`.
- Everything you log goes to an inbox as "pending"; you approve it; charts count approved items only.
- Workouts come from Strava only. Typed spending is temporary until the bank import replaces it.
- "$14 lunch" becomes a spending entry plus an ate-out entry. Unclear messages are saved as notes and flagged.
- Job applications store company **and** job title. Follow-ups auto-set: applied +7 days, screen/interview +3 days.
- Goals: riding 8 h/week, spending $1,000/month (CAD), 10 job applications/week. LeetCode goal dropped.
- Check-in reminder: phone reminder at 9:00 (no code).
- Bank: Wealthsimple, CAD only. Merchant list first, AI only for unknown merchants.
- Roadmap: the six phases from round 2 (v0.1 → v1+). _(You left A blank, so I took it as ok.)_

**Tech**

- Website on Cloudflare Pages, Python (FastAPI) backend on Fly.io, SQLite with automatic backups.
- Login via Cloudflare Access (email code). No login code of our own.
- AI through **OpenRouter**, pinned to one model that supports structured output (the JSON-shape guarantee the parser relies on). Note: your text passes through OpenRouter _and_ the model company, so I'll turn on OpenRouter's "no data retention" provider filter.
- Repo at `~/second-brain`, public on GitHub. Real data never goes in the repo. _(You didn't say public/private, so I assumed public. Say so if not.)_

**Day 1 build (your "beautiful dashboard" answer)**
A dashboard looks good because of type, spacing and restraint (the Lexington study's main point), not because of charts. So day 1 is:

- capture box → AI parse → inbox → dashboard, deployed behind login;
- the full design system below applied from the start;
- the dashboard shows exact numbers against goals ("6 of 10 applications this week", "2 follow-ups due Thursday").

Line charts wait for v0.2: on day 1 there's no history to plot, and an empty chart looks worse than a clean number.

---

## Design notes: Lexington rules adapted for a dashboard

The study measured marketing sites at 1280px. A dashboard is denser and used daily, so here's what carries over and what changes.

| Rule from the study                                        | In the dashboard                                                                                                                                                                                                                  |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| One family, weights 400/500                                | Same. Hierarchy from size and gray, never bold.                                                                                                                                                                                   |
| Headings tracked about -0.025em                            | Same, on page title and section headings only. Numbers stay at normal spacing.                                                                                                                                                    |
| Body 14, labels 12 uppercase, H2 36, H1 48                 | Body 14, labels 12, **stat numbers 28**, page title 36. No 48px H1: it's a tool, not a hero page.                                                                                                                                 |
| Off-white tinted background, near-black text, one mid gray | Same. Cool tint. A second, lighter gray only for rules/borders.                                                                                                                                                                   |
| Accent on fewer than 5 elements                            | Accent means **"off goal" or "due"**, nothing else. On-goal numbers stay ink. A healthy week has almost no color, so color = something to act on.                                                                                 |
| 12-col grid, labels in cols 1–3, content in 4–12           | Dashboard reads like a **report**, not a grid of boxes: each domain is a row with its label on the left and numbers on the right.                                                                                                 |
| No shadows, gradients or boxed cards; 1px rules            | Same. Stat "tiles" are numbers separated by rules, not cards.                                                                                                                                                                     |
| Radius 6px on buttons only                                 | Buttons and inputs (capture box, inbox edit fields).                                                                                                                                                                              |
| Quiet CTAs                                                 | Mostly. Exception: **Approve all** in the inbox is the most-used button in the app, so it gets the one solid fill.                                                                                                                |
| Small uppercase section labels                             | Yes: APPLICATIONS, CHECK-IN, EATING, SPENDING.                                                                                                                                                                                    |
| Show the product working                                   | For the v1 case study: a real timeline of one capture (typed 12:14 → parsed → approved 18:02 → counted).                                                                                                                          |
| Copy: exact numbers, plain words, admit limits             | All in-app text: "3 of 10 this week", not "Keep going!". Empty states say what to do: "Nothing logged today. Type what you did above." The v0.4 weekly AI review gets the same rules in its prompt (no "Great job", no "Unlock"). |

**Gaps the study didn't cover (my defaults):**

- **Phone width.** The study only checked desktop. Below 768px the 12-col grid collapses to one column, labels sit above content, and the capture page is just the text box and the inbox count.
- **Tabular numbers.** Columns of numbers must align. I'll check that Switzer has tabular figures; if it doesn't, numbers use a second face that does.
- **Money privacy.** Dollar figures are blurred by default; one key (`$`) reveals them.
- **Fonts.** Fontshare fonts are free for commercial use. We'll host the font files with the app instead of loading them from Fontshare.
- **Copy first.** Following the study's verdict, I'll write the dashboard labels and empty-state text before styling anything.

---

## Questions

**1. Accent color.** It appears only on things that need action. Pick one:

- rust/orange (Mulberry: warm against the cool background, reads as "attention" without screaming error) — _my pick_
- blue (Navy)
- your own color

A: rust

**2. Typeface.** Switzer (used by 3 of the 5 themes) or General Sans (Duckbutt, slightly warmer)?
Default: Switzer.
A: switzer

**3. Dark mode.** Default: both from day 1, following your system setting. Once the colors are defined as tokens it's mostly a second set of values.
A: yes always dark

**4. Section label style.** Plain `APPLICATIONS` or Navy-style `/// APPLICATIONS`?
Default: plain.
A: plain

**5. Riding goal timing.** Your 8 h/week goal shows nothing until the Strava import exists (currently v0.3). Move the Strava import up to v0.2? It's roughly a 2–3 hour job.
Default: yes, move it to v0.2.
A:ok

**6. 9:00 check-in.** A morning check-in rates **last night's sleep** and **yesterday's** energy and mood. Is that what you want, or would you rather rate today at 21:00?
Default: 9:00, rating yesterday.
A: sorry yeah i misunderstood. lets do the rate of the day the same day at 21:00

**7. Wealthsimple sample.** Not needed until v0.3. When you get there, export one month's CSV and replace the amounts and merchant names with fake ones, so I can match the format. Ok?
A:ok
z

---

Anything else:
A:
