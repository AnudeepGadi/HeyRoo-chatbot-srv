from typing import Annotated, Optional
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from client import QueryRpcClient
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import pika

class Query(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

if __name__ == "__main__":
    app = FastAPI()
    origins = [
        "http://localhost"
    ]

    app.mount("/static", StaticFiles(directory="static"), name="static")   

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    query_rpc_client = QueryRpcClient()

    @app.get("/")
    async def home():
        return FileResponse("index.html")

    @app.post("/query", response_model=Answer)
    async def handle_query(query:Query):
        return Answer(answer=query_rpc_client.call(query.question))
    
    uvicorn.run(app, port=5000)

