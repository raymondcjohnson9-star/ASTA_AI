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
3. Choose **Run workflow**, or push a commit to main.
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
