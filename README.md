# Intelligent Document Analysis Tool

This repository contains two offline-first document processing pipelines developed for Adobe's Document AI Hackathon:

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

## Setup and Usage

### Prerequisites

* Docker (version 20.10 or higher)
* Linux or WSL2 environment for compatibility with `--platform=linux/amd64`
* Python scripts are compatible with Python 3.10+

### Building and Running

From within either `Challenge_1a` or `Challenge_1b`, run:

```bash
# Build the Docker image
docker build -t doc-understand .

# Run the container with mounted data
docker run --rm -v $(pwd):/app doc-understand
```

Each challenge has a separate entry point script that automatically processes available files and prints or stores the results.

