
Datapane automatically handles taking the results from your compute function and updating the user's view of the app. By default, the output of your functions will be inserted directly below where the compute block, i.e. a Form, in your app.

This works for most common cases, however you may want to specify this behavior - for instance you may want to add the results to the user's existing `Group` block, add a new `Page`, or even replace the `Form` itself. Tio accomplish this, Datapane compute blocks accept two arguments, `target=` and `swap=` that are used to specify how to update the View of your user's app with the results.

Datapane inserts the blocks returned from a compute function into your current view - by default is the target another block and replace it,
- `target` determines which block it targets to update the function results
- `swap` indicates the how it will update the targetted block with the blocks returned from the function

## Block Targetting

All blocks have an optional `name` property which can be used by Datapane to reference and target them. In example below, we can see how the same value is used both as the block name, but also assigned to the compute block's `target` parameter - thus ensure that blocked targetted is updated with the results from calling the function.

```python
import datapane as dp

def f(params):
    first_name = params["first_name"]
    return dp.Text(f"Hello, {first_name}!")

app = dp.Blocks(
    dp.Form(on_submit=f,
            controls=dp.Controls(name=dp.TextBox()), target="replace_me"),
    dp.Text("This will be replaced", name='replace_me')
)

dp.serve_app(app)
```

!!! tip
    the `dp.Empty block is provided as an empty placeholder for use as a target - it is not displayed on the screen and always requires a name


### Target modes


Instead of replacing other blocks, Datapane also provides `dp.TargetMode` as a helper to insert blocks around your app, or to replace the form itself. `dp.TargetMode` is used as follows:

```python
import datapane as dp

def f(params):
    first_name = params["first_name"]
    return dp.Text(f"Hello, {first_name}!")

controls = dp.Controls(dp.TextBox("first_name"))

app = dp.Blocks(
    dp.Form(on_submit=f, controls=controls, target=dp.TargetMode.BELOW),
)

dp.serve_app(app)
```

#### Insert below (default)
Insert the block directly below the form using `dp.TargetMode.BELOW`.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/below.png" style='width:50%'/>
</div>

#### Insert to the side

Insert the block to right side of the form using `dp.TargetMode.SIDE`

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/side.png" style='width:50%'/>
</div>


#### Replace self

Replace the form itself using `dp.TargetMode.SELF`. This helpful for forms which should only be called a single time.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/self.png" style='width:50%'/>
</div>

## Swapping

In addition to choosing _where_ to insert your block, Datapane also provides helpers around _how_ to insert a block. This is primarily useful when you are inserting blocks into a layout block -- for instance, if you had a form which added an additional item to a list each time it is run.

You pass this property into your compute block using `dp.Swap`

```python
import datapane as dp

def f(params):
    first_name = params["first_name"]
    return dp.Text(f"Hello, {first_name}!")

controls = dp.Controls(dp.TextBox("first_name"))

app = dp.Blocks(
    dp.Form(on_submit=f, controls=controls, target='my_grid', swap=dp.Swap.APPEND),
    dp.Group(columns=2, name='my_grid")
)

dp.serve_app(app)
```

### Replace the block (default)

By default, Datapane will replace the target completely using `dp.Swap.REPLACE`.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/replace.png" style='width:50%'/>
</div>

### Prepend

`dp.Swap.Prepend` allows you to insert a block as the first item in a layout block.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/prepend.png" style='width:50%'/>
</div>

### Append

`dp.Swap.APPEND` allows you to insert a block as the last item in a layout block.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/append.png" style='width:50%'/>
</div>

### Inner

`dp.Swap.Inner` allows you to insert a block _inside_ a layout block without replace it. For instance, if you had a page and wanted to replace its contents, but didn't want to delete the page.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/inner.png" style='width:50%'/>
</div>
