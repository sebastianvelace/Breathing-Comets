# Reglas del repositorio (prioridad máxima)

## Git
- Trabaja y haz push **solo en `main`**. Nunca crees ramas `claude/*` ni otras ramas, salvo que el usuario lo pida explícitamente.
- Autor y committer de todos los commits: `sebasvelace <sebastianvelace@gmail.com>`. Antes del primer commit de cada sesión ejecuta `sh scripts/git-identity.sh`.
- **No agregues** `Co-Authored-By`, `Claude-Session`, "Generated with Claude Code" ni ninguna otra línea de atribución en commits, PR, issues o comentarios.
- No firmes commits con llaves del entorno (`commit.gpgsign false`).
- Los hooks de `.githooks/` deben estar activos (`core.hooksPath .githooks`); no los saltes con `--no-verify`.

## Producto
- La guía es `docs/BUILD.md`. Ante cualquier duda, manda ese documento.

## Transparencia
- El uso de IA se declara en la sección "Use of AI" de la entrega de Space Apps, no en el historial de git.
