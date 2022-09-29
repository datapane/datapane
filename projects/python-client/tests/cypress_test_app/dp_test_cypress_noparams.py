import datapane as dp

app = dp.App(
    dp.Text("__REPORT_RENDERED__"),
)

dp.upload(app, name="no-params-test-report", overwrite=True)
