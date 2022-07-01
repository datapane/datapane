---
description: >-
  Environment allows you to set environment variables and docker image to use
  when running apps.
---

# Environments & Variables

{% hint style="info" %}
Please see the [Environment API Reference](https://datapane.github.io/datapane/teams.html#datapane.client.api.teams.Variable) for more details. You can also create Environments directly from the Web interface.
{% endhint %}

## Overview

Apps often contain variables such as database keys and passwords, which you do not want embedding in your source code and visible to the outside world.&#x20;

In addition, you'll often want to include custom dependencies and packages outside those in our [default Docker image](configuration-and-dependencies.md#docker-dependencies).&#x20;

Datapane lets you specify your variables and Docker images through **Environments.**&#x20;

## Creating an environment

You can create a new environment from Python, the CLI or the web interface. Adding multiple versions of environments with the same name will create new versions.&#x20;

{% tabs %}
{% tab title="Python" %}
```python
import datapane as dp

dp.Environment.create(
    name="env1", 
    environment={"foo": "bar", "bat": "ball"}, 
    docker_image="image_name",
    project="project_name"
)
```
{% endtab %}

{% tab title="CLI" %}
```
$ datapane environment create env2 --environment foo=bar --docker-image image_name --project project_name
```
{% endtab %}
{% endtabs %}

#### Parameters

| Parameter      | Description                                             | Required |
| -------------- | ------------------------------------------------------- | -------- |
| `name`         | The name of your environment                            | True     |
| `environment`  | A dictionary of key:value pairs for your variables      | True     |
| `docker-image` | Your image name on DockerHub                            | False    |
| `project`      | Project this environment is part of (default is `home`) | False    |

## Loading an environment

To tell your app which environment and Docker image to use, specify the environment in your `datapane.yaml` file.&#x20;

{% code title="" %}
```yaml
environment: my-environment
```
{% endcode %}

To access variables inside your Python script, use `os.environ.get`as follows:&#x20;

```python
import datapane as dp
import os 

env = dp.Environment.get(name="my-environment", owner = "john")
var = os.environ.get("foo")
```

#### Get Parameters

| Parameter | Description                                                                                                                                                                                                    | Required |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `name`    | The name of your environment                                                                                                                                                                                   | True     |
| `project` | The project of the environment. This _defaults_ to the `home` or `shared` project if not found in `home`, so should be set explicitly if you want other people to run the app with an environment you created. | False    |

{% hint style="warning" %}
If you want other people inside your organisation to run your apps with an environment which you created, you should specify the `project` in this method. When someone runs your script, it will try and look for the environment in the default project and may fail.

```python
foo = dp.Environment.get(name='foo', project='project_name')
```
{% endhint %}
