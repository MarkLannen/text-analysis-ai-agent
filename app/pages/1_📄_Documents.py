"""
Document Management Page
Upload, view, and manage text documents.
"""
import streamlit as st
from pathlib import Path
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.document_service import DocumentService
from services.vector_store import VectorStore

st.set_page_config(page_title="Documents", page_icon="📄", layout="wide")

# Initialize services
@st.cache_resource
def get_document_service():
    return DocumentService()

@st.cache_resource
def get_vector_store():
    return VectorStore()

doc_service = get_document_service()
vector_store = get_vector_store()


def main():
    st.title("📄 Document Management")
    st.markdown("Upload and manage your text documents for analysis.")

    # Upload section
    st.subheader("Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
        help="Supported formats: TXT, Markdown, PDF"
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    # Save document
                    doc_id = doc_service.save_document(
                        uploaded_file.name,
                        uploaded_file.read(),
                        uploaded_file.type
                    )

                    # Get text content and embed
                    doc = doc_service.get_document(doc_id)
                    if doc:
                        vector_store.add_document(doc_id, doc["content"], doc["name"])
                        st.success(f"✅ Uploaded and indexed: {uploaded_file.name}")

                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")

    st.markdown("---")

    # Document library
    st.subheader("📚 Document Library")

    documents = doc_service.list_documents()

    if not documents:
        st.info("No documents uploaded yet. Upload some files above to get started!")
    else:
        # Selection for analysis
        if "selected_docs" not in st.session_state:
            st.session_state.selected_docs = []

        st.markdown("**Select documents for analysis:**")

        # Create columns for document cards
        for doc in documents:
            col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])

            with col1:
                selected = st.checkbox(
                    "Select",
                    key=f"select_{doc['id']}",
                    value=doc['id'] in st.session_state.selected_docs,
                    label_visibility="collapsed"
                )
                if selected and doc['id'] not in st.session_state.selected_docs:
                    st.session_state.selected_docs.append(doc['id'])
                elif not selected and doc['id'] in st.session_state.selected_docs:
                    st.session_state.selected_docs.remove(doc['id'])

            with col2:
                st.markdown(f"**{doc['name']}**")
                st.caption(f"Added: {doc['created_at']} | Size: {doc['size']}")

            with col3:
                # Embedding status
                if vector_store.is_document_indexed(doc['id']):
                    st.success("Indexed", icon="✅")
                else:
                    if st.button("Index", key=f"index_{doc['id']}"):
                        with st.spinner("Indexing..."):
                            full_doc = doc_service.get_document(doc['id'])
                            if full_doc:
                                vector_store.add_document(doc['id'], full_doc["content"], full_doc["name"])
                                st.rerun()

            with col4:
                if st.button("🗑️", key=f"delete_{doc['id']}", help="Delete document"):
                    doc_service.delete_document(doc['id'])
                    vector_store.delete_document(doc['id'])
                    if doc['id'] in st.session_state.selected_docs:
                        st.session_state.selected_docs.remove(doc['id'])
                    st.rerun()

        # Show selection summary
        st.markdown("---")
        num_selected = len(st.session_state.selected_docs)
        if num_selected > 0:
            st.success(f"📌 {num_selected} document(s) selected for analysis")
            if st.button("Clear Selection"):
                st.session_state.selected_docs = []
                st.rerun()
        else:
            st.info("Select documents above to use them in Chat or Compare")


if __name__ == "__main__":
    main()
