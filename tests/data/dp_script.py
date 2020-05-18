import pandas as pd
import datapane as dp

# basic report creation, with params
df = pd.DataFrame.from_dict({"x": [4, 3, 2, 1], "y": [10.5, 20.5, 30.5, 40.5]})
blocks = [dp.Markdown(f"Dummy Markdown block - {dp.Params['p1']}"), dp.Table.create(df)]

# test running as main or by datapane runner
if dp.on_datapane:
    print("on datapane")
if __name__ == "__datapane__":  # same as dp.by_datapane
    print("by datapane")
    report = dp.Report(*blocks, name="s")
    report.publish(headline="My Report")
