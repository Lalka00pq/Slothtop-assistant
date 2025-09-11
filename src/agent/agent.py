# python
from typing import List
import requests
import json
# project
from src.tools.tools import open_app_tool, close_app_tool, turn_off_pc_tool, restart_pc_tool, get_weather_tool
from src.tools.computer_state_tools.monitoring_tools.monitoring_tool import start_monitoring_cpu_tool, stop_monitoring_cpu_tool, start_monitoring_gpu_tool, stop_monitoring_gpu_tool
from src.tools.computer_state_tools.drives_info import get_disk_info
from src.tools.web_work_tools import tavily_web_search_tool
from src.tools.internet_speed import test_internet_speed
from langchain_core.prompts import ChatPromptTemplate
from src.schemas.schemas import Settings
# 3rd party
from langchain_ollama.chat_models import ChatOllama as OllamaLLM
from langchain.agents import AgentExecutor, create_tool_calling_agent
import ollama
from pydantic import BaseModel, Field
# settings
config = Settings.from_json_file('src/app/settings.json')


class AgentOutput(BaseModel):
    output: str = Field(description="The main output response from the agent.")
    tools_used: List[str] = Field(default_factory=list,
                                  description="List of tools used by the agent in the response.")
    tool_outputs: dict = Field(default_factory=dict,
                               description="Outputs from the tools used by the agent.")


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

    def __init__(self, llm: str = config.user_settings.agent_settings.default_model):
        """Initialize the SlothAgent with a language model and a list of tools.

        Args:
            llm (str): The language model to use for the agent.
            tools_list (Optional[list[BaseTool]], optional): A list of tools the agent can use.
              Defaults to None.

        Returns:
            None: None
        """
        self.tools = [
            test_internet_speed,
            open_app_tool,
            close_app_tool,
            turn_off_pc_tool,
            restart_pc_tool,
            tavily_web_search_tool,
            start_monitoring_cpu_tool,
            stop_monitoring_cpu_tool,
            start_monitoring_gpu_tool,
            stop_monitoring_gpu_tool,
            get_weather_tool,
            get_disk_info,
        ]
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", '''Your name is Slothy. {agent_settings.prompt}'''.format(
                agent_settings=config.user_settings.agent_settings)),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        if not self.check_ollama_connection():
            raise Exception(
                "Ollama server is not running. Please check if Ollama server is running.")

        self.llm = OllamaLLM(model=llm,
                             temperature=config.user_settings.agent_settings.temperature,
                             top_k=config.user_settings.agent_settings.top_k,
                             top_p=config.user_settings.agent_settings.top_p,
                             num_predict=config.user_settings.agent_settings.num_predict)
        self.llm.with_structured_output(AgentOutput)
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

    def invoke_agent(self, query: str) -> dict:
        """Invoke the agent with the given input text.
        Args:
            query (str): The input text to process.

        Returns:
            dict: The agent's response containing 'output' and optional 'thoughts'.
        """

        response = self.agent_executor.invoke({"input": query})

        return {
            "output": response["output"],
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
                                 top_p=config.user_settings.agent_settings.top_p,
                                 num_predict=config.user_settings.agent_settings.num_predict)
        except Exception as e:
            print(f"Error changing LLM: {e} - using default LLM.")

        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def change_settings_params(self, param: str, value, params: List[str] = ['temperature', 'top_k', 'top_p', 'num_predict']) -> None:

        if param in params:
            with open("src/app/settings.json", "r+", encoding='utf-8') as file:
                settings = json.load(file)
                settings["user_settings"]["agent_settings"][param] = value
                file.seek(0)
                json.dump(settings, file, indent=4, ensure_ascii=False)
                file.truncate()

            setattr(self.llm, param, value)

            self.agent = create_tool_calling_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt
            )
            self.agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True
            )
        else:
            raise ValueError(
                f"Parameter '{param}' is not valid. Choose from {params}.")
