from typing import Annotated
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Column, Session, SQLModel, TIMESTAMP, create_engine, select, text


class SummaryProjectEntity(SQLModel, table=True):
    __tablename__ = "summary_project"

    id: int | None = Field(default=None, primary_key=True)
    req_id: str = Field(default=None, unique=True)
    create_at: datetime = Field(default_factory=datetime.utcnow)
    title: str = Field(default=None)
    libs: str = Field(default=None)
    deploy_info: str = Field(default=None)

    def __str__(self):
        return f""""
        Project Information
        
        id={self.id} 
        req_id={self.req_id}, 
        create_at={self.create_at}, 
        title={self.title}, 
        libs={self.libs}, 
        deploy_info={self.deploy_info}
    """


