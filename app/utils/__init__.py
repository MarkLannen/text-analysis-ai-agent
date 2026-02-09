"""
Utilities package
Helper functions and prompt templates.
"""
from .prompts import (
    SYSTEM_PROMPT,
    RAG_TEMPLATE,
    COMPARISON_TEMPLATE,
    WHOLE_DOC_SYSTEM_PROMPT,
    CHAPTER_SUMMARY_TEMPLATE,
    CHAPTER_EVENTS_TEMPLATE,
    TIMELINE_MERGE_TEMPLATE,
    build_rag_prompt,
    build_comparison_prompt,
    build_summary_prompt,
    build_chapter_summary_prompt,
    build_chapter_events_prompt,
    build_timeline_merge_prompt,
)

__all__ = [
    'SYSTEM_PROMPT',
    'RAG_TEMPLATE',
    'COMPARISON_TEMPLATE',
    'WHOLE_DOC_SYSTEM_PROMPT',
    'CHAPTER_SUMMARY_TEMPLATE',
    'CHAPTER_EVENTS_TEMPLATE',
    'TIMELINE_MERGE_TEMPLATE',
    'build_rag_prompt',
    'build_comparison_prompt',
    'build_summary_prompt',
    'build_chapter_summary_prompt',
    'build_chapter_events_prompt',
    'build_timeline_merge_prompt',
]
