from typing import Annotated
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import JSON, Column
from sqlmodel import Field,Column, Session, SQLModel, TIMESTAMP, create_engine, select, text

class SummaryRequestEntity(SQLModel, table=True):
    
    __tablename__ = "summary_request"
    
    id: int | None = Field(default=None, primary_key=True)
    req_id: str = Field(default=None, unique=True)
    create_at: datetime = Field(default_factory=datetime.utcnow)
    file_dir: str = Field(default=None)
    status: str = Field(default="pending") # running, done, failed, pending
    options: dict = Field(sa_column=Column(JSON), default_factory=dict)
    github_url: str = Field(default=None)

    def __str__(self):
        return f"""
        id: {self.id}
        req_id: {self.req_id}
        create_at: {self.create_at}
        status: {self.status}
        options: {self.options}
        file_dir: {self.file_dir}
        """