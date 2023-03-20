Compute blocks, such as `dp.Form`, allow you to take parameters from end-users or update your app dynamically by triggering backend functions. When you add a Compute block, you specify a Python function which returns... you guessed it, blocks! The use of compute blocks require a running server, so won't they work in reports.

## Forms

Build forms using [dp.Form][datapane.blocks.compute.Form], which expose controls, such as textboxes, file uploads, and number ranges. When a user submits the form, it runs the backend Python function you have chosen, and automatically updates the user's display with the result.

This means you can calculate complex analytics on demand in response to user input and present the results directly to them - without leaving Python or writing any front-end code.

```python
import datapane as dp

def f(first_name: str):
    return dp.Text(f"Hello, {first_name}!")

view = dp.View(
    dp.Text("Welcome to my app"),
    dp.Form(on_submit=f,
            controls=dp.Controls(first_name=dp.TextBox()),
            label="Enter your name:"),
)

dp.serve_app(view)
```

You typically provide `dp.Form` with two parameters:

- The `controls` you would like the user to enter (e.g. a dropdown, a text input, a slider).
- A Python `function` which is run when the user submits the form.

This function is passed the form's controls as parameters and can return any (compatible) object that can be inserted into your app, like a Datapane block (such as [dp.Group][datapane.blocks.layout.Group]), or an object that Datapane knows how to display, e.g. a pandas DataFrame or a plot.

Optionally, you can also specify the `target` where you would like to insert the results of your function. When your function returns a block, Datapane will automatically place it in view, this `target` tells Datapane exactly where to [update the display](./updates.md).

## Dynamic blocks

[dp.Dynamic][datapane.blocks.compute.Dynamic] can trigger backend functions automatically, either when the block is loaded or on a timer. This allows you to create live dashboards, or refresh your app dynamically.

In the example below, the `on_load` parameter to `dp.Dynamic` - this instructs the app to automatically call the `get_time` function when the app is loaded and update the user's view with the result. As a result, the app always displays the correct time when it's loaded.

```python
from datetime import datetime
import datapane as dp

def get_time() -> str:
    return datetime.now().time().isoformat()

view = dp.View(
    dp.Text(f"This app was created at {get_time()},\n the app was loaded at..."),
    dp.Dynamic(on_load=get_time)
)

dp.serve_app(view)
```

`dp.Dynamic` also has an `on_timer` parameter which can be used to call a backend function on a regular schedule - see the [API docs][datapane.blocks.compute.Dynamic] for more information.

## The `dp.Compute` block

`Form` and `Dynamic` are Compute blocks that handle common interaction patterns in a simple way. If you require more control over how your app works and the types of interactions you want to support, we provide the [dp.Compute][datapane.blocks.compute.Compute] block.

!!! note
    Both `dp.Form` and `dp.Dynamic` are wrappers around the lower-level `dp.Compute` functionality and are recommended for basic app use-cases.

`dp.Compute` provides lower-level control of how your interactive app blocks behave and allows you to combine forms, triggers, and exposes advanced capabilities such as swapping

Please see the API docs for [dp.Compute][datapane.blocks.compute.Compute] for more information.
