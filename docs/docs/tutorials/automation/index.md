---
description: Automating report creation, including via GitHub Actions
---

# Automation

## Introduction

Once you have a report you're happy with, you often need to generate it automatically; for instance, to run on a schedule, or to be triggered through an API. To make this easier, Datapane provides a GitHub action which allows you to run your Python script automatically to generate and publish a new report.

{% embed url="https://github.com/marketplace/actions/datapane-build" %}

To learn more about GitHub actions, [see the documentation](https://docs.github.com/en/free-pro-team@latest/actions).

### GitHub Actions vs. Datapane Teams Script Runner

_Datapane Teams_ also provides a [script runner](../datapane-teams/script-and-jupyter-deployment/), which has several advantages and optimizations not available on the GitHub action runner, including:

* **Friendly end-user forms**. GitHub actions are not suitable for allowing authenticated, non-technical users to to run your script with parameters; Datapane's script runner provides self-service forms for stakeholders.
* **Jupyter support**. Datapane's script runner allows you to deploy and run Jupyter Notebooks with parameters to generate dynamic reports, whilst the GitHub Action relies on a Python file
* **On-premise and cloud hosting**. Datapane's script runner does not require GitHub, and can run on your own cloud environment or server.
* **Private report generation**. Generate private reports which are not shared with the outside world.

## Configuring your job

{% hint style="info" %}
This tutorial presumes you have a basic understanding of how to use GitHub actions. For more information, please refer to GitHub's documentation.
{% endhint %}

Your GitHub action requires access to your Datapane API token, which you can find on your [settings page](https://datapane.com/settings) once you have logged in to Datapane. This should not be stored in plain text, and should be added to your repository's [secrets](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets) section.

The Datapane action requires that the repository contains a Python script which publishes a report. Once you have your token in your repository, you can you can add the Datapane action as a `job`, including the path to the Python script, and a reference to your secret token.

```yaml
jobs:
  build_report:
    runs-on: ubuntu-latest
    name: Run end-of-week Datapane reports
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v1
        with:
          python-version: 3.8
      - uses: datapane/build-action@v2
        with:
          script: "reports/end_of_week.py"
          token: ${{ secrets.TOKEN }}
```

## Running your action

### Running on a schedule

To run your report on a schedule, you can use the `schedule` option:

```yaml
on:
  schedule:
    # run at 5pm every Friday
    - cron:  '00 17 * * 5'
```

### Manual running

Manual runs can be triggered via the `workflow_dispatch` option. If your report has user-configurable parameters, you can define these in your workflow and enter them via the GH Action site when manually triggering your workflow.

The parameters in the GH Action UI are all strings, however Datapane will convert them to primitive values as needed, e.g. the string `false` becomes a python boolean `False` value. Workflow parameters are described in the [docs](https://docs.github.com/en/free-pro-team@latest/actions/reference/events-that-trigger-workflows#workflow\_dispatch). The input must manually be converted to the `parameters` json string to pass to the Datapane `build-action` as follows.

```yaml
on:
  workflow_dispatch:
    inputs:
      company:
        description: 'Company stock name'
        required: true
        default: 'GOOG'
      market:
        description: 'Country to report for'
        required: false
jobs:
  build_report:
    runs-on: ubuntu-latest
    name: Run Parameterised Datapane report
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v1
        with:
          python-version: 3.8
      - uses: datapane/build-action@v2
        with:
          script: "reports/financials.py"
          token: ${{ secrets.TOKEN }}
          parameters: ${{ toJson(github.event.inputs) }}
```

Once you have committed your manual run, you can run it in the following ways:

**Trigger by Github UI**

{% hint style="info" %}
For more information, see GH [docs](https://docs.github.com/en/free-pro-team@latest/actions/managing-workflow-runs/manually-running-a-workflow#running-a-workflow-on-github) for running a parameterised datapane workflow using the GH Action UI.
{% endhint %}

GitHub's action UI provides an interface for running your action with parameters.&#x20;

**Trigger by API/Webhook**

{% hint style="info" %}
For more information, see GitHub [docs](https://docs.github.com/en/free-pro-team@latest/rest/reference/actions#create-a-workflow-dispatch-event) for running a parameterised datapane workflow via an API Call.
{% endhint %}

To trigger your report generation through an API, you need to send a POST request to `/repos/{owner}/{repo}/actions/workflows/{workflow_name}/dispatches`. For instance, for a repo called `acme/reporting`, with a workflow as above called `financial_report` you could trigger it as follows:

```bash
$ curl \
  -u GH_USERNAME:GH_TOKEN \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/acme/reporting/actions/workflows/financial_report/dispatches \
  -d '{"ref":"ref", "inputs": { "company": "APPL", "market": "UK"} }'
```

## Advanced Usage

### Caching

**Caching pip**

Pip dependencies can be cached via [actions/cache](https://docs.github.com/en/free-pro-team@latest/actions/guides/building-and-testing-python#caching-dependencies). The cache key should contain the `requirements` and `version` input parameters, if they're used.

An example workflow on Ubuntu with caching is shown below:

```yaml
env:
  version: "==0.8.0"
  requirements: '["networkx"]'
jobs:
  build_report:
    runs-on: ubuntu-latest
    name: Build Datapane report
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v1
        with:
          python-version: 3.8
      - uses: actions/cache@v2
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ env.requirements }}-${{ env.version }}
      - uses: datapane/build-action@v2
        with:
          script: "reports/financials.py"
          token: ${{ secrets.TOKEN }}
          version: "${{ env.version }}"
          requirements: "${{ env.requirements }}"
```

**Caching packages**

It's also possible to cache the installed packages themselves, speeding up action running, by creating a `venv` first, activating it, and caching it between runs.

```yaml
env:
  version: "==0.8.0"
  requirements: '["networkx==2.5", "pandas==1.0.5"]'
jobs:
  build_report:
    runs-on: ubuntu-latest
    name: Build Datapane report
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v1
        with:
          python-version: 3.8
      - uses: actions/cache@v2
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ env.requirements }}-${{ env.version }}
      - uses: actions/cache@v2
        with:
          path: ~/.venv
          key: ${{ runner.os }}-pip-${{ env.requirements }}-${{ env.version }}
      - name: Create and activate venv
        run: |
          python3 -m venv ~/.venv
          echo "~/.venv/bin" >> $GITHUB_PATH
      - uses: datapane/build-action@v2
        with:
          script: "reports/dp_script.py"
          token: ${{ secrets.TOKEN }}
          requirements: "${{ env.requirements }}"
```

Note that when doing this, ensure that you clearly specify your package version in your requirements otherwise you may end up with cache hits for old versions of your packages.
