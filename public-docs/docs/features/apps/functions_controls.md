## Writing backend functions

When you add an app-specific block, such as a Form, you pass it a backend function to run when it is triggered.

The function passed into an app block can be any Python function, including a `lambda` or nested inline function. The main requirements are that the function returns Datapane blocks. If the function is being called by a form, it must also take a params dict.

!!! tip "Jupyter Support"

    We recommend using Jupyter whilst building your app, as it makes it easy to debug interactively. You can build your function in one cell and call it from another with sample parameters. As they are normal Python functions, no magic is needed.

    Datapane will automatically display the result from the function below where you call it so you can interactively develop your functions and app piece-by-piece.

### Parameters

Each `dp.Form` function takes a `params` parameter which is a dictionary containing all the controls specified in the `controls` parameter to the compute block. For instance, if you have a Form with the following controls:

```python
dp.Form(
    on_submit=f,
    controls=[dp.TextBox(name='first_name')]
)
```

the `first_name` parameter would be accessible as follows:

```python
def f(params)
    first_name = params['first_name']
```

For convenience, you can specify several, or all, of the names of the `params` in the function definition and Datapane will automatically unpack them, e.g.

```python
def f(params, foo: str):
    # params will contain only `bar`
    return dp.Text(foo)

dp.Form(on_submit=f,
        controls=dict(foo=dp.TextBox(), bar=dp.NumberBox())
        )
```

### Returning Values

Datapane functions can return any [Datapane block](../display_blocks.ipynb) or [raw Python objects](../display_blocks.ipynb#automatic-conversion) that are supported by Datapane. You can return these directly, as a list, or return a layout or container block like `dp.Blocks` or `dp.Group` for a more advanced layout.

!!! tip
    You can even return compute blocks like `dp.Form` and `dp.Dynamic` from a function, allowing you to chain functions together that build more complex operations and interactive apps, such as wizards.


## Controls

Controls are used to define the specific parameters to present to the user for input, such as a `TextField`, a number `Range`, or even a `File` upload.

These parameters are collected from the user and passed by Datapane into the respective Python function when calling it. This way you can collect input from your user and your user can use your app interactively.

When the user submits the form, Datapane automatically handles uploading the user's input, validates it, converts it to the correct type, and provides initial values if none are given. From there, Datapane calls the Compute function with the params in the `params` dict as mentioned [above](#compute-functions).

When adding a Compute Block to your code, you pass in the collection of parameters that make up your contols via a `dp.Controls` object.

```python
dp.Form(on_submit=f,
        controls=dp.Controls(name=dp.TextBox(),
                             age=dp.Range(initial=30, min=0, max=100)))
```

### Built-in Parameters

Datapane comes with many parameters built-in to handle a wide variety of user inputs.
All these parameters accept some common options, including,

- `name` - the name given to the parameter when used in your compute function
- `initial` - the initial value used when displaying the parameter in your app
- `label` - a descriptive label used when displaying the parameter in your app

The built-in parameters include,

| Parameter   | Python Type  | Description               |
| ----------- | -------------|---------------------------|
| [Switch][datapane.blocks.parameters.Switch] | `bool` | A boolean toggle |
| [TextBox][datapane.blocks.parameters.TextBox] | `str` | A field to enter text |
| [NumberBox][datapane.blocks.parameters.NumberBox] | `double` | A field to enter numbers |
| [Range][datapane.blocks.parameters.Range]    | `double` | A slider to select a number from a range |
| [Choice][datapane.blocks.parameters.Choice] | `str` | Select an single choice from a set of options|
| [MultiChoice][datapane.blocks.parameters.MultiChoice] | `[str]` | Select multiple choices from a set of options |
| [Tags][datapane.blocks.parameters.Tags] | `[str]` | Create multiple string tags|
| [Date][datapane.blocks.parameters.Date] | `datetime.date` | Select a date |
| [Time][datapane.blocks.parameters.Time] | `datetime.time`| Select a time |
| [DateTime][datapane.blocks.parameters.DateTime] | `datetime.datetime` | Select a date and a time |
| [File][datapane.blocks.parameters.File] | `pathlib.Path`| Upload a file |

The [Controls API docs](../../reference/apps/controls.ipynb) also include detailed information and live samples of each parameter type.
