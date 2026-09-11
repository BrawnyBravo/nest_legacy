# Fork notes — BrawnyBravo/nest_legacy

Fork of [tronikos/nest_legacy](https://github.com/tronikos/nest_legacy), maintained as a personal fork.
`main` is kept level with upstream automatically by `.github/workflows/sync-upstream.yml`.

**If that sync ever reports a conflict in one of the files below, this page is why.**

## Deliberate divergences from upstream

These are fork-only. They must **never** be included in a pull request back to `tronikos`.

### 1. `hacs.json` — removed `zip_release` and `filename`

Upstream ships:

```json
"zip_release": true,
"filename": "nest_legacy.zip"
```

That tells HACS to install a zip asset attached to a GitHub **Release**, ignoring the branch. It is
correct for upstream, which publishes a release for every version. It is wrong for this fork, which
publishes none — HACS would look for a release that does not exist and the install would simply fail.

Removing those two keys makes HACS install from the **default branch** instead, which is the branch
the daily sync keeps current. So an upstream fix reaches the house automatically, without anyone
remembering to cut a release.

**Consequence, accepted knowingly:** if a release is ever published on this fork, HACS switches back to
release-based installs and silently stops tracking `main`. The sync job keeps reporting success while
delivering nothing. **Do not create Releases here.**

### 2. `custom_components/nest_legacy/manifest.json` — real version instead of `0.0.0`

Upstream keeps `"version": "0.0.0"` in the tree and rewrites it at release time from the git tag
(`.github/workflows/release.yml`). Since this fork installs from the branch, that release step never
runs, and the version Home Assistant displays would be a permanent `0.0.0`.

Set to `0.6.0-house.1`: the upstream release this fork is based on, plus a `-house.N` suffix so HACS
and the Home Assistant UI show it as distinct from upstream's own build.

**When bumping:** raise the base to whatever upstream release `main` now sits on, and reset the suffix
to `.1`. Raise only the suffix for changes made here.

## Resolving a sync conflict in these files

Take **upstream's** version of the file, then re-apply the divergence above. Both are small and
deliberate; neither should ever be "fixed" by accepting upstream wholesale and moving on.

## Why this fork exists

The office remote temperature sensor. Improvement plan and the reasoning behind every item:
`C:\repo\ha-forks\PLAN.md`.
