from typing import Union
from models import UploadData
from fastapi import FastAPI, UploadFile, File, HTTPException
from database import create_db_and_tables, SessionDep
from contextlib import asynccontextmanager
from logic import process_csv_upload

# this module is the router module
app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Creating database and tables...")
    create_db_and_tables()
    yield
    print("INFO:     Application shutting down.")


# finish with this one, response model is temporary
@app.get("/summary/{user_id}?start_date={start_date}&end_date={end_date}", response_model=UploadData)
async def read_root():
    return {"Hello": "World"}


# begin with this endpoint
@app.post("/upload", status_code=201)
async def upload_transactions(db: SessionDep, file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    try:
          processed_count = process_csv_upload(db=db, file=file.file)
          return {"message": f"Successfully uploaded and processed {processed_count} transactions."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {str(e)}")
