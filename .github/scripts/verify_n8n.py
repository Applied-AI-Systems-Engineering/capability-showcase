"""Execute published synthetic n8n examples in disposable, network-disabled containers."""
import json
import pathlib
import subprocess
import tempfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
IMAGE = "n8nio/n8n:2.42.6"
CASES = [
    ("public-synthetic-record-lookup-filtering.json", "Validated volunteer lookup", "lookup"),
    ("public-synthetic-synthetic-lifecycle.json", "Validated synthetic-lifecycle", "lifecycle"),
    ("public-synthetic-guard-assertions-synthetic.json", "Existing guard assertions - synthetic state", "guards"),
]

def execution_json(output):
    decoder = json.JSONDecoder()
    for offset, char in enumerate(output):
        if char != "{":
            continue
        try:
            result, _ = decoder.raw_decode(output[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(result, dict) and "resultData" in result.get("data", {}):
            return result
    raise RuntimeError("No execution result returned")

def verify(result, node, case):
    data = result["data"]["resultData"]
    if data.get("error"):
        raise RuntimeError(data["error"])
    run = data["runData"][node][-1]
    items = [item["json"] for item in run["data"]["main"][0]]
    if case == "lookup":
        assert [item["ID"] for item in items] == ["S001", "S002"], items
    elif case == "lifecycle":
        assert len(items) == 1, items
        assert items[0]["preview"]["before"]["status"] == "available", items
        assert items[0]["receipt"]["row"]["ID"] == "S001", items
        assert items[0]["receipt"]["row"]["status"] == "busy", items
    else:
        assert len(items) == 1, items
        for key, expected in (("originalComponent", 13), ("volunteerSchema", 14)):
            assert items[0][key]["passed"] == expected, items
            assert items[0][key]["total"] == expected, items

def main():
    subprocess.run(["docker", "pull", IMAGE], check=True, timeout=300)
    for filename, final_node, case in CASES:
        workflow = json.loads((ROOT / "n8n" / "workflows" / filename).read_text())
        assert workflow["active"] is False
        assert all(node["type"] in ("n8n-nodes-base.manualTrigger", "n8n-nodes-base.code") for node in workflow["nodes"])
        assert all(not node.get("credentials") for node in workflow["nodes"])
        workflow["id"] = uuid.uuid4().hex[:16]
        for node in workflow["nodes"]:
            node["id"] = str(uuid.uuid4())
        with tempfile.TemporaryDirectory() as folder:
            pathlib.Path(folder).chmod(0o755)
            fixture = pathlib.Path(folder, "workflow.json")
            fixture.write_text(json.dumps(workflow))
            fixture.chmod(0o644)
            command = [
                "docker", "run", "--rm", "--network", "none",
                "--memory", "2g", "--cpus", "2",
                "--tmpfs", "/home/node/.n8n:uid=1000,gid=1000,mode=0700",
                "--mount", f"type=bind,source={folder},target=/fixture,readonly",
                "-e", "N8N_DIAGNOSTICS_ENABLED=false",
                "-e", "N8N_VERSION_NOTIFICATIONS_ENABLED=false",
                "-e", "N8N_TEMPLATES_ENABLED=false",
                "--entrypoint", "sh", IMAGE, "-c",
                f"n8n import:workflow --input=/fixture/workflow.json && n8n execute --id={workflow['id']} --rawOutput",
            ]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
            if completed.returncode:
                raise RuntimeError(completed.stdout + completed.stderr)
            verify(execution_json(completed.stdout), final_node, case)
            print(f"PASS {filename}: native execution and expected output; external network disabled")
    print("PASS: 3 synthetic workflows; guard totals 13 and 14. No provider integration tested.")

if __name__ == "__main__":
    main()
