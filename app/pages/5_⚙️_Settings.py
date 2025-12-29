"""
Settings Page
Configure LLM providers, API keys, and application settings.
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from config.ebook_apps import EBOOK_APPS

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")


@st.cache_resource
def get_settings():
    return Settings()


def main():
    st.title("⚙️ Settings")
    st.markdown("Configure your LLM providers and application preferences.")

    settings = get_settings()
    current_config = settings.get_llm_config()

    # LLM Settings
    st.subheader("🤖 LLM Configuration")

    col1, col2 = st.columns(2)

    with col1:
        provider = st.selectbox(
            "LLM Provider",
            options=["ollama", "openai", "anthropic"],
            format_func=lambda x: {
                "ollama": "Ollama (Local - Free)",
                "openai": "OpenAI (GPT-4)",
                "anthropic": "Anthropic (Claude)"
            }.get(x, x),
            index=["ollama", "openai", "anthropic"].index(current_config.get("provider", "ollama")),
            help="Select your preferred LLM provider"
        )

    with col2:
        # Model options based on provider
        model_options = {
            "ollama": ["llama3.2", "llama3.1", "mistral", "mixtral", "phi3", "gemma2"],
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        }

        current_model = current_config.get("model", model_options[provider][0])
        if current_model not in model_options[provider]:
            current_model = model_options[provider][0]

        model = st.selectbox(
            "Model",
            options=model_options[provider],
            index=model_options[provider].index(current_model) if current_model in model_options[provider] else 0,
            help="Select the model to use"
        )

    # API Key section (for paid providers)
    if provider in ["openai", "anthropic"]:
        st.markdown("---")
        st.subheader("🔑 API Key")

        current_key = current_config.get("api_key", "")
        masked_key = "•" * 20 + current_key[-4:] if current_key and len(current_key) > 4 else ""

        api_key = st.text_input(
            f"{provider.capitalize()} API Key",
            value="",
            type="password",
            placeholder=masked_key if masked_key else "Enter your API key",
            help=f"Your {provider.capitalize()} API key. This will be stored locally."
        )

        if current_key:
            st.caption(f"Current key: {masked_key}")

        st.markdown(f"""
        **How to get an API key:**
        - {'[OpenAI API Keys](https://platform.openai.com/api-keys)' if provider == 'openai' else '[Anthropic Console](https://console.anthropic.com/)'}
        """)
    else:
        api_key = None

        # Ollama instructions
        st.markdown("---")
        st.info("""
        **Ollama Setup Required**

        Ollama runs LLMs locally on your machine for free. To use it:

        1. Install Ollama from [ollama.ai](https://ollama.ai)
        2. Open Terminal and run: `ollama pull llama3.2`
        3. Keep Ollama running in the background

        Once installed, you can use any model by running `ollama pull <model-name>`
        """)

    # Save button
    st.markdown("---")

    if st.button("💾 Save Settings", type="primary"):
        try:
            settings.save_llm_config(
                provider=provider,
                model=model,
                api_key=api_key if api_key else current_config.get("api_key")
            )
            st.success("✅ Settings saved successfully!")
            st.cache_resource.clear()
        except Exception as e:
            st.error(f"Error saving settings: {str(e)}")

    # Test connection
    st.markdown("---")
    st.subheader("🧪 Test Connection")

    if st.button("Test LLM Connection"):
        with st.spinner("Testing connection..."):
            try:
                from services.llm_service import LLMService

                test_config = {
                    "provider": provider,
                    "model": model,
                    "api_key": api_key if api_key else current_config.get("api_key")
                }

                llm = LLMService(
                    provider=test_config["provider"],
                    model=test_config["model"],
                    api_key=test_config.get("api_key")
                )

                response = llm.query("Say 'Connection successful!' in exactly those words.", "")
                st.success(f"✅ Connection successful! Response: {response[:100]}")

            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

    # Ebook App Settings
    st.markdown("---")
    st.subheader("📚 Ebook App Settings")

    st.markdown("Configure settings for different ebook reader applications.")

    for app_key, app_config in EBOOK_APPS.items():
        with st.expander(f"📖 {app_config['name']}"):
            st.caption(app_config.get("tips", ""))
            st.caption(f"Page turn key: `{app_config.get('page_turn_key', 'right')}`")

    # OCR Settings
    st.markdown("---")
    st.subheader("📝 OCR Settings")

    ocr_config = settings.get_ocr_config()

    ocr_lang = st.selectbox(
        "OCR Language",
        options=["eng", "fra", "deu", "spa", "ita", "por", "rus", "chi_sim", "chi_tra", "jpn", "kor"],
        format_func=lambda x: {
            "eng": "English",
            "fra": "French",
            "deu": "German",
            "spa": "Spanish",
            "ita": "Italian",
            "por": "Portuguese",
            "rus": "Russian",
            "chi_sim": "Chinese (Simplified)",
            "chi_tra": "Chinese (Traditional)",
            "jpn": "Japanese",
            "kor": "Korean"
        }.get(x, x),
        index=["eng", "fra", "deu", "spa", "ita", "por", "rus", "chi_sim", "chi_tra", "jpn", "kor"].index(
            ocr_config.get("language", "eng")
        ) if ocr_config.get("language", "eng") in ["eng", "fra", "deu", "spa", "ita", "por", "rus", "chi_sim", "chi_tra", "jpn", "kor"] else 0,
        help="Primary language for OCR recognition"
    )

    if st.button("💾 Save OCR Settings"):
        settings.save_ocr_config(language=ocr_lang)
        st.success("✅ OCR settings saved!")

    # Data Management
    st.markdown("---")
    st.subheader("🗃️ Data Management")

    col1, col2 = st.columns(2)

    with col1:
        data_dir = Path(__file__).parent.parent.parent / "data"
        docs_count = len(list((data_dir / "documents").glob("*.txt"))) if (data_dir / "documents").exists() else 0
        st.metric("Documents Stored", docs_count)

    with col2:
        screenshots_dir = data_dir / "screenshots"
        screenshots_count = len(list(screenshots_dir.glob("*.png"))) if screenshots_dir.exists() else 0
        st.metric("Screenshots Stored", screenshots_count)

    if st.button("🗑️ Clear All Data", type="secondary"):
        st.warning("This will delete all documents, screenshots, and embeddings. This cannot be undone.")
        if st.button("⚠️ Confirm Delete All"):
            # TODO: Implement data clearing
            st.info("Data clearing not implemented yet")


if __name__ == "__main__":
    main()
