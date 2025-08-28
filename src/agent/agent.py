# python
from typing import Optional
import json
import requests
# project
from src.tools.tools import open_app_tool, close_app_tool, turn_off_pc_tool, restart_pc_tool, get_weather_tool
from src.tools.monitoring_tools.monitoring_tool import start_monitoring_cpu_tool, stop_monitoring_cpu_tool, start_monitoring_gpu_tool, stop_monitoring_gpu_tool
from src.tools.web_work_tools import tavily_web_search_tool
from src.schemas.schemas import Settings
# 3rd party
from langchain_ollama.chat_models import ChatOllama as OllamaLLM
from langchain.agents import create_tool_calling_agent, AgentExecutor, ConversationalAgent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
import ollama
# settings
config = Settings.from_json_file('src/app/settings.json')


class SlothAgent:
    @classmethod
    def check_ollama_connection(cls) -> bool:
        """Check if Ollama server is running and accessible.

        Returns:
            bool: True if Ollama server is running and accessible, False otherwise.
        """
        try:
            # Try to connect to the Ollama API with timeout
            ollama.list()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama server: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error checking Ollama connection: {e}")
            return False

    def __init__(self, llm: str = config.user_settings.agent_settings.model,
                 tools_list: Optional[list[BaseTool]] = None):
        """Initialize the SlothAgent with a language model and a list of tools.

        Args:
            llm (str): The language model to use for the agent.
            tools_list (Optional[list[BaseTool]], optional): A list of tools the agent can use.
              Defaults to None.

        Returns:
            None: None
        """
        self.tools = tools_list or [
            open_app_tool,
            close_app_tool,
            # turn_off_pc_tool,
            # restart_pc_tool,
            tavily_web_search_tool,
            # start_monitoring_cpu_tool,
            # stop_monitoring_cpu_tool,
            # start_monitoring_gpu_tool,
            # stop_monitoring_gpu_tool,
            get_weather_tool,
        ]
        self.agent_name = config.user_settings.agent_settings.name

        PREFIX = f"""You are {self.agent_name}. This is your name and identity. You should always:
1. Remember that your name is {self.agent_name}
2. Refer to yourself as {self.agent_name}
3. Respond as {self.agent_name} in all interactions

You are an AI assistant that helps with computer tasks and answers questions.
When interacting with humans, always maintain your identity as {self.agent_name}.

For complex tasks requiring tools, use the following format:
Thought: Do I need to use a tool? Yes/No. Explain why.
Action: Tool name (if needed)
Action Input: Tool input (if needed)
Observation: Tool output
Thought: What to do next?
Final Answer: As {self.agent_name}, I [your response]

For simple questions or casual conversation, just respond naturally.

Assistant has access to these tools:"""

        FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:
Thought: Do I need to use a tool? Yes/No. Explain why.
Action: Tool name
Action Input: Tool input
Observation: Tool output
... (repeat this pattern if needed)
Thought: I know what to say
Final Answer: Response to the human

For questions that don't require tools, simply respond without using the format above.

