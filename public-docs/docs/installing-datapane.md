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
