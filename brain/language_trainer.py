"""Train ASTA_AI's small general-purpose neural language model."""
from pathlib import Path
try:
    from .language_model import NeuralLanguageModel
except ImportError:
    from language_model import NeuralLanguageModel

ROOT = Path(__file__).resolve().parents[1]

def train():
    text = (ROOT / "datasets" / "general_learning_text.txt").read_text(encoding="utf-8")
    model = NeuralLanguageModel.from_text(text, embedding_size=24)
    model.train(text, epochs=80, learning_rate=0.08)
    output = ROOT / "models" / "asta_language_model.json"
    model.save(output)
    print(f"Trained on {len(text.split())} words; final average loss: {model.loss_history[-1]:.4f}")
    print("Sample:", model.generate("a good", max_tokens=12))

if __name__ == "__main__":
    train()
