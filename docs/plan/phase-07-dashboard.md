# Phase 07: Dashboard

**Status:** not started · **Who:** Claude

## Goal
One screen that answers "how am I doing this week?" in exact numbers, styled per DESIGN.md.

## In scope
- Copy first, then build. Report rows, in this order:
  1. **APPLICATIONS:** "6 of 10 this week" (accent if behind pace), pipeline counts by stage, follow-ups due with company, role and date (accent if due today or overdue).
  2. **CHECK-IN:** today's energy, mood and sleep, or "Not checked in today" after 21:00 (in accent); 7-day averages.
  3. **EATING:** prepped vs ate out this week.
  4. **SPENDING:** "$412 of $1,000 this month · typed only", top categories, blurred by default.
  5. **RIDING:** "Strava import arrives in v0.2". An honest placeholder, not a fake number.
  6. **INBOX:** "3 waiting" with a link, shown only if more than zero.
- Accent appears only where a value is off goal or due.
- No charts (no history yet). Charts arrive in v0.2.
- Seed script with a week of fake data, used here and later for the demo.

## Out of scope
Charts, goal editing, deploy.

## Acceptance checks
1. With seed data at 1280px, every row matches the copy rules; no "No data" or cheerleading text.
2. Change seed data so applications are on pace. Their accent disappears, and the accent shows only on items that are actually off goal or due.
3. At 375px, the page reads top to bottom with no horizontal scroll.
4. Dollar figures are blurred on load.
