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
