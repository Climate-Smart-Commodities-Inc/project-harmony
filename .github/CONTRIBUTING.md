# Contributing to Project Harmony

## The deterministic contract

Our bots follow **published rules only** — every automated behavior is listed here and in
`.github/workflows/`. Nothing guesses, nothing improvises, no AI.

| Bot | Trigger | Action |
|---|---|---|
| Welcome Bot | Your first issue or PR | Posts one welcome comment. Never again. |
| Help Wanted Router | Issue opened with `talent-application` / `stakeholder-intro` | Looks up your exact form selection in a table, adds the matching track/group label, posts the matching next-steps checklist. Unknown value → human routes it by hand. |
| Triage Labels | Issue opened/edited | Adds labels from a fixed keyword table. Never removes labels, never assigns people. |
| Stale Bot | Mondays 9am UTC | Stale after 30 days quiet, close after 14 more. Never touches `pinned`, `security`, or `talent-application`. |
| PR Guard | PR opened/edited/synced | Requires `Closes #NNN` in the PR body. Missing → label + comment. Added later → label clears itself. |
| Label Sync | `labels.yml` changes | Creates/updates labels. Never deletes labels it didn't define. |
| Dependabot | Weekly | Proposes dependency updates. A human merges. |

**Bots never:** merge code, close talent applications, assign work to people, or make decisions.
Anything the rules don't cover waits for a human.

## How to apply as talent

1. Open an issue with the **🙋 Talent Application** form.
2. Pick your role track (Expert / Advisor, Software Builder, Data & GIS, Field Operations, Grants & Research, Design & Docs).
3. The router posts your track's next steps within seconds; a maintainer follows up personally.

## How to open a PR

1. Claim or open an issue first — every PR needs a linked issue (`Closes #NNN`).
2. Fill the PR template checklist.
3. A human reviews every PR. No auto-merges, ever.

## Questions?

Open a **💬 Discussion** (Q&A) — or file a stakeholder intro and we'll route you to the right human.
