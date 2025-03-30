from typing import Annotated
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field,Column, Session, SQLModel, TIMESTAMP, create_engine, select, text


class Request(SQLModel, table=True):
    
    __tablename__ = "request"
    
    id: int | None = Field(default=None, primary_key=True)
    create_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending")
