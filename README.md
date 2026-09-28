
# TrustLens – AI Powered Packaged Product Analysis Platform

TrustLens is an AI-powered platform for analyzing packaged products from their ingredient information.

The system accepts a product image, extracts the ingredient list using OCR and ingredient detection, and generates an AI-based Trust Report containing ingredient-level analysis, safety information, trust scores, concerns, positive aspects, and unknown ingredients.

This repository contains the integrated TrustLens AI API, combining the product-detail and ingredient extraction pipeline with the AI-powered Trust Report generator.

---

## Features

- Product ingredient extraction from images
- OCR-based text extraction using PaddleOCR
- Ingredient identification using LayoutLMv3
- Ingredient post-processing and normalization
- Ingredient database matching
- RAG-based ingredient retrieval using FAISS
- Local embeddings using `nomic-embed-text`
- AI report generation using `llama3.2:3b`
- Ingredient-level trust scores and remarks
- Adult, child, and pregnancy safety information
- Overall trust score and analysis
- Detection of unknown ingredients
- FastAPI REST API
- Swagger/OpenAPI documentation
- Local AI inference through Ollama

---

## System Architecture

```text
                         Product Image
                              │
                              ▼
                     ┌─────────────────┐
                     │    FastAPI API  │
                     └────────┬────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ ProductDetailsWrapper  │
                  └───────────┬────────────┘
                              │
                              ▼
                       OCR / Detection
                              │
                  ┌───────────┴───────────┐
                  │                       │
                  ▼                       ▼
             PaddleOCR               LayoutLMv3
                  │                       │
                  └───────────┬───────────┘
                              │
                              ▼
                     Ingredient List
                              │
                              ▼
                  ┌────────────────────────┐
                  │   TrustReportWrapper   │
                  └───────────┬────────────┘
                              │
                              ▼
                     Report Generator
                              │
                              ▼
                       RAG / FAISS
                              │
                              ▼
                    nomic-embed-text
                              │
                              ▼
                     Retrieved Context
                              │
                              ▼
                        llama3.2:3b
                              │
                              ▼
                     Trust Report JSON
                              │
                              ▼
                    Final API Response
````

---

## Technology Stack

### Backend

* Python 3.10
* FastAPI
* Uvicorn

### OCR & Ingredient Detection

* PaddleOCR
* PaddlePaddle
* LayoutLMv3
* Hugging Face Transformers
* PyTorch + CUDA

### AI / RAG

* Ollama
* Llama 3.2 3B
* FAISS
* LangChain
* Ollama Embeddings
* `nomic-embed-text`

---

## Project Structure

```text
TrustLens/
│
├── .gitignore
├── Activity_diagram.png
│
├── TrustLens/
│   └── requirements.txt
│
└── trustlens-ai-api/
    │
    ├── app.py
    ├── requirements.txt
    ├── README.md
    │
    ├── api/
    │   ├── routes.py
    │   └── trust_report_api.py
    │
    ├── config/
    │   └── settings.py
    │
    ├── pipeline/
    │   └── trustlens_pipeline.py
    │
    ├── product_details/
    │   ├── layoutlmv3/
    │   ├── paddleocr/
    │   ├── models/
    │   ├── utils/
    │   └── wrapper/
    │
    ├── trust_report/
    │   ├── engine/
    │   │   ├── analysis.py
    │   │   ├── llm.py
    │   │   ├── products.json
    │   │   ├── prompt.py
    │   │   ├── rag.py
    │   │   └── report_generator.py
    │   │
    │   └── wrapper/
    │       ├── dto.py
    │       └── trust_report_wrapper.py
    │
    ├── models/
    │   └── layoutlmv3_ingredient/
    │
    ├── samples/
    │   └── images/
    │
    └── tests/
```

---

# Setup

## 1. Prerequisites

Recommended environment:

* Ubuntu/Linux
* Python 3.10
* NVIDIA GPU recommended for local ML inference
* CUDA-compatible PyTorch environment
* Ollama

The integrated project was developed and tested using Python `3.10.18`.

---

## 2. Clone the Repository

```bash
git clone https://github.com/deeonenonly/TrustLens.git
cd TrustLens
```

---

## 3. Create the Integration Virtual Environment

The final integrated application uses a dedicated Python environment.

```bash
python3.10 -m venv int_venv
```

Activate it:

```bash
source int_venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

## 4. Install API Dependencies

```bash
pip install -r trustlens-ai-api/requirements.txt
```

