# Disconnected synthetic n8n examples

These locally authored examples use invented volunteer records. Import the five workflow JSON files into an isolated n8n instance and keep every workflow inactive. Do not connect provider credentials for these demonstrations.

This document covers the reviewed n8n selection under n8n/. Separately published LangGraph examples are documented in [their own scope and execution instructions](../../langgraph/README.md); the n8n verification described here does not establish their results.

Run the manual trigger in Record Lookup and Update Demo: record S001 changes from available to busy inside that execution. Run the labelled invented lookup fixture in Record Lookup and Filtering: the independently authored Code component validates the nine-column schema and performs case-sensitive contains lookup, returning S001 and S002 for Full Name containing Alex. Run the manual guard workflow: the original schema passes 13 assertions and the nine-column volunteer schema passes 14 assertions.

The spreadsheet MCP gateway and volunteer lookup assistant are disabled topology templates. Their provider selections and workflow references are blank. They are expected to refuse CLI execution because no enabled start node exists. They require additional authorized configuration and integrated testing before use.

The demos were imported and executed with n8n 2.42.6 in an isolated container with outbound networking disabled. The standalone JavaScript component and native workflow tests have distinct scopes. Fixture authority objects do not authenticate Slack users; a listener flag does not verify a production MCP listener. In-memory receipts do not establish durable replay prevention or provider writes. No Sheets, OpenAI or Slack integration was tested.

CLI verification assigned temporary workflow and node identities and a temporary name prefix. Final graphs matched imported graphs after removing only those test identities. Editor imports can assign new identities automatically.

See [public-synthetic-NOTICE.md](../workflows/public-synthetic-NOTICE.md) for scope and usage limits. The release review classifies only these original demonstrations, invented fixtures and instructions. It does not authorize releasing other project files.

An exact staged tree is insufficient for publication by itself. Required release gates include a governed redacted Gitleaks scan of that exact tree, independent release review and confirmed repository placement. After a separately authorized push, compare the remote tree with the approved staged file hashes. Raw execution logs and development materials remain private.
