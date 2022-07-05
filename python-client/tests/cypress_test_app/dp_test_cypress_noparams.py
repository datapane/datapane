import datapane as dp

dp.Report(
    dp.Text("__REPORT_RENDERED__"),
).upload(name="no-params-test-report", overwrite=True)
