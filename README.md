# ASTA_AI

ASTA_AI is a learning project for building a small AI from the ground up with Python.

## What it can do now

- Learn simple logic patterns with a small neural network.
- Classify short messages as greetings, questions, thanks, or farewells.
- Select a prepared reply for a recognized message.
- Learn word-to-word patterns from editable training text and generate experimental phrases.
- Teach Python concepts using an editable lesson dataset, example code, explanations, and exercises.
- Match coding questions to relevant lessons and check that lesson examples are valid Python syntax.

**Important limitations:** the chatbot still chooses prepared replies. The phrase generator is a simple word n-gram model, not a ChatGPT-like language model. The coding tutor is example-based: it searches lessons written by a human and presents them. It does not independently understand all programming questions, execute code, or verify that a program behaves correctly.

## Train on GitHub

1. Open the Actions tab.
2. Select **ASTA_AI - Train and Test**.
3. Choose **Run workflow**. Automatic runs on pushes are disabled while development continues.
4. Open the completed run and download the `asta-ai-trained-model` artifact.

The workflow runs tests, trains the logic and intent models, trains the phrase generator, validates the Python lesson examples, and packages generated JSON model files. Workflow artifacts are downloadable outputs; they are not automatically saved back into the repository.

## Teach the chatbot

Edit `datasets/text_training_data.json`.

- Add phrases inside `intents` to teach it which category a message belongs to.
- Add reply choices inside `responses` under the matching category.
- Keep the JSON valid, and add several varied examples for each category.

## Teach the phrase generator

Edit `datasets/conversation_text.txt`. Add original example sentences, preferably one sentence per line, on topics you want it to imitate.

Run:

~~~bash
python brain/text_generator.py
~~~

It saves `models/asta_text_generator.json` and prints sample phrases. This small order-2 model learns neighboring-word patterns; it may produce repetitive or nonsensical text.

## Teach ASTA_AI to code in Python

Edit `datasets/python_lessons.json`. Each lesson contains:
- `title` and `keywords` for finding the topic.
- `explanation` describing the programming concept.
- `code` with a Python example.
- `exercise` for practice.
- `answer` with a sample solution.

Add more lessons using the same structure. The trainer parses each example with Python's AST parser to catch syntax errors. **It never executes the lesson code.**

On a computer with Python 3.11 or newer, start the tutor:

~~~bash
python brain/code_tutor.py
~~~

Ask questions such as `how do loops work?`, `teach me functions`, or `how do I use lists?`. ASTA_AI shows a matching explanation, example, and practice task. It asks before showing the sample answer.

Validate the lesson dataset and save its searchable index:

~~~bash
python brain/code_trainer.py
~~~

Run all automated tests:

~~~bash
python -m unittest discover -s tests -v
~~~

## Try the chatbot on a computer

~~~bash
python brain/text_trainer.py
python brain/chat.py
~~~

Type `quit` to end the chat. This chat loop uses the intent model and prepared replies; it does not yet use the phrase generator as its reply engine.

## Android

GitHub Actions can run the training workflow from your phone's browser, but it is not itself an Android chat or coding-tutor app. An Android interface is a later project step.

## Project layout

- `brain/` — neural network, text classifier, phrase generator, Python coding tutor, and trainers.
- `datasets/` — chatbot examples, phrase-generator text, and Python lessons.
- `tests/` — automated checks.
- `.github/workflows/` — GitHub Actions training and validation workflow.
- `models/` — generated model files, available as workflow artifacts.

## Next steps

The next serious step toward coding ability is a neural model trained on many carefully selected code examples, followed by evaluation and a safe code-execution sandbox. More lessons alone improve this tutor's coverage, but do not turn it into an autonomous programmer.


## Python code-pattern learner

ASTA_AI can inspect Python source without executing it. The pattern learner recognizes
common structures such as loops, conditions, functions, lists, dictionaries and function
calls, then retrieves examples with similar syntax structures.

Run it on a computer:

```bash
python brain/code_pattern_trainer.py
python -m unittest discover -s tests -v
```

The example library is editable at `datasets/python_code_examples.json`.
This is static syntax analysis and example matching, not an autonomous code-writing
model. It does not execute submitted code or guarantee that a program works.


## General neural language model (first experimental version)

ASTA_AI now includes a small next-word neural model written in plain Python.
It learns token embeddings and predicts a likely next token using a hidden layer
and a softmax output. The starter corpus is in
`datasets/general_learning_text.txt`; add original, appropriate example text there
to change what it learns.

Train it with:

```bash
python brain/language_trainer.py
```

The model is deliberately small and educational. It has a tiny vocabulary and training
corpus, so its generated text may repeat words or be inaccurate. It is not yet a
reliable general assistant or comparable to a large language model. The model predicts
text patterns; it does not independently verify facts or understand intentions.

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## Personalization and phone controls: design principles

