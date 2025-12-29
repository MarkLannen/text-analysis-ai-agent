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
