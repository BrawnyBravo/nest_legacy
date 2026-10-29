# Fork notes: BrawnyBravo/nest_legacy

Fork of [tronikos/nest_legacy](https://github.com/tronikos/nest_legacy).
`main` is kept level with upstream automatically by `.github/workflows/sync-upstream.yml`.

**If that sync ever reports a conflict in one of the files below, this page is why.**

## Why the fork exists

It is a workbench for fixes that go back upstream. Changes are made and tested here, then sent to
`tronikos/nest_legacy` as pull requests from clean branches (see below). The fork is not meant to
diverge from upstream beyond the plumbing listed on this page.

**Home Assistant installs the upstream project, not this fork.** A fix only reaches a running install
once upstream has merged and released it.

Upstream contributions from this fork:

- [#72](https://github.com/tronikos/nest_legacy/pull/72): an option to stop camera event polling.
  Closed; upstream solved the same problem in v0.7.0 (an event poll interval of 0 disables the poll).
- [#73](https://github.com/tronikos/nest_legacy/pull/73): skip cameras disabled in the device registry
  when polling events. Merged 2026-09-13 and released in v0.7.1.

## What it carries that upstream does not

These are fork-only. They must **never** be included in a pull request back to `tronikos`.

### 1. `hacs.json`: removed `zip_release` and `filename`

Upstream ships:

```json
"zip_release": true,
"filename": "nest_legacy.zip"
```

That tells HACS to install a zip asset attached to a GitHub **Release**, ignoring the branch. It is
correct for upstream, which publishes a release for every version. It is wrong for this fork, which
publishes none: HACS would look for a release that does not exist and the install would fail.

Removing those two keys makes the fork installable from its **default branch**, for testing a change
on a real install before it goes upstream.

**Do not create Releases here.** A release switches HACS back to release-based installs, and it would
silently stop tracking `main` while the sync job keeps reporting success.

**One exception exists.** Release `v0.8.0-bb.1` (2026-10-10) was built from the `bb/install` branch,
which carries upstream's `hacs.json` unchanged, to test [#87](https://github.com/tronikos/nest_legacy/pull/87) and
[#88](https://github.com/tronikos/nest_legacy/pull/88) before upstream released them.
While that release exists, an install of this fork gets that release, not `main`. Both changes shipped
upstream in v0.8.1 (2026-10-24), so the release is no longer needed.

### 2. `custom_components/nest_legacy/manifest.json`: real version instead of `0.0.0`

Upstream keeps `"version": "0.0.0"` in the tree and rewrites it at release time from the git tag
(`.github/workflows/release.yml`). A branch install never runs that step, so the version would read
`0.0.0` forever.

The fork sets `<upstream release>-house.<n>`, currently `0.7.1-house.1`. Raise the base to whatever
upstream release `main` now sits on and reset the suffix to `.1`; raise only the suffix for changes
made here.

### 3. `.github/workflows/sync-upstream.yml` and this page

## Syncing: these lines conflict by design

The version line and `hacs.json` are deliberate edits to files upstream also changes, so the daily sync
**will** conflict on them from time to time. That is expected, not a fault, and since 2026-10-29 the
sync job settles it itself by a fixed rule:

- `hacs.json`: upstream's file, minus `zip_release` and `filename`.
- `manifest.json`: upstream's file, with the fork's own `version` string kept.

A conflict in any other file still backs the merge out and opens an issue. The job also refuses to push
if the merged `hacs.json` would carry `zip_release` or `filename`.

## Syncing: workflow files stay the fork's own

The sync job never takes upstream's changes under `.github/workflows/`. Its token has no `workflows`
permission, so GitHub refuses any push whose commits change a workflow file. The job puts every
workflow file back to the fork's copy before committing the merge (files upstream adds are dropped,
files it changes or deletes are restored) and refuses to push if the merge would still change one. To
adopt an upstream workflow change, copy it across by hand in a pull request.

## Sending a change upstream

`main` carries fork-only files. A pull request branched from `main` would drag them into someone else's
project, so an upstream-bound change gets its own branch off **`upstream/main`**, carrying only the
files the change touches. Verify with:

```sh
git diff --name-only upstream/main <branch> | grep -E "sync-upstream|FORK-NOTES|hacs.json|manifest.json"
```

That should print nothing. If it prints anything, the branch is not ready to be a pull request.