Future memory and habit features must be opt-in, visible, editable, and deletable.
ASTA_AI should only learn from information the user chooses to provide or explicitly
allow it to access. Phone actions should use Android permissions and an allowlist;
sensitive actions such as sending messages, sharing data, or making purchases require
a clear confirmation. The current Python project does not yet control an Android phone.


## Decision support engine (first version)

ASTA_AI includes a transparent weighted decision engine in `brain/decision_engine.py`.
It can rank options using 1-5 scores and priorities supplied by the user, identify
strong and weak areas, and explain the ranking. It does not independently verify
the scores, make high-stakes decisions, or take action on the user's behalf.

Run its tests with:

```bash
python -m unittest discover -s tests -v
```

## Internet research without a paid search API

ASTA_AI has a best-effort public web-search connector in `brain/web_research.py`.
It requests DuckDuckGo's public HTML search page using Python's standard library.
No Tavily key or extra Python package is required.

Run on a computer or supported Python environment:

```bash
python brain/research_cli.py "latest developments in renewable energy"
```

This is not guaranteed uptime: search providers can change page markup, block automated
requests, or rate-limit traffic. Search snippets may be incomplete or stale. ASTA_AI
must show source links, compare original pages, and treat page content as untrusted data.
The connector is not yet integrated into an Android app or general chat engine.

## Adaptive interface foundation

This repository is currently a Python backend and command-line prototype, not a finished
Android application. The adaptive UI module defines task modes and layout hints that an
Android frontend can use to switch workspaces (chat, coding, research, analysis, and
planning) based on the user's request. Actual on-screen changes require connecting this
contract to the Android UI.

GitHub Actions is paused for now. The workflow can only be started manually from the
Actions tab; it will not run automatically on pushes or pull requests.


## Unified assistant core (first orchestration version)

The unified entry point is `brain/assistant_core.py`. It routes requests to the
adaptive workspace selector, Python lesson retrieval, and keyless public web search.
It returns a structured result containing the workspace, answer, sources, and action.
The command-line demo is `python brain/assistant_cli.py`.

Memory is opt-in and local: only messages beginning with `remember that` or
`remember:` are saved to `models/user_memory.json`. Use `show memory`,
`forget: exact memory text`, or `forget all memories` to inspect or delete it.
ASTA_AI does not silently collect chat history or habits.

This is a first orchestration layer, not a ChatGPT-level model. General open-ended
conversation remains limited, web search depends on the public search provider, and
the adaptive workspace metadata still needs a real Android frontend to render it.


## Optional general language-model connection

The unified assistant can now call an external chat model through
`brain/language_engine.py`. This adds open-ended language generation while
keeping ASTA's existing Python lessons, research routing, decision tools, and
explicit memory commands.

**No model is bundled with this repository.** The language adapter is a connector,
not a trained foundation model. Its quality depends on the model you install or
connect. The assistant sends the current request, up to four recent conversation
turns, and explicitly saved notes to the configured model. Do not save passwords,
private keys, or other secrets in ASTA memory.

### Option A: local Ollama server (no hosted API key)

1. Install Ollama on a computer that can run a model, then download a chat model
   supported by your computer.
2. Start the Ollama server and make sure the model is available locally.
3. Set these environment variables in the environment where ASTA_AI runs:

```bash
ASTA_LLM_PROVIDER=ollama
ASTA_LLM_BASE_URL=http://127.0.0.1:11434
ASTA_LLM_MODEL=your-installed-model-name
python brain/assistant_cli.py
```

Replace `your-installed-model-name` with the exact model name shown by Ollama.
If ASTA runs on a different device from the Ollama server, use the server
computer's reachable LAN address instead of `127.0.0.1`, and only expose the
server on a trusted network.

### Option B: hosted OpenAI-compatible service

Set `ASTA_LLM_PROVIDER=openai`, `ASTA_LLM_BASE_URL` to the provider's API base,
`ASTA_LLM_MODEL` to a model name supported by that provider, and
`ASTA_LLM_API_KEY` in a private environment variable or secret store.
Never commit an API key to this repository or paste it into chat. Hosted model
usage may cost money according to the provider's pricing.

### Important limitations

- If no provider is configured, ASTA keeps using its existing local tools and
  clearly reports that a general language model is not connected.
- Local Ollama inference needs a separate computer/server with enough memory and
  processing power for the chosen model. A GitHub repository or GitHub Actions
  workflow does not host the model for the Android phone.
- This repository is still a Python command-line prototype, not an Android app.
  The model adapter must later be connected to an Android frontend through a
  secure backend or a supported on-device inference runtime.
- Model answers can be wrong. Verify important facts, especially changing
  information. The web research tool remains a separate explicit tool.
