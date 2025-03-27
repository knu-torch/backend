from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
import zipfile
import json

from google.generativeai import configure, GenerativeModel
from fpdf import FPDF
import uvicorn
import google.generativeai as genai


# 환경 변수로 API 키 설정
os.environ["GEMINI_API_KEY"] = "AIzaSyAlX1D_kIgCvoXXU72JgltquG8zWX2xu7Y"
configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = GenerativeModel("gemini-2.0-flash")
# for model in genai.list_models():
#     print(model.name, model.supported_generation_methods)

app = FastAPI(debug=True)

class APIOption(BaseModel):
    language: str = None
    detail_level: str = None
    include_comments: bool = False

# PDF 파일 생성 함수
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

# 압축 해제 및 코드 수집
def extract_and_collect_code(zip_path: str, extract_to: str) -> tuple[str, list[str]]:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    code_contents = ""
    filenames = []

    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".java", ".cpp", ".html", ".css")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                except Exception:
                    continue

                rel_path = os.path.relpath(file_path, extract_to)
                filenames.append(rel_path)
                code_contents += f"\n===== {rel_path} =====\n{code}\n"

    return code_contents, filenames

@app.post("/summarize")
async def summarize_zip_project(
        text: str = Form(...),
        options: str = Form(...),
        zip_file: UploadFile = File(...)
):
    session_id = uuid.uuid4().hex
    temp_dir = os.path.join("temp", session_id)
    os.makedirs(temp_dir, exist_ok=True)

    zip_path = os.path.join(temp_dir, f"{session_id}.zip")
    with open(zip_path, 'wb') as f:
        f.write(await zip_file.read())

    code_text, file_list = extract_and_collect_code(zip_path, os.path.join(temp_dir, "extracted"))
    parsed_options = APIOption(**json.loads(options))

    prompt = f"""
사용자가 작성한 프로젝트에 대한 설명: {text}

옵션:
{parsed_options}

총 {len(file_list)}개의 코드 파일이 포함되어 있습니다.
파일 목록: {', '.join(file_list[:10])} {'...외 다수' if len(file_list) > 10 else ''}

파일 내용:
{code_text[:50000]}

이 프로젝트는 어떤 구조이고, 무엇을 수행하며, 주요 컴포넌트는 어떤 것들인지 요약해줘.
"""

    try:
        response = gemini_model.generate_content(prompt)
        summary = response.text.strip()
    except Exception as e:
        summary = f"Gemini 요약 중 오류 발생: {e}"

    pdf_path = os.path.join(temp_dir, f"{session_id}_summary.pdf")
    create_pdf(summary, pdf_path)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="project_summary.pdf"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
