#!/usr/bin/env python3
"""Move the user's cv-tailor data in and out of a single zip (for sandboxes that reset, e.g. claude.ai).

Data home: $CV_TAILOR_HOME or ~/.cv-tailor (profile.json, lamaran.xlsx, rencana_belajar.md, config.json, history/).

Commands:
  data_bundle.py where               print the data home and the output folder to use
  data_bundle.py find                look for an uploaded data zip / profile in the usual upload folders
  data_bundle.py unpack FILE.zip     restore a data zip into the data home (backs up what's there)
  data_bundle.py pack OUT.zip        write the data home into a zip for the user to download
"""
import datetime as dt
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

UPLOAD_DIRS = [Path("/mnt/user-data/uploads"), Path("/mnt/data"), Path.cwd()]
CLAUDE_AI_OUTPUTS = Path("/mnt/user-data/outputs")
CHATGPT_DATA = Path("/mnt/data")  # ChatGPT Code Interpreter: uploads and downloadable files live here


def home():
    return Path(os.environ.get("CV_TAILOR_HOME", Path.home() / ".cv-tailor"))


def output_dir():
    cfg = home() / "config.json"
    if cfg.exists():
        out = json.loads(cfg.read_text(encoding="utf-8")).get("output_dir")
        if out:
            return Path(out).expanduser()
    if CLAUDE_AI_OUTPUTS.is_dir():
        return CLAUDE_AI_OUTPUTS
    if CHATGPT_DATA.is_dir():
        return CHATGPT_DATA
    return Path.cwd()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    h = home()
    if cmd == "where":
        print(f"data_home={h}")
        print(f"output_dir={output_dir()}")
        print(f"claude_ai={CLAUDE_AI_OUTPUTS.is_dir()}")
        print(f"profile_exists={(h / 'profile.json').exists()}")
    elif cmd == "find":
        hits = []
        for d in UPLOAD_DIRS:
            if d.is_dir():
                hits += sorted(d.glob("cv-tailor-data*.zip")) + sorted(d.glob("profile*.json")) + \
                        sorted(d.glob("lamaran*.xlsx"))
        print("\n".join(str(p) for p in hits) if hits else "none")
    elif cmd == "unpack":
        src = Path(sys.argv[2])
        if h.exists() and any(h.iterdir()):
            backup = h.with_name(h.name + "-backup-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
            shutil.copytree(h, backup)
            print(f"Existing data backed up to {backup}")
        h.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(src) as z:
            for name in z.namelist():
                target = (h / name).resolve()
                if not str(target).startswith(str(h.resolve())):
                    sys.exit(f"Refusing unsafe path in zip: {name}")
            z.extractall(h)
        cfg = h / "config.json"
        if cfg.exists():  # paths from another machine don't apply here
            data = json.loads(cfg.read_text(encoding="utf-8"))
            for k in ("output_dir", "tracker"):
                if k in data and not Path(data[k]).expanduser().parent.exists():
                    del data[k]
            cfg.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Restored into {h}: " + ", ".join(sorted(p.name for p in h.iterdir())))
    elif cmd == "pack":
        out = Path(sys.argv[2])
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(h.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(h))
            cfg = h / "config.json"
            tracker = json.loads(cfg.read_text(encoding="utf-8")).get("tracker") if cfg.exists() else None
            if tracker and Path(tracker).expanduser().is_file() and not (h / "lamaran.xlsx").exists():
                z.write(Path(tracker).expanduser(), "lamaran.xlsx")  # tracker kept outside the data home
        print(f"Packed {h} -> {out}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
