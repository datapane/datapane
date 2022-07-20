#!/bin/bash
set -euo pipefail

find docs -type f -name '*.ipynb' -not -path '*.ipynb_checkpoints*' -print0 | while IFS= read -r -d '' f; do
    cd "${f%/*}"
    poetry run jupyter nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=-1 --ClearMetadataPreprocessor.enabled=True --ClearMetadataPreprocessor.preserve_cell_metadata_mask tags --execute "${f##*/}"
    cd -
done
