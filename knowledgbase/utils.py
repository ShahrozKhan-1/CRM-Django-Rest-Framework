from langchain_community.document_loaders.parsers.pdf import PyPDFParser
from langchain_core.documents.base import Blob
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
from .models import KnowledgeDocument
from CRM.settings import vector_store


def get_docs(attachments):
    docs = []
    session = requests.Session()
    parser = PyPDFParser()
    for attachment in attachments:
        url = attachment.file
        response = session.get(url)
        response.raise_for_status()
        blob = Blob.from_data(
            response.content,
            mime_type="application/pdf",
            metadata={"source": url},
        )
        pdf_docs = parser.parse(blob)
        docs.extend(pdf_docs)

    return docs

def create_chunks(doc):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(doc)
    return chunks


def create_embeddings(files):
    
    print("got the input and making the embeddings")
    docs = get_docs(files)
    chunks = create_chunks(docs)
    vector_store.add_documents(chunks)
    for attachment in files:
        attachment.status = KnowledgeDocument.STATUS.COMPLETED
        attachment.save(update_fields=["status"])
    return KnowledgeDocument.STATUS.COMPLETED
