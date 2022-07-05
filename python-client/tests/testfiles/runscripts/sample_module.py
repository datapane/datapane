# import datapane as dp
df = "my_df"
print(f"x is {x}")
y = x


def foo():
    global y
    print("in foo")
    print(df)
    y += 1
    print(y)
    return df
