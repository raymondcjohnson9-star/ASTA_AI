"""Run ASTA_AI's unified assistant from a terminal."""
from assistant_core import AssistantCore

def main():
    assistant = AssistantCore()
    print("ASTA_AI core ready. Type 'quit' to exit.")
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nASTA_AI: Goodbye!")
            break
        if message.casefold() in {"quit", "exit"}:
            print("ASTA_AI: Goodbye!")
            break
        response = assistant.handle(message)
        print(f"ASTA_AI [{response['workspace']['mode']}]: {response['answer']}")

if __name__ == "__main__":
    main()
