Datapane provides several advanced features to help you build production-ready apps, assiting with performance, caching, session handling, and more.

In this section we list some of these features and how they can help you build more advanced apps for your users.

## Lifecycle

Datapane apps have a simple, stateful lifecycle that follows the general execution of a Python scripts / Jupyter notebook - that is, they are are executed from top-to-bottom, and all global variables and top-level functions that have been defined in scope are available for use in your Python functions - it's all just normal Python and works as expected!

This means you can do things like load a database table into memory before defining a backend function and make use of it within the function, or use modifiers like `global` to mutate an object within backend functions.

```python
from vega_datasets import data
import datapane as dp

# a globally-accessible DataFrame
df = data.iris()

def filter_df(column: str):
    return dp.DataTable(df[column])

blocks = dp.Blocks(
    dp.Form(
        on_submit=filter_df,
        controls=dp.Controls(column = dp.Choice(options=list(df.columns), label="Select column to filter"))
    )
)
dp.serve_app(blocks)
```

In the example above, `df` is referenced by `filter_df` and can be accessed in that function by all users when the function is called. It's important to note that Datapane supports multiple users by default, and Datapane will call ``filter_df` automatically for each user individually upon submitting the form.

!!! warning:
    Datapane apps support multiple users via threads, so normal considerations apply when modifying shared data structures across different threads

When shutting down the server, no state is preserved, this means that all users will lose any unsaved data and will need to reload their apps within the browser upon restarting the server again.

### Lifecycle tips

- Datapane apps are stateful, and state is preserved across multiple function invocations
- The entire Python script is not run in its entirety upon each function call - this means you can load variables in the global (for instance, to make a large database query)

## Function Chaining

We have mentioned that a backend function receipts parameters as input and returns a set of blocks that updates the users view. For simple cases the blocks returned will be objects like Plots and DataTables. However it's also possible to return further Compute Blocks from a backend function.

These are presented to the User in their App for performing further input that is in return sent to this __nested__ function - we term this _function chaining_. The functions defined and returned in these nested _Compute Blocks_ can be `lambdas`, previously defined / inline functions, and can, most importantly, refer to and capture existing variables in scope. This means it's possible to collect multiple pieces of input from a user, return per-user data, and even dynamically generate future input based on existing input - Python's dynamic nature makes quite advanced scenarios possible. This may be demonstrated best with an example,

```python
from pathlib import Path
import pandas as pd
import datapane as dp

def load_file(file: Path):
    # load the user's input into the file
    df = pd.read_csv(file)

    def process_df(col_name: str):
        # a nested function which has access to `df` loaded in the previous interaction
        return dp.DataTable(df[col_name])

    return [
        df.describe(),
        # return a new Form that calls the nested function
        dp.Form(on_submit=process_df, controls=dict(col_name=dp.TextBox()))
    ]

blocks = dp.Blocks(
    dp.Form(
        on_submit=load_file,
        controls=dict(file=dp.File())
    )
)
dp.serve_app(blocks)
```

In the above, the function chaining is isolated for each user, and uploaded `df` is stored independently to other users currently using the app.

## Function Caching

Your backend function may perform complex calculations and thus take a long time to finish and/or is memory/compute intensive - this can slow down he performance of your app and frustrate users. To help, Datapane provides the ability to cache backend functions and reuse their results when called via a _Compute Block_.
By setting the `cache=True` when defining the _Compute Block_, subsequent calls to the same function with the same parameters will return the same, previously calculated, value. This can result in large speedups even on trivial functions.

!!! note
    The `cache` parameter is currently _experimental_ and is treated by the Datapane server as a suggestion that may be ignored depending on certain heuristics. Additionally the cache is fixed to store 128 values and will drop older results upon hitting this this limit.

!!! warning
    The app developer is responsible for ensuring that the function behaves correctly when cached and does not depend on its side-effects - for instance caching a function that sends an email on every invocation would result in incorrect and unexpected behavior.

```python
import time
import datapane as dp

# this function is cached when ever the same x and y values are seen
def calc(x: int, y: int):
    time.sleep(1)
    z = x+y
    return dp.BigNumber("Result", x+y)

blocks = dp.Blocks(
    dp.Form(
        on_submit=calc,
        controls=[dp.NumberBox('x', initial=2), dp.NumberBox('y', initial=3)],
        cache=True,
        label="Add values"
    )
)

dp.serve_app(blocks)
```

## Session State

It's often highly useful, and sometime necessary, to store and share _state_ between various function calls for a particular user.

Datapane supports this automatically via the concept of _user-sessions_. When a user first visits a Datapane App, Datapane creates a user-session that can be used to store any data that can be shared when running their backend functions.

To make use of this, simply add a parameter called `session` to your backend function definition. This parameter will automatically be populated with a mutable `dict` private to the user and stored on a per-user-session basis across all functions.

!!! note
    Using the `session` parameter on a function disables [Function Caching](#function-caching) as it makes the function stateful

In the example below, we use the `session` variable to accumulate and modify a variable across function calls.

```python
import datapane as dp

def calc(params: dict, session: dict):
    # read a value from the per user-session dict
    acc = session.get('acc', 0)
    result = params['x'] * params['y'] + acc
    # store back in the session
    session['acc'] = result
    return dp.BigNumber("Result", result)

blocks = dp.Blocks(
    dp.Form(
        on_submit=calc,
        controls=[dp.NumberBox('x', initial=2), dp.NumberBox('y', initial=3)],
        label="Multiply and accumulate values to state",
    )
)

dp.serve_app(blocks)
```
