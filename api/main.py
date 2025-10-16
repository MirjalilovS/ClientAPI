from typing import Union
from models import UploadData
from fastapi import FastAPI
from database import create_db_and_tables
from contextlib import asynccontextmanager

# this module is the router module
app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Creating database and tables...")
    create_db_and_tables()
    yield
    print("INFO:     Application shutting down.")


# finish with this one
@app.get("/summary/{user_id}?start_date={start_date}&end_date={end_date}")
async def read_root():
    return {"Hello": "World"}


# begin with this endpoint
@app.post("/upload")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
