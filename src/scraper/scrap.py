# ======================= library  ======================= #
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter


# ======================= functions  ======================= #
async def scraper(urls):
    """
    
    """
    await asyncio.sleep(2)
    loader = AsyncChromiumLoader(urls)
    text_transformer = Html2TextTransformer()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)

    docs = await loader.aload()
    transformed_docs = text_transformer.transform_documents(docs)
    split_docs_nested = [text_splitter.split_documents([doc]) for doc in transformed_docs]

    processed_chunks = []
    for doc_list, original_doc in zip(split_docs_nested, transformed_docs):
        for chunk in doc_list:
            chunk.metadata['source'] = original_doc.metadata.get('source', 'Unknown')
            processed_chunks.append(chunk)

    return processed_chunks
