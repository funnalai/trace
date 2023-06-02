import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from preprocessing import return_relevant_document_context
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompletionRequestBody(BaseModel):
    context: str


def extract_stream(file: UploadFile = File(...)):
    pdf_as_bytes = file.file.read()
    # We convert the bytes into a Streamable object of bytes
    return io.BytesIO(pdf_as_bytes)


@app.get("/")
async def root():
    try:
        print(os.getenv("LINEAR_API_KEY"))
        # db = Prisma()
        # await db.connect()
        # post = await db.user.create({})

        return {"hello": "world"}
    except Exception as ex:
        print(ex)
        return {"error": "yes"}
