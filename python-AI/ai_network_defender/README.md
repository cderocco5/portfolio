# AI Network Defender

## Overview
**AI Network Defender** is an AI-powered cybersecurity tool that analyzes firewall logs using **Retrieval-Augmented Generation (RAG)** and the MITRE ATT&CK framework.

It acts like a virtual SOC analyst by:
- Ingesting Palo Alto firewall logs  
- Retrieving similar historical events  
- Enriching analysis with threat intelligence  
- Generating AI-driven threat assessments  



## Features

- Analyze Palo Alto firewall logs  
- RAG-based contextual reasoning  
- MITRE ATT&CK mapping for threats  
- Threat classification (low / medium / high)  
- Human-readable explanations and response recommendations  



## Installation

### 1. Install dependencies
```bash
pip install openai pandas numpy faiss-cpu
```

### 2. Set your OpenAI API key
```bash
export OPENAI_API_KEY="your_api_key_here"
```



## Project Structure

```
AI-Network-Defender/
├─ main.py
├─ palo_alto_logs.csv
```



## How to Run

```bash
python main.py
```



## How It Works

### 1. Load Logs
`main.py` reads firewall logs from a CSV file:

```python
df = pd.read_csv("palo_alto_logs.csv")
```

Each row is converted into a natural language description:

```
Traffic from 192.168.1.5:51515 to 10.0.0.2:22 using ssh action=allow bytes=1200
```



### 2. Add MITRE ATT&CK info
The app includes MITRE ATT&CK techniques such as:

- T1110 Brute Force  
- T1021  Remote Services  
- T1046  Network Scanning  
- T1071  Application Layer C2  
- T1041  Data Exfiltration  



### 3. Create Embeddings
Both logs and MITRE data are converted into vectors using OpenAI embeddings.
Text is converted into embeddings (vectors) so LLMs can understand the data 


### 4. Store in Vector Database
FAISS is used for fast similarity search:

```python
index = faiss.IndexFlatL2(dimension)
```

### 5. Retrieval Augmented Generations (RAGs)
When analyzing a new event:
- Finds similar past logs  
- Pulls relevant MITRE techniques  



### 6. AI Analysis
The OpenAI model produces a structured response:

```
- Is it malicious?
-  Determine Threat level
- MITRE technique
- Explanation
- Recommended response
```



# Example of Model showing communication is normal 
```
Event:
Traffic from 8.8.8.8:53 to 192.168.1.30:53 using dns action=allow bytes=200
AI RAG Analysis:
- **Is it malicious?** No
- **Threat level:** Low
- **MITRE ATT&CK technique:** None specific; normal **DNS communication** (no clear ATT&CK technique indicated)

- **Explanation:**
  The event shows traffic from **8.8.8.8:53** to **192.168.1.30:53** using **DNS**, with **allow** action and only **200 bytes** transferred. Port **53** is standard for DNS, and
**8.8.8.8** is a well-known legitimate public DNS resolver (Google DNS). Based on the provided context alone, this looks like routine DNS traffic rather than a malicious indicator
.

- **Recommended response:**
  - Allow and monitor as normal DNS activity
  - Verify that **192.168.1.30** is expected to use external DNS
  - Check for unusual DNS patterns only if there are repeated anomalies, high volume, or suspicious domains
  - No immediate incident response required unless additional indicators appear
```


# Example of Model showing Malicious data based on the RAG with MITRE

```
Event:
Traffic from 123.45.67.89:6667 to 192.168.1.40:80 using irc action=allow bytes=6500
AI RAG Analysis:
- **Is it malicious?** Yes
- **Threat level:** High
- **MITRE ATT&CK technique:** **T1071.001 – Application Layer Protocol: Web Protocols** *(or more generally C2 over application layer protocol; IRC is also commonly associated wit
h command and control)*
- **Explanation:**
  The source is a **public IP (123.45.67.89)** communicating with an internal host over **port 80** using **IRC**, which is unusual because IRC typically uses ports like 6667 and
is often associated with **command-and-control (C2)** traffic. The event is marked **allow**, and the byte count (**6500**) suggests an active session rather than a simple scan. I
n the provided historical context, this pattern stands out as the most suspicious and is consistent with possible malware beaconing or remote control traffic disguised over HTTP-l
ike access.
- **Recommended response:**
  1. **Isolate 192.168.1.40** from the network if possible.
  2. **Block 123.45.67.89** at firewall/proxy and monitor for related destinations.
  3. **Investigate host 192.168.1.40** for malware, persistence, suspicious processes, and outbound connections.
  4. **Review proxy/firewall logs** for additional IRC or anomalous application-layer traffic.
  5. **Collect forensic evidence** (memory, running processes, autoruns, network connections).
  6. If confirmed, **eradicate the infection and reset any exposed credentials**.

```



## Use Cases

- SOC analyst automation  
- Threat detection research  
- AI + security   

## Notes
**AI Network Defender** demonstrates how AI + RAG can augment cybersecurity workflows, turning raw firewall logs into actionable intelligence. This makes it a strong portfolio project and a learning tool for AI in cybersecurity.

