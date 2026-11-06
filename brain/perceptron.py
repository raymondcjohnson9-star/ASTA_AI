"""A tiny perceptron trained from scratch using only Python's standard library."""

class Perceptron:
    def __init__(self, learning_rate=0.1, epochs=20):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights = [0.0, 0.0]
        self.bias = 0.0

    @staticmethod
    def _step(value):
        return 1 if value >= 0 else 0

    def predict(self, inputs):
        total = sum(w * x for w, x in zip(self.weights, inputs)) + self.bias
        return self._step(total)

    def train(self, examples):
        for _ in range(self.epochs):
            for inputs, expected in examples:
                prediction = self.predict(inputs)
                error = expected - prediction
                for index, value in enumerate(inputs):
                    self.weights[index] += self.learning_rate * error * value
                self.bias += self.learning_rate * error
        return self
