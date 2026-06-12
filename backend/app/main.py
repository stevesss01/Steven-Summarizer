from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.summarize import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():

    return {
        "message":
        "Steven Summarizer API Running"
    }