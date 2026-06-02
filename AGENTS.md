# Agent Instructions

## Architecture Diagrams

Do not rely on GitHub's inline Mermaid renderer for architecture documents.

When adding or changing architecture diagrams:

- Store Mermaid source files in `docs/diagrams/*.mmd`.
- Render SVG files from the Mermaid source and commit both `.mmd` and `.svg`.
- Embed SVG files in Markdown with `![Diagram title](diagrams/name.svg)`.
- Add a source link immediately below each image, for example `Source: [name.mmd](diagrams/name.mmd)`.
- Do not put direct fenced `mermaid` blocks in `docs/ARCHITECTURE.md`.
- Avoid Mermaid labels that contain raw HTML, `<br/>`, angle-bracket placeholders, or very long text.
- Keep diagram labels short and stable. Put detailed explanation in the surrounding Markdown.

Regenerate SVGs from a repo root:

```sh
for f in docs/diagrams/*.mmd; do
  npx -y @mermaid-js/mermaid-cli -b white -i "$f" -o "${f%.mmd}.svg"
done
```

Before committing diagram changes, verify:

```sh
git diff --check
rg -n '```mermaid' docs/ARCHITECTURE.md
```

The `rg` command should return no matches for `docs/ARCHITECTURE.md`.
