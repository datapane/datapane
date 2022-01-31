import datapane as dp

file_param = dp.Params.get("__FILE__")
str_param = dp.Params.get("__STRING__REQUIRED__")

dp.Report(
    dp.Text(str_param),
    dp.Text(file_param.read_text()),
).upload(name="params-test-report")
