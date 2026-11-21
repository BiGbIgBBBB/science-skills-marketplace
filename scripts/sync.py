#!/usr/bin/env python3
"""Sync selected upstream skills into plugins/<name>/skills and regenerate manifests.

Usage: python3 scripts/sync.py [--cache DIR] [--offline]

Two kinds of plugin are declared in sources.json:

* upstream plugins ("upstream": "<name>") - their skills/ directory is rebuilt on
  every run from the named upstream repository. Never edit those files by hand;
  the next sync overwrites them. Per-skill "exclude" globs drop bulky or
  irrelevant upstream files. An upstream normally keeps one directory per skill
  under "skills_dir"; a repository that is itself a single skill (SKILL.md at
  its root) declares "root_skill": "<skill name>" instead.
* local plugins ("local": true) - hand-written skills kept in this repository.
  The sync leaves their skills/ directory untouched and only refreshes the
  manifest and version.

A plugin's version is bumped only when the content of its skills/ directory
differs from the hash recorded in sources.lock.json.

--offline skips the upstream fetch and refreshes only local plugins and manifests.

Exit status: 0 on success; 3 when an upstream could not be fetched (its plugins
are left untouched, everything else is synced and safe to commit); anything else
is a crash and the working tree should not be committed.
"""
import argparse, datetime, fnmatch, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "sources.json").read_text())
LOCK_PATH = ROOT / "sources.lock.json"
ALWAYS_IGNORE = (".git", "__pycache__", "*.pyc", ".DS_Store")
EXIT_PARTIAL = 3  # the tree is consistent and safe to commit, but an upstream was unreachable


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fetch(name, up, cache, attempts=3):
    """Shallow-fetch one upstream. Retries transient network failures."""
    dest = cache / name
    for attempt in range(1, attempts + 1):
        try:
            if (dest / ".git").exists():
                git("remote", "set-url", "origin", up["repo"], cwd=dest)
                git("fetch", "--depth", "1", "origin", up["branch"], cwd=dest)
                git("reset", "--hard", "FETCH_HEAD", cwd=dest)
            else:
                shutil.rmtree(dest, ignore_errors=True)
                git("clone", "--depth", "1", "--branch", up["branch"], up["repo"], str(dest))
            return dest, git("rev-parse", "HEAD", cwd=dest)
        except subprocess.CalledProcessError as e:
            if attempt == attempts:
                raise RuntimeError((e.stderr or str(e)).strip().splitlines()[-1]) from e
            time.sleep(5 * attempt)


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


def copy_upstream_skills(pl, up, repo_dir, pdir, missing):
    """Rebuild pdir/skills from the upstream checkout.

    A skill that has disappeared upstream (renamed or removed) keeps its last
    synced copy and is reported, so an upstream reshuffle never silently deletes
    a skill that is installed and in use.
    """
    skills_dir = pdir / "skills"
    backup = None
    if skills_dir.exists():
        backup = Path(tempfile.mkdtemp(prefix="skills-prev-")) / "skills"
        shutil.move(str(skills_dir), str(backup))
    skills_dir.mkdir(parents=True)
    present = []
    excludes = pl.get("exclude", {})
    for s in pl["skills"]:
        src = repo_dir if up.get("root_skill") == s else repo_dir / up.get("skills_dir", "skills") / s
        if (src / "SKILL.md").exists():
            shutil.copytree(src, skills_dir / s, ignore=make_ignore(src, excludes.get(s, [])))
        elif backup is not None and (backup / s / "SKILL.md").exists():
            shutil.copytree(backup / s, skills_dir / s)
            missing.append(f"{pl['name']}:{s} (kept the last synced copy)")
        else:
            missing.append(f"{pl['name']}:{s} (no copy available)")
            continue
        present.append(s)
    if backup is not None:
        shutil.rmtree(backup.parent, ignore_errors=True)
    return present


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=None)
    ap.add_argument("--offline", action="store_true", help="do not fetch upstreams; refresh local plugins and manifests only")
    a = ap.parse_args()

    old_lock = json.loads(LOCK_PATH.read_text()) if LOCK_PATH.exists() else {}
    unreachable = {}
    if a.offline:
        repos = {}
        lock = {"upstreams": old_lock.get("upstreams", {})}
    else:
        cache = Path(a.cache) if a.cache else Path(tempfile.mkdtemp(prefix="skills-upstream-"))
        cache.mkdir(parents=True, exist_ok=True)
        repos, lock = {}, {"upstreams": {}}
        for n, u in CFG["upstreams"].items():
            try:
                repos[n] = fetch(n, u, cache)
                lock["upstreams"][n] = {"repo": u["repo"], "commit": repos[n][1]}
            except RuntimeError as e:
                # Leave this upstream's plugins exactly as they are and carry on with the others.
                unreachable[n] = str(e)
                if n in old_lock.get("upstreams", {}):
                    lock["upstreams"][n] = old_lock["upstreams"][n]
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
            if a.offline or pl["upstream"] in unreachable:
                present = prev.get("skills") or sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md"))
            else:
                repo_dir = repos[pl["upstream"]][0]
                present = copy_upstream_skills(pl, up, repo_dir, pdir, missing)
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
        msg = "skills not found upstream (renamed or removed?): " + ", ".join(missing)
        print("WARNING: " + msg, file=sys.stderr)
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::warning title=Upstream skill missing::{msg}")
    if unreachable:
        for n, why in unreachable.items():
            msg = f"upstream '{n}' could not be fetched, its plugins were left unchanged: {why}"
            print("ERROR: " + msg, file=sys.stderr)
            if os.environ.get("GITHUB_ACTIONS"):
                print(f"::error title=Upstream unreachable::{msg}")
        return EXIT_PARTIAL
    return 0


if __name__ == "__main__":
    sys.exit(main())
