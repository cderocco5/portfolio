## WIZ AI Auto-Remediation Terraform and CLI Engine

## Overview

This project is an LLM AI cloud remediation engine that processes hypothetical Wiz CNAPP findings and automatically generates terraform templates and AWS CLI for fixes.

Combines:

- Machine Learning for classification
- OpenAI LLM to create remediations
- Rule-based fallbacks
- FastAPI service (API layer) to interact with WIZ


### 1. Input Layer (Wiz Issues)

concised "Wiz" finding. (Prod Env will use real WIZ finding which is more repose)

```json
{
  "id": "wiz-123",
  "type": "S3_PUBLIC",
  "resource": {"name": "my-bucket"},
  "severity": "HIGH",
  "details": {"public": true}
}
```



## 2. ML Classification Layer

### Purpose

Classifies issues into categories such as: 
(In enterprise we would train on wiz data from environment)

* `s3_misconfig`
* `network_exposure`
* `iam_issue`
* `database_exposure`
* `k8s_exposure`
* `secret_exposure`
* `encryption_issue`
* `logging_issue`

### Uses

* Uses TF-IDF vectorization
* Uses Logistic Regression

```python
self.vectorizer = TfidfVectorizer()
self.model = LogisticRegression()
```



## 3. LLM Remediation Engine


Uses OpenAI to generate:

* Explanation of the issue
* Terraform fix
* CLI command
* Risk level
* Auto-fix safety flag

### Prompt Design for gpt-4o-mini

```text
You are a senior cloud security engineer.
Analyze this Wiz issue and generate a structured remediation.
```


###Example Output

```json
{
  "explanation": "S3 bucket is publicly accessible...",
  "terraform": "...",
  "cli": "...",
  "risk_level": "HIGH",
  "auto_fix_safe": true
}
```



## 4. Fallback Fix Templates

If the LLM fails or classification is straightforward, predefined fixes are used. In future I can expand project to use RAG with predefinded templates

### Example (S3 Public Access Fix)

```hcl
resource "aws_s3_bucket_public_access_block" "block" {
  bucket = "my-bucket"
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}
```



## 5. Remediation Engine

### Responsibilities

- Classifies issue
- Calls LLM
- Applies fallback templates
- Returns structured output

## 6. API Layer (FastAPI) to test API calls

### Endpoint

```
POST /remediate
```




## 1. Install Dependencies

```bash
pip install fastapi uvicorn openai scikit-learn pydantic
```



## 2. llm api key

### Mac/Linux

```bash
export OPENAI_API_KEY=your_api_key_here
```



## 3. Run Script 

```bash
python main.py
```




# Example Output

```json
## Example Remediation Output useing cli or terraform to autofix the misconfiguration

```json
{
  "category": "s3_misconfig",
  "llm": {
    "raw": "Here is a structured remediation for the Wiz issue regarding the public S3 bucket:",
    "explanation": "The S3 bucket 'my-bucket' is publicly accessible, which poses a significant security risk. Public access to S3 buckets can lead to unauthorized data exposure, data breaches, and compliance violations. It is essential to restrict access to only authorized users and services.",
    "terraform": {
      "resource": {
        "aws_s3_bucket": {
          "my_bucket": {
            "bucket": "my-bucket",
            "acl": "private",
            "block_public_acls": true,
            "ignore_public_acls": true,
            "restrict_public_buckets": true
          }
        }
      }
    },
    "cli": [
      "aws s3api put-bucket-acl --bucket my-bucket --acl private",
      "aws s3api put-public-access-block --bucket my-bucket --block-public-acls true --ignore-public-acls true --restrict-public-buckets true"
    ],
    "risk_level": "HIGH",
    "auto_fix_safe": false
  },
  "fallback": {
    "terraform": "resource \"aws_s3_bucket_public_access_block\" \"block\" {\n  bucket = \"my-bucket\"\n  block_public_acls = true\n  block_public_policy = true\n  ignore_public_acls = true\n  restrict_public_buckets = true\n}",
    "cli": "aws s3api put-public-access-block --bucket my-bucket --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
  }
}
```
  




