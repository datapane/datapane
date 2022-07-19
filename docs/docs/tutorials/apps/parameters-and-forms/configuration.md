# Configuration

Configuration for your Datapane Python script.

Inside your `datapane.yaml`, you can set the following fields.

## `app`

#### Value

A relative path.

#### Description

The path to your Python script or Jupyter Notebook which will be the basis of your script. Defaults to `dp_app.py`.

## `name`

#### Value

String (allowed characters are `[a-z0-9-_]`)

#### Description

The name of your script, which appears on the web UI.&#x20;

!!! info

    Deploying multiple scripts with the same name increments the version number automatically

## `pre_commands`

#### Value

A list of bash commands.

#### Description

A list of bash commands which will run before your script is executed. This is frequently used to do things like installing pip dependencies from a local folder deployed with `include`, or pull data from git.&#x20;

!!! info

    These will run each time your script runs, so could add some latency. For more complex dependencies, we recommend building a Docker container.

## `include`

#### Value

A list of relative paths or folders

#### Description

Local files or folders to include in your script. These will be available in the current working directory when your script runs, so can be used to upload local libraries, source files, SQL, etc.

!!! info

    For larger files and binary objects, we recommend using the Blob API

## `exclude`

#### Value

A list of relative paths or folders

#### Description

Files to explicitly exclude from the deployment (i.e. exceptions to the folders or files specified in `include`)

## `parameters`

#### Value

A list of objects

#### Description

A list of parameters which are turned into web forms and passed into your code at runtime. Comprised of a list of objects, i.e.

```yaml
parameters:
    - name: my_param
      type: string
      default: foo
```

For full documentation on parameters, please see the respective documentation:

[Parameters](/tutorials/apps/parameters-and-forms/parameters){ .md-button }

## `requirements`

#### Value

A list of pip-compliant packages

#### Description

A list of packages you want installed before your script runs. These can be anything that would normally be in a `requirements.txt`.&#x20;

!!! info

    These parameters are installed on each script run, so you if have many of them, this can cause a delay in execution. If you need to re-use the same parameters repeatedly, or have more complex requirements, we recommend adding your requirements to a Docker image and specifying with `container_image_name`

#### Value

A Docker URI

#### Description

A public docker image which your script will run in. For instructions on creating your image, please see the following tutorial.

[Configuration and dependencies](/tutorials/apps/configuration-and-dependencies){ .md-button }

## `repo`

#### Value

URL

#### Description

The URL of a repo or file on GitHub. This is displayed as a reference in the web UI, and does not affect the execution of your code.
