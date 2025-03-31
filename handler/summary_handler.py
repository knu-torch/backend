from fastapi import Form, APIRouter, UploadFile, File, Request, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import zipfile
from io import BytesIO
from datetime import datetime
from sqlmodel import Session, select

from model.payload import summary
from utils.utils import create_pdf
from ai import AI
from db.connection import SessionDep, engine
from model.entity.summary_request import SummaryRequestEntity
from model.entity.summary_project import SummaryProjectEntity

MAX_MEMORY_ZIP_SIZE = 50 * 1024 * 1024
SUMMARY_RESULT_FILE_NAME = "summary_result.pdf"

router = APIRouter(
    prefix="/summary",
    tags=["summary"]
)

# AI 실행 함수
def run_ai(temp_dir, options, db_id):
    summary_result = {}
    status = ""

    try:
        summary_result = AI(temp_dir, options)
        status = "done"
        with Session(engine) as session:
            request_obj = session.get(SummaryRequestEntity, int(db_id))
            if request_obj:
                request_obj.status = status
                id = request_obj.id
                req_id = request_obj.req_id
                create_at = request_obj.create_at
                session.commit()
    except Exception as e:
        print(f"Error while execute AI function: {e}")
        status = "failed"
        with Session(engine) as session:
            request_obj = session.get(SummaryRequestEntity, int(db_id))
            if request_obj:
                request_obj.status = status
                session.commit()

        return

    with Session(engine) as session:
        new_request = SummaryProjectEntity(
            id = id,
            req_id=req_id,
            create_at=create_at,
            title=summary_result['title'],
            libs=summary_result['libs'],
            deploy_info=summary_result['deploy_info']
            )
        session.add(new_request)
        session.commit()
        session.refresh(new_request)



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

    # 요청 생성
    new_request = SummaryRequestEntity(req_id = request_id,create_at=datetime.utcnow(), status="running")
    session.add(new_request)
    session.commit()
    session.refresh(new_request)

    db_id = str(new_request.id)

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

    # llm 처리, db 저장
    background_tasks.add_task(run_ai, temp_dir, form_data.summary_options, db_id)

    base_url = str(request.base_url).rstrip("/")
    result_url = f"{base_url}/summary/{request_id}"

    return {
        "message" : "OK",
        "request_id" : f"{request_id}",
        "result_url" : result_url
    }



@router.get("/{request_id}")
async def get_summary_result(
        request_id: str,
        session: SessionDep,
):

    statement = select(SummaryProjectEntity).where(SummaryProjectEntity.req_id == request_id)
    summary_data = session.exec(statement).first()

    if not summary_data:
        raise HTTPException(status_code=404, detail="Summary data not found for the given request_id")

    pdf_path = f"temp/{request_id}/{SUMMARY_RESULT_FILE_NAME}"

    create_pdf(str(summary_data), pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=SUMMARY_RESULT_FILE_NAME
    )
