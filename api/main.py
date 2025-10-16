from typing import Union
from . import models
from .models import UploadData
from fastapi import FastAPI, UploadFile, File, HTTPException
from .database import SessionDep, create_db_and_tables
from contextlib import asynccontextmanager
from . import logic
from .logic import process_csv
import traceback

# this module is the router module
app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Creating database and tables...")
    create_db_and_tables()
    yield
    print("INFO:     Application shutting down.")


# finish with this one, response model is temporary
@app.get(
    "/summary/{user_id}?start_date={start_date}&end_date={end_date}",
    response_model=UploadData,
    status_code=200,
)
async def summarise_data():
    try:
        return {"message": "Successfully summarised data."}
    # this exception will need improvement
    except Exception as e:
        print("---Detailed error traceback---")
        traceback.print_exc()
        print("---End of traceback---")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while summarising the data: {str(e)}",
        )


# begin with this endpoint
@app.post("/upload", status_code=201)
async def upload_transactions(db: SessionDep, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )

    try:
        processed_count = process_csv(db=db, file=file.file)
        return {
            "message": f"Successfully uploaded and processed {processed_count} transactions."
        }
    except Exception as e:
        print("---Detailed error traceback---")
        traceback.print_exc()
        print("---End of traceback---")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}",
        )
