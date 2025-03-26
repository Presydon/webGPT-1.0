# ======================= libraries  ======================= #
import os
import asyncio
import sys
from langchain.schema import Document
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.conversation.talks import load_small_talks, clean_input
from dotenv import load_dotenv
load_dotenv()

# ======================= variables  ======================= #
groq_api = os.getenv('GROQ_API_KEY')
model = "llama-3.3-70b-versatile"
LLM = ChatGroq(model=model, api_key=groq_api, temperature=0)
system_prompt = """
    You are WebGPT, an AI assistant for question-answering tasks that **only answers questions based on the provided context**.

    - Understand the context first and provide a relevant answer.
    - If the answer is **not** found in the Context, reply with: "I can't find your request in the provided context."
    - If the question is **unrelated** to the Context, reply with: "I can't answer that. do not generate responses."
    - **Do not** use external knowledge, assumptions, or filler responses. Stick to the context provided.
    - Keep responses clear, concise, and relevant to the user's query.

    Context:
    {context}

    Now, answer the user's question:
    {input}
    """

PROMPT = ChatPromptTemplate([('system', system_prompt), ('human', "{input}")])

SCRAPPER_CHAIN = PROMPT | LLM

if sys.platform.startswith('win'):
    asyncio.set_event_loop()

# ======================= functions  ======================= #
def run_asyncio_coroutine(coro):
    """
    
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def process_query(user_query, vector_store):
    user_query_cleaned = clean_input(user_query)
    response = ""
    source_url = ""

    small_talks = load_small_talks()

    if user_query_cleaned in small_talks:
        response = small_talks[user_query_cleaned]
        source_url = 'Knowledge based'

    else:
        retrieved_docs = vector_store.similarity_search(user_query_cleaned, k=5)

        if not retrieved_docs:
            return "No relevant information found.", 'N/A'
        
        context = "\n\n".join([f"{doc.page_content}\n(Source: {doc.metadata.get('source', 'Unknown')})" for doc in retrieved_docs])

        # formatted_prompt = f"Based on the following context, answer the user's question:\n\n{context}\n\nQuestion: {user_query}\nAnswer:"

        system_prompt = f"""
            You are WebGPT, an AI assistant for question-answering tasks that **only answers questions based on the provided context**.

            - Understand the context first and provide a relevant answer.
            - If the answer is **not** found in the Context, reply with: "I can't find your request in the provided context."
            - If the question is **unrelated** to the Context, reply with: "I can't answer that. do not generate responses."
            - **Do not** use external knowledge, assumptions, or filler responses. Stick to the context provided.
            - Keep responses clear, concise, and relevant to the user's query.

            Context:
            {context}

            Now, answer the user's question:
            {user_query}
            """

        answer = LLM.invoke(system_prompt)

        response = answer.content

        source_url = retrieved_docs[0].metadata.get('source', 'N/A')

    return response, source_url
        #Debugging
        # print("Retrieved Docs:", retrieved_docs)
        # if retrieved_docs:
        #     print('First Doc Type: ', type(retrieved_docs[0]))

        # def format_documents(doc):
        #     if isinstance(doc, Document):
        #         return f"doc.page_content\n()Source: {doc.metadata.get('source', 'Unknown')}"
        #     return str(doc)
        
        # context = "\n\n".join([format_documents(doc) for doc in retrieved_docs])

        # print("Formatted Context:\n", context)

        # response = SCRAPPER_CHAIN.invoke({'context': context, 'input': user_query})

        # source_url = retrieved_docs[0].metadata.get('source', None) if retrieved_docs else None

        # return response, source_url        





# def process_query(user_query, vector_store):
#     """
    
#     """
#     user_query_cleaned = clean_input(user_query)
#     response = ""
#     source_url = ""

#     small_talks = load_small_talks()

#     if user_query_cleaned in small_talks:
#         response = small_talks[user_query_cleaned]
#         source_url = 'Knowledge based'

#     else:
#         retrieved_docs = vector_store.similarity_search(user_query_cleaned, k=5)

#         formatted_docs = []

#         for doc in retrieved_docs:
#             if isinstance(doc, str):
#                 formatted_docs.append(Document(page_content=doc, metadata={'source': "Unknown"}))
#             elif isinstance(doc, dict):
#                 formatted_docs.append(Document(page_content=doc.get("page_content", ""), metadata=doc.get('metadata', {})))
#             else:
#                 formatted_docs.append(doc)

#         if formatted_docs:
#             context = "\n".join([doc.page_content for doc in formatted_docs])
#             scraper_chain = create_stuff_documents_chain(llm=LLM, prompt=PROMPT)
#             response = scraper_chain.invoke({'context': context, 'input': user_query_cleaned})
#             source_url = formatted_docs[0].metadata.get("source", "Unknown")

#             if not response.strip():
#                 response = "I can't find your request in the provided context."
#                 source_url = "No source found"

#         else:
#             response = "I can't find your request in the provided context."
#             source_url = ""

#     return response, source_url

