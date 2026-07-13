# NOTES.md — decisions, things that broke, questions

> Running log for check-ins with Nick. Not a how-to (that's `Project-Cheatsheet.md`) — this is
> *why I made choices*, *what broke*, and *what I still need to ask*.

## Decisions (and why)

- **Dropped Anthropic, went to a free provider.** Per Nick's direction: build on the **OpenAI standard
  chat endpoint**, stay **provider-agnostic**, and don't eval Anthropic (already benchmarked). Also a
  lesson — Claude leaned toward Anthropic because it's made by Anthropic (bias to distrust).
- **First provider = Google Gemini**, now **switching to Groq** because Gemini's free tier kept failing.
- **`.env` variable named `GEMINI_API_KEY`.** The name is mine to choose; naming by provider scales when
  I add more providers later.
- **Using the `requests` library (not an official SDK).** I want to see the raw HTTP mechanics (headers,
  JSON body, status codes) — matches the spec and Nick. Can revisit later.
- **Pin exact model names** (e.g. `gemini-3.1-flash-lite`), not "latest" aliases, so eval runs are
  reproducible and I always know which model produced a score.

## Things that broke (and what I learned)

- **Mismatched quotes** in a command → terminal showed `dquote>`. Fix: Ctrl+C, redo with matching quotes.
- **`cat.env` → command not found.** Needed a space: `cat .env` (command and filename are separate words).
- **nano kept closing before saving** → `.env` ended up empty. Switched to `echo '...' > .env`, which
  writes and saves in one step.
- **`404` NOT_FOUND** — `gemini-2.5-flash` got deprecated. Lesson: model names retire fast; verify against
  the provider's live models page and pin a current one.
- **`503` UNAVAILABLE** — Gemini free tier "high demand" on every Flash variant. It's a *transient* error;
  Phase 4 (retry with backoff) is built to auto-handle exactly this. Decided to switch to Groq for reliability.

## Open questions for Nick

- OK to use **Groq** as my primary model given Gemini's free tier was too flaky?
- Which free providers do you want in my **comparison set** (Groq + Cerebras? + Gemini when it's up)?
- Confirm **`requests` vs official SDK** — I'm using `requests` on purpose to learn the mechanics.
- Any **spending or rate-limit constraints** I should design around?

## Deviations from the spec's tech defaults (spec said to record these)

- **Model provider:** Gemini/Groq instead of Anthropic — per Nick's redirection.
- **Talking to models via OpenAI-compatible endpoints** across providers (keeps the harness provider-agnostic).

## Progress

- ✅ Setup complete (git, venv, requirements, `.env`, key-loading test).
- 🔄 Phase 1 ~90%: first real API call worked ("Paris"); still need graceful error handling + a reliable
  provider, then commit.
- ⬜ Phase 2 next: questions from a file, scoring loop, percentage (write 15–20 of my own MCQs).
