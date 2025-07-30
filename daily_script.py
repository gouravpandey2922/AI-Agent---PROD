import os
import datetime
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import psycopg2

# Fetch secrets (already working)
RENDER_DB_URL = os.environ['RENDER_DB_URL']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']

def main():
    today = datetime.date.today()
    
    # DB connection (already succeeds)
    conn = psycopg2.connect(RENDER_DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print(f"Connected to DB: {db_version}")
    cur.close()
    conn.close()
    
    # OpenAI embedding (tweak input as needed)
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="Sample business data to embed"  # Replace: e.g., pull from DB query
    )
    embedding = response.data[0].embedding
    
    # Pinecone: Auto-create index if missing
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "auditdoc-index"
    dimension = 1536  # Match your embedding model
    
    # Check if index exists; create if not
    if index_name not in pc.list_indexes().names():
        print(f"Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",  # Good for text embeddings
            spec=ServerlessSpec(cloud='aws', region='us-east-1')  # Adjust region if needed
        )
    else:
        print(f"Index {index_name} already exists")
    
    # Now upsert safely
    index = pc.Index(index_name)
    index.upsert([("id1", embedding, {"date": str(today)})])  # Extend: Use real IDs/metadata
    
    print(f"Daily run complete: Data processed for {today}")

if __name__ == "__main__":
    main()
