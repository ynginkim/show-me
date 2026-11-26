# Contributing to show-me

Before a change, read the README, relevant local guidance, and the current issue. Keep changes focused and preserve the user's files and explicit scope. For a skillset, distinguish mode (routing), playbook (end-to-end flow), skill (reusable work), and principle (decision criteria). Do not turn a suggestion or plan into a claim of completed execution.

## Development and checks

Use Python 3.12 or newer for standard-library checks. The pinned `skills@1.7.4` installer requires Node.js >= 22.20.0; use that version or newer, plus Git, for installation smoke tests. Deck screenshots need Node 18+, a system Chrome and `playwright-core` (`python3 skills/resolve-show-me-tools/scripts/preflight.py --install`); media conversion needs ffmpeg; sheets and comparisons need Pillow and numpy. Do not install these just to edit prose.

From the repository root:

```sh
python3 scripts/check.py .
python3 scripts/selftest.py
python3 scripts/test_tools.py        # add --no-browser when Chrome or playwright-core is unavailable
```

Changes to `skills/resolve-show-me-tools/assets/engine/` must be copied to `examples/sample-deck/slides/engine/` (the `copies` check fails otherwise) and re-checked with `check_deck.py` on the sample deck. If you have the local v2 regression kit (`.work/regress-v2/`, never committed), run it too and report the comparison. Installation smoke tests use a clean clone and a new temporary destination outside the source tree and can require network access. Report commands, results, and anything not run. Structural checks do not prove model behavior, slide legibility on a projector, or license clearance.

## Pull requests

1. Use a separate branch; keep existing user changes intact.
2. Explain the problem, scope, and evidence. Avoid unrelated rewrites.
3. Test the affected contracts, examples, links, and installation resources. Update [CHANGELOG.md](CHANGELOG.md) for user-visible changes.
4. List sources for added code, fonts, samples, and images; do not apply MIT to third-party assets automatically.
5. Never add real client screens, personal recordings, or other onsite-only material to examples, tests, or documentation. Build a neutral sample instead.
6. Check for secrets, local paths, generated output (`qa/`, `node_modules/`), large binary files, and accidental dependency changes.
7. Submit a draft PR with test evidence and remaining limits. Use a short imperative commit subject, such as `docs: clarify local installation`.

Publishing a tag, release, package, or changing repository visibility and permissions is a separate maintainer operation. See [RELEASING.md](RELEASING.md).

## Community

Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). For vulnerabilities use [SECURITY.md](SECURITY.md), not a public bug report. For ordinary questions see [SUPPORT.md](SUPPORT.md).
