# Intelligent Document Analysis Tool for Adobe Hackathon 2025
_Transforming static documents into context-aware knowledge companions_

Project Overview
This repository contains two robust, offline-first document processing pipelines developed for Adobe's Document AI Hackathon. Our solutions efficiently extract structural metadata and generate persona-specific insights from PDF collections without requiring internet connectivity.

* **Challenge 1A**: Title and outline extraction from unstructured PDFs.
* **Challenge 1B**: Persona-specific document summarization using contextual ranking.

Each component is designed to run entirely offline, with efficient use of CPU and memory resources, and a total execution time under 30 seconds per document batch. The project showcases practical applications of natural language processing, information retrieval, and layout-based PDF parsing.

---

## Repository Structure

```
.
├── Challenge_1a/
│   ├── sample_dataset/
│   ├── Dockerfile
│   ├── README.md
│   ├── download_nltk.py
│   ├── process_pdfs.py
│   └── requirements.txt
│
├── Challenge_1b/
│   ├── Collection 1/
│   ├── Collection 2/
│   ├── Collection 3/
│   ├── Dockerfile
│   ├── README.md
│   ├── approach_explanation.md
│   ├── document_processor.py
│   ├── run_collections.py
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

## Challenge 1A: Title and Outline Extraction

The goal of Challenge 1A is to extract the main document title and a structured outline (H1, H2, H3 headings with page numbers) from a given PDF file.

This is achieved through a combination of layout-aware heuristics and natural language filters. The approach handles documents with noisy or inconsistent formatting, and outputs a JSON file structured as per the competition requirements.

The script is fully containerized and runs offline without external API dependencies.

For implementation details, refer to: [`Challenge_1a/README.md`](./Challenge_1a/README.md)

---

## Challenge 1B: Persona-Specific Summarization

The objective of Challenge 1B is to identify and extract the most relevant sections of a document collection for a given user persona and their stated goal. This includes:

* Section-wise semantic and lexical scoring
* Title inference from raw document blocks
* Extractive summarization using TF-IDF and positional heuristics
* Personalized ranking logic using job-related keywords and domain lexicons

The pipeline is optimized for offline execution, using locally hosted models and efficient chunked processing. It supports multiple document collections and can be scaled or extended for different personas and use cases.

For full documentation and methodology, refer to:

* [`Challenge_1b/README.md`](./Challenge_1b/README.md)
* [`Challenge_1b/approach_explanation.md`](./Challenge_1b/approach_explanation.md)

---

## Technical Specifications

| Component              | Technology Stack             |
|------------------------|------------------------------|
| PDF Processing         | PyMuPDF, PDFMiner            |
| NLP Processing         | NLTK, spaCy, SentencePiece   |
| Relevance Engine       | Custom TF-IDF, Cosine Similarity |
| Summarization          | Extractive + Positional Heuristics |
| Containerization       | Docker (AMD64 compatible)    |
| Language               | Python 3.10+                 |

## Getting Started

### Prerequisites
- Docker (version 20.10+)
- AMD64 compatible system (tested on Ubuntu 22.04/WSL2)
- 8GB RAM recommended

### Installation & Execution

**Challenge 1A**:
```bash
cd Challenge_1a
docker build --platform linux/amd64 -t doc-structure .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output doc-structure
```

**Challenge 1B**:
```bash
cd Challenge_1b
docker build --platform linux/amd64 -t doc-intelligence .
docker run --rm -v $(pwd)/collections:/app/collections doc-intelligence
```

Each challenge has a separate entry point script that automatically processes available files and prints or stores the results.

## Why Our Solution Stands Out

1. **Contextual Intelligence**  
   Understands professional roles and specific tasks

2. **Explainable Outputs**  
   Transparent scoring mechanisms for auditability

3. **Domain Adaptability**  
   - Academic: Recognizes "Methodology"/"Results" sections
   - Financial: Extracts metric-trend-justification triplets
   - Educational: Links textbook concepts to learning objectives

4. **Resource Optimization**  
   Smaller memory footprint than comparable solutions
