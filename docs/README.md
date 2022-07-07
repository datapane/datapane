# datapane-docs-beta
The new Datapane documentation.

# Generating the docs

1. Run `./nbbuild.sh` to execute all Jupyter notebooks and generate Datapane reports and image previews.
2. Run `poetry run mkdocs build` to generate static site in `site/`.

`poetry run mkdocs serve` can be used to serve locally.

# Embedding reports and previews

1. Save your report to the same directory as the notebook:

    ```python
    report.save(path="simple-report.html")
    ```

2. Use `dpdocsutils` to:
    - embed the interactive report (`iframe=True`), 
    - or insert a generated preview image that hyperlinks to the interactive report (`iframe=False`, default)

    ```python
    from dpdocsutils import previews
    previews.embed_local_report('/tutorials/basics/simple-report.html', width="100%", height=400)
    ```

3. Mark the cell with the metadata tag `remove_input` so we only see the output.

# Hiding input and/or output

Use metadata to show or hide input/output cells in notebooks.
- `remove_input`, e.g. for cells containing preview code from `dpdocsutils`.
- `remove_all_output`, e.g. for the cells outputting information after calling `.save()` or `.upload()`.
- `remove_cell`, e.g. when you want something executed without displaying input or output.