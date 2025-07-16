# project
from src.agent.agent import create_agent


def main() -> None:
    """Main function to create the agent and invoke it with a sample input."""

    agent = create_agent()

    result = agent.invoke(
        {"input": "Restart the computer in 5 seconds."})

    print(result)


if __name__ == "__main__":
    main()
