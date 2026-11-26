# Version and release policy

`VERSION` is the repository version source. A version string alone does not publish a Git tag or release. Do not interpret a document or a draft PR as a published release.

Use `vMAJOR.MINOR.PATCH` tags. Before 1.0, a breaking contract change increments MINOR; compatible additions increment MINOR and compatible fixes increment PATCH. Breaking changes include renamed/removed skills or playbooks, changed input/output formats, installation paths, required resources, command/file contracts, and breaking changes to the deck engine API (slide attributes, the `showme-config` block, component markup, `ShowMe` functions).

The engine carries its own version in the header of `skills/resolve-show-me-tools/assets/engine/show-me.js`. Every deck keeps the engine copy it was made with, so an engine release never changes existing decks until the user asks for `new_deck.py --update-engine`. Bump the engine version whenever its behaviour or markup changes, and record the regression result in the changelog. Document migrations explicitly.

## Release checklist

- [ ] Review and merge the approved implementation; rerun checks on the exact release commit.
- [ ] Check source notices, bundled resources, secrets, and third-party redistribution terms.
- [ ] Verify clean installation at the intended ref and record runtime/tool versions.
- [ ] Run the sample deck check and, when available, the local v2 engine regression on the exact commit.
- [ ] Verify the Lightplay file contract at exact commit SHAs when it changed.
- [ ] Change VERSION to the release number and move Unreleased entries to a dated changelog section.
- [ ] Review release notes and obtain maintainer approval to publish.
- [ ] Create the tag and GitHub release at the verified commit; do not move published tags.
- [ ] Reinstall using the published tag and record the result.

Publish any required third-party license attachments alongside redistributed resources. Independently versioned integrations keep their own release lifecycle.

## Reproducible installation

The pinned [`skills@1.7.4` installer](https://github.com/vercel-labs/skills/blob/v1.7.4/package.json) requires Node.js >= 22.20.0. This does not replace the runtime requirements of the deck tools (Chrome, playwright-core, ffmpeg).

The skills installer parses a quoted `owner/repo#REF` as a Git ref. `@name` selects a skill, not a version. Use a published tag or full 40-character commit SHA; do not advertise a tag before it exists. Pin the installer itself, for example `npx skills@1.7.4 add 'owner/repo#FULL_COMMIT_SHA'`, replacing the source with the verified repository and SHA.

The `1.7.4` parser and clone behavior were reviewed in [source-parser.ts](https://github.com/vercel-labs/skills/blob/v1.7.4/src/source-parser.ts) and [git.ts](https://github.com/vercel-labs/skills/blob/v1.7.4/src/git.ts). Private repositories still require existing Git access; do not create or paste access tokens into commands, documents, or issues.
