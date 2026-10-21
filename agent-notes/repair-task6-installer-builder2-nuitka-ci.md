# Installer Builder 2 PR #3: offline Nuitka argument coverage

## Goal

Repair the feature's stale directory assertion and wire safe full unit/package checks. Preserve formatter and deployment behavior; no real freezer/compiler/Inno Setup/DMG/signer/release invocation.

## State

- Same-org origin git@github.com:accessibleapps/installer_builder2.git. Fresh master ef093977cb30ab4dba7be03fbe108de8563f0054, published PR #3 new-nuitka head 6f48f0658170207857349fd655d848d312144f89. Original preserved at backup/task6-installer-builder2-3-published-before-repair; no original local feature branch existed. Canonical master clean and untouched.
- New isolated worktree installer-builder2-nuitka-ci / repair/task6-installer-builder2-nuitka-ci directly derives from that PR. Source feature is the full original 119-added/9-deleted diff; default lacks formatter/tests/deployment flag, so this assertion defect belongs to feature, not a fake baseline prerequisite.
- Actions enabled; no hosted run exists for proposed local head. No publication, model call, settings, hook, release or old-description changes.

## Decisions and why

- Original five unittest methods lived inside production module and were not discoverable by normal test discovery. Move all five intact into test_installer_builder2.py, correcting only the directory expectation. Real compile_distribution sends data_directories via --include-data-dir; Nuitka's primary manual documents recursive source=target, not the test's extra =**/* (that is a separate --include-data-files form).
- Add two exact mocked-subprocess tests: builder forwards files/patterns/explicit mapping/directory/deployment; default run leaves deployment off. No test can call the real subprocess boundary in these cases. Preserve production formatter/argv behavior.
- CI runs all seven tests on Windows/macOS Python 3.13 because these are the README's actual target platforms and os.path is exercised. Only attrs is imported by offline source; install pinned attrs26.1.0 in isolated --no-project environment. Build actual setuptools wheel/sdist without resolving/invoking application toolchain.
- pyproject has no requires-python, README says >=3.6, while current downstream innosetup_builder declares >=3.8.6. This task does not invent/drop support metadata or claim historical-floor graph coverage. Real frozen-app/toolchain validation remains outside safe test scope.
- Ordinary PR/master events, read-only contents, verified pinned actions, no persisted credentials/cache, bounded timeout/concurrency; no release workflow.
- Primary sources: https://nuitka.net/user-documentation/user-manual.html#data-files and https://nuitka.net/user-documentation/common-issue-solutions.html#deployment-mode. Deployment disables runtime helpers; no compatibility benefit is inferred.

## Verification

- Before assertion correction, actively authored relocated test file on CPython3.13 / attrs26.1.0: 5 tests ran, 4 passed, one failed at directory expected =testdir/=**/* versus actual =testdir/. No compiler/service calls. This is actual red, not an execution of full CI.
- After assertion correction and exact command/deployment regressions, the same actively authored file: 7 tests passed in 0.002s on CPython 3.13 with attrs26.1.0. The real subprocess boundary was mocked. Full hosted unit/build gate pending; no local full CI/build.
- actionlint1.7.12 (optional shellcheck/pyflakes disabled) and zizmor1.31.1 --offline --pedantic passed, exit0, no findings. Manifest unchanged.

## Next step

Return complete local diff/head and exact safe regression/audit result before publication. Actual final-head hosted green and Claude review remain separate coordinator gates.
