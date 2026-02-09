"""
Text Comparison Page
Compare multiple documents side-by-side with AI analysis.
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.document_service import DocumentService
from services.vector_store import VectorStore
from services.llm_service import LLMService
from services.comparison_service import ComparisonService
from config.settings import Settings

st.set_page_config(page_title="Compare", page_icon="⚖️", layout="wide")


@st.cache_resource
def get_services():
    return {
        "document": DocumentService(),
        "vector": VectorStore(),
        "settings": Settings(),
        "comparison": ComparisonService()
    }


def main():
    st.title("⚖️ Compare Texts")
    st.markdown("Compare multiple documents and analyze their similarities and differences.")

    services = get_services()
    documents = services["document"].list_documents()

    if not documents:
        st.warning("No documents uploaded yet. Go to Documents page first.")
        st.stop()

    # Document selection
    st.subheader("📚 Select Documents to Compare")

    col1, col2 = st.columns(2)

    with col1:
        doc1_id = st.selectbox(
            "Document 1",
            options=[None] + [doc["id"] for doc in documents],
            format_func=lambda x: "Select a document..." if x is None else next((d["name"] for d in documents if d["id"] == x), x),
            key="doc1"
        )

    with col2:
        doc2_id = st.selectbox(
            "Document 2",
            options=[None] + [doc["id"] for doc in documents],
            format_func=lambda x: "Select a document..." if x is None else next((d["name"] for d in documents if d["id"] == x), x),
            key="doc2"
        )

    # Optional additional documents
    with st.expander("➕ Add more documents to compare"):
        additional_docs = st.multiselect(
            "Additional documents",
            options=[doc["id"] for doc in documents if doc["id"] not in [doc1_id, doc2_id]],
            format_func=lambda x: next((d["name"] for d in documents if d["id"] == x), x)
        )

    # Collect all selected documents
    selected_ids = [d for d in [doc1_id, doc2_id] + additional_docs if d is not None]

    if len(selected_ids) < 2:
        st.info("👆 Select at least 2 documents to compare")
        st.stop()

    # Check indexing
    unindexed = [
        doc_id for doc_id in selected_ids
        if not services["vector"].is_document_indexed(doc_id)
    ]

    if unindexed:
        st.warning(f"⚠️ {len(unindexed)} document(s) not indexed. Please index them in the Documents page first.")
        st.stop()

    st.success(f"📊 Comparing {len(selected_ids)} documents")

    # Retrieval depth control
    with st.sidebar:
        st.subheader("🔎 Retrieval Depth")
        depth_preset = st.radio(
            "Context per document",
            options=["Focused (3)", "Broad (8)", "Comprehensive (15)", "Custom"],
            index=0,
            help="More chunks = more context but slower responses"
        )

        depth_map = {"Focused (3)": 3, "Broad (8)": 8, "Comprehensive (15)": 15}
        if depth_preset == "Custom":
            compare_n_results = st.slider("Chunks per document", min_value=1, max_value=30, value=3)
        else:
            compare_n_results = depth_map[depth_preset]

        st.caption(f"Retrieving **{compare_n_results}** chunks per document")

    st.markdown("---")

    # Side-by-side view
    st.subheader("📄 Document Previews")

    cols = st.columns(len(selected_ids))
    for i, (col, doc_id) in enumerate(zip(cols, selected_ids)):
        with col:
            doc = services["document"].get_document(doc_id)
            if doc:
                st.markdown(f"**{doc['name']}**")
                st.caption(f"Size: {doc['size']}")
                with st.container(height=300):
                    st.text(doc["content"][:2000] + ("..." if len(doc["content"]) > 2000 else ""))

    st.markdown("---")

    # Comparison chat
    st.subheader("🔍 Ask Comparative Questions")

    # Preset comparison prompts
    preset_prompts = [
        "What are the main themes or topics discussed in each document?",
        "How do the writing styles differ between these documents?",
        "What are the key similarities between these texts?",
        "What are the main differences or contrasting viewpoints?",
        "Summarize each document in 2-3 sentences."
    ]

    st.caption("Quick questions:")
    preset_cols = st.columns(len(preset_prompts))
    selected_preset = None

    for i, (col, prompt) in enumerate(zip(preset_cols, preset_prompts)):
        with col:
            if st.button(f"📝", key=f"preset_{i}", help=prompt):
                selected_preset = prompt

    # Custom question input
    question = st.text_input(
        "Or ask your own question:",
        value=selected_preset if selected_preset else "",
        placeholder="e.g., How does Author A's view on X compare to Author B's perspective?"
    )

    if st.button("🔍 Compare", type="primary", disabled=not question):
        with st.spinner("Analyzing documents..."):
            try:
                # Get relevant chunks from each document
                all_chunks = []
                doc_contexts = {}

                for doc_id in selected_ids:
                    chunks = services["vector"].search(
                        query=question,
                        doc_ids=[doc_id],
                        n_results=compare_n_results
                    )

                    doc = services["document"].get_document(doc_id)
                    doc_name = doc["name"] if doc else "Unknown"

                    doc_contexts[doc_name] = chunks
                    all_chunks.extend(chunks)

                # Build comparison context
                context_parts = []
                for doc_name, chunks in doc_contexts.items():
                    if chunks:
                        doc_text = "\n\n".join([c["content"] for c in chunks])
                        context_parts.append(f"=== FROM: {doc_name} ===\n{doc_text}")

                context = "\n\n---\n\n".join(context_parts)

                # Build comparison prompt
                doc_names = [next((d["name"] for d in documents if d["id"] == doc_id), "Unknown") for doc_id in selected_ids]
                comparison_prompt = f"""Compare the following documents: {', '.join(doc_names)}

Question: {question}

Provide a detailed comparison, citing specific passages from each document. Use [Document Name] to attribute quotes or ideas to specific sources.

If certain information is only found in some documents and not others, note this explicitly."""

                # Get LLM response
                llm_config = services["settings"].get_llm_config()
                llm = LLMService(
                    provider=llm_config["provider"],
                    model=llm_config["model"],
                    api_key=llm_config.get("api_key")
                )

                response = llm.query(comparison_prompt, context)

                # Display response
                st.markdown("### 📊 Comparison Results")
                st.markdown(response)

                # Show sources
                with st.expander("📚 Source Excerpts"):
                    for doc_name, chunks in doc_contexts.items():
                        st.markdown(f"**{doc_name}:**")
                        for chunk in chunks:
                            st.text(chunk["content"][:300] + "...")
                        st.markdown("---")

            except Exception as e:
                st.error(f"Error during comparison: {str(e)}")

    # Comparison history
    if "comparison_history" not in st.session_state:
        st.session_state.comparison_history = []


if __name__ == "__main__":
    main()
