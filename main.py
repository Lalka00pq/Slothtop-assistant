# project
from src.agent.agent import create_agent


def main() -> None:
    """Main function to create the agent and invoke it with a sample input."""

    agent = create_agent()

    result = agent.invoke(
        {"input": "Can you search through my Obsidian vault. I want to find find how many notes I have?"})

    print(result['output'] if 'output' in result else 'No result')


if __name__ == "__main__":
    main()
