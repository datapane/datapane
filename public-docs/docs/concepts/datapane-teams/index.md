# Introduction

## Overview

Data scientists like using the Python ecosystem to analyze data, but struggle to share results with stakeholders or make analyses self-service.&#x20;

Datapane provides an API-first platform enables data teams to share interactive reports and apps with stakeholders and clients. This means data scientists can use the tools they are gifted at to drive business decisions, and stakeholders can self-serve on insights and scripts (instead of waiting on a backlog).

## Comparisons

### Realtime frameworks such as Dash and Streamlit

Application frameworks such as Dash and Streamlit are for building realtime, synchronous applications. In this model, you build and host a Python application on a server which presents a web front-end. This is generally a good fit if you are building a realtime app; for instance, a computer vision model which you want to test with different parameters to see the result update in a highly interactive fashion.

Datapane's reporting and script automation APIs work differently, and which is most suitable depends on your use-case.

* Datapane's _Report API_ sits inside your existing environment -- such as Jupyter, Airflow, Colab, etc. -- and allows you to create and upload reports from plots and data in these environments. The report which is created does not require you to deploy your source code or run a Python server, and thus can be easily embedded, shared, emailed, etc. Each time you upload the report, it sends up only the plots and data, and creates a new version snapshot.
* For reporting use-cases, Datapane's _App API_ allows you to deploy your existing Jupyter Notebook or Python scripts: you don't build an application or manage the infrastructure. Your apps are run in a **serverless**, event-driven model in response to auto-generated forms, external API calls, or on a schedule, in order to automatically generate reports. This is suitable for allowing data science teams to deploy their notebooks and scripts so that stakeholders can generate and refresh reports in their web-browser; it is also often used to generate new reports on a cadence (e.g. a weekly analytics report which is emailed to the team), in response to API-events, or via other applications -- such as Slack, Microsoft Teams, or Salesforce integrations.

### Tableau, Looker, and other traditional BI tools

Datapane is not intended to be a drop-and-drop dashboard builder, and most companies use Datapane in addition to Tableau, Looker, or another BI platform. Python is often preferred by data science teams for its flexibility, ecosystem, and developer tooling (e.g. versioning, collaboration), but there are various other reasons why you may use the Python ecosystem and Datapane in addition to your BI platform.

1. Making data science available across your company. Although BI platforms allow some exploratory analysis methods, they are extremely limited for any advanced analyses or data science. Datapane makes it easy for the rest of the company to bring advanced analyses into their workflow, by consuming reports or or automating them to generate actionable results. For instance, allowing product and marketing teams to integrate forecasting, machine learning, clustering, etc. into their workflows.
2. Building reports from ad-hoc data sources, such as APIs and data warehouses. A traditional BI tool sits on a centralized data warehouse, and Python is often used to pull, join, and merge data from non-centralized data sources for ad-hoc analyses. For instance, pulling data from Salesforce and joining it with Google Ads data, to create a report for a client or internal stakeholder.
3. Advanced visualizations. Python's ecosystem has a wealth of libraries for advanced visualizations which are not possible in a general-purpose BI tool.

## Support

For a full explanation of the various kinds of enterprise support available, read our [support policy](/concepts/support-policy/).&#x20;

