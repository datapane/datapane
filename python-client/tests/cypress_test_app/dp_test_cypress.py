import datapane as dp
import datapane.blocks.text

file_param = dp.Params.get("__FILE__")
str_param = dp.Params.get("__STRING__REQUIRED__")
int_param = dp.Params.get("__INT__")
float_param = dp.Params.get("__FLOAT__")

app = dp.App(
    datapane.blocks.inline_text.Text(str_param),
    datapane.blocks.inline_text.Text(str(int_param)),
    datapane.blocks.inline_text.Text(str(float_param)),
    datapane.blocks.inline_text.Text(file_param.read_text()),
)

dp.upload_report(app, name="params-test-report", overwrite=True)
