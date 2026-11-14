#!/bin/sh
# Configura la identidad de git de este repositorio (tiene prioridad sobre la global del contenedor).
set -e
cd "$(git rev-parse --show-toplevel)"
git config user.name  "sebasvelace"
git config user.email "sebastianvelace@gmail.com"
git config commit.gpgsign false
git config tag.gpgsign false
git config core.hooksPath .githooks
