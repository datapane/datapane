import json
import os
from pathlib import Path

# import system datapane, not local file
import datapane as dp
from pytil.various import join_multiline

# import and run bundled file, and stdout
try:
    # relative should fail
    from . import dp_script

    exit(1)
except ImportError:
    import dp_script

print("ran script")
print(f"p2={dp.Params['p2']}")
print(f"{os.environ['ENV_VAR']}")
# data bundling, using __file__ and cwd lookup
c_txt = (Path(__file__).parent / "c.json").read_text()
c_txt_rel = Path("c.json").read_text()
assert c_txt == c_txt_rel
c_json = json.loads(c_txt)
print(c_json["HELLO"])
print("SAMPLE OUTPUT")
# DP Results & 3rd-party libs
if dp.Params["p3"]:
    t = f"""
hello
,
world!
"""
    dp.Result.set(join_multiline(t))
