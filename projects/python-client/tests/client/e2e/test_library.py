import os
import subprocess
import sys


def test_arbitrary_arguments_from_cli():
    """Running the pytest command with arguments for -p
    to make sure Datapane doesn't process them."""
    test_file_path = os.path.realpath(__file__)
    test_command = [
        sys.executable,
        "-m",
        "pytest",
        test_file_path,
        "-k",
        "test_datapane_init_from_cli",
        "-p",
        "no:warnings",
    ]

    p = subprocess.run(test_command, capture_output=True)

    assert p.returncode == 0, str(p.stderr).replace("\\n", "\n")


def test_no_arguments_from_cli():
    """Running the pytest command without arguments for -p."""
    test_file_path = os.path.realpath(__file__)
    test_command = [
        sys.executable,
        "-m",
        "pytest",
        test_file_path,
        "-k",
        "test_datapane_init_from_cli",
    ]

    p = subprocess.run(test_command)

    assert p.returncode == 0


def test_datapane_init_from_cli():
    """This test is run by keyword expression from other CLI tests.
    It explicitly imports datapane to ensure __init__ is always executed."""
    import datapane as dp

    assert True
