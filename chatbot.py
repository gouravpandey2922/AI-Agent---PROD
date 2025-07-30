import streamlit as st
import pandas as pd
import numpy as np
import uuid
import psycopg2
import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy import text as sql_text
import hashlib

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec



load_dotenv()


# Use environment variable for safety
DATABASE_URL = os.getenv("RENDER_DB_URL")  # Store this securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "webscraper-py"


index = pc.Index(index_name)

# Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY
)

def get_embedding(text):
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def semantic_search(query, index, top_k=5):
    query_embedding = get_embedding(query)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    return results['matches']

def build_context(results):
    context_texts = []
    for match in results:
        metadata = match['metadata']
        snippet = metadata.get('text', '')  # ensure your metadata has this or change accordingly
        context_texts.append(
            f"Company: {metadata.get('company', 'N/A')}, Date: {metadata.get('date_issued', 'N/A')}, Source: {metadata.get('source', 'N/A')}\n{snippet}\n"
        )
    return "\n---\n".join(context_texts)

def generate_answer(question, context):
    prompt = f"""
Use the following context to answer the question:

Context:
{context}

Question:
{question}

Answer:"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")

st.title("Agentic Audit Intelligence Platform")

user_question = st.text_input("Ask a question:")

if user_question:
    with st.spinner("Searching for relevant info..."):
        search_results = semantic_search(user_question, index, top_k=5)
        if not search_results:
            st.warning("No relevant documents found.")
        else:
            context = build_context(search_results)
            answer = generate_answer(user_question, context)
            st.markdown("### Answer:")
            st.write(answer)
            st.markdown("---")
            st.markdown("### Context used:")
            st.write(context)
