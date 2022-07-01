# Apps

## Introduction

In addition to creating reports by running the computation on your own notebook, pipeline, or server, you may want to deploy Python scripts or notebooks to Datapane so they can be scheduled, be run with parameters, or run in response to API events.

Datapane provides an app platform, so you can generate reports in an automated fashion, in addition to creating them in your local environment.

Once you deploy your script or notebook as an app, it can be run in three ways:

#### Web Forms

Apps can be run with parameters entered through friendly web forms, which allows you to create interactive, self-service reporting tools for stakeholders.

{% content-ref url="tut-parameterising-a-script/" %}
[tut-parameterising-a-script](tut-parameterising-a-script/)
{% endcontent-ref %}

#### On a schedule

Apps can generate and update reports on a schedule, allowing you to create "live" dashboards and automated reports.

{% content-ref url="scheduling.md" %}
[scheduling.md](scheduling.md)
{% endcontent-ref %}

#### Through an API

You can trigger report generation through our API, which allows you to generate reports in response to events from other tools, such as Slack and Microsoft Teams, or your own product.

## Deploying an app

If you have a local Python script or notebook which creates a report using Datapane's `Report.upload` method (see [Creating a Report](../../reports/tut-creating-a-report.md)), you can deploy it to Datapane using the CLI. &#x20;

Let's use an example of a COVID report, which will be returned to the user when they run our app using the Datapane web interface.

{% hint style="info" %}
We recommend creating only one report per app. As many can be created as needed; however, only the last one in each app will be tracked in the web interface.
{% endhint %}

{% code title="simple_script.py" %}
```python
import pandas as pd
import altair as alt
import datapane as dp

dataset = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
df = dataset.groupby(['continent', 'date'])['new_cases_smoothed_per_million'].mean().reset_index()

plot = alt.Chart(df).mark_area(opacity=0.4, stroke='black').encode(
    x='date:T',
    y=alt.Y('new_cases_smoothed_per_million:Q', stack=None),
    color=alt.Color('continent:N', scale=alt.Scale(scheme='set1')),
    tooltip='continent:N'
).interactive().properties(width='container')

dp.Report(
    dp.Plot(plot), 
    dp.Table(df)
).upload(name='covid_report', open=True)
```
{% endcode %}

To deploy it, use Datapane's CLI.

```bash
$ datapane app deploy --app=simple_script.py --name=covid_script
```

This makes your app available on your private instance, where you can share it with other users. If you send them your app, they are able to generate the report from the previous example dynamically by hitting the Run button.

![](<../../.gitbook/assets/image (105).png>)

Every time the app is run, it pulls new COVID data and generates a fresh report, which can be shared or embedded.

![](<../../.gitbook/assets/image (113).png>)

## Configuration

In the previous example, we are deploying a single app and providing the name and file location through command-line arguments. This works well for simple scripts, but app often need other configuration, such as [parameter definitions](tut-parameterising-a-script/), other files or folders to deploy, and Python or OS requirements.

Datapane allows you to provide a configuration file called `datapane.yaml`. When you run `deploy`, Datapane looks for this file automatically. Before we continue, create a new folder and then run the `datapane app init` command inside it:&#x20;

```bash
$ datapane app init
$ ls
```

This will create a `datapane.yaml` file and a sample app.&#x20;

![](../../.gitbook/assets/screenshot-2021-09-17-at-14.31.13.png)

We already have an app from our previous example, so we can delete the sample `dp_script.py` and copy in our own. Because we're replacing the default app, we should specify the filename of our app in `datapane.yaml` using the `app` field. Whilst we are there, we can also choose a name.

{% code title="datapane.yaml" %}
```yaml
name: covid_script
app: simple_script.py # this could also be ipynb if it was a notebook
```
{% endcode %}

If we run `datapane app deploy` in this directory, Datapane will deploy our code with the configuration in `datapane.yaml`. Because we have given the script the same name as our previous one, this will overwrite `covid_script`. See the following link for the full reference on the configuration format.

{% content-ref url="tut-parameterising-a-script/datapane-yaml.md" %}
[datapane-yaml.md](tut-parameterising-a-script/datapane-yaml.md)
{% endcontent-ref %}

In the next section, we will explore adding parameters to your app, to enable reports to be generated dynamically based on user inputs.
