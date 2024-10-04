from fastapi import FastAPI, Request
from pydantic import BaseModel
from essay_editor import EssayEditor
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


static_path = os.path.join(os.getcwd(), "static")
print(f"Mounting static files from {static_path}")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load HTML templates
templates = Jinja2Templates(directory="templates")


class EditRequest(BaseModel):
    text: str
    user_prompt: str


class SentenceRevision(BaseModel):
    original_sentence: str
    revised_sentence: Optional[str]
    explanation: Optional[str]


@app.post("/edit_text")
def process_text(edit_request: EditRequest) -> List[SentenceRevision]:
    editor = EssayEditor(edit_request.user_prompt)
    result = editor.process_text(edit_request.text)
    return result


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    print(f"Serving index.html to {request.client.host}")
    return templates.TemplateResponse("index.html", {"request": request})
