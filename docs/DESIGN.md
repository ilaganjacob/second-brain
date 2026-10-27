# Design

The Lexington design study's rules, adapted for a dark-only, data-dense dashboard used every day. The study measured marketing sites at 1280px; the changes below are where a dashboard differs.

**The rule behind all of it:** restraint does the work. Type, spacing and one accent color make the page look designed, not decoration or charts.

## Tokens

Starting values. Tune them in the browser in v0.1, then treat them as fixed.

| Token | Value | Use |
| --- | --- | --- |
| `--font` | Switzer, self-hosted (from Fontshare) | Everything |
| `--weight-regular` / `--weight-medium` | 400 / 500 | Never bold. Hierarchy comes from size and gray. |
| `--size-label` | 12px, uppercase, letter-spacing +0.06em | Section labels, column headers |
| `--size-body` | 14px | Body, list rows, inputs |
| `--size-stat` | 28px, weight 500 | Big numbers in a row |
| `--size-title` | 36px, tracking -0.025em | Page title. No 48px hero: this is a tool. |
| `--bg` | `#0E1013` (cool near-black) | Page background |
| `--rule` | `#23262C` | 1px dividers, input borders |
| `--text` | `#E7E9EC` | Primary text and on-goal numbers |
| `--text-2` | `#8A8F98` | Secondary text, units, labels |
| `--accent` | rust, `#D9663B` | Off goal, overdue, due today. Nothing else. |
| `--radius` | 6px | Buttons and inputs only |
| `--space` | 4px base; 8, 12, 16, 24, 32, 48, 64 | Sections are separated by 48–64px plus a rule |

Dark mode only. Define colors only as tokens on `:root`, so a light theme stays possible later.

## Layout

- **12-column grid** on desktop. Each domain is a **report row**: label in columns 1–3, content in 4–12. No boxed cards, no shadows, no gradients.
- Stats inside a row sit side by side, separated by space or a 1px vertical rule, with tabular figures.
- **Phone (< 768px):** a single column, with the label above its content. The capture page shows only the text box, a submit button and "3 waiting in inbox".
- Almost nothing is centered.

## Color rules

- On-goal values are `--text`. Off-goal and due values are `--accent`. A good week is almost colorless, so any color on screen means "act on this".
- Charts (v0.2): every series is `--text-2` except the one highlighted series, which is `--accent` only if it's off goal, otherwise `--text`.

## Components

- **Capture box:** the only big input in the app. Placeholder text shows a real example ("applied to Shopify, frontend dev · $14 lunch · energy 3 mood 4").
- **Inbox:** one row per proposal, showing domain label, parsed fields and a confidence flag in `--accent` if low. Per row: Edit, Reject. **Approve all** is the one solid button in the app, because it's pressed every day. Every other action is a quiet text button or a pale fill.
- **Money:** every dollar figure is blurred by default; the `$` key toggles it. The state stays per-browser.
- **Numbers:** `font-variant-numeric: tabular-nums`. If Switzer lacks tabular figures, numbers get a second face that has them (check in phase 05).

## Copy rules

From the study: exact numbers, plain words, admit limits. Write the copy before styling a screen.

| Don't | Do |
| --- | --- |
| "Great progress!" | "6 of 10 applications this week" |
| "You have upcoming tasks" | "2 follow-ups due Thursday: Shopify, Wave" |
| "No data" | "Nothing logged today. Type what you did above." |
| "Spending looks good" | "$412 of $1,000 · typed only, bank import in v0.3" |

The same rules go into the LLM prompt for the weekly review (v0.4): no "Great job", "Unlock", "Elevate" or "Seamless".

## Later surfaces (v1)

The case study and now page follow the study's marketing patterns more closely: a 48px outcome headline, a timeline that shows the product working (typed 12:14 → parsed → approved 18:02 → counted), and honest limits.
