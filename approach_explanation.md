## Outline
This system is designed as an **offline, intelligent document analysis engine** that identifies, ranks, and summarizes the most relevant sections from a collection of PDF documents. It operates based on a specified **persona** and their **job-to-be-done**, ensuring that the output is both contextually useful and role specific. The solution is optimized for environments with **no internet access**, is efficient on **CPU only setups**, and supports **diverse domains**, including academia, business, and education. The complete pipeline runs within 30 seconds for 3–5 documents and uses less than 1 GB of memory.

## Key Design Objectives
1. **Persona Centric Extraction**: Focused extraction of content based on the specific responsibilities, language, and needs of the target persona.
2. **Domain Agnostic Generalization**: Ability to adapt to multiple document types such as research papers, business reports, and textbooks without requiring reconfiguration.
3. **Offline First Efficiency**: Designed to work entirely offline, with minimal memory and compute requirements.
4. **Transparency and Explainability**: All decisions—titles, scores, and summaries—are interpretable and grounded in clearly defined heuristics and scoring logic.

## Methodology
### 1. Section Segmentation
PDF documents are parsed using `PyMuPDF`, extracting page-wise text content. The segmentation process identifies coherent content blocks through a combination of:
* Pattern recognition in headers (e.g., numbered headings, capitalized titles)
* Layout heuristics, including double newlines and indentation cues
* Word count thresholds to filter out noise such as boilerplate or metadata
This segmentation logic has been tuned to perform well across a variety of layout formats, including academic (LaTeX/IEEE), textbook (chapter-based), and business reports.

### 2. Persona-Aware Relevance Scoring
Each identified section is scored for relevance using a hybrid strategy combining lexical and semantic signals. The scoring process includes:
* **Lexical Matching**: Weighted overlap with keywords and phrases from the persona’s job-to-be-done.
* **Domain Vocabulary Alignment**: Emphasis on the presence of domain-specific terms relevant to the persona.
* **Instructional Cues**: Boosted scores for content containing how-to guides, comparisons, and procedural information.
* **Penalty Terms**: De-prioritization of sections that are formulaic, repetitive, or administrative in nature (e.g., legal disclaimers).
These scores are normalized and used to rank sections across all documents, providing a global relevance ordering tailored to the persona’s intent.

```python
def calculate_relevance(section, persona, job):  
    # 1. Primary signal: Job keyword alignment  
    job_score = max(  
        [fuzz.partial_ratio(job, phrase) for phrase in keyphrases(section)]  
    )  

    # 2. Secondary signal: Persona lexicon boost  
    persona_boost = log(1 + sum(  
        term_frequency(domain_lexicons[persona], section)  
    ))  

    # 3. Penalty signals  
    if contains(legal_boilerplate, section):  
        job_score *= 0.3  # Demote generic disclaimers  

    return job_score * persona_boost  
```

### 3. Interpretable Title Inference
To enhance usability and readability, each extracted section is assigned an informative title using a dual approach:
* When available, the most prominent heading is selected based on font size and positioning.
* In the absence of an explicit title, the system falls back to extracting a title using either the first sentence or through keyphrase clustering techniques.
This ensures that every section is immediately scannable and meaningfully labeled, even in semi-structured or unstructured PDFs.

### 4. Sub-Section Summarization
Within each relevant section, a concise, extractive summary is generated using a multi-feature scoring model. The summarization process considers:
* **TF-IDF Weighted Keywords**: Identified from a custom-trained offline corpus.
* **Sentence Position**: Prioritizes leading sentences which often serve as topic sentences.
* **Structural Features**: Emphasizes bullet points, lists, numerals, and tabular formats.
* **Domain Adaptation**: Uses different weighting schemes for academic, financial, or educational content to tailor the summary appropriately.
This method allows for fast yet informative summarization without relying on large language models or internet access.
<img width="3840" height="806" alt="Untitled diagram _ Mermaid Chart-2025-07-28-151821" src="https://github.com/user-attachments/assets/67a08577-947c-4666-8ee6-74c82e399d9d" />




## Generalization and Persona Test Cases
The system has been evaluated on three representative personas to demonstrate domain adaptability:
| **Persona**                    | **Target Documents**              | **Strategy Highlights**                                                                                                                                 |
| ------------------------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Researcher (Literature Review) | Academic Papers                   | Extracts sections such as Methodology, Results, Datasets; prioritizes comparisons and benchmarks using bio-NLP lexicons.                                |
| Analyst (Financial Reports)    | Business & Annual Reports         | Captures KPIs such as R\&D expenditure, revenue trends, and strategic outlook; filters out legal and meta-content using regex and keyword dictionaries. |
| Student (Exam Preparation)     | Science and Engineering Textbooks | Focuses on definition-heavy and concept-rich sections; boosts scores for reaction mechanisms, summaries, and formulas.                                  |

## Output Format
The final output is saved in `challenge1b_output.json`, structured as follows:
* **Metadata**: Includes document set, selected persona, job description, and timestamp.
* **Top Sections**: Lists top-ranked sections with `importance_rank`, `title`, and `page_number`.
* **Sub-sections**: Provides extracted summaries with filtering and signal-based ranking.

## Performance & Offline Compliance
* **Execution Time**: Under 30 seconds for 3–5 PDF files.
* **Memory Footprint**: Less than 700 MB of RAM.
* **Model Size**: \~400 MB (stored and accessed fully offline).
* **Dependencies**: No internet access required during inference, making it ideal for enterprise, air-gapped, or restricted environments.

## Strengths Summary
* Personalized and context-sensitive extraction tailored to user roles
* Robust title inference and interpretability for each section
* Compact, offline-compatible architecture with fast execution
* High generalizability across technical, business, and educational content
* Modular design allows easy extension to support additional personas and tasks
