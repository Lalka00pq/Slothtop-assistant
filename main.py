# project
# from src.voice.voice_recognition import record_and_transcribe
from src.agent.agent import create_agent


def main() -> None:
    """Main function to create the agent and invoke it with a sample input."""

    agent = create_agent()

    result = agent.invoke(
        {"input": "can you search the web for the latest news on AI?. Give me only the first 3 results."})

    print(result)


if __name__ == "__main__":
    main()
