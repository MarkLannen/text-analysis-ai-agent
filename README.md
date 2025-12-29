# Text Analysis AI Agent

A native desktop application for analyzing and comparing digital texts using LLMs. Upload documents or capture ebooks via screenshot + OCR, then ask questions and get answers grounded solely in your texts.

## Features

- **Document Management** - Upload and manage PDF, TXT, and Markdown files
- **Ebook Capture** - Import ebooks from Kindle, Apple Books, Kobo, and more via screenshot + OCR
- **Chat with Your Texts** - Ask questions and get answers grounded only in your selected documents (RAG)
- **Text Comparison** - Compare 2+ documents side-by-side with AI-powered analysis
- **LLM Agnostic** - Use free local models (Ollama) or paid APIs (OpenAI, Anthropic)
- **Vector Search** - ChromaDB-powered semantic search across your document library

## Prerequisites

### Required

- **Python 3.9+**
- **Tesseract OCR** (for ebook capture feature)

### Optional

- **Node.js 18+** (only if running as Electron desktop app)
- **Ollama** (for free local LLM inference)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MarkLannen/text-analysis-ai-agent.git
cd text-analysis-ai-agent
```

### 2. Set Up Python Environment

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

Tesseract is required for the ebook capture feature.

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

**Windows:**
Download installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### 4. Install Ollama (Optional - for free local LLMs)

Ollama lets you run LLMs locally for free.

1. Download from [ollama.ai](https://ollama.ai)
2. Install and start Ollama
3. Pull a model:
```bash
ollama pull llama3.2
```

Other recommended models:
```bash
ollama pull mistral
ollama pull phi3
```

## Running the Application

### Option A: Run with Streamlit (Recommended for Development)

```bash
cd app
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

### Option B: Run as Desktop App (Electron)

```bash
# Install Electron dependencies
cd electron
npm install

# Start the app
npm start
```

This launches a native desktop window with the Streamlit app embedded.

### Option C: Development Mode (Electron)

```bash
cd electron
npm run dev
```

Opens with DevTools enabled for debugging.

## Configuration

### LLM Providers

Configure your LLM provider in the **Settings** page:

| Provider | Setup Required |
|----------|----------------|
| **Ollama** (default) | Install Ollama + pull a model |
| **OpenAI** | Add your API key in Settings |
| **Anthropic** | Add your API key in Settings |

### Supported Ebook Apps

The capture feature supports these ebook readers:

- Amazon Kindle
- Apple Books
- Kobo Desktop
- Google Play Books (web)
- Barnes & Noble Nook
- Calibre E-book Viewer
- Generic (any reader)

## Usage Guide

### 1. Upload Documents

1. Go to the **Documents** page
2. Upload PDF, TXT, or Markdown files
3. Documents are automatically chunked and indexed in ChromaDB

### 2. Capture Ebooks

1. Go to the **Capture** page
2. Select your ebook reader app
3. Position the reader window with text visible
4. Choose **Manual** or **Auto** capture mode
5. Capture pages → OCR extracts text → Save as document

### 3. Chat with Your Texts

1. Go to the **Chat** page
2. Select one or more documents from the sidebar
3. Ask questions - responses are grounded only in selected texts
4. View source citations for each answer

### 4. Compare Documents

1. Go to the **Compare** page
2. Select 2+ documents
3. Ask comparative questions
4. Get analysis with citations from each source

## Project Structure

```
text-analysis-ai-agent/
├── app/                         # Streamlit application
│   ├── main.py                 # App entry point
│   ├── pages/                  # Streamlit pages
│   │   ├── 1_📄_Documents.py   # Document management
│   │   ├── 2_📸_Capture.py     # Ebook OCR capture
│   │   ├── 3_💬_Chat.py        # Chat interface
│   │   ├── 4_⚖️_Compare.py     # Text comparison
│   │   └── 5_⚙️_Settings.py    # Settings
│   ├── services/               # Core services
│   │   ├── document_service.py # Document CRUD
│   │   ├── vector_store.py     # ChromaDB operations
│   │   ├── llm_service.py      # LLM provider abstraction
│   │   ├── ocr_service.py      # Tesseract OCR
│   │   ├── screenshot_service.py
│   │   └── comparison_service.py
│   ├── config/                 # Configuration
│   │   ├── settings.py         # App settings
│   │   └── ebook_apps.py       # Ebook app configs
│   └── utils/
│       └── prompts.py          # LLM prompt templates
│
├── electron/                    # Electron desktop shell
│   ├── main.js                 # Electron main process
│   ├── preload.js              # IPC bridge
│   └── package.json
│
├── data/                        # Local data (gitignored)
│   ├── documents/              # Uploaded files
│   ├── screenshots/            # Captured screenshots
│   └── chromadb/               # Vector database
│
├── requirements.txt             # Python dependencies
└── README.md
```

## Building for Distribution

### Build Electron App

```bash
cd electron

# macOS
npm run build:mac

# Windows
npm run build:win

# Linux
npm run build:linux
```

Outputs are saved to `electron/dist/`

## Troubleshooting

### "Tesseract not found"
Ensure Tesseract is installed and in your PATH:
```bash
tesseract --version
```

### "Could not connect to Ollama"
Make sure Ollama is running:
```bash
ollama serve
```

### ChromaDB errors
Try clearing the database:
```bash
rm -rf data/chromadb
```

### Screenshot capture not working
On macOS, grant screen recording permission:
System Preferences → Security & Privacy → Privacy → Screen Recording → Enable for Terminal/your IDE

## License

MIT
