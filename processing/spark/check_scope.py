"""Verify that current non-C3 tracked content matches the latest upstream main."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PREFIXES = ("docs/C3-data-processing/", "processing/spark/", "tests/processing/",
            "evidence/C3/", "data/aggregated/c3/")
INPUTS = ("data/synthetic/c3-table2.csv", "data/synthetic/c3-responses.csv")
ATTRIBUTES = ("data/synthetic/.gitattributes",)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def allowed(path):
    return path.startswith(PREFIXES) or path in INPUTS or path in ATTRIBUTES


def main():
    os.environ["GIT_TERMINAL_PROMPT"] = "0"
    os.environ["GCM_INTERACTIVE"] = "Never"
    baseline = git("rev-parse", "upstream/main")
    remote = git("ls-remote", "upstream", "refs/heads/main").split()[0]
    if remote != baseline:
        raise SystemExit("Upstream moved: fetch, inspect new paths and safely synchronize before continuing")
    subprocess.run(["git", "merge-base", "--is-ancestor", baseline, "HEAD"], cwd=ROOT, check=True)
    changed = git("diff", "--name-only", baseline).splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    disallowed = [p for p in changed + untracked if not allowed(p)]
    if disallowed:
        raise SystemExit("Out-of-scope changes: " + ", ".join(disallowed))
    subprocess.run(["git", "diff", "--check", baseline], cwd=ROOT, check=True)
    protected = [p for p in git("ls-tree", "-r", "--name-only", baseline).splitlines() if not allowed(p)]
    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_upstream_main": baseline,
        "live_remote_main": remote,
        "latest_upstream_main_included": True,
        "sync_method": "fast-forward only from clean member3; prior A3 already merged upstream",
        "protected_tracked_file_count": len(protected),
        "protected_paths_equal_upstream_main": True,
        "out_of_scope_changes": disallowed,
        "allowed_changed_or_new_paths": sorted(set(changed + untracked + ["evidence/C3/sync-check.json"])),
        "allowed_prefixes": list(PREFIXES), "allowed_input_files": list(INPUTS),
        "allowed_attributes_files": list(ATTRIBUTES),
        "untouched_shared_files": ["README.md", "coordination/interfaces.md", "coordination/tasks.md", "references/sources.csv"],
        "publication": "Only own Fork/member3 is an intended push target; no original-main merge performed",
    }
    path = ROOT / "evidence/C3/sync-check.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: latest upstream main {baseline[:7]}; {len(protected)} protected tracked files unchanged; C3-only changes")


if __name__ == "__main__":
    main()
