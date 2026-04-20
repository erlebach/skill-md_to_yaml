# Allowed `layout` values (IR)

Authoritative schema: [`deck-compile/schema/models.py`](../../deck-compile/schema/models.py) and generated [`deck-compile/schema/deck.schema.json`](../../deck-compile/schema/deck.schema.json).

| Layout | Typical use |
|--------|-------------|
| `title` | Opening slide |
| `hero` | Big title + description |
| `content` | Bullets / narrative body |
| `transcribe` | Dense transcript-style (legacy; often `content` + metadata) |
| `divider` | Section break |
| `figure` | Full-width figure + caption |
| `figure-wide` | Wide figure + two columns below |
| `diagram` | Mermaid body (no fences) |
| `two-column` | Structured `left` / `right` columns |
| `quote` | Pull quote |
| `comparison` | Side-by-side comparison |
| `code` | Code block |
| `steps` | Numbered steps |
| `summary` | Summary / recap |
| `table` | `headers:` / `rows:` in YAML |
| `proof` | Same rendering as `content`; marked for math-heavy derivations |

Do **not** invent new `layout` strings; the compiler rejects unknown layouts at parse time.
