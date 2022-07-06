for f in $(find docs -type f -name '*.ipynb' ! -path '*.ipynb_checkpoints*')
    do 
        cd ${f%/*};
        poetry run jupyter nbconvert --to notebook --inplace --ExecutePreprocessor.timeout=-1 --execute ${f##*/};
        cd -;
done