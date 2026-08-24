from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from pathlib import Path
from CRM.settings import EMBED_MODEL


path = Path("../../KnowledgeBase")
embed_model = GoogleGenerativeAIEmbeddings(model=str(EMBED_MODEL))


def load_docs():
    docs = []
    for pdf_file in path.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        pdf_docs = loader.load()

        docs.extend(pdf_docs)
    return docs

def create_chunks(doc):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(doc)
    return chunks


def create_embeddings():
    vector_store = Chroma(embedding_function=embed_model, persist_directory="../../VectorDB")
    docs = load_docs()
    chunks = create_chunks(docs)
    vector_store.add_documents(chunks)