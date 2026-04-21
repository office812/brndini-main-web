<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

<!-- BEGIN:stream-idle-prevention -->
# Prevent stream idle timeouts

The stream idle timeout error happens when no output is emitted for ~60s. Follow these rules to avoid it:

- **Avoid sub-agents** (the `Agent` tool) unless absolutely necessary. They are the #1 cause of idle timeouts because the parent stream goes silent while the child agent runs. Prefer direct `Grep`, `Glob`, and `Read` calls.
- **Any bash command expected to take more than 30 seconds** (builds, installs, tests, long `find`/`grep`) MUST be run with `run_in_background: true`, then polled.
- **Set short explicit timeouts** on bash commands (e.g. `timeout: 60000`) rather than relying on the default, so slow commands fail fast instead of stalling the stream.
- **Emit a one-sentence progress update between tool calls** — never go silent for long stretches. Short updates keep the stream alive.
- **Break large operations into small, visible steps.** Many small tool calls beat one giant one.
- **Keep thinking blocks short.** Don't stall between tool calls with extended internal reasoning.
- **Prefer narrow-scope searches.** Use `Grep`/`Glob` with specific paths/globs rather than scanning the whole tree.
<!-- END:stream-idle-prevention -->
