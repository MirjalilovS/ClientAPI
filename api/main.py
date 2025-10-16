from typing import Union, Annotated
from . import models, exceptions
from datetime import date, datetime
from .models import UploadData, SummaryData
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from .database import SessionDep, create_db_and_tables
from contextlib import asynccontextmanager
from . import logic
from .logic import process_csv, calc_summary_stats
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
    "/summary/{user_id}",
    response_model=SummaryData,
    status_code=200,
)
async def summarise_data(
    db: SessionDep,
    user_id: int,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
):
    if start_date and end_date and start_date > end_date:
        raise exceptions.InvalidDateRange(
            status_code=400,
            detail="Invalid date range: start_date cannot be after end_date.",
        )

    try:
        summary = calc_summary_stats(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
    except exceptions.NoTransactionsFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    return summary


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
