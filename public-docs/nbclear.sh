#!/bin/bash
set -euo pipefail

# clear all output from notebooks in-place
# this is not necessary before commit because the git filter does this automatically
find docs -type f -name '*.ipynb' -not -path '*.ipynb_checkpoints*' -print0 | while IFS= read -r -d '' f; do
    cd "${f%/*}"
    poetry run jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --ClearMetadataPreprocessor.preserve_cell_metadata_mask tags --inplace "${f##*/}"
    cd -
done
