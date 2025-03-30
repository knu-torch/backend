from pydantic import BaseModel
from model.enums import summary_options
from fastapi import UploadFile, Form, File

class SummaryRequest(BaseModel):
    summary_options: list[summary_options.SummaryOption]
    project_file: bytes

    @classmethod
    def as_form(
        cls,
        summary_options: list[str] = Form(...),
        project_file: bytes = File()
    ):
        return cls(
            summary_options=summary_options,
            project_file=project_file
        )
