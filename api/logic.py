import csv
from . import models
from sqlmodel import Session


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
