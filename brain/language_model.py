"""Tiny neural next-word language model implemented with plain Python.

This is an educational model: one previous token is embedded into a hidden layer,
then a softmax layer predicts the next token. It never executes generated text.
"""
import json
import math
import random
import re
from pathlib import Path


def tokenize(text):
    return re.findall(r"[a-z0-9_]+|[^\w\s]", text.lower())


def softmax(values):
    peak = max(values)
    exps = [math.exp(max(-60.0, value - peak)) for value in values]
    total = sum(exps)
    return [value / total for value in exps]


class NeuralLanguageModel:
    def __init__(self, vocabulary, embedding_size=24, seed=17):
        if len(vocabulary) < 3:
            raise ValueError("Vocabulary must contain at least three tokens")
        self.vocabulary = list(vocabulary)
        self.token_to_id = {token: index for index, token in enumerate(self.vocabulary)}
        self.embedding_size = embedding_size
        rng = random.Random(seed)
        scale = 0.12
        self.embeddings = [
            [rng.uniform(-scale, scale) for _ in range(embedding_size)]
            for _ in self.vocabulary
        ]
        self.output_weights = [
            [rng.uniform(-scale, scale) for _ in range(embedding_size)]
            for _ in self.vocabulary
        ]
        self.output_bias = [0.0 for _ in self.vocabulary]
        self.loss_history = []

    @classmethod
    def from_text(cls, text, embedding_size=24, seed=17):
        tokens = ["<PAD>", "<UNK>", "<END>"] + sorted(set(tokenize(text)))
        return cls(tokens, embedding_size, seed)

    def _probabilities(self, previous_id):
        hidden = self.embeddings[previous_id]
        logits = [
            sum(weight * value for weight, value in zip(row, hidden)) + bias
            for row, bias in zip(self.output_weights, self.output_bias)
        ]
        return hidden, softmax(logits)

    def train(self, text, epochs=80, learning_rate=0.08):
        if epochs < 1 or learning_rate <= 0:
            raise ValueError("epochs and learning_rate must be positive")
        words = tokenize(text)
        if len(words) < 2:
            raise ValueError("Training text needs at least two tokens")
        unknown = [word for word in words if word not in self.token_to_id]
        if unknown:
            raise ValueError("Training text contains tokens outside this model vocabulary")
        sequence = [self.token_to_id["<PAD>"]] + [self.token_to_id[w] for w in words]
        sequence.append(self.token_to_id["<END>"])
        for _ in range(epochs):
            total_loss = 0.0
            for previous_id, target_id in zip(sequence[:-1], sequence[1:]):
                hidden, probs = self._probabilities(previous_id)
                total_loss -= math.log(max(probs[target_id], 1e-12))
                errors = probs[:]
                errors[target_id] -= 1.0
                old_weights = [row[:] for row in self.output_weights]
                for token_id, error in enumerate(errors):
                    self.output_bias[token_id] -= learning_rate * error
                    for h in range(self.embedding_size):
                        self.output_weights[token_id][h] -= learning_rate * error * hidden[h]
                embedding_gradient = [0.0] * self.embedding_size
                for token_id, error in enumerate(errors):
                    for h in range(self.embedding_size):
                        embedding_gradient[h] += error * old_weights[token_id][h]
                for h, gradient in enumerate(embedding_gradient):
                    self.embeddings[previous_id][h] -= learning_rate * gradient
            self.loss_history.append(total_loss / (len(sequence) - 1))
        return self

    def next_token(self, previous_token, temperature=0.85):
        if temperature <= 0:
            raise ValueError("temperature must be positive")
        token_id = self.token_to_id.get(previous_token.lower(), self.token_to_id["<UNK>"])
        hidden = self.embeddings[token_id]
        logits = [
            (sum(w * x for w, x in zip(row, hidden)) + bias) / temperature
            for row, bias in zip(self.output_weights, self.output_bias)
        ]
        probs = softmax(logits)
        # Deterministic best-token selection keeps small models reproducible.
        return self.vocabulary[max(range(len(probs)), key=probs.__getitem__)]

    def generate(self, prompt="", max_tokens=30, temperature=0.85):
        if max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        words = tokenize(prompt)
        previous = words[-1] if words else "<PAD>"
        output = words[:]
        for _ in range(max_tokens):
            token = self.next_token(previous, temperature)
            if token == "<END>":
                break
            if token in {"<PAD>", "<UNK>"}:
                break
            output.append(token)
            previous = token
        return " ".join(output).replace(" .", ".").replace(" ,", ",").replace(" ?", "?").replace(" !", "!")

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "vocabulary": self.vocabulary,
            "embedding_size": self.embedding_size,
            "embeddings": self.embeddings,
            "output_weights": self.output_weights,
            "output_bias": self.output_bias,
            "loss_history": self.loss_history,
        }
        path.write_text(json.dumps(state), encoding="utf-8")

    @classmethod
    def load(cls, path):
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        model = cls(state["vocabulary"], state["embedding_size"])
        model.embeddings = state["embeddings"]
        model.output_weights = state["output_weights"]
        model.output_bias = state["output_bias"]
        model.loss_history = state.get("loss_history", [])
        return model
