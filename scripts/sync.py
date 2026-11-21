#!/usr/bin/env python3
"""Sync selected upstream skills into plugins/<name>/skills and regenerate manifests.

Usage: python3 scripts/sync.py [--cache DIR]
Versions are bumped only for plugins whose content actually changed.
"""
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "sources.json").read_text())


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fetch(name, up, cache):
    dest = cache / name
    if (dest / ".git").exists():
        git("fetch", "--depth", "1", "origin", up["branch"], cwd=dest)
        git("reset", "--hard", "FETCH_HEAD", cwd=dest)
    else:
        git("clone", "--depth", "1", "--branch", up["branch"], up["repo"], str(dest))
    return dest, git("rev-parse", "HEAD", cwd=dest)


def remote_head(url, branch):
    try:
        out = git("ls-remote", url, branch)
        return out.split()[0] if out else None
    except Exception:
        return None


def tree_hash(path):
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(path)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def new_version():
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"1.{now:%Y%m%d}.{int(now.strftime('%H%M'))}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=None)
    a = ap.parse_args()
    cache = Path(a.cache) if a.cache else Path(tempfile.mkdtemp(prefix="skills-upstream-"))
    cache.mkdir(parents=True, exist_ok=True)

    repos = {n: fetch(n, u, cache) for n, u in CFG["upstreams"].items()}
    lock = {"upstreams": {n: {"repo": CFG["upstreams"][n]["repo"], "commit": c} for n, (_, c) in repos.items()}}
    market_plugins, changed, missing = [], [], []

    for pl in CFG["plugins"]:
        up = CFG["upstreams"][pl["upstream"]]
        src_root = repos[pl["upstream"]][0] / up["skills_dir"]
        pdir = ROOT / "plugins" / pl["name"]
        manifest = pdir / ".claude-plugin" / "plugin.json"
        old = json.loads(manifest.read_text()) if manifest.exists() else {}
        old_hash = tree_hash(pdir / "skills") if (pdir / "skills").exists() else None

        if (pdir / "skills").exists():
            shutil.rmtree(pdir / "skills")
        (pdir / "skills").mkdir(parents=True)
        present = []
        ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store")
        for entry in pl["skills"]:
            e = {"name": entry} if isinstance(entry, str) else entry
            s_name = e["name"]
            s_up = CFG["upstreams"][e.get("upstream", pl["upstream"])]
            s_repo = repos[e.get("upstream", pl["upstream"])][0]
            src = s_repo if s_up.get("layout") == "root-skill" else s_repo / s_up["skills_dir"] / s_name
            if not (src / "SKILL.md").exists():
                missing.append(f"{pl['name']}:{s_name}")
                continue
            shutil.copytree(src, pdir / "skills" / s_name, ignore=ignore)
            if e.get("upstream", pl["upstream"]) != pl["upstream"]:
                lic_f = s_repo / s_up["license_file"]
                if lic_f.exists():
                    shutil.copy(lic_f, pdir / "skills" / s_name / "UPSTREAM_LICENSE")
            present.append(s_name)
        lic = repos[pl["upstream"]][0] / up["license_file"]
        if lic.exists():
            shutil.copy(lic, pdir / "UPSTREAM_LICENSE")

        content_changed = tree_hash(pdir / "skills") != old_hash
        version = new_version() if (content_changed or "version" not in old) else old["version"]
        if content_changed:
            changed.append(pl["name"])
        upstream_url = up["repo"].removesuffix(".git")
        meta = {
            "name": pl["name"],
            "version": version,
            "description": pl["description"],
            "author": CFG["marketplace"]["owner"],
            "homepage": upstream_url,
            "license": up["license"],
            "keywords": pl.get("keywords", []),
        }
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
        market_plugins.append({
            "name": pl["name"],
            "source": f"./plugins/{pl['name']}",
            "description": pl["description"],
            "version": version,
            "category": "science",
            "keywords": pl.get("keywords", []),
        })
        lock[pl["name"]] = {"version": version, "skills": present}

    for ex in CFG.get("external_plugins", []):
        entry = {k: v for k, v in ex.items() if v is not None}
        market_plugins.append(entry)
        src = ex["source"]
        if src.get("source") == "github":
            lock.setdefault("external", {})[ex["name"]] = {
                "repo": src["repo"], "ref": src.get("ref"),
                "commit": src.get("sha") or remote_head(f"https://github.com/{src['repo']}.git", src.get("ref") or "HEAD"),
            }

    m = CFG["marketplace"]
    market = {
        "name": m["name"],
        "owner": m["owner"],
        "metadata": {"description": m["description"]},
        "plugins": market_plugins,
    }
    (ROOT / ".claude-plugin").mkdir(exist_ok=True)
    (ROOT / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "sources.lock.json").write_text(json.dumps(lock, indent=2) + "\n")

    print("changed plugins:", ", ".join(changed) or "none")
    if missing:
        print("WARNING: skills not found upstream (renamed/removed?):", ", ".join(missing), file=sys.stderr)


if __name__ == "__main__":
    main()
