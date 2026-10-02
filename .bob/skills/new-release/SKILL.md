---
name: new-release
description: >
  Use when the user wants to create a new release for this project. Triggers on
  "/new-release", "new release", "release erstellen", "neue Version", "neues Release".
  Suggests the next version number, collects a description, then runs release.sh.
metadata:
  argument-hint: "[version]"
---

# New Release Workflow

## Step 1 — Propose version

Run:
```
git tag --sort=-v:refname | head -1
```
Extract the latest tag and suggest the next **patch** version (default) or ask the user if they
want minor/major. Present the suggestion clearly:

> Current: `1.5.0` → Proposed: **`1.6.0`** (patch)
> Change to minor (`2.0.0`) or major (`1.6.0`)? Or just confirm.

If the user passed a version argument directly (e.g. `/new-release 1.6.0`), skip this step.

## Step 2 — Collect the release description

Ask the user: *"What's new in this release?"*
Collect a few bullet points. This becomes the CHANGELOG body (### Added / ### Improved / ### Fixed).

Format the input as valid CHANGELOG markdown before proceeding:
```
### Added
- <bullet 1>
- <bullet 2>

### Improved / Fixed (only if applicable)
- ...
```

Show the formatted version to the user and ask for confirmation before continuing.

## Step 3 — Prepare CHANGELOG

Do NOT open the editor interactively. Instead:

1. Read `CHANGELOG.md` with `read_file`.
2. Read the header (first 6 lines) and the rest (from line 7).
3. Get today's date first: run `date +%Y-%m-%d` — do NOT hardcode or guess it.
4. Build the new entry:
   ```
   ## [<VERSION>] - <YYYY-MM-DD>

   <formatted description from Step 2>
   ```
5. Prepend it between the header and the rest using `apply_diff` or `write_file`.
6. Show a diff preview and ask: *"CHANGELOG sieht gut aus?"*

## Step 4 — Bump versions

Update `setup.py`, `md_to_pdf/__init__.py`, and `README.md` using `search_and_replace`:
- `setup.py`: `version="<OLD>"` → `version="<NEW>"`
- `__init__.py`: `__version__ = "<OLD>"` → `__version__ = "<NEW>"`
- `README.md`: all occurrences of `md_to_pdf-<OLD>-py3-none-any.whl` → `md_to_pdf-<NEW>-py3-none-any.whl`

## Step 5 — Final confirmation

Show a summary:
```
Version:   1.5.0 → 1.6.0
Tag:       v1.6.0
Commit:    "Release v1.6.0"
```

Ask: *"Alles klar — soll ich committen, taggen und pushen?"*

## Step 6 — Commit, tag, push

Only after explicit confirmation, run these commands **in order**:

```bash
# 1. Stage release files
git add setup.py md_to_pdf/__init__.py CHANGELOG.md README.md

# 2. Commit and tag
git commit -m "Release v<VERSION>: <one-line summary>"
git tag v<VERSION>

# 3. If on a feature/release branch, merge to main first
git checkout main
git merge <branch> --ff-only

# 4. Push commit + tag — triggers GitHub Actions (builds wheel + creates GitHub Release)
git push origin main --tags
```

Report that GitHub Actions will automatically build the wheel and create the GitHub Release.
