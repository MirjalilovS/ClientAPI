import csv
from . import models
from sqlmodel import Session, select, func
from . import exceptions
from datetime import timedelta


def process_csv(db: Session, file) -> int:
    counter = 0
    reader = csv.DictReader(file.read().decode("utf-8").splitlines())
    for row in reader:
        print("Processing row:", row)
        try:
            transaction_data = models.UploadData.model_validate(row)
            db.add(transaction_data)
            counter += 1
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            raise

    db.commit()

    return counter


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
