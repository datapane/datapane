import datapane as dp

file_param = dp.Params.get("__FILE__")
str_param = dp.Params.get("__STRING__REQUIRED__")
int_param = dp.Params.get("__INT__")
float_param = dp.Params.get("__FLOAT__")

dp.Report(
    dp.Text(str_param),
    dp.Text(str(int_param)),
    dp.Text(str(float_param)),
    dp.Text(file_param.read_text()),
).upload(name="params-test-report", overwrite=True)
