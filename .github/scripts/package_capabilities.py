"""Package only the public demonstration selection after verification."""
import hashlib
import json
import os
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[2]
paths = [root / name for name in ("README.md", "AGENTS.md", "SECURITY.md", "capabilities.json")]
for folder in ("langgraph", "n8n"):
    paths.extend(path for path in (root / folder).rglob("*") if path.is_file() and path.suffix in (".py", ".json", ".md", ".txt"))
paths.extend(root / name for name in (
    ".github/workflows/verify.yml",
    ".github/scripts/verify_n8n.py",
    ".github/scripts/package_capabilities.py",
    ".github/scripts/validate_capabilities.py",
    ".github/scripts/test_validate_capabilities.py",
))
paths = sorted(set(paths))
if any(path.is_symlink() for path in paths):
    raise RuntimeError("Symlinks are excluded from distribution")
manifest = {
    "source_commit": os.environ["GITHUB_SHA"],
    "workflow_run": os.environ["GITHUB_RUN_ID"],
    "scope": "Public synthetic demonstrations; no provider integration or live inference certified",
    "files": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
}
out = Path(os.environ["RUNNER_TEMP"]) / "capability-distribution"
out.mkdir()
archive = out / "capability-showcase.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for path in paths:
        bundle.write(path, path.relative_to(root))
    bundle.writestr("verification-manifest.json", json.dumps(manifest, indent=2))
(out / "SHA256SUMS").write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + "  capability-showcase.zip\n")
(out / "verification-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    for path, digest in manifest["files"].items():
        assert hashlib.sha256(bundle.read(path)).hexdigest() == digest
print(f"Verified distribution: {len(paths)} selected files; commit {manifest['source_commit']}")
