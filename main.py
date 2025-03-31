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

import uvicorn

app = FastAPI(debug=True, docs_url="/api/docs",
              title="AI Project Reviewer")



"""
option이랑 zip_file받으면,
1. zipfile unzip 후 디렉토리에 저장,
2. ai모듈 출력 (arg -> dir_path, option dict)
3. ai모듈 리턴값 받으면 db에 저장
4. request id 리턴

## db running, wait, done 등 (ai 처리 시간이 좀 걸려서)
## option -> front에서 곧 상세 정보 전달 예정 (string으로 주는데, 파이썬에서 json으로 변경해서 사용)
"""

"""
request_id를 key로 해서 db에 조회하고, return
"""
# 디렉토리 path, check box option 2개만 ai에 전달


@app.get("/api/healthCheck")
async def healthCheckHandler():
    return { "message" : "OK" }
    
app.include_router(
    summary_handler.router
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
