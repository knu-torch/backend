import os
import zipfile
from google.generativeai import configure, GenerativeModel
from model.enums import summary_options

def setup_gemini():
    os.environ["GEMINI_API_KEY"] = "AIzaSyAlX1D_kIgCvoXXU72JgltquG8zWX2xu7Y"
    configure(api_key=os.getenv("GEMINI_API_KEY"))
    return GenerativeModel("gemini-2.0-flash")

gemini_model = setup_gemini()

def extract_code_from_zip(zip_path: str) -> str:
    extracted_code = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            if not file_name.endswith('/'):
                with zip_ref.open(file_name) as file:
                    extracted_code.append(f"### {file_name}\n" + file.read().decode("utf-8", errors="ignore"))
    return "\n\n".join(extracted_code) if extracted_code else "코드 파일이 없습니다."

def generate_prompt(option: list[summary_options.SummaryOption], code_text: str) -> str:
    base_prompt = ""
    
    if summary_options.SummaryOption.Project in option:
        base_prompt += "\n- 1. 이 프로젝트를 한 줄로 요약해줘.\n- 2. 이 프로젝트에 사용된 라이브러리 종류와 버전 정보를 알려줘.\n- 3. git action이나 서비스 파일을 분석하여 배포 관련 정보를 알려줘.\n- 4. 한국어로 작성해줘."
    if summary_options.SummaryOption.Package in option:
        base_prompt += "\n- 1. 이 프로젝트에서 사용된 패키지들의 상호의존성을 알아보기 쉽게 보여줘.\n- 2. 외부 라이브러리는 제외해줘.\n- 3. 패키지 별 요약을 최대 2줄로 작성해줘.\n- 4. 한국어로 작성해줘."
    
    return f"{base_prompt}\n\n{code_text}"

def summarize_code(code_text: str, options: list[summary_options.SummaryOption]) -> dict:
    prompt = generate_prompt(options, code_text)
    try:
        response = gemini_model.generate_content(prompt)
        summary_text = response.text if response else "요약 생성 실패"
        
        # 결과를 적절히 분리 (예제)
        parts = summary_text.split("\n")
        return {
            "title": parts[0] if len(parts) > 0 else "제목 없음",
            "libs": parts[1] if len(parts) > 1 else "라이브러리 정보 없음",
            "deploy_info": parts[2] if len(parts) > 2 else "배포 정보 없음"
        }
    
    except Exception as e:
        return {"error": f"요약 중 오류 발생: {e}"}

def AI(dir_path: str, option: list[summary_options.SummaryOption]) -> dict:
    extracted_code = extract_code_from_zip(dir_path)
    
    if extracted_code == "코드 파일이 없습니다.":
        return {"error": "ZIP 파일 내에 코드 파일이 없습니다."}
    
    return summarize_code(extracted_code, option)
