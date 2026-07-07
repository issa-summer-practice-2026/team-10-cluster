# Collaboration workflow

This is the day-to-day rhythm of the week — and the actual skill you're
practising. The code changes are tiny on purpose; the **issue → branch → PR →
review → green CI → merge** loop is the point.

> Golden rule: **`main` only changes through a reviewed, green pull request.**
> You never push to `main`, and you don't merge your own PR.

## The loop, once

1. **Open an issue.** Pick an item from [backlog/](backlog/). Create a GitHub
   Issue — each backlog file gives you ready-to-paste **Title** and
   **Description**. Note the number GitHub assigns (e.g. `#7`).
2. **Branch.** One change per branch, named `type/kebab-case`:
   ```bash
   git switch -c feat/oil-telltale
   ```
3. **Make the change.** Apply the exact code + test from the backlog item.
   Commit in small, imperative steps:
   ```bash
   git commit -am "feat: add oil-pressure telltale"
   ```
4. **Check locally before pushing:**
   ```bash
   python scripts/dev.py test
   python scripts/dev.py lint
   ```
5. **Open a PR.** Push and open a pull request into `main`. Paste the backlog
   item's **PR** text and keep the **`Closes #<n>`** line (replace `<n>` with your
   issue number) so merging auto-closes the issue:
   ```bash
   git push -u origin feat/oil-telltale
   ```
6. **Review.** Your teammate does a **real** review — comments, request changes,
   then approve. (You can't approve or merge your own PR.)
7. **Merge on green.** When CI is green **and** the PR is approved, **Squash and
   merge**. The issue closes itself; the PR title becomes a release note on
   Thursday.

*(CLI equivalent, optional):* `gh issue create`, `gh pr create --fill`,
`gh pr merge --squash`.

## Naming (it isn't cosmetic — it becomes your release notes)

**Branches** — one change each, kebab-case, type-prefixed:

```
feat/oil-telltale
fix/redline-threshold
docs/readme-badge
```

**Commits** — imperative, ~50-char subject; the *why* in the body; keep them
small:

```
feat: add oil-pressure lamp
fix: correct redline zone
test: cover overheat rule
```

**Pull requests** — a descriptive title reads like a release note; the body says
*what & why* and links the issue:

```
Title:  feat: oil-pressure telltale
Body:   ...what and why...
        Closes #12
```

Good PR titles + labels → Thursday's release notes write themselves.

## "Red can't merge"

CI is the safety net. A red check **blocks** the merge — that's the whole point.
Some backlog items are designed to go red if applied incompletely (each notes
*"Goes red if…"*). When a check is red: **read the run log**, fix the change,
push again, and watch it go green. Never bypass the gate.

## How you verify a change actually worked

- `python scripts/dev.py test` — the tests pass (locally, in CI, and later inside
  the image).
- Open the **cluster + simulator** — you can *see* the change on screen.
- `GET /api/state` — the JSON reflects your change.
- `GET /health` — the app still boots. `GET /version` — which build is running.

## Participation (tracked, not graded)

- Author **≥ 3** merged PRs; review **≥ 3** of your teammate's.
- You **can't** merge your own PR.
- Keep PRs **small** — one backlog item each.

Ready? Start with [backlog/](backlog/) — the first two items are backend-only
warm-ups whose lamps are already on screen.
