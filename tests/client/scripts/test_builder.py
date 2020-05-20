import tarfile
import typing as t
from pathlib import Path

from datapane.client.scripts import DatapaneCfg, builder
from datapane.common.utils import setup_logging

# debug
setup_logging(verbose_mode=True)


def gen_build_cfg() -> DatapaneCfg:
    return DatapaneCfg(
        name="my_foo_module",
        script=Path("foo.py"),
        requirements=["requests >=2.6"],
        include=["bar.py", "config.yaml", "model.bin", "sub_pkg/"],
        exclude=["README.md", ".gitignore", "sub_pkg/ignore_me.py"],
    )


def _test_pkg_contents(files: t.List[str]):
    files_set = set(files)
    expected_files = {"foo.py", "bar.py", "config.yaml", "model.bin", "sub_pkg/woo.py"}
    ignored_files = {"README.md", "sub_pkg/ignore_me.py"}
    assert expected_files.issubset(files_set)
    assert ignored_files.isdisjoint(files_set)


def test_local_bundler(datadir: Path, monkeypatch):
    # TODO - add tests using git support when implemented
    assert datadir.exists()
    monkeypatch.chdir(datadir)

    # build sdist
    with builder.build_bundle(gen_build_cfg(), use_git=False) as sdist_file:
        # test for included/excluded files in sdist
        with tarfile.open(sdist_file) as tf:
            _test_pkg_contents(tf.getnames())
