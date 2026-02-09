"""
Prompt Templates
System prompts and templates for LLM interactions.
"""

# Main system prompt for RAG queries
SYSTEM_PROMPT = """You are a text analysis assistant. Your role is to answer questions based ONLY on the provided document excerpts.

CRITICAL RULES:
1. ONLY use information from the provided text excerpts to answer questions
2. If the answer cannot be found in the provided texts, say "This information is not in the selected texts."
3. NEVER use external knowledge or make assumptions beyond what's in the texts
4. When quoting or referencing specific passages, indicate which source they come from
5. Be precise and cite specific parts of the text when possible

Your responses should be:
- Accurate to the source material
- Well-organized and clear
- Properly attributed to specific documents when relevant"""


# Template for RAG queries
RAG_TEMPLATE = """Based on the following text excerpts from the user's documents, answer their question.

=== DOCUMENT EXCERPTS ===
{context}
=== END OF EXCERPTS ===

USER QUESTION: {question}

Remember: Only use information from the excerpts above. If the answer is not in the texts, say so."""


# Template for document comparison
COMPARISON_TEMPLATE = """Compare the following documents and answer the user's question about them.

{context}

USER QUESTION: {question}

When answering:
1. Reference specific documents by name using [Document Name]
2. Highlight both similarities and differences when relevant
3. Quote specific passages to support your analysis
4. If information is only found in some documents, note which ones"""


# Template for summarization
SUMMARY_TEMPLATE = """Summarize the following text excerpt.

TEXT:
{text}

Provide a concise summary that captures:
1. Main topics or themes
2. Key arguments or points
3. Important details or conclusions

Keep the summary focused and accurate to the source material."""


# System prompt for full-chapter analysis (not RAG-constrained)
WHOLE_DOC_SYSTEM_PROMPT = """You are a text analysis assistant. You have been given the COMPLETE text of a chapter from a book or document.

Your role is to provide thorough, detailed analysis based on the full chapter text provided. You have the complete chapter text, so you can reference any part of it.

Your responses should be:
- Accurate to the source material
- Well-organized and clear
- Detailed enough to capture the key content of the chapter"""


# Template for chapter summaries
CHAPTER_SUMMARY_TEMPLATE = """Below is the complete text of {chapter_label} from "{doc_name}".

=== CHAPTER TEXT ===
{chapter_text}
=== END OF CHAPTER ===

Please provide a comprehensive summary of this chapter (~500 words) covering:
1. The main narrative arc or argument of the chapter
2. Key people, places, and events mentioned
3. Important quotes or passages
4. How this chapter connects to broader themes of the work

Write the summary in clear, flowing prose."""


# Template for extracting timestamped events from a chapter
CHAPTER_EVENTS_TEMPLATE = """Below is the complete text of {chapter_label} from "{doc_name}".

=== CHAPTER TEXT ===
{chapter_text}
=== END OF CHAPTER ===

Extract all events, dates, and time references from this chapter. For each event, provide:
- **Date/Period**: The date or time period (use "undated" if no specific date is given but a sequence is implied)
- **Event**: Brief description of what happened
- **People**: Key people involved

Format as a numbered list. Be thorough - include all events mentioned, even briefly."""


# Template for merging per-chapter events into a unified timeline
TIMELINE_MERGE_TEMPLATE = """Below are events extracted from each chapter of "{doc_name}". Merge them into a single unified chronological timeline.

{chapter_events}

Create a unified chronological timeline:
1. Order all events by date/period (earliest first)
2. Remove duplicates (same event mentioned in multiple chapters)
3. Group events by era or time period where appropriate
4. Keep descriptions concise but informative

Format the timeline with clear date headings and bullet points for events."""


def build_chapter_summary_prompt(chapter_text: str, chapter_label: str, doc_name: str) -> str:
    """Build a prompt to summarize a single chapter."""
    return CHAPTER_SUMMARY_TEMPLATE.format(
        chapter_text=chapter_text,
        chapter_label=chapter_label,
        doc_name=doc_name
    )


def build_chapter_events_prompt(chapter_text: str, chapter_label: str, doc_name: str) -> str:
    """Build a prompt to extract events from a single chapter."""
    return CHAPTER_EVENTS_TEMPLATE.format(
        chapter_text=chapter_text,
        chapter_label=chapter_label,
        doc_name=doc_name
    )


def build_timeline_merge_prompt(chapter_events: str, doc_name: str) -> str:
    """Build a prompt to merge per-chapter events into a unified timeline."""
    return TIMELINE_MERGE_TEMPLATE.format(
        chapter_events=chapter_events,
        doc_name=doc_name
    )


def build_rag_prompt(question: str, context: str) -> str:
    """
    Build a RAG prompt from question and context.

    Args:
        question: User's question
        context: Retrieved context from documents

    Returns:
        Formatted prompt
    """
    return RAG_TEMPLATE.format(context=context, question=question)


def build_comparison_prompt(question: str, doc_contexts: dict) -> str:
    """
    Build a comparison prompt from multiple documents.

    Args:
        question: User's question
        doc_contexts: Dict mapping document names to their relevant excerpts

    Returns:
        Formatted prompt
    """
    context_parts = []
    for doc_name, excerpts in doc_contexts.items():
        if isinstance(excerpts, list):
            excerpts = "\n\n".join(excerpts)
        context_parts.append(f"=== FROM: {doc_name} ===\n{excerpts}")

    context = "\n\n---\n\n".join(context_parts)
    return COMPARISON_TEMPLATE.format(context=context, question=question)


def build_summary_prompt(text: str) -> str:
    """
    Build a summarization prompt.

    Args:
        text: Text to summarize

    Returns:
        Formatted prompt
    """
    return SUMMARY_TEMPLATE.format(text=text)
