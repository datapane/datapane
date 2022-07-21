# Contributing to Datapane

## How is Datapane developed?

Datapane CLI and library is an open-source product developed by the Datapane team and open-source contributors.

For ease of development across multiple projects, we maintain our code within a public monorepo.

For making Code changes, just open a PR, have it reviewed, and we'll merge it when ready.

### Regarding End-to-end tests

Datapane Teams is maintained in a separate private repo (referred to as `datapane-hosted`), which has the public monorepo nested within it as a Git Submodule.

This is to allow cross-project when we're working on the backend (easier e2e testing).

Crucially, this means End-to-end tests will not run for public contributions.

For now, it's recommended to use your judgement:

-   smaller contributions can forgo the e2e tests, which can be fixed retroactively by one of our staff; Or
-   A temporary PR updating the submodule to point at the Contributor's Fork
    -   Be mindful that this allows untrusted code to be run within our Private Repo

The longer term plan is to provide a way to run e2e tests for the public directly.

## Navigating the Repo

We maintain a Multi-language Monorepo.
This is to simplify cross-project work without the overhead of multiple repositories hanging around.

However, you should be able to work on one project without needing to be aware of the other projects.

### Structure

There are 4 directories to be aware of:

#### Root (`./`)

The Root of the repository holds any repo-level files relating to datapane as a whole.

In here, we'd expect to see things like Git configs, global linting rules, and high-level guidelines.

Generally speaking, if something is for a specific project, it shouldn't live in the root directory.

#### Docs (`./docs`)

The Global Documentation, the home for any and all documentation relating to how to use
any Datapane product.

This is a great place for contributing examples + guides to.

#### Dev Tools (`./dev`)

The home for any resources relating to managing the repository.

This could be scripts for cross-project dependencies, shared utilities,
or project templates to act as a reference point.

#### Projects (`./projects/*`)

Any projects live here.
These could be projects we intend to distribute, or supporting projects that are
used internally by other projects.

Each project will have a `CONTRIBUTING.md` file to explain how to get started there.

**Notable** projects include:

-   `python-client`: the Datapane CLI + Framework
-   `web-components`: a Supporting Project which builds components used to render reports

## Ways to Contribute

Whilst this document is aimed at people wanting to work on the codebase, we recognise
that Contributing is so much more than just writing code.

If you'd like to just ask a question, show off what you're doing, or just hang out with us,
feel free to drop by our Discord or Forum on our [Community page][community-page].

### Did you find a bug?

-   **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/datapane/datapane/issues).

-   If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/datapane/datapane/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

### Did you write a patch that fixes a bug?

-   Open a new GitHub pull request with the patch.

-   Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

### Do you intend to add a new feature or change an existing one?

-   That's great - it's always good to hear feedback and new ideas!

-   Check to see if it's been discussed already in our [Forum][forum]

-   Open up a new Thread in the [Forum][forum] so we can start chatting about your needs!

### Do you have questions about the source code?

-   Feel free to drop by to [Chat][chat], or post a question in the [Forum][forum]!

### Do you want to contribute to the Datapane community?

Datapane is a joint startup and community effort. We encourage you to pitch in and join to add any features you are interested in!

Feel free to come [Chat][chat] with us!

Thanks! :heart: :heart: :heart:

Datapane Team

[community-page]: https://datapane.com/community
[chat]: https://chat.datapane.com/
[forum]: https://forum.datapane.com/
