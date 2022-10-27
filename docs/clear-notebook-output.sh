#!/usr/bin/env bash

set -euo pipefail
# takes a notebook as stdin, and strips known flakiness for stdout.
# example: `./clear-notebook-output.sh < docs/quickstart.ipynb`

# pass the stdin directly to jq (<&0)
exec jq --indent 1 "$(cat <<'EOF'
    # clear the outputs, if they're set
    (.cells[] | select(has("outputs")) | .outputs) = []
    # clear execution_count, if it's set
    | (.cells[] | select(has("execution_count")) | .execution_count) = null
    # unconditionally set the notebook metadata to be static
    | .metadata = {"language_info": {"name": "python"}}
    # allow tags, nothing else
    | .cells[].metadata |= if has("tags") then {tags} else {} end
EOF
)" <&0
