"""Interactive command-line interface for the example-based coding tutor."""
from pathlib import Path
try:
    from .code_brain import CodeBrain
except ImportError:
    from code_brain import CodeBrain


def main():
    root = Path(__file__).resolve().parents[1]
    brain = CodeBrain.from_file(root / "datasets" / "python_lessons.json")
    print("ASTA_AI Python Tutor")
    print("Ask about a Python topic, or type 'quit' to stop.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in {"quit", "exit"}:
            print("ASTA_AI: Keep practising Python. Goodbye!")
            break
        lesson = brain.answer(question)
        if lesson is None:
            print("ASTA_AI: I don't have a lesson for that yet. Add one to datasets/python_lessons.json.")
            continue
        print(f"\nTopic: {lesson['title']}")
        print(lesson["explanation"])
        print("\nExample code:\n" + lesson["code"])
        print("\nPractice task: " + lesson["exercise"])
        show = input("Show the sample answer? (yes/no): ").strip().lower()
        if show in {"yes", "y"}:
            print("\nSample answer:\n" + lesson["answer"])


if __name__ == "__main__":
    main()
