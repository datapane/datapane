#!/usr/bin/env bash

set -euo pipefail


# pass the stdin directly to jq (<&0)
exec jq --indent 1 \
  "(.cells[] | select(has(\"outputs\")) | .outputs) = [] | (.cells[] | select(has(\"execution_count\")) | .execution_count) = null | .metadata = {\"language_info\": {\"name\": \"python\"}} | .cells[].metadata |= if has(\"tags\") then {tags} else {} end" \
  <&0
