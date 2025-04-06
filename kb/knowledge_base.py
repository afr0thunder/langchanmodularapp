import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class KnowledgeBase:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.index_dir = os.path.join("faiss_index", agent_name)
        self.embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_dir):
            return FAISS.load_local(self.index_dir, self.embedder)
        else:
            return None

    def ingest_docs(self, doc_paths: List[str]):
        all_docs = []
        for path in doc_paths:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".txt":
                loader = TextLoader(path)
            elif ext == ".pdf":
                loader = PyPDFLoader(path)
            else:
                print(f"Unsupported file format: {path}")
                continue
            docs = loader.load()
            all_docs.extend(docs)

        # Split long docs into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(all_docs)

        # Create or extend FAISS index
        if self.vectorstore:
            self.vectorstore.add_documents(split_docs)
        else:
            self.vectorstore = FAISS.from_documents(split_docs, self.embedder)

        # Save index
        self.vectorstore.save_local(self.index_dir)

    def query(self, query: str, k: int = 3) -> str:
        if not self.vectorstore:
            return ""
        results = self.vectorstore.similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in results])
