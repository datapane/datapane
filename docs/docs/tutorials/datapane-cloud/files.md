---
description: You can store common files and datasets on Datapane to use in your scripts.
---

# Files

{% hint style="success" %}
Please see the [File API Reference](https://datapane.github.io/datapane/teams.html#datapane.client.api.teams.Blob) for more details.
{% endhint %}

It is often necessary to make use of non-code assets such as datasets, models, or files when generating reports. In many situations, deploying these alongside your script is not ideal.

1. If they are deployed on a **different cadence** to your script; for instance, you want to make use of a model which is trained on a daily cadence, even though the code of your script remains static.
2. If they are deployed from a **different environment** than your script; for instance, you may train a model on Sagemaker and want to use it in your script.
3. If they are **large**, and re-uploading them each time you deploy your script is cumbersome.

For these use-cases, Datapane provides a File API which allows you to upload files from any Python or CLI environment, and access them inside your scripts or through the CLI. See the Python [API Docs](https://datapane.github.io/datapane/teams.html#datapane.client.api.teams.Blob) for more information on using Files.

{% hint style="info" %}
This feature is only available on Datapane Teams plans at present
{% endhint %}

## **CLI**

### `upload`

Upload a file and return an id and a url which you can use to retrieve the file.

```
datapane file upload <name> <filename> [--project project-name]
```

### `download`

Download a file and save it on your local machine.

```
datapane file download <name> <filename> [--project project-name]
```

## Python&#x20;

### `upload_df, upload_file, upload_obj`

#### Parameters

All upload methods take the object to upload as the first parameter. Depending on the method, this can be a file path, DataFrame, or a Python object.&#x20;

All methods have the additional parameters:

| Parameter | Description                | Required |
| --------- | -------------------------- | -------- |
| `name`    | The value of your variable | True     |

```python
import datapane as dp

# Upload a DataFrame
f = dp.File.upload_df(df, name='my_df')

# Upload a file
f = dp.File.upload_file("~/my_dataset.csv", name='my_ds')

# Upload an object
f = dp.File.upload_obj([1,2,3], name='my_list')
```

### `download_df, download_file, download_obj`

Download a DataFrame, file, or object. All download operations have the following parameters:

| Parameter | Description                         | Required |
| --------- | ----------------------------------- | -------- |
| `name`    | The name of your file               | True     |
| `project` | The project to upload the file to.  | False    |

{% hint style="warning" %}
If you want other people inside your organization to run your apps which access a file which you created, you must specify yourself as the `owner` in this method. When someone runs your app, it runs under their name, and if you do not set an explicitly specify the `owner` , it will try and look for the file under their name and fail.

```python
dp.File.get(name='foo', owner='john')
```
{% endhint %}

```python
import datapane as dp

# Download a DataFrame
file = dp.File.get(name="file_id")

# Download a DataFrame
f = file.download_df()

# Download a file
f = file.download_file("~/my_dataset.csv")

# Download an object
f = file.download_obj()
```

If your teammates within your private workspace want to access your file, they need to specifying the name of the file and project name(provided they are a member of that project) in `project`

```python
file = dp.File.get(name='myfile', owner='john')

# Retrieve file
f = file.download_df() # Or download_file(), download_obj()
```

Now others can use your file for their code!
