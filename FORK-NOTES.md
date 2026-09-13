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
  when polling events. Open.

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

### 2. `custom_components/nest_legacy/manifest.json`: real version instead of `0.0.0`

Upstream keeps `"version": "0.0.0"` in the tree and rewrites it at release time from the git tag
(`.github/workflows/release.yml`). A branch install never runs that step, so the version would read
`0.0.0` forever.

The fork sets `<upstream release>-house.<n>`, currently `0.7.0-house.1`. Raise the base to whatever
upstream release `main` now sits on and reset the suffix to `.1`; raise only the suffix for changes
made here.

### 3. `.github/workflows/sync-upstream.yml` and this page

## Syncing: these lines conflict by design

The version line and `hacs.json` are deliberate edits to files upstream also changes, so the daily sync
**will** conflict on them from time to time. That is expected, not a fault. Take **upstream's** version
of the file, then re-apply the divergence above. Neither should ever be "fixed" by accepting upstream
wholesale, and a conflict is always resolved, never left for the fork to drift.

## Sending a change upstream

`main` carries fork-only files. A pull request branched from `main` would drag them into someone else's
project, so an upstream-bound change gets its own branch off **`upstream/main`**, carrying only the
files the change touches. Verify with:

```sh
git diff --name-only upstream/main <branch> | grep -E "sync-upstream|FORK-NOTES|hacs.json|manifest.json"
```

That should print nothing. If it prints anything, the branch is not ready to be a pull request.
