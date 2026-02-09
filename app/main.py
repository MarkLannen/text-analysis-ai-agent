"""
Text Analysis AI Agent - Main Streamlit Application
"""
import streamlit as st
from pathlib import Path
import sys

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.document_service import DocumentService
from config.settings import Settings

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Text Analysis AI Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""

    # Sidebar
    with st.sidebar:
        st.title("📚 Text Analysis")
        st.markdown("---")
        st.markdown("""
        **Navigation**
        - 📄 Documents - Manage your texts
        - 📸 Capture - Import ebooks via OCR
        - 💬 Chat - Ask questions about texts
        - ⚖️ Compare - Compare multiple texts
        - 📖 Deep Analysis - Chapter summaries & timelines
        - ⚙️ Settings - Configure LLM & options
        """)

        st.markdown("---")
        st.caption("v0.1.0 - Powered by LLMs")

    # Main content
    st.markdown('<p class="main-header">📚 Text Analysis AI Agent</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze and compare texts using AI - with responses grounded only in your documents.</p>', unsafe_allow_html=True)

    # Feature cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📄 Document Management</h3>
            <p>Upload and manage your text documents. Supports PDF, TXT, and Markdown files.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>💬 Chat with Your Texts</h3>
            <p>Ask questions and get answers grounded solely in your selected documents.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📸 Ebook Capture</h3>
            <p>Import ebooks from Kindle, Apple Books, and more via screenshot + OCR.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>⚖️ Compare Texts</h3>
            <p>Compare 2 or more texts side-by-side with AI-powered analysis.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>📖 Deep Analysis</h3>
            <p>Chapter-by-chapter summaries, chronological timelines, and full-chapter Q&A.</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick start
    st.markdown("---")
    st.subheader("🚀 Quick Start")
    st.markdown("""
    1. **Upload documents** in the Documents page
    2. **Configure your LLM** in Settings (free Ollama models available)
    3. **Start chatting** with your texts in the Chat page
    """)

    # Status
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    doc_service = DocumentService()
    settings = Settings()
    llm_config = settings.get_llm_config()

    with col1:
        st.metric("Documents", len(doc_service.list_documents()))

    with col2:
        provider_labels = {
            "ollama": "Ollama",
            "openai": "OpenAI",
            "anthropic": "Anthropic"
        }
        provider = llm_config.get("provider", "ollama")
        st.metric("LLM Provider", provider_labels.get(provider, provider))

    with col3:
        st.metric("Status", "Ready")


if __name__ == "__main__":
    main()
