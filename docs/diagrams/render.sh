#!/usr/bin/env bash
# Render the architecture diagram. Needs Graphviz (`sudo apt-get install -y graphviz fonts-dejavu`).
set -euo pipefail
cd "$(dirname "$0")"
dot -Tpng -Gdpi=110 architecture.dot -o architecture.png
dot -Tsvg architecture.dot -o architecture.svg
