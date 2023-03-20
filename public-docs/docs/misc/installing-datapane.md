---
description: Installing and setting up the Datapane library and API on your device
---

Datapane's Python library and CLI can be installed using either `pip` or `conda` on macOS, Windows, or Linux. Datapane supports Python **3.8 - 3.11**.

!!! info
    Instructions for installing Python can be found at [https://wiki.python.org/moin/BeginnersGuide/Download](https://wiki.python.org/moin/BeginnersGuide/Download).

    Additional install instructions can be found on the project [GitHub's page](https://github.com/datapane/datapane).

## pip

If you use `pip`, you can install it with:

=== "Shell"

    ```bash
    pip3 install -U datapane
    ```

=== "Jupyter"

    ```bash
    !pip3 install -U datapane
    ```

## conda

If you use `conda`, you can install it with:

=== "Shell"

    ```bash
    conda install -c conda-forge "datapane>=0.16.0"
    ```

=== "Jupyter"

    ```bash
    !conda install -c conda-forge "datapane>=0.16.0"
    ```

!!! warning
    Conda sometimes installs an older version of Datapane. If you receive errors, please check the version and try running `conda update --all` or try in a new conda environment (`conda create -n ENV` and `conda activate ENV`)

## Upgrading

We upgrade Datapane regularly to include new features, both in the client and on the hosted version. From time to time your client may no longer be compatible with the Datapane server when uploading an app. If this happens, you will receive an error like the following:

```
IncompatibleVersionError: Your client is out-of-date (version 0.9.2) and may be causing errors,
please upgrade to version 0.10.2
```

In such an event, please upgrade your Datapane cli via `pip` or `conda` and try again.

### Upgrading via pip

If you installed Datapane via pip, run the following command:

```bash
pip install -U datapane
```

### Upgrading via conda

If you installed `datapane` via conda, run the following command, adding the `--all` flag if needed. As above, if you receive errors please try using a fresh conda environment.

```bash
conda update datapane OR conda update --all
```

## Datapane Cloud

[Datapane Cloud](https://cloud.datapane.com) is a free and paid-for platform for hosting, sharing, and embedding reports, apps, functions and more securely.

Simply create your account, sign in, and add your API token to your local environment by running the following from the terminal or within Python respectively,

```bash
datapane login {TOKEN}
```

```python
import datapane as dp
dp.login({TOKEN})
```

Datapane Cloud comes with a generous free tier for individual use and public sharing, and paid plans for teams usage, permissions, authentication and more - see [here](https://datapane.com/pricing/)


## Analytics

By default, the Datapane Python library collects error reports and usage telemetry.
This is used by us to help make the product better and to fix bugs.
If you would like to disable this, simply create a file called `no_analytics` in your `datapane` config directory, e.g.

### Linux

```bash
$ mkdir -p ~/.config/datapane && touch ~/.config/datapane/no_analytics
```

### macOS

```bash
$ mkdir -p ~/Library/Application\ Support/datapane && touch ~/Library/Application\ Support/datapane/no_analytics
```

### Windows (PowerShell)

```powershell
PS> mkdir ~/AppData/Roaming/datapane -ea 0
PS> ni ~/AppData/Roaming/datapane/no_analytics -ea 0
```

You may need to try `~/AppData/Local` instead of `~/AppData/Roaming` on certain Windows configurations depending on the type of your user-account.


## Windows Tips and Troubleshooting

We generally recommend installing via `conda` over `pip` on Windows as it's easier to install all the required dependencies.

If you need to install Python first, the latest versions of Windows 10 can install Python for you automatically - running `python` from the command-prompt will take you to the Windows Store where you can download an [official version](https://docs.python.org/3/using/windows.html#the-microsoft-store-package).

We also strongly recommend using a 64-bit rather than the 32-bit version of Python, you can check this by running the following command from the Command Prompt,

```bash
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

Also note that on Windows, you can run the `datapane` command either by running `datapane` or `datapane.exe` on the command-line.

### Windows-specific Issues

#### Import errors when running/importing Datapane

You may encounter errors such as `ImportError: DLL load failed` when running Datapane or importing it within your Python code.

If so, try installing the [Visual C++ Redistributables for Windows](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads) from Microsoft and running again (you most likely want to download the version for x64, i.e. `vc_redist.x64.exe`)

#### Datapane install errors trying to compile `pyarrow` using Visual C++

This usually occurs when you are running a 32-bit version of Python and installing via `pip`. Either try using `conda` or install a 64-bit version of Python (for example from the Windows Store as mentioned above).

This may also occur when using Windows 7 - we only support directly Windows 10, however, it may be worth trying to install via `conda` instead, if you are stuck on Windows 7.

#### 'datapane.exe' is not recognized as an internal or external command

This occurs when your Windows `%PATH%` doesn't include all the Python directories, specifically the `Scripts` directory.

You may notice during the Datapane install messages such as (or similar to):

```
The script datapane.exe is installed in 'C:\users\<USERNAME>\appdata\local\programs\python\python37\Scripts' which is not on PATH.
Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
```

To fix this, adjust your `%PATH%` to include your specific `Scripts` path as mentioned in the `pip` warning (see [here](https://datatofish.com/add-python-to-windows-path/) for more detailed instructions). Alternatively, you can try running the Datapane client directly, using the command `python3.exe -m datapane.client` instead.

!!! info
    If you are still having problems installing, please ask on our [Datapane Discord server](https://chat.datapane.com)
