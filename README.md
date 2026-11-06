# ASTA_AI

ASTA_AI is a learning project for building a small AI from the ground up with Python.

## Current abilities

- A perceptron that learns the AND logic pattern.
- A feed-forward neural network trained on XOR.
- A text brain that learns to classify phrases as greetings, questions, thanks, or farewells.
- Editable training examples, model saving/loading, and automated tests.

This is an early educational model, not a full conversational AI. It recognizes patterns in examples and does not yet understand or generate open-ended language.

## Train on GitHub

1. Open the Actions tab.
2. Select **ASTA_AI - Train and Test**.
3. Choose **Run workflow**, or push a commit to main.
4. Open the completed run and download the asta-ai-trained-model artifact.

The workflow tests and trains both brains, then uploads their saved JSON model files.

## Teach ASTA_AI new phrases

Edit datasets/text_training_data.json. Add phrases inside an existing intent, or create a new intent with several example phrases. Keep the JSON valid: use double quotes and commas between items. Add varied examples that express the same intent.

The vocabulary is built from the dataset, so new words become available when they appear in training phrases. Each workflow run rebuilds the text classifier from the current dataset.

## Run on a computer

Install Python 3.11 or newer, then run:

~~~bash
python -m unittest discover -s tests -v
python brain/trainer.py
python brain/text_trainer.py
~~~

The text model is saved at models/asta_text_brain.json. To use it:

~~~python
from brain.text_brain import TextBrain
brain = TextBrain.load("models/asta_text_brain.json")
print(brain.predict("hello there"))
~~~

## Project layout

- brain/ — neural network, text classifier, and trainers.
- datasets/ — examples you can edit to teach the models.
- tests/ — automatic checks.
- .github/workflows/ — GitHub Actions training workflow.
- models/ — generated model files, available from workflow artifacts.

## Important limitation

This version classifies short text into known categories. A conversational language model will require much larger datasets, a language-model training approach, extensive evaluation, and considerably more computing power. We will build toward that in stages.
