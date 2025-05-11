from fastapi import Form, APIRouter, UploadFile, File, Request, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import zipfile
from io import BytesIO
from datetime import datetime
from sqlmodel import Session, select, or_
import requests
import json

import pika
from dotenv import load_dotenv

from model.payload import summary
from utils.pdf_util import create_pdf
from utils.github_util import resolve_and_download_github_zip

from ai_module import AI
from db.connection import SessionDep, engine
from model.entity.summary_request import SummaryRequestEntity
from model.entity.summary_project import SummaryProjectEntity
from model.enums.summary_options import SummaryInputType

MAX_MEMORY_ZIP_SIZE = 50 * 1024 * 1024
SUMMARY_RESULT_FILE_NAME = "summary_result.pdf"

router = APIRouter(
    prefix="/summary",
    tags=["summary"]
)

load_dotenv()

@router.post("")
async def post_summary_request_handler(
    request: Request,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    form_data: summary.SummaryRequest = Depends(summary.SummaryRequest.as_form),
):
    print(form_data.project_file)
    print(form_data.summary_options)

    request_id = str(uuid.uuid4())

    # zip파일 unzip 후 저장 dir
    temp_dir = f"temp/{request_id}"

    os.makedirs(temp_dir, exist_ok=True)

    if SummaryInputType(form_data.mode) == SummaryInputType.Zip:
        file_bytes = await form_data.project_file.read()
        file_path = os.path.join(temp_dir, form_data.project_file.filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    elif SummaryInputType(form_data.mode) == SummaryInputType.Github:
        if not form_data.github_url:
            raise HTTPException(status_code=400, detail="github_url is required when mode is 'Github'")
        # try:
        #     file_path = os.path.join(temp_dir, form_data.github_url.rstrip("/").removesuffix(".git").split("/")[-1])
        #     file_path += ".zip"
        #
        #     resolve_and_download_github_zip(form_data.github_url, file_path)
        # except Exception as e:
        #     raise HTTPException(status_code=400, detail=f"GitHub download failed: {e}")

        # 사용 안함
        file_path = os.path.join(temp_dir, form_data.github_url.rstrip("/").removesuffix(".git").split("/")[-1])
        # file_path += ".zip"


    # file_size = len(file_bytes)
    # zip 용량에 따른 처리 차별
    # if file_size <= MAX_MEMORY_ZIP_SIZE:
    #     file_stream = BytesIO(file_bytes)
    #     with zipfile.ZipFile(file_stream, 'r') as zip_ref:
    #         zip_ref.extractall(temp_dir)
    # else:
    #     file_path = os.path.join(temp_dir, form_data.project_file.filename)
    #     with open(file_path, "wb") as f:
    #         f.write(file_bytes)
    #     with zipfile.ZipFile(file_path, 'r') as zip_ref:
    #         zip_ref.extractall(temp_dir)

        
    # 요청 생성
    new_request = SummaryRequestEntity(
        req_id = request_id,
        create_at=datetime.utcnow(),
        status="running",
        options=form_data.summary_options,
        file_dir=file_path
    )
    session.add(new_request)
    session.commit()
    session.refresh(new_request)

    # job publish
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST"), port=os.getenv("RABBITMQ_PORT"))
    )
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    message = {
        "request_id": f"{request_id}",
        "mode": f"{form_data.mode}",
        "github_url" : f"{form_data.github_url}"
    }

    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=json.dumps(message).encode('utf-8'),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        ))
    connection.close()
    
    base_url = str(request.base_url).rstrip("/")
    result_url = f"{base_url}/summary/download/{request_id}"

    return {
        "message" : "OK",
        "request_id" : f"{request_id}",
        "result_url" : result_url
    }


# /request_id/result
# TODO : status 값을 다루는 Entity나 Enum class 생성 (not str)
@router.get("/download/{request_id}")
async def get_summary_result(
        request_id: str,
        session: SessionDep,
):

    summary_query = select(SummaryProjectEntity).where(SummaryProjectEntity.req_id == request_id)
    status_query = select(SummaryRequestEntity.status).where(SummaryRequestEntity.req_id == request_id)

    summary_data = session.exec(summary_query).first()
    status = session.exec(status_query).first()

    # statement = (
    #     select(SummaryProjectEntity)
    #     .join(SummaryRequestEntity, SummaryProjectEntity.req_id == SummaryRequestEntity.req_id)
    #     .where(
    #         SummaryProjectEntity.req_id == request_id,
    #         SummaryRequestEntity.status == "done"
    #     )
    # )

    # done일 경우에는 summary_data가 있지만, 아닐 경우에는 summary_data가 비어 있음, AI가 완료되지 않아 db에 값을 넣지 못했기 떄문
    if not status:
        raise HTTPException(status_code=404, detail="Request ID not found.")

    pdf_path = f"temp/{request_id}/{SUMMARY_RESULT_FILE_NAME}"

    if status == 'done':
        create_pdf(str(summary_data), pdf_path)
    else:
        create_pdf("", pdf_path)

    response = FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=SUMMARY_RESULT_FILE_NAME
    )

    response.headers["Status"] = status  # "done" or "running" or "pedding"

    return response
