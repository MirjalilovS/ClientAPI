from fastapi import FastAPI
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


# SQLModel is a combination of Pydantic and SQLAlchemy meaning we only need one schema
class UploadData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    transaction_id: UUID = Field(index=True)
    user_id: int = Field(index=True)
    product_id: int
    timestamp: datetime
    transaction_amount: Decimal = Field(max_digits=10, decimal_places=2)


class SummaryData(BaseModel):
    user_id: int
    total_amount: Decimal
    max_amount: Decimal
    min_amount: Decimal
    mean_amount: Decimal
    transaction_count: int
