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
        return f"""
# Project Information

| KEY | VALUE |
|------|------|
| ID | {self.id} |
| REQ ID | {self.req_id} |
| CREATE AT | {self.create_at} |

---
\n
## title\n{self.title}\n
## libs\n{self.libs}\n
## deploy_info\n{self.deploy_info}\n      
"""