Remember:
1. Don't use tools for basic conversation
2. Use tools only when specifically needed
3. After using a tool, always provide a clear Final Answer
4. Be concise and direct in responses"""

        SUFFIX = """Previous conversation:
                {chat_history}

                New input: {input}
                {agent_scratchpad}

                Remember to use tools only when necessary. For casual conversation, respond naturally.
                """

        self.prompt = ConversationalAgent.create_prompt(
            tools=self.tools,
            prefix=PREFIX,
            format_instructions=FORMAT_INSTRUCTIONS,
            suffix=SUFFIX,
            input_variables=["input",
                             "chat_history", "agent_scratchpad"]
        )

        if not self.check_ollama_connection():
            raise Exception(
                "Ollama server is not running. Please check if Ollama server is running.")

        self.llm = OllamaLLM(model=llm,
                             temperature=0.7,
                             top_p=0.95)
        self.agent = ConversationalAgent.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input"
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=3,
        )

    def invoke_agent(self, query: str) -> dict:
        """Invoke the agent with the given input text.
        Args:
            query (str): The input text to process.

        Returns:
            dict: The agent's response containing 'output' and optional 'thoughts'.
        """
        thoughts = []

        enhanced_query = f"Remember, you are {self.agent_name}. User's query: {query}"

        response = self.agent_executor.invoke({
            "input": enhanced_query,
            "name": self.agent_name
        })
        if isinstance(response, dict) and 'intermediate_steps' in response:
            for step in response['intermediate_steps']:
                if isinstance(step, tuple) and len(step) >= 2:
                    thoughts.append({
                        'thought': str(step[0]),
                        'observation': str(step[1])
                    })

        return {
            "output": response["output"],
            "thoughts": thoughts
        }

    def change_llm(self, new_llm: str) -> None:
        """Change the language model used by the agent.

        Args:
            new_llm (str): The new language model to use.
        """
        try:
            self.llm = OllamaLLM(model=new_llm)
        except Exception as e:
            print(f"Error changing LLM: {e} - using default LLM.")

        self.agent = ConversationalAgent.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt.partial(
                name=self.agent_name)
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )

    def change_name(self, new_name: str) -> None:
        """Change the name of the agent.

        Args:
            new_name (str): The new name to use.
        """
        self.agent_name = new_name

        PREFIX = f"""You are {self.agent_name}. This is your name and identity. You should always:
1. Remember that your name is {self.agent_name}
2. Refer to yourself as {self.agent_name}
3. Respond as {self.agent_name} in all interactions

You are an AI assistant that helps with computer tasks and answers questions.
When interacting with humans, always maintain your identity as {self.agent_name}.

For complex tasks requiring tools, use the following format:
Thought: Do I need to use a tool? Yes/No. Explain why.
Action: Tool name (if needed)
Action Input: Tool input (if needed)
Observation: Tool output
Thought: What to do next?
Final Answer: As {self.agent_name}, I [your response]

For questions that don't require tools, simply respond naturally but always as {self.agent_name}."""

        FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:
Thought: Do I need to use a tool? Yes/No. Explain why.
Action: Tool name
Action Input: Tool input
Observation: Tool output
... (repeat this pattern if needed)
Thought: I know what to say
Final Answer: I [your response]

For questions that don't require tools, simply respond without using the format above.

Remember:
1. Always maintain your identity
2. Don't use tools for basic conversation
3. Use tools only when specifically needed
4. Be concise and direct in responses"""

        SUFFIX = """Previous conversation:
{chat_history}

New input: {input}
{agent_scratchpad}

Remember to use tools only when necessary."""

        self.prompt = ConversationalAgent.create_prompt(
            tools=self.tools,
            prefix=PREFIX,
            format_instructions=FORMAT_INSTRUCTIONS,
            suffix=SUFFIX,
            input_variables=["input", "chat_history",
                             "agent_scratchpad"]
        )

        self.agent = ConversationalAgent.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt.partial(name=self.agent_name)
        )

        self.memory.clear()

        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=3
        )

        with open('src/app/settings.json', 'r+', encoding='utf-8') as file:
            config = json.load(file)
            config['user_settings']['agent_settings']['name'] = new_name
            file.seek(0)
            json.dump(config, file, indent=4, ensure_ascii=False)
            file.truncate()

    def change_prompt(self,
                      new_prompt: str,
                      name: str = config.user_settings.agent_settings.name) -> None:
        """Change the prompt used by the agent.

        Args:
            new_prompt (str): The new prompt to use.
        """
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", '''Your name is {name}. {new_prompt}'''.format(
                new_prompt=new_prompt, name=name)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        with open('src/app/settings.json', 'r+', encoding='utf-8') as file:
            config = json.load(file)
            config['user_settings']['agent_settings']['prompt'] = new_prompt
            config['user_settings']['agent_settings']['name'] = name
            file.seek(0)
            json.dump(config, file, indent=4, ensure_ascii=False)
            file.truncate()

        self.agent = ConversationalAgent.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools,
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )
