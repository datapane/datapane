# datapane-docs

The Datapane documentation.

## Requirements

1. `poetry`, as per [their instructions](https://python-poetry.org/docs/master/#installing-with-the-official-installer)
2. `chromium`, through your package manager:

    _we will pick up `chromium` or `chromium-browser` from your `$PATH`_

    - MacOS: `brew install chromium`
    - Fedora: `sudo dnf install chromium`

## Generating the docs

1. Run `poetry run ./nbbuild.sh` to execute all Jupyter notebooks and generate Datapane apps and image previews.
2. Run `poetry run mkdocs build` to generate static site in `site/`.

`poetry run mkdocs serve` can be used to serve locally.

_hint:_ You can also use the same tool we use for Deploys for local serving after a build:

```
wrangler pages dev --live-reload
```

## Hiding input and/or output

Use metadata to show or hide input/output cells in notebooks.

-   `remove_input`,
-   `remove_all_output`, e.g. for the cells outputting information after calling `.save()` or `.upload()`.
-   `remove_cell`, e.g. when you want something executed without displaying input or output.

## Contributing

The docs include many Jupyter notebook (`ipynb`) files that must have their output and metadata (except `tags`) cleared before a commit.

The `.gitattributes` in the `/public-docs` directory expects the `clear-notebook-output` filter. Please add it to your config with the following command:

```bash
git config filter.clear-notebook-output.clean "./public-docs/clear-notebook-output.sh"
```

(this also requires the `jq` command to be installed)

## Deploying

We use Cloudflare Pages for hosting the docs, under the project name `datapane-docs`.

You will need `wrangler` 2.x [installed][wrangler-install].

1. Follow the [build](#Generating-the-docs) instructions to generate the `./site/` directory
2. Run `task deploy`

    _this will run the correct wrangler command for you based on your branch_

[wrangler-install]: https://developers.cloudflare.com/workers/wrangler/get-started/
