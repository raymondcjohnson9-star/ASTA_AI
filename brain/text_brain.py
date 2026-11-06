"""A tiny trainable text-intent classifier built from scratch."""
import json
import re
from pathlib import Path
from neural_network import NeuralNetwork

def tokenize(text):
    return re.findall(r"[a-z0-9']+", text.lower())

class TextBrain:
    def __init__(self, vocabulary, labels, hidden_size=12, seed=17):
        self.vocabulary = list(vocabulary)
        self.labels = list(labels)
        self.word_index = {word: index for index, word in enumerate(self.vocabulary)}
        self.network = NeuralNetwork(len(self.vocabulary), hidden_size, len(self.labels), seed)

    @classmethod
    def from_dataset(cls, dataset):
        labels = sorted(dataset["intents"].keys())
        words = set()
        for phrases in dataset["intents"].values():
            for phrase in phrases:
                words.update(tokenize(phrase))
        return cls(sorted(words), labels)

    def encode(self, text):
        vector = [0.0] * len(self.vocabulary)
        for word in tokenize(text):
            index = self.word_index.get(word)
            if index is not None:
                vector[index] = 1.0
        return vector

    def training_examples(self, dataset):
        examples = []
        for label_index, label in enumerate(self.labels):
            for phrase in dataset["intents"][label]:
                targets = [0.0] * len(self.labels)
                targets[label_index] = 1.0
                examples.append((self.encode(phrase), targets))
        return examples

    def train(self, dataset, epochs=4500, learning_rate=0.35):
        self.network.train(self.training_examples(dataset), epochs, learning_rate)
        return self

    def predict(self, text):
        scores = self.network.predict(self.encode(text))
        best = max(range(len(scores)), key=scores.__getitem__)
        return {"intent": self.labels[best], "confidence": round(scores[best], 4),
                "scores": {label: round(score, 4) for label, score in zip(self.labels, scores)}}

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        net = self.network
        state = {"vocabulary": self.vocabulary, "labels": self.labels,
                 "input_size": net.input_size, "hidden_size": net.hidden_size,
                 "output_size": net.output_size,
                 "weights_input_hidden": net.weights_input_hidden,
                 "bias_hidden": net.bias_hidden,
                 "weights_hidden_output": net.weights_hidden_output,
                 "bias_output": net.bias_output}
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        brain = cls(state["vocabulary"], state["labels"], state["hidden_size"])
        brain.network.weights_input_hidden = state["weights_input_hidden"]
        brain.network.bias_hidden = state["bias_hidden"]
        brain.network.weights_hidden_output = state["weights_hidden_output"]
        brain.network.bias_output = state["bias_output"]
        return brain
