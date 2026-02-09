"""
Chat Interface Page
Ask questions about your documents using RAG.
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.document_service import DocumentService
from services.vector_store import VectorStore
from services.llm_service import LLMService
from config.settings import Settings

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")


@st.cache_resource
def get_services():
    return {
        "document": DocumentService(),
        "vector": VectorStore(),
        "settings": Settings()
    }


def get_llm_service(settings: Settings):
    """Get LLM service based on current settings."""
    config = settings.get_llm_config()
    return LLMService(
        provider=config["provider"],
        model=config["model"],
        api_key=config.get("api_key")
    )


def main():
    st.title("💬 Chat with Your Texts")
    st.markdown("Ask questions and get answers grounded in your selected documents.")

    services = get_services()
    documents = services["document"].list_documents()

    # Sidebar - Document selection
    with st.sidebar:
        st.subheader("📚 Select Documents")

        if not documents:
            st.warning("No documents uploaded yet. Go to Documents page first.")
            st.stop()

        # Multi-select for documents
        selected_doc_ids = st.multiselect(
            "Choose documents to query",
            options=[doc["id"] for doc in documents],
            format_func=lambda x: next((d["name"] for d in documents if d["id"] == x), x),
            default=st.session_state.get("selected_docs", []),
            help="Select one or more documents to chat about"
        )

        if selected_doc_ids:
            st.success(f"📌 {len(selected_doc_ids)} document(s) selected")

            # Show selected documents
            for doc_id in selected_doc_ids:
                doc = next((d for d in documents if d["id"] == doc_id), None)
                if doc:
                    st.caption(f"• {doc['name']}")
        else:
            st.info("Select at least one document to start chatting")

        st.markdown("---")

        # Retrieval depth control
        st.subheader("🔎 Retrieval Depth")
        depth_preset = st.radio(
            "How much context to retrieve",
            options=["Focused (5)", "Broad (15)", "Comprehensive (30)", "Custom"],
            index=0,
            help="More chunks = more context but slower responses"
        )

        depth_map = {"Focused (5)": 5, "Broad (15)": 15, "Comprehensive (30)": 30}
        if depth_preset == "Custom":
            n_results = st.slider("Number of chunks", min_value=1, max_value=50, value=5)
        else:
            n_results = depth_map[depth_preset]

        st.caption(f"Retrieving **{n_results}** chunks per query")

        st.markdown("---")

        # Model info
        llm_config = services["settings"].get_llm_config()
        st.caption(f"**Model:** {llm_config['model']}")
        st.caption(f"**Provider:** {llm_config['provider']}")

        if st.button("⚙️ Change Model"):
            st.switch_page("pages/5_⚙️_Settings.py")

    # Main chat area
    if not selected_doc_ids:
        st.info("👈 Select documents from the sidebar to start chatting")
        st.stop()

    # Check if documents are indexed
    unindexed = [
        doc_id for doc_id in selected_doc_ids
        if not services["vector"].is_document_indexed(doc_id)
    ]

    if unindexed:
        st.warning(f"⚠️ {len(unindexed)} document(s) not indexed. Please index them in the Documents page first.")
        st.stop()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources if available
            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.caption(f"**{source['doc_name']}** (chunk {source['chunk_index'] + 1})")
                        st.text(source['content'][:200] + "...")

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating response..."):
                try:
                    # Search for relevant chunks
                    chunks = services["vector"].search(
                        query=prompt,
                        doc_ids=selected_doc_ids,
                        n_results=n_results
                    )

                    if not chunks:
                        response = "I couldn't find any relevant information in the selected documents for this question."
                        sources = []
                    else:
                        # Build context from chunks
                        context_parts = []
                        for i, chunk in enumerate(chunks):
                            doc_name = chunk["metadata"].get("doc_name", "Unknown")
                            context_parts.append(f"[Source: {doc_name}]\n{chunk['content']}")

                        context = "\n\n---\n\n".join(context_parts)

                        # Get LLM response
                        llm = get_llm_service(services["settings"])
                        response = llm.query(prompt, context)

                        sources = [
                            {
                                "doc_name": chunk["metadata"].get("doc_name", "Unknown"),
                                "chunk_index": chunk["metadata"].get("chunk_index", 0),
                                "content": chunk["content"]
                            }
                            for chunk in chunks
                        ]

                    st.markdown(response)

                    # Show sources
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.caption(f"**{source['doc_name']}** (chunk {source['chunk_index'] + 1})")
                                st.text(source['content'][:200] + "...")

                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    })

                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
