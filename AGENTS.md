# Repository instructions for coding agents

This repository contains selected public synthetic demonstrations. Begin with README.md and the affected component's scope instructions.

## Authority and data

Work only within the commissioned scope. Public source is not authority to connect providers, publish private artifacts, activate services or access resident systems. Never add credentials, private logs, local absolute paths or personal records. Do not change repository visibility, licensing, ownership, permissions or secrets without specific authorization.

## Changes and evidence

Use a focused branch and pull request for changes. Explain the behavior changed and its acceptance criteria. Run applicable checks; record checks not executed and failures accurately. Do not report fixtures as live inference, topology as integration, or a passing test as production readiness.

## Verification

LangGraph: install langgraph/requirements.txt in an isolated Python 3.12 environment, then run `python -m unittest discover -s langgraph -p 'test_*.py' -v`.

n8n: `python3 .github/scripts/verify_n8n.py` requires Docker and an image download. It executes the three manual synthetic workflows in disposable network-disabled containers. Do not substitute a resident n8n instance. The disabled topology templates remain unqualified for live use.

## Dependencies and release

Keep action references pinned to reviewed commits and execution images pinned to reviewed digests. Review dependency updates through checks and pull requests; do not enable automatic merging. Preserve third-party notices. No repository-wide open-source license is granted.
