#!/usr/bin/env python3
"""Sync selected upstream skills into plugins/<name>/skills and regenerate manifests.

Usage: python3 scripts/sync.py [--cache DIR] [--offline]

Two kinds of plugin are declared in sources.json:

* upstream plugins ("upstream": "<name>") - their skills/ directory is rebuilt on
  every run from the named upstream repository. Never edit those files by hand;
  the next sync overwrites them. Per-skill "exclude" globs drop bulky or
  irrelevant upstream files.
* local plugins ("local": true) - hand-written skills kept in this repository.
  The sync leaves their skills/ directory untouched and only refreshes the
  manifest and version.

A plugin's version is bumped only when the content of its skills/ directory
differs from the hash recorded in sources.lock.json.

--offline skips the upstream fetch and refreshes only local plugins and manifests.
"""
import argparse, datetime, fnmatch, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "sources.json").read_text())
LOCK_PATH = ROOT / "sources.lock.json"
ALWAYS_IGNORE = (".git", "__pycache__", "*.pyc", ".DS_Store")


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


def tree_hash(path):
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            h.update(str(p.relative_to(path)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def new_version():
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"1.{now:%Y%m%d}.{int(now.strftime('%H%M'))}"


def make_ignore(skill_root, patterns):
    """Ignore callback for copytree: the fixed junk list plus per-skill globs.

    A pattern matches a path relative to the skill root, either exactly or as a
    glob ("assets/figures4papers", "tests", "references/*.R").
    """
    def ignore(directory, names):
        rel_dir = Path(directory).relative_to(skill_root)
        out = set()
        for n in names:
            rel = (rel_dir / n).as_posix()
            if any(fnmatch.fnmatch(n, pat) for pat in ALWAYS_IGNORE):
                out.add(n)
            elif any(fnmatch.fnmatch(rel, pat) for pat in patterns):
                out.add(n)
        return out
    return ignore


def copy_upstream_skills(pl, src_root, pdir, missing):
    skills_dir = pdir / "skills"
    if skills_dir.exists():
        shutil.rmtree(skills_dir)
    skills_dir.mkdir(parents=True)
    present = []
    excludes = pl.get("exclude", {})
    for s in pl["skills"]:
        src = src_root / s
        if not (src / "SKILL.md").exists():
            missing.append(f"{pl['name']}:{s}")
            continue
        shutil.copytree(src, skills_dir / s, ignore=make_ignore(src, excludes.get(s, [])))
        present.append(s)
    return present


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=None)
    ap.add_argument("--offline", action="store_true", help="do not fetch upstreams; refresh local plugins and manifests only")
    a = ap.parse_args()

    old_lock = json.loads(LOCK_PATH.read_text()) if LOCK_PATH.exists() else {}
    if a.offline:
        repos = {}
        lock = {"upstreams": old_lock.get("upstreams", {})}
    else:
        cache = Path(a.cache) if a.cache else Path(tempfile.mkdtemp(prefix="skills-upstream-"))
        cache.mkdir(parents=True, exist_ok=True)
        repos = {n: fetch(n, u, cache) for n, u in CFG["upstreams"].items()}
        lock = {"upstreams": {n: {"repo": CFG["upstreams"][n]["repo"], "commit": c} for n, (_, c) in repos.items()}}
    market_plugins, changed, missing = [], [], []
    owner = CFG["marketplace"]["owner"]

    for pl in CFG["plugins"]:
        pdir = ROOT / "plugins" / pl["name"]
        skills_dir = pdir / "skills"
        manifest = pdir / ".claude-plugin" / "plugin.json"
        old = json.loads(manifest.read_text()) if manifest.exists() else {}
        prev = old_lock.get(pl["name"], {})
        local = pl.get("local", False)

        if local:
            present = sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md"))
            homepage, license_ = owner.get("url", ""), pl.get("license", "MIT")
        else:
            up = CFG["upstreams"][pl["upstream"]]
            homepage, license_ = up["repo"].removesuffix(".git"), up["license"]
            if a.offline:
                present = prev.get("skills", [])
            else:
                repo_dir = repos[pl["upstream"]][0]
                present = copy_upstream_skills(pl, repo_dir / up["skills_dir"], pdir, missing)
                lic = repo_dir / up["license_file"]
                if lic.exists():
                    shutil.copy(lic, pdir / "UPSTREAM_LICENSE")

        digest = tree_hash(skills_dir) if skills_dir.exists() else ""
        content_changed = digest != prev.get("hash")
        version = new_version() if (content_changed or "version" not in old) else old["version"]
        if content_changed:
            changed.append(pl["name"])
        meta = {
            "name": pl["name"],
            "version": version,
            "description": pl["description"],
            "author": owner,
            "homepage": homepage,
            "license": license_,
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
        lock[pl["name"]] = {"version": version, "hash": digest, "skills": present}

    m = CFG["marketplace"]
    market = {
        "name": m["name"],
        "owner": m["owner"],
        "metadata": {"description": m["description"]},
        "plugins": market_plugins,
    }
    (ROOT / ".claude-plugin").mkdir(exist_ok=True)
    (ROOT / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market, indent=2, ensure_ascii=False) + "\n")
    LOCK_PATH.write_text(json.dumps(lock, indent=2) + "\n")

    print("changed plugins:", ", ".join(changed) or "none")
    if missing:
        print("WARNING: skills not found upstream (renamed/removed?):", ", ".join(missing), file=sys.stderr)


if __name__ == "__main__":
    main()
