# AI Projects

```
python-AI
├─ ai_azure_role_risk_assessment
├─ ai_network_defender
├─ ai_wiz_autoremediation_rec
├─ mcp_statcast_baseball
```
---
## AI Azure Role Risk Assessment Overview

This project is an AI-powered tool that analyzes Azure roles based on activity logs and identifies roles with potentially excessive permissions.

- Fetch Azure Activity Logs
- Analyze Azure Role Definitions
- Detect unused permissions
- Generate risk scores using AI (Isolation Forest)
- LLM-generated explanations and recommendations
---
## AI Network Defender Overview
**AI Network Defender** is an AI-powered cybersecurity tool that analyzes firewall logs using **Retrieval-Augmented Generation (RAG)** and the MITRE ATT&CK framework.

It acts like a virtual SOC analyst by:
- Ingesting Palo Alto firewall logs  
- Retrieving similar historical events  
- Enriching analysis with MITRE ATT&CK framework and a RAG of specific flow logs 
- Generating AI-driven threat assessments  by analyzing Palo Alto firewall logs  
- RAG-based contextual reasoning  
- MITRE ATT&CK mapping for threats  
- Threat classification (low / medium / high)  
- Human-readable explanations and response recommendations
---

## AI Wiz Auto-remediation Engine

This project is an LLM AI cloud remediation engine that processes hypothetical Wiz CNAPP findings and automatically generates terraform templates and AWS CLI for fixes.

Combines:

- Machine Learning for classification
- OpenAI LLM to create remediations
- Rule-based fallbacks ( can use RAGs when more developed )


## MLB Statcast MCP Server 

A local MCP (Model Context Protocol) server that connects Claude Code to MLB Statcast data. Ask Claude natural language questions about any MLB batter and get real stats pulled live from Baseball Savant.