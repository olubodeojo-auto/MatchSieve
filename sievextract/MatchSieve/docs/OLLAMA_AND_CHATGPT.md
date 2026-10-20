# Local AI, Claude and ChatGPT integration boundaries

## Ollama

The build can call a local Ollama instance at `http://127.0.0.1:11434/api/chat`. It does not need an OpenAI API key for local generation. In `.env`, set `OLLAMA_ENABLED=true` and set `OLLAMA_MODEL` to the exact model name shown by `ollama list`.

The deterministic Python layer calculates the actual metrics. Ollama only writes a plain-English commentary from a bounded structured JSON payload. If it is offline, the report still works without narrative. Any AI-written commentary remains draft text for review.

## Claude on the laptop

This build does not assume that Claude Desktop or Claude Code has a callable local API. A desktop application login is not the same as a developer API credential. Later, Claude can be linked through a documented MCP server or API if that suits the workflow, but that is separate from the existing local Ollama path.

## This ChatGPT conversation

A local folder cannot securely or automatically attach itself to this exact ChatGPT conversation just by placing a URL in a file. This directory therefore includes `docs/CHATGPT_HANDOFF.md` and a portable project context file. Upload that handoff or keep working in the same conversation to resume the work. If the repository is later connected through an available GitHub app, use it to inspect/modify repository content with explicit access.

## ChatGPT Apps / plugins

ChatGPT apps such as Metricool or Runway run in the ChatGPT app environment and require their own connection/authorization. They are not general Python libraries that this local app can invoke automatically. This project will create publish-ready copy/media queues and can later use a documented API or automation connector; it will not pretend that a ChatGPT plugin is connected from Python.

## Cost control

- Keep metrics and source facts in Python/SQLite.
- Use local retrieval to pass only relevant evidence to Ollama.
- Cache generated commentary by fixture, market and report version when the underlying evidence has not changed.
- Do not send a whole season or million-page corpus to the model.
- Keep paid cloud-model integrations as optional later providers, not dependencies.
