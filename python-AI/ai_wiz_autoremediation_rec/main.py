# Advanced AI Auto-Remediation Recommendation Engine
# - Wiz issue ingestion
# - ML-based classification (sklearn placeholder) to classify our Wiz data
# - Use LLM to generate remediation recomendations with prompt engineering
# - Terraform + CLI + Explanation output
# - FastAPI service to make remediations

import json
import os
from typing import Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# OpenAI
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple ML classifier

class IssueClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self.trained = False


    # train model
    def train(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self.trained = True

    # prediction vectors
    def predict(self, text: str) -> str:
        if not self.trained:
            return "unknown"
        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]

classifier = IssueClassifier()

# Sample 'minimized' WIZ dataset
classifier.train(
    [
        "S3 bucket is public","S3 bucket allows public read access",
        "Security group open to 0.0.0.0",
        "Security group allows SSH from anywhere",
        "IAM role has admin access",
        "IAM user has wildcard permissions",
        "RDS instance publicly accessible",
        "Database exposed to internet",
        "Kubernetes dashboard publicly exposed",
        "K8s API server open to internet",
        "Hardcoded AWS keys found",
        "Secrets exposed in environment variables",
        "EBS volume not encrypted",
        "Unencrypted storage volume",
        "CloudTrail logging disabled",
        "No audit logging enabled",
        "S3 bucket without encryption",
        "Storage bucket missing encryption",
        "Overly permissive IAM policy",
        "Privilege escalation possible in IAM role"
    ],
    [
        "s3_misconfig",
        "s3_misconfig",
        "network_exposure",
        "network_exposure",
        "iam_issue",
        "iam_issue",
        "database_exposure",
        "database_exposure",
        "k8s_exposure",
        "k8s_exposure",
        "secret_exposure",
        "secret_exposure",
        "encryption_issue",
        "encryption_issue",
        "logging_issue",
        "logging_issue",
        "encryption_issue",
        "encryption_issue",
        "iam_issue",
        "iam_issue"
    ]

)

# 2. Fix Templates (Fallback). in case LLM does not generate proper response. 
# Could have lots of false postives not everything in AWS is a bucket. Make more granular

FIX_TEMPLATES = {
    "s3_misconfig": {
        "terraform": '''resource "aws_s3_bucket_public_access_block" "block" {{
  bucket = "{bucket}"
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}}''',
        "cli": "aws s3api put-public-access-block --bucket {bucket} --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
    }
}
# 3. input prompt and generate fix using openai agents

def generate_llm_fix(issue: Dict[str, Any]) -> Dict[str, str]:
    prompt = f"""
You are a senior cloud security engineer.
Analyze this Wiz issue and generate a structured remediation:
Issue:
{json.dumps(issue, indent=2)}

Return JSON with:
- explanation
- terraform
- cli
- risk_level
- auto_fix_safe (true/false)
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in AWS, Terraform, and cloud security."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2 # low value to be more deterministic
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {"raw": content}

# 4. Engine to build recommendatiosn for remediations

class RemediationEngine:

    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        text = json.dumps(issue)
        category = classifier.predict(text)

        resource = issue.get("resource") or {"name": "mys3bucketexample"}

        # LLM first
        llm_result = generate_llm_fix(issue)

        # Fallback if needed
        template = FIX_TEMPLATES.get(category)

        terraform_fallback = None
        cli_fallback = None

        if template:
            terraform_fallback = template["terraform"].format(
                bucket=resource.get("name", "UNKNOWN_BUCKET")
            )
            cli_fallback = template["cli"].format(
                bucket=resource.get("name")
            )

        return {
            "category": category,
            "llm": llm_result,
            "fallback": {
                "terraform": terraform_fallback,
                "cli": cli_fallback
            }
        }

engine = RemediationEngine()

#  FastAPI Service

app = FastAPI(title="AI Auto-Remediation Engine")

class Issue(BaseModel):
    id: str
    type: str
    resource: Dict[str, Any]
    severity: str
    details: Dict[str, Any]

@app.post("/remediate")
def remediate(issue: Issue):
    return engine.generate_fix(issue.dict())


if __name__ == "__main__":
    sample_issue = {
        "id": "wiz-123",
        "type": "S3_PUBLIC",
        "resource": {"name": "my-bucket"},
        "severity": "HIGH",
        "details": {"public": True}
    }
    # test with other service
    #sample_issue = {
    #    "id": "wiz-568",
    #    "type": "APIGATEWAY_PUBLIC",
    #    "resource": {"name": "my-apigateway"},
    #    "severity": "HIGH",
    #    "details": {"public": True}
    #}

    result = engine.generate_fix(sample_issue)
    print(json.dumps(result, indent=2))
