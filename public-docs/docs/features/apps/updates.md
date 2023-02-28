
Datapane automatically handles taking the results from your compute function and updating the user's view of the app. By default, the output of your functions will be inserted directly below where the compute block, i.e. a Form, in your app.

This works for most common cases, however you may want to specify this behavior - for instance you may want to add the results to the user's existing `Group` block, add a new `Page`, or even replace the `Form` itself. To accomplish this, Datapane compute blocks accept two arguments, `target=` and `swap=` that are used to specify how to update the View of your user's app with the results.

- `target` determines _which_ block to target to update with the new blocks
- `swap` indicates _how_ the targetted block will be updated with the new blocks

## Block Targetting

All blocks have an optional `name` property which is used for referencing and targetting. In the example below, the same value is used both as the block name and also assigned to the compute block's `target` parameter. This indicates to Datapane that the targetted block should be updated with the function result.

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
    the [dp.Empty][datapane.blocks.compute.Empty] block is provided as an empty placeholder for use as a target - it is not displayed on the screen and always requires a `name`. You can think of this like a HTML `<div/>`.

!!! note
    the `target` parameter can also be given a block object directly to use as the target


### Target modes

Instead of replacing other blocks, Datapane also provides `dp.TargetMode` as a helper to insert blocks around your app, or to replace the form itself.
When using `dp.TargetMode` you don't need to create empty blocks or think about block names, instead Datapane will automatically configure things to update as needed.

`dp.TargetMode` is used as follows:

```python
import datapane as dp

def f(params):
    first_name = params["first_name"]
    return dp.Text(f"Hello, {first_name}!")

app = dp.Blocks(
    dp.Form(on_submit=f, controls=dict(first_name=dp.TextBox()), target=dp.TargetMode.BELOW),
)

dp.serve_app(app)
```

#### Insert below (default)
Insert the result blocks directly below the form using `dp.TargetMode.BELOW`.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/below.png" style='width:50%'/>
</div>

#### Insert to the side

Insert the result blocks to right side of the form using `dp.TargetMode.SIDE`

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/side.png" style='width:50%'/>
</div>


#### Replace self

Replace the form itself using `dp.TargetMode.SELF`. This helpful for forms which should only be called a single time.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/self.png" style='width:50%'/>
</div>

## Block Swapping

In addition to choosing _where_ to insert your block, Datapane also provides helpers around _how_ to insert a block. This is more of an advanced feature only available on the `dp.Compute` block that is primarily useful when you are inserting blocks into a [layout block](../layout_blocks.ipynb) -- for instance, if you had a form which prepended/appended a result to a list upon each run.

This behavior is configured using the `dp.Swap` enum which is passed into a Compute block via the `swap` parameter. In the example below, every time the form is s`ubmitted, the results are prepended to the front of the previous data inside the 2-column `dp.Group` block.

```python
import datapane as dp

def f(params):
    first_name = params["first_name"]
    return dp.Text(f"Hello, {first_name}!")

app = dp.Blocks(
    dp.Compute(function=f, controls=dp.Controls(first_name=dp.TextBox()), target='my_grid', swap=dp.Swap.PREPEND),
    dp.Group(columns=2, name="my_grid")
)

dp.serve_app(app)
```

### Replace (default)

By default, Datapane will replace the target completely using `dp.Swap.REPLACE`.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/replace.png" style='width:50%'/>
</div>

### Prepend

`dp.Swap.PREPEND` allows you to insert a block as the first item in a layout block.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/prepend.png" style='width:50%'/>
</div>

### Append

`dp.Swap.APPEND` allows you to insert a block as the last item in a layout block.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/append.png" style='width:50%'/>
</div>

### Inner

`dp.Swap.Inner` allows you to insert a block _inside_ a layout block without replacing it. For instance, if you had a `Select` and wanted to replace its contents, but didn't want to delete the `Select` itself.

<div style='display: flex; justify-content:center'>
    <img src="/img/advanced/inner.png" style='width:50%'/>
</div>
