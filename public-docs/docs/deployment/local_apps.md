You can host a Datapane app from inside your current Python environment, whether that's your local machine, or a hosted notebook like Colab or Databricks.

To host your app, run `dp.serve`.

!!! note
    A port will be chosen automatically, but you can manually specify `port` and `host`.

```python
import datapane as dp

def calc(params):
    return params['x'] * params['y']

app = dp.Blocks(
    dp.Form(
        on_submit=calc,
        controls=[dp.NumberBox('x'), dp.NumberBox('y')],
    )
)

dp.serve_app(app)
```

## Creating a public URL

Datapane has built-in support for ngrok, which allows you to create a public, shareable URL for your data app. Simply add `public=True` to your serve command. This will prompt you to enter your ngrok token, and will return a URL which you can share.

```python
import datapane as dp

def calc(params):
    return params['x'] * params['y']

app = dp.Blocks(
    dp.Form(
        on_submit=calc,
        controls=[dp.NumberBox('x'), dp.NumberBox('y')],
    )
)

dp.serve_app(app, public=True)
```

## Embed mode

If you are embedding your app in a third-party product, you will need to pass `embed_mode=True` to `dp.serve`. This disables specific security policies which will not work in an iframe.
