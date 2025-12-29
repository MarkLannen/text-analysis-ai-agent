"""
Ebook Capture Page
Capture ebook pages via screenshot + OCR.
"""
import streamlit as st
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.screenshot_service import ScreenshotService
from services.ocr_service import OCRService
from services.document_service import DocumentService
from services.vector_store import VectorStore
from config.ebook_apps import EBOOK_APPS

st.set_page_config(page_title="Capture", page_icon="📸", layout="wide")


@st.cache_resource
def get_services():
    return {
        "screenshot": ScreenshotService(),
        "ocr": OCRService(),
        "document": DocumentService(),
        "vector": VectorStore()
    }


def main():
    st.title("📸 Ebook Capture")
    st.markdown("Capture ebook pages via screenshot and convert to searchable text using OCR.")

    services = get_services()

    # Initialize session state
    if "capture_pages" not in st.session_state:
        st.session_state.capture_pages = []
    if "capture_running" not in st.session_state:
        st.session_state.capture_running = False

    # Sidebar settings
    with st.sidebar:
        st.subheader("⚙️ Capture Settings")

        # Ebook app selector
        selected_app = st.selectbox(
            "Ebook Reader App",
            options=list(EBOOK_APPS.keys()),
            format_func=lambda x: EBOOK_APPS[x]["name"],
            help="Select the ebook reader application you're using"
        )

        app_config = EBOOK_APPS[selected_app]

        # Capture mode
        capture_mode = st.radio(
            "Capture Mode",
            options=["manual", "auto"],
            format_func=lambda x: "Manual" if x == "manual" else "Auto Page-Turn",
            help="Manual: You click to capture each page. Auto: Automatically captures and turns pages."
        )

        if capture_mode == "auto":
            page_delay = st.slider(
                "Delay between pages (seconds)",
                min_value=0.5,
                max_value=5.0,
                value=1.5,
                step=0.5,
                help="Time to wait after page turn before capturing"
            )

            max_pages = st.number_input(
                "Max pages to capture",
                min_value=1,
                max_value=1000,
                value=50,
                help="Stop after this many pages"
            )

        st.markdown("---")
        st.caption(f"**App tips for {app_config['name']}:**")
        st.caption(app_config.get("tips", "Position the reader window before starting."))

    # Main capture area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📷 Capture Area")

        # Instructions
        with st.expander("📖 How to use", expanded=True):
            st.markdown(f"""
            1. Open **{app_config['name']}** and navigate to the book you want to capture
            2. Position the reader window so the text is clearly visible
            3. Click **"Start Capture"** below
            4. {"Click 'Capture Page' for each page, then manually turn pages" if capture_mode == "manual" else "The app will automatically capture and turn pages"}
            5. When done, click **"Finish & Save"** to process all pages
            """)

        # Capture controls
        if not st.session_state.capture_running:
            if st.button("🎬 Start Capture Session", type="primary", use_container_width=True):
                st.session_state.capture_running = True
                st.session_state.capture_pages = []
                st.rerun()
        else:
            st.success("📸 Capture session active")

            if capture_mode == "manual":
                # Manual capture button
                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    if st.button("📸 Capture Page", use_container_width=True):
                        with st.spinner("Capturing..."):
                            try:
                                screenshot = services["screenshot"].capture_screen()
                                if screenshot:
                                    st.session_state.capture_pages.append(screenshot)
                                    st.success(f"Captured page {len(st.session_state.capture_pages)}")
                            except Exception as e:
                                st.error(f"Capture failed: {str(e)}")

                with col_b:
                    if st.button("⏭️ Skip Page", use_container_width=True):
                        st.info("Skipped - manually turn to next page")

                with col_c:
                    if st.button("🛑 Stop Capture", type="secondary", use_container_width=True):
                        st.session_state.capture_running = False
                        st.rerun()

            else:
                # Auto capture
                col_a, col_b = st.columns(2)

                with col_a:
                    if st.button("▶️ Start Auto Capture", type="primary", use_container_width=True):
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        for i in range(max_pages):
                            status_text.text(f"Capturing page {i + 1} of {max_pages}...")
                            progress_bar.progress((i + 1) / max_pages)

                            try:
                                # Capture screenshot
                                screenshot = services["screenshot"].capture_screen()
                                if screenshot:
                                    st.session_state.capture_pages.append(screenshot)

                                # Simulate page turn
                                services["screenshot"].simulate_page_turn(app_config.get("page_turn_key", "right"))

                                # Wait for page to render
                                time.sleep(page_delay)

                            except Exception as e:
                                status_text.error(f"Error on page {i + 1}: {str(e)}")
                                break

                        status_text.success(f"Captured {len(st.session_state.capture_pages)} pages")
                        st.session_state.capture_running = False
                        st.rerun()

                with col_b:
                    if st.button("🛑 Stop", type="secondary", use_container_width=True):
                        st.session_state.capture_running = False
                        st.rerun()

            # Show capture count
            st.info(f"📄 Pages captured: {len(st.session_state.capture_pages)}")

    with col2:
        st.subheader("📝 Captured Pages")

        if st.session_state.capture_pages:
            # Preview thumbnails
            for i, page in enumerate(st.session_state.capture_pages[-5:]):
                st.image(page, caption=f"Page {len(st.session_state.capture_pages) - 4 + i}", width=200)

            if len(st.session_state.capture_pages) > 5:
                st.caption(f"... and {len(st.session_state.capture_pages) - 5} more pages")

        else:
            st.info("No pages captured yet")

    # Save section
    if st.session_state.capture_pages and not st.session_state.capture_running:
        st.markdown("---")
        st.subheader("💾 Save Captured Book")

        book_name = st.text_input(
            "Book Title",
            placeholder="Enter a name for this book",
            help="This will be the document name in your library"
        )

        if st.button("✅ Process & Save", type="primary", disabled=not book_name):
            with st.spinner("Processing pages with OCR..."):
                all_text = []
                progress_bar = st.progress(0)

                for i, page_image in enumerate(st.session_state.capture_pages):
                    progress_bar.progress((i + 1) / len(st.session_state.capture_pages))

                    try:
                        text = services["ocr"].extract_text(page_image)
                        if text.strip():
                            all_text.append(f"--- Page {i + 1} ---\n{text}")
                    except Exception as e:
                        st.warning(f"OCR failed for page {i + 1}: {str(e)}")

                if all_text:
                    # Combine all text
                    full_text = "\n\n".join(all_text)

                    # Save as document
                    doc_id = services["document"].save_document(
                        name=book_name,
                        content=full_text.encode("utf-8"),
                        mime_type="text/plain"
                    )

                    # Index in vector store
                    services["vector"].add_document(doc_id, full_text, book_name)

                    st.success(f"✅ Saved '{book_name}' with {len(st.session_state.capture_pages)} pages!")

                    # Clear session
                    st.session_state.capture_pages = []
                    st.session_state.capture_running = False

                else:
                    st.error("No text could be extracted from the captured pages.")

        if st.button("🗑️ Discard Captures"):
            st.session_state.capture_pages = []
            st.session_state.capture_running = False
            st.rerun()


if __name__ == "__main__":
    main()
