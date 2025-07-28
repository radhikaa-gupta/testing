#!/usr/bin/env python3
"""
Universal Document Processing System
Processes documents to extract relevant information based on persona and task.
Works completely offline without requiring internet connection.
"""

import os
import json
import datetime
import logging
import re
from typing import List, Tuple
import fitz  # PyMuPDF
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  # ✅ Fixed this

class OfflineDocumentProcessor:
    def __init__(self):  # ✅ Fixed this
        """Initialize the processor with offline text processing capabilities."""
        logger.info("Initializing offline document processor...")
        
        self.domain_keywords = {
            'hr': ['employee', 'onboarding', 'compliance', 'form', 'policy', 'training', 'benefits', 'hiring', 'recruitment', 'performance'],
            'forms': ['fillable', 'interactive', 'field', 'form', 'signature', 'fill', 'sign', 'input', 'checkbox', 'text field'],
            'acrobat': ['pdf', 'acrobat', 'adobe', 'convert', 'create', 'edit', 'export', 'share', 'signature', 'form'],
            'technical': ['api', 'code', 'function', 'method', 'parameter', 'configuration', 'setup', 'install'],
            'business': ['process', 'workflow', 'management', 'strategy', 'planning', 'analysis', 'report'],
            'travel': ['itinerary', 'booking', 'hotel', 'flight', 'destination', 'travel', 'trip', 'vacation']
        }
        logger.info("Offline processor initialized successfully")

    def extract_text_by_page(self, pdf_path: str) -> List[Tuple[int, str]]:
        """Extract text from PDF, returning (page_number, text) tuples."""
        try:
            doc = fitz.open(pdf_path)
            pages = []
            for i, page in enumerate(doc):
                text = page.get_text()
                if text.strip():  # Only include pages with content
                    pages.append((i + 1, text))
            doc.close()
            logger.info(f"Extracted {len(pages)} pages from {pdf_path}")
            return pages
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        return text.strip()
    
    def split_sections(self, text: str, min_words: int = 15) -> List[str]:
        """Split text into meaningful sections."""
        # Clean the text first
        text = self.clean_text(text)
        
        # Try different splitting strategies
        sections = []
        
        # Split by double newlines first
        double_newline_sections = [s.strip() for s in text.split("\n\n") if len(s.split()) >= min_words]
        sections.extend(double_newline_sections)
        
        # If we don't have enough sections, try single newlines
        if len(sections) < 3:
            single_newline_sections = [s.strip() for s in text.split("\n") 
                                     if len(s.split()) >= min_words and s.strip() not in sections]
            sections.extend(single_newline_sections)
        
        # If still not enough, try sentence-based splitting
        if len(sections) < 3:
            sentences = re.split(r'[.!?]+', text)
            sentence_groups = []
            current_group = []
            current_word_count = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                word_count = len(sentence.split())
                current_group.append(sentence)
                current_word_count += word_count
                
                if current_word_count >= min_words:
                    group_text = '. '.join(current_group) + '.'
                    if group_text not in sections:
                        sentence_groups.append(group_text)
                    current_group = []
                    current_word_count = 0
            
            sections.extend(sentence_groups)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_sections = []
        for section in sections:
            if section not in seen and len(section.split()) >= min_words:
                seen.add(section)
                unique_sections.append(section)
        
        return unique_sections[:15]  # Limit to top 15 sections per page
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using simple frequency analysis."""
        # Clean and lowercase
        text = self.clean_text(text.lower())
        
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'shall',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
            'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Extract words (minimum 3 characters)
        words = [word for word in re.findall(r'\b\w{3,}\b', text) if word not in stop_words]
        
        # Count frequency
        word_counts = Counter(words)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(20)]
    
    def calculate_relevance_score(self, section: str, task_text: str, persona: str) -> float:
        """Calculate relevance score using keyword matching and context analysis."""
        section_lower = section.lower()
        task_lower = task_text.lower()
        persona_lower = persona.lower()
        
        score = 0.0
        
        # Extract keywords from task and persona
        task_keywords = self.extract_keywords(task_lower)
        persona_keywords = self.extract_keywords(persona_lower)
        section_keywords = self.extract_keywords(section_lower)
        
        # Direct keyword matching
        task_matches = sum(1 for keyword in task_keywords if keyword in section_lower)
        persona_matches = sum(1 for keyword in persona_keywords if keyword in section_lower)
        
        # Weight the matches
        score += task_matches * 2.0  # Task keywords are more important
        score += persona_matches * 1.5
        
        # Check for domain-specific keywords
        combined_text = f"{task_lower} {persona_lower}"
        for domain, keywords in self.domain_keywords.items():
            domain_score = sum(1 for keyword in keywords if keyword in combined_text)
            if domain_score > 0:
                section_domain_score = sum(1 for keyword in keywords if keyword in section_lower)
                score += section_domain_score * 1.0
        
        # Boost score for sections with specific action words
        action_words = ['create', 'manage', 'fill', 'sign', 'convert', 'edit', 'export', 'share', 'process']
        action_matches = sum(1 for word in action_words if word in section_lower)
        score += action_matches * 1.5
        
        # Normalize by section length (favor more substantial content)
        word_count = len(section.split())
        if word_count > 50:
            score *= 1.2
        elif word_count < 20:
            score *= 0.8
        
        # Boost score for sections that seem like instructions or procedures
        if any(phrase in section_lower for phrase in ['step', 'how to', 'to create', 'to fill', 'to sign', 'procedure', 'instructions']):
            score *= 1.3
        
        return score
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Create a summary by extracting key sentences."""
        if len(text.split()) <= 30:
            return text
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) > 3]
        
        if len(sentences) <= 2:
            return text
        
        # Score sentences based on keyword frequency and position
        sentence_scores = []
        all_words = self.extract_keywords(text)
        top_keywords = set(all_words[:10])  # Top 10 keywords
        
        for i, sentence in enumerate(sentences):
            score = 0.0
            sentence_words = set(self.extract_keywords(sentence))
            
            # Keyword overlap score
            keyword_overlap = len(sentence_words.intersection(top_keywords))
            score += keyword_overlap * 2
            
            # Position score (earlier sentences get slight boost)
            if i < len(sentences) * 0.3:
                score += 1
            
            # Length score (prefer medium-length sentences)
            word_count = len(sentence.split())
            if 10 <= word_count <= 25:
                score += 1
            
            sentence_scores.append((sentence, score))
        
        # Sort by score and select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Build summary
        summary_sentences = []
        current_length = 0
        
        for sentence, score in sentence_scores:
            sentence_length = len(sentence.split())
            if current_length + sentence_length <= max_length:
                summary_sentences.append(sentence)
                current_length += sentence_length
            else:
                break
        
        if not summary_sentences:
            # Fallback: return first few sentences
            return '. '.join(sentences[:2]) + '.'
        
        return '. '.join(summary_sentences) + '.'
    
    def extract_title_from_text(self, text: str, max_length: int = 80) -> str:
        """Extract a meaningful title from text."""
        # Clean the text
        text = self.clean_text(text)
        
        # Try to find the first meaningful line
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) >= 3 and len(line) <= 150:
                # Check if it looks like a title (not too many common words)
                common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
                line_words = line.lower().split()
                common_count = sum(1 for word in line_words if word in common_words)
                
                if common_count < len(line_words) * 0.5:  # Less than 50% common words
                    title = line.replace('\n', ' ').strip()
                    if len(title) > max_length:
                        title = title[:max_length-3] + "..."
                    return title
        
        # Fallback: use first few meaningful words
        words = text.split()[:12]
        title = ' '.join(words).replace('\n', ' ')
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        return title if title else "Content Section"
    
    def process_documents(self, input_json_path: str, output_path: str = "output.json", 
                         top_k_sections: int = 5) -> None:
        """Main processing function."""
        logger.info(f"Processing documents from {input_json_path}")
        
        # Load input configuration
        try:
            with open(input_json_path, 'r', encoding='utf-8') as f:
                input_config = json.load(f)
        except Exception as e:
            logger.error(f"Error reading input JSON: {e}")
            return
        
        # Extract configuration with flexible field names
        documents = input_config.get("documents", [])
        persona_info = input_config.get("persona", {})
        job_info = input_config.get("job_to_be_done", {})
        
        # Handle different possible field names
        persona_role = persona_info.get("role", persona_info.get("persona", "User"))
        job_task = job_info.get("task", job_info.get("description", "Process documents"))
        
        # Create metadata
        metadata = {
            "input_documents": [doc["filename"] for doc in documents],
            "persona": persona_role,
            "job_to_be_done": job_task,
            "processing_timestamp": datetime.datetime.now().isoformat(),
            "processor_version": "offline_v1.0"
        }
        
        # Create task context for relevance scoring
        task_context = f"{persona_role}: {job_task}"
        
        all_scored_sections = []
        
        # Process each document
        for doc_info in documents:
            filename = doc_info["filename"]
            
            if not os.path.exists(filename):
                logger.warning(f"File not found: {filename}")
                continue
            
            logger.info(f"Processing {filename}")
            
            # Extract text from PDF
            pages = self.extract_text_by_page(filename)
            
            for page_num, page_text in pages:
                if not page_text.strip():
                    continue
                
                # Split into sections
                sections = self.split_sections(page_text)
                
                if not sections:
                    continue
                
                # Score each section
                for section_text in sections:
                    relevance_score = self.calculate_relevance_score(
                        section_text, job_task, persona_role
                    )
                    
                    all_scored_sections.append({
                        'document': filename,
                        'page_number': page_num,
                        'text': section_text,
                        'score': relevance_score
                    })
        
        # Sort all sections by relevance score
        all_scored_sections.sort(key=lambda x: x['score'], reverse=True)
        
        # Take top k sections
        top_sections = all_scored_sections[:top_k_sections]
        
        # Format output
        extracted_sections = []
        subsection_analysis = []
        
        for i, section_data in enumerate(top_sections, 1):
            # Create section title
            section_title = self.extract_title_from_text(section_data['text'])
            
            # Add to extracted sections
            extracted_sections.append({
                "document": section_data['document'],
                "section_title": section_title,
                "importance_rank": i,
                "page_number": section_data['page_number']
            })
            
            # Summarize and add to subsection analysis
            refined_text = self.summarize_text(section_data['text'])
            subsection_analysis.append({
                "document": section_data['document'],
                "refined_text": refined_text,
                "page_number": section_data['page_number']
            })
        
        # Create output JSON
        output_data = {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        # Write output
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)
            logger.info(f"✅ Output written to {output_path}")
            logger.info(f"Processed {len(top_sections)} relevant sections from {len(set(s['document'] for s in top_sections))} documents")
        except Exception as e:
            logger.error(f"Error writing output: {e}")
def main():
    """Main execution function."""
    input_path = "input.json"
    if not os.path.exists(input_path):
        logger.error(f"Input file {input_path} not found!")
        logger.info("Please create an input.json file with the following structure:")
        logger.info("""
{
    "documents": [
        {"filename": "document1.pdf", "title": "Document 1"}
    ],
    "persona": {"role": "Your role here"},
    "job_to_be_done": {"task": "Your task description here"}
}
        """)
        return
    
    processor = OfflineDocumentProcessor()
    processor.process_documents(input_path)
    logger.info("Processing completed!")

# ✅ Fixed entry point
if __name__ == "__main__":
    main()
