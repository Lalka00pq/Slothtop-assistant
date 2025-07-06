# project
# from src.voice.voice_recognition import record_and_transcribe
from src.agent.agent import create_agent


def main() -> None:
    """Main function to create the agent and invoke it with a sample input."""

    agent = create_agent()

    result = agent.invoke(
        {"input": "can you open Discord."})

    print(result)


if __name__ == "__main__":
    main()
