from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from fpdf import FPDF
from pydantic import BaseModel
from handler import summary_handler
import uuid
import os
import zipfile
import json
import requests
import pymysql

from ai import AI


# 디렉토리 path, check box option 2개만 ai에 전달

import uvicorn

app = FastAPI(debug=True, docs_url="/api/docs",
              title="AI Project Reviewer")



class APIOption(BaseModel):
    language: str = None
    detail_level: str = None
    include_comments: bool = False

def create_pdf(summary_text: str, output_path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = "C:/Windows/Fonts/malgun.ttf"
    pdf.add_font("malgun", "", font_path, uni=True)
    pdf.set_font("malgun", size=12)

    for line in summary_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf.output(output_path)



"""
option이랑 zip_file받으면,
1. zipfile unzip 후 디렉토리에 저장,
2. ai모듈 출력 (arg -> dir_path, option dict)
3. ai모듈 리턴값 받으면 db에 저장
4. request id 리턴

## db running, wait, done 등 (ai 처리 시간이 좀 걸려서)
## option -> front에서 곧 상세 정보 전달 예정 (string으로 주는데, 파이썬에서 json으로 변경해서 사용)
"""


@app.post("/summarize")
async def get_project_info(
        request: Request,
        call_next,
        options: str,
        zip_file: UploadFile = File(...)
):
    ## request_id 발급
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    print(f"Request ID: {request_id}")
    response = await call_next(request)
    response.headers["x-request-id"] = request_id


    AI()

    return response


"""
request_id를 key로 해서 db에 조회하고, return
"""


@app.get("/re")
async def re(
        request_id: str = ""
):
    conn = pymysql.connect(
        host='localhost',  # 또는 IP 주소
        user='root',  # 사용자 이름
        password='your_pass',  # 비밀번호
        db='your_db_name',  # 사용할 데이터베이스 이름
        charset='utf8mb4',  # 문자 인코딩
        cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 받을 수 있음
    )

    try:
        with conn.cursor() as cursor:
            # SQL 쿼리 작성
            sql = "SELECT * FROM your_table"
            cursor.execute(sql)

            # 결과 가져오기
            result = cursor.fetchall()
            for row in result:
                print(row)
    finally:
        conn.close()


@app.get("/api/healthCheck")
async def healthCheckHandler():
    return { "message" : "OK" }
    
app.include_router(
    summary_handler.router
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
