"""API skeleton for the test-first catalog validation change."""


def validate_catalog(catalog, root):
    # Count-only baseline: intentionally does not yet reject invalid references.
    return len(catalog.get("capabilities", [])) if isinstance(catalog, dict) else 0
