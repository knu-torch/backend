from typing import Annotated
from model.payload import summary
from fastapi import Form, APIRouter, UploadFile, File, Depends

router = APIRouter(
    prefix="/summary",
    tags=["summary"]
)

@router.post("")
async def post_summary_request_handler(
    form_data: summary.SummaryRequest = Depends(summary.SummaryRequest.as_form),
):
    print(form_data.project_file)
    return { "message" : "OK" }
