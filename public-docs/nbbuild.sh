#!/bin/bash
set -euo pipefail

# TODO: we should probably bundle the statics within the docs build
# We build against the datpane source, so reference a CDN that has statics
# that match closer to what we build against
# Note that Staging can be a few hours out of step with source.
dp_version="$(poetry run python -c 'print(__import__("datapane").__version__)')"
export DATAPANE_CDN_BASE="https://staging.datapane-cdn.com/v${dp_version}"

# Prevent a real browser from being discovered for Apps that request `open=True`.
# We never want it during the docs build
# we use `true`, as it should always be available, and always give a '0' exit code
export BROWSER='true'


# remove artifacts before building
find docs -type f \( -name '*.html' -o -name '*-preview.png' \) -delete

find docs -type f -name '*.ipynb' -not -path '*.ipynb_checkpoints*' -print0 | while IFS= read -r -d '' f; do
    cd "${f%/*}"
    poetry run jupyter nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=-1 --ClearMetadataPreprocessor.enabled=True --ClearMetadataPreprocessor.preserve_cell_metadata_mask tags --execute "${f##*/}"
    cd -
done
