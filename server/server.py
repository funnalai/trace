import io
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from preprocessing import return_relevant_document_context
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
import requests

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
        db = Prisma()
        await db.connect()
        # post = await db.user.create({})

        return {"hello": "world"}
    except Exception as ex:
        print(ex)
        return {"error": "yes"}

@app.get("/linear")
async def linear():
    try:
        linear_key = os.environ["LINEAR_API_KEY"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": linear_key
        }

        query = {
            "query": "{ issues { nodes { id title } } }"
        }

        response = requests.post("https://api.linear.app/graphql", headers=headers, json=query)
        print(response.json())
        return response.json()
    except Exception as ex:
        print(ex)
        return {"error": "yes"}