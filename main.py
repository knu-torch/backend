from fastapi import FastAPI
from handler import summary_handler

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)

# 허용할 Origin (프론트 주소)
origins = [
    "http://localhost:3000",   # React 등 프론트엔드 개발 서버
    "http://127.0.0.1:3000",   # 다른 로컬 주소
    "https://your-domain.com"  # 실제 배포 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Status"],
)
# # app = FastAPI(debug=True, docs_url="/api/docs",
#               title="AI Project Reviewer")



"""
option이랑 zip_file받으면,
1. zipfile unzip 후 디렉토리에 저장,
2. ai모듈 출력 (arg -> zip_path, options dict)
3. ai모듈 리턴값 받으면 db에 저장
4. request id 리턴

## db running, wait, done 등 (ai 처리 시간이 좀 걸려서)
## options -> front에서 곧 상세 정보 전달 예정 (string으로 주는데, 파이썬에서 json으로 변경해서 사용)
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

from worker.worker import worker
from threading import Thread
import argparse


def start_workers(count: int =2):
    for _ in range(count):
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start!")
    parser.add_argument("--workers", type=int, default=2, help="Number of worker threads to start")
    args = parser.parse_args()

    start_workers(args.workers)
    uvicorn.run(app, host="0.0.0.0", port=8000)
