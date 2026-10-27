# Phase 05: Design system and shell

**Status:** not started · **Who:** Claude

## Goal
The visual system from DESIGN.md exists as tokens and a page shell, before any real screen is built.

## In scope
- Switzer 400/500 self-hosted in `web/public/fonts` (Fontshare license allows this). Check for tabular figures; if missing, add a numeric face and record why.
- `tokens.css` with every token from DESIGN.md on `:root`. No color appears anywhere else.
- Base styles: body 14px, label class, stat class, title class, 1px rules, 12-column grid, report-row layout, phone breakpoint at 768px.
- App shell: top bar with "Second Brain", navigation (Dashboard, Inbox, Capture), and the money blur toggled by the `$` key.
- A `/styleguide` route showing every token and component state, for checking the design quickly.
- Plain CSS modules. No Tailwind or component library, so every style is a deliberate choice.

## Out of scope
Real data, capture and inbox behavior.

## Acceptance checks
1. `/styleguide` at 1280px: one font, no bold, no shadows or gradients, accent visible only in its "off goal" example.
2. The same page at phone width (375px) has no horizontal scroll, and labels stack above content.
3. Pressing `$` blurs and unblurs the sample dollar figures, and the setting survives a reload.
4. A column of numbers (`1,000`, `412`, `14`) lines up on the right edge.
