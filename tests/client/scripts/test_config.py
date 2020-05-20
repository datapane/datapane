from pathlib import Path

from datapane.client.scripts import config as sc


def test_extract_notebook(datadir: Path):
    converted_code = sc.extract_py_notebook(datadir / "sample.ipynb")
    expected_code = Path(datadir / "sample.py").read_text()
    assert converted_code == expected_code
    # check the mod docstring is present
    assert '"""Sample notebook"""' in converted_code


def test_config_yaml_py(datadir: Path, monkeypatch):
    # use dp_script.py by default
    monkeypatch.chdir(datadir)
    cfg = sc.DatapaneCfg.create_initial(config_file=Path("dp_script.py.yaml"))
    assert cfg.name == "dp_test_script"


def test_config_yaml_notebook(datadir: Path, monkeypatch):
    monkeypatch.chdir(datadir)
    script = Path("custom_datapane.ipynb")
    cfg = sc.DatapaneCfg.create_initial(config_file=Path("dp_script.ipynb.yaml"), script=script)
    assert cfg.script == script


def test_config_pyproject_py(datadir: Path):
    # TODO - NYI
    ...


def test_config_embedded_py(datadir: Path):
    # TODO - NYI
    ...
