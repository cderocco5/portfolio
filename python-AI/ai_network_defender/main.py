from openai import OpenAI
import pandas as pd
import numpy as np
import faiss

# inti api and load netowrk logs
client = OpenAI()
df = pd.read_csv("palo_alto_logs.csv")

def row_to_text(row):
    return (
        f"Traffic from {row['src_ip']}:{row['src_port']} "
        f"to {row['dst_ip']}:{row['dst_port']} "
        f"using {row['app']} action={row['action']} bytes={row['bytes']}"
    )

log_docs = df.apply(row_to_text, axis=1).tolist()

# mitre attack data for rag
mitre_data = [
    { "technique": "T1110", "name": "Brute Force","description": "Adversaries may attempt to guess passwords for accounts such as SSH or RDP."},
    {"technique": "T1021", "name": "Remote Services","description": "Use of RDP, SMB, or SSH to move laterally across systems."},
    {"technique": "T1046", "name": "Network Service Scanning","description": "Scanning ports/services to identify targets."},
    {"technique": "T1071", "name": "Application Layer Protocol", "description": "Using HTTP, HTTPS, or DNS for command and control communication."},
    {"technique": "T1041", "name": "Exfiltration Over C2 Channel",
     "description": "Large data transfers out of the network over command channels."}
]


# save miter data techniques for RAG
def mitre_to_text(entry):
    return f"{entry['technique']} {entry['name']} {entry['description']}"

mitre_docs = [mitre_to_text(m) for m in mitre_data]


# embed text so llm can understand
def embed(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [d.embedding for d in response.data]

print("Generating embeddings...")

log_embeddings = embed(log_docs)
mitre_embeddings = embed(mitre_docs)

# vector database
all_docs = log_docs + mitre_docs
all_embeddings = log_embeddings + mitre_embeddings

dimension = len(all_embeddings[0])
index = faiss.IndexFlatL2(dimension)

index.add(np.array(all_embeddings).astype("float32"))

print("completed embedings...")

# build my RAG
def retrieve(query, k=5):
    q_emb = embed([query])[0]
    D, I = index.search(np.array([q_emb]).astype("float32"), k)
    results = []
    for i in I[0]:
        results.append(all_docs[i])

    return result

# ai analysts functions
def analyze_event(event_text):
    context = retrieve(event_text)

    prompt = f"""
    You are a SOC cybersecurity analyst using MITRE ATT&CK.

    Context (historical logs + threat intelligence):
    {context}

    Analyze this network event:
    {event_text}

    Provide:
    - Is it malicious? (yes/no)
    - Threat level (low, medium, high)
    - MITRE ATT&CK technique (if applicable)
    - Explanation
    - Recommended response
    """

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt
    )

    return response.output_text

# sample events
test_events = [
    "Traffic from 192.168.1.100:4444 to 10.0.0.5:3389 using unknown action=allow bytes=9999",
    "Traffic from 8.8.8.8:53 to 192.168.1.30:53 using dns action=allow bytes=200",
    "Traffic from 123.45.67.89:6667 to 192.168.1.40:80 using irc action=allow bytes=6500"
]

# =========================
# RUN ANALYSIS
# =========================
for event in test_events:
    print("Event:")
    print(event)

    result = analyze_event(event)

    print("AI RAG Analysis:")
    print(result)