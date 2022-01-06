import datapane as dp

str_param = dp.Params.get("__STRING__REQUIRED__")
dp.Report(dp.Text(str_param), dp.Text("--------")).upload(name="params-test-report")
