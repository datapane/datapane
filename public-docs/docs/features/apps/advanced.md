Datapane provides helpers to manage caching and sessions for your app.


## Lifecycle tips

- Datapane apps are stateful, and state is preserved across multiple function invocations.
- State is not currently persisted across restarts of the server
- The script is not run in its entirety upon each function call. This means you can load variables in the global (for instance, to make a large database query)

## Caching

You may want to cache the computation of a function which takes a long time or is memory/compute intensive. If you specify the `cache` parameter, subsequent calls to the same function same parameters will return the same results. This results in a large speedup even on trivial functions.

!!! note
    This is a hint that may be disabled depending on certain heuristics

```python
import datapane as dp

def calc(params):
    return params['x'] * params['y']

app = dp.Blocks(
    dp.Form(
        on_submit=calc,
        controls=[dp.NumberBox('x'), dp.NumberBox('y', initial=0)],
        cache=True
    )
)

dp.serve_app(app)
```

## Sessions

It's often necessary to share state between various function calls. Functions can have an (optional) parameter called `session`, which if present, contains a mutable `dict` which is stored on a per-session basis across all functions.


!!! note
    As our function is now stateful (i.e. will return different results given the same parameters), we disable the `cache` parameter.

```python
import datapane as dp

def calc(params, session):
    acc = session.get('acc', 0)
    result = params['x'] * params['y'] + acc

    session['acc'] = result

    return dp.Text(result)

app = dp.Blocks(
    dp.Form(
        on_submit=calc,
        controls=[dp.NumberBox('x'), dp.NumberBox('y')],
    )
)

dp.serve_app(app)
```
