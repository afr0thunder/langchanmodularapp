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
    def __init__(self, agent_storage: str = AGENT_DATA_DIR):
        print("Ingesting from:", agent_storage)
        print("Files found:", os.listdir(agent_storage))
        self.db = DBManager()
        self.agent_storage = agent_storage
        if not os.path.exists(agent_storage):
            os.makedirs(agent_storage)

    def create_agent(self, name: str, base_prompt: str, llm_choice: str, ingest_path: str=None) -> None:
        self.db.save_agent(name, base_prompt, llm_choice)

        if ingest_path and os.path.isdir(ingest_path):
            valid_exts = ('.txt', '.pdf', '.md')
            file_paths = [
                os.path.join(ingest_path, f)
                for f in os.listdir(ingest_path)
                if f.lower().endswith(valid_exts)
            ]

            if file_paths:
                kb = KnowledgeBase(agent_name=name)
                print(f"Ingesting {len(file_paths)} documents...")
                kb.ingest_docs(file_paths)
            else:
                print("No supported files to ingest.")
        elif ingest_path:
            print(f"Unsupported ingest path: {ingest_path}")

    def get_agent(self, name: str) -> Agent:
        config = self.db.load_agent(name)
        return Agent(name=config['name'], base_prompt=config['base_prompt'], llm_choice=config['llm_choice'])

    def list_agents(self) -> List[str]:
        return self.db.list_agents()

    def delete_agent(self, name: str) -> None:
        self.db.delete_agent(name)

    def update_agent_prompt(self, name: str, new_prompt: str):
        self.db.update_agent_prompt(name, new_prompt)