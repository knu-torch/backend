from typing import Annotated
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field,Column, Session, SQLModel, TIMESTAMP, create_engine, select, text


class SummaryRequestEntity(SQLModel, table=True):
    
    __tablename__ = "summary_request"
    
    id: int | None = Field(default=None, primary_key=True)
    req_id: str = Field(default=None, unique=True)
    create_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending") # running, done, failed, pending
