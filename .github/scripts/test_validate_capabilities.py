"""Regression checks for broken references and disabled-template claims."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import yaml
from validate_capabilities import validate_catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in ("example.py", "README.md"):
            (self.root / name).write_text("fixture", encoding="utf-8")
        (self.root / "template.json").write_text(json.dumps({"active": False}), encoding="utf-8")
        self.jobs = {"jobs": {"runtime": {"name": "Synthetic runtime", "steps": [{"run": "echo fixture"}]}}}
        self.catalog = {"schema_version": 1, "capabilities": [
            {"id": "example", "documentation": "README.md", "source": ["example.py"],
             "verification": {"workflow": "verify.yml", "job": "Synthetic runtime"}},
            {"id": "topology", "documentation": "README.md", "source": ["template.json"],
             "status": "disabled-templates", "runtime_verified": False},
        ]}

    def validate(self, catalog=None):
        (self.root / "verify.yml").write_text(yaml.safe_dump(self.jobs), encoding="utf-8")
        return validate_catalog(self.catalog if catalog is None else catalog, self.root)

    def test_valid_existing_shape(self):
        self.assertEqual(self.validate(), 2)

    def test_malformed_catalog(self):
        for value in ([], {}, {"schema_version": True, "capabilities": []},
                      {"schema_version": 1, "capabilities": [None]}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.validate(value)

    def test_missing_references(self):
        for field in ("documentation", "source", "workflow"):
            catalog = copy.deepcopy(self.catalog)
            entry = catalog["capabilities"][0]
            if field == "source":
                entry[field] = ["missing.py"]
            elif field == "workflow":
                entry["verification"][field] = "missing.yml"
            else:
                entry[field] = "missing.md"
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(catalog)

    def test_unsafe_and_malformed_paths(self):
        for value in (None, 7, "", "../outside.py", "/absolute.py", "C:/private.py", "..\\private.py"):
            catalog = copy.deepcopy(self.catalog)
            catalog["capabilities"][0]["source"] = [value]
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.validate(catalog)

    def test_missing_job(self):
        self.catalog["capabilities"][0]["verification"]["job"] = "Nonexistent runtime"
        with self.assertRaisesRegex(ValueError, "job does not exist"):
            self.validate()

    def test_missing_jobs_mapping(self):
        self.jobs = {}
        with self.assertRaisesRegex(ValueError, "no jobs"):
            self.validate()

    def test_duplicate_id(self):
        self.catalog["capabilities"][1]["id"] = "example"
        with self.assertRaisesRegex(ValueError, "unique"):
            self.validate()

    def test_disabled_template_cannot_claim_verification(self):
        for change in ({"runtime_verified": True}, {"runtime_verified": None},
                       {"verification": {"workflow": "verify.yml", "job": "Synthetic runtime"}}):
            catalog = copy.deepcopy(self.catalog)
            catalog["capabilities"][1].update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "runtime-unverified"):
                self.validate(catalog)

    def test_disabled_template_must_be_inactive(self):
        for value in ({"active": True}, {}, []):
            (self.root / "template.json").write_text(json.dumps(value), encoding="utf-8")
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "inactive"):
                self.validate()


if __name__ == "__main__":
    unittest.main()
