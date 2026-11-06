# ASTA_AI

ASTA_AI is a learning project for building a small AI from the ground up with Python.

## What it can do now

- Learn simple logic patterns with a neural network.
- Classify short messages as greetings, questions, thanks, or farewells.
- Select a prepared reply for a recognized message.
- Ask for clarification when it cannot recognize the words.
- Let you add your own training phrases and replies.
- Save and load the trained text model.

**Honest limitation:** this is a small intent-based chatbot, not a generative language model. It selects replies written in its dataset; it does not independently compose knowledgeable answers or understand every question.

## Train on GitHub

1. Open the Actions tab.
2. Select **ASTA_AI - Train and Test**.
3. Choose **Run workflow**, or push a commit to main.
4. Open the completed run and download the asta-ai-trained-model artifact.

The workflow runs tests, trains both brains, and packages their model JSON files.

## Teach ASTA_AI

Edit `datasets/text_training_data.json`.

- Add phrases inside `intents` to teach it which category a message belongs to.
- Add reply choices inside `responses` under the matching category.
- Keep the JSON valid, and add several varied examples for each category.

Example response section:

~~~json
"responses": {
  "greeting": ["Hello! What would you like to talk about?"],
  "thanks": ["You're welcome!"]
}
~~~

The text vocabulary is built from the training phrases. After changing the dataset, run the GitHub Actions workflow again to train the updated model.

## Try a chat on a computer

Install Python 3.11 or newer, then run:

~~~bash
python -m unittest discover -s tests -v
python brain/text_trainer.py
python brain/chat.py
~~~

Type messages when prompted. Type `quit` to end the chat. The chat program uses the saved model and the reply data.

## Android

The GitHub Actions workflow can train the model from your phone's browser, but it is not itself an Android chat app. We can build an Android interface that uses this brain as a later step.

## Project layout

- `brain/` — neural network, text classifier, trainer, and chat loop.
- `datasets/` — phrases and replies you can edit.
- `tests/` — automated checks.
- `.github/workflows/` — GitHub Actions training workflow.
- `models/` — generated model files, available as workflow artifacts.

## Next steps toward a stronger AI

A more capable conversational model needs a much larger, carefully prepared dataset, a language-model training architecture, evaluation, and considerably more computing power. We'll grow this project in manageable stages.
