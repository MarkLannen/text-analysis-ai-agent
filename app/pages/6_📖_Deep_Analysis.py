"""
Deep Analysis Page
Chapter-aware document analysis: summaries, timelines, and chapter Q&A.
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.document_service import DocumentService
from services.chapter_service import ChapterService
from services.llm_service import LLMService
from config.settings import Settings
from utils.prompts import (
    WHOLE_DOC_SYSTEM_PROMPT,
    build_chapter_summary_prompt,
    build_chapter_events_prompt,
    build_timeline_merge_prompt,
)

st.set_page_config(page_title="Deep Analysis", page_icon="📖", layout="wide")


@st.cache_resource
def get_services():
    doc_service = DocumentService()
    return {
        "document": doc_service,
        "chapter": ChapterService(doc_service),
        "settings": Settings(),
    }


def get_llm(settings: Settings) -> LLMService:
    config = settings.get_llm_config()
    return LLMService(
        provider=config["provider"],
        model=config["model"],
        api_key=config.get("api_key"),
    )


def main():
    st.title("📖 Deep Analysis")
    st.markdown("Analyze entire chapters: summaries, timelines, and targeted Q&A with full chapter context.")

    services = get_services()
    documents = services["document"].list_documents()

    # --- Sidebar ---
    with st.sidebar:
        st.subheader("📚 Select Document")

        if not documents:
            st.warning("No documents uploaded yet. Go to Documents page first.")
            st.stop()

        doc_id = st.selectbox(
            "Document",
            options=[doc["id"] for doc in documents],
            format_func=lambda x: next((d["name"] for d in documents if d["id"] == x), x),
        )

        doc = services["document"].get_document(doc_id)
        if doc:
            st.caption(f"**Size:** {doc['size']}")
            st.caption(f"**Characters:** {doc['text_length']:,}")

        st.markdown("---")
        llm_config = services["settings"].get_llm_config()
        st.caption(f"**Model:** {llm_config['model']}")
        st.caption(f"**Provider:** {llm_config['provider']}")

    if not doc_id or not doc:
        st.info("Select a document from the sidebar.")
        st.stop()

    doc_name = doc["name"]

    # --- Chapter Detection ---
    st.subheader("📑 Chapter Detection")

    # Initialize session state for this document
    state_key = f"chapters_{doc_id}"
    if state_key not in st.session_state:
        # Try loading cached chapters
        cached = services["chapter"].get_chapters(doc_id)
        if cached:
            st.session_state[state_key] = cached

    if st.button("🔍 Detect Chapters", type="primary"):
        with st.spinner("Scanning document for chapter boundaries..."):
            chapters = services["chapter"].detect_chapters(doc_id)
            if chapters:
                services["chapter"].save_chapters(doc_id, chapters)
                st.session_state[state_key] = chapters
                st.success(f"Found {len(chapters)} chapter(s)")
            else:
                st.warning("No chapter boundaries detected. The document may not have clear chapter markers.")

    chapters = st.session_state.get(state_key, [])

    if not chapters:
        st.info("Click **Detect Chapters** to scan the document for chapter boundaries.")
        st.stop()

    # Show chapter table
    st.markdown(f"**{len(chapters)} chapters detected:**")
    chapter_data = []
    for ch in chapters:
        chapter_data.append({
            "Chapter": ch["number"],
            "Title": ch["title"],
            "Length": f"{ch['char_count']:,} chars",
        })
    st.dataframe(chapter_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- Tabs ---
    tab_summaries, tab_timeline, tab_qa = st.tabs(["📝 Chapter Summaries", "📅 Timeline", "❓ Chapter Q&A"])

    # === Chapter Summaries Tab ===
    with tab_summaries:
        st.markdown("Generate detailed summaries of each chapter using the full chapter text.")

        summaries_key = f"summaries_{doc_id}"
        if summaries_key not in st.session_state:
            st.session_state[summaries_key] = {}

        if st.button("📝 Generate All Summaries", type="primary", key="gen_summaries"):
            llm = get_llm(services["settings"])
            progress_bar = st.progress(0, text="Starting...")

            for i, ch in enumerate(chapters):
                chapter_label = f"Chapter {ch['number']}" if ch["number"].isdigit() else ch["number"]
                progress_bar.progress(
                    (i) / len(chapters),
                    text=f"Summarizing {chapter_label}..."
                )

                chapter_text = services["chapter"].get_chapter_text(doc_id, ch["index"])
                if not chapter_text:
                    continue

                prompt = build_chapter_summary_prompt(chapter_text, chapter_label, doc_name)
                summary = llm.generate_with_system(prompt, WHOLE_DOC_SYSTEM_PROMPT)
                st.session_state[summaries_key][ch["index"]] = summary

            progress_bar.progress(1.0, text="All summaries complete!")

        # Display summaries
        summaries = st.session_state.get(summaries_key, {})
        if summaries:
            for ch in chapters:
                if ch["index"] in summaries:
                    chapter_label = f"Chapter {ch['number']}" if ch["number"].isdigit() else ch["number"]
                    with st.expander(f"{chapter_label}: {ch['title']}", expanded=False):
                        st.markdown(summaries[ch["index"]])
        elif not st.session_state.get("_generating"):
            st.info("Click **Generate All Summaries** to analyze each chapter.")

    # === Timeline Tab ===
    with tab_timeline:
        st.markdown("Extract events from each chapter and merge into a chronological timeline.")

        timeline_key = f"timeline_{doc_id}"
        events_key = f"chapter_events_{doc_id}"

        if events_key not in st.session_state:
            st.session_state[events_key] = {}

        if st.button("📅 Generate Timeline", type="primary", key="gen_timeline"):
            llm = get_llm(services["settings"])
            progress_bar = st.progress(0, text="Starting event extraction...")

            # Phase 1: Extract events from each chapter
            all_chapter_events = {}
            for i, ch in enumerate(chapters):
                chapter_label = f"Chapter {ch['number']}" if ch["number"].isdigit() else ch["number"]
                progress_bar.progress(
                    i / (len(chapters) + 1),
                    text=f"Extracting events from {chapter_label}..."
                )

                chapter_text = services["chapter"].get_chapter_text(doc_id, ch["index"])
                if not chapter_text:
                    continue

                prompt = build_chapter_events_prompt(chapter_text, chapter_label, doc_name)
                events = llm.generate_with_system(prompt, WHOLE_DOC_SYSTEM_PROMPT)
                all_chapter_events[chapter_label] = events

            st.session_state[events_key] = all_chapter_events

            # Phase 2: Merge into unified timeline
            progress_bar.progress(
                len(chapters) / (len(chapters) + 1),
                text="Merging into unified timeline..."
            )

            chapter_events_text = ""
            for label, events in all_chapter_events.items():
                chapter_events_text += f"\n\n=== {label} ===\n{events}"

            merge_prompt = build_timeline_merge_prompt(chapter_events_text, doc_name)
            timeline = llm.generate_with_system(merge_prompt, WHOLE_DOC_SYSTEM_PROMPT)
            st.session_state[timeline_key] = timeline

            progress_bar.progress(1.0, text="Timeline complete!")

        # Display timeline
        if timeline_key in st.session_state:
            st.markdown("### Unified Timeline")
            st.markdown(st.session_state[timeline_key])

            # Show per-chapter events in expander
            chapter_events = st.session_state.get(events_key, {})
            if chapter_events:
                with st.expander("Per-chapter event details"):
                    for label, events in chapter_events.items():
                        st.markdown(f"**{label}:**")
                        st.markdown(events)
                        st.markdown("---")
        else:
            st.info("Click **Generate Timeline** to extract events and build a chronological timeline.")

    # === Chapter Q&A Tab ===
    with tab_qa:
        st.markdown("Ask questions about a specific chapter using the full chapter text as context.")

        # Chapter selector
        chapter_options = []
        for ch in chapters:
            label = f"Chapter {ch['number']}" if ch["number"].isdigit() else ch["number"]
            chapter_options.append((ch["index"], f"{label}: {ch['title']} ({ch['char_count']:,} chars)"))

        selected_chapter_idx = st.selectbox(
            "Select a chapter",
            options=[opt[0] for opt in chapter_options],
            format_func=lambda x: next(opt[1] for opt in chapter_options if opt[0] == x),
            key="qa_chapter_select",
        )

        question = st.text_input(
            "Ask a question about this chapter:",
            placeholder="e.g., What are the main arguments in this chapter?",
            key="chapter_qa_input",
        )

        qa_key = f"chapter_qa_{doc_id}"
        if qa_key not in st.session_state:
            st.session_state[qa_key] = []

        if st.button("🔍 Ask", type="primary", key="chapter_qa_ask", disabled=not question):
            chapter_text = services["chapter"].get_chapter_text(doc_id, selected_chapter_idx)
            if not chapter_text:
                st.error("Could not retrieve chapter text.")
            else:
                ch = chapters[selected_chapter_idx]
                chapter_label = f"Chapter {ch['number']}" if ch["number"].isdigit() else ch["number"]

                with st.spinner(f"Analyzing {chapter_label}..."):
                    llm = get_llm(services["settings"])

                    prompt = f"""Below is the complete text of {chapter_label} from "{doc_name}".

=== CHAPTER TEXT ===
{chapter_text}
=== END OF CHAPTER ===

Question: {question}

Answer the question based on the chapter text above. Be thorough and cite specific passages where relevant."""

                    response = llm.generate_with_system(prompt, WHOLE_DOC_SYSTEM_PROMPT)

                    st.session_state[qa_key].append({
                        "chapter": chapter_label,
                        "question": question,
                        "answer": response,
                    })

        # Display Q&A history
        qa_history = st.session_state.get(qa_key, [])
        if qa_history:
            for entry in reversed(qa_history):
                with st.expander(f"**[{entry['chapter']}]** {entry['question']}", expanded=(entry == qa_history[-1])):
                    st.markdown(entry["answer"])

            if st.button("🗑️ Clear Q&A History", key="clear_qa"):
                st.session_state[qa_key] = []
                st.rerun()


if __name__ == "__main__":
    main()
