"""Check the public capability catalog against source and workflow jobs."""
import json
from pathlib import Path, PurePosixPath

import yaml


def validate_catalog(catalog, root):
    root = Path(root).resolve()

    def fail(message):
        raise ValueError(message)

    def file_ref(value):
        if not isinstance(value, str) or not value or "\\" in value:
            fail("Reference must be a nonempty repository-relative POSIX path")
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or ":" in value:
            fail("Reference escapes repository: " + value)
        target = root.joinpath(*path.parts)
        if target.is_symlink() or not target.resolve().is_relative_to(root) or not target.is_file():
            fail("Missing or unsafe file reference: " + value)
        return target

    if not isinstance(catalog, dict) or type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1:
        fail("Expected existing catalog schema_version 1")
    entries = catalog.get("capabilities")
    if not isinstance(entries, list) or not entries:
        fail("capabilities must be a nonempty list")
    ids = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("Each capability must be an object")
        identity = entry.get("id")
        if not isinstance(identity, str) or not identity.strip() or identity in ids:
            fail("Capability id must be nonempty and unique")
        ids.add(identity)
        file_ref(entry.get("documentation"))
        sources = entry.get("source")
        if not isinstance(sources, list) or not sources:
            fail("Capability source must be a nonempty list")
        source_paths = [file_ref(source) for source in sources]
        if entry.get("status") == "disabled-templates":
            if entry.get("runtime_verified") is not False or "verification" in entry:
                fail("Disabled templates must remain explicitly runtime-unverified")
            for source in source_paths:
                workflow = json.loads(source.read_text(encoding="utf-8"))
                if not isinstance(workflow, dict) or workflow.get("active") is not False:
                    fail("Disabled template workflow must be explicitly inactive")
        else:
            verification = entry.get("verification")
            if not isinstance(verification, dict):
                fail("Runnable capability requires verification references")
            workflow = yaml.safe_load(file_ref(verification.get("workflow")).read_text(encoding="utf-8"))
            jobs = workflow.get("jobs") if isinstance(workflow, dict) else None
            if not isinstance(jobs, dict) or not jobs:
                fail("Referenced workflow has no jobs")
            names = {
                job.get("name", key) for key, job in jobs.items()
                if isinstance(job, dict) and isinstance(job.get("name", key), str)
            }
            name = verification.get("job")
            if not isinstance(name, str) or name not in names:
                fail("Referenced verification job does not exist")
    return len(entries)


def main():
    root = Path(__file__).resolve().parents[2]
    catalog = json.loads((root / "capabilities.json").read_text(encoding="utf-8"))
    count = validate_catalog(catalog, root)
    print(f"PASS: {count} capability entries; source/documentation/job references and disabled-template boundary checked")


if __name__ == "__main__":
    main()