The API requirements include:

* FastAPI
* Uvicorn
* PaddleOCR
* PaddlePaddle
* Pillow
* Transformers
* PyTorch with CUDA 12.6 support

---

## 5. Install Trust Report Dependencies

```bash
pip install -r TrustLens/requirements.txt
```

These dependencies include:

* Ollama Python client
* LangChain
* LangChain Community
* FAISS CPU

---

# Ollama Setup

Ollama is used as the local AI service.

Check the installation:

```bash
ollama --version
```

Start the Ollama service when required:

```bash
ollama serve
```

---

## Required Ollama Models

TrustLens uses two separate models.

### Llama 3.2 3B

Used for:

```text
Trust Report generation
```

Pull the model:

```bash
ollama pull llama3.2:3b
```

### Nomic Embed Text

Used for:

```text
RAG embeddings
```

Pull the model:

```bash
ollama pull nomic-embed-text
```

Verify the installed models:

```bash
ollama list
```

Expected models:

```text
llama3.2:3b
nomic-embed-text
```

### Model Roles

```text
llama3.2:3b
    ↓
LLM / Trust Report generation

nomic-embed-text
    ↓
Embeddings / RAG retrieval
```

The two models serve different purposes and are managed by Ollama rather than pip.

---

# LayoutLMv3 Model

The project uses a trained LayoutLMv3 model for ingredient detection.

The model directory is:

```text
trustlens-ai-api/models/layoutlmv3_ingredient/
```

The large trained model weights and training checkpoints are intentionally excluded from Git because of their size.

The repository includes the relevant configuration and tokenizer-related files, while the trained weight files must be available locally for the full ingredient extraction pipeline.

---

# Running the API

Navigate to the API directory:

```bash
cd trustlens-ai-api
```

Activate the integration environment if necessary:

```bash
source ../int_venv/bin/activate
```

Start the FastAPI server:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Swagger API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI provides an interactive Swagger UI for testing the available endpoints.

---

# Main API Endpoint

The main product analysis endpoint is:

```http
POST /api/v1/analyze-url
```

It accepts an image URL.

