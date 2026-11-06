# ASTA_AI

ASTA_AI is a learning project for building a small AI from the ground up with Python.

## What it can do now

- Learn simple logic patterns with a small neural network.
- Classify short messages as greetings, questions, thanks, or farewells.
- Select a prepared reply for a recognized message.
- Learn word-to-word patterns from editable training text and generate experimental phrases.
- Save and load its trained text models.

**Important limitation:** the chatbot still chooses prepared replies. The new phrase generator is a simple word n-gram model: it samples likely next words from patterns in its training text. It does not understand meaning, verify facts, or generate like ChatGPT. Its sentences may be repetitive or nonsensical.

## Train on GitHub

1. Open the Actions tab.
2. Select **ASTA_AI - Train and Test**.
3. Choose **Run workflow**, or push a commit to main.
4. Open the completed run and download the `asta-ai-trained-model` artifact.

The workflow runs the tests, trains the logic and intent models, trains the phrase generator, and packages the generated JSON model files. Workflow artifacts are downloadable outputs; they are not automatically saved back into the repository.

## Teach the chatbot

Edit `datasets/text_training_data.json`.

- Add phrases inside `intents` to teach it which category a message belongs to.
- Add reply choices inside `responses` under the matching category.
- Keep the JSON valid, and add several varied examples for each category.

The text vocabulary is built from the training phrases. After changing the dataset, run the GitHub Actions workflow again.

## Teach the phrase generator

Edit `datasets/conversation_text.txt`. Add original example sentences, preferably one sentence per line, on topics you want it to imitate. Then train it again.

On a computer with Python 3.11 or newer, run:

~~~bash
python -m unittest discover -s tests -v
python brain/text_generator.py
~~~

The script learns from the text file, saves `models/asta_text_generator.json`, and prints five sample phrases. You can also use the generator from Python:

~~~python
from brain.text_generator import TextGenerator
from pathlib import Path

training_text = Path("datasets/conversation_text.txt").read_text(encoding="utf-8")
generator = TextGenerator(order=2).train(training_text)
print(generator.generate("hello", max_words=15))
~~~

The current order-2 model learns pairs of neighboring words. This is intentionally small and understandable; more training text gives it more patterns, but does not automatically give it real-world knowledge.

## Try the chatbot on a computer

~~~bash
python -m unittest discover -s tests -v
python brain/text_trainer.py
python brain/chat.py
~~~

Type messages when prompted. Type `quit` to end the chat. This chat program uses the intent model and prepared reply data; it does not yet use the phrase generator as its reply engine.

## Android

GitHub Actions can run the training workflow from your phone's browser, but it is not itself an Android chat app. An Android interface is a later project step.

## Project layout

- `brain/` — neural network, text classifier, trainers, chat loop, and phrase generator.
- `datasets/` — chatbot examples, replies, and editable generator training text.
- `tests/` — automated checks.
- `.github/workflows/` — GitHub Actions training workflow.
- `models/` — generated model files, available as workflow artifacts.

## Next steps toward a stronger AI

A more capable conversational model needs a much larger dataset, a neural language-model architecture, careful evaluation, and considerably more computing power. We'll build toward that in manageable stages.
