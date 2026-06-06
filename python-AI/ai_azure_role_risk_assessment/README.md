# Azure Role Risk Assessment Tool

## Overview

This project is an AI-powered tool that analyzes Azure roles based on activity logs and identifies roles with potentially excessive permissions.

**Features:**

- Fetch Azure Activity Logs
- Analyze Azure Role Definitions
- Detect unused permissions
- Generate risk scores using AI (Isolation Forest)
- LLM-generated explanations and recommendations



## Prerequisites


- Azure Subscription with access to Activity Logs and Role Definitions
- OpenAI API Key

## Python packages:

```
pip install azure-identity azure-mgmt-authorization azure-mgmt-monitor openai pandas scikit-learn
```

### Environment Variables:

```
export AZURE_SUBSCRIPTION_ID=<your_subscription_id>
export OPENAI_API_KEY=<your_openai_api_key>
```


## Steps to Run

### 1. Authenticate with Azure

Make sure you are logged in with `az login` if using CLI.



### 2. Run the script
```
python main.py
```

This will:

- Fetch Azure Activity Logs and Role Definitions
- Map permissions vs. actions used 
- Generate a risk score based on which permissions are on the roles
- e.g if azure role from activity logs only list network interfaces but has Contributor role on sub, that should be a high risk score
- Generate LLM explanations for risk score and recommendated role

### 4. Output

The script saves results to `azure_role_risk_report.json`.

Sample columns in the report:

- role_name
- granted_permissions
- used_permissions
- unused_permissions
- risk_score  -1 = high risk, 1 = normal
- LLM-generated recommendation

