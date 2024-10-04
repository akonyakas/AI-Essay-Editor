# AI Essay Editor

A FastAPI app for editing essays with grammar correction and a user-friendly interface.

## Requirements

- Python 3.12+
- FastAPI
- Uvicorn

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-repository/ai-essay-editor.git
cd ai-essay-editor
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env file and set OpenAI API key

```bash
OPENAI_API_KEY=""
```

### 5. Run uvicorn app

```bash
uvicorn main:app --reload
```

### 6. Access the app

Open: `http://127.0.0.1:8000`

This version is more concise, keeping only the essential steps.
