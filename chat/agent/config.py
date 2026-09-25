import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
EMBED_MODEL= os.getenv('EMBED_MODEL')

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

embed_model = GoogleGenerativeAIEmbeddings(model=str(EMBED_MODEL))
vector_store = Chroma(embedding_function=embed_model, persist_directory="VectorDB")