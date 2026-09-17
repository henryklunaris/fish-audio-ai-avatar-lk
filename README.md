# Coral: an expressive AI video avatar

Coral is a realtime AI avatar you can talk to in the browser. Her voice is
[Fish Audio](https://fish.audio) S2.1 Pro with emotion tags, her face is a
[Tavus](https://tavus.io) avatar that lip-syncs to that voice, and the whole
pipeline runs on [LiveKit Agents](https://docs.livekit.io/agents) and LiveKit Cloud.

Say "whisper me a secret" or "I just got the job!" and watch the emotion badge
under the video change as Fish Audio performs it.

```
Browser (Next.js)  <-- WebRTC -->  LiveKit Cloud  <-->  agent (Python)
                                        ^                  |  STT + LLM + Fish Audio TTS
                                        |                  v
                                        +-------------  Tavus avatar worker (lip-sync video)
```

## What is in the repo

| Folder   | What                                                                  |
| -------- | --------------------------------------------------------------------- |
| `agent/` | Python agent (LiveKit Agents 1.8). Fish Audio TTS, expressive mode, Tavus avatar |
| `web/`   | Next.js frontend from `agent-starter-react`, branded, with a live mood badge |
| `docs/`  | LiveKit Cloud agents SOP (CLI cheatsheet, deploy, logs)               |

Both folders were scaffolded from LiveKit's official starters
(`agent-starter-python`, `agent-starter-react`) and then customised.

## Why Fish Audio

LiveKit's expressive mode tells the LLM which delivery tags the TTS understands.
With Fish Audio S2.1 Pro that means inline tags like `[whispering]`, `[excited]`,
`[laughing]` or `[sighing]` are written by the LLM, performed by Fish, and stripped
from the transcript. The frontend reads the resulting mood through the
`useAgentExpression` hook and shows it as a badge. See
[Fish Audio emotions](https://docs.fish.audio/developer-guide/core-features/emotions)
and [LiveKit expressive mode](https://docs.livekit.io/agents/models/tts/expressive/).

Fish Audio runs through LiveKit Inference, so you do not need a Fish API key.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) and Python 3.10+
- Node 24 and [pnpm](https://pnpm.io)
- [LiveKit CLI](https://docs.livekit.io/intro/basics/cli/) 2.17+ and a LiveKit Cloud project
- A [Tavus](https://platform.tavus.io) API key

## Setup

1. Log in and point the CLI at your project:

   ```bash
   lk cloud auth
   ```

2. Write LiveKit credentials into both apps:

Note: if you plan to only run in console mode only, you may skip this step, since step 1 authenticates for you with your LK credentials.

   ```bash
   cd agent && lk app env --write --destination .env.local && cd ..
   cd web && lk app env --write --destination .env.local && cd ..
   ```

   Note: if you plan to only run in console, you may skip this step.

3. Create a `.env` in the repo root (the agent loads it before `agent/.env.local`):

   ```
   TAVUS_API_KEY=your_tavus_key
   # optional
   TAVUS_FACE_ID=rc9cff32ceba   # stock or custom face, see below
   TAVUS_PAL_ID=             # echo-mode PAL with LiveKit transport, see below
   FISH_VOICE_ID=            # Fish Audio voice reference ID, default is "Sarah"
   AVATAR_ENABLED=true       # set to false for voice-only (console mode)
   ```

4. Add `AGENT_NAME=agent` to `web/.env.local` so the frontend dispatches this agent.

### Pick a Tavus face and PAL (optional)

Without these the plugin uses Tavus's stock PAL and face. To choose your own:

```bash
cd agent
uv run scripts/tavus_pal.py faces                 # lists stock face IDs
uv run scripts/tavus_pal.py create --face <id>    # creates an echo-mode PAL
```

Put the printed IDs in the root `.env` as `TAVUS_FACE_ID` and `TAVUS_PAL_ID`.

### Pick a Fish Audio voice (optional)

Browse the [Fish Audio voice library](https://fish.audio/app/discovery/), copy a
voice ID and set `FISH_VOICE_ID`. Ideally match the voice to the face you chose.

## Run it

Terminal 1, the agent:

```bash
cd agent
uv sync
uv run src/agent.py dev
```

Terminal 2, the web app:

```bash
cd web
pnpm install
pnpm dev
```

Open http://localhost:3000 and click "Talk to Coral". The avatar joins a few
seconds after you connect. You can also test the agent from the Agent Console in
the LiveKit Cloud dashboard.

Voice-only in the terminal (no Tavus minutes used):

```bash
AVATAR_ENABLED=false uv run src/agent.py console
```

## Tests

```bash
cd agent
uv run pytest                                     # in-process turn evals
lk agent simulate --scenarios scenarios.yaml      # full simulated conversations
```

## Deploy

Agent to LiveKit Cloud (from `agent/`):

```bash
lk agent create .                                 # first time
lk agent deploy --secrets-file ../.env            # updates, and pushes TAVUS_* secrets
```

Web app to Vercel: set `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` and
`AGENT_NAME=agent` as environment variables, then `vercel`. The included token
route is unauthenticated, so add auth before going public.

More CLI detail in `docs/livekit-cloud-agents-sop.md`.

## Swapping pieces

Every model is a string in `agent/src/agent.py`:

| Slot   | Current                          | Notes                                   |
| ------ | -------------------------------- | --------------------------------------- |
| STT    | `deepgram/nova-3`                | any LiveKit Inference STT               |
| LLM    | `google/gemma-4-31b-it`          | `openai/gpt-5.4` etc.                   |
| TTS    | `fishaudio/s2.1-pro`             | keep for expressive mode                |
| Avatar | Tavus                            | any [avatar plugin](https://docs.livekit.io/agents/models/avatar/) |

## License

MIT
