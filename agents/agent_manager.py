import os
from typing import List, Optional
from database.db_manager import DBManager
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from kb.knowledge_base import KnowledgeBase
from dotenv import load_dotenv

AGENT_DATA_DIR = "agents_data"
load_dotenv()

class Agent:
    def __init__(self, name: str, base_prompt: str, llm_choice: str):
        self.name = name
        self.base_prompt = base_prompt
        self.llm_choice = llm_choice
        self.vector_store = KnowledgeBase(agent_name=name)
        self.chain = self._init_chain()

    def _init_chain(self):
        prompt = PromptTemplate.from_template(self.base_prompt)

        if self.llm_choice == "deepseek":
            llm = ChatOpenAI(
                openai_api_base= os.getenv("OPEN_API_BASE"),
                openai_api_key=os.getenv("OPEN_API_KEY"),
                model="deepseek-chat",
            )

        else:
            raise ValueError(f"Unsupported LLM: {self.llm_choice}")

        return LLMChain(prompt=prompt, llm=llm)

    def respond(self, user_input, context=None):
        return self.chain.run({"input": user_input, "context": context})

    def run(self, user_input: str) -> str:
        context = self.vector_store.query(user_input)
        return self.chain.run({"input": user_input, "context": context})


class AgentManager:
    def __init__(self):
        self.db = DBManager()
        if not os.path.exists(AGENT_DATA_DIR):
            os.makedirs(AGENT_DATA_DIR)

    def create_agent(self, name: str, base_prompt: str, llm_choice: str, ingest_path: str=None) -> None:
        self.db.save_agent(name, base_prompt, llm_choice)
        if ingest_path:
            vector_store.ingest_docs([ingest_path])

    def get_agent(self, name: str) -> Agent:
        config = self.db.load_agent(name)
        return Agent(name=config['name'], base_prompt=config['base_prompt'], llm_choice=config['llm_choice'])

    def list_agents(self) -> List[str]:
        return self.db.list_agents()

    def delete_agent(self, name: str) -> None:
        self.db.delete_agent(name)

    def get_agent_config(self, agent_name):
        config_path = os.path.join(self.agent_storage, agent_name, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No config found for agent {agent_name}")
        with open(config_path, "r") as f:
            return json.load(f)