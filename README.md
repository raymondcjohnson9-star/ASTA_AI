# ASTA_AI

A personal machine-learning project built step by step from scratch.

## Current abilities

- A perceptron that learns the AND logic pattern.
- A small feed-forward neural network with backpropagation.
- A tiny XOR training dataset.
- Save and load the network's learned weights.
- Continue training from a previously saved model.
- Automated tests and a GitHub Actions training workflow.

## Run it

Python 3.10 or newer is required. No third-party packages are needed.

```bash
python -m unittest discover -s tests -v
python brain/trainer.py
```

The trainer saves the model to `models/xor_model.json`. When run again, it loads that file and continues training instead of creating a fresh network.

## Load the saved model in Python

```python
from brain.neural_network import NeuralNetwork

model = NeuralNetwork.load("models/xor_model.json")
print(model.predict([0, 1]))
```

## Important

This is an educational neural network that learns a tiny mathematical pattern. It is not yet a conversational AI. A useful language model requires much larger datasets, more sophisticated architecture, and substantially more computing resources. We will build toward text learning in later stages.

## Project layout

```text
brain/                  Neural-network code and trainer
datasets/               Training examples
models/                 Saved model parameters (created after training)
tests/                  Automated tests
.github/workflows/      GitHub Actions automation
```
