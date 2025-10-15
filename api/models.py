from fastapi import FastAPI
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import declarative_base

# making upload endpoint:
# need sqlalchemy model, pydantic model


class UploadData(BaseModel):
    transaction_id: UUID
    user_id: int
    product_id: int
    timestamp: datetime
    transaction_amount: Decimal


Base = declarative_base()


class DatabaseModel(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    timestamp = Column(DateTime)
    transaction_amount = Column(Numeric(10, 2))
