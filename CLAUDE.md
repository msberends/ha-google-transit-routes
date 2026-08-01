# ha-google-transit-routes

## Quality bar

This project is intended for public release (HACS) and should be maintained
to the standard of a codebase an experienced HA-integration team has
carefully tended for years — not a one-off script. Concretely:

- Match idiomatic, current Home Assistant Core patterns, not just "whatever
  runs." When implementing a non-trivial HA mechanism (config flow features,
  entity platforms, coordinators, subentries, etc.), check how real Core
  integrations do it first (grep/fetch `home-assistant/core` source) rather
  than guessing at an API shape.
- Keep `README.md`, `strings.json`, and both `translations/*.json` files
  (`en`, `nl`) in sync with the code whenever user-facing behavior changes —
  stale docs/translations are a defect, not a follow-up task.
- Preserve backward compatibility for existing users on upgrade (entity IDs,
  unique IDs, automations/dashboards referencing existing entities) unless a
  breaking change is explicitly agreed with the user; when a migration is
  needed, use Home Assistant's proper config-entry-version migration
  mechanism (`async_migrate_entry`), not ad hoc one-off checks.
- Every change ships with passing tests (`tests/`) and updated docs in the
  same change — not as a "later" item. See "Running tests" below.
- No dead code, no half-finished abstractions, no copy-pasted boilerplate
  left over from a pattern that got replaced.

## Live Home Assistant instance — DO NOT WRITE

`/var/www/homeassistant` is the user's **live, production** Home Assistant
installation (running in Docker, container name `homeassistant`). It is
useful for read-only diagnosis (checking logs with `docker logs
homeassistant`, inspecting `config/.storage/*` for entity/config-entry
state), but:

- **Never edit, copy into, or delete files under `/var/www/homeassistant`.**
- Never call services/actions against the live instance (e.g. via its REST
  API or `docker exec`) unless the user explicitly asks for that specific
  action.
- Treat anything found there as read-only evidence for debugging, not as a
  place to make changes or run experiments.

## Releases

**Never commit, push, or release on your own initiative.** After finishing a
fix, stop and ask the user whether they want it committed/pushed/released —
do not treat "the fix works" as a trigger to start the git sequence.
Implementing a change and shipping it are separate decisions; only the user
makes the second one. Do the sequence unprompted only when the user's
current message is itself the request (e.g. "commit and push", "push this",
"cut a release").

When the user does ask for it, every `git push` to `main` must be paired
with a GitHub release, no exceptions — including docs-only changes (e.g. to
this file). HACS tracks this repo by release, not by commit, and an
unreleased push left HACS trying (and failing) to download a commit-SHA
archive URL instead of a proper release zipball. Concretely, do the full
sequence yourself every time:

1. Bump `"version"` in `manifest.json` (and `card/package.json`'s
   `"version"` if the card changed) — semver, matching the size of the
   change.
2. Commit, then push to `main`.
3. Tag the pushed commit with the new version number (no `v` prefix — the
   tag must match `manifest.json`'s `version` string exactly, since that's
   what HACS compares) and push the tag.
4. Create a GitHub release from that tag (`gh release create`) with a short
   summary of what changed.

## Running tests

Use the venv at `.venv` in this repo (gitignored, persists across
sessions — do NOT use `/tmp/...` scratchpad paths for this, those are
wiped per-session):

```bash
source .venv/bin/activate
python -m pytest tests -q
```

If `.venv` doesn't exist yet (or needs rebuilding), create it with **Python
3.13+**, not the system `python3` (3.12):

```bash
uv venv --python 3.13 .venv   # uv already has 3.13 cached locally, no apt/system changes needed
source .venv/bin/activate
uv pip install -r requirements_test.txt
```

Why 3.13, not system Python: `pytest-homeassistant-custom-component` stopped
publishing wheels for Python 3.12 after version `0.13.205`, which pins
`homeassistant==2025.1.4` — a version that **predates config subentries**
(`homeassistant.config_entries.ConfigSubentry` doesn't exist in it). This
integration's config flow uses subentries (see the "Saved routes as
subentries" section below), so testing it requires a modern `homeassistant`,
which requires Python 3.13+. Verified: on Python 3.13 with
`homeassistant==2026.2.3` / `pytest-homeassistant-custom-component==0.13.316`,
the full suite passes cleanly and repeatably (35 passed, 0 errors, 3
consecutive runs) with no extra workarounds — the previous note in this file
about uninstalling `aiodns`/`pycares` was specific to the old Python
3.12/homeassistant 2025.1.4 combination and does not apply here; on the
current combination `aiodns`/`pycares` are required (a fixture in the newer
test harness needs `AsyncResolver`, which needs `aiodns`).

## Saved routes as subentries

Each saved route is a **config subentry** (`homeassistant.config_entries.
ConfigSubentry`) of the integration's single config entry, not a plain list
in `entry.options`. This is why: it's what makes each route render as its
own block/device on the integration's page, with its own add/reconfigure/
remove UI, instead of being buried behind one shared "gear icon" options
menu. Requires `minimum_ha_version: "2025.7"` in `manifest.json` — that's
when Home Assistant Core shipped the polished subentries UI (backend API
landed earlier, in ~2025.1, but wasn't a good end-user experience until
2025.7).

When editing `config_flow.py`, mirror the pattern used by real Home
Assistant Core integrations that already ship subentries (e.g. `ntfy`,
`openai_conversation`) rather than inventing a bespoke shape — fetch their
source from `home-assistant/core` on GitHub as a reference before writing
subentry flow code.
