# ASTA_AI

Your personal machine-learning project, built step by step from scratch.

## What is included now

- A simple perceptron that learns the AND logic pattern.
- A small feed-forward neural network with one hidden layer and backpropagation.
- A tiny XOR training dataset.
- Automated tests.
- A GitHub Actions workflow that runs the tests and trains the starter model on every push to `main`, on pull requests, and when manually started.

## Run it

You need Python 3.10 or newer. No third-party packages are required.

```bash
python -m unittest discover -s tests -v
python brain/trainer.py
```

## How the first model learns

The starter neural network sees four examples of the XOR pattern. It makes predictions, compares them with the expected answers, and adjusts its weights using backpropagation.

This is a small learning project, not yet a conversational AI. We will expand it gradually with better datasets, more model layers, saved model weights, and eventually Android and desktop interfaces. Training a capable language model from scratch is a much larger project and needs far more data and computing power.

## Project layout

```text
brain/                  Model code and training program
datasets/               Training examples
tests/                  Automated tests
.github/workflows/      GitHub Actions automation
```
