import os
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from openai import OpenAI
import pandas as pd
from sklearn.ensemble import IsolationForest

# init open ai
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# azure auth
credential = DefaultAzureCredential()
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

auth_client = AuthorizationManagementClient(credential, subscription_id)
monitor_client = MonitorManagementClient(credential, subscription_id)

#  Get Role Definitions 
role_defs = list(auth_client.role_definitions.list(
    scope=f"/subscriptions/{subscription_id}"
))


# add all role and perms to list
roles = []
for rd in role_defs:
    roles.append({
        "role_name": rd.role_name,
        "permissions": rd.permissions[0].actions if rd.permissions else []
    })
# get activity logs
# Pull logs from beginning of year
logs = monitor_client.activity_logs.list(
    filter="eventTimestamp ge '2026-01-01T00:00:00Z'"
)



# get the actions used by the role
used_actions = {}
for log in logs:
    user = log.caller
    action = log.operation_name.value
    used_actions.setdefault(user, set()).add(action)

# Map Role Permissions vs Used Actions ---
role_analysis = []
for role in roles:
    granted = set(role["permissions"])
    used = set()
    for user, actions in used_actions.items():
        # Simple assumption: map user to role if known (requires real mapping)
        used.update(actions)
    unused = granted - used
    role_analysis.append({
        "role_name": role["role_name"],
        "granted_permissions": len(granted),
        "used_permissions": len(used),
        "unused_permissions": len(unused)
    })

df = pd.DataFrame(role_analysis)
# AI Anomaly Detection to determine the risk of the permission on the roles
# -1 -> anomaly (high risk)
# 1 ->  normal
model = IsolationForest(contamination=0.2, random_state=42)
df["risk_score"] = model.fit_predict(df[["granted_permissions","unused_permissions"]])


# Ask LLM for recommendations
for _, row in df.iterrows():
    prompt = f"""
The Azure role '{row['role_name']}' has {row['granted_permissions']} granted permissions, 
of which {row['unused_permissions']} appear unused based on activity logs.
Explain the potential risks and suggest least-privilege adjustments.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You are an Azure security expert."},
            {"role":"user","content":prompt}
        ]
    )
    row["explanation"] = response.choices[0].message.content

# output
df.to_json("azure_role_risk_report.json", indent=2)
print(df[["role_name","unused_permissions","risk_score","explanation"]])