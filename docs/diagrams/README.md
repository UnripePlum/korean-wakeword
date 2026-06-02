# Architecture Diagrams

This directory stores Mermaid source files and pre-rendered SVGs.

GitHub can render Mermaid blocks directly, but rendering may vary by GitHub's Mermaid version. Architecture docs embed SVG files for stable display and link to the `.mmd` source for review.

Regenerate SVGs:

```sh
for f in docs/diagrams/*.mmd; do
  npx -y @mermaid-js/mermaid-cli -b white -i "$f" -o "${f%.mmd}.svg"
done
```
