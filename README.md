
# ExtractIQ — AI Data Extraction Bot

ExtractIQ converts unstructured resume and invoice text into structured JSON using Google Gemini and Pydantic.

## Features

- Resume and invoice extraction
- Schema-constrained JSON output
- Missing-field handling
- JSON preview and download
- User-friendly API error messages
- Private API-key configuration

## Run locally

Install Python 3.10 or newer.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file with your own Gemini API key:

```dotenv
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-3.8-flash
```

Run the application:

```bash
streamlit run app.py
```

## Deploy on Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

Set these Environment Variables privately in Render:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`

Never commit `.env` or expose API keys.

## Limitations

This version extracts from pasted text. PDF parsing and a FastAPI `/api/extract` endpoint are not included.
A Gemini quota or model-access error must be resolved through the Google AI account settings.
