from pydantic import BaseModel
from model.enums.summary_options import SummaryInputType, SummaryOption
from fastapi import UploadFile, Form, File, HTTPException
import json
import logging

logger = logging.getLogger(__name__)

class SummaryRequest(BaseModel):
    summary_options: list[SummaryOption]
    mode: SummaryInputType
    project_file: UploadFile | None = None
    github_url: str | None = None

    @classmethod
    def as_form(
        cls,
        summary_options: str = Form(...),
        mode: SummaryInputType = Form(...),
        project_file: UploadFile | None = File(None),
        github_url: str | None = Form(None)
    ):

        try:
            parsed = json.loads(summary_options)
        except json.JSONDecodeError as e:
            logger.warning(f"[summary_options] JSON decode error: {e}")
            raise HTTPException(
                status_code=400,
                detail="summary_options must be a valid JSON string list"
            )

        if mode == SummaryInputType.Zip and project_file is None:
            logger.warning("Missing file for zip mode")
            raise HTTPException(
                status_code=400,
                detail="project_file is required when mode is 'Zip'"
            )

        if mode == SummaryInputType.Github and not github_url:
            logger.warning("Missing github_url for github mode")
            raise HTTPException(
                status_code=400,
                detail="github_url is required when mode is 'Github'"
            )
        return cls(
            summary_options=parsed,
            mode=mode,
            project_file=project_file,
            github_url=github_url
        )
