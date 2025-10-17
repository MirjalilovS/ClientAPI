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

app = FastAPI(
    title="E-Commerce Transaction API",
    description="An API to upload and summarize large datasets of e-commerce transactions.",
    version="1.0.0",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Creating database and tables...")
    create_db_and_tables()
    yield
    print("INFO:     Application shutting down.")


@app.get(
    "/summary/{user_id}",
    response_model=SummaryData,
    status_code=200,
)
async def summarise_data(
    db: SessionDep,
    user_id: int,
    start_date: Annotated[datetime | None, Query()] = None,
    end_date: Annotated[datetime | None, Query()] = None,
):
    """
    Retrieves summary statistics for a specific user, optionally filtered by a date range.

    This endpoint calculates the maximum, minimum, mean, sum, and total count of
    transaction amounts for the given `user_id`. If `start_date` and `end_date`
    are provided, only transactions within that inclusive range are considered.
    """
    try:
        if start_date and end_date and start_date > end_date:
            raise exceptions.InvalidDateRange(
                "Invalid date range: start_date cannot be after end_date.",
            )
        summary = calc_summary_stats(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
    except exceptions.NoTransactionsFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except exceptions.InvalidDateRange as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    return summary


@app.post("/upload", status_code=201)
async def upload_transactions(db: SessionDep, file: UploadFile = File(...)):
    """
    Uploads a CSV file with transaction data.

    The file is processed row by row, validated, and saved to the database.
    Returns a count of the successfully processed transactions.
    """
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
