for f in $(find docs -type f -name '*.ipynb' ! -path '*.ipynb_checkpoints*')
    do 
        cd ${f%/*};
        poetry run jupyter nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=-1 --ClearMetadataPreprocessor.enabled=True --ClearMetadataPreprocessor.preserve_cell_metadata_mask tags --execute ${f##*/};
        cd -;
done