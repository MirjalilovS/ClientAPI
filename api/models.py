from fastapi import FastAPI
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlmodel import Column, Integer, String, Numeric, DateTime, SQLModel
from pydantic import BaseModel

#SQLModel is a combination of Pydantic and SQLAlchemy meaning we only need one schema
class DatabaseModel(SQLModel):
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    timestamp = Column(DateTime)
    transaction_amount = Column(Numeric(10, 2))
