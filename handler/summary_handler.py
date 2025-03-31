from fastapi import Form, APIRouter, UploadFile, File, Depends, Request
from fastapi.responses import FileResponse
import uuid
import os
import zipfile
from io import BytesIO

from model.payload import summary
from utils.utils import create_pdf
from ai import AI

MAX_MEMORY_ZIP_SIZE = 50 * 1024 * 1024
SUMMARY_RESULT_FILE_NAME = "summary_result.pdf"

router = APIRouter(
    prefix="/summary",
    tags=["summary"]
)

@router.post("")
async def post_summary_request_handler(
    request: Request,
    form_data: summary.SummaryRequest = Depends(summary.SummaryRequest.as_form),
):
    print(form_data.project_file)
    print(form_data.summary_options)

    request_id = str(uuid.uuid4())

    # TODO: db 연결 및 status running으로 set


    # zip파일 unzip 후 저장 dir
    temp_dir = f"temp/{request_id}"

    os.makedirs(temp_dir, exist_ok=True)

    file_bytes = await form_data.project_file.read()
    file_size = len(file_bytes)

    # zip 용량에 따른 처리 차별
    if file_size <= MAX_MEMORY_ZIP_SIZE:
        file_stream = BytesIO(file_bytes)
        with zipfile.ZipFile(file_stream, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    else:
        file_path = os.path.join(temp_dir, form_data.project_file.filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

    # llm 처리, db  저장
    summary_result = AI(temp_dir, form_data.summary_options)

    # TODO: db status 변경



    base_url = str(request.base_url).rstrip("/")
    result_url = f"{base_url}/summary/{request_id}"

    return {
        "message" : "OK",
        "request_id" : f"{request_id}",
        "result_url" : result_url
    }



@router.get("/{request_id}")
async def get_summary_result(request_id: str):
    # TODO: request_id 로 db값 추출 (status가 running or 값없으면 assert)
    summary_data = ""

    pdf_path = f"temp/{request_id}/{SUMMARY_RESULT_FILE_NAME}"

    create_pdf(summary_data, pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=SUMMARY_RESULT_FILE_NAME
    )
