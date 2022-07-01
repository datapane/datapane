# Adding Source Code

### Introduction

Ever checked out a cool report and wondered how it is built? Datapane now allows you to add your source code to a report so that others can reproduce and build on it. 

![](../../.gitbook/assets/screenshot-2021-09-16-at-15.22.06.png)

If you're using the Community version, it's a great way to build an audience. For Datapane Teams, it helps to democratize data and empower your team to build their own reports. 

{% hint style="info" %}
This feature is available for Datapane version 0.11.11 or later
{% endhint %}

### Adding Source code

In the report settings page, attach a static file \(we only support `.ipynb` at present\) or a link to a repo: 

![](../../.gitbook/assets/screenshot-2021-07-19-at-09.53.20.png)

You can also do this via the Python API through the `source_url` or `source_file` parameters as follows: 

{% tabs %}
{% tab title="File" %}
```python
dp.Report(
    dp.DataTable(example_df)
.upload(name="report_example", source_file = "~/me/my-file.ipynb")
```
{% endtab %}

{% tab title="URL" %}
```python
dp.Report(
    dp.DataTable(example_df)
.upload(name="report_example", source_url = "https://github.com/me/my-repo")
```
{% endtab %}
{% endtabs %}

\(Hint: you can also include the name of the file you are currently working in!\). When a viewer sees your report, they will see an option to 'View code'. Clicking on that option will show them the rendered notebook code - try it with the embedded report below! 

{% embed url="https://datapane.com/u/johnmicahreid/reports/0kzZz2k/hello-world/" %}

{% hint style="warning" %}
Adding source code does not auto-refresh or execute your report. If you are interested in building a report that updates regularly, check out our section on [Automation](../automation-with-github-actions.md). 
{% endhint %}

### Excluding sensitive information

If your notebook contains sensitive information that you don't want users to see e.g. secrets or tokens,  add the `exclude` tag to every notebook cell you want excluded. When you add this source file to your report, our backend will automatically remove those cells so your viewers can't see them. 

To do this in Jupyter, click 'View' -&gt; 'Cell Toolbar' -&gt; 'Tags'.  This will enable the tag toolbar, where you can type in `exclude` to add it as a tag. 

![](../../.gitbook/assets/screenshot-2021-07-19-at-10.47.04.png)

