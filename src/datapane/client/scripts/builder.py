"""
Wrapper to build Python bundles using sdits and wheels for distribution
Derived from flit flit_core.sdist code
TODO
  - fork flit and extract out the include/exclude logic and wheel building
  - look at flit.sdist for vcs code
"""
# Portions of this code as taken from the flit project using the following license:
#
# Copyright (c) 2015, Thomas Kluyver and contributors
# All rights reserved.
#
# BSD 3-clause license:
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os.path as osp
import tarfile
import typing as t
from contextlib import contextmanager
from pathlib import Path

from flit_core.config import _check_glob_patterns
from flit_core.sdist import FilePatterns, SdistBuilder, clean_tarinfo

from datapane.common.utils import log, temp_fname

from .config import DatapaneCfg, extract_py_notebook


def preprocess_src_dir(dp_config: DatapaneCfg) -> Path:
    """Preprocess source-dir as needed"""
    old_mod = dp_config.proj_dir / dp_config.script

    # TODO - pass mod_code via classvar in dp_config
    if old_mod.suffix == ".ipynb":
        log.debug(f"Converting notebook {dp_config.script}")
        mod_code = extract_py_notebook(old_mod)

        # write the code to the new python module, avoiding basic name-clash
        new_mod = old_mod.with_suffix(".py")
        if new_mod.exists():
            new_mod = old_mod.with_name(f"_{old_mod.stem}.py")
        new_mod.write_text(mod_code, encoding="utf-8")

        dp_config.script = Path(new_mod.name)
        return new_mod


# Flit sdist builder wrapper
class Module:
    def __init__(self, file: Path):
        self.file = file.absolute()

    def iter_files(self):
        yield str(self.file)


DROP_DIRS_INIT = [".git", "__pycache__"]
DROP_DIRS = [f"{d}{osp.sep}" for d in DROP_DIRS_INIT]


class Bundler(SdistBuilder):
    def __init__(self, cfgdir: Path, module: Module, include_patterns=(), exclude_patterns=()):
        self.cfgdir = cfgdir
        self.module = module
        self.extra_files = []
        self.includes = FilePatterns(include_patterns, str(cfgdir))
        self.excludes = FilePatterns(exclude_patterns, str(cfgdir))

    # TODO - this should be handled by recursive globbing when added to flit
    def drop_unrequired_files(self, f: str) -> bool:
        return any((d in f for d in DROP_DIRS))

    def apply_includes_excludes(self, files) -> t.List[str]:
        """Modify upstream to drop files from hardcoded drop filters"""
        files = super().apply_includes_excludes(files)
        reduced_files = {f for f in files if not self.drop_unrequired_files(f)}

        if reduced_files != set(files):
            log.info("Found .git/__pycache__ files - ignoring for deployment")

        # assume already sorted?
        return sorted(reduced_files)

    def build(self, target: Path):
        with tarfile.TarFile.open(target, mode="w:gz", compresslevel=6, format=tarfile.PAX_FORMAT) as tf:
            files_to_add: t.List[str] = self.apply_includes_excludes(self.select_files())

            for relpath in files_to_add:
                path = osp.join(self.cfgdir, relpath)
                ti: tarfile.TarInfo = tf.gettarinfo(path, arcname=relpath)
                ti = clean_tarinfo(ti)
                if ti.isfile():
                    with open(path, "rb") as f:
                        tf.addfile(ti, f)
                else:
                    tf.addfile(ti)  # Symlinks & ?

        log.info(f"Built bundle: {target}")


@contextmanager
def build_bundle(dp_config: DatapaneCfg, use_git: bool = False) -> t.ContextManager[Path]:
    """
    Build a local sdist-bundle on the client for uploading
    currently requires version and docstring
    """
    proj_dir = dp_config.proj_dir
    # TODO - add git support
    incs = _check_glob_patterns(dp_config.include, "include")
    excs = _check_glob_patterns(dp_config.exclude, "exclude")

    with temp_fname(suffix=".tar.gz", prefix="datapane-temp-bundle-") as sdist_file:
        sdist_file_p = Path(sdist_file)
        temp_mod = preprocess_src_dir(dp_config)
        try:
            sb = Bundler(proj_dir, Module(dp_config.script), incs, excs)
            sb.build(sdist_file_p)
        finally:
            if temp_mod:
                temp_mod.unlink()
        log.debug(f"Generated sdist {sdist_file_p}")
        yield sdist_file_p
