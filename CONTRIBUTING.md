# Contributing to Datapane

## How is Datapane Framework developed?

Datapane Framework is an open-source product developed by Datapane and open-source contributors.

For ease of development across the multiple projects, the workspace is maintained within a public, multi-langauge monorepo.

For making changes, just:

1. open a PR
2. have it reviewed
3. merge!!

### Regarding End-to-end tests

Datapane Cloud is maintained in a separate private repo, which has the public monorepo nested within it as a Git Submodule.

This is to ease some pain when working on the backend (easier e2e testing), while still allowing an easy path for public
contributions to Datapane Framework.

Crucially, this means End-to-end tests will not run for public contributions.

For now, it's recommended to use your judgement:

-   smaller contributions can forgo the e2e tests, which can be fixed retroactively by someone with access; or
-   A temporary PR can be created, updating the submodule to point at the contributor's fork.
    -   WARNING: Be mindful that this allows untrusted code to be run within the private repo (without secrets).

The longer term plan is to provide a way to run e2e tests for the public directly.

## Navigating the Repo

The repo is made up of multiple projects of different languages.
This is to simplify cross-project work without the overhead of multiple repositories hanging around.

However, you should still be able to work on one project without needing to be aware of the others.

### Structure

There are 4 directories to be aware of:

#### Root (`./`)

The root of the repository holds any files that apply to all projects.

This could include:

-   High-level documentation
-   Workspace configurations

Generally speaking, if something is for a specific project, it shouldn't live in the root directory.

#### Docs (`./docs`)

The home for any and all documentation relating to how to use Datapane Framework.

This is a great place for contributing examples + guides to.

#### Dev Tools (`./dev`)

The home for any resources relating to managing the workspace.

This could be scripts for cross-project dependencies, shared utilities,
or project templates to act as a reference point.

#### Projects (`./projects/*`)

Any projects live here.
These could be projects for public distribution, or supporting projects that are
used internally within the workspace.

Each project will have a `CONTRIBUTING.md` file to explain how to get started there.

**Notable** projects include:

-   `python-client`: the Datapane CLI + Framework
-   `web-components`: a Supporting Project which builds components used to render reports

## Ways to Contribute

Whilst this document is aimed at people wanting to work on the codebase, we recognize
that contributing is so much more than just writing code.

If you'd like to just ask a question, show off what you're doing, or just hang out with us,
feel free to drop by our Discord server or forum, found on our [community page][community-page].

### Did you find a bug?

-   **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/datapane/datapane/issues).

-   If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/datapane/datapane/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

### Did you write a patch that fixes a bug?

-   Open a new GitHub pull request with the patch.

-   Ensure the PR description clearly describes the problem and solution. Include the relevant issue number, if applicable.

### Do you intend to add a new feature or change an existing one?

-   That's great - it's always good to hear feedback and new ideas!

-   Check to see if it's been discussed already in our [forum][forum]

-   Open up a new Thread in the [forum][forum], we can start chatting about your needs!

### Do you have questions about the source code?

-   Feel free to drop by to [chat][chat], or post a question in the [forum][forum]!

### Do you want to contribute to the Datapane community?

Datapane is a joint startup and community effort. We encourage you to pitch in and join to add any features you are interested in!

Feel free to come [chat][chat] with us!

Thanks! :heart: :heart: :heart:

Datapane Team

[community-page]: https://datapane.com/community
[chat]: https://chat.datapane.com/
[forum]: https://forum.datapane.com/
