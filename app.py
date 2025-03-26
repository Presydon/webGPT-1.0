# ======================= libraries  ======================= #
import os
import sys
import subprocess
import asyncio
from playwright.async_api import async_playwright
import streamlit as st
from src.scraper.scrap import scraper
from src.embeddings.vector_store import initialize
from src.functions.chatbot import process_query

# ======================= configurations variables  ======================= #
os.environ["USER_AGENT"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.system("playwright install")
os.system("playwright install --with-deps chromium")
# os.system("playwright install-deps")

# ======================= packages installation  ======================= #
try:
    subprocess.run('playwrigiht install', shell=True, check=True)
except Exception as e:
    print(f"Playwright installation failed: {e}")

# ======================= launch browser  ======================= #
async def launch_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        await browser.close()
    
# ======================= streamlit setup  ======================= #
st.title('WebGPT 1.0 🤖')

urls = st.text_area('Enter URLs (one per line)')
run_scraper = st.button('Run Scraper', disabled=not urls.strip())

# ======================= session state config  ======================= #
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'scraping_done' not in st.session_state:
    st.session_state.scraping_done = False

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None

# ======================= scrapper running  ======================= #
if run_scraper:
    st.write('Fetching and processing URLs... This may take a while..')

    scraper = scraper(urls.split('\n'))  

    # Run the async function safely
    try:
        asyncio.run(launch_browser())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        split_docs = loop.run_until_complete(scraper)
    finally:
        loop.close()

    if not split_docs:
        st.error("No data extracted from the URLs.")

    else:
        st.session_state.vector_store = initialize(split_docs, reset=False)
        st.session_state.scraping_done = True
        st.success("Scraping and processing completed!")

# ======================= clear button  ======================= #
if st.button('Clear chat'):
    st.session_state.messages = []
    st.session_state.history = ""
    st.success("Chat Cleared!")

# ======================= display chat functionality  ======================= #
if not st.session_state.scraping_done:
    st.warning("Scrape some data first to enable chat!")

else:
    st.write("Chat With WebGPT 💬")

# ======================= display chat history  ======================= #
    for message in st.session_state.messages:
        role, text = message['role'], message['text']
        with st.chat_message(role):
            st.write(text)

# ======================= user input take-in  ======================= #
    user_query = st.chat_input("Ask a question...")

    if user_query:
        st.session_state.messages.append({"role": "user", "text": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        if "vector_store" not in st.session_state or st.session_state.vector_store is None:
            st.error("The vetor database is not initialised. Please run the scraper first.")
        else:
            response, source_url = process_query(user_query, st.session_state.vector_store)

        formatted_response = f"**Answer:** {response}"
        if response != "I can't find your request in the provided context." and source_url:
            formatted_response += f"\n\n**Source:** {source_url}"

        st.session_state.messages.append({'role': 'assistant', "text": formatted_response})
        with st.chat_message('assistant'):
            st.write(formatted_response)
