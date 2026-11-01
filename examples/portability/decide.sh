#!/usr/bin/env bash
# Qualquer shell pluga: JSON entra, veredito sai.
set -euo pipefail
SPEC="${1:-examples/decide_const1.json}"
zq-ir decide "$SPEC" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["verdict"], d["refusal_reason"], d["receipt"]["seal_sha3_256"][:16])'
