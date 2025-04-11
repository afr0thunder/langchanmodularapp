import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class KnowledgeBase:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.index_dir = os.path.join("faiss_index", agent_name)
        self.embedder = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda"}  # Enable GPU
        )
        self.vectorstore = self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_dir):
            return FAISS.load_local(
                self.index_dir,
                self.embedder,
                allow_dangerous_deserialization=True
            )
        else:
            return None

    def _load_single_file(self, file_path: str) -> List[Document]:
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext == ".txt":
                loader = TextLoader(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            return loader.load()
        except Exception as e:
            print(f"[ERROR] Failed to load {file_path}: {e}")
            return []

    def ingest_docs(self, doc_paths: List[str]):
        print(f"Ingesting {len(doc_paths)} documents...")
        all_docs = []

        for i, path in enumerate(doc_paths, 1):
            norm_path = os.path.normpath(path)
            print(f"[{i}/{len(doc_paths)}] Processing {os.path.basename(norm_path)}...")
            docs = self._load_single_file(norm_path)
            if docs:
                print(f"  ✔ Loaded {len(docs)} chunks")
            else:
                print(f"  ✘ Skipped (no loadable content)")
            all_docs.extend(docs)

        if not all_docs:
            print("No documents loaded; skipping FAISS index creation.")
            return

        # Split long docs into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(all_docs)
        print(f"Split into {len(split_docs)} chunks. Creating FAISS index...")

        # Create or extend FAISS index
        if self.vectorstore:
            self.vectorstore.add_documents(split_docs)
        else:
            self.vectorstore = FAISS.from_documents(split_docs, self.embedder)

        # Save index
        self.vectorstore.save_local(self.index_dir)
        print(f"FAISS index saved to {self.index_dir}")

    def query(self, query: str, k: int = 3) -> str:
        if not self.vectorstore:
            return ""
        results = self.vectorstore.similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in results])
