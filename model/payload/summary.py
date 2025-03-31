from pydantic import BaseModel
from model.enums import summary_options
from fastapi import UploadFile, Form, File
import json

class SummaryRequest(BaseModel):
    summary_options: list[summary_options.SummaryOption]
    project_file: UploadFile

    @classmethod
    def as_form(
        cls,
        summary_options: str = Form(...),
        project_file: UploadFile = File(...)
    ):
        try:
            parsed = json.loads(summary_options)
        except json.JSONDecodeError:
            raise ValueError("summary_options must be a valid JSON string list")

        return cls(
            summary_options=parsed,
            project_file=project_file
        )
