# Scheduled Report Runs

Generate reports on a scheduled cadence to create live dashboards.

If you deploy your script or Jupyter Notebook as a Datapane app, you may want to run it on a schedule to automatically create reports for your team -- for instance, to pull down fresh data from your warehouse each day, or poll an internal API for changes.&#x20;

Scheduling is controlled through the Datapane CLI, where you can use crontab to configure when you would like your report to run.&#x20;

To create a new schedule, use `create`:

```shell
$ datapane schedule create <script name> <crontab> [-p <parameters>]
```

`create` takes three parameters:

-   `app`: the name of the app to run
-   `cron`: crontab representing the schedule interval. Note that schedules will be run in UTC, not the user's local timezone.
-   `parameters` (optional): if your app requires parameters, a key/value list of parameters to use when running the app on schedule

!!! info

    If you need help generating a crontab, please use a website such as [https://crontab.guru/](https://crontab.guru/).

If we wanted to run our COVID app every day at 9am, we could use the following command:

```shell
$ datapane schedule create your-username/covid_script "0 9 * * MON"
```

Optionally, we could also include any input parameters using `-p`

```shell
$ datapane schedule create[your-username]/covid_script "0 9 * * MON" -p '{"continents": ["Europe"], "field_to_plot": "gdp_per_capita"}'
```

If we wanted to find out what active schedules we have, we can use the `list` command:

```shell
$ datapane schedule list

Available Schedules:
  id  script                                          cron         parameter_vals
----  ----------------------------------------------  -----------  -------------------------------------------------------------
   3  https://acme.datapane.net/api/scripts/X0AEQAd/  0 9 * * MON  {}
   4  https://acme.datapane.net/api/scripts/X0AEQAd/  0 9 * * MON  {"continents": ["Europe"], "field_to_plot": "gdp_per_capita"}
```

If we would like to delete our schedule, we can use `delete`

```shell
$ datapane schedule delete 3
```

## Using a scheduled report

As you can update a report, scheduling allows you to create a live report which is updated automatically on a cadence. If you browse to the report which your script publishes, it will automatically be updated and show you the latest version. Similarly, if you are [embedding your report](../../reports/publishing-and-sharing/embedding-reports/#business-tooling) (or an element of your report) into a third-party platform such as Confluence or Salesforce, your embed will be updated automatically.
