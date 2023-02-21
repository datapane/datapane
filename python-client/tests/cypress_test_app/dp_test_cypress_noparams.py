import datapane as dp
import datapane.blocks.text

app = dp.App(
    datapane.blocks.inline_text.Text("__REPORT_RENDERED__"),
)

dp.upload_report(app, name="no-params-test-report", overwrite=True)
