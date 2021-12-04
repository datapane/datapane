import json
import os
from pathlib import Path

# import system datapane, not local file
import datapane as dp
from pytil.various import join_multiline

# import and run bundled file, and stdout
try:
    # relative should fail
    from . import dp_app

    exit(1)
except ImportError:
    import dp_app

print("ran app")
# check env values and params
assert os.environ['ENV_VAR'] == "env_value"
print(f"ENV_VAR={os.environ['ENV_VAR']}")
print(f"p2={dp.Params['p2']}")

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
