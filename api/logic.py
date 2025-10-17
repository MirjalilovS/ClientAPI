import csv
from . import models
from sqlmodel import Session, select, func
from . import exceptions
from datetime import timedelta
from pydantic import ValidationError
import io

BATCH_SIZE = 1000


def process_csv(db: Session, file) -> int:
    counter = 0
    text_stream = io.TextIOWrapper(file, encoding="utf-8")
    reader = csv.DictReader(text_stream)
    try:
        for row in reader:
            # Create a model instance from the row
            transaction_data = models.UploadData.model_validate(row)

            # Add the object to the database session
            db.add(transaction_data)
            counter += 1

            # 2. COMMIT in batches to keep memory usage low and transactions small
            if counter % BATCH_SIZE == 0:
                db.commit()
                print(f"Committed batch of {BATCH_SIZE} transactions. Total: {counter}")

        # 3. Commit any remaining transactions after the loop
        db.commit()
        print(f"Committed final batch. Total processed: {counter}")

        return counter
    except ValidationError as e:
        db.rollback()  # Roll back the current batch if an error occurs
        raise exceptions.CSVProcessingError(
            f"Invalid data in CSV at row ~{counter + 1}: {e}"
        )
    except Exception as e:
        db.rollback()
        raise exceptions.CSVProcessingError(
            f"An unexpected error occurred at row ~{counter + 1}: {e}"
        )


def calc_summary_stats(
    db: Session, user_id: int, start_date: str = None, end_date: str = None
):
    statement = select(
        func.max(models.UploadData.transaction_amount),
        func.min(models.UploadData.transaction_amount),
        func.avg(models.UploadData.transaction_amount),
        func.sum(models.UploadData.transaction_amount),
        func.count(models.UploadData.transaction_amount),
    ).where(models.UploadData.user_id == user_id)

    if start_date:
        statement = statement.where(models.UploadData.timestamp >= start_date)
    if end_date:
        end_date = end_date + timedelta(days=1)
        statement = statement.where(models.UploadData.timestamp < end_date)

    result = db.exec(statement).one_or_none()

    if not result or result[0] is None:
        raise exceptions.NoTransactionsFoundError(
            "No transactions found for the given user and/or date range."
        )

    max_amount, min_amount, mean_amount, total_amount, transaction_count = result
    rounded_mean = round(float(mean_amount), 2)
    summary = models.SummaryData(
        user_id=user_id,
        total_amount=total_amount,
        max_amount=max_amount,
        min_amount=min_amount,
        mean_amount=rounded_mean,
        transaction_count=transaction_count,
    )
    return summary
