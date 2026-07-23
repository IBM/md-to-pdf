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
Collect a few bullet points. This becomes the CHANGELOG body (### Added / ### Changed / ### Fixed).

Format the input as valid CHANGELOG markdown before proceeding:
```
### Added
- <bullet 1>
- <bullet 2>

### Changed / Fixed (only if applicable)
- ...
```

Show the formatted version to the user and ask for confirmation before continuing.

## Step 3 — Prepare CHANGELOG

Do NOT open the editor interactively. Instead:

1. Read `CHANGELOG.md` with `read_file`.
2. Read the header (first 6 lines) and the rest (from line 7).
3. Build the new entry:
   ```
   ## [<VERSION>] - <YYYY-MM-DD>

   <formatted description from Step 2>
   ```
4. Prepend it between the header and the rest using `apply_diff` or `write_file`.
5. Show a diff preview and ask: *"CHANGELOG sieht gut aus?"*

## Step 4 — Bump versions

Update `setup.py`, `md_to_pdf/__init__.py`, and `README.md` using `search_and_replace`:
- `setup.py`: `version="<OLD>"` → `version="<NEW>"`
- `__init__.py`: `__version__ = "<OLD>"` → `__version__ = "<NEW>"`
- `README.md`: all occurrences of `md_to_pdf-<OLD>-py3-none-any.whl` → `md_to_pdf-<NEW>-py3-none-any.whl`

## Step 5 — Build wheel

```bash
uv build --wheel --out-dir dist/
```

Confirm the file `dist/md_to_pdf-<VERSION>-py3-none-any.whl` exists.

## Step 6 — Final confirmation

Show a summary:
```
Version:   1.5.0 → 1.6.0
Wheel:     dist/md_to_pdf-1.6.0-py3-none-any.whl
Tag:       1.6.0
Commit:    "Release 1.6.0"
```

Ask: *"Alles klar — soll ich pushen und das GitHub Release erstellen?"*

## Step 7 — Commit, tag, push & GitHub Release

Only after explicit confirmation, run these commands **in order**:

```bash
# 1. Stage all release artefacts — including the wheel
git add setup.py md_to_pdf/__init__.py CHANGELOG.md README.md dist/md_to_pdf-<VERSION>-py3-none-any.whl

# 2. Commit and tag
git commit -m "Release v<VERSION>: <one-line summary>"
git tag v<VERSION>

# 3. Push commit + tag together
git push origin main --tags
```

Then create the GitHub release and attach the wheel as a downloadable asset:

```bash
gh release create v<VERSION> dist/md_to_pdf-<VERSION>-py3-none-any.whl \
  --title "v<VERSION>" \
  --notes "## What's new

<bullet points from CHANGELOG — same content as the ### Added / ### Changed sections>

No breaking changes. Full changelog: [CHANGELOG.md](CHANGELOG.md)"
```

Report the release URL returned by `gh release create` (printed to stdout).
