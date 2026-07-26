import re
from typing import Dict, List, Any
from importlib import import_module

documents = import_module("01_documents").documents
preprocess_text = import_module("02_preprocessing").preprocess_text


def chunk_by_paragraphs(text: str, max_words: int = 300, overlap_paragraphs: int = 1) -> List[str]:
    """
    Splits text by natural paragraphs while maintaining context integrity.
    If a paragraph is too large, it gracefully splits without breaking legal meaning.
    """
    # 1. التقسيم بناءً على الفواصل المزدوجة بين الفقرات
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    if not paragraphs:
        return []

    chunks = []
    current_chunk = []
    current_word_count = 0

    for para in paragraphs:
        para_words = len(para.split())
        
        # إذا كانت الفقرة منفردة أكبر من الحد الأقصى، يتم تقسيمها بالجمل
        if para_words > max_words:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sent in sentences:
                sent_words = len(sent.split())
                if current_word_count + sent_words > max_words and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = current_chunk[-overlap_paragraphs:] if len(current_chunk) >= overlap_paragraphs else []
                    current_word_count = sum(len(p.split()) for p in current_chunk)
                
                current_chunk.append(sent)
                current_word_count += sent_words
        else:
            if current_word_count + para_words > max_words and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = current_chunk[-overlap_paragraphs:] if len(current_chunk) >= overlap_paragraphs else []
                current_word_count = sum(len(p.split()) for p in current_chunk)

            current_chunk.append(para)
            current_word_count += para_words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def build_chunks() -> List[Dict[str, Any]]:
    """Builds preprocessed search chunk dicts from document list using paragraph chunking."""
    rows = []

    for document in documents:
        doc_id = document["id"]
        doc_title = document["title"]
        is_current = document["is_current"]
        doc_text = document["text"]

        # زيادة السعة إلى 300 كلمة للفقرة لتستوعب الشروط والقوائم القانونية كاملة
        text_chunks = chunk_by_paragraphs(doc_text, max_words=300, overlap_paragraphs=1)
        
        for chunk_number, chunk in enumerate(text_chunks):
            search_input = f"{doc_title} {chunk}"
            
            rows.append(
                {
                    "chunk_id": f"{doc_id}_{chunk_number}",
                    "document_id": doc_id,
                    "title": doc_title,
                    "is_current": is_current,
                    "chunk_text": chunk,
                    "search_text": preprocess_text(search_input),
                }
            )

    return rows
