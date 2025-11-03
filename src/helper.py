from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

#Extract text from PDF files
def load_pdf_files(data):
    loader=DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents =loader.load()
    return documents


def filter_to_minimal_docs(docs : List[Document]) -> List[Document]:
    """
    Given a list of Documnet objects, return a new list of Document objects
    containing only 'source' in metadata and the originak page_content.
    """
    minimal_docs: List[Document]=[]
    for doc in docs:
        src= doc.metadata.get("source")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source":src}
            )
        )
    return minimal_docs


def text_split(minimal_docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
    )
    texts_chunks=text_splitter.split_documents(minimal_docs)
    return texts_chunks


def download_embeddings():
    """
    Download and return the HuggingFace embedding model.
    """

    model_name="sentence-transformers/all-MiniLM-L6-v2"
    embedding= HuggingFaceEmbeddings(
        model_name=model_name
    )
    return embedding

embedding= download_embeddings()