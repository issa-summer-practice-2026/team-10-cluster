# Conflict & revert drill

> Git practice, not app code. New here? Read [../workflow.md](../workflow.md).

**Goal:** deliberately create a merge conflict and resolve it; then revert a
merged change — and watch CI stay green throughout.

**Why:** conflicts and mistakes are normal. A conflict just means two branches
touched the **same lines**; resolving it calmly is the skill, and the size of the
edit doesn't matter. Reverting cleanly is the "oh no" recovery you'll rely on.

Do this as a **pair** — you need two branches from two people.

## Part A — create and resolve a conflict

You'll both edit the **same line** of `CHANGELOG.md` (under `## [Unreleased]`).

1. **Person A** — branch, add a line under *Unreleased*, PR it, and **merge** it:
   ```bash
   git switch -c chore/changelog-a
   # under "## [Unreleased]" add:  - Note from A
   git commit -am "docs: changelog note from A"
   git push -u origin chore/changelog-a   # open PR, review, merge
   ```
2. **Person B** — from `main` *before* A merged (or without pulling A), edit the
   **same line** differently and open a PR:
   ```bash
   git switch -c chore/changelog-b
   # under "## [Unreleased]" add:  - Note from B
   git commit -am "docs: changelog note from B"
   git push -u origin chore/changelog-b   # open PR
   ```
3. B's PR now **conflicts** with `main`. Resolve it by updating the branch and
   **keeping both** lines:
   ```bash
   git switch chore/changelog-b
   git fetch origin && git merge origin/main   # conflict in CHANGELOG.md
   # edit the file: keep BOTH "- Note from A" and "- Note from B",
   # delete the <<<<<<< ======= >>>>>>> markers
   git commit -am "docs: resolve changelog conflict (keep both notes)"
   git push
   ```
4. CI goes green on the resolved PR → review → **merge**.

**Done when:** the conflict was resolved via a PR, both notes survived, and the
merge was green.

## Part B — revert a merged change

Reverting makes a **new commit** that undoes a merged one — it doesn't rewrite
history, so it's safe and reviewable.

1. Pick a merged PR (e.g. one of the changelog notes above, or a telltale
   exercise). Find its merge commit on `main`.
2. On a fresh branch, revert it and open a PR:
   ```bash
   git switch -c revert/changelog-a
   git revert <merge-or-commit-sha>     # for a squash-merge, revert the squashed commit
   git push -u origin revert/changelog-a   # open PR
   ```
3. Review → CI green → **merge** the revert.

**Done when:** a revert PR merged and **the pipeline stayed green** the whole
time.

*Stretch:* practise bringing an out-of-date branch up to date two ways — `git
merge origin/main` vs `git rebase origin/main` — and note how the history differs.
