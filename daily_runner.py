# %%
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

# %%
# Use environment variable for safety
DATABASE_URL = os.getenv("RENDER_DB_URL")  # Store this securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# %%



client = OpenAI(
    api_key=OPENAI_API_KEY
)

response = client.responses.create(
    model="gpt-4o-mini",
    input="write a haiku about ai",
    store=True,
)

print(response.output_text)

# %% [markdown]
# # Web Scraper

# %% [markdown]
# ### FDA Warning Letters

# %%
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_warning_letters(URL="https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/warning-letters"):
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content)

    # Find all <td> tags with a nested <a> tag (usually in company name column)
    links = []

    for td in soup.find_all('td', class_='views-field-company-name'):
        a_tag = td.find('a')
        if a_tag and 'href' in a_tag.attrs:
            links.append("https://www.fda.gov" + a_tag['href'])



    data = []
    rows = soup.find_all('tr')
    for row in rows:
        date_tag = row.find('td', class_='views-field-field-letter-issue-datetime')
        link_tag = row.find('td', class_='views-field-company-name')

        if date_tag and link_tag:
            time_tag = date_tag.find('time')
            a_tag = link_tag.find('a')

            date_issued = time_tag['datetime'] if time_tag and 'datetime' in time_tag.attrs else None
            letter_link = "https://www.fda.gov" + a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
            company = a_tag.get_text(strip=True) if a_tag else None

            if date_issued and letter_link:
                data.append({
                    'date_issued': date_issued,
                    'company': company,
                    'link': letter_link
                })

    # Convert to DataFrame
    df = pd.DataFrame(data)


    return df



# Run scraper and print results

warning_letters = scrape_warning_letters()
warning_letters
# for wl in warning_letters:
#     print(f"{wl['date']} - {wl['title']}")
#     print(f"Link: {wl['link']}\n")


# %%
def scrape_letter(URL):
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the starting point — a <p> tag with text containing "WARNING LETTER"
    start_p = soup.find('p', string=lambda s: s and "WARNING LETTER" in s)
    if not start_p:
        return "WARNING LETTER start not found"

    letter_paragraphs = []
    for tag in start_p.find_all_next():
        if tag.name != 'p':
            continue

        # Replace <br/> tags with newlines in the HTML content, then strip other tags
        raw_html = tag.decode_contents()
        cleaned_text = BeautifulSoup(raw_html.replace('<br/>', '\n'), 'html.parser').get_text()
        cleaned_text = cleaned_text.strip()

        if not cleaned_text:
            continue

        # Stop conditions
        if 'Qualtrics' in cleaned_text or 'Content current as of:' in cleaned_text:
            break

        letter_paragraphs.append(cleaned_text)

    # Combine and return
    full_text = "\n\n".join(letter_paragraphs)
    if "WARNING LETTER" in full_text:
        return "WARNING LETTER: " + full_text.split("WARNING LETTER", 1)[1].strip()
    else:
        return full_text
    # return soup


# %%
warning_letters['text'] = warning_letters['link'].apply(scrape_letter)
warning_letters['source'] = "FDA Warning Letters"
warning_letters

# %%
warning_letters.text.iloc[4]

# %%


# %% [markdown]
# # SQL Connection

# %%


# %%
conn = psycopg2.connect(DATABASE_URL)
engine = create_engine(DATABASE_URL)

# %%
# 3. Create the table (if it doesn't exist)
create_table_sql = """
CREATE TABLE IF NOT EXISTS warning_letters (
    id SERIAL PRIMARY KEY,
    date_issued TIMESTAMPTZ,
    company TEXT,
    link TEXT,
    text TEXT,
    text_hash TEXT UNIQUE,
    source TEXT
);
"""

with engine.begin() as conn:
    conn.execute(sql_text(create_table_sql))

# 4. Example DataFrame (you should replace this with your actual df)



# 5. Add MD5 hash of the 'text' column
warning_letters['text_hash'] = warning_letters['text'].apply(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())

# 6. Remove duplicates already in the DB
with engine.connect() as conn:
    existing_hashes = pd.read_sql("SELECT text_hash FROM warning_letters", conn)['text_hash'].tolist()

new_rows = warning_letters[~warning_letters['text_hash'].isin(existing_hashes)]

7. Insert only new rows
if not new_rows.empty:
    new_rows.to_sql('warning_letters', con=engine, if_exists='append', index=False)
    print(f"Inserted {len(new_rows)} new rows.")
else:
    print("No new rows to insert.")

# %%
new_rows

# %% [markdown]
# ## Pinecone DB

# %%
pc = Pinecone(api_key=PINECONE_API_KEY)

# %% [markdown]
# ### Create Embeddings

# %%
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

new_rows['ada_embedding'] = new_rows.text.apply(lambda x: get_embedding(x, model='text-embedding-3-small'))
# df.to_csv('output/embedded_1k_reviews.csv', index=False)

# %%
new_rows

# %% [markdown]
# ### Create vector index, if needed

# %%
# from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

index_name = "webscraper-py"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        vector_type="dense",
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
        deletion_protection="disabled",
        tags={
            "environment": "development"
        }
    )

index = pc.Index(index_name)

# %% [markdown]
# ### Add news to vector DB

# %%
items_to_upsert = []
for i, row in new_rows.iterrows():
    vector_id = str(uuid.uuid4())  # generate unique ID for each row
    embedding = row["ada_embedding"]
    metadata = {
        "company": row["company"],
        "date_issued": row["date_issued"],
        "source": row["source"],
        "text": row['text']
    }
    items_to_upsert.append({
        "id": vector_id,
        "values": embedding,
        "metadata": metadata
    })

# Upsert into Pinecone
index.upsert(vectors=items_to_upsert)

# %% [markdown]
# ### Search Vectors

# %%
query_embedding = get_embedding("What warnings are there for 	Glenmark Pharmaceuticals Limited")
query_embedding

# %%
results = index.query(
    vector=query_embedding,
    top_k=5,  # number of top results to return
    include_metadata=True  # to get back company, source, etc.
)

results

# %% [markdown]
# ## RAG

# %%


def semantic_search(query, index, top_k=5):
    query_embedding = get_embedding(query)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    return results['matches']

def build_context(results):
    # Combine top results' metadata + snippet into a context string for the LLM
    context_texts = []
    for match in results:
        metadata = match['metadata']
        snippet = metadata.get('text_snippet', '')  # if you stored snippet of original text
        # If you don't have snippets stored, you may need to adjust
        context_texts.append(f"Company: {metadata['company']}, Date: {metadata['date_issued']}, Sourced by: {metadata['source']}\n{snippet}\n")
    return "\n---\n".join(context_texts)

def generate_answer(question, context):
    prompt = f"""
Use the following context to answer the question:

Context:
{context}

Question:
{question}

Answer:"""
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )
    return response.output_text

# Example usage
user_question = "What are the common FDA violations related to labeling?"
search_results = semantic_search(user_question, index, top_k=5)
context = build_context(search_results)
answer = generate_answer(user_question, context)
print(answer)


# %%



