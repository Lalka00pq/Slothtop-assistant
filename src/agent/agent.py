# python
from typing import Optional
import requests
import json
# project
from src.tools.tools import open_app_tool, close_app_tool, turn_off_pc_tool, restart_pc_tool, get_weather_tool
from src.tools.monitoring_tools.monitoring_tool import start_monitoring_cpu_tool, stop_monitoring_cpu_tool, start_monitoring_gpu_tool, stop_monitoring_gpu_tool
from src.tools.web_work_tools import tavily_web_search_tool
from src.schemas.schemas import Settings
# 3rd party
from langchain_ollama.chat_models import ChatOllama as OllamaLLM
from langchain.agents import AgentExecutor, ConversationalAgent
from langchain_core.tools import BaseTool
from langchain.memory import ConversationBufferMemory
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

    def __init__(self, llm: str = config.user_settings.agent_settings.default_model,
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
        self.agent_name = "Slothy"

        PREFIX = f"""You are {self.agent_name}, an AI assistant focused on efficient and logical task execution.

CORE IDENTITY:
1. You are {self.agent_name}
2. Always refer to yourself as {self.agent_name}
3. Respond as {self.agent_name} in all interactions

TOOL USAGE GUIDELINES - READ CAREFULLY:
Tools should ONLY be used when ABSOLUTELY NECESSARY. Before using any tool, ask yourself:
1. Is this task IMPOSSIBLE to complete without tools?
2. Is this query specifically requesting a tool-based action?
3. Does this require interaction with the computer system or external data?

Examples when NOT to use tools:
- General questions about topics
- Casual conversation
- Explaining concepts
- Providing information you already know
- Follow-up questions about previous responses
- Theoretical discussions

Examples when to use tools:
- Specific requests to open/close applications
- Direct requests for weather information
- Explicit requests to search for current information
- System monitoring requests
- Direct commands to control the computer

If using tools, follow this format:
Thought: Do I need a tool? (Provide clear reasoning why a tool is absolutely necessary)
Action: Tool name
Action Input: Tool input
Observation: Tool output
Thought: What to do next?
Final Answer: As {self.agent_name}, I [your response]

For all other interactions, simply respond naturally without any special format.

Available tools (Use ONLY when necessary):"""

        FORMAT_INSTRUCTIONS = f"""DECISION MAKING PROCESS:

1. First, ALWAYS ask yourself: "Is a tool ABSOLUTELY NECESSARY for this task?"
   - Can I answer without tools? -> Respond naturally
   - Is this just a conversation? -> Respond naturally
   - Am I being asked to perform a specific system action? -> Consider tools

2. If you decide to use a tool, use this format:
   Thought: I need a tool because [specific reason why this task is impossible without tools]
   Action: [tool name]
   Action Input: [precise input]
   Observation: [tool output]
   Thought: [next step analysis]
   Final Answer: As {self.agent_name}, I [your response]

3. After using a tool:
   - Don't use additional tools unless explicitly required
   - Focus on answering the user's original question
   - Be concise and direct

4. CRITICAL RULES:
   - Never use tools for information you already know
   - Never use tools just to verify your knowledge
   - Never use tools for basic conversation
   - One tool use is usually enough per request
   - If you're unsure if you need a tool, you probably don't

For all non-tool interactions, respond naturally and conversationally as {self.agent_name}."""

        SUFFIX = """CONVERSATION CONTEXT:
Previous discussion:
{chat_history}

Current query: {input}
{agent_scratchpad}

FINAL REMINDER:
- Tools are for SPECIFIC SYSTEM ACTIONS only
- Respond naturally to general questions
- Think carefully before using any tool
- One tool per request is usually enough
- Stay focused on the user's actual needs
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
                             temperature=config.user_settings.agent_settings.temperature,
                             top_k=config.user_settings.agent_settings.top_k,
                             top_p=config.user_settings.agent_settings.top_p)
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
            self.llm = OllamaLLM(model=new_llm,
                                 temperature=config.user_settings.agent_settings.temperature,
                                 top_k=config.user_settings.agent_settings.top_k,
                                 top_p=config.user_settings.agent_settings.top_p)
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

    def change_temperature(self, new_temperature: float) -> None:
        """Change the temperature setting of the language model.

        Args:
            new_temperature (float): The new temperature value to set.
        """
        with open("src/app/settings.json", "r+", encoding='utf-8') as file:
            settings = json.load(file)
            settings["user_settings"]["agent_settings"]["temperature"] = new_temperature
            file.seek(0)
            json.dump(settings, file, indent=4, ensure_ascii=False)
            file.truncate()

        self.llm.temperature = new_temperature

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

    def change_top_k(self, value: int) -> None:
        """Change the top_k setting of the language model.

        Args:
            new_top_k (int): The new top_k value to set.
        """
        with open("src/app/settings.json", "r+", encoding='utf-8') as file:
            settings = json.load(file)
            settings["user_settings"]["agent_settings"]["top_k"] = value
            file.seek(0)
            json.dump(settings, file, indent=4, ensure_ascii=False)
            file.truncate()

        self.llm.top_k = value

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

    def change_top_p(self, value: float) -> None:
        """Change the top_p setting of the language model.

        Args:
            new_top_p (float): The new top_p value to set.
        """
        with open("src/app/settings.json", "r+", encoding='utf-8') as file:
            settings = json.load(file)
            settings["user_settings"]["agent_settings"]["top_p"] = value
            file.seek(0)
            json.dump(settings, file, indent=4, ensure_ascii=False)
            file.truncate()

        self.llm.top_p = value

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