- The adapter does not train or modify the model weights. Personalization memory
  and model training are different things.


## Android chat application (first client)

A native Kotlin + Jetpack Compose Android client is in `android/`. It provides
a dark chat screen, connection settings, message bubbles, and sends messages to
the Python assistant API. The access token field is masked and is held only in
the app's current session; it is not written to disk.

### Run the ASTA API server

On a trusted server with Python 3.11+, configure a private random token and the
language model provider. For example, with Ollama running on the same server:

```bash
export ASTA_API_TOKEN="replace-with-a-long-random-secret"
export ASTA_LLM_PROVIDER=ollama
export ASTA_LLM_BASE_URL=http://127.0.0.1:11434
export ASTA_LLM_MODEL="your-installed-model-name"
python brain/api_server.py
```

The API listens on `127.0.0.1:8765` by default. Put it behind a trusted HTTPS
reverse proxy before connecting from Android. Do not expose the Python HTTP
server directly to the public internet. The Android client intentionally refuses
plain HTTP addresses and sends the token as a bearer credential. Keep the token
private and rotate it if it is exposed.

The API's `/health` endpoint checks whether the server process is running.
The `/api/chat` endpoint requires the bearer token. A language model must be
configured on the server for open-ended answers; otherwise ASTA uses its local
features and explains that no general model is connected.

### Build the Android APK

The separate workflow `ASTA Android APK` is manual-only. When ready, open GitHub
Actions, select that workflow, and choose **Run workflow**. Download the
`ASTA-Android-debug` artifact from the completed run. The existing training
workflow remains manual-only too.

**Current status:** this is an initial Android chat client and authenticated API,
not a published app. The API still needs deployment to a server with HTTPS, and
a language model must be installed/configured there. The app does not yet have
voice input, image uploads, background phone controls, or persistent on-device
chat history.


## Intelligence development — phase 1

The first intelligence-development branch adds a transparent request-analysis
module in `brain/reasoning_engine.py`. It extracts constraints actually stated
by the user, identifies missing information, and produces a checklist-style plan
with verification steps. It does not claim to be deep reasoning or a trained
foundation model.

The assistant routes planning and analysis requests through this module and
returns the structured result alongside the normal answer. The Android client
now reads the returned workspace title and displays an active-workspace panel,
so the backend's adaptive workspace selection is visible in the app.

New tests cover constraint extraction, missing details, formatting, and the
assistant's planning route. GitHub Actions workflows remain manual-only:
`workflow_dispatch` is the only trigger. No build or training workflow was
started as part of this change.

### Remaining work

- Run the Python test suite and Android debug build before merging this branch.
- Connect a language model runtime before expecting fluent, open-ended answers.
- Add durable server-side storage before relying on memory across restarts.
- Add richer workspace-specific Android components, voice, image input, and
  permission-gated phone integrations in later phases.


## Intelligence development — phase 2: memory and explicit learning

ASTA now has two separate user-controlled stores:

- **Memory** saves preferences and facts only after an explicit `remember that ...` or `remember: ...` command.
- **Approved learning examples** are saved only after an explicit `teach ASTA: ...` command. These examples are supplied as context to a configured language model when relevant; they do not update or retrain model weights.

Useful chat commands:

- `show memory` — list saved memory.
- `forget: exact memory text` — remove one exact memory.
- `forget all memories` — clear saved memory.
- `teach ASTA: ...` — add a user-approved teaching example.
- `show lessons` — list approved teaching examples.
- `forget lesson: exact example text` — remove one example.
- `clear learning` — clear all approved teaching examples.

Both stores use readable JSON and atomic file replacement. The API accepts configurable paths:

```bash
export ASTA_MEMORY_PATH=/var/lib/asta/user_memory.json
export ASTA_LEARNING_PATH=/var/lib/asta/approved_learning.json
python brain/api_server.py
```

**Deployment warning:** setting a path does not create durable storage by itself. The directory must be on a persistent disk/volume provided by the hosting platform, with write permission for the ASTA process. If the host uses an ephemeral filesystem, data can still disappear when the service is replaced. Back up these files securely and never store passwords, API keys, or highly sensitive information in memory.

The authenticated API now exposes `GET /api/memory` to retrieve the two user-controlled lists. It requires the same bearer token as chat. The Android screen has not yet been updated with a dedicated memory manager; commands can be used in chat for now.

### Learning limitations

ASTA does not silently study all conversations or users' habits. The teaching store is an approved-example library, not autonomous model training. A connected language model can use those examples as context; without a configured model, they are saved but do not make the deterministic fallback more intelligent. Actual weight training, evaluation data, and safe model updates remain future work.

Tests have been added for atomic-memory behavior, persistence across assistant instances, and explicit learning commands. They have **not** been run in this phase. GitHub Actions and APK builds remain manual-only and were not started.
