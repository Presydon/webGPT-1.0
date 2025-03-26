# ======================= library  ======================= #
import os
import shutil
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# ======================= variables  ======================= #
model_name = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIRECTORY = os.path.abspath('./faiss_index')
EMBEDDINGS = HuggingFaceEmbeddings(model_name=model_name)
VECTOR_DB = None

os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

# ======================= functions  ======================= #

def _reset_index():
    """
    
    """
    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
        os.makedirs(PERSIST_DIRECTORY)
        print("FAISS index has been reset")


def initialize(split_docs, reset):
    """
    
    """
    global VECTOR_DB

    if reset:
        _reset_index()

    if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
        VECTOR_DB = FAISS.load_local(PERSIST_DIRECTORY, EMBEDDINGS, allow_dangerous_deserialization=True)
    else:
        VECTOR_DB = FAISS.from_documents(documents=split_docs, embedding=EMBEDDINGS)
        VECTOR_DB.save_local(PERSIST_DIRECTORY)

    return VECTOR_DB


def load():
    """
    
    """
    try:
        return FAISS.load_local(PERSIST_DIRECTORY, EMBEDDINGS)
    
    except:
        return None
