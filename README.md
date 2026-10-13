# Applied AI Systems Architecture & Engineering

[![Verify public capabilities](https://github.com/Khemology/capability-showcase/actions/workflows/verify.yml/badge.svg)](https://github.com/Khemology/capability-showcase/actions/workflows/verify.yml)

Selected demonstrations of validated workflows, stateful execution and tool integration. Each capability includes its execution instructions, evidence scope and current limitations.

Public examples use synthetic data and remain disconnected from private systems.

## Explore the capabilities

| Capability | Evidence and instructions | Current scope |
| --- | --- | --- |
| Validated state and conditional routing | [LangGraph examples](langgraph/README.md) | Two runnable local examples with deterministic tests |
| Record lookup, filtering and guarded state changes | [n8n execution and verification notes](n8n/verification/PUBLIC-RELEASE.md) | Invented records; disconnected demonstrations |
| MCP gateway and assistant topology | [n8n workflow files](n8n/workflows) | Disabled templates; live integration is not verified |

## Run and inspect

Start with the linked capability instructions. The LangGraph examples run offline after their public dependencies are installed. Their decisions use scripted fixtures, not live model inference. The n8n examples require an isolated instance; keep workflows inactive and do not attach provider credentials.

Tests and historical verification have specific scopes. Source files, hashes and passing fixture tests do not establish production deployment, autonomous reasoning or live provider integration.

## Development and release boundaries

- Public content consists of selected synthetic demonstrations and reviewed documentation.
- Release-eligible private development is separate from this public showcase.
- Permanently private products, credentials, runtime state and internal governance remain outside this repository.
- GitHub publication does not authorize access to private systems or bypass network isolation.

## Automated verification

[GitHub Actions](https://github.com/Khemology/capability-showcase/actions/workflows/verify.yml) runs the LangGraph deterministic tests and the three manual n8n demonstrations. n8n executes in disposable containers with external networking disabled and no provider credentials. The verifier checks lookup results, the synthetic state change, and the 13- and 14-assertion guard summaries. The two disabled topology templates remain outside runtime verification.

Dependency updates are proposed through pull requests for review. A passing workflow verifies these specific demonstrations; it does not certify private products or production integrations.

## Contributions and review

Use issues for reproducible problems or clearly scoped proposals. Proposed changes should identify the affected capability, intended behavior, verification and remaining limits. Never include credentials, personal records, private logs or internal system details in public issues or pull requests.

Third-party notices and component-specific scope statements apply. Public visibility does not grant an additional license; no repository-wide open-source license has been selected.
