# Datapane Cloud

{% content-ref url="reports/publishing-and-sharing/" %}
[publishing-and-sharing](reports/publishing-and-sharing/)
{% endcontent-ref %}

If you want to share your report on the web, _Datapane Studio_ provides a free API and hosted platform for uploading and sharing reports. If you have already [created an account and are signed in](tut-getting-started.md#authentication), you can upload your report in a single Python command:

```python
dp.Report(
    dp.Plot(plot), 
    dp.DataTable(df)
).upload(name='Vaccination Report', open=True)  # upload & open report in the browser
```

Once uploaded, you can share your report with your community, class, or friends by sharing the link.

![A published report on Datapane - easy to share privately or publicly](.gitbook/assets/dp-screenshot.png)

In addition, you can embed your uploaded report into social platforms, like Reddit and Medium, where your readers can explore your data and plots interactively without leaving your content, like this:

{% embed url="https://datapane.com/u/datapane/reports/covid-vaccinations/" %}
Live embedded Datapane report
{% endembed %}

{% hint style="info" %}
Your free Studio account comes with an unlimited number of public reports, and 5 private reports so you can test it within your organization. If you need more private reports, [contact us](mailto:support@datapane.com) or try our Enterprise product (read on)
{% endhint %}

# Datapane Teams

{% content-ref url="broken-reference" %}
[Broken link](broken-reference)
{% endcontent-ref %}

If your team is using the Python data stack for analysis and visualization, but is still relying on a drag-and-drop BI tool to share results, _Datapane Teams_ provides an API-first way to share reports directly from Python. This enables data teams to use the tools they are gifted at to drive business decisions, and allows stakeholders to self-serve on what the data team is building, instead of going through a backlog.

In addition to providing secure, authenticated report sharing, _Datapane Teams_ allows automated report generation by allowing data teams to deploy their Python scripts and Jupyter Notebooks to the cloud. Reports can be generated from parameters entered through web forms, on a schedule, or on-demand through our HTTP and Python APIs.

Other features include:

* APIs to utilise blobs and secrets in your scripts
* [Whitelabel embedding](datapane-teams/styling.md) of Datapane reports in your own products
* [Groups and secure-sharing features](datapane-teams/authentication-and-sharing/) to control access and share reports with external clients
* and [many more](https://datapane.com/enterprise/)