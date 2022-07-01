---
description: >-
  Apps can be parameterised, allowing them to dynamically generate reports
  through web forms or the API.
---

# Parameters and Forms

## Overview

Stakeholders commonly need to provide some configuration to your apps to enable self-service report generation. Datapane allows you to add parameters, which are presented to end users as **web forms**. This means that other people who have accounts on your instance can generate reports without worrying about code, notebooks, or setting up a Python environment.&#x20;

## Running & Parameters

Input parameters can be defined in your `datapane.yaml` configuration file, where you can enter a schema and configure the inputs. In your Python code, the parameters which you define in this file are accessible in the `Params` dictionary. You can get an item from the dictionary with `Params.get([value_name], [default_value])`

Following the previous example, the dataset we are pulling includes a few other useful parameters which people may want to graph. Let's add the ability for the end-user to choose from `new_cases_smoothed_per_million` , `new_deaths_smoothed_per_million`, `median_age`, and `gdp_per_capita` . Additionally, let's allow them to choose a subset of continents for the graph.

Based on this, we are going to add two parameters: `plot_field` and `continents` to the `parameters` section of our `datapane.yaml`. To configure what the end-user's form looks like, we can choose the type of widget. For the above, we're choosing a `enum` (which provides a dropdown select menu where the user must select one option), and a `list` (which allows the user to choose or more choices from a predefined list). We can also set the default parameters for each input and a description.

{% hint style="info" %}
Full details of parameter configuration and available fields are provided in the [API reference](parameters.md#parameter-form-fields).
{% endhint %}

{% code title="datapane.yaml" %}
```yaml
name: covid_script
script: simple_script.py # this could also be ipynb if it was a notebook
  
parameters:
  - name: field_to_plot
    description: Field to plot
    type: enum
    choices: 
      - new_cases_smoothed_per_million
      - new_deaths_smoothed_per_million
      - median_age
      - gdp_per_capita
  - name: continents
    description: Field to plot
    type: list
    choices:
      - Africa
      - Asia
      - Europe
      - Oceania
      - North America
      - South America
    default: 
      - Asia
      - North America
```
{% endcode %}

You can then use the `Params` object as you would when running on your Datapane instance, and we can customise our data and graph based on those inputs.

{% code title="simple_script.py" %}
```python
import pandas as pd
import altair as alt
import datapane as dp

dataset = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')

# Get input parameters
continents = dp.Params.get('continents', ['Asia', 'North America'])
field_to_plot = dp.Params.get('field_to_plot', 'new_cases_smoothed_per_million')

df = dataset[dataset.continent.isin(continents)].groupby(['continent', 'date'])[field_to_plot].mean().reset_index()

plot = alt.Chart(df).mark_area(opacity=0.4, stroke='black').encode(
    x='date:T',
    y=alt.Y(field_to_plot, stack=None),
    color=alt.Color('continent:N', scale=alt.Scale(scheme='set1')),
    tooltip='continent:N'
).interactive().properties(width='container')

dp.Report(
    dp.Plot(plot), 
    dp.Table(df)
).publish(name='covid_report', open=True)
```
{% endcode %}

When we run `app deploy`, Datapane will deploy a new version of our app, and use our parameters definition to generate the following form:

![](<../../../.gitbook/assets/image (103).png>)

Stakeholders can enter parameters and generate custom reports themselves, based on these fields. &#x20;

![](<../../../.gitbook/assets/image (111).png>)