Example:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/analyze-url?image_url=<IMAGE_URL>' \
  -H 'accept: */*' \
  -d ''
```

---

# Processing Flow

## Step 1 – Image Input

The API receives a packaged-product image URL.

## Step 2 – Product Detail Extraction

`ProductDetailsWrapper` processes the image.

## Step 3 – OCR

PaddleOCR extracts text and layout information from the image.

## Step 4 – Ingredient Detection

LayoutLMv3 helps identify the ingredient section and ingredient tokens.

## Step 5 – Ingredient Post-processing

The extracted OCR text is normalized and converted into an ingredient list.

Example:

```json
[
  "Water",
  "Sugar",
  "Iodized Salt"
]
```

## Step 6 – Trust Report Generation

The extracted ingredient list is passed to:

```text
TrustReportWrapper
```

The wrapper converts the list into a comma-separated input for the report generator.

Example:

```text
Water, Sugar, Iodized Salt
```

## Step 7 – RAG Retrieval

The report engine retrieves relevant ingredient information from the TrustLens ingredient database using FAISS.

## Step 8 – Embeddings

`nomic-embed-text` generates embeddings for the retrieval process.

## Step 9 – LLM Analysis

`llama3.2:3b` generates the Trust Report using the retrieved ingredient information.

## Step 10 – Final Response

The generated report is returned through the FastAPI endpoint.

---

# Response Structure

The final API response intentionally separates extracted product information from AI analysis.

Example:

```json
{
  "productDetails": {
    "productName": null,
    "status": 1,
    "errorMessage": null,
    "ingredients": [
      "Water",
      "Sugar",
      "Iodized Salt"
    ]
  },
  "trustReport": {
    "report": {
      "overall_analysis": {
        "overall_trust_score": 75,
        "status": 0,
        "overall_safety_adult": {},
        "overall_safety_child": {},
        "overall_safety_pregnancy": {},
        "overall_flags": [],
        "overall_remarks": "...",
        "key_concerns": [],
        "positive_aspects": []
      },
      "individual_ingredients": [],
      "unknown_ingredients": []
    }
  }
}
```

### Response Design

The OCR-extracted ingredient list is returned under:

```text
productDetails.ingredients
```

The `trustReport` object contains only the report generated by the integrated report-generation component.

The ingredient list is intentionally **not duplicated** inside `trustReport`.

---

# Trust Report Contents

## Overall Analysis

The generated report can contain:

* Overall trust score
* Overall status
* Adult safety information
* Child safety information
* Pregnancy safety information
* Overall flags
* Key concerns
* Positive aspects
* Overall remarks

## Individual Ingredient Analysis

For matched ingredients:

* Ingredient name
* Database ingredient
* Individual trust score
* Ingredient status
* Rationale
* Adult safety
* Child safety
* Pregnancy safety
* Remarks
* Flags

## Unknown Ingredients

Ingredients that cannot be matched to the TrustLens database are returned in:

```json
"unknown_ingredients": []
```

Unknown ingredients are explicitly marked rather than having database information invented for them.

---

# Example

Input:

```text
Water, Sugar, Salt
```

The report generator processes each ingredient through the retrieval and analysis pipeline:

```text
Water
  ↓
Ingredient database matching
  ↓
Trust analysis

Sugar
  ↓
Ingredient database matching
  ↓
Trust analysis

Salt
  ↓
Ingredient database matching
  ↓
Trust analysis
```

The resulting individual analyses are then combined into the overall Trust Report.

---

# Ingredient Matching

The ingredient extraction process can produce variations in spelling and formatting because the input originates from OCR.

Examples include:

```text
lodized Salt
Iodized Salt
Salt
```

The post-processing and matching pipeline normalizes extracted text and attempts to match it against known TrustLens ingredient data.

When no suitable database match is found, the ingredient is returned under:

```text
unknown_ingredients
```

---

# Testing

The repository contains tests for individual components:

```text
tests/test_api.py
tests/test_product_details.py
tests/test_trust_report.py
```

Additional test scripts include:

```text
test_layoutlmv3.py
test_ocr.py
test_postprocessor.py
test_product_details.py
```

The integrated API can also be tested through:

```text
http://127.0.0.1:8000/docs
```

---

# Development Environment

The integrated project was tested using:

```text
Python        3.10.18
pip           26.2.1
FastAPI       0.141.1
Uvicorn       0.52.4
PaddleOCR     3.7.0
PaddlePaddle  3.3.1
PyTorch       2.13.0+cu126
Transformers  5.14.1
FAISS         1.14.3
Ollama        0.6.2
LangChain     1.3.13
```

Ollama models used:

```text
llama3.2:3b
nomic-embed-text
```

---

# Important Local Dependencies

The following are intentionally not included in Git.

## Virtual Environments

```text
int_venv/
trustlens-ai-api/.venv/
TrustLens/venv_linux/
```

These should be recreated locally using the provided requirements files.

## Ollama Models

```text
llama3.2:3b
nomic-embed-text
```

These are managed by Ollama and must be pulled separately.

## Large LayoutLMv3 Weights

Large `.safetensors` files and checkpoint directories are excluded from the repository due to their size.

---

# Current Limitations

* OCR quality depends on product image quality.
* OCR can produce spelling and formatting variations.
* Some extracted ingredient names may not exactly match database names.
* Unknown ingredients are reported as unknown rather than inferred.
* Exact ingredient quantities are generally unavailable from an ingredient list alone.
* Large trained LayoutLMv3 weights are not included in Git.
* Ollama must be installed and running locally.
* The report generator requires the required Ollama models to be available locally.

---

# Future Improvements

Potential future improvements include:

* Improved OCR normalization
* Better ingredient alias and fuzzy matching
* Larger ingredient database
* Product-name search
* Report history
* Marketing-claim verification
* User authentication
* Secure user data storage
* Frontend integration
* More robust prompt engineering
* Improved error handling
* Migration from deprecated LangChain integrations to the current standalone integrations
* Automated model and environment setup

---

# Project Status

The integrated backend currently supports:

```text
Product Image
      ↓
OCR / Ingredient Detection
      ↓
Ingredient List
      ↓
Ingredient Matching
      ↓
RAG Retrieval
      ↓
nomic-embed-text
      ↓
llama3.2:3b
      ↓
AI Trust Report
      ↓
FastAPI JSON Response
```

The complete pipeline has been tested end-to-end using:

```text
POST /api/v1/analyze-url
```

The final response contains:

```text
productDetails
    └── ingredients

trustReport
    └── report
         ├── overall_analysis
         ├── individual_ingredients
         └── unknown_ingredients
```

---

# Repository

GitHub:

[https://github.com/deeonenonly/TrustLens](https://github.com/deeonenonly/TrustLens)

